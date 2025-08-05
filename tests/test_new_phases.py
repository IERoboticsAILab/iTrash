#!/usr/bin/env python3
"""
Test script for the new phase system with specific classification phases.
Tests the flow: classification -> specific phase -> try_again_green on error
"""

import time
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from global_state import state
from display.media_display import SimpleMediaDisplay

def test_phase_flow():
    """Test the new phase flow"""
    print("🔄 Testing New Phase Flow System\n")
    
    # Initialize display
    display = SimpleMediaDisplay()
    if not display.display_initialized:
        print("❌ Display not initialized, cannot test")
        return
    
    print("✅ Display initialized, testing phase flow...")
    
    # Test 1: Blue trash classification
    print("\n1️⃣ Testing blue trash classification...")
    state.update("phase", "blue_trash")
    time.sleep(2)
    
    # Test 2: Yellow trash classification  
    print("\n2️⃣ Testing yellow trash classification...")
    state.update("phase", "yellow_trash")
    time.sleep(2)
    
    # Test 3: Brown trash classification
    print("\n3️⃣ Testing brown trash classification...")
    state.update("phase", "brown_trash")
    time.sleep(2)
    
    # Test 4: Error/classification failure (should show try_again_green)
    print("\n4️⃣ Testing classification error (should show try_again_green)...")
    state.update("phase", "error")
    time.sleep(2)
    
    # Test 5: Success
    print("\n5️⃣ Testing success...")
    state.update("phase", "success")
    time.sleep(2)
    
    # Test 6: Incorrect bin
    print("\n6️⃣ Testing incorrect bin...")
    state.update("phase", "incorrect")
    time.sleep(2)
    
    # Test 7: Back to idle
    print("\n7️⃣ Testing back to idle...")
    state.update("phase", "idle")
    time.sleep(2)
    
    display.stop()
    print("\n✅ Phase flow test completed")

def test_state_mapping():
    """Test the state mapping"""
    print("\n📊 Testing State Mapping\n")
    
    # Expected mappings
    expected_mappings = {
        "blue_trash": "throw_blue.png",
        "yellow_trash": "throw_yellow.png", 
        "brown_trash": "throw_brown.png",
        "error": "try_again_green.png",
        "success": "great_job.png",
        "incorrect": "incorrect_new.png"
    }
    
    from config.settings import SystemStates
    from display.media_display import SimpleMediaDisplay
    
    display = SimpleMediaDisplay()
    
    for phase, expected_image in expected_mappings.items():
        print(f"Testing {phase} -> {expected_image}")
        state.update("phase", phase)
        time.sleep(1)
        
        # Check if the correct image is being displayed
        current_state = display.acc
        if phase == "blue_trash" and current_state == SystemStates.THROW_BLUE:
            print(f"   ✅ {phase} correctly maps to state {current_state}")
        elif phase == "yellow_trash" and current_state == SystemStates.THROW_YELLOW:
            print(f"   ✅ {phase} correctly maps to state {current_state}")
        elif phase == "brown_trash" and current_state == SystemStates.THROW_BROWN:
            print(f"   ✅ {phase} correctly maps to state {current_state}")
        elif phase == "error" and current_state == SystemStates.USER_CONFIRMATION:
            print(f"   ✅ {phase} correctly maps to try_again_green state {current_state}")
        else:
            print(f"   ❌ {phase} maps to unexpected state {current_state}")
    
    display.stop()

def main():
    """Main test function"""
    print("🔄 New Phase System Test Suite\n")
    
    # Test phase flow
    test_phase_flow()
    
    # Test state mapping
    test_state_mapping()
    
    print("\n" + "="*50)
    print("📋 Test Summary:")
    print("   • Blue trash -> throw_blue.png")
    print("   • Yellow trash -> throw_yellow.png") 
    print("   • Brown trash -> throw_brown.png")
    print("   • Error/classification failure -> try_again_green.png")
    print("   • Success -> great_job.png")
    print("   • Incorrect bin -> incorrect_new.png")

if __name__ == "__main__":
    main() 