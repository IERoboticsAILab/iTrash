"""
Simple media display module for iTrash system.
Handles image switching with fullscreen display using Pygame.
"""

import os
import time
import threading
import pygame
import cv2
from pathlib import Path
import logging
from config.settings import DisplayConfig, SystemStates
from global_state import state

logger = logging.getLogger(__name__)

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
        self.preloaded_images = {}
        self.display_initialized = False
        self.last_error_time = 0
        self.error_count = 0
        
        # Rendering state (single-thread, driven from main thread)
        self.current_mode = "image"  # 'image' or 'video'
        self._needs_clear = True
        
        # Idle video support (handled inside render loop only)
        self.video_path = self._resolve_idle_video_path()
        self.video_cap = None
        self.video_fps = 30.0
        self.video_delay = 1.0 / 30.0
        self._last_video_ts = 0.0
        
        # Initialize display
        self._init_display()
        
        # LED updates occur only on state changes
    
    def _init_display(self):
        """Initialize Pygame display"""
        try:
            # Force X11 driver as requested and set sane defaults
            os.environ['SDL_VIDEODRIVER'] = 'x11'
            os.environ['DISPLAY'] = os.environ.get('DISPLAY', ':0')
            os.environ['SDL_VIDEO_X11_NODIRECTCOLOR'] = '1'
            os.environ['SDL_VIDEO_X11_DGAMOUSE'] = '0'
            pygame.display.init()
            
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
                    # Prefer double buffering and hardware surface when available
                    self.screen = pygame.display.set_mode(
                        size, flags | pygame.DOUBLEBUF | pygame.HWSURFACE
                    )
                    self.screen_width, self.screen_height = size
                    break
                except Exception as e:
                    logger.warning("Display mode %s with flags %s failed: %s", size, flags, e)
                    continue
            
            if self.screen:
                pygame.mouse.set_visible(False)
                self.display_initialized = True
                # Preload images for current screen size
                self._preload_images()
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
        """Request showing a given state; actual drawing happens in render loop."""
        if force_recovery:
            if not self._recover_display(force=True):
                return False
        if state_number in self.image_mapping:
            self.acc = state_number
            return True
        return False

    def _preload_images(self):
        """Preload and scale images to memory for fast, seamless transitions."""
        preloaded = {}
        for state_number, image_file in self.image_mapping.items():
            try:
                image_path = Path(self.images_dir) / image_file
                if not image_path.exists():
                    continue
                img = pygame.image.load(str(image_path)).convert()
                img_width, img_height = img.get_size()
                img_ratio = img_width / img_height
                screen_ratio = self.screen_width / self.screen_height
                if img_ratio > screen_ratio:
                    new_width = self.screen_width
                    new_height = int(self.screen_width / img_ratio)
                else:
                    new_height = self.screen_height
                    new_width = int(self.screen_height * img_ratio)
                scaled_img = pygame.transform.smoothscale(img, (new_width, new_height))
                x = (self.screen_width - new_width) // 2
                y = (self.screen_height - new_height) // 2
                preloaded[state_number] = (scaled_img, x, y)
            except Exception:
                continue
        self.preloaded_images = preloaded

    def _get_preloaded_surface(self, state_number):
        """Return a tuple (surface, x, y) for the given state, if preloaded."""
        return self.preloaded_images.get(state_number, (None, None, None))
    
    def _resolve_idle_video_path(self):
        """Resolve the path to the idle video, preferring repo-relative path."""
        try:
            # Prefer repo-relative location
            rel_path = Path("display/videos/intro.mp4")
            if rel_path.exists():
                return str(rel_path)
            
        except Exception:
            pass
        return None

    def _open_video(self):
        if not self.video_path or not self.display_initialized:
            return False
        if self.video_cap is None:
            cap = cv2.VideoCapture(self.video_path)
            if not cap.isOpened():
                return False
            fps = cap.get(cv2.CAP_PROP_FPS) or 30.0
            self.video_cap = cap
            self.video_fps = float(fps)
            self.video_delay = max(1.0 / self.video_fps, 0.01)
        return True

    def _close_video(self):
        if self.video_cap is not None:
            try:
                self.video_cap.release()
            except Exception:
                pass
            self.video_cap = None

    def tick(self):
        """Render one frame based on current global phase. Must be called from main thread."""
        if not self.is_running or not self.display_initialized:
            return
        try:
            # Determine desired state from global phase
            current_phase = state.get("phase", "idle")
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
                "error": SystemStates.USER_CONFIRMATION,
                "qr_codes": SystemStates.QR_CODES,
            }
            desired_state = phase_to_state.get(current_phase, SystemStates.IDLE)

            # Handle state change
            if desired_state != self.acc:
                self.acc = desired_state
                # Apply LED on every state change (safe no-op if hardware not ready)
                self._update_led_color_for_state(self.acc)
                if self.acc == SystemStates.IDLE and self.video_path:
                    if self.current_mode != "video":
                        self._open_video()
                        self.current_mode = "video"
                        self._needs_clear = True
                else:
                    if self.current_mode == "video":
                        self._close_video()
                    self.current_mode = "image"
                    self._needs_clear = True
            else:
                # No state change; do not reapply LEDs
                pass

            # Render one frame
            if self.current_mode == "video" and self.video_cap is not None:
                now = time.time()
                if now - self._last_video_ts < self.video_delay:
                    return
                ok, frame = self.video_cap.read()
                if not ok:
                    try:
                        self.video_cap.set(cv2.CAP_PROP_POS_FRAMES, 0)
                        return
                    except Exception:
                        self._close_video()
                        self._open_video()
                        return
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                h, w = frame_rgb.shape[:2]
                img_ratio = w / h
                screen_ratio = self.screen_width / self.screen_height
                if img_ratio > screen_ratio:
                    new_w = self.screen_width
                    new_h = int(self.screen_width / img_ratio)
                else:
                    new_h = self.screen_height
                    new_w = int(self.screen_height * img_ratio)
                try:
                    surf = pygame.image.frombuffer(frame_rgb.tobytes(), (w, h), 'RGB')
                    surf = pygame.transform.smoothscale(surf, (new_w, new_h))
                    x = (self.screen_width - new_w) // 2
                    y = (self.screen_height - new_h) // 2
                    if self._needs_clear:
                        self.screen.fill((0, 0, 0))
                        self._needs_clear = False
                    self.screen.blit(surf, (x, y))
                    pygame.display.flip()
                    pygame.event.pump()
                    self._last_video_ts = now
                except Exception:
                    if self._recover_display():
                        self._preload_images()
                    return
            else:
                surf, x, y = self._get_preloaded_surface(self.acc)
                if surf is not None:
                    try:
                        if self._needs_clear:
                            self.screen.fill((0, 0, 0))
                            self._needs_clear = False
                        self.screen.blit(surf, (x, y))
                        pygame.display.flip()
                        pygame.event.pump()
                    except Exception:
                        if self._recover_display():
                            self._preload_images()
                        return
        finally:
            # Nothing to clean per-tick
            pass


    def set_acc(self, value):
        """Set state and update display"""
        if value in self.image_mapping:
            self.acc = value
            # Update LED color based on the new display state
            self._update_led_color_for_state(value)
    
    def monitor_state(self):
        """Deprecated: state monitoring is handled in the render loop."""
        pass
    
    def start(self):
        """Start the display system"""
        self.is_running = True
        # Initial LED color
        self._update_led_color_for_state(SystemStates.IDLE)
    
    def stop(self):
        """Stop the display system"""
        self.is_running = False
        self._close_video()
        
        if self.screen:
            try:
                pygame.quit()
            except Exception as e:
                logger.debug("pygame.quit raised but was suppressed: %s", e)
    
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
                    
                    color = phase_colors.get(phase, (0, 0, 0))
                    # Idle/off should strictly clear without re-writing zeros
                    if color == (0, 0, 0):
                        # Extra-stable off: send two clear frames
                        led_strip.clear_all()
                        time.sleep(0.01)
                        led_strip.clear_all()
                        return
                    # Clear then set target color for a clean transition
                    led_strip.clear_all()
                    led_strip.set_color_all(color)
        except Exception as e:
            # Silently fail if LED control is not available
            logger.debug("LED update suppressed: %s", e)
    
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
                        SystemStates.QR_CODES: (0, 255, 0),              # Blue
                        
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
                    
                    color = state_colors.get(state_value, (0, 0, 0))
                    # Idle/off should strictly clear without re-writing zeros
                    if color == (0, 0, 0):
                        # Extra-stable off: send two clear frames
                        led_strip.clear_all()
                        time.sleep(0.01)
                        led_strip.clear_all()
                        return
                    # Clear then set target color for a clean transition
                    led_strip.clear_all()
                    led_strip.set_color_all(color)
        except Exception as e:
            # Silently fail if LED control is not available
            logger.debug("LED update suppressed: %s", e)
    
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
            logger.exception("Display start error: %s", e)
    
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
    logger.info("Testing Force Recovery Functionality")
    
    display = SimpleMediaDisplay()
    if not display.display_initialized:
        logger.warning("Display not initialized, cannot test recovery")
        return
    
    logger.info("Display initialized, testing force recovery...")
    
    # Test 1: Force recovery
    logger.info("Testing force recovery...")
    success = display.force_recovery()
    logger.info("Force recovery result: %s", "Success" if success else "Failed")
    
    # Test 2: Show image with force recovery
    logger.info("Testing show image with force recovery...")
    success = display.show_image(0, force_recovery=True)
    logger.info("Show with force recovery: %s", "Success" if success else "Failed")
    
    display.stop()
    logger.info("Force recovery test completed")


if __name__ == "__main__":
    # Test force recovery functionality
    test_force_recovery()
    
    # Simple test
    logger.info("Running simple display test...")
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


 