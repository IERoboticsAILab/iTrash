#!/usr/bin/env python3
"""
Test script for display startup and initialization.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from display.media_display import SimpleMediaDisplay, DisplayManager

def test_display_startup():
    """Test that display starts properly"""
    print("🚀 Testing Display Startup")
    print("=" * 40)
    
    # Test 1: Simple display startup
    print("\n1️⃣ Testing SimpleMediaDisplay startup...")
    try:
        display = SimpleMediaDisplay()
        print(f"   ✅ Display created")
        print(f"   📊 Initial status: {display.get_status()}")
        
        # Try to start
        display.start()
        print(f"   📊 After start status: {display.get_status()}")
        
        # Wait a moment
        time.sleep(2)
        
        # Stop
        display.stop()
        print("   ✅ Display stopped")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")
    
    # Test 2: Display manager startup
    print("\n2️⃣ Testing DisplayManager startup...")
    try:
        manager = DisplayManager()
        print("   ✅ Manager created")
        
        # Start display
        manager.start_display()
        print("   ✅ Manager started")
        
        # Get status
        status = manager.get_display_status()
        print(f"   📊 Status: {status}")
        
        # Wait a moment
        time.sleep(2)
        
        # Stop
        manager.stop_display()
        print("   ✅ Manager stopped")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def test_state_changes():
    """Test state changes with display"""
    print("\n🔄 Testing State Changes")
    print("=" * 40)
    
    try:
        display = SimpleMediaDisplay()
        display.start()
        
        # Test different states
        test_states = [0, 1, 2, 3, 4]
        
        for state in test_states:
            print(f"   📺 Testing state {state}...")
            display.set_acc(state)
            time.sleep(1)
        
        display.stop()
        print("   ✅ State changes completed")
        
    except Exception as e:
        print(f"   ❌ Error: {e}")

def main():
    """Main test function"""
    print("🧪 Display Startup Test Suite\n")
    
    try:
        # Test startup
        test_display_startup()
        
        # Test state changes
        test_state_changes()
        
        print("\n🎉 All tests completed!")
        print("\n📋 Summary:")
        print("   • Display should initialize on startup")
        print("   • System should work even without display")
        print("   • State changes should be logged")
        print("   • No crashes should occur")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 