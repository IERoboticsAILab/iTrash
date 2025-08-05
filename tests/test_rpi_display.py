#!/usr/bin/env python3
"""
Raspberry Pi Display Troubleshooting Test
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

def test_environment():
    """Test environment variables and system info"""
    print("🔍 Environment Check:")
    print(f"   DISPLAY: {os.environ.get('DISPLAY', 'Not set')}")
    print(f"   USER: {os.environ.get('USER', 'Not set')}")
    print(f"   HOME: {os.environ.get('HOME', 'Not set')}")
    print(f"   XAUTHORITY: {os.environ.get('XAUTHORITY', 'Not set')}")
    
    # Check if running as root
    if os.geteuid() == 0:
        print("   ⚠️  Running as root - this may cause display issues")
    else:
        print("   ✅ Running as regular user")

def test_pygame_setup():
    """Test Pygame initialization with different settings"""
    print("\n🎮 Pygame Setup Test:")
    
    # Test 1: Basic Pygame init
    try:
        import pygame
        pygame.init()
        print("   ✅ Basic Pygame initialization successful")
    except Exception as e:
        print(f"   ❌ Basic Pygame initialization failed: {e}")
        return False
    
    # Test 2: Display info
    try:
        info = pygame.display.Info()
        print(f"   ✅ Display info: {info.current_w}x{info.current_h}")
    except Exception as e:
        print(f"   ❌ Display info failed: {e}")
    
    # Test 3: Try different display modes
    display_tests = [
        ("Windowed", 0),
        ("Fullscreen", pygame.FULLSCREEN),
        ("Small window", 0, (800, 600))
    ]
    
    for test_name, flags, *args in display_tests:
        try:
            if args:
                screen = pygame.display.set_mode(args[0], flags)
            else:
                screen = pygame.display.set_mode((1024, 768), flags)
            print(f"   ✅ {test_name} mode successful")
            pygame.display.quit()
            break
        except Exception as e:
            print(f"   ❌ {test_name} mode failed: {e}")
    
    pygame.quit()
    return True

def test_display_manager():
    """Test the display manager"""
    print("\n🖼️  Display Manager Test:")
    
    try:
        from display.media_display import DisplayManager
        
        # Create display manager
        manager = DisplayManager()
        print("   ✅ Display manager created")
        
        # Try to start display
        try:
            manager.start_display()
            print("   ✅ Display manager started")
            
            # Get status
            status = manager.get_display_status()
            print(f"   📊 Display status: {status}")
            
            # Stop display
            manager.stop_display()
            print("   ✅ Display manager stopped")
            
        except Exception as e:
            print(f"   ❌ Display manager failed: {e}")
            
    except Exception as e:
        print(f"   ❌ Failed to import display manager: {e}")

def test_simple_display():
    """Test simple display class"""
    print("\n📺 Simple Display Test:")
    
    try:
        from display.media_display import SimpleMediaDisplay
        
        # Create display
        display = SimpleMediaDisplay()
        print("   ✅ Simple display created")
        
        # Check status
        status = display.get_status()
        print(f"   📊 Display status: {status}")
        
        # Try to show an image
        if display.display_initialized:
            try:
                success = display.show_image(0)  # Show white.png
                if success:
                    print("   ✅ Image display successful")
                else:
                    print("   ❌ Image display failed")
            except Exception as e:
                print(f"   ❌ Image display error: {e}")
        else:
            print("   ⚠️  Display not initialized - skipping image test")
        
        # Cleanup
        display.stop()
        print("   ✅ Display cleanup successful")
        
    except Exception as e:
        print(f"   ❌ Simple display test failed: {e}")

def main():
    """Main test function"""
    print("🍓 Raspberry Pi Display Troubleshooting\n")
    
    # Test environment
    test_environment()
    
    # Test Pygame setup
    if test_pygame_setup():
        # Test display manager
        test_display_manager()
        
        # Test simple display
        test_simple_display()
    
    print("\n📋 Troubleshooting Tips:")
    print("   1. Make sure you're running in a desktop environment")
    print("   2. Try running: export DISPLAY=:0")
    print("   3. Check if X11 is running: ps aux | grep X")
    print("   4. Try running as non-root user")
    print("   5. Install missing packages: sudo apt-get install python3-pygame")
    print("   6. For headless mode, the system will still function without display")

if __name__ == "__main__":
    main() 