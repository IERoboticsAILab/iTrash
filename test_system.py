#!/usr/bin/env python3
"""
Comprehensive system test for iTrash on Raspberry Pi.
Tests all hardware components and software functionality.
"""

import time
import sys
import os
import threading
from datetime import datetime

def test_imports():
    """Test if all required modules can be imported"""
    print("🔍 Testing module imports...")
    
    try:
        import cv2
        print("✅ OpenCV imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import OpenCV: {e}")
        return False
    
    try:
        import RPi.GPIO as GPIO
        print("✅ RPi.GPIO imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import RPi.GPIO: {e}")
        print("   This is required for proximity sensors")
        return False
    
    try:
        from rpi_ws281x import Adafruit_NeoPixel, Color
        print("✅ rpi_ws281x imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import rpi_ws281x: {e}")
        print("   This is required for LED strip")
        return False
    
    try:
        from pynput import keyboard
        print("✅ pynput imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import pynput: {e}")
        print("   This is required for manual controls")
        return False
    
    try:
        import numpy as np
        from PIL import Image
        print("✅ NumPy and PIL imported successfully")
    except ImportError as e:
        print(f"❌ Failed to import NumPy/PIL: {e}")
        return False
    
    return True

def test_gpio():
    """Test GPIO functionality"""
    print("\n🔌 Testing GPIO functionality...")
    
    try:
        import RPi.GPIO as GPIO
        
        # Test GPIO setup
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Test pins from config
        from config.settings import HardwareConfig
        
        test_pins = [
            HardwareConfig.DETECT_OBJECT_SENSOR_PIN,
            HardwareConfig.BLUE_PROXIMITY_PIN,
            HardwareConfig.YELLOW_PROXIMITY_PIN,
            HardwareConfig.BROWN_PROXIMITY_PIN
        ]
        
        for pin in test_pins:
            try:
                GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
                state = GPIO.input(pin)
                print(f"✅ Pin {pin} configured successfully (state: {state})")
            except Exception as e:
                print(f"❌ Failed to configure pin {pin}: {e}")
        
        GPIO.cleanup()
        return True
        
    except Exception as e:
        print(f"❌ GPIO test failed: {e}")
        return False

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
        
        print("✅ LED strip initialized successfully")
        
        # Test different colors
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 255)]
        color_names = ["Red", "Green", "Blue", "White"]
        
        for color, name in zip(colors, color_names):
            print(f"   Testing {name} color...")
            for i in range(strip.numPixels()):
                strip.setPixelColor(i, Color(*color))
            strip.show()
            time.sleep(0.5)
        
        # Clear LEDs
        for i in range(strip.numPixels()):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        
        print("✅ LED strip test completed successfully")
        return True
        
    except Exception as e:
        print(f"❌ LED strip test failed: {e}")
        return False

def test_camera():
    """Test camera functionality"""
    print("\n📷 Testing camera...")
    
    try:
        from core.camera import CameraController
        
        camera = CameraController()
        
        if camera.initialize():
            print("✅ Camera initialized successfully")
            
            # Test frame capture
            frame = camera.capture_image()
            if frame is not None:
                height, width = frame.shape[:2]
                print(f"✅ Frame captured successfully: {width}x{height}")
                
                # Test image encoding
                encoded = camera.encode_image_to_base64(frame)
                if encoded:
                    print("✅ Image encoding successful")
                else:
                    print("❌ Image encoding failed")
            else:
                print("❌ Frame capture failed")
            
            camera.release()
            return True
        else:
            print("❌ Camera initialization failed")
            return False
            
    except Exception as e:
        print(f"❌ Camera test failed: {e}")
        return False

def test_manual_controls():
    """Test manual controls functionality"""
    print("\n⌨️  Testing manual controls...")
    
    try:
        from core.manual_controls import ManualProximitySensors
        
        sensors = ManualProximitySensors()
        print("✅ Manual proximity sensors initialized")
        print("   Press keys to test:")
        print("   - 'o' for object detection")
        print("   - 'b' for blue bin")
        print("   - 'y' for yellow bin")
        print("   - 'r' for brown bin")
        print("   - 'c' to clear all")
        print("   - 'q' to quit test")
        
        # Test for 10 seconds
        start_time = time.time()
        while time.time() - start_time < 10:
            if sensors.detect_object_proximity():
                print("   ✅ Object detection triggered")
            if sensors.detect_blue_bin():
                print("   ✅ Blue bin triggered")
            if sensors.detect_yellow_bin():
                print("   ✅ Yellow bin triggered")
            if sensors.detect_brown_bin():
                print("   ✅ Brown bin triggered")
            time.sleep(0.1)
        
        sensors.cleanup()
        print("✅ Manual controls test completed")
        return True
        
    except Exception as e:
        print(f"❌ Manual controls test failed: {e}")
        return False

