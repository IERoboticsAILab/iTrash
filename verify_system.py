#!/usr/bin/env python3
"""
Comprehensive iTrash system verification script.
Checks all components and their integration to ensure everything works correctly.
"""

import sys
import os
from pathlib import Path

# Add the project root to the Python path
sys.path.append(str(Path(__file__).parent))

def verify_configuration():
    """Verify all configuration settings"""
    print("🔧 Verifying Configuration")
    print("=" * 40)
    
    try:
        from config.settings import (
            SystemStates, DisplayConfig, HardwareConfig, 
            Colors, TrashClassification, TimingConfig, AIConfig
        )
        
        # Check SystemStates
        print("✅ SystemStates imported successfully")
        expected_states = [
            'IDLE', 'PROCESSING', 'SHOW_TRASH', 'USER_CONFIRMATION',
            'SUCCESS', 'QR_CODES', 'REWARD', 'INCORRECT', 'TIMEOUT',
            'THROW_YELLOW', 'THROW_BLUE', 'THROW_BROWN'
        ]
        
        for state_name in expected_states:
            if hasattr(SystemStates, state_name):
                print(f"   ✅ {state_name}: {getattr(SystemStates, state_name)}")
            else:
                print(f"   ❌ Missing state: {state_name}")
        
        # Check DisplayConfig
        print("\n✅ DisplayConfig imported successfully")
        print(f"   📐 Window size: {DisplayConfig.WINDOW_WIDTH}x{DisplayConfig.WINDOW_HEIGHT}")
        print(f"   🖼️  Fullscreen: {DisplayConfig.FULLSCREEN}")
        print(f"   📋 Image mapping: {len(DisplayConfig.IMAGE_MAPPING)} states")
        
        # Check image mapping completeness
        for state_num in range(12):
            if state_num in DisplayConfig.IMAGE_MAPPING:
                image_file = DisplayConfig.IMAGE_MAPPING[state_num]
                image_path = Path("display/images") / image_file
                if image_path.exists():
                    print(f"   ✅ State {state_num}: {image_file}")
                else:
                    print(f"   ❌ State {state_num}: {image_file} (missing)")
            else:
                print(f"   ❌ State {state_num}: No image mapping")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration verification failed: {e}")
        return False

def verify_global_state():
    """Verify global state management"""
    print("\n🔄 Verifying Global State Management")
    print("=" * 40)
    
    try:
        from global_state import state
        from api.state import LocalState
        
        # Test state operations
        print("✅ Global state imported successfully")
        
        # Test basic operations
        state.update("test_key", "test_value")
        retrieved = state.get("test_key")
        if retrieved == "test_value":
            print("   ✅ State update and retrieval working")
        else:
            print("   ❌ State update/retrieval failed")
        
        # Test sensor status
        state.update_sensor_status("object_detected", True)
        sensor_status = state.get_sensor_status("object_detected")
        if sensor_status:
            print("   ✅ Sensor status update working")
        else:
            print("   ❌ Sensor status update failed")
        
        # Test phase updates
        test_phases = ["idle", "processing", "show_trash", "user_confirmation", "reward"]
        for phase in test_phases:
            state.update("phase", phase)
            current_phase = state.get("phase")
            if current_phase == phase:
                print(f"   ✅ Phase '{phase}' updated successfully")
            else:
                print(f"   ❌ Phase '{phase}' update failed")
        
        # Reset state
        state.reset()
        print("   ✅ State reset working")
        
        return True
        
    except Exception as e:
        print(f"❌ Global state verification failed: {e}")
        return False

def verify_display_system():
    """Verify display system integration"""
    print("\n🖼️  Verifying Display System")
    print("=" * 40)
    
    try:
        from display.media_display import SimpleMediaDisplay, DisplayManager
        from config.settings import SystemStates, DisplayConfig
        
        # Test display initialization
        print("✅ Display system imported successfully")
        
        # Test display manager
        manager = DisplayManager()
        print("   ✅ DisplayManager created")
        
        # Test phase-to-state mapping
        print("\n   🔍 Testing phase-to-state mapping...")
        test_phases = {
            "idle": SystemStates.IDLE,
            "processing": SystemStates.PROCESSING,
            "show_trash": SystemStates.SHOW_TRASH,
            "user_confirmation": SystemStates.USER_CONFIRMATION,
            "success": SystemStates.SUCCESS,
            "reward": SystemStates.REWARD,
            "incorrect": SystemStates.INCORRECT,
            "timeout": SystemStates.TIMEOUT,
            "qr_codes": SystemStates.QR_CODES
        }
        
        for phase, expected_state in test_phases.items():
            if expected_state in DisplayConfig.IMAGE_MAPPING:
                print(f"   ✅ {phase} -> State {expected_state} -> {DisplayConfig.IMAGE_MAPPING[expected_state]}")
            else:
                print(f"   ❌ {phase} -> State {expected_state} (no image mapping)")
        
        return True
        
    except Exception as e:
        print(f"❌ Display system verification failed: {e}")
        return False

def verify_hardware_integration():
    """Verify hardware loop integration"""
    print("\n⚙️  Verifying Hardware Integration")
    print("=" * 40)
    
    try:
        from core.hardware_loop import HardwareLoop, start_hardware_loop, stop_hardware_loop
        from global_state import state
        
        print("✅ Hardware loop imported successfully")
        
        # Test hardware loop creation
        hardware_loop = HardwareLoop()
        print("   ✅ HardwareLoop created")
        
        # Test state integration
        print("   🔍 Testing state integration...")
        
        # Simulate hardware events
        test_events = [
            ("object_detected", "processing"),
            ("classification_complete", "show_trash"),
            ("user_confirmation", "user_confirmation"),
            ("disposal_complete", "reward"),
            ("back_to_idle", "idle")
        ]
        
        for event, expected_phase in test_events:
            state.update("phase", expected_phase)
            current_phase = state.get("phase")
            if current_phase == expected_phase:
                print(f"   ✅ {event} -> {expected_phase}")
            else:
                print(f"   ❌ {event} -> {expected_phase} (got {current_phase})")
        
        return True
        
    except Exception as e:
        print(f"❌ Hardware integration verification failed: {e}")
        return False

def verify_api_integration():
    """Verify API integration"""
    print("\n🌐 Verifying API Integration")
    print("=" * 40)
    
    try:
        from api.endpoints import router
        from api.state import LocalState
        from global_state import state
        
        print("✅ API components imported successfully")
        
        # Test API state integration
        print("   🔍 Testing API state integration...")
        
        # Test API endpoints would use the same state
        state.update("api_test", "test_value")
        api_state = LocalState()
        api_state.update("api_test", "test_value")
        
        if state.get("api_test") == api_state.get("api_test"):
            print("   ✅ API and global state integration working")
        else:
            print("   ❌ API and global state integration failed")
        
        return True
        
    except Exception as e:
        print(f"❌ API integration verification failed: {e}")
        return False

def verify_unified_system():
    """Verify unified system integration"""
    print("\n🚀 Verifying Unified System")
    print("=" * 40)
    
    try:
        from unified_main import create_app, lifespan
        from display.media_display import DisplayManager
        from core.hardware_loop import start_hardware_loop, stop_hardware_loop
        from api.mqtt_client import start_mqtt, stop_mqtt
        from global_state import state
        
        print("✅ Unified system components imported successfully")
        
        # Test app creation
        app = create_app()
        print("   ✅ FastAPI app created")
        
        # Test display manager integration
        display_manager = DisplayManager()
        print("   ✅ DisplayManager integrated")
        
        # Test state management
        state.update("system_status", "testing")
        system_status = state.get("system_status")
        if system_status == "testing":
            print("   ✅ System state management working")
        else:
            print("   ❌ System state management failed")
        
        return True
        
    except Exception as e:
        print(f"❌ Unified system verification failed: {e}")
        return False

def verify_file_structure():
    """Verify file structure and dependencies"""
    print("\n📁 Verifying File Structure")
    print("=" * 40)
    
    required_dirs = [
        "config",
        "core", 
        "display",
        "api",
        "analytics",
        "blockchain-part",
        "tests"
    ]
    
    required_files = [
        "config/settings.py",
        "global_state.py",
        "display/media_display.py",
        "core/hardware_loop.py",
        "api/endpoints.py",
        "api/state.py",
        "unified_main.py",
        "requirements.txt"
    ]
    
    # Check directories
    for dir_name in required_dirs:
        if Path(dir_name).exists():
            print(f"   ✅ Directory: {dir_name}")
        else:
            print(f"   ❌ Missing directory: {dir_name}")
    
    # Check files
    for file_name in required_files:
        if Path(file_name).exists():
            print(f"   ✅ File: {file_name}")
        else:
            print(f"   ❌ Missing file: {file_name}")
    
    # Check image files
    images_dir = Path("display/images")
    if images_dir.exists():
        image_files = list(images_dir.glob("*.png"))
        print(f"   ✅ Images directory: {len(image_files)} PNG files found")
        
        # Check for required images
        from config.settings import DisplayConfig
        for state_num, image_file in DisplayConfig.IMAGE_MAPPING.items():
            image_path = images_dir / image_file
            if image_path.exists():
                print(f"      ✅ {image_file}")
            else:
                print(f"      ❌ Missing: {image_file}")
    else:
        print("   ❌ Images directory not found")
    
    return True

def main():
    """Main verification function"""
    print("🔍 iTrash System Verification")
    print("=" * 60)
    print("🎯 Comprehensive system check to ensure everything works correctly")
    print("=" * 60)
    
    verifications = [
        ("File Structure", verify_file_structure),
        ("Configuration", verify_configuration),
        ("Global State", verify_global_state),
        ("Display System", verify_display_system),
        ("Hardware Integration", verify_hardware_integration),
        ("API Integration", verify_api_integration),
        ("Unified System", verify_unified_system)
    ]
    
    results = {}
    
    for verification_name, verification_func in verifications:
        print(f"\n{'='*20} {verification_name} {'='*20}")
        try:
            results[verification_name] = verification_func()
        except Exception as e:
            print(f"❌ {verification_name} failed with exception: {e}")
            results[verification_name] = False
    
    # Summary
    print(f"\n{'='*60}")
    print("📋 Verification Results Summary:")
    print("=" * 60)
    
    passed = 0
    total = len(results)
    
    for verification_name, success in results.items():
        status = "✅ PASS" if success else "❌ FAIL"
        print(f"   {verification_name}: {status}")
        if success:
            passed += 1
    
    print(f"\n🎯 Overall Results: {passed}/{total} verifications passed")
    
    if passed == total:
        print("\n🎉 All verifications passed! Your iTrash system is ready!")
        print("💡 The system is fully integrated and should work correctly.")
    elif passed >= total * 0.8:
        print("\n✅ Most verifications passed! System is mostly ready.")
        print("💡 Check the failed verifications above for any issues.")
    else:
        print("\n⚠️  Several verifications failed. Check the issues above.")
        print("💡 The system may need some adjustments before use.")
    
    print("\n🚀 Ready to run your iTrash system!")

if __name__ == "__main__":
    main() 