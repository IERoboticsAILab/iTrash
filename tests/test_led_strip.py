#!/usr/bin/env python3
"""
Test script for LED strip functionality.
Tests basic LED operations to ensure hardware is working.
"""

import time
import os
import sys

# Add the parent directory to the path so we can import our modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.hardware import HardwareController, LEDStrip
from config.settings import Colors

def test_led_strip_direct():
    """Test LED strip directly"""
    print("🔴 Testing LED Strip Directly")
    
    try:
        # Test direct LED strip initialization
        led_strip = LEDStrip()
        print("✅ LED strip initialized")
        
        # Test basic colors
        colors = [
            ("Red", (255, 0, 0)),
            ("Green", (0, 255, 0)),
            ("Blue", (0, 0, 255)),
            ("Yellow", (255, 255, 0)),
            ("White", (255, 255, 255)),
            ("Off", (0, 0, 0))
        ]
        
        for color_name, color_value in colors:
            print(f"   Testing {color_name}...")
            led_strip.set_color_all(color_value)
            time.sleep(1)
        
        # Test flash
        print("   Testing flash...")
        led_strip.flash(Colors.RED, 500)
        
        # Clear
        led_strip.clear_all()
        print("✅ LED strip test completed")
        
    except Exception as e:
        print(f"❌ LED strip test failed: {e}")

def test_hardware_controller():
    """Test hardware controller"""
    print("\n🔧 Testing Hardware Controller")
    
    try:
        # Test hardware controller initialization
        hardware = HardwareController()
        print("✅ Hardware controller initialized")
        
        # Get LED strip
        led_strip = hardware.get_led_strip()
        if led_strip:
            print("✅ LED strip retrieved from controller")
            
            # Test colors through controller
            print("   Testing colors through controller...")
            led_strip.set_color_all((255, 0, 0))  # Red
            time.sleep(1)
            led_strip.set_color_all((0, 255, 0))  # Green
            time.sleep(1)
            led_strip.set_color_all((0, 0, 255))  # Blue
            time.sleep(1)
            
            # Test animations
            print("   Testing success animation...")
            hardware.show_success_animation()
            time.sleep(1)
            
            print("   Testing error animation...")
            hardware.show_error_animation()
            time.sleep(1)
            
            # Clear
            led_strip.clear_all()
            print("✅ Hardware controller test completed")
        else:
            print("❌ LED strip not available from controller")
            
    except Exception as e:
        print(f"❌ Hardware controller test failed: {e}")

def test_led_operations():
    """Test specific LED operations used in the system"""
    print("\n🎯 Testing System LED Operations")
    
    try:
        hardware = HardwareController()
        led_strip = hardware.get_led_strip()
        
        if not led_strip:
            print("❌ LED strip not available")
            return
        
        # Test the exact operations used in the system
        operations = [
            ("White (processing)", (255, 255, 255)),
            ("Blue (blue trash)", (0, 0, 255)),
            ("Yellow (yellow trash)", (255, 255, 0)),
            ("Brown (brown trash)", (139, 69, 19)),
            ("Clear", (0, 0, 0))
        ]
        
        for op_name, color in operations:
            print(f"   Testing {op_name}...")
            led_strip.set_color_all(color)
            time.sleep(2)
        
        print("✅ System LED operations test completed")
        
    except Exception as e:
        print(f"❌ System LED operations test failed: {e}")

def main():
    """Main test function"""
    print("💡 LED Strip Test Suite\n")
    
    # Test 1: Direct LED strip
    test_led_strip_direct()
    
    # Test 2: Hardware controller
    test_hardware_controller()
    
    # Test 3: System operations
    test_led_operations()
    
    print("\n" + "="*50)
    print("📋 Test Summary:")
    print("   • Direct LED strip functionality")
    print("   • Hardware controller integration")
    print("   • System-specific LED operations")
    print("   • If any test fails, check hardware connections")

if __name__ == "__main__":
    main() 