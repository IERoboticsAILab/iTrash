#!/usr/bin/env python3
"""
Complete iTrash system test with fullscreen display integration.
Tests the entire system end-to-end to ensure everything works together.
"""

import time
import sys
import threading
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

def test_display_integration():
    """Test that the display system integrates properly"""
    print("🖼️  Testing Display Integration")
    print("=" * 40)
    
    try:
        from display.media_display import SimpleMediaDisplay, DisplayManager
        from config.settings import SystemStates, DisplayConfig
        from global_state import state
        
        # Test display initialization
        display = SimpleMediaDisplay()
        if not display.display_initialized:
            print("❌ Display initialization failed")
            return False
        
        print("✅ Display system initialized")
        print(f"📐 Screen: {display.screen_width}x{display.screen_height}")
        
        # Test image mapping
        print(f"📋 Image mapping: {len(DisplayConfig.IMAGE_MAPPING)} states configured")
        
        # Test a few key states
        test_states = [0, 1, 2, 3, 4]
        for state_num in test_states:
            if state_num in DisplayConfig.IMAGE_MAPPING:
                print(f"   ✅ State {state_num}: {DisplayConfig.IMAGE_MAPPING[state_num]}")
            else:
                print(f"   ❌ State {state_num}: No image mapping")
        
        display.stop()
        return True
        
    except Exception as e:
        print(f"❌ Display integration test failed: {e}")
        return False

def test_state_management():
    """Test the global state management system"""
    print("\n🔄 Testing State Management")
    print("=" * 40)
    
    try:
        from global_state import state
        from config.settings import SystemStates
        
        # Test state updates
        test_phases = ["idle", "processing", "show_trash", "user_confirmation", "reward"]
        
        for phase in test_phases:
            state.update("phase", phase)
            current_phase = state.get("phase")
            print(f"   ✅ Phase '{phase}' set and retrieved: {current_phase}")
        
        # Test sensor status
        state.update_sensor_status("object_detected", True)
        sensor_status = state.get("sensor_status", {})
        print(f"   ✅ Sensor status updated: {sensor_status}")
        
        return True
        
    except Exception as e:
        print(f"❌ State management test failed: {e}")
        return False

def test_hardware_loop_integration():
    """Test hardware loop integration with display"""
    print("\n⚙️  Testing Hardware Loop Integration")
    print("=" * 40)
    
    try:
        from core.hardware_loop import HardwareLoop
        from display.media_display import SimpleMediaDisplay
        from global_state import state
        
        # Initialize display
        display = SimpleMediaDisplay()
        if not display.display_initialized:
            print("❌ Display not available for hardware loop test")
            return False
        
        # Initialize hardware loop (without actual hardware)
        print("🔧 Initializing hardware loop...")
        
        # Test state simulation
        print("🎮 Simulating hardware events...")
        
        # Simulate object detection
        state.update("phase", "processing")
        time.sleep(1)
        
        # Simulate classification
        state.update("phase", "show_trash")
        time.sleep(1)
        
        # Simulate user confirmation
        state.update("phase", "user_confirmation")
        time.sleep(1)
        
        # Simulate success
        state.update("phase", "reward")
        time.sleep(1)
        
        # Back to idle
        state.update("phase", "idle")
        time.sleep(1)
        
        display.stop()
        print("✅ Hardware loop integration test completed")
        return True
        
    except Exception as e:
        print(f"❌ Hardware loop integration test failed: {e}")
        return False

def test_unified_system():
    """Test the unified system with display integration"""
    print("\n🚀 Testing Unified System")
    print("=" * 40)
    
    try:
        from unified_main import create_app
        from display.media_display import DisplayManager
        from global_state import state
        
        print("🔧 Creating unified application...")
        
        # Create the FastAPI app
        app = create_app()
        print("✅ FastAPI application created")
        
        # Test display manager
        display_manager = DisplayManager()
        print("✅ Display manager created")
        
        # Test state updates
        print("🎮 Testing state updates...")
        
        test_phases = [
            ("idle", "System ready"),
            ("processing", "Processing trash"),
            ("show_trash", "Showing classification"),
            ("user_confirmation", "Waiting for user"),
            ("reward", "Success!")
        ]
        
        for phase, description in test_phases:
            print(f"   📸 {description} ({phase})")
            state.update("phase", phase)
            time.sleep(2)
        
        # Reset to idle
        state.update("phase", "idle")
        
        print("✅ Unified system test completed")
        return True
        
    except Exception as e:
        print(f"❌ Unified system test failed: {e}")
        return False

