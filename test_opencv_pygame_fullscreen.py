#!/usr/bin/env python3
"""
Test OpenCV vs Pygame fullscreen display to determine the best method.
"""

import os
import sys
from pathlib import Path

def test_opencv_fullscreen():
    """Test OpenCV fullscreen display"""
    print("📹 Testing OpenCV Fullscreen")
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
        
        # Get screen dimensions (you might want to detect this dynamically)
        screen_width = 1920
        screen_height = 1080
        print(f"📐 Target screen size: {screen_width}x{screen_height}")
        
        # Resize to fit screen while maintaining aspect ratio
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
        
        print("🖼️  OpenCV fullscreen image displayed!")
        print("💡 Press any key to exit")
        
        cv2.imshow('iTrash Fullscreen', background)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        print("✅ OpenCV fullscreen test completed")
        return True
        
    except ImportError:
        print("❌ OpenCV not available")
        return False
    except Exception as e:
        print(f"❌ OpenCV error: {e}")
        return False

def test_pygame_fullscreen():
    """Test Pygame fullscreen display"""
    print("\n🎮 Testing Pygame Fullscreen")
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
        print(f"📐 Detected screen dimensions: {screen_width}x{screen_height}")
        
        # Set display mode to fullscreen
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("iTrash Fullscreen")
        
        # Load and scale image
        img = pygame.image.load(str(test_image))
        print(f"📸 Original image size: {img.get_size()}")
        
        # Scale to fit screen while maintaining aspect ratio
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
        
        print("🖼️  Pygame fullscreen image displayed!")
        print("💡 Press 'q' or 'ESC' to exit")
        
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key in [pygame.K_q, pygame.K_ESCAPE]:
                        running = False
            
            # Clear screen with black
            screen.fill((0, 0, 0))
            
            # Draw image
            screen.blit(img_scaled, (x, y))
            
            # Update display
            pygame.display.flip()
            clock.tick(60)
        
        pygame.quit()
        print("✅ Pygame fullscreen test completed")
        return True
        
    except ImportError:
        print("❌ Pygame not available")
        return False
    except Exception as e:
        print(f"❌ Pygame error: {e}")
        return False

def test_cycle_images():
    """Test cycling through multiple images in fullscreen"""
    print("\n🔄 Testing Image Cycling in Fullscreen")
    print("=" * 40)
    
    # Find all image files
    images_dir = Path("display/images")
    if not images_dir.exists():
        print("❌ Images directory not found")
        return False
    
    png_files = list(images_dir.glob("*.png"))
    if not png_files:
        print("❌ No PNG files found")
        return False
    
    print(f"📸 Found {len(png_files)} images to cycle through")
    
    # Choose display method
    print("\n🎯 Choose display method:")
    print("   1. OpenCV")
    print("   2. Pygame")
    
    try:
        choice = input("Enter choice (1-2): ").strip()
        
        if choice == "1":
            return cycle_images_opencv(png_files)
        elif choice == "2":
            return cycle_images_pygame(png_files)
        else:
            print("❌ Invalid choice")
            return False
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
        return False

def cycle_images_opencv(image_files):
    """Cycle through images using OpenCV"""
    try:
        import cv2
        import numpy as np
        
        screen_width = 1920
        screen_height = 1080
        
        cv2.namedWindow('iTrash Fullscreen', cv2.WINDOW_NORMAL)
        cv2.setWindowProperty('iTrash Fullscreen', cv2.WND_PROP_FULLSCREEN, cv2.WINDOW_FULLSCREEN)
        
        current_index = 0
        
        while True:
            # Load current image
            img_path = image_files[current_index]
            img = cv2.imread(str(img_path))
            
            if img is not None:
                # Resize and center
                img_ratio = img.shape[1] / img.shape[0]
                screen_ratio = screen_width / screen_height
                
                if img_ratio > screen_ratio:
                    new_width = screen_width
                    new_height = int(screen_width / img_ratio)
                else:
                    new_height = screen_height
                    new_width = int(screen_height * img_ratio)
                
                img_resized = cv2.resize(img, (new_width, new_height), interpolation=cv2.INTER_LANCZOS4)
                
                # Create background and center image
                background = np.zeros((screen_height, screen_width, 3), dtype=np.uint8)
                y_offset = (screen_height - new_height) // 2
                x_offset = (screen_width - new_width) // 2
                background[y_offset:y_offset+new_height, x_offset:x_offset+new_width] = img_resized
                
                cv2.imshow('iTrash Fullscreen', background)
                print(f"📸 Displaying: {img_path.name}")
            
            # Wait for key press
            key = cv2.waitKey(0) & 0xFF
            
            if key == 27:  # ESC
                break
            elif key == ord('n'):  # Next image
                current_index = (current_index + 1) % len(image_files)
            elif key == ord('p'):  # Previous image
                current_index = (current_index - 1) % len(image_files)
        
        cv2.destroyAllWindows()
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def cycle_images_pygame(image_files):
    """Cycle through images using Pygame"""
    try:
        import pygame
        
        pygame.init()
        
        info = pygame.display.Info()
        screen_width = info.current_w
        screen_height = info.current_h
        
        screen = pygame.display.set_mode((screen_width, screen_height), pygame.FULLSCREEN)
        pygame.display.set_caption("iTrash Fullscreen")
        
        current_index = 0
        clock = pygame.time.Clock()
        
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    return True
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        return True
                    elif event.key == pygame.K_n:  # Next
                        current_index = (current_index + 1) % len(image_files)
                    elif event.key == pygame.K_p:  # Previous
                        current_index = (current_index - 1) % len(image_files)
            
            # Load and display current image
            img_path = image_files[current_index]
            img = pygame.image.load(str(img_path))
            
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
            
            # Center image
            x = (screen_width - new_width) // 2
            y = (screen_height - new_height) // 2
            
            # Clear and draw
            screen.fill((0, 0, 0))
            screen.blit(img_scaled, (x, y))
            pygame.display.flip()
            
            print(f"📸 Displaying: {img_path.name}")
            clock.tick(60)
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 OpenCV vs Pygame Fullscreen Test")
    print("=" * 50)
    
    print("🎯 Choose test:")
    print("   1. Test OpenCV fullscreen")
    print("   2. Test Pygame fullscreen")
    print("   3. Test image cycling")
    print("   0. Exit")
    
    try:
        choice = input("\n🎯 Enter your choice (0-3): ").strip()
        
        if choice == "0":
            print("👋 Goodbye!")
            return
        elif choice == "1":
            test_opencv_fullscreen()
        elif choice == "2":
            test_pygame_fullscreen()
        elif choice == "3":
            test_cycle_images()
        else:
            print("❌ Invalid choice")
            
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
    except Exception as e:
        print(f"❌ Error: {e}")

if __name__ == "__main__":
    main() 