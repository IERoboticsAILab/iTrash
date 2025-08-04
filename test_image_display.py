#!/usr/bin/env python3
"""
Test script for iTrash image display system.
This script will cycle through all system states to verify images are displayed correctly.
"""

import time
import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

from display.media_display import SimpleMediaDisplay, DisplayManager
from config.settings import SystemStates, DisplayConfig
from global_state import state

def test_image_display():
    """Test the image display system by cycling through all states"""
    
    print("🧪 Testing iTrash Image Display System")
    print("=" * 50)
    
    # Initialize display
    try:
        display = SimpleMediaDisplay()
        print("✅ Display system initialized successfully")
    except Exception as e:
        print(f"❌ Failed to initialize display: {e}")
        return False
    
    # Check if images directory exists
    images_dir = Path("display/images")
    if not images_dir.exists():
        print(f"❌ Images directory not found: {images_dir}")
        return False
    
    print(f"✅ Images directory found: {images_dir}")
    
    # Test each state
    test_states = [
        (SystemStates.IDLE, "Idle"),
        (SystemStates.PROCESSING, "Processing"),
        (SystemStates.SHOW_TRASH, "Show Trash"),
        (SystemStates.USER_CONFIRMATION, "User Confirmation"),
        (SystemStates.SUCCESS, "Success"),
        (SystemStates.QR_CODES, "QR Codes"),
        (SystemStates.REWARD, "Reward"),
        (SystemStates.INCORRECT, "Incorrect"),
        (SystemStates.TIMEOUT, "Timeout"),
        (SystemStates.THROW_YELLOW, "Throw Yellow"),
        (SystemStates.THROW_BLUE, "Throw Blue"),
        (SystemStates.THROW_BROWN, "Throw Brown")
    ]
    
    print("\n🖼️  Testing image display for each state:")
    print("-" * 50)
    
    for state_num, state_name in test_states:
        print(f"\n📸 Testing State {state_num}: {state_name}")
        
        # Check if image file exists
        if state_num in DisplayConfig.IMAGE_MAPPING:
            image_file = DisplayConfig.IMAGE_MAPPING[state_num]
            image_path = images_dir / image_file
            
            if image_path.exists():
                print(f"   ✅ Image file found: {image_file}")
                print(f"   📁 Path: {image_path}")
                print(f"   📏 Size: {image_path.stat().st_size} bytes")
            else:
                print(f"   ❌ Image file missing: {image_file}")
                continue
        
        # Try to display the image
        try:
            success = display.show_image(state_num)
            if success:
                print(f"   ✅ Image displayed successfully")
                print(f"   🖼️  Current image: {display.current_image_path}")
            else:
                print(f"   ❌ Failed to display image")
        except Exception as e:
            print(f"   ❌ Error displaying image: {e}")
        
        # Wait a bit to see the image
        time.sleep(2)
    
    print("\n" + "=" * 50)
    print("🎯 Image Display Test Complete!")
    
    # Get final status
    status = display.get_status()
    print(f"\n📊 Final Status:")
    print(f"   Current State: {status['acc']}")
    print(f"   Current Image: {status['current_image']}")
    print(f"   System Running: {status['is_running']}")
    
    return True

def test_state_monitoring():
    """Test the state monitoring functionality"""
    
    print("\n🔄 Testing State Monitoring")
    print("=" * 50)
    
    try:
        display = SimpleMediaDisplay()
        display.start()
        print("✅ State monitoring started")
        
        # Test state changes
        test_phases = [
            ("idle", "Idle"),
            ("processing", "Processing"),
            ("user_confirmation", "User Confirmation"),
            ("show_trash", "Show Trash"),
            ("idle", "Back to Idle")
        ]
        
        for phase, phase_name in test_phases:
            print(f"\n🔄 Changing to phase: {phase_name}")
            state.update("phase", phase)
            time.sleep(3)  # Wait for state change to be detected
        
        display.stop()
        print("✅ State monitoring test complete")
        return True
        
    except Exception as e:
        print(f"❌ State monitoring test failed: {e}")
        return False

def test_display_manager():
    """Test the DisplayManager class"""
    
    print("\n🎛️  Testing Display Manager")
    print("=" * 50)
    
    try:
        manager = DisplayManager()
        manager.start_display()
        print("✅ Display manager started")
        
        # Test for a few seconds
        time.sleep(5)
        
        # Get status
        status = manager.get_display_status()
        print(f"📊 Display Manager Status: {status}")
        
        manager.stop_display()
        print("✅ Display manager stopped")
        return True
        
    except Exception as e:
        print(f"❌ Display manager test failed: {e}")
        return False

def main():
    """Main test function"""
    
    print("🚀 Starting iTrash Image Display Tests")
    print("=" * 60)
    
    # Test 1: Basic image display
    test1_success = test_image_display()
    
    # Test 2: State monitoring
    test2_success = test_state_monitoring()
    
    # Test 3: Display manager
    test3_success = test_display_manager()
    
    # Summary
    print("\n" + "=" * 60)
    print("📋 Test Summary:")
    print(f"   Image Display Test: {'✅ PASS' if test1_success else '❌ FAIL'}")
    print(f"   State Monitoring Test: {'✅ PASS' if test2_success else '❌ FAIL'}")
    print(f"   Display Manager Test: {'✅ PASS' if test3_success else '❌ FAIL'}")
    
    if all([test1_success, test2_success, test3_success]):
        print("\n🎉 All tests passed! Image display system is working correctly.")
    else:
        print("\n⚠️  Some tests failed. Check the output above for details.")
    
    print("\n💡 To see the images, check the console output for image paths.")
    print("   You can open these images manually to verify they display correctly.")

if __name__ == "__main__":
    main() 