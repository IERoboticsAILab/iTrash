#!/usr/bin/env python3
"""
Simple LED strip test for iTrash system.
Tests only the LED strip functionality to isolate hardware issues.
"""

import sys
import os
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import HardwareConfig, Colors

def test_led_strip():
    """Test LED strip functionality"""
    print("🧪 Testing LED Strip")
    print("=" * 30)
    
    try:
        # Import the LED strip class
        from rpi_ws281x import Adafruit_NeoPixel, Color
        
        print(f"✅ rpi_ws281x library imported successfully")
        print(f"📋 Configuration:")
        print(f"   - LED Count: {HardwareConfig.LED_COUNT}")
        print(f"   - LED Pin: {HardwareConfig.LED_PIN}")
        print(f"   - Frequency: {HardwareConfig.LED_FREQ_HZ}")
        print(f"   - DMA: {HardwareConfig.LED_DMA}")
        print(f"   - Brightness: {HardwareConfig.LED_BRIGHTNESS}")
        print(f"   - Invert: {HardwareConfig.LED_INVERT}")
        print(f"   - Channel: {HardwareConfig.LED_CHANNEL}")
        
        # Initialize LED strip
        print("\n🔧 Initializing LED strip...")
        strip = Adafruit_NeoPixel(
            HardwareConfig.LED_COUNT,
            HardwareConfig.LED_PIN,
            HardwareConfig.LED_FREQ_HZ,
            HardwareConfig.LED_DMA,
            HardwareConfig.LED_INVERT,
            HardwareConfig.LED_BRIGHTNESS,
            HardwareConfig.LED_CHANNEL
        )
        
        print("✅ LED strip object created")
        
        # Begin the strip
        print("🔧 Starting LED strip...")
        strip.begin()
        print("✅ LED strip started successfully")
        
        # Test white color
        print("\n⚪ Setting all LEDs to WHITE...")
        white_color = Color(*Colors.WHITE)
        for i in range(HardwareConfig.LED_COUNT):
            strip.setPixelColor(i, white_color)
        strip.show()
        print("✅ All LEDs set to white")
        
        # Wait for 3 seconds
        print("⏱️  Keeping white for 3 seconds...")
        time.sleep(3)
        
        # Test clearing
        print("\n⚫ Clearing all LEDs...")
        for i in range(HardwareConfig.LED_COUNT):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        print("✅ All LEDs cleared")
        
        # Test individual colors
        print("\n🎨 Testing individual colors...")
        colors_to_test = [
            ("RED", Colors.RED),
            ("GREEN", Colors.GREEN),
            ("BLUE", Colors.BLUE),
            ("YELLOW", Colors.YELLOW),
            ("BROWN", Colors.BROWN)
        ]
        
        for color_name, color_value in colors_to_test:
            print(f"   Testing {color_name}...")
            color_obj = Color(*color_value)
            for i in range(HardwareConfig.LED_COUNT):
                strip.setPixelColor(i, color_obj)
            strip.show()
            time.sleep(1)
            
            # Clear
            for i in range(HardwareConfig.LED_COUNT):
                strip.setPixelColor(i, Color(0, 0, 0))
            strip.show()
        
        print("✅ All color tests completed")
        
        # Final white test
        print("\n⚪ Final test: Setting all LEDs to WHITE...")
        white_color = Color(*Colors.WHITE)
        for i in range(HardwareConfig.LED_COUNT):
            strip.setPixelColor(i, white_color)
        strip.show()
        print("✅ Final white test completed")
        print("💡 LEDs should now be WHITE")
        
        return True
        
    except ImportError as e:
        print(f"❌ Failed to import rpi_ws281x: {e}")
        print("Make sure you have installed: pip install rpi_ws281x")
        return False
        
    except Exception as e:
        print(f"❌ LED strip test failed: {e}")
        print(f"Error type: {type(e).__name__}")
        return False

def main():
    """Main test function"""
    print("🗑️  iTrash LED Strip Test")
    print("=" * 40)
    
    success = test_led_strip()
    
    if success:
        print("\n🎉 LED strip test completed successfully!")
        print("The LED strip is working correctly.")
    else:
        print("\n💥 LED strip test failed!")
        print("Please check the hardware connections and configuration.")
    
    print("\nPress Ctrl+C to exit...")
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Test completed")

if __name__ == "__main__":
    main() 