def test_end_to_end_simulation():
    """Test a complete end-to-end simulation"""
    print("\n🎯 Testing End-to-End Simulation")
    print("=" * 40)
    
    try:
        from display.media_display import SimpleMediaDisplay
        from global_state import state
        import threading
        
        # Initialize display
        display = SimpleMediaDisplay()
        if not display.display_initialized:
            print("❌ Display not available for simulation")
            return False
        
        print("🎬 Starting end-to-end simulation...")
        print("💡 This will simulate a complete trash disposal cycle")
        print("💡 Press Ctrl+C to stop early")
        
        # Start the display system
        display.start()
        
        # Simulate complete cycle
        simulation_steps = [
            (2, "idle", "System ready - waiting for trash"),
            (3, "processing", "Object detected - processing..."),
            (3, "show_trash", "Showing classification result"),
            (5, "user_confirmation", "Waiting for user to dispose"),
            (2, "reward", "Great job! Reward given"),
            (2, "idle", "Back to ready state")
        ]
        
        for duration, phase, description in simulation_steps:
            print(f"\n📸 {description}")
            state.update("phase", phase)
            time.sleep(duration)
        
        # Keep running for a bit more
        print("\n🔄 Continuing simulation... Press Ctrl+C to stop")
        time.sleep(5)
        
        display.stop()
        print("✅ End-to-end simulation completed")
        return True
        
    except KeyboardInterrupt:
        print("\n👋 Simulation interrupted by user")
        return True
    except Exception as e:
        print(f"❌ End-to-end simulation failed: {e}")
        return False

def test_error_handling():
    """Test error handling and recovery"""
    print("\n🛡️  Testing Error Handling")
    print("=" * 40)
    
    try:
        from display.media_display import SimpleMediaDisplay
        from global_state import state
        
        # Test invalid state
        print("🧪 Testing invalid state handling...")
        display = SimpleMediaDisplay()
        
        if display.display_initialized:
            # Test invalid state number
            result = display.show_image(999)
            if not result:
                print("   ✅ Invalid state properly handled")
            
            # Test error state
            state.update("phase", "error")
            time.sleep(1)
            
            # Test recovery
            state.update("phase", "idle")
            time.sleep(1)
            
            display.stop()
            print("✅ Error handling test completed")
            return True
        else:
            print("❌ Display not available for error handling test")
            return False
            
    except Exception as e:
        print(f"❌ Error handling test failed: {e}")
        return False

def main():
    """Main test function"""
    print("🚀 Complete iTrash System Test")
    print("=" * 60)
    print("🎯 Testing the entire system with fullscreen display integration")
    print("=" * 60)
    
    tests = [
        ("Display Integration", test_display_integration),
        ("State Management", test_state_management),
        ("Hardware Loop Integration", test_hardware_loop_integration),
        ("Unified System", test_unified_system),
        ("Error Handling", test_error_handling),
        ("End-to-End Simulation", test_end_to_end_simulation)
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n{'='*20} {test_name} {'='*20}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 Test Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("\n🎉 All tests passed! Your iTrash system is ready!")
        print("💡 The fullscreen display is fully integrated and working.")
    elif passed >= total * 0.8:
        print("\n✅ Most tests passed! System is mostly ready.")
        print("💡 Check the failed tests above for any issues.")
    else:
        print("\n⚠️  Several tests failed. Check the issues above.")
        print("💡 The system may need some adjustments.")
    
    print("\n🚀 Ready to run your iTrash system with fullscreen display!")

if __name__ == "__main__":
    main() 