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
            else:
                self.display_initialized = False
                
        except Exception as e:
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
        
        try:
            # Clean up existing display
            if self.screen:
                pygame.display.quit()
                self.screen = None
            
            # Reinitialize display
            self._init_display()
            
            return self.display_initialized
                
        except Exception as e:
            return False
    
    def force_recovery(self):
        """Force display recovery regardless of error state"""
        return self._recover_display(force=True)
    

    
    def show_image(self, state_number, force_recovery=False):
        """Show image for given state number with optional force recovery"""
        # Force recovery if requested
        if force_recovery:
            if not self._recover_display(force=True):
                return False
        
        if not self.screen or state_number not in self.image_mapping:
            return False
        
        try:
            # Get image path
            image_file = self.image_mapping[state_number]
            image_path = Path(self.images_dir) / image_file
            
            if not image_path.exists():
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
                return True
                
            except pygame.error as e:
                if "GL context" in str(e) or "BadAccess" in str(e):
                    if self._recover_display():
                        # Retry once after recovery
                        try:
                            self.screen.fill((0, 0, 0))
                            self.screen.blit(scaled_img, (x, y))
                            pygame.display.flip()
                            return True
                        except Exception as retry_e:
                            return False
                    else:
                        return False
                else:
                    raise e
            
        except Exception as e:
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
            
            # Update LED color based on the new display state
            self._update_led_color_for_state(value)
    
    def monitor_state(self):
        """Monitor state changes"""
        # Ensure initial state is set
        if self.acc == 0:
            self.set_acc(SystemStates.IDLE)
        
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
                    "qrcode": SystemStates.QR_CODES,
                    "incorrect": SystemStates.INCORRECT,
                    "timeout": SystemStates.TIMEOUT,
                    "error": SystemStates.USER_CONFIRMATION,  # Show try_again_green.png on error
                    "qr_codes": SystemStates.QR_CODES
                }
                
                new_state = phase_to_state.get(current_phase, 0)
                
                if new_state != self.acc:
                    # Update LED color based on new phase before changing display
                    self._update_led_color(current_phase)
                    self.set_acc(new_state)
                    
            except Exception as e:
                print(f"Monitor error: {e}")
    
    def start(self):
        """Start the display system"""
        if not self.display_initialized:
            self.is_running = True
            self.timer_thread = threading.Thread(target=self.monitor_state, daemon=True)
            self.timer_thread.start()
            return
        
        self.is_running = True
        
        # Start monitoring first
        self.timer_thread = threading.Thread(target=self.monitor_state, daemon=True)
        self.timer_thread.start()
        
        # Small delay to ensure monitor is running
        time.sleep(0.1)
        
        # Show initial image after monitor is active
        self.show_image(SystemStates.IDLE)
        
        # Set initial LED color for idle state
        self._update_led_color_for_state(SystemStates.IDLE)
    
    def stop(self):
        """Stop the display system"""
        self.is_running = False
        
        if self.timer_thread:
            self.timer_thread.join(timeout=1)
        
        if self.screen:
            try:
                pygame.quit()
            except Exception as e:
                pass
    
    def _update_led_color(self, phase):
        """Update LED color based on current phase - synchronized with display images"""
        try:
            # Import here to avoid circular imports
            from core.hardware_loop import get_hardware_loop
            
            hardware_loop = get_hardware_loop()
            if hardware_loop and hardware_loop.hardware:
                led_strip = hardware_loop.hardware.get_led_strip()
                if led_strip:
                    # Map phases to LED colors - synchronized with display images
                    phase_colors = {
                        # Idle state - white.png
                        "idle": (0, 0, 0),                    # Off (clean white screen)
                        
                        # Processing state - processing_new.png
                        "processing": (255, 255, 255),        # White (processing indicator)
                        
                        # Show trash state - show_trash.png
                        "show_trash": (255, 255, 255),        # White (show trash indicator)
                        
                        # User confirmation state - try_again_green.png (error case)
                        "user_confirmation": (255, 0, 0),     # Red (error indicator)
                        
                        # Success state - great_job.png
                        "success": (0, 255, 0),               # Green (success indicator)
                        
                        # QR codes state - qr_codes.png
                        "qr_codes": (0, 0, 255),              # Blue (QR code indicator)
                        
                        # QR code phase - qr_codes.png (LEDs off)
                        "qrcode": (0, 0, 0),                  # Off (QR code display)
                        
                        # Reward state - reward_received_new.png
                        "reward": (0, 255, 0),                # Green (reward indicator)
                        
                        # Incorrect state - incorrect_new.png
                        "incorrect": (255, 0, 0),             # Red (incorrect indicator)
                        
                        # Timeout state - timeout_new.png
                        "timeout": (255, 0, 0),               # Red (timeout indicator)
                        
                        # Trash-specific states
                        "blue_trash": (0, 0, 255),            # Blue (throw_blue.png)
                        "yellow_trash": (255, 255, 0),        # Yellow (throw_yellow.png)
                        "brown_trash": (139, 69, 19),         # Brown (throw_brown.png)
                        
                        # Error state - try_again_green.png
                        "error": (255, 0, 0),                 # Red (error indicator)
                    }
                    
                    # Clear LEDs first to ensure clean transition
                    led_strip.clear_all()
                    
                    color = phase_colors.get(phase, (0, 0, 0))
                    led_strip.set_color_all(color)
        except Exception as e:
            # Silently fail if LED control is not available
            pass
    
    def _update_led_color_for_state(self, state_value):
        """Update LED color based on display state value - synchronized with images"""
        try:
            # Import here to avoid circular imports
            from core.hardware_loop import get_hardware_loop
            from config.settings import SystemStates
            
            hardware_loop = get_hardware_loop()
            if hardware_loop and hardware_loop.hardware:
                led_strip = hardware_loop.hardware.get_led_strip()
                if led_strip:
                    # Map display states to LED colors - synchronized with images
                    state_colors = {
                        # State 0 - white.png (idle)
                        SystemStates.IDLE: (0, 0, 0),                    # Off
                        
                        # State 1 - processing_new.png
                        SystemStates.PROCESSING: (255, 255, 255),        # White
                        
                        # State 2 - show_trash.png
                        SystemStates.SHOW_TRASH: (255, 255, 255),        # White
                        
                        # State 3 - try_again_green.png (error/retry)
                        SystemStates.USER_CONFIRMATION: (255, 0, 0),     # Red
                        
                        # State 4 - great_job.png (success)
                        SystemStates.SUCCESS: (0, 255, 0),               # Green
                        
                        # State 5 - qr_codes.png
                        SystemStates.QR_CODES: (0, 0, 255),              # Blue
                        
                        # State 6 - reward_received_new.png
                        SystemStates.REWARD: (0, 255, 0),                # Green
                        
                        # State 7 - incorrect_new.png
                        SystemStates.INCORRECT: (255, 0, 0),             # Red
                        
                        # State 8 - timeout_new.png
                        SystemStates.TIMEOUT: (255, 0, 0),               # Red
                        
                        # State 9 - throw_yellow.png
                        SystemStates.THROW_YELLOW: (255, 255, 0),        # Yellow
                        
                        # State 10 - throw_blue.png
                        SystemStates.THROW_BLUE: (0, 0, 255),            # Blue
                        
                        # State 11 - throw_brown.png
                        SystemStates.THROW_BROWN: (139, 69, 19),         # Brown
                    }
                    
                    # Clear LEDs first to ensure clean transition
                    led_strip.clear_all()
                    
                    color = state_colors.get(state_value, (0, 0, 0))
                    led_strip.set_color_all(color)
        except Exception as e:
            # Silently fail if LED control is not available
            pass
    
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


 