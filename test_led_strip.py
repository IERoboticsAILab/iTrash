#!/usr/bin/env python3
"""
Simple LED Strip Test - Turn on all LEDs
"""

from core.hardware import HardwareController
from config.settings import Colors

# Initialize hardware
print("🔧 Initializing hardware...")
hardware = HardwareController()
led_strip = hardware.get_led_strip()
print("✅ Hardware initialized successfully")

# Turn on all LEDs to white
print("💡 Turning on all LEDs...")
led_strip.set_color_all(Colors.WHITE)
print("✅ All LEDs are now ON")

print("Press Ctrl+C to stop")
try:
    while True:
        pass
except KeyboardInterrupt:
    print("\n🛑 Shutting down...")
    led_strip.clear_all()
    hardware.cleanup()
    print("✅ LEDs turned off and hardware cleaned up") 