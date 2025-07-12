"""
Development version of iTrash system with manual controls.
Uses keyboard triggers for proximity sensors and continuous camera feed.
"""

import asyncio
import time
import threading
import signal
import sys
import logging
import os
import json
from datetime import datetime
from config.settings import SystemStates, TimingConfig
from core.hardware import LEDStrip
from core.camera import CameraController
from core.ai_classifier import ClassificationManager
from core.database import db_manager
from core.manual_controls import ManualHardwareController, CameraFeedDisplay
from display.media_display import DisplayManager

def setup_logging():
    """Setup comprehensive logging for the iTrash system"""
    # Create logs directory if it doesn't exist
    if not os.path.exists('logs'):
        os.makedirs('logs')
    
    # Create timestamp for log files
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            # Console handler
            logging.StreamHandler(),
            # File handler for all logs
            logging.FileHandler(f'logs/itrash_system_{timestamp}.log'),
            # Separate file for detailed events
            logging.FileHandler(f'logs/events_{timestamp}.log')
        ]
    )
    
    # Create separate logger for events
    event_logger = logging.getLogger('events')
    event_logger.setLevel(logging.INFO)
    
    # Create file handler for events
    event_handler = logging.FileHandler(f'logs/events_{timestamp}.log')
    event_handler.setLevel(logging.INFO)
    
    # Create formatter for events
    event_formatter = logging.Formatter('%(asctime)s - %(message)s')
    event_handler.setFormatter(event_formatter)
    
    # Add handler to event logger
    event_logger.addHandler(event_handler)
    
    return logging.getLogger(__name__), event_logger

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
        
        # Setup logging
        self.logger, self.event_logger = setup_logging()
        
        # Initialize components
        self._initialize_components()
    
    def log_event(self, event_type, details=None, data=None):
        """Log an event with timestamp and details"""
        timestamp = datetime.now().isoformat()
        event_data = {
            'timestamp': timestamp,
            'event_type': event_type,
            'details': details or {},
            'data': data
        }
        
        # Log to event logger
        self.event_logger.info(json.dumps(event_data))
        
        # Also log to main logger
        self.logger.info(f"EVENT: {event_type} - {details}")
    
    def _initialize_components(self):
        """Initialize all system components"""
        self.logger.info("Initializing iTrash development system...")
        self.log_event("system_start", {"version": "development"})
        
        # Initialize database
        if not db_manager.connect():
            self.logger.warning("Failed to connect to database")
            self.log_event("database_error", {"error": "connection_failed"})
        else:
            self.log_event("database_connected")
        
        # Initialize LED strip only (no GPIO for proximity sensors)
        try:
            led_strip = LEDStrip()
            self.hardware = ManualHardwareController(led_strip)
            self.logger.info("Manual hardware controller initialized successfully")
            self.log_event("hardware_initialized", {"type": "manual_controller"})
        except Exception as e:
            self.logger.error(f"Error initializing hardware: {e}")
            self.log_event("hardware_error", {"error": str(e)})
            self.hardware = None
        
        # Initialize camera
        try:
            self.camera = CameraController()
            if self.camera.initialize():
                self.logger.info("Camera initialized successfully")
                self.log_event("camera_initialized")
                # Initialize camera feed display
                self.camera_feed = CameraFeedDisplay(self.camera)
                self.log_event("camera_feed_initialized")
            else:
                self.logger.warning("Camera initialization failed")
                self.log_event("camera_error", {"error": "initialization_failed"})
                self.camera = None
        except Exception as e:
            self.logger.error(f"Error initializing camera: {e}")
            self.log_event("camera_error", {"error": str(e)})
            self.camera = None
        
        # Initialize classifier
        try:
            led_strip = self.hardware.get_led_strip() if self.hardware else None
            self.classifier = ClassificationManager(led_strip)
            self.logger.info("AI classifier initialized successfully")
            self.log_event("classifier_initialized")
        except Exception as e:
            self.logger.error(f"Error initializing classifier: {e}")
            self.log_event("classifier_error", {"error": str(e)})
            self.classifier = None
        
        # Initialize display manager
        try:
            self.display_manager = DisplayManager()
            self.logger.info("Display manager initialized successfully")
            self.log_event("display_initialized")
        except Exception as e:
            self.logger.error(f"Error initializing display manager: {e}")
            self.log_event("display_error", {"error": str(e)})
            self.display_manager = None
        
        # Initialize accumulator
        db_manager.update_acc(SystemStates.IDLE)
        self.logger.info("Development system initialization complete")
        self.log_event("system_initialized")
    
    def start_display(self):
        """Start the display in a separate thread"""
        if self.display_manager:
            try:
                self.display_thread = threading.Thread(
                    target=self.display_manager.start_display,
                    daemon=True
                )
                self.display_thread.start()
                self.logger.info("Display started successfully")
                self.log_event("display_started")
            except Exception as e:
                self.logger.error(f"Error starting display: {e}")
                self.log_event("display_start_error", {"error": str(e)})
    
    def start_camera_feed(self):
        """Start the camera feed display"""
        if self.camera_feed:
            try:
                self.camera_feed.start_feed()
                self.logger.info("Camera feed started successfully")
                self.log_event("camera_feed_started")
            except Exception as e:
                self.logger.error(f"Error starting camera feed: {e}")
                self.log_event("camera_feed_error", {"error": str(e)})
    
    async def wait_for_user_confirmation(self, trash_class):
        """Wait for user confirmation of classification"""
        if not self.hardware:
            return False
        
        led_strip = self.hardware.get_led_strip()
        proximity_sensors = self.hardware.get_proximity_sensors()
        
        # Set state to user confirmation
        db_manager.update_acc(SystemStates.USER_CONFIRMATION)
        self.log_event("user_confirmation_started", {"trash_class": trash_class})
        
        # Show appropriate LED color based on classification
        if trash_class == "blue":
            led_strip.set_color_all((0, 0, 255))  # Blue
            self.log_event("led_color_set", {"color": "blue", "rgb": (0, 0, 255)})
        elif trash_class == "yellow":
            led_strip.set_color_all((255, 255, 0))  # Yellow
            self.log_event("led_color_set", {"color": "yellow", "rgb": (255, 255, 0)})
        elif trash_class == "brown":
            led_strip.set_color_all((139, 69, 19))  # Brown
            self.log_event("led_color_set", {"color": "brown", "rgb": (139, 69, 19)})
        
        # Wait for user to throw trash in correct bin
        start_time = time.time()
        while time.time() - start_time < TimingConfig.USER_CONFIRMATION_TIMEOUT:
            # Check if trash was thrown in correct bin
            if trash_class == "blue" and proximity_sensors.detect_blue_bin():
                self.log_event("bin_detected", {"bin_type": "blue", "correct": True})
                return True
            elif trash_class == "yellow" and proximity_sensors.detect_yellow_bin():
                self.log_event("bin_detected", {"bin_type": "yellow", "correct": True})
                return True
            elif trash_class == "brown" and proximity_sensors.detect_brown_bin():
                self.log_event("bin_detected", {"bin_type": "brown", "correct": True})
                return True
            
            await asyncio.sleep(0.1)
        
        # Timeout - user didn't confirm
        self.log_event("user_confirmation_timeout", {"trash_class": trash_class})
        return False
    
    async def process_trash_detection(self):
        """Process trash detection and classification"""
        if not self.camera or not self.classifier:
            self.logger.error("Camera or classifier not available")
            self.log_event("processing_error", {"error": "missing_components"})
            return
        
        # Set state to processing
        db_manager.update_acc(SystemStates.PROCESSING)
        self.log_event("processing_started")
        
        # Capture image
        self.logger.info("Capturing image...")
        frame = self.camera.capture_image()
        if frame is None:
            self.logger.error("Failed to capture image")
            self.log_event("image_capture_failed")
            db_manager.update_acc(SystemStates.IDLE)
            return
        
        # Log image capture success
        self.log_event("image_captured", {
            "frame_shape": frame.shape if hasattr(frame, 'shape') else "unknown",
            "timestamp": datetime.now().isoformat()
        })
        
        # Classify trash
        self.logger.info("Classifying trash...")
        trash_class = await self.classifier.process_image_with_feedback(frame)
        
        if not trash_class:
            self.logger.error("Failed to classify trash")
            self.log_event("classification_failed")
            # Show error animation
            if self.hardware:
                self.hardware.show_error_animation()
                self.log_event("error_animation_shown")
            db_manager.update_acc(SystemStates.IDLE)
            return
        
        # Log successful classification
        self.log_event("classification_success", {
            "trash_class": trash_class,
            "confidence": getattr(self.classifier, 'last_confidence', 'unknown')
        })
        
        # Set state to show trash
        db_manager.update_acc(SystemStates.SHOW_TRASH)
        
        # Wait for user confirmation
        confirmed = await self.wait_for_user_confirmation(trash_class)
        
        if confirmed:
            # Success - show reward
            db_manager.update_acc(SystemStates.REWARD)
            self.log_event("user_confirmation_success", {"trash_class": trash_class})
            
            if self.hardware:
                self.hardware.show_success_animation()
                self.log_event("success_animation_shown")
            
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
                self.log_event("image_stored", {
                    "date": today,
                    "time": hour_day,
                    "trash_class": trash_class,
                    "success": True
                })
        else:
            # Timeout or incorrect bin
            db_manager.update_acc(SystemStates.TIMEOUT)
            self.log_event("user_confirmation_failed", {"trash_class": trash_class})
            
            if self.hardware:
                self.hardware.show_error_animation()
                self.log_event("error_animation_shown")
        
        # Reset to idle after delay
        await asyncio.sleep(2)
        db_manager.update_acc(SystemStates.IDLE)
        
        # Clear LEDs
        if self.hardware:
            self.hardware.get_led_strip().clear_all()
            self.log_event("leds_cleared")
    
    async def main_loop(self):
        """Main system loop"""
        if not self.hardware:
            self.logger.error("Hardware not available, exiting")
            self.log_event("system_error", {"error": "hardware_unavailable"})
            return
        
        proximity_sensors = self.hardware.get_proximity_sensors()
        
        self.logger.info("Starting development main loop...")
        self.logger.info("Waiting for manual object detection triggers...")
        self.logger.info("Press 'o' to simulate object detection")
        self.log_event("main_loop_started")
        
        # Initial delay
        await asyncio.sleep(TimingConfig.OBJECT_DETECTION_DELAY)
        
        # Set initial state
        db_manager.update_acc(SystemStates.IDLE)
        
        while self.is_running:
            try:
                # Check for manual object detection
                if proximity_sensors.detect_object_proximity():
                    self.logger.info("Manual object detection triggered!")
                    self.log_event("object_detected", {"trigger_type": "manual"})
                    
                    # Set state to processing
                    db_manager.update_acc(SystemStates.PROCESSING)
                    
                    # Show white LEDs
                    led_strip = self.hardware.get_led_strip()
                    led_strip.set_color_all((255, 255, 255))
                    self.log_event("led_color_set", {"color": "white", "rgb": (255, 255, 255)})
                    
                    # Process the detection
                    await self.process_trash_detection()
                
                await asyncio.sleep(0.1)  # Small delay to prevent CPU overuse
                
            except KeyboardInterrupt:
                self.logger.info("Interrupted by user")
                self.log_event("user_interrupt")
                break
            except Exception as e:
                self.logger.error(f"Error in main loop: {e}")
                self.log_event("main_loop_error", {"error": str(e)})
                await asyncio.sleep(1)
    
    def start(self):
        """Start the iTrash development system"""
        self.logger.info("Starting iTrash development system...")
        self.log_event("system_starting")
        self.is_running = True
        
        # Start display
        self.start_display()
        
        # Start camera feed
        self.start_camera_feed()
        
        # Start main loop
        try:
            asyncio.run(self.main_loop())
        except KeyboardInterrupt:
            self.logger.info("System stopped by user")
            self.log_event("system_stopped", {"reason": "user_interrupt"})
        finally:
            self.stop()
    
    def stop(self):
        """Stop the iTrash development system"""
        self.logger.info("Stopping iTrash development system...")
        self.log_event("system_stopping")
        self.is_running = False
        
        # Stop camera feed
        if self.camera_feed:
            self.camera_feed.stop_feed()
            self.log_event("camera_feed_stopped")
        
        # Cleanup hardware
        if self.hardware:
            self.hardware.cleanup()
            self.log_event("hardware_cleanup")
        
        # Release camera
        if self.camera:
            self.camera.release()
            self.log_event("camera_released")
        
        # Close database connection
        db_manager.close()
        self.log_event("database_closed")
        
        self.logger.info("Development system stopped")
        self.log_event("system_stopped", {"reason": "normal_shutdown"})


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