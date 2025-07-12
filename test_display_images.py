#!/usr/bin/env python3
"""
Display Images Test for iTrash system.
Shows all display images in a slideshow to verify they work properly.
"""

import time
import os
import sys
from PIL import Image, ImageTk
import tkinter as tk
from config.settings import DisplayConfig

def test_display_images():
    """Test all display images in a slideshow"""
    print("🖼️  Testing Display Images")
    print("=" * 40)
    
    # Check images directory
    images_dir = "display/images"
    if not os.path.exists(images_dir):
        print(f"❌ Images directory not found: {images_dir}")
        return False
    
    # Create main window
    root = tk.Tk()
    root.title("iTrash Display Images Test")
    root.geometry("1000x700")
    
    # Center window
    root.update_idletasks()
    x = (root.winfo_screenwidth() // 2) - (1000 // 2)
    y = (root.winfo_screenheight() // 2) - (700 // 2)
    root.geometry(f"1000x700+{x}+{y}")
    
    # Create label for image display
    image_label = tk.Label(root)
    image_label.pack(expand=True, fill='both')
    
    # Create info label
    info_label = tk.Label(root, text="", font=("Arial", 12))
    info_label.pack(pady=10)
    
    # Create progress label
    progress_label = tk.Label(root, text="", font=("Arial", 10))
    progress_label.pack(pady=5)
    
    # Create controls frame
    controls_frame = tk.Frame(root)
    controls_frame.pack(pady=10)
    
    # Control variables
    current_index = 0
    image_files = list(DisplayConfig.IMAGE_MAPPING.items())
    total_images = len(image_files)
    
    def show_image(index):
        """Show image at specified index"""
        if 0 <= index < total_images:
            acc_value, image_file = image_files[index]
            image_path = os.path.join(images_dir, image_file)
            
            try:
                # Load and resize image
                image = Image.open(image_path)
                image = image.convert("RGB")
                
                # Calculate resize dimensions to fit window
                window_width = 900
                window_height = 500
                
                # Get original dimensions
                orig_width, orig_height = image.size
                
                # Calculate scale factor
                scale_x = window_width / orig_width
                scale_y = window_height / orig_height
                scale = min(scale_x, scale_y)
                
                # Calculate new dimensions
                new_width = int(orig_width * scale)
                new_height = int(orig_height * scale)
                
                # Resize image
                image = image.resize((new_width, new_height), Image.Resampling.LANCZOS)
                
                # Convert to PhotoImage
                photo = ImageTk.PhotoImage(image)
                
                # Update display
                image_label.config(image=photo)
                image_label.image = photo  # Keep reference
                
                # Update info
                info_label.config(text=f"State {acc_value}: {image_file}")
                progress_label.config(text=f"Image {index + 1} of {total_images}")
                
                return True
                
            except Exception as e:
                print(f"❌ Failed to load {image_file}: {e}")
                info_label.config(text=f"Error loading: {image_file}")
                return False
    
    def next_image():
        """Show next image"""
        nonlocal current_index
        current_index = (current_index + 1) % total_images
        show_image(current_index)
    
    def prev_image():
        """Show previous image"""
        nonlocal current_index
        current_index = (current_index - 1) % total_images
        show_image(current_index)
    
    def auto_advance():
        """Auto advance to next image"""
        next_image()
        root.after(2000, auto_advance)  # Advance every 2 seconds
    
    # Create control buttons
    tk.Button(controls_frame, text="⏮ Previous", command=prev_image).pack(side=tk.LEFT, padx=5)
    tk.Button(controls_frame, text="⏯ Auto", command=lambda: root.after(0, auto_advance)).pack(side=tk.LEFT, padx=5)
    tk.Button(controls_frame, text="⏭ Next", command=next_image).pack(side=tk.LEFT, padx=5)
    tk.Button(controls_frame, text="❌ Close", command=root.quit).pack(side=tk.LEFT, padx=5)
    
    # Bind keyboard shortcuts
    root.bind("<Left>", lambda e: prev_image())
    root.bind("<Right>", lambda e: next_image())
    root.bind("<space>", lambda e: auto_advance())
    root.bind("<Escape>", lambda e: root.quit())
    root.bind("<q>", lambda e: root.quit())
    
    # Show first image
    if show_image(0):
        print("✅ Display test started")
        print("   Controls:")
        print("   - Left/Right arrows: Navigate")
        print("   - Space: Auto advance")
        print("   - Q/Escape: Quit")
        print("   - Buttons: Manual control")
        
        # Start auto advance
        root.after(3000, auto_advance)
        
        # Start main loop
        root.mainloop()
        
        print("✅ Display test completed")
        return True
    else:
        print("❌ Failed to show first image")
        root.destroy()
        return False

def main():
    """Main function"""
    try:
        return test_display_images()
    except KeyboardInterrupt:
        print("\n👋 Display test interrupted")
        return False
    except Exception as e:
        print(f"💥 Display test failed: {e}")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 