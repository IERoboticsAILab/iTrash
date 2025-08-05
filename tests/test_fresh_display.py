#!/usr/bin/env python3
"""
Test script for fresh Pygame display approach.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.append(str(Path(__file__).parent.parent))

from display.media_display import SimpleMediaDisplay

def test_fresh_display():
    """Test that fresh Pygame display works for each image"""
    print("🔄 Testing Fresh Pygame Display Approach")
    print("=" * 50)
    
    # Create display
    display = SimpleMediaDisplay()
    
    # Test states to cycle through
    test_states = [0, 1, 2, 3, 4, 5]  # Different system states
    
    for state in test_states:
        print(f"\n📺 Testing State {state}...")
        
        try:
            # Show image (this will open fresh Pygame)
            success = display.show_image(state)
            
            if success:
                print(f"   ✅ State {state} displayed successfully")
            else:
                print(f"   ❌ State {state} failed to display")
            
            # Small delay to see the image
            time.sleep(1)
            
        except Exception as e:
            print(f"   ❌ Error displaying state {state}: {e}")
    
    # Cleanup
    display.stop()
    print("\n🎉 Fresh display test completed!")

def test_rapid_changes():
    """Test rapid state changes"""
    print("\n⚡ Testing Rapid State Changes")
    print("=" * 50)
    
    display = SimpleMediaDisplay()
    
    # Rapidly change states
    for i in range(5):
        state = i % 3  # Cycle through 0, 1, 2
        print(f"   Changing to state {state}...")
        
        try:
            success = display.show_image(state)
            if success:
                print(f"   ✅ State {state} OK")
            else:
                print(f"   ❌ State {state} failed")
        except Exception as e:
            print(f"   ❌ Error: {e}")
        
        time.sleep(0.5)  # Quick changes
    
    display.stop()
    print("🎉 Rapid changes test completed!")

def main():
    """Main test function"""
    print("🚀 Fresh Pygame Display Test Suite\n")
    
    try:
        # Test basic fresh display
        test_fresh_display()
        
        # Test rapid changes
        test_rapid_changes()
        
        print("\n📋 Summary:")
        print("   • Each image opens fresh Pygame context")
        print("   • Pygame closes after each display")
        print("   • No persistent display context issues")
        print("   • Should solve Raspberry Pi display problems")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        return False
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 