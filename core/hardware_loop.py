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
        # Initialize hardware
        try:
            self.hardware = HardwareController()
        except Exception as e:
            print(f"Error initializing hardware: {e}")
            self.hardware = None
        
        # Initialize camera
        try:
            self.camera = CameraController()
            if not self.camera.initialize():
                print("Warning: Camera initialization failed")
                self.camera = None
        except Exception as e:
            print(f"Error initializing camera: {e}")
            self.camera = None
        
        # Initialize classifier
        try:
            led_strip = self.hardware.get_led_strip() if self.hardware else None
            self.classifier = ClassificationManager(led_strip)
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
        
        # Initial delay
        time.sleep(TimingConfig.OBJECT_DETECTION_DELAY)
        
        # Set initial state
        state.update("phase", "idle")
        state.update("system_status", "running")
        
        while self.is_running:
            try:
                # Get current phase to check if we should block object detection
                current_phase = state.get("phase")
                
                # Only check for object detection if we're in idle phase
                # This prevents re-detection while processing or waiting for user confirmation
                if current_phase == "idle" and proximity_sensors.detect_object_proximity():
                    # Add delay before processing
                    time.sleep(TimingConfig.IDLE_TO_PROCESSING_DELAY)
                    
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
        
        # Check if we're in one of the trash-specific phases
        trash_phases = ["blue_trash", "yellow_trash", "brown_trash"]
        
        if current_phase in trash_phases:
            # Map phase to expected bin type
            phase_to_bin = {
                "blue_trash": "blue",
                "yellow_trash": "yellow", 
                "brown_trash": "brown"
            }
            
            expected_bin = phase_to_bin.get(current_phase)
            
            if bin_type == expected_bin:
                # Correct bin!
                state.update("reward", True)
                state.update("phase", "reward")
                
                # Show success animation
                if self.hardware:
                    self.hardware.show_success_animation()
                
                # Auto-reset after delay
                def auto_reset():
                    import time
                    time.sleep(TimingConfig.REWARD_DISPLAY_TIME)  # Show reward for configured time
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
                
                # Show error animation
                if self.hardware:
                    self.hardware.show_error_animation()
                
                # Auto-reset for incorrect bin
                def auto_reset():
                    import time
                    time.sleep(TimingConfig.INCORRECT_DISPLAY_TIME)  # Show error for configured time
                    state.update("phase", "idle")
                    state.update("reward", False)
                    
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
                    if result and result in ["blue", "yellow", "brown"]:
                        state.update("last_classification", result)
                        
                        # Add delay before showing result
                        time.sleep(TimingConfig.PROCESSING_TO_RESULT_DELAY)
                        
                        # Show appropriate LED color and set specific phase
                        led_strip = self.hardware.get_led_strip() if self.hardware else None
                        if led_strip:
                            if result == "blue":
                                led_strip.set_color_all((0, 0, 255))
                                state.update("phase", "blue_trash")
                            elif result == "yellow":
                                led_strip.set_color_all((255, 255, 0))
                                state.update("phase", "yellow_trash")
                            elif result == "brown":
                                led_strip.set_color_all((139, 69, 19))
                                state.update("phase", "brown_trash")
                    else:
                        # Classification failed or invalid result - show try_again_green
                        state.update("phase", "error")
                        
                        # Clear LEDs
                        if self.hardware:
                            try:
                                self.hardware.get_led_strip().clear_all()
                            except:
                                pass
                        
                except Exception as e:
                    state.update("phase", "error")
                    
                    # Clear LEDs
                    if self.hardware:
                        try:
                            self.hardware.get_led_strip().clear_all()
                        except:
                            pass
                finally:
                    loop.close()
            
            # Start classification in separate thread with timeout
            classify_thread = threading.Thread(target=classify_async, daemon=True)
            classify_thread.start()
            
            # Set a timeout for classification (30 seconds)
            classify_thread.join(timeout=30)
            
            # If thread is still alive after timeout, show try_again_green
            if classify_thread.is_alive():
                state.update("phase", "error")
                
                # Clear LEDs
                if self.hardware:
                    try:
                        self.hardware.get_led_strip().clear_all()
                    except:
                        pass
            
        except Exception as e:
            state.update("phase", "error")
            
            # Clear LEDs
            if self.hardware:
                try:
                    self.hardware.get_led_strip().clear_all()
                except:
                    pass
    
    def start(self):
        """Start the hardware loop"""
        if self.is_running:
            return
        
        self.is_running = True
        self.thread = threading.Thread(target=self._hardware_loop, daemon=True)
        self.thread.start()
    
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