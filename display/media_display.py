"""
Media display module for iTrash system.
Handles user interface and image transitions.
"""

import threading
import time
import os
import subprocess
import sys
from tkinter import Tk, Label, Frame
from PIL import Image, ImageTk
import pyautogui
from config.settings import DisplayConfig, SystemStates
from core.database import db_manager

class MediaDisplay:
    """Main display interface for iTrash system"""
    
    def __init__(self, images_dir="display/images"):
        self.images_dir = images_dir
        self.acc = 0
        self.last_acc = 0
        self.browser_opened = False
        self.root = None
        self.frame = None
        self.label = None
        self.tk_image = None
        self.timer_thread = None
        self.is_running = False
        
        # Load image mapping
        self.media = self._load_media()
        
        # Initialize database connection
        if not db_manager.is_connected:
            db_manager.connect()
    
    def _load_media(self):
        """Load media items from configuration"""
        media = []
        for acc_value, image_file in DisplayConfig.IMAGE_MAPPING.items():
            image_path = os.path.join(self.images_dir, image_file)
            if os.path.exists(image_path):
                media.append({
                    'type': 'image',
                    'file': image_path,
                    'acc_value': acc_value
                })
            else:
                print(f"Warning: Image file not found: {image_path}")
        
        return media
    
    def _get_image_by_acc(self, acc_value):
        """Get image file path by accumulator value"""
        for item in self.media:
            if item.get('acc_value') == acc_value:
                return item['file']
        return None
    
    def init_ui(self):
        """Initialize the user interface"""
        self.root = Tk()
        self.root.title("iTrash Media Display")
        
        if DisplayConfig.FULLSCREEN:
            self.root.attributes('-fullscreen', True)
        
        self.frame = Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        
        self.label = Label(self.frame)
        self.label.pack(fill='both', expand=True)
        
        # Bind escape key to quit
        self.root.bind("<Escape>", lambda event: self.quit())
        
        # Bind other keys for debugging
        self.root.bind("<Key>", self._handle_key_press)
    
    def _handle_key_press(self, event):
        """Handle key press events"""
        if event.char == 'q':
            self.quit()
        elif event.char == 'r':
            self.refresh_display()
        elif event.char == 'b':
            self.toggle_browser()
    
    def show_media(self):
        """Show media based on current accumulator value"""
        if not (0 <= self.acc < len(DisplayConfig.IMAGE_MAPPING)):
            print(f"Index {self.acc} out of range.")
            return
        
        if self.acc == SystemStates.IDLE:
            self.switch_to_chromium()
        elif self.acc == SystemStates.REWARD:
            # Show reward image for 5 seconds then reset
            self.restore_and_show_image()
            time.sleep(DisplayConfig.IMAGE_DISPLAY_DELAY)
            db_manager.update_acc(SystemStates.IDLE)
        else:
            if self.browser_opened:
                self.minimize_chromium()
            if self.acc != self.last_acc:
                self.restore_and_show_image()
                self.last_acc = self.acc
    
    def switch_to_chromium(self):
        """Switch to Chromium browser window"""
        try:
            # Use xdotool to find and focus on the Chromium window
            window_id = subprocess.check_output(
                ["xdotool", "search", "--onlyvisible", "--class", "chromium"]
            ).strip().decode()
            subprocess.call(["xdotool", "windowactivate", window_id])
            self.browser_opened = True
            time.sleep(0.5)  # Allow some time for the switch to complete
        except subprocess.CalledProcessError:
            print("Chromium window not found.")
    
    def minimize_chromium(self):
        """Minimize Chromium browser window"""
        try:
            # Use xdotool to find and minimize the Chromium window
            window_id = subprocess.check_output(
                ["xdotool", "search", "--onlyvisible", "--class", "chromium"]
            ).strip().decode()
            subprocess.call(["xdotool", "windowminimize", window_id])
            self.browser_opened = False
        except subprocess.CalledProcessError:
            print("Failed to minimize Chromium window.")
    
    def toggle_browser(self):
        """Toggle browser visibility"""
        if self.browser_opened:
            self.minimize_chromium()
        else:
            self.switch_to_chromium()
    
    def restore_and_show_image(self):
        """Restore the Tkinter window and show image"""
        if self.root:
            self.root.deiconify()  # Restore the window if it was minimized
        
        image_file = self._get_image_by_acc(self.acc)
        if image_file:
            self.show_image(image_file)
        else:
            print(f"No image found for ACC value: {self.acc}")
    
    def show_image(self, file_path):
        """Display image on the interface"""
        try:
            image = Image.open(file_path)
            image = image.convert("RGB")
            image = image.resize(
                (DisplayConfig.WINDOW_WIDTH, DisplayConfig.WINDOW_HEIGHT),
                Image.Resampling.LANCZOS
            )
            self.tk_image = ImageTk.PhotoImage(image)
            self.label.config(image=self.tk_image)
        except Exception as e:
            print(f"Error loading image {file_path}: {e}")
            self.next_media()
    
    def next_media(self):
        """Move to next media item"""
        self.acc = (self.acc + 1) % len(DisplayConfig.IMAGE_MAPPING)
        self.show_media()
    
    def set_acc(self, value):
        """Set accumulator value and update display"""
        if 0 <= value < len(DisplayConfig.IMAGE_MAPPING):
            self.acc = value
            self.show_media()
        else:
            print(f"Invalid index: {value}. Must be between 0 and {len(DisplayConfig.IMAGE_MAPPING) - 1}.")
    
    def get_acc_mongo(self):
        """Monitor MongoDB for accumulator changes"""
        acc_timer = None
        
        while self.is_running:
            time.sleep(0.1)
            
            try:
                new_acc = db_manager.get_acc_value()
                if new_acc is not None:
                    self.set_acc(new_acc)
                    
                    # Handle timeout for ACC == 3 (user confirmation)
                    if new_acc == SystemStates.USER_CONFIRMATION:
                        if acc_timer is None:
                            acc_timer = time.time()
                        elif time.time() - acc_timer >= 10:  # 10 second timeout
                            db_manager.update_acc(SystemStates.IDLE)
                            acc_timer = None
                    else:
                        acc_timer = None
                        
            except Exception as e:
                print(f"Error monitoring MongoDB: {e}")
                time.sleep(1)  # Wait longer on error
    
    def refresh_display(self):
        """Refresh the display"""
        if self.root:
            self.root.update()
    
    def start(self):
        """Start the media display"""
        self.is_running = True
        
        # Initialize UI
        self.init_ui()
        
        # Show initial media
        self.show_media()
        
        # Start monitoring thread
        self.timer_thread = threading.Thread(target=self.get_acc_mongo)
        self.timer_thread.daemon = True
        self.timer_thread.start()
        
        # Start main loop
        self.root.mainloop()
    
    def quit(self):
        """Quit the application"""
        self.is_running = False
        if self.root:
            self.root.quit()
    
    def get_status(self):
        """Get current status"""
        return {
            "acc": self.acc,
            "last_acc": self.last_acc,
            "browser_opened": self.browser_opened,
            "is_running": self.is_running,
            "media_count": len(self.media)
        }


class DisplayManager:
    """Manager for display operations"""
    
    def __init__(self):
        self.display = None
    
    def start_display(self, images_dir="display/images"):
        """Start the media display"""
        self.display = MediaDisplay(images_dir)
        self.display.start()
    
    def stop_display(self):
        """Stop the media display"""
        if self.display:
            self.display.quit()
    
    def get_display_status(self):
        """Get display status"""
        if self.display:
            return self.display.get_status()
        return {"status": "not_started"}


# Utility functions for testing
def test_display():
    """Test the display functionality"""
    manager = DisplayManager()
    try:
        manager.start_display()
    except KeyboardInterrupt:
        print("Display stopped by user")
    finally:
        manager.stop_display()


if __name__ == '__main__':
    test_display() 