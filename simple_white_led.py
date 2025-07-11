#!/usr/bin/env python3
"""
Simple script to set all LEDs to white.
Quick hardware verification for iTrash LED strip.
"""

import sys
import os
import time

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from config.settings import HardwareConfig

def set_white():
    """Set all LEDs to white"""
    try:
        from rpi_ws281x import Adafruit_NeoPixel, Color
        
        print("🔧 Initializing LED strip...")
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
        
        # Set all LEDs to white
        print("⚪ Setting all LEDs to WHITE...")
        white_color = Color(255, 255, 255)
        for i in range(HardwareConfig.LED_COUNT):
            strip.setPixelColor(i, white_color)
        strip.show()
        
        print("✅ All LEDs are now WHITE")
        print("💡 Press Ctrl+C to exit")
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n👋 Exiting...")
        # Clear LEDs before exit
        for i in range(HardwareConfig.LED_COUNT):
            strip.setPixelColor(i, Color(0, 0, 0))
        strip.show()
        print("✅ LEDs cleared")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        print("Check hardware connections and configuration")

if __name__ == "__main__":
    print("🗑️  iTrash - Simple White LED Test")
    print("=" * 40)
    set_white() 