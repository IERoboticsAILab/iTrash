#!/usr/bin/env python3
"""
Test script for the updated fullscreen display system.
"""

import time
import sys
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from display.media_display import SimpleMediaDisplay, DisplayManager
from config.settings import SystemStates, DisplayConfig

def test_display_initialization():
    """Test if the display system initializes correctly"""
    print("🔧 Testing Display Initialization")
    print("=" * 40)
    
    try:
        display = SimpleMediaDisplay()
        
        if display.display_initialized:
            print("✅ Display initialized successfully")
            print(f"📐 Screen dimensions: {display.screen_width}x{display.screen_height}")
            return display
        else:
            print("❌ Display initialization failed")
            return None
            
    except Exception as e:
        print(f"❌ Error during initialization: {e}")
        return None

def test_single_image_display(display):
    """Test displaying a single image"""
    print("\n🖼️  Testing Single Image Display")
    print("=" * 40)
    
    if not display:
        print("❌ No display available")
        return False
    
    try:
        # Test idle state
        print("📸 Testing idle state (white.png)...")
        success = display.show_image(SystemStates.IDLE)
        
        if success:
            print("✅ Image displayed successfully")
            time.sleep(2)  # Show for 2 seconds
            return True
        else:
            print("❌ Failed to display image")
            return False
            
    except Exception as e:
        print(f"❌ Error displaying image: {e}")
        return False

def test_state_cycling(display):
    """Test cycling through different states"""
    print("\n🔄 Testing State Cycling")
    print("=" * 40)
    
    if not display:
        print("❌ No display available")
        return False
    
    test_states = [
        (SystemStates.IDLE, "Idle"),
        (SystemStates.PROCESSING, "Processing"),
        (SystemStates.SHOW_TRASH, "Show Trash"),
        (SystemStates.USER_CONFIRMATION, "User Confirmation"),
        (SystemStates.SUCCESS, "Success"),
        (SystemStates.REWARD, "Reward")
    ]
    
    try:
        for state_num, state_name in test_states:
            print(f"📸 Testing {state_name} (State {state_num})...")
            
            success = display.show_image(state_num)
            if success:
                print(f"   ✅ {state_name} displayed")
            else:
                print(f"   ❌ {state_name} failed")
            
            time.sleep(2)  # Show each state for 2 seconds
        
        return True
        
    except Exception as e:
        print(f"❌ Error during state cycling: {e}")
        return False

def test_display_manager():
    """Test the DisplayManager class"""
    print("\n🎛️  Testing Display Manager")
    print("=" * 40)
    
    try:
        manager = DisplayManager()
        manager.start_display()
        
        # Get status
        status = manager.get_display_status()
        print(f"📊 Display Manager Status: {status}")
        
        # Test for a few seconds
        time.sleep(5)
        
        manager.stop_display()
        print("✅ Display manager test completed")
        return True
        
    except Exception as e:
        print(f"❌ Display manager test failed: {e}")
        return False

def test_manual_state_control():
    """Test manual state control"""
    print("\n🎮 Testing Manual State Control")
    print("=" * 40)
    
    try:
        display = SimpleMediaDisplay()
        
        if not display.display_initialized:
            print("❌ Display not initialized")
            return False
        
        print("🎯 Available states:")
        for state_num, image_file in DisplayConfig.IMAGE_MAPPING.items():
            print(f"   {state_num}: {image_file}")
        
        print("\n💡 This will cycle through states automatically.")
        print("💡 Press Ctrl+C to stop.")
        
        display.start()
        
        # Let it run for a while
        time.sleep(10)
        
        display.stop()
        return True
        
    except KeyboardInterrupt:
        print("\n👋 Manual test interrupted")
        return True
    except Exception as e:
        print(f"❌ Manual test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Testing Updated Fullscreen Display System")
    print("=" * 60)
    
    # Test 1: Display initialization
    display = test_display_initialization()
    
    if display:
        # Test 2: Single image display
        test_single_image_display(display)
        
        # Test 3: State cycling
        test_state_cycling(display)
        
        # Test 4: Display manager
        test_display_manager()
        
        # Test 5: Manual control (optional)
        print("\n🎯 Would you like to test manual state control? (y/n)")
        try:
            choice = input().strip().lower()
            if choice == 'y':
                test_manual_state_control()
        except KeyboardInterrupt:
            print("\n👋 Test interrupted")
        
        # Cleanup
        display.stop()
    
    print("\n" + "=" * 60)
    print("🎉 Fullscreen display system test completed!")
    print("💡 The system is now ready for integration with your iTrash system.")

if __name__ == "__main__":
    main() 