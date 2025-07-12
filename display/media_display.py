"""
Simple media display module for iTrash system.
Handles image switching without complex GUI.
"""

import os
import time
import shutil
import threading
from config.settings import DisplayConfig, SystemStates
from api.state import state

class SimpleMediaDisplay:
    """Simple display interface that copies images to standard location"""
    
    def __init__(self, images_dir="display/images"):
        self.images_dir = images_dir
        self.acc = 0
        self.last_acc = 0
        self.is_running = False
        self.timer_thread = None
        
        # Standard location for current image
        self.current_image_path = "/tmp/itrash_current.png"
        
        # Load image mapping
        self.image_mapping = DisplayConfig.IMAGE_MAPPING
        
        # Initialize state connection
        pass
    
    def show_image(self, state_number):
        """Show image for given state number"""
        if state_number not in self.image_mapping:
            print(f"Unknown state: {state_number}")
            return False
        
        image_file = self.image_mapping[state_number]
        source_path = os.path.join(self.images_dir, image_file)
        
        if not os.path.exists(source_path):
            print(f"Image file not found: {source_path}")
            return False
        
        try:
            # Copy image to standard location
            shutil.copy2(source_path, self.current_image_path)
            print(f"Displaying: {image_file} (State: {state_number})")
            return True
        except Exception as e:
            print(f"Error copying image: {e}")
            return False
    
    def set_acc(self, value):
        """Set accumulator value and update display"""
        if value in self.image_mapping:
            self.acc = value
            self.show_image(value)
        else:
            print(f"Invalid state: {value}")
    
    def monitor_state(self):
        """Monitor local state for phase changes"""
        phase_timer = None
        
        while self.is_running:
            time.sleep(0.1)
            
            try:
                current_phase = state.get("phase", "idle")
                
                # Map phase to state number
                phase_to_state = {
                    "idle": 0,
                    "processing": 1,
                    "show_trash": 2,
                    "user_confirmation": 3,
                    "reward": 4,
                    "timeout": 5,
                    "error": 6
                }
                
                new_state = phase_to_state.get(current_phase, 0)
                
                if new_state != self.acc:
                    self.set_acc(new_state)
                    
                    # Handle timeout for user confirmation (state 3)
                    if current_phase == "user_confirmation":
                        if phase_timer is None:
                            phase_timer = time.time()
                        elif time.time() - phase_timer >= 10:  # 10 second timeout
                            state.update("phase", "idle")
                            phase_timer = None
                    else:
                        phase_timer = None
                        
            except Exception as e:
                print(f"Error monitoring state: {e}")
                time.sleep(1)
    
    def start(self):
        """Start the display system"""
        self.is_running = True
        
        # Show initial image
        self.show_image(SystemStates.IDLE)
        
        # Start monitoring thread
        self.timer_thread = threading.Thread(target=self.monitor_state)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
        print("Simple display system started")
        print(f"Current image location: {self.current_image_path}")
        print("Use any image viewer to display this file in fullscreen")
    
    def stop(self):
        """Stop the display system"""
        self.is_running = False
        if self.timer_thread:
            self.timer_thread.join(timeout=1)
        print("Simple display system stopped")
    
    def get_status(self):
        """Get current status"""
        return {
            "acc": self.acc,
            "current_image": self.current_image_path,
            "is_running": self.is_running
        }


class DisplayManager:
    """Manager for display operations"""
    
    def __init__(self):
        self.display = None
    
    def start_display(self, images_dir="display/images"):
        """Start the display system"""
        try:
            self.display = SimpleMediaDisplay(images_dir)
            self.display.start()
        except Exception as e:
            print(f"Error starting display: {e}")
    
    def stop_display(self):
        """Stop the display system"""
        if self.display:
            self.display.stop()
    
    def get_display_status(self):
        """Get display status"""
        if self.display:
            return self.display.get_status()
        return {"error": "Display not initialized"}


# Utility function to manually show specific states
def show_state(state_number):
    """Utility function to manually show a specific state"""
    display = SimpleMediaDisplay()
    display.show_image(state_number)
    print(f"Showing state {state_number}. Image available at: {display.current_image_path}")


if __name__ == "__main__":
    # Test the display system
    display = SimpleMediaDisplay()
    display.start()
    
    try:
        # Test different states
        for state in [0, 1, 2, 3, 4]:
            print(f"\nTesting state {state}...")
            display.show_image(state)
            time.sleep(2)
    except KeyboardInterrupt:
        print("\nStopping display...")
    finally:
        display.stop()


 