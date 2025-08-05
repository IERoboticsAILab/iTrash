#!/usr/bin/env python3
"""
Basic image display test - tries different methods to show an image.
"""

import os
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

def test_basic_image_access():
    """Test basic image file access"""
    print("🔍 Testing Basic Image Access")
    print("=" * 40)
    
    # Find an image file
    images_dir = Path("display/images")
    if not images_dir.exists():
        print("❌ Images directory not found")
        return None
    
    # Look for any PNG file
    png_files = list(images_dir.glob("*.png"))
    if not png_files:
        print("❌ No PNG files found")
        return None
    
    test_image = png_files[0]
    print(f"✅ Found test image: {test_image}")
    return test_image

def test_pil_display():
    """Test displaying image with PIL"""
    print("\n🖼️  Testing PIL Image Display")
    print("=" * 40)
    
    test_image = test_basic_image_access()
    if not test_image:
        return False
    
    try:
        from PIL import Image
        
        # Open the image
        img = Image.open(test_image)
        print(f"✅ PIL opened image: {img.size} {img.mode}")
        
        # Try to show the image (this might open a window)
        print("🖼️  Attempting to display image with PIL...")
        img.show()
        print("✅ PIL show() called - check if a window opened")
        
        img.close()
        return True
        
    except ImportError:
        print("❌ PIL not available")
        return False
    except Exception as e:
        print(f"❌ PIL error: {e}")
        return False

def test_opencv_display():
    """Test displaying image with OpenCV"""
    print("\n📹 Testing OpenCV Image Display")
    print("=" * 40)
    
    test_image = test_basic_image_access()
    if not test_image:
        return False
    
    try:
        import cv2
        
        # Read the image
        img = cv2.imread(str(test_image))
        if img is None:
            print("❌ OpenCV could not read image")
            return False
        
        print(f"✅ OpenCV read image: {img.shape}")
        
        # Try to display the image
        print("🖼️  Attempting to display image with OpenCV...")
        cv2.imshow('iTrash Test Image', img)
        print("✅ OpenCV imshow() called - check if a window opened")
        print("💡 Press any key to close the window")
        
        # Wait for key press
        cv2.waitKey(0)
        cv2.destroyAllWindows()
        
        return True
        
    except ImportError:
        print("❌ OpenCV not available")
        return False
    except Exception as e:
        print(f"❌ OpenCV error: {e}")
        return False

def test_matplotlib_display():
    """Test displaying image with matplotlib"""
    print("\n📊 Testing Matplotlib Image Display")
    print("=" * 40)
    
    test_image = test_basic_image_access()
    if not test_image:
        return False
    
    try:
        import matplotlib.pyplot as plt
        import matplotlib.image as mpimg
        
        # Read and display image
        img = mpimg.imread(str(test_image))
        print(f"✅ Matplotlib read image: {img.shape}")
        
        print("🖼️  Attempting to display image with Matplotlib...")
        plt.figure(figsize=(8, 6))
        plt.imshow(img)
        plt.title('iTrash Test Image')
        plt.axis('off')
        plt.show()
        print("✅ Matplotlib show() called - check if a window opened")
        
        return True
        
    except ImportError:
        print("❌ Matplotlib not available")
        return False
    except Exception as e:
        print(f"❌ Matplotlib error: {e}")
        return False

def test_system_open():
    """Test opening image with system default viewer"""
    print("\n🖥️  Testing System Default Viewer")
    print("=" * 40)
    
    test_image = test_basic_image_access()
    if not test_image:
        return False
    
    try:
        import subprocess
        import platform
        
        system = platform.system()
        print(f"🖥️  Detected system: {system}")
        
        if system == "Darwin":  # macOS
            subprocess.run(["open", str(test_image)])
            print("✅ Opened with macOS 'open' command")
        elif system == "Windows":
            os.startfile(str(test_image))
            print("✅ Opened with Windows default viewer")
        elif system == "Linux":
            subprocess.run(["xdg-open", str(test_image)])
            print("✅ Opened with Linux xdg-open")
        else:
            print(f"⚠️  Unknown system: {system}")
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ System open error: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Basic Image Display Test")
    print("=" * 50)
    
    # Test different display methods
    methods = [
        ("PIL", test_pil_display),
        ("OpenCV", test_opencv_display),
        ("Matplotlib", test_matplotlib_display),
        ("System Default", test_system_open)
    ]
    
    results = {}
    
    for name, test_func in methods:
        print(f"\n{'='*20} Testing {name} {'='*20}")
        try:
            results[name] = test_func()
        except Exception as e:
            print(f"❌ {name} test failed with exception: {e}")
            results[name] = False
    
    # Summary
    print(f"\n{'='*50}")
    print("📋 Test Results Summary:")
    print("=" * 50)
    
    for name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {name}: {status}")
    
    working_methods = [name for name, success in results.items() if success]
    
    if working_methods:
        print(f"\n🎉 Working display methods: {', '.join(working_methods)}")
        print("💡 The image display system should work with these methods")
    else:
        print(f"\n⚠️  No display methods worked!")
        print("💡 This might indicate:")
        print("   - No display environment available")
        print("   - Missing dependencies")
        print("   - Display permissions issues")

if __name__ == "__main__":
    main() 