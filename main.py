"""
Main application for iTrash unified system.
Orchestrates hardware control, AI classification, display, and analytics.
"""

import asyncio
import time
import threading
import signal
import sys
from datetime import datetime
from config.settings import SystemStates, TimingConfig
from core.hardware import HardwareController
from core.camera import CameraController
from core.ai_classifier import ClassificationManager
from core.database import db_manager
from display.media_display import DisplayManager

class iTrashSystem:
    """Main iTrash system controller"""
    
    def __init__(self):
        self.hardware = None
        self.camera = None
        self.classifier = None
        self.display_manager = None
        self.is_running = False
        self.display_thread = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all system components"""
        print("Initializing iTrash system...")
        
        # Initialize database
        if not db_manager.connect():
            print("Warning: Failed to connect to database")
        
        # Initialize hardware
        try:
            self.hardware = HardwareController()
            print("Hardware initialized successfully")
        except Exception as e:
            print(f"Error initializing hardware: {e}")
            self.hardware = None
        
        # Initialize camera
        try:
            self.camera = CameraController()
            if self.camera.initialize():
                print("Camera initialized successfully")
            else:
                print("Warning: Camera initialization failed")
                self.camera = None
        except Exception as e:
            print(f"Error initializing camera: {e}")
            self.camera = None
        
        # Initialize classifier
        try:
            led_strip = self.hardware.get_led_strip() if self.hardware else None
            self.classifier = ClassificationManager(led_strip)
            print("AI classifier initialized successfully")
        except Exception as e:
            print(f"Error initializing classifier: {e}")
            self.classifier = None
        
        # Initialize display manager
        try:
            self.display_manager = DisplayManager()
            print("Display manager initialized successfully")
        except Exception as e:
            print(f"Error initializing display manager: {e}")
            self.display_manager = None
        
        # Initialize accumulator
        db_manager.update_acc(SystemStates.IDLE)
        print("System initialization complete")
    
    def start_display(self):
        """Start the display in a separate thread"""
        if self.display_manager:
            try:
                self.display_thread = threading.Thread(
                    target=self.display_manager.start_display,
                    daemon=True
                )
                self.display_thread.start()
                print("Display started successfully")
            except Exception as e:
                print(f"Error starting display: {e}")
    
    async def wait_for_user_confirmation(self, trash_class):
        """Wait for user confirmation of classification"""
        if not self.hardware:
            return False
        
        led_strip = self.hardware.get_led_strip()
        proximity_sensors = self.hardware.get_proximity_sensors()
        
        # Set state to user confirmation
        db_manager.update_acc(SystemStates.USER_CONFIRMATION)
        
        # Show appropriate LED color based on classification
        if trash_class == "blue":
            led_strip.set_color_all((0, 0, 255))  # Blue
        elif trash_class == "yellow":
            led_strip.set_color_all((255, 255, 0))  # Yellow
        elif trash_class == "brown":
            led_strip.set_color_all((139, 69, 19))  # Brown
        
        # Wait for user to throw trash in correct bin
        start_time = time.time()
        while time.time() - start_time < TimingConfig.USER_CONFIRMATION_TIMEOUT:
            # Check if trash was thrown in correct bin
            if trash_class == "blue" and proximity_sensors.detect_blue_bin():
                return True
            elif trash_class == "yellow" and proximity_sensors.detect_yellow_bin():
                return True
            elif trash_class == "brown" and proximity_sensors.detect_brown_bin():
                return True
            
            await asyncio.sleep(0.1)
        
        # Timeout - user didn't confirm
        return False
    
    async def process_trash_detection(self):
        """Process trash detection and classification"""
        if not self.camera or not self.classifier:
            print("Camera or classifier not available")
            return
        
        # Set state to processing
        db_manager.update_acc(SystemStates.PROCESSING)
        
        # Capture image
        frame = self.camera.capture_image()
        if frame is None:
            print("Failed to capture image")
            db_manager.update_acc(SystemStates.IDLE)
            return
        
        # Classify trash
        trash_class = await self.classifier.process_image_with_feedback(frame)
        
        if not trash_class:
            print("Failed to classify trash")
            # Show error animation
            if self.hardware:
                self.hardware.show_error_animation()
            db_manager.update_acc(SystemStates.IDLE)
            return
        
        # Set state to show trash
        db_manager.update_acc(SystemStates.SHOW_TRASH)
        
        # Wait for user confirmation
        confirmed = await self.wait_for_user_confirmation(trash_class)
        
        if confirmed:
            # Success - show reward
            db_manager.update_acc(SystemStates.REWARD)
            if self.hardware:
                self.hardware.show_success_animation()
            
            # Store image data
            current_time = datetime.now()
            today = current_time.strftime("%Y-%m-%d")
            hour_day = current_time.strftime("%H:%M:%S")
            
            # Encode image
            image_base64 = self.camera.encode_image_to_base64(frame)
            if image_base64:
                db_manager.insert_image_data(
                    image_base64, today, hour_day, trash_class, "", True
                )
        else:
            # Timeout or incorrect bin
            db_manager.update_acc(SystemStates.TIMEOUT)
            if self.hardware:
                self.hardware.show_error_animation()
        
        # Reset to idle after delay
        await asyncio.sleep(2)
        db_manager.update_acc(SystemStates.IDLE)
        
        # Clear LEDs
        if self.hardware:
            self.hardware.get_led_strip().clear_all()
    
    async def main_loop(self):
        """Main system loop"""
        if not self.hardware:
            print("Hardware not available, exiting")
            return
        
        proximity_sensors = self.hardware.get_proximity_sensors()
        
        print("Starting main loop...")
        print("Waiting for objects to be detected...")
        
        # Initial delay
        await asyncio.sleep(TimingConfig.OBJECT_DETECTION_DELAY)
        
        # Set initial state
        db_manager.update_acc(SystemStates.IDLE)
        
        while self.is_running:
            try:
                # Check for object detection
                if proximity_sensors.detect_object_proximity():
                    print("Object detected!")
                    
                    # Set state to processing
                    db_manager.update_acc(SystemStates.PROCESSING)
                    
                    # Show white LEDs
                    led_strip = self.hardware.get_led_strip()
                    led_strip.set_color_all((255, 255, 255))
                    
                    # Process the detection
                    await self.process_trash_detection()
                
                await asyncio.sleep(0.1)  # Small delay to prevent CPU overuse
                
            except KeyboardInterrupt:
                print("Interrupted by user")
                break
            except Exception as e:
                print(f"Error in main loop: {e}")
                await asyncio.sleep(1)
    
    def start(self):
        """Start the iTrash system"""
        print("Starting iTrash system...")
        self.is_running = True
        
        # Start display
        self.start_display()
        
        # Start main loop
        try:
            asyncio.run(self.main_loop())
        except KeyboardInterrupt:
            print("System stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the iTrash system"""
        print("Stopping iTrash system...")
        self.is_running = False
        
        # Stop display
        if self.display_manager:
            self.display_manager.stop_display()
        
        # Cleanup hardware
        if self.hardware:
            self.hardware.cleanup()
        
        # Release camera
        if self.camera:
            self.camera.release()
        
        # Disconnect database
        db_manager.disconnect()
        
        print("System stopped")


def signal_handler(signum, frame):
    """Handle system signals"""
    print(f"Received signal {signum}, shutting down...")
    sys.exit(0)


def main():
    """Main entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start system
    system = iTrashSystem()
    
    try:
        system.start()
    except Exception as e:
        print(f"Error starting system: {e}")
        system.stop()


if __name__ == "__main__":
    main() 