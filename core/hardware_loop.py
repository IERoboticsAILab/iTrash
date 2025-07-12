"""
Background hardware loop for iTrash unified system.
Runs sensor detection and hardware control in a separate thread.
"""

import threading
import time
import asyncio
from typing import Optional
from datetime import datetime

from global_state import state
from core.hardware import HardwareController
from core.camera import CameraController
from core.ai_classifier import ClassificationManager
from config.settings import TimingConfig

class HardwareLoop:
    """Background hardware loop manager"""
    
    def __init__(self):
        self.is_running = False
        self.thread = None
        self.hardware: Optional[HardwareController] = None
        self.camera: Optional[CameraController] = None
        self.classifier: Optional[ClassificationManager] = None
        
        # Initialize components
        self._initialize_components()
    
    def _initialize_components(self):
        """Initialize hardware components"""
        print("Initializing hardware components...")
        
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
    
    def _hardware_loop(self):
        """Main hardware loop"""
        if not self.hardware:
            print("Hardware not available, exiting hardware loop")
            return
        
        proximity_sensors = self.hardware.get_proximity_sensors()
        led_strip = self.hardware.get_led_strip()
        
        print("Hardware loop started - monitoring sensors...")
        
        # Initial delay
        time.sleep(TimingConfig.OBJECT_DETECTION_DELAY)
        
        # Set initial state
        state.update("phase", "idle")
        state.update("system_status", "running")
        
        while self.is_running:
            try:
                # Check for object detection
                if proximity_sensors.detect_object_proximity():
                    print("Object detected in hardware loop!")
                    
                    # Update state
                    state.update("phase", "processing")
                    state.update_sensor_status("object_detected", True)
                    
                    # Show white LEDs
                    led_strip.set_color_all((255, 255, 255))
                    
                    # Process the detection
                    self._process_trash_detection()
                
                # Check bin sensors
                self._check_bin_sensors(proximity_sensors)
                
                # Small delay to prevent CPU overuse
                time.sleep(0.1)
                
            except Exception as e:
                print(f"Error in hardware loop: {e}")
                time.sleep(1)
    
    def _check_bin_sensors(self, proximity_sensors):
        """Check bin sensors and update state"""
        # Check blue bin
        if proximity_sensors.detect_blue_bin():
            state.update_sensor_status("blue_bin", True)
            self._handle_bin_detection("blue")
        else:
            state.update_sensor_status("blue_bin", False)
        
        # Check yellow bin
        if proximity_sensors.detect_yellow_bin():
            state.update_sensor_status("yellow_bin", True)
            self._handle_bin_detection("yellow")
        else:
            state.update_sensor_status("yellow_bin", False)
        
        # Check brown bin
        if proximity_sensors.detect_brown_bin():
            state.update_sensor_status("brown_bin", True)
            self._handle_bin_detection("brown")
        else:
            state.update_sensor_status("brown_bin", False)
    
    def _handle_bin_detection(self, bin_type: str):
        """Handle bin detection"""
        current_phase = state.get("phase")
        last_classification = state.get("last_classification")
        
        # Only process if we're in user confirmation phase
        if current_phase == "user_confirmation":
            if last_classification == bin_type:
                # Correct bin!
                state.update("reward", True)
                state.update("phase", "reward")
                print(f"Correct bin detected: {bin_type}")
                
                # Show success animation
                if self.hardware:
                    self.hardware.show_success_animation()
                
                # Auto-reset after delay
                def auto_reset():
                    import time
                    time.sleep(2)  # Show reward for 2 seconds
                    state.update("phase", "idle")
                    state.update("reward", False)
                    state.update("last_classification", None)
                    
                    # Clear LEDs
                    if self.hardware:
                        try:
                            self.hardware.get_led_strip().clear_all()
                        except:
                            pass
                
                # Start auto-reset in separate thread
                import threading
                reset_thread = threading.Thread(target=auto_reset, daemon=True)
                reset_thread.start()
                
            else:
                # Wrong bin
                state.update("phase", "incorrect")
                print(f"Incorrect bin detected: {bin_type}, expected: {last_classification}")
                
                # Show error animation
                if self.hardware:
                    self.hardware.show_error_animation()
                
                # Auto-reset after delay
                def auto_reset():
                    import time
                    time.sleep(2)  # Show error for 2 seconds
                    state.update("phase", "idle")
                    state.update("reward", False)
                
                # Start auto-reset in separate thread
                import threading
                reset_thread = threading.Thread(target=auto_reset, daemon=True)
                reset_thread.start()
    
    def _process_trash_detection(self):
        """Process trash detection and classification"""
        if not self.camera or not self.classifier:
            print("Camera or classifier not available")
            state.update("phase", "error")
            return
        
        try:
            # Capture image
            frame = self.camera.capture_image()
            if frame is None:
                print("Failed to capture image")
                state.update("phase", "error")
                return
            
            # Classify trash (run in thread to avoid blocking)
            def classify_async():
                try:
                    # Run classification in event loop
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    
                    result = loop.run_until_complete(
                        self.classifier.process_image_with_feedback(frame)
                    )
                    
                    if result:
                        state.update("last_classification", result)
                        state.update("phase", "user_confirmation")
                        print(f"Classification result: {result}")
                        
                        # Show appropriate LED color
                        led_strip = self.hardware.get_led_strip() if self.hardware else None
                        if led_strip:
                            if result == "blue":
                                led_strip.set_color_all((0, 0, 255))
                            elif result == "yellow":
                                led_strip.set_color_all((255, 255, 0))
                            elif result == "brown":
                                led_strip.set_color_all((139, 69, 19))
                    else:
                        state.update("phase", "error")
                        print("Classification failed")
                        
                except Exception as e:
                    print(f"Error in classification: {e}")
                    state.update("phase", "error")
                finally:
                    loop.close()
            
            # Start classification in separate thread
            classify_thread = threading.Thread(target=classify_async, daemon=True)
            classify_thread.start()
            
        except Exception as e:
            print(f"Error in trash detection: {e}")
            state.update("phase", "error")
    
    def start(self):
        """Start the hardware loop"""
        if self.is_running:
            print("Hardware loop already running")
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._hardware_loop, daemon=True)
        self.thread.start()
        print("Hardware loop started")
    
    def stop(self):
        """Stop the hardware loop"""
        self.is_running = False
        
        # Clear LEDs
        if self.hardware:
            try:
                self.hardware.get_led_strip().clear_all()
            except:
                pass
        
        # Cleanup hardware
        if self.hardware:
            try:
                self.hardware.cleanup()
            except:
                pass
        
        # Release camera
        if self.camera:
            try:
                self.camera.release()
            except:
                pass
        
        print("Hardware loop stopped")

# Global hardware loop instance
hardware_loop: Optional[HardwareLoop] = None

def start_hardware_loop():
    """Start the background hardware loop"""
    global hardware_loop
    hardware_loop = HardwareLoop()
    hardware_loop.start()
    return hardware_loop

def stop_hardware_loop():
    """Stop the background hardware loop"""
    global hardware_loop
    if hardware_loop:
        hardware_loop.stop()
        hardware_loop = None

def get_hardware_loop() -> Optional[HardwareLoop]:
    """Get the hardware loop instance"""
    return hardware_loop 