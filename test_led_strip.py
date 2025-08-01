#!/usr/bin/env python3
"""
Simple LED Strip Test - Standalone initialization
"""

import RPi.GPIO as GPIO
from rpi_ws281x import *

# LED Configuration
LED_COUNT = 60
LED_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 125
LED_INVERT = False
LED_CHANNEL = 0

# Initialize LED strip directly
print("🔧 Initializing LED strip...")
strip = Adafruit_NeoPixel(
    LED_COUNT,
    LED_PIN,
    LED_FREQ_HZ,
    LED_DMA,
    LED_INVERT,
    LED_BRIGHTNESS,
    LED_CHANNEL
)
strip.begin()
print("✅ LED strip initialized successfully")

# Turn on all LEDs to white
print("💡 Turning on all LEDs...")
for i in range(LED_COUNT):
    strip.setPixelColor(i, Color(255, 255, 255))
strip.show()
print("✅ All LEDs are now ON")

print("Press Ctrl+C to stop")
try:
    while True:
        pass
except KeyboardInterrupt:
    print("\n🛑 Shutting down...")
    # Turn off all LEDs
    for i in range(LED_COUNT):
        strip.setPixelColor(i, Color(0, 0, 0))
    strip.show()
    print("✅ LEDs turned off") 