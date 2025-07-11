#!/usr/bin/env python3
"""
Quick test script for iTrash LED strip and basic functionality.
Run with: sudo .venv/bin/python quick_test.py
"""

import sys
import time

def test_imports():
    """Test critical imports"""
    print("🔍 Testing imports...")
    
    try:
        import RPi.GPIO as GPIO
        print("✅ RPi.GPIO imported")
    except ImportError as e:
        print(f"❌ RPi.GPIO failed: {e}")
        return False
    
    try:
        from rpi_ws281x import Adafruit_NeoPixel, Color
        print("✅ rpi_ws281x imported")
    except ImportError as e:
        print(f"❌ rpi_ws281x failed: {e}")
        return False
    
    try:
        import cv2
        print("✅ OpenCV imported")
    except ImportError as e:
        print(f"❌ OpenCV failed: {e}")
        return False
    
    return True

def test_led_strip():
    """Test LED strip functionality"""
    print("\n💡 Testing LED strip...")
    
    try:
        from rpi_ws281x import Adafruit_NeoPixel, Color
        from config.settings import HardwareConfig
        
        # Initialize LED strip
        strip = Adafruit_NeoPixel(
            HardwareConfig.LED_COUNT,
            HardwareConfig.LED_PIN,
            HardwareConfig.LED_FREQ_HZ,
            HardwareConfig.LED_DMA,
            HardwareConfig.LED_INVERT,
            HardwareConfig.LED_BRIGHTNESS,
            HardwareConfig.LED_CHANNEL
        )
        strip.begin()
        
        print("✅ LED strip initialized")
        
        # Test colors
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        names = ["Red", "Green", "Blue"]
        
        for color, name in zip(colors, names):
            print(f"   Testing {name}...")
            for i in range(min(10, strip.numPixels())):  # Test first 10 LEDs
                strip.setPixelColor(i, Color(*color))
            strip.show()
            time.sleep(1)
        
        # Clear
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        
        print("✅ LED strip test completed")
        return True
        
    except Exception as e:
        print(f"❌ LED strip test failed: {e}")
        return False

def test_camera():
    """Test camera"""
    print("\n📷 Testing camera...")
    
    try:
        import cv2
        
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            if ret:
                print(f"✅ Camera working: {frame.shape}")
                cap.release()
                return True
            else:
                print("❌ Camera can't capture frames")
                cap.release()
                return False
        else:
            print("❌ Camera can't open")
            return False
            
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_manual_controls():
    """Test manual controls briefly"""
    print("\n⌨️  Testing manual controls...")
    
    try:
        from core.manual_controls import ManualProximitySensors
        
        sensors = ManualProximitySensors()
        print("✅ Manual controls initialized")
        print("   (Press 'o' to test, or wait 3 seconds)")
        
        # Test for 3 seconds
        start_time = time.time()
        while time.time() - start_time < 3:
            if sensors.detect_object_proximity():
                print("   ✅ Object detection works!")
                break
            time.sleep(0.1)
        
        sensors.cleanup()
        print("✅ Manual controls test completed")
        return True
        
    except Exception as e:
        print(f"❌ Manual controls test failed: {e}")
        return False

def main():
    """Run quick tests"""
    print("🚀 iTrash Quick Test")
    print("=" * 30)
    
    if not test_imports():
        print("❌ Import test failed - check dependencies")
        return False
    
    tests = [
        ("LED Strip", test_led_strip),
        ("Camera", test_camera),
        ("Manual Controls", test_manual_controls)
    ]
    
    results = []
    for name, test_func in tests:
        try:
            result = test_func()
            results.append((name, result))
        except Exception as e:
            print(f"❌ {name} test crashed: {e}")
            results.append((name, False))
    
    print("\n" + "=" * 30)
    print("📊 RESULTS")
    print("=" * 30)
    
    passed = 0
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {name}")
        if result:
            passed += 1
    
    print(f"\nPassed: {passed}/{len(results)}")
    
    if passed == len(results):
        print("🎉 All tests passed! Ready to run the system.")
        print("\nTo start the system:")
        print("  sudo .venv/bin/python main_dev.py")
    else:
        print("⚠️  Some tests failed. Check the errors above.")
    
    return passed == len(results)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Test interrupted")
    except Exception as e:
        print(f"�� Test failed: {e}") 