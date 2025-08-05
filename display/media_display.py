"""
Fullscreen media display module for iTrash system.
Handles image switching with true fullscreen display using Pygame.
"""

import os
import time
import threading
import pygame
import platform
from pathlib import Path
from config.settings import DisplayConfig, SystemStates
from global_state import state

def is_raspberry_pi():
    """Check if running on Raspberry Pi"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            return 'Raspberry Pi' in f.read()
    except:
        return platform.machine().startswith('arm')

class SimpleMediaDisplay:
    """Fullscreen display interface using Pygame"""
    
    def __init__(self, images_dir="display/images"):
        self.images_dir = images_dir
        self.acc = 0
        self.last_acc = 0
        self.is_running = False
        self.timer_thread = None
        
        # Screen dimensions (will be set on first display)
        self.screen_width = 1920
        self.screen_height = 1080
        
        # Current image path and surface
        self.current_image_path = None
        self.current_image_surface = None
        
        # Load image mapping
        self.image_mapping = DisplayConfig.IMAGE_MAPPING
        
        # Pygame will be initialized fresh for each display
        self.display_initialized = False
    
    def _initialize_display(self):
        """Initialize Pygame display for fullscreen - fresh for each display"""
        try:
            # Check if running on Raspberry Pi
            if is_raspberry_pi():
                # Set display environment for Raspberry Pi
                os.environ['SDL_VIDEODRIVER'] = 'x11'
                os.environ['DISPLAY'] = ':0'
                
                # Additional Pi-specific settings
                os.environ['SDL_AUDIODRIVER'] = 'alsa'
                os.environ['SDL_VIDEO_X11_NODIRECTCOLOR'] = '1'
            
            # Initialize Pygame fresh
            pygame.init()
            
            # Get screen info
            info = pygame.display.Info()
            self.screen_width = info.current_w
            self.screen_height = info.current_h
            
            # Set display mode to fullscreen
            self.screen = pygame.display.set_mode((self.screen_width, self.screen_height), pygame.FULLSCREEN)
            pygame.display.set_caption("iTrash Fullscreen Display")
            
            # Hide mouse cursor
            pygame.mouse.set_visible(False)
            
            self.display_initialized = True
            print(f"✅ Pygame display initialized: {self.screen_width}x{self.screen_height}")
            
        except Exception as e:
            print(f"❌ Failed to initialize Pygame display: {e}")
            self.display_initialized = False
            self.screen = None
    
    def _close_display(self):
        """Close Pygame display"""
        try:
            if self.screen:
                pygame.display.quit()
                self.screen = None
            pygame.quit()
            self.display_initialized = False
        except Exception as e:
            print(f"⚠️  Error closing display: {e}")
    
    def _reinitialize_display(self):
        """Reinitialize display if there are context issues"""
        print("🔄 Reinitializing display...")
        self._close_display()
        time.sleep(0.1)  # Small delay
        self._initialize_display()
    
    def _load_and_scale_image(self, image_path):
        """Load and scale image to fit screen while maintaining aspect ratio"""
        try:
            # Load image
            img = pygame.image.load(str(image_path))
            
            # Get image dimensions
            img_width, img_height = img.get_size()
            
            # Calculate scaling to fit screen
            img_ratio = img_width / img_height
            screen_ratio = self.screen_width / self.screen_height
            
            if img_ratio > screen_ratio:
                # Image is wider than screen
                new_width = self.screen_width
                new_height = int(self.screen_width / img_ratio)
            else:
                # Image is taller than screen
                new_height = self.screen_height
                new_width = int(self.screen_height * img_ratio)
            
            # Scale image
            scaled_img = pygame.transform.scale(img, (new_width, new_height))
            
            # Calculate position to center
            x = (self.screen_width - new_width) // 2
            y = (self.screen_height - new_height) // 2
            
            return scaled_img, (x, y)
            
        except Exception as e:
            print(f"❌ Error loading/scaling image: {e}")
            return None, (0, 0)
    
    def _display_image(self, image_surface, position):
        """Display image on screen"""
        if not self.display_initialized or not self.screen:
            return False
        
        try:
            # Clear screen with black
            self.screen.fill((0, 0, 0))
            
            # Draw image
            self.screen.blit(image_surface, position)
            
            # Update display
            pygame.display.flip()
            
            return True
            
        except Exception as e:
            print(f"❌ Error displaying image: {e}")
            return False
    
    def show_image(self, state_number):
        """Show image for given state number in fullscreen"""
        if state_number not in self.image_mapping:
            print(f"Unknown state: {state_number}")
            return False
        
        image_file = self.image_mapping[state_number]
        source_path = Path(self.images_dir) / image_file
        
        if not source_path.exists():
            print(f"Image file not found: {source_path}")
            return False

        # Initialize display if not already initialized
        if not self.display_initialized:
            self._initialize_display()
            
            if not self.display_initialized:
                print(f"❌ Failed to initialize display for: {image_file}")
                return False
        
        try:
            # Load and scale image
            image_surface, position = self._load_and_scale_image(source_path)
            
            if image_surface is None:
                print(f"Failed to load image: {image_file}")
                return False
            
            # Display image
            success = self._display_image(image_surface, position)
            
            if success:
                # Update current image info
                self.current_image_path = str(source_path)
                self.current_image_surface = image_surface
                print(f"✅ Displayed: {image_file} (State: {state_number})")
                return True
            else:
                # Try to reinitialize display if display failed
                print(f"Display failed, trying to reinitialize...")
                self._reinitialize_display()
                
                # Try display again
                success = self._display_image(image_surface, position)
                if success:
                    self.current_image_path = str(source_path)
                    self.current_image_surface = image_surface
                    print(f"✅ Displayed after reinit: {image_file} (State: {state_number})")
                    return True
                else:
                    print(f"Failed to display image even after reinit: {image_file}")
                    return False
                
        except Exception as e:
            print(f"❌ Error in show_image: {e}")
            # Try to reinitialize on any error
            if "context" in str(e).lower() or "badaccess" in str(e).lower():
                print("🔄 Context error detected, reinitializing display...")
                self._reinitialize_display()
            return False
    
    def set_acc(self, value):
        """Set accumulator value and update display"""
        if value in self.image_mapping:
            self.acc = value
            if self.display_initialized:
                self.show_image(value)
            else:
                # Log state change even without display
                image_file = self.image_mapping.get(value, "unknown.png")
                print(f"📝 State change (no display): {value} -> {image_file}")
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
                    "idle": SystemStates.IDLE,
                    "processing": SystemStates.PROCESSING,
                    "show_trash": SystemStates.SHOW_TRASH,
                    "user_confirmation": SystemStates.USER_CONFIRMATION,
                    "success": SystemStates.SUCCESS,
                    "reward": SystemStates.REWARD,
                    "incorrect": SystemStates.INCORRECT,
                    "timeout": SystemStates.TIMEOUT,
                    "error": SystemStates.INCORRECT,  # Use incorrect state for errors
                    "qr_codes": SystemStates.QR_CODES
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
        # Initialize display if not already initialized
        if not self.display_initialized:
            self._initialize_display()
        
        if not self.display_initialized:
            print("⚠️  Display not initialized, but continuing without display")
            self.is_running = True
            # Start monitoring thread even without display
            self.timer_thread = threading.Thread(target=self.monitor_state)
            self.timer_thread.daemon = True
            self.timer_thread.start()
            print("✅ Display system started (headless mode)")
            return
        
        self.is_running = True
        
        # Show initial image
        self.show_image(SystemStates.IDLE)
        
        # Start monitoring thread
        self.timer_thread = threading.Thread(target=self.monitor_state)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
        print("✅ Fullscreen display system started")
        print("🖼️  Images are now displayed in fullscreen mode")
        print("💡 Press ESC to exit fullscreen mode")
    
    def stop(self):
        """Stop the display system"""
        self.is_running = False
        
        if self.timer_thread:
            self.timer_thread.join(timeout=1)
        
        # Cleanup any remaining Pygame
        self._close_display()
        
        print("✅ Fullscreen display system stopped")
    
    def get_status(self):
        """Get current status"""
        return {
            "acc": self.acc,
            "current_image": self.current_image_path,
            "is_running": self.is_running,
            "display_initialized": self.display_initialized,
            "screen_dimensions": f"{self.screen_width}x{self.screen_height}"
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
    if display.display_initialized:
        display.show_image(state_number)
        print(f"Showing state {state_number}. Image displayed in fullscreen.")
        
        # Keep display open for a few seconds
        time.sleep(3)
        display.stop()
    else:
        print(f"Display not initialized. Cannot show state {state_number}.")


if __name__ == "__main__":
    # Test the display system
    display = SimpleMediaDisplay()
    
    if display.display_initialized:
        display.start()
        
        try:
            # Test different states
            for state in [0, 1, 2, 3, 4]:
                print(f"\nTesting state {state}...")
                display.show_image(state)
                time.sleep(3)  # Show each state for 3 seconds
        except KeyboardInterrupt:
            print("\nStopping display...")
        finally:
            display.stop()
    else:
        print("❌ Display initialization failed")


 