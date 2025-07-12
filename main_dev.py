"""
Development version of iTrash system with manual controls.
Uses keyboard triggers for proximity sensors and continuous camera feed.
"""

import asyncio
import time
import threading
import signal
import sys
import os
from datetime import datetime
from config.settings import SystemStates, TimingConfig
from core.hardware import LEDStrip
from core.camera import CameraController
from core.ai_classifier import ClassificationManager
from core.database import db_manager
from core.manual_controls import ManualHardwareController, CameraFeedDisplay
from display.media_display import DisplayManager

# Simple logging setup
def log_event(event_type, message, data=None):
    """Simple logging function for key events"""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    log_entry = f"[{timestamp}] {event_type}: {message}"
    if data:
        log_entry += f" | Data: {data}"
    print(log_entry)
    
    # Also save to log file
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    log_file = os.path.join(log_dir, f"itrash_{datetime.now().strftime('%Y-%m-%d')}.log")
    try:
        with open(log_file, "a") as f:
            f.write(log_entry + "\n")
    except Exception as e:
        print(f"Failed to write to log file: {e}")

class iTrashSystemDev:
    """Development version of iTrash system with manual controls"""
    
    def __init__(self):
        self.hardware = None
        self.camera = None
        self.classifier = None
        self.display_manager = None
        self.camera_feed = None
        self.is_running = False
        self.display_thread = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all system components"""
        log_event("SYSTEM", "Initializing iTrash development system...")
        
        # Initialize database
        if not db_manager.connect():
            log_event("ERROR", "Failed to connect to database")
        else:
            log_event("SYSTEM", "Database connected successfully")
        
        # Initialize LED strip only (no GPIO for proximity sensors)
        try:
            led_strip = LEDStrip()
            self.hardware = ManualHardwareController(led_strip)
            log_event("HARDWARE", "Manual hardware controller initialized successfully")
        except Exception as e:
            log_event("ERROR", f"Error initializing hardware: {e}")
            self.hardware = None
        
        # Initialize camera
        try:
            self.camera = CameraController()
            if self.camera.initialize():
                log_event("CAMERA", "Camera initialized successfully")
                # Initialize camera feed display
                self.camera_feed = CameraFeedDisplay(self.camera)
            else:
                log_event("ERROR", "Camera initialization failed")
                self.camera = None
        except Exception as e:
            log_event("ERROR", f"Error initializing camera: {e}")
            self.camera = None
        
        # Initialize classifier
        try:
            led_strip = self.hardware.get_led_strip() if self.hardware else None
            self.classifier = ClassificationManager(led_strip)
            log_event("AI", "AI classifier initialized successfully")
        except Exception as e:
            log_event("ERROR", f"Error initializing classifier: {e}")
            self.classifier = None
        
        # Initialize display manager
        try:
            self.display_manager = DisplayManager()
            log_event("DISPLAY", "Display manager initialized successfully")
        except Exception as e:
            log_event("ERROR", f"Error initializing display manager: {e}")
            self.display_manager = None
        
        # Initialize accumulator
        db_manager.update_acc(SystemStates.IDLE)
        log_event("SYSTEM", "Development system initialization complete")
    
    def start_display(self):
        """Start the display in a separate thread"""
        if self.display_manager:
            try:
                self.display_thread = threading.Thread(
                    target=self.display_manager.start_display,
                    daemon=True
                )
                self.display_thread.start()
                log_event("DISPLAY", "Display started successfully")
            except Exception as e:
                log_event("ERROR", f"Error starting display: {e}")
    
    def start_camera_feed(self):
        """Start the camera feed display"""
        if self.camera_feed:
            try:
                self.camera_feed.start_feed()
                log_event("CAMERA", "Camera feed started successfully")
            except Exception as e:
                log_event("ERROR", f"Error starting camera feed: {e}")
    
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
            log_event("LED", f"LED strip set to BLUE for {trash_class} classification")
        elif trash_class == "yellow":
            led_strip.set_color_all((255, 255, 0))  # Yellow
            log_event("LED", f"LED strip set to YELLOW for {trash_class} classification")
        elif trash_class == "brown":
            led_strip.set_color_all((139, 69, 19))  # Brown
            log_event("LED", f"LED strip set to BROWN for {trash_class} classification")
        
        # Wait for user to throw trash in correct bin
        start_time = time.time()
        while time.time() - start_time < TimingConfig.USER_CONFIRMATION_TIMEOUT:
            # Check if trash was thrown in correct bin
            if trash_class == "blue" and proximity_sensors.detect_blue_bin():
                log_event("SENSOR", f"BLUE bin proximity sensor triggered for {trash_class} classification")
                return True
            elif trash_class == "yellow" and proximity_sensors.detect_yellow_bin():
                log_event("SENSOR", f"YELLOW bin proximity sensor triggered for {trash_class} classification")
                return True
            elif trash_class == "brown" and proximity_sensors.detect_brown_bin():
                log_event("SENSOR", f"BROWN bin proximity sensor triggered for {trash_class} classification")
                return True
            
            await asyncio.sleep(0.1)
        
        # Timeout - user didn't confirm
        return False
    
    async def process_trash_detection(self):
        """Process trash detection and classification"""
        if not self.camera or not self.classifier:
            log_event("ERROR", "Camera or classifier not available")
            return
        
        # Set state to processing
        db_manager.update_acc(SystemStates.PROCESSING)
        
        # Capture image
        frame = self.camera.capture_image()
        if frame is None:
            log_event("CAMERA", "Failed to capture image")
            db_manager.update_acc(SystemStates.IDLE)
            return
        
        log_event("CAMERA", "Image captured successfully")
        
        # Classify trash
        trash_class = await self.classifier.process_image_with_feedback(frame)
        
        if not trash_class:
            log_event("AI", "Failed to classify trash - no response from GPT")
            # Show error animation
            if self.hardware:
                self.hardware.show_error_animation()
            db_manager.update_acc(SystemStates.IDLE)
            return
        
        log_event("AI", f"GPT classification response: {trash_class}")
        
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
            log_event("LED", "LED strip cleared")
    
    async def main_loop(self):
        """Main system loop"""
        if not self.hardware:
            log_event("ERROR", "Hardware not available, exiting")
            return
        
        proximity_sensors = self.hardware.get_proximity_sensors()
        
        log_event("SYSTEM", "Starting development main loop...")
        log_event("SYSTEM", "Waiting for manual object detection triggers...")
        log_event("SYSTEM", "Press 'o' to simulate object detection")
        
        # Initial delay
        await asyncio.sleep(TimingConfig.OBJECT_DETECTION_DELAY)
        
        # Set initial state
        db_manager.update_acc(SystemStates.IDLE)
        
        while self.is_running:
            try:
                # Check for manual object detection
                if proximity_sensors.detect_object_proximity():
                    log_event("SENSOR", "Manual object detection triggered!")
                    
                    # Set state to processing
                    db_manager.update_acc(SystemStates.PROCESSING)
                    
                    # Show white LEDs
                    led_strip = self.hardware.get_led_strip()
                    led_strip.set_color_all((255, 255, 255))
                    log_event("LED", "LED strip set to WHITE for object detection")
                    
                    # Process the detection
                    await self.process_trash_detection()
                
                await asyncio.sleep(0.1)  # Small delay to prevent CPU overuse
                
            except KeyboardInterrupt:
                log_event("SYSTEM", "Interrupted by user")
                break
            except Exception as e:
                log_event("ERROR", f"Error in main loop: {e}")
                await asyncio.sleep(1)
    
    def start(self):
        """Start the iTrash development system"""
        log_event("SYSTEM", "Starting iTrash development system...")
        self.is_running = True
        
        # Start display
        self.start_display()
        
        # Start camera feed
        self.start_camera_feed()
        
        # Start main loop
        try:
            asyncio.run(self.main_loop())
        except KeyboardInterrupt:
            log_event("SYSTEM", "System stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the iTrash development system"""
        log_event("SYSTEM", "Stopping iTrash development system...")
        self.is_running = False
        
        # Stop camera feed
        if self.camera_feed:
            self.camera_feed.stop_feed()
            log_event("CAMERA", "Camera feed stopped")
        
        # Cleanup hardware
        if self.hardware:
            self.hardware.cleanup()
            log_event("HARDWARE", "Hardware cleanup completed")
        
        # Release camera
        if self.camera:
            self.camera.release()
            log_event("CAMERA", "Camera released")
        
        # Close database connection
        db_manager.close()
        log_event("SYSTEM", "Database connection closed")
        
        log_event("SYSTEM", "Development system stopped")


def signal_handler(signum, frame):
    """Handle system signals"""
    log_event("SYSTEM", f"Received signal {signum}, shutting down...")
    sys.exit(0)


def main():
    """Main entry point for development system"""
    log_event("SYSTEM", "iTrash development system starting up...")
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start the development system
    system = iTrashSystemDev()
    system.start()


if __name__ == "__main__":
    main() 