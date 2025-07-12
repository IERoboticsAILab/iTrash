"""
Development version of iTrash system with manual controls.
Uses keyboard triggers for proximity sensors and continuous camera feed.
"""

import asyncio
import time
import threading
import signal
import sys
from datetime import datetime
from config.settings import SystemStates, TimingConfig
from core.hardware import LEDStrip
from core.camera import CameraController
from core.ai_classifier import ClassificationManager
from core.database import db_manager
from core.manual_controls import ManualHardwareController, CameraFeedDisplay
from display.media_display import DisplayManager

class iTrashSystemDev:
    """Development version of iTrash system with manual controls"""
    
    def __init__(self):
        self.hardware = None
        self.camera = None
        self.classifier = None
        self.display_manager = None
        self.camera_feed = None
        self.camera_display_thread = None
        self.is_running = False
        self.display_thread = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize all system components"""
        print("Initializing iTrash development system...")
        
        # Initialize database
        if not db_manager.connect():
            print("Warning: Failed to connect to database")
        
        # Initialize LED strip only (no GPIO for proximity sensors)
        try:
            led_strip = LEDStrip()
            self.hardware = ManualHardwareController(led_strip)
            print("Manual hardware controller initialized successfully")
        except Exception as e:
            print(f"Error initializing hardware: {e}")
            self.hardware = None
        
        # Initialize camera
        try:
            self.camera = CameraController()
            if self.camera.initialize():
                print("Camera initialized successfully")
                # Initialize camera feed display
                self.camera_feed = CameraFeedDisplay(self.camera)
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
        print("Development system initialization complete")
    
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
    
    def start_camera_feed(self):
        """Start the camera feed display"""
        if self.camera_feed:
            try:
                self.camera_feed.start_feed()
                print("Camera feed started successfully")
            except Exception as e:
                print(f"Error starting camera feed: {e}")
    
    def start_virtual_camera_display(self):
        """Start a virtual camera display in a separate window"""
        if not self.camera or not self.camera.is_initialized:
            print("Camera not available for virtual display")
            return
        
        try:
            import cv2
            import threading
            
            def camera_display_loop():
                """Camera display loop in separate thread"""
                window_name = "iTrash Camera Feed"
                cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
                cv2.resizeWindow(window_name, 800, 600)
                
                print(f"📷 Virtual camera display started: {window_name}")
                print("   Press 'q' in camera window to close")
                
                while self.is_running:
                    try:
                        ret, frame = self.camera.read_frame()
                        if not ret:
                            print("Failed to read frame from camera")
                            break
                        
                        # Add overlay information
                        overlay = frame.copy()
                        
                        # Add title
                        cv2.putText(overlay, "iTrash Camera Feed", (10, 30), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
                        
                        # Add status info
                        cv2.putText(overlay, "Press 'q' to close", (10, overlay.shape[0] - 20), 
                                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
                        
                        # Display frame
                        cv2.imshow(window_name, overlay)
                        
                        # Check for quit key
                        if cv2.waitKey(1) & 0xFF == ord('q'):
                            break
                            
                    except Exception as e:
                        print(f"Error in camera display: {e}")
                        break
                
                cv2.destroyAllWindows()
                print("📷 Virtual camera display closed")
            
            # Start camera display in separate thread
            self.camera_display_thread = threading.Thread(target=camera_display_loop, daemon=True)
            self.camera_display_thread.start()
            print("✅ Virtual camera display started successfully")
            
        except Exception as e:
            print(f"Error starting virtual camera display: {e}")
    
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
        
        print("Starting development main loop...")
        print("Waiting for manual object detection triggers...")
        print("Press 'o' to simulate object detection")
        
        # Initial delay
        await asyncio.sleep(TimingConfig.OBJECT_DETECTION_DELAY)
        
        # Set initial state
        db_manager.update_acc(SystemStates.IDLE)
        
        while self.is_running:
            try:
                # Check for manual object detection
                if proximity_sensors.detect_object_proximity():
                    print("Manual object detection triggered!")
                    
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
        """Start the iTrash development system"""
        print("Starting iTrash development system...")
        self.is_running = True
        
        # Start display
        self.start_display()
        
        # Start camera feed
        self.start_camera_feed()

        # Start virtual camera display
        self.start_virtual_camera_display()
        
        # Start main loop
        try:
            asyncio.run(self.main_loop())
        except KeyboardInterrupt:
            print("System stopped by user")
        finally:
            self.stop()
    
    def stop(self):
        """Stop the iTrash development system"""
        print("Stopping iTrash development system...")
        self.is_running = False
        
        # Stop camera feed
        if self.camera_feed:
            self.camera_feed.stop_feed()
        
        # Stop virtual camera display
        if self.camera_display_thread and self.camera_display_thread.is_alive():
            self.camera_display_thread.join()
            print("Virtual camera display thread joined")
        
        # Cleanup hardware
        if self.hardware:
            self.hardware.cleanup()
        
        # Release camera
        if self.camera:
            self.camera.release()
        
        # Close database connection
        db_manager.close()
        
        print("Development system stopped")


def signal_handler(signum, frame):
    """Handle system signals"""
    print(f"\nReceived signal {signum}, shutting down...")
    sys.exit(0)


def main():
    """Main entry point for development system"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create and start the development system
    system = iTrashSystemDev()
    system.start()


if __name__ == "__main__":
    main() 