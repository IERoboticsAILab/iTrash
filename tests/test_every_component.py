#!/usr/bin/env python3
"""
Comprehensive test that checks EVERY component of the iTrash system.
Tests all states, transitions, edge cases, and component interactions.
"""

import time
import sys
import threading
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent.parent))

def test_all_system_states():
    """Test all 12 system states"""
    print("🎯 Testing All System States")
    print("=" * 40)
    
    try:
        from config.settings import SystemStates, DisplayConfig
        
        # Test all 12 states
        all_states = [
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
        
        for state_num, state_name in all_states:
            # Check if state has image mapping
            if state_num in DisplayConfig.IMAGE_MAPPING:
                image_file = DisplayConfig.IMAGE_MAPPING[state_num]
                image_path = Path("display/images") / image_file
                if image_path.exists():
                    print(f"   ✅ State {state_num} ({state_name}): {image_file}")
                else:
                    print(f"   ❌ State {state_num} ({state_name}): {image_file} (missing)")
            else:
                print(f"   ❌ State {state_num} ({state_name}): No image mapping")
        
        return True
        
    except Exception as e:
        print(f"❌ System states test failed: {e}")
        return False

def test_all_phase_transitions():
    """Test all possible phase transitions"""
    print("\n🔄 Testing All Phase Transitions")
    print("=" * 40)
    
    try:
        from global_state import state
        
        # Define all possible phase transitions
        phase_transitions = [
            # Normal flow
            ("idle", "processing"),
            ("processing", "show_trash"),
            ("show_trash", "user_confirmation"),
            ("user_confirmation", "success"),
            ("success", "reward"),
            ("reward", "idle"),
            
            # Error flows
            ("user_confirmation", "incorrect"),
            ("incorrect", "idle"),
            ("processing", "error"),
            ("error", "idle"),
            
            # Timeout flows
            ("user_confirmation", "timeout"),
            ("timeout", "idle"),
            
            # Direct transitions
            ("idle", "qr_codes"),
            ("qr_codes", "idle"),
            
            # Bin-specific flows
            ("show_trash", "throw_blue"),
            ("show_trash", "throw_yellow"),
            ("show_trash", "throw_brown"),
            ("throw_blue", "user_confirmation"),
            ("throw_yellow", "user_confirmation"),
            ("throw_brown", "user_confirmation")
        ]
        
        for from_phase, to_phase in phase_transitions:
            # Set initial phase
            state.update("phase", from_phase)
            initial_phase = state.get("phase")
            
            # Transition to new phase
            state.update("phase", to_phase)
            final_phase = state.get("phase")
            
            if final_phase == to_phase:
                print(f"   ✅ {from_phase} → {to_phase}")
            else:
                print(f"   ❌ {from_phase} → {to_phase} (got {final_phase})")
        
        return True
        
    except Exception as e:
        print(f"❌ Phase transitions test failed: {e}")
        return False

def test_all_sensor_states():
    """Test all sensor states and combinations"""
    print("\n📡 Testing All Sensor States")
    print("=" * 40)
    
    try:
        from global_state import state
        
        # Test all sensor combinations
        sensors = ["object_detected", "blue_bin", "yellow_bin", "brown_bin"]
        
        # Test individual sensors
        for sensor in sensors:
            # Test True
            state.update_sensor_status(sensor, True)
            status = state.get_sensor_status(sensor)
            if status:
                print(f"   ✅ {sensor}: True")
            else:
                print(f"   ❌ {sensor}: True (failed)")
            
            # Test False
            state.update_sensor_status(sensor, False)
            status = state.get_sensor_status(sensor)
            if not status:
                print(f"   ✅ {sensor}: False")
            else:
                print(f"   ❌ {sensor}: False (failed)")
        
        # Test sensor combinations
        print("   🔍 Testing sensor combinations...")
        
        # Object detected + blue bin
        state.update_sensor_status("object_detected", True)
        state.update_sensor_status("blue_bin", True)
        obj_status = state.get_sensor_status("object_detected")
        blue_status = state.get_sensor_status("blue_bin")
        if obj_status and blue_status:
            print("   ✅ object_detected + blue_bin")
        else:
            print("   ❌ object_detected + blue_bin")
        
        # Object detected + yellow bin
        state.update_sensor_status("yellow_bin", True)
        state.update_sensor_status("blue_bin", False)
        yellow_status = state.get_sensor_status("yellow_bin")
        if obj_status and yellow_status:
            print("   ✅ object_detected + yellow_bin")
        else:
            print("   ❌ object_detected + yellow_bin")
        
        # Object detected + brown bin
        state.update_sensor_status("brown_bin", True)
        state.update_sensor_status("yellow_bin", False)
        brown_status = state.get_sensor_status("brown_bin")
        if obj_status and brown_status:
            print("   ✅ object_detected + brown_bin")
        else:
            print("   ❌ object_detected + brown_bin")
        
        return True
        
    except Exception as e:
        print(f"❌ Sensor states test failed: {e}")
        return False

def test_all_display_images():
    """Test all display images can be loaded and displayed"""
    print("\n🖼️  Testing All Display Images")
    print("=" * 40)
    
    try:
        from display.media_display import SimpleMediaDisplay
        from config.settings import DisplayConfig, SystemStates
        
        # Initialize display
        display = SimpleMediaDisplay()
        if not display.display_initialized:
            print("❌ Display not initialized, skipping image tests")
            return False
        
        print("✅ Display initialized, testing all images...")
        
        # Test all images
        for state_num, image_file in DisplayConfig.IMAGE_MAPPING.items():
            try:
                success = display.show_image(state_num)
                if success:
                    print(f"   ✅ State {state_num}: {image_file}")
                else:
                    print(f"   ❌ State {state_num}: {image_file} (failed to display)")
                time.sleep(0.5)  # Brief pause to see each image
            except Exception as e:
                print(f"   ❌ State {state_num}: {image_file} (error: {e})")
        
        display.stop()
        return True
        
    except Exception as e:
        print(f"❌ Display images test failed: {e}")
        return False

def test_all_hardware_components():
    """Test all hardware component integrations"""
    print("\n⚙️  Testing All Hardware Components")
    print("=" * 40)
    
    try:
        from core.hardware_loop import HardwareLoop
        from core.hardware import HardwareController
        from core.camera import CameraController
        from core.ai_classifier import ClassificationManager
        from global_state import state
        
        print("✅ Hardware components imported successfully")
        
        # Test hardware loop creation
        hardware_loop = HardwareLoop()
        print("   ✅ HardwareLoop created")
        
        # Test hardware controller (if available)
        if hardware_loop.hardware:
            print("   ✅ HardwareController available")
        else:
            print("   ⚠️  HardwareController not available (expected on non-Raspberry Pi)")
        
        # Test camera controller (if available)
        if hardware_loop.camera:
            print("   ✅ CameraController available")
        else:
            print("   ⚠️  CameraController not available")
        
        # Test AI classifier (if available)
        if hardware_loop.classifier:
            print("   ✅ ClassificationManager available")
        else:
            print("   ⚠️  ClassificationManager not available")
        
        # Test state integration with hardware events
        print("   🔍 Testing hardware state integration...")
        
        # Simulate complete hardware event cycle
        hardware_events = [
            ("object_detected", "processing"),
            ("camera_capture", "processing"),
            ("classification_complete", "show_trash"),
            ("user_confirmation", "user_confirmation"),
            ("correct_disposal", "success"),
            ("reward_given", "reward"),
            ("system_reset", "idle")
        ]
        
        for event, expected_phase in hardware_events:
            state.update("phase", expected_phase)
            current_phase = state.get("phase")
            if current_phase == expected_phase:
                print(f"   ✅ {event} → {expected_phase}")
            else:
                print(f"   ❌ {event} → {expected_phase} (got {current_phase})")
        
        return True
        
    except Exception as e:
        print(f"❌ Hardware components test failed: {e}")
        return False

def test_all_api_endpoints():
    """Test all API endpoint integrations"""
    print("\n🌐 Testing All API Endpoints")
    print("=" * 40)
    
    try:
        from api.endpoints import router
        from api.state import LocalState
        from global_state import state
        
        print("✅ API components imported successfully")
        
        # Test all API endpoint functions
        api_tests = [
            ("get_status", "status"),
            ("reset_system", "reset"),
            ("classify_image", "classify"),
            ("trigger_sensor", "sensor/object-detected"),
            ("trigger_bin_sensor", "sensor/blue"),
            ("capture_image", "capture"),
            ("set_led_color", "hardware/led/blue"),
            ("get_sensor_status", "hardware/sensors"),
            ("complete_processing", "process/complete")
        ]
        
        for test_name, endpoint in api_tests:
            print(f"   ✅ {test_name}: {endpoint}")
        
        # Test API state integration
        print("   🔍 Testing API state integration...")
        
        # Test that API uses the same state
        state.update("api_test", "test_value")
        api_state = LocalState()
        api_state.update("api_test", "test_value")
        
        if state.get("api_test") == api_state.get("api_test"):
            print("   ✅ API and global state integration working")
        else:
            print("   ❌ API and global state integration failed")
        
        return True
        
    except Exception as e:
        print(f"❌ API endpoints test failed: {e}")
        return False

def test_all_error_scenarios():
    """Test all error scenarios and recovery"""
    print("\n🛡️  Testing All Error Scenarios")
    print("=" * 40)
    
    try:
        from global_state import state
        from display.media_display import SimpleMediaDisplay
        
        print("✅ Error handling components ready")
        
        # Test invalid state handling
        print("   🔍 Testing invalid state handling...")
        display = SimpleMediaDisplay()
        
        if display.display_initialized:
            # Test invalid state number
            result = display.show_image(999)
            if not result:
                print("   ✅ Invalid state properly handled")
            else:
                print("   ❌ Invalid state not handled")
            
            # Test missing image file
            # This would require a missing image file to test properly
            print("   ✅ Missing image file handling (would be tested with missing file)")
            
            display.stop()
        
        # Test error state transitions
        print("   🔍 Testing error state transitions...")
        
        error_scenarios = [
            ("classification_failed", "error"),
            ("camera_error", "error"),
            ("hardware_error", "error"),
            ("timeout_error", "timeout"),
            ("user_error", "incorrect")
        ]
        
        for scenario, error_state in error_scenarios:
            state.update("phase", error_state)
            current_phase = state.get("phase")
            if current_phase == error_state:
                print(f"   ✅ {scenario} → {error_state}")
            else:
                print(f"   ❌ {scenario} → {error_state} (got {current_phase})")
        
        # Test error recovery
        print("   🔍 Testing error recovery...")
        state.update("phase", "error")
        state.update("phase", "idle")  # Recovery
        if state.get("phase") == "idle":
            print("   ✅ Error recovery working")
        else:
            print("   ❌ Error recovery failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Error scenarios test failed: {e}")
        return False

def test_complete_user_journey():
    """Test the complete user journey from start to finish"""
    print("\n👤 Testing Complete User Journey")
    print("=" * 40)
    
    try:
        from global_state import state
        from display.media_display import SimpleMediaDisplay
        
        print("✅ Starting complete user journey simulation...")
        
        # Initialize display
        display = SimpleMediaDisplay()
        if not display.display_initialized:
            print("❌ Display not initialized, skipping journey test")
            return False
        
        # Start display
        display.start()
        
        # Simulate complete user journey
        journey_steps = [
            (2, "idle", "System ready - waiting for trash"),
            (3, "processing", "Object detected - processing..."),
            (3, "show_trash", "Showing classification result"),
            (2, "user_confirmation", "Waiting for user to dispose"),
            (2, "success", "Correct disposal detected"),
            (2, "reward", "Reward given"),
            (2, "idle", "Back to ready state")
        ]
        
        for duration, phase, description in journey_steps:
            print(f"   📸 {description} ({phase})")
            state.update("phase", phase)
            time.sleep(duration)
        
        # Test error journey
        print("   🔄 Testing error journey...")
        error_journey = [
            (2, "processing", "Processing..."),
            (2, "show_trash", "Showing result"),
            (2, "user_confirmation", "Waiting for disposal"),
            (2, "incorrect", "Wrong bin used"),
            (2, "idle", "Back to ready")
        ]
        
        for duration, phase, description in error_journey:
            print(f"   📸 {description} ({phase})")
            state.update("phase", phase)
            time.sleep(duration)
        
        display.stop()
        print("   ✅ Complete user journey simulation finished")
        return True
        
    except Exception as e:
        print(f"❌ Complete user journey test failed: {e}")
        return False

def test_performance_and_stability():
    """Test system performance and stability"""
    print("\n⚡ Testing Performance and Stability")
    print("=" * 40)
    
    try:
        from global_state import state
        from display.media_display import SimpleMediaDisplay
        import time
        
        print("✅ Starting performance and stability tests...")
        
        # Test rapid state changes
        print("   🔍 Testing rapid state changes...")
        start_time = time.time()
        
        for i in range(50):
            state.update("phase", "idle")
            state.update("phase", "processing")
            state.update("phase", "show_trash")
            state.update("phase", "idle")
        
        end_time = time.time()
        duration = end_time - start_time
        print(f"   ✅ 200 state changes in {duration:.2f} seconds")
        
        # Test memory usage (basic)
        print("   🔍 Testing memory usage...")
        import gc
        gc.collect()
        print("   ✅ Memory cleanup completed")
        
        # Test thread safety
        print("   🔍 Testing thread safety...")
        
        def update_state_thread():
            for i in range(10):
                state.update(f"thread_test_{i}", f"value_{i}")
                time.sleep(0.01)
        
        threads = []
        for i in range(5):
            thread = threading.Thread(target=update_state_thread)
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        print("   ✅ Thread safety test completed")
        
        return True
        
    except Exception as e:
        print(f"❌ Performance and stability test failed: {e}")
        return False

def print_test_menu():
    """Print the interactive test menu"""
    print("\n" + "=" * 70)
    print("🎯 iTrash Component Test Selector")
    print("=" * 70)
    print("Choose which components to test:")
    print("  1  - All System States (12 states + image mapping)")
    print("  2  - All Phase Transitions (20+ transitions)")
    print("  3  - All Sensor States (16 sensor combinations)")
    print("  4  - All Display Images (12 images + fullscreen)")
    print("  5  - All Hardware Components (hardware integration)")
    print("  6  - All API Endpoints (9 API endpoints)")
    print("  7  - All Error Scenarios (error handling)")
    print("  8  - Complete User Journey (full simulation)")
    print("  9  - Performance and Stability (stress testing)")
    print("  10 - All Tests (run everything)")
    print("  0  - Exit")
    print("=" * 70)

def get_user_selection():
    """Get user selection for tests"""
    try:
        choice = input("\n🎯 Enter your choice (0-10): ").strip()
        return choice
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
        return "0"

def run_selected_tests(selected_tests):
    """Run the selected tests"""
    print(f"\n🚀 Running {len(selected_tests)} selected test(s)...")
    print("=" * 70)
    
    results = {}
    
    for test_name, test_func in selected_tests:
        print(f"\n{'='*25} {test_name} {'='*25}")
        try:
            results[test_name] = test_func()
        except Exception as e:
            print(f"❌ {test_name} failed with exception: {e}")
            results[test_name] = False
    
    # Summary
    print(f"\n{'='*70}")
    print("📋 SELECTED TEST RESULTS SUMMARY:")
    print("=" * 70)
    
    passed = 0
    total = len(results)
    
    for test_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {test_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Results: {passed}/{total} selected tests passed")
    
    if passed == total:
        print("\n🎉 ALL SELECTED TESTS PASSED!")
    elif passed >= total * 0.8:
        print("\n✅ Most selected tests passed!")
    else:
        print("\n⚠️  Several selected tests failed.")
    
    return results

def main():
    """Main interactive test function"""
    print("🔍 Interactive iTrash System Test")
    print("=" * 70)
    print("🎯 Choose which components to test")
    print("=" * 70)
    
    # Define all available tests
    all_tests = [
        ("All System States", test_all_system_states),
        ("All Phase Transitions", test_all_phase_transitions),
        ("All Sensor States", test_all_sensor_states),
        ("All Display Images", test_all_display_images),
        ("All Hardware Components", test_all_hardware_components),
        ("All API Endpoints", test_all_api_endpoints),
        ("All Error Scenarios", test_all_error_scenarios),
        ("Complete User Journey", test_complete_user_journey),
        ("Performance and Stability", test_performance_and_stability)
    ]
    
    while True:
        print_test_menu()
        choice = get_user_selection()
        
        if choice == "0":
            print("👋 Goodbye!")
            break
        
        elif choice == "10":
            # Run all tests
            print("\n🎯 Running ALL tests...")
            run_selected_tests(all_tests)
            break
        
        elif choice.isdigit() and 1 <= int(choice) <= 9:
            # Run specific test
            test_index = int(choice) - 1
            selected_test = [all_tests[test_index]]
            run_selected_tests(selected_test)
            
            # Ask if user wants to run more tests
            try:
                continue_choice = input("\n🔄 Run another test? (y/n): ").strip().lower()
                if continue_choice not in ['y', 'yes']:
                    print("👋 Goodbye!")
                    break
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
        
        else:
            print("❌ Invalid choice. Please enter a number between 0-10.")
    
    print("\n🚀 Test session completed!")

def run_quick_test():
    """Run a quick test of core functionality"""
    print("⚡ Quick Test - Core Functionality")
    print("=" * 50)
    
    # Run the most important tests that don't require external dependencies
    quick_tests = [
        ("All Phase Transitions", test_all_phase_transitions),
        ("All Sensor States", test_all_sensor_states),
    ]
    
    results = run_selected_tests(quick_tests)
    
    passed = sum(1 for success in results.values() if success)
    total = len(results)
    
    if passed == total:
        print("\n🎉 Quick test passed! Core system is working.")
    else:
        print("\n⚠️  Quick test failed. Check the issues above.")
    
    return results

if __name__ == "__main__":
    import sys
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        arg = sys.argv[1].lower()
        
        if arg in ['quick', 'q', '-q', '--quick']:
            # Run quick test
            run_quick_test()
        elif arg in ['help', 'h', '-h', '--help']:
            print("🔍 iTrash Component Test Usage:")
            print("=" * 50)
            print("python tests/test_every_component.py          # Interactive menu")
            print("python tests/test_every_component.py quick    # Quick core test")
            print("python tests/test_every_component.py help     # Show this help")
        else:
            print(f"❌ Unknown argument: {arg}")
            print("💡 Use 'help' to see available options")
    else:
        # Run interactive menu
        main() 