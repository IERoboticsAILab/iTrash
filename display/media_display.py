"""
Simple media display module for iTrash system.
Handles image switching with fullscreen display using Pygame.
"""

import os
import time
import threading
import pygame
from pathlib import Path
from config.settings import DisplayConfig, SystemStates
from global_state import state

class SimpleMediaDisplay:
    """Simple fullscreen display interface using Pygame"""
    
    def __init__(self, images_dir="display/images"):
        self.images_dir = images_dir
        self.acc = 0
        self.is_running = False
        self.timer_thread = None
        self.screen = None
        self.screen_width = 1920
        self.screen_height = 1080
        self.image_mapping = DisplayConfig.IMAGE_MAPPING
        self.display_initialized = False
        self.last_error_time = 0
        self.error_count = 0
        
        # Initialize display
        self._init_display()
    
    def _init_display(self):
        """Initialize Pygame display"""
        try:
            # Set environment for Raspberry Pi
            os.environ['SDL_VIDEODRIVER'] = 'x11'
            os.environ['DISPLAY'] = ':0'
            
            # Additional environment variables to help with display issues
            os.environ['SDL_VIDEO_X11_NODIRECTCOLOR'] = '1'
            os.environ['SDL_VIDEO_X11_DGAMOUSE'] = '0'
            
            pygame.init()
            
            # Get screen info and set fullscreen
            info = pygame.display.Info()
            self.screen_width = info.current_w
            self.screen_height = info.current_h
            
            # Try different display modes if fullscreen fails
            display_modes = [
                ((self.screen_width, self.screen_height), pygame.FULLSCREEN),
                ((1024, 768), pygame.FULLSCREEN),
                ((800, 600), pygame.FULLSCREEN),
                ((self.screen_width, self.screen_height), 0),  # Windowed mode
                ((1024, 768), 0),
            ]
            
            for size, flags in display_modes:
                try:
                    self.screen = pygame.display.set_mode(size, flags)
                    self.screen_width, self.screen_height = size
                    break
                except Exception as e:
                    print(f"Display mode {size} with flags {flags} failed: {e}")
                    continue
            
            if self.screen:
                pygame.mouse.set_visible(False)
                self.display_initialized = True
                print(f"✅ Display initialized: {self.screen_width}x{self.screen_height}")
            else:
                print("❌ All display modes failed")
                self.display_initialized = False
                
        except Exception as e:
            print(f"❌ Display init failed: {e}")
            self.screen = None
            self.display_initialized = False
    
    def _recover_display(self, force=False):
        """Try to recover display after an error or force recovery"""
        current_time = time.time()
        
        # Don't try to recover too frequently unless forced
        if not force and current_time - self.last_error_time < 5:
            return False
        
        self.last_error_time = current_time
        self.error_count += 1
        
        if force:
            print(f"🔄 Forcing display recovery (attempt {self.error_count})")
        else:
            print(f"🔄 Attempting display recovery (attempt {self.error_count})")
        
        try:
            # Clean up existing display
            if self.screen:
                pygame.display.quit()
                self.screen = None
            
            # Reinitialize display
            self._init_display()
            
            if self.display_initialized:
                print("✅ Display recovery successful")
                return True
            else:
                print("❌ Display recovery failed")
                return False
                
        except Exception as e:
            print(f"❌ Display recovery error: {e}")
            return False
    
    def force_recovery(self):
        """Force display recovery regardless of error state"""
        return self._recover_display(force=True)
    

    
    def show_image(self, state_number, force_recovery=False):
        """Show image for given state number with optional force recovery"""
        # Force recovery if requested
        if force_recovery:
            print("🔄 Force recovery requested before showing image")
            if not self._recover_display(force=True):
                print("❌ Force recovery failed")
                return False
        
        if not self.screen or state_number not in self.image_mapping:
            return False
        
        try:
            # Get image path
            image_file = self.image_mapping[state_number]
            image_path = Path(self.images_dir) / image_file
            
            if not image_path.exists():
                print(f"❌ Image file not found: {image_path}")
                return False
            
            # Load and scale image
            img = pygame.image.load(str(image_path))
            img_width, img_height = img.get_size()
            
            # Scale to fit screen
            img_ratio = img_width / img_height
            screen_ratio = self.screen_width / self.screen_height
            
            if img_ratio > screen_ratio:
                new_width = self.screen_width
                new_height = int(self.screen_width / img_ratio)
            else:
                new_height = self.screen_height
                new_width = int(self.screen_height * img_ratio)
            
            scaled_img = pygame.transform.scale(img, (new_width, new_height))
            
            # Center image
            x = (self.screen_width - new_width) // 2
            y = (self.screen_height - new_height) // 2
            
            # Display with error handling
            try:
                self.screen.fill((0, 0, 0))
                self.screen.blit(scaled_img, (x, y))
                pygame.display.flip()
                
                print(f"✅ Displayed: {image_file}")
                return True
                
            except pygame.error as e:
                if "GL context" in str(e) or "BadAccess" in str(e):
                    print(f"🔄 GL context error, attempting recovery: {e}")
                    if self._recover_display():
                        # Retry once after recovery
                        try:
                            self.screen.fill((0, 0, 0))
                            self.screen.blit(scaled_img, (x, y))
                            pygame.display.flip()
                            print(f"✅ Displayed after recovery: {image_file}")
                            return True
                        except Exception as retry_e:
                            print(f"❌ Retry failed: {retry_e}")
                            return False
                    else:
                        return False
                else:
                    raise e
            
        except Exception as e:
            print(f"❌ Display error: {e}")
            
            # Try to recover from certain types of errors
            if "GL context" in str(e) or "BadAccess" in str(e):
                if self._recover_display():
                    # Retry the operation
                    return self.show_image(state_number)
            
            return False
    
    def set_acc(self, value):
        """Set state and update display"""
        if value in self.image_mapping:
            self.acc = value
            self.show_image(value)
    
    def monitor_state(self):
        """Monitor state changes"""
        while self.is_running:
            time.sleep(0.1)
            
            try:
                current_phase = state.get("phase", "idle")
                
                # Map phase to state
                phase_to_state = {
                    "idle": SystemStates.IDLE,
                    "processing": SystemStates.PROCESSING,
                    "show_trash": SystemStates.SHOW_TRASH,
                    "user_confirmation": SystemStates.USER_CONFIRMATION,
                    "blue_trash": SystemStates.THROW_BLUE,
                    "yellow_trash": SystemStates.THROW_YELLOW,
                    "brown_trash": SystemStates.THROW_BROWN,
                    "success": SystemStates.SUCCESS,
                    "reward": SystemStates.REWARD,
                    "incorrect": SystemStates.INCORRECT,
                    "timeout": SystemStates.TIMEOUT,
                    "error": SystemStates.USER_CONFIRMATION,  # Show try_again_green.png on error
                    "qr_codes": SystemStates.QR_CODES
                }
                
                new_state = phase_to_state.get(current_phase, 0)
                
                if new_state != self.acc:
                    self.set_acc(new_state)
                    
            except Exception as e:
                print(f"Monitor error: {e}")
    
    def start(self):
        """Start the display system"""
        if not self.display_initialized:
            print("⚠️  No display, running in headless mode")
            self.is_running = True
            self.timer_thread = threading.Thread(target=self.monitor_state, daemon=True)
            self.timer_thread.start()
            return
        
        self.is_running = True
        
        # Show initial image
        self.show_image(SystemStates.IDLE)
        
        # Start monitoring
        self.timer_thread = threading.Thread(target=self.monitor_state, daemon=True)
        self.timer_thread.start()
        
        print("✅ Display system started")
    
    def stop(self):
        """Stop the display system"""
        self.is_running = False
        
        if self.timer_thread:
            self.timer_thread.join(timeout=1)
        
        if self.screen:
            try:
                pygame.quit()
            except Exception as e:
                print(f"Warning: Error during pygame cleanup: {e}")
        
        print("✅ Display stopped")
    
    def get_status(self):
        """Get status"""
        return {
            "acc": self.acc,
            "is_running": self.is_running,
            "has_display": self.display_initialized,
            "screen": f"{self.screen_width}x{self.screen_height}",
            "error_count": self.error_count
        }


class DisplayManager:
    """Simple display manager"""
    
    def __init__(self):
        self.display = None
        self.recovery_interval = 30  # seconds between automatic recovery checks
    
    def start_display(self, images_dir="display/images"):
        """Start display"""
        try:
            self.display = SimpleMediaDisplay(images_dir)
            self.display.start()
        except Exception as e:
            print(f"Display start error: {e}")
    
    def stop_display(self):
        """Stop display"""
        if self.display:
            self.display.stop()
    
    def get_display_status(self):
        """Get status"""
        if self.display:
            return self.display.get_status()
        return {"error": "No display"}
    
    def force_recovery(self):
        """Force display recovery"""
        if self.display:
            return self.display.force_recovery()
        return False
    

    
    def show_image_with_recovery(self, state_number, force_recovery=False):
        """Show image with optional forced recovery"""
        if self.display:
            return self.display.show_image(state_number, force_recovery=force_recovery)
        return False


# Simple test function
def show_state(state_number):
    """Show a specific state"""
    display = SimpleMediaDisplay()
    if display.display_initialized:
        display.show_image(state_number)
        time.sleep(3)
    display.stop()


def test_force_recovery():
    """Test the force recovery functionality"""
    print("🔄 Testing Force Recovery Functionality")
    
    display = SimpleMediaDisplay()
    if not display.display_initialized:
        print("❌ Display not initialized, cannot test recovery")
        return
    
    print("✅ Display initialized, testing force recovery...")
    
    # Test 1: Force recovery
    print("\n1️⃣ Testing force recovery...")
    success = display.force_recovery()
    print(f"   Force recovery result: {'✅ Success' if success else '❌ Failed'}")
    
    # Test 2: Show image with force recovery
    print("\n2️⃣ Testing show image with force recovery...")
    success = display.show_image(0, force_recovery=True)
    print(f"   Show with force recovery: {'✅ Success' if success else '❌ Failed'}")
    
    display.stop()
    print("\n✅ Force recovery test completed")


if __name__ == "__main__":
    # Test force recovery functionality
    test_force_recovery()
    
    # Simple test
    print("\n🖼️  Running simple display test...")
    display = SimpleMediaDisplay()
    display.start()
    
    try:
        for state in [0, 1, 2, 3, 4]:
            display.show_image(state)
            time.sleep(2)
    except KeyboardInterrupt:
        pass
    finally:
        display.stop()


 