def test_display():
    """Test display functionality"""
    print("\n🖥️  Testing display...")
    
    try:
        from display.media_display import DisplayManager
        from config.settings import DisplayConfig, SystemStates
        import os
        
        # Test display manager initialization
        manager = DisplayManager()
        print("✅ Display manager initialized")
        
        # Check if display images exist
        images_dir = "display/images"
        if not os.path.exists(images_dir):
            print(f"❌ Display images directory not found: {images_dir}")
            return False
        
        # Check each required image
        missing_images = []
        for acc_value, image_file in DisplayConfig.IMAGE_MAPPING.items():
            image_path = os.path.join(images_dir, image_file)
            if os.path.exists(image_path):
                print(f"   ✅ {image_file} found")
            else:
                print(f"   ❌ {image_file} missing")
                missing_images.append(image_file)
        
        if missing_images:
            print(f"❌ Missing images: {', '.join(missing_images)}")
            return False
        
        # Test display status
        status = manager.get_display_status()
        print(f"   Display status: {status}")
        
        # Test image loading and display
        print("   Testing image display...")
        try:
            from PIL import Image, ImageTk
            import tkinter as tk
            
            # Create a test window
            root = tk.Tk()
            root.title("Display Test")
            root.geometry("800x600")
            
            # Test loading and displaying each image
            for acc_value, image_file in DisplayConfig.IMAGE_MAPPING.items():
                image_path = os.path.join(images_dir, image_file)
                try:
                    # Load and resize image
                    image = Image.open(image_path)
                    image = image.convert("RGB")
                    image = image.resize((400, 300), Image.Resampling.LANCZOS)
                    
                    # Convert to PhotoImage
                    photo = ImageTk.PhotoImage(image)
                    
                    # Display in window
                    label = tk.Label(root, image=photo)
                    label.image = photo  # Keep a reference
                    label.pack()
                    
                    print(f"   ✅ {image_file} displayed successfully")
                    
                    # Update window
                    root.update()
                    time.sleep(0.5)  # Show each image briefly
                    
                    # Remove label for next image
                    label.destroy()
                    
                except Exception as e:
                    print(f"   ❌ Failed to display {image_file}: {e}")
                    root.destroy()
                    return False
            
            root.destroy()
            print("   ✅ All images displayed successfully")
            
        except Exception as e:
            print(f"   ❌ Image display test failed: {e}")
            return False
        
        print("✅ Display test completed")
        return True
        
    except Exception as e:
        print(f"❌ Display test failed: {e}")
        return False

def test_database():
    """Test database connectivity"""
    print("\n🗄️  Testing database...")
    
    try:
        from core.database import db_manager
        
        if db_manager.connect():
            print("✅ Database connection successful")
            
            # Test accumulator operations
            db_manager.update_acc(0)
            acc_value = db_manager.get_acc_value()
            print(f"   Accumulator value: {acc_value}")
            
            return True
        else:
            print("❌ Database connection failed")
            return False
            
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False

def test_hardware_controller():
    """Test complete hardware controller"""
    print("\n🔧 Testing hardware controller...")
    
    try:
        from core.hardware import HardwareController
        
        controller = HardwareController()
        print("✅ Hardware controller initialized")
        
        # Test LED strip
        led_strip = controller.get_led_strip()
        if led_strip:
            print("✅ LED strip accessible")
            led_strip.set_color_all((255, 0, 0))  # Red
            time.sleep(1)
            led_strip.clear_all()
        
        # Test proximity sensors
        sensors = controller.get_proximity_sensors()
        if sensors:
            print("✅ Proximity sensors accessible")
            # Test sensor states
            print(f"   Object sensor: {sensors.detect_object_proximity()}")
            print(f"   Blue bin: {sensors.detect_blue_bin()}")
            print(f"   Yellow bin: {sensors.detect_yellow_bin()}")
            print(f"   Brown bin: {sensors.detect_brown_bin()}")
        
        controller.cleanup()
        print("✅ Hardware controller test completed")
        return True
        
    except Exception as e:
        print(f"❌ Hardware controller test failed: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting iTrash Raspberry Pi System Test")
    print("=" * 50)
    
    tests = [
        ("Module Imports", test_imports),
        ("GPIO", test_gpio),
        ("LED Strip", test_led_strip),
        ("Camera", test_camera),
        ("Manual Controls", test_manual_controls),
        ("Display", test_display),
        ("Database", test_database),
        ("Hardware Controller", test_hardware_controller)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
            results.append((test_name, False))
    
    # Summary
    print("\n" + "=" * 50)
    print("📊 TEST SUMMARY")
    print("=" * 50)
    
    passed = 0
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} {test_name}")
        if result:
            passed += 1
    
    print(f"\nResults: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! System is ready to use.")
    else:
        print("⚠️  Some tests failed. Please check the issues above.")
        print("\nTroubleshooting tips:")
        print("1. Make sure all dependencies are installed: pip install -r requirements.txt")
        print("2. Check camera permissions and connections")
        print("3. Verify GPIO pins are not in use by other processes")
        print("4. Ensure you're running on a Raspberry Pi with proper hardware")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 