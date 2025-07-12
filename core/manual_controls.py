"""
Manual controls module for iTrash system development and testing.
Provides keyboard triggers for proximity sensors and continuous camera feed.
"""

import cv2
import threading
import time
import logging
from pynput import keyboard
from config.settings import HardwareConfig, Colors

class ManualProximitySensors:
    """Manual proximity sensor controller using keyboard triggers"""
    
    def __init__(self):
        self.object_detected = False
        self.blue_bin_triggered = False
        self.yellow_bin_triggered = False
        self.brown_bin_triggered = False
        self.logger = logging.getLogger(__name__)
        
        # Keyboard mapping
        self.key_mapping = {
            'o': 'object_detection',      # 'o' key for main object detection
            'b': 'blue_bin',              # 'b' key for blue bin
            'y': 'yellow_bin',            # 'y' key for yellow bin
            'r': 'brown_bin',             # 'r' key for brown bin (red key)
            'c': 'clear_all'              # 'c' key to clear all triggers
        }
        
        # Start keyboard listener
        self.listener = keyboard.Listener(on_press=self._on_key_press)
        self.listener.start()
        
        self.logger.info("Manual proximity sensors initialized")
        self.logger.info("Keyboard controls:")
        self.logger.info("  'o' - Trigger main object detection")
        self.logger.info("  'b' - Trigger blue bin proximity")
        self.logger.info("  'y' - Trigger yellow bin proximity")
        self.logger.info("  'r' - Trigger brown bin proximity")
        self.logger.info("  'c' - Clear all triggers")
        self.logger.info("  'q' - Quit camera feed")
    
    def _on_key_press(self, key):
        """Handle key press events"""
        try:
            if hasattr(key, 'char') and key.char:
                key_char = key.char.lower()
                if key_char in self.key_mapping:
                    action = self.key_mapping[key_char]
                    
                    if action == 'object_detection':
                        self.object_detected = True
                        self.logger.info("🔍 Object detection triggered!")
                    elif action == 'blue_bin':
                        self.blue_bin_triggered = True
                        self.logger.info("🔵 Blue bin triggered!")
                    elif action == 'yellow_bin':
                        self.yellow_bin_triggered = True
                        self.logger.info("🟡 Yellow bin triggered!")
                    elif action == 'brown_bin':
                        self.brown_bin_triggered = True
                        self.logger.info("🟤 Brown bin triggered!")
                    elif action == 'clear_all':
                        self.clear_all_triggers()
                        self.logger.info("🧹 All triggers cleared!")
                        
        except AttributeError:
            pass
    
    def clear_all_triggers(self):
        """Clear all sensor triggers"""
        self.object_detected = False
        self.blue_bin_triggered = False
        self.yellow_bin_triggered = False
        self.brown_bin_triggered = False
        self.logger.debug("All sensor triggers cleared")
    
    def detect_object_proximity(self):
        """Detect object on the main object detection sensor"""
        if self.object_detected:
            self.object_detected = False  # Reset after detection
            self.logger.info("Object proximity detected")
            return True
        return False
    
    def detect_blue_bin(self):
        """Detect object in blue bin"""
        if self.blue_bin_triggered:
            self.blue_bin_triggered = False  # Reset after detection
            self.logger.info("Blue bin detection triggered")
            return True
        return False
    
    def detect_yellow_bin(self):
        """Detect object in yellow bin"""
        if self.yellow_bin_triggered:
            self.yellow_bin_triggered = False  # Reset after detection
            self.logger.info("Yellow bin detection triggered")
            return True
        return False
    
    def detect_brown_bin(self):
        """Detect object in brown bin"""
        if self.brown_bin_triggered:
            self.brown_bin_triggered = False  # Reset after detection
            self.logger.info("Brown bin detection triggered")
            return True
        return False
    
    def cleanup(self):
        """Clean up keyboard listener"""
        if self.listener:
            self.logger.info("Cleaning up keyboard listener")
            self.listener.stop()


class CameraFeedDisplay:
    """Continuous camera feed display with overlay information"""
    
    def __init__(self, camera_controller):
        self.camera = camera_controller
        self.is_running = False
        self.display_thread = None
        self.logger = logging.getLogger(__name__)
        self.frame_count = 0
        
    def start_feed(self):
        """Start continuous camera feed in a separate thread"""
        if not self.camera or not self.camera.is_initialized:
            self.logger.warning("Camera not available for feed display")
            return
        
        self.is_running = True
        self.display_thread = threading.Thread(target=self._display_loop, daemon=True)
        self.display_thread.start()
        self.logger.info("Camera feed started")
    
    def _display_loop(self):
        """Main display loop for camera feed"""
        window_name = "iTrash Camera Feed"
        cv2.namedWindow(window_name, cv2.WINDOW_NORMAL)
        
        # Set window size
        cv2.resizeWindow(window_name, 800, 600)
        self.logger.info(f"Camera feed window created: {window_name}")
        
        while self.is_running:
            try:
                ret, frame = self.camera.read_frame()
                if not ret:
                    self.logger.error("Failed to read frame from camera")
                    break
                
                self.frame_count += 1
                
                # Add overlay information
                frame_with_overlay = self._add_overlay(frame)
                
                # Display frame
                cv2.imshow(window_name, frame_with_overlay)
                
                # Check for quit key
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    self.logger.info("Quit key pressed, stopping camera feed")
                    break
                    
            except Exception as e:
                self.logger.error(f"Error in camera feed: {e}")
                break
        
        cv2.destroyAllWindows()
        self.logger.info(f"Camera feed stopped after {self.frame_count} frames")
    
    def _add_overlay(self, frame):
        """Add information overlay to camera frame"""
        overlay = frame.copy()
        
        # Add title
        cv2.putText(overlay, "iTrash Camera Feed", (10, 30), 
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 2)
        
        # Add instructions
        instructions = [
            "Keyboard Controls:",
            "o - Trigger object detection",
            "b - Trigger blue bin",
            "y - Trigger yellow bin", 
            "r - Trigger brown bin",
            "c - Clear all triggers",
            "q - Quit camera feed"
        ]
        
        y_offset = 70
        for instruction in instructions:
            cv2.putText(overlay, instruction, (10, y_offset), 
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
            y_offset += 25
        
        # Add frame info
        height, width = frame.shape[:2]
        frame_info = f"Frame: {width}x{height} (#{self.frame_count})"
        cv2.putText(overlay, frame_info, (10, height - 20), 
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        
        return overlay
    
    def stop_feed(self):
        """Stop camera feed"""
        self.logger.info("Stopping camera feed...")
        self.is_running = False
        if self.display_thread:
            self.display_thread.join(timeout=1)
            self.logger.info("Camera feed thread stopped")


class ManualHardwareController:
    """Manual hardware controller for development and testing"""
    
    def __init__(self, led_strip):
        self.led_strip = led_strip
        self.proximity_sensors = ManualProximitySensors()
        self.logger = logging.getLogger(__name__)
        self.animation_count = 0
    
    def get_led_strip(self):
        """Get LED strip instance"""
        return self.led_strip
    
    def get_proximity_sensors(self):
        """Get proximity sensors instance"""
        return self.proximity_sensors
    
    def cleanup(self):
        """Clean up hardware resources"""
        self.logger.info("Cleaning up manual hardware controller")
        if self.led_strip:
            self.led_strip.clear_all()
        if self.proximity_sensors:
            self.proximity_sensors.cleanup()
        self.logger.info("Manual hardware controller cleanup complete")
    
    def blink_leds(self, color, duration=1.0, interval=0.5):
        """Blink LEDs with specified color"""
        self.logger.debug(f"Blinking LEDs with color {color} for {duration}s")
        self.animation_count += 1
        
        if self.led_strip:
            start_time = time.time()
            while time.time() - start_time < duration:
                self.led_strip.set_color_all(color)
                time.sleep(interval)
                self.led_strip.clear_all()
                time.sleep(interval)
    
    def show_processing_animation(self):
        """Show processing animation"""
        self.logger.info("Showing processing animation")
        self.blink_leds((255, 255, 255), duration=2.0, interval=0.3)
    
    def show_success_animation(self):
        """Show success animation"""
        self.logger.info("Showing success animation")
        self.blink_leds((0, 255, 0), duration=1.5, interval=0.2)
    
    def show_error_animation(self):
        """Show error animation"""
        self.logger.info("Showing error animation")
        self.blink_leds((255, 0, 0), duration=1.5, interval=0.2)