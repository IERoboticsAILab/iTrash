"""
Test script for iTrash unified system.
Tests all components individually and together.
"""

import sys
import os
import time
import asyncio

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import *
from core.hardware import HardwareController
from core.camera import CameraController
from core.ai_classifier import ClassificationManager
from core.database import db_manager
from display.media_display import DisplayManager

def test_database():
    """Test database connection and operations"""
    print("Testing database...")
    
    try:
        # Test connection
        if db_manager.connect():
            print("✅ Database connection successful")
        else:
            print("❌ Database connection failed")
            return False
        
        # Test accumulator operations
        db_manager.update_acc(0)
        acc_value = db_manager.get_acc_value()
        print(f"✅ Accumulator value: {acc_value}")
        
        # Test increment
        db_manager.increment_acc(1)
        acc_value = db_manager.get_acc_value()
        print(f"✅ Incremented accumulator: {acc_value}")
        
        return True
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_hardware():
    """Test hardware components"""
    print("Testing hardware...")
    
    try:
        hardware = HardwareController()
        print("✅ Hardware controller initialized")
        
        # Test LED strip
        led_strip = hardware.get_led_strip()
        print("✅ LED strip initialized")
        
        # Test basic LED operations
        led_strip.set_color_all((255, 0, 0))  # Red
        print("✅ LED strip set to red")
        time.sleep(1)
        
        led_strip.set_color_all((0, 255, 0))  # Green
        print("✅ LED strip set to green")
        time.sleep(1)
        
        led_strip.clear_all()
        print("✅ LED strip cleared")
        
        # Test proximity sensors
        proximity_sensors = hardware.get_proximity_sensors()
        print("✅ Proximity sensors initialized")
        
        # Test sensor readings (just check if they don't crash)
        proximity_sensors.detect_object_proximity()
        proximity_sensors.detect_blue_bin()
        proximity_sensors.detect_yellow_bin()
        proximity_sensors.detect_brown_bin()
        print("✅ Proximity sensor readings successful")
        
        # Cleanup
        hardware.cleanup()
        print("✅ Hardware cleanup successful")
        
        return True
        
    except Exception as e:
        print(f"❌ Hardware test failed: {e}")
        return False

def test_camera():
    """Test camera functionality"""
    print("Testing camera...")
    
    try:
        camera = CameraController()
        
        if camera.initialize():
            print("✅ Camera initialized")
            
            # Test frame capture
            frame = camera.capture_image()
            if frame is not None:
                print(f"✅ Frame captured: {frame.shape}")
            else:
                print("❌ Frame capture failed")
                return False
            
            # Test base64 encoding
            base64_image = camera.encode_image_to_base64(frame)
            if base64_image:
                print(f"✅ Image encoded to base64: {len(base64_image)} characters")
            else:
                print("❌ Base64 encoding failed")
                return False
            
            # Test QR code detection (with empty frame)
            qr_data = camera.detect_qr_code(frame)
            print(f"✅ QR detection test completed: {qr_data}")
            
            # Cleanup
            camera.release()
            print("✅ Camera cleanup successful")
            
            return True
        else:
            print("❌ Camera initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_ai_classifier():
    """Test AI classifier"""
    print("Testing AI classifier...")
    
    try:
        classifier = ClassificationManager()
        print("✅ Classifier initialized")
        
        # Test stats
        stats = classifier.get_classification_stats()
        print(f"✅ Classifier stats: {stats}")
        
        return True
        
    except Exception as e:
        print(f"❌ AI classifier test failed: {e}")
        return False

async def test_classification_with_image():
    """Test classification with a sample image"""
    print("Testing classification with image...")
    
    try:
        # Create a simple test image
        import numpy as np
        import cv2
        
        # Create a simple colored rectangle
        test_image = np.zeros((224, 224, 3), dtype=np.uint8)
        test_image[50:150, 50:150] = [255, 0, 0]  # Blue rectangle
        
        classifier = ClassificationManager()
        
        # Test classification
        result = await classifier.process_image_with_feedback(test_image)
        print(f"✅ Classification result: {result}")
        
        return True
        
    except Exception as e:
        print(f"❌ Classification test failed: {e}")
        return False

def test_display():
    """Test display functionality"""
    print("Testing display...")
    
    try:
        display_manager = DisplayManager()
        print("✅ Display manager initialized")
        
        # Test status
        status = display_manager.get_display_status()
        print(f"✅ Display status: {status}")
        
        return True
        
    except Exception as e:
        print(f"❌ Display test failed: {e}")
        return False

def test_configuration():
    """Test configuration loading"""
    print("Testing configuration...")
    
    try:
        # Test hardware config
        print(f"✅ LED count: {HardwareConfig.LED_COUNT}")
        print(f"✅ LED pin: {HardwareConfig.LED_PIN}")
        print(f"✅ Camera index: {HardwareConfig.CAMERA_INDEX}")
        
        # Test system states
        print(f"✅ System states: {SystemStates.IDLE}, {SystemStates.PROCESSING}")
        
        # Test colors
        print(f"✅ Colors: {Colors.BLUE}, {Colors.YELLOW}, {Colors.BROWN}")
        
        # Test display config
        print(f"✅ Window size: {DisplayConfig.WINDOW_WIDTH}x{DisplayConfig.WINDOW_HEIGHT}")
        
        return True
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False

async def run_all_tests():
    """Run all tests"""
    print("🧪 Starting iTrash System Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Database", test_database),
        ("Hardware", test_hardware),
        ("Camera", test_camera),
        ("AI Classifier", test_ai_classifier),
        ("Classification with Image", test_classification_with_image),
        ("Display", test_display),
    ]
    
    results = {}
    
    for test_name, test_func in tests:
        print(f"\n🔍 Testing {test_name}...")
        try:
            if asyncio.iscoroutinefunction(test_func):
                result = await test_func()
            else:
                result = test_func()
            results[test_name] = result
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results[test_name] = False
    
    # Print summary
    print("\n" + "=" * 50)
    print("📊 Test Results Summary")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results.items():
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{test_name}: {status}")
        if result:
            passed += 1
    
    print(f"\nOverall: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to run.")
        return True
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        return False

def main():
    """Main test function"""
    try:
        success = asyncio.run(run_all_tests())
        if success:
            print("\n🚀 Ready to start iTrash system!")
            print("Run 'python main.py' to start the system")
        else:
            print("\n🔧 Please fix the failed tests before running the system")
        
    except KeyboardInterrupt:
        print("\n⏹️  Tests interrupted by user")
    except Exception as e:
        print(f"\n💥 Test suite crashed: {e}")

if __name__ == "__main__":
    main() 