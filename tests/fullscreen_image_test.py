#!/usr/bin/env python3
"""
Fullscreen image display test - perfect the fullscreen display without any decorations.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

def test_pil_fullscreen():
    """Test PIL with fullscreen display"""
    print("🖼️  Testing PIL Fullscreen Display")
    print("=" * 40)
    
    # Find an image file
    images_dir = Path("display/images")
    if not images_dir.exists():
        print("❌ Images directory not found")
        return False
    
    png_files = list(images_dir.glob("*.png"))
    if not png_files:
        print("❌ No PNG files found")
        return False
    
    test_image = png_files[0]
    print(f"✅ Found test image: {test_image}")
    
    try:
        from PIL import Image, ImageTk
        import tkinter as tk
        
        # Create fullscreen window
        root = tk.Tk()
        
        # Get screen dimensions
        screen_width = root.winfo_screenwidth()
        screen_height = root.winfo_screenheight()
        print(f"📐 Screen dimensions: {screen_width}x{screen_height}")
        
        # Configure fullscreen
        root.attributes('-fullscreen', True)
        root.overrideredirect(True)  # Remove window decorations
        root.configure(bg='black')
        
        # Load and resize image
        img = Image.open(test_image)
        print(f"📸 Original image size: {img.size}")
        
        # Resize to fit screen while maintaining aspect ratio
        img_ratio = img.size[0] / img.size[1]
        screen_ratio = screen_width / screen_height
        
        if img_ratio > screen_ratio:
            # Image is wider than screen
            new_width = screen_width
            new_height = int(screen_width / img_ratio)
        else:
            # Image is taller than screen
            new_height = screen_height
            new_width = int(screen_height * img_ratio)
        
        img_resized = img.resize((new_width, new_height), Image.Resampling.LANCZOS)
        print(f"📐 Resized image: {img_resized.size}")
        
        # Convert to PhotoImage
        photo = ImageTk.PhotoImage(img_resized)
        
        # Create label and center it
        label = tk.Label(root, image=photo, bg='black')
        label.place(relx=0.5, rely=0.5, anchor='center')
        
        print("🖼️  Fullscreen image displayed!")
        print("💡 Press 'q' to quit or 'ESC' to exit")
        
        # Bind keys for exit
        def on_key(event):
            if event.keysym in ['q', 'Q', 'Escape']:
                root.destroy()
        
        root.bind('<Key>', on_key)
        root.focus_set()
        
        # Start the main loop
        root.mainloop()
        
        img.close()
        return True
        
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_opencv_fullscreen():
    """Test OpenCV with fullscreen display"""
    print("\n📹 Testing OpenCV Fullscreen Display")
    print("=" * 40)
    
    # Find an image file
    images_dir = Path("display/images")
    if not images_dir.exists():
        print("❌ Images directory not found")
        return False
    
    png_files = list(images_dir.glob("*.png"))
    if not png_files:
        print("❌ No PNG files found")
        return False
    
    test_image = png_files[0]
    print(f"✅ Found test image: {test_image}")
    
    try:
        import cv2
        import numpy as np
        
        # Read image
        img = cv2.imread(str(test_image))
        if img is None:
            print("❌ OpenCV could not read image")
            return False
        
        print(f"📸 Original image size: {img.shape}")
        
        # Get screen dimensions
        screen_width = 1920  # Default, you might want to detect this
        screen_height = 1080
        
        # Resize to fit screen
        img_ratio = img.shape[1] / img.shape[0]
        screen_ratio = screen_width / screen_height
        
        if img_ratio > screen_ratio:
            new_width = screen_width
            new_height = int(screen_width / img_ratio)
        else:
            new_height = screen_height
            new_width = int(screen_height * img_ratio)
        
        img_resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
        print(f"📐 Resized image: {img_resized.shape}")
        
        # Create black background
        background = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
        
        # Calculate position to center the image
        y_offset = (screen_height - new_height) // 2
        x_offset = (screen_width - new_width) // 2
        
        # Place image on background
        background[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = img_resized
        
        # Create fullscreen window
        cv2.namedWindow('iTrash Fullscreen', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('iTrash Fullscreen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        print("🖼️  Fullscreen image displayed!")
        print("💡 Press any key to exit")
        
        cv2.imshow('iTrash Fullscreen', background)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return True
        
    except ImportError:
        print("❌ OpenCV not available")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def test_sdl_fullscreen():
    """Test SDL with fullscreen display"""
    print("\n🎮 Testing SDL Fullscreen Display")
    print("=" * 40)
    
    # Find an image file
    images_dir = Path("display/images")
    if not images_dir.exists():
        print("❌ Images directory not found")
        return False
    
    png_files = list(images_dir.glob("*.png"))
    if not png_files:
        print("❌ No PNG files found")
        return False
    
    test_image = png_files[0]
    print(f"✅ Found test image: {test_image}")
    
    try:
        import pygame
        
        # Initialize pygame
        pygame.init()
        
        # Get screen info
        info = pygame.display.Info()
        screen_width = info.current_w
        screen_height = info.current_h
        print(f"📐 Screen dimensions: {screen_width}x{screen_height}")
        
        # Set display mode to fullscreen
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("iTrash Fullscreen")
        
        # Load and scale image
        img = pygame.image.load(str(test_image))
        print(f"📸 Original image size: {img.get_size()}")
        
        # Scale to fit screen
        img_ratio = img.get_width() / img.get_height()
        screen_ratio = screen_width / screen_height
        
        if img_ratio > screen_ratio:
            new_width = screen_width
            new_height = int(screen_width / img_ratio)
        else:
            new_height = screen_height
            new_width = int(screen_height * img_ratio)
        
        img_scaled = pygame.transform.scale(img, (new_width, new_height))
        print(f"📐 Scaled image: {img_scaled.get_size()}")
        
        # Calculate position to center
        x = (screen_width - new_width) // 2
        y = (screen_height - new_height) // 2
        
        # Main loop
        running = True
        clock = pygame.time.Clock()
        
        print("🖼️  Fullscreen image displayed!")
        print("💡 Press 'q' or 'ESC' to exit")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_q, pygame.K_ESCAPE]:
                        running = False
            
            # Clear screen
            screen.fill((0, 0, 0))
            
            # Draw image
            screen.blit(img_scaled, (x, y))
            
            # Update display
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        return True
        
    except ImportError:
        print("❌ Pygame not available")
        return False
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Fullscreen Image Display Test")
    print("=" * 50)
    
    # Test different fullscreen methods
    methods = [
        ("PIL + Tkinter", test_pil_fullscreen),
        ("OpenCV", test_opencv_fullscreen),
        ("SDL/Pygame", test_sdl_fullscreen)
    ]
    
    print("🎯 Choose a display method to test:")
    for i, (name, _) in enumerate(methods, 1):
        print(f"   {i}. {name}")
    print("   0. Exit")
    
    try:
        choice = input("\n🎯 Enter your choice (1-3): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            return
        
        choice_num = int(choice)
        if 1 <= choice_num <= len(methods):
            name, test_func = methods[choice_num - 1]
            print(f"\n{'='*20} Testing {name} {'='*20}")
            test_func()
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 