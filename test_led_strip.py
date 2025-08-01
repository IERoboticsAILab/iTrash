from rpi_ws281x import Adafruit_NeoPixel, Color
import time

# LED configuration
STRIP1_COUNT = 62
STRIP1_PIN = 18  # GPIO 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 100
LED_INVERT = False
LED_CHANNEL = 0

# Initialize
strip1 = Adafruit_NeoPixel(STRIP1_COUNT, STRIP1_PIN, LED_FREQ_HZ, LED_DMA,
                           LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
strip1.begin()

# Test: fill with green
for i in range(strip1.numPixels()):
    strip1.setPixelColor(i, Color(0, 255, 0))  # Green
strip1.show()