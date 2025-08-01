import argparse
import time
from rpi_ws281x import Adafruit_NeoPixel, Color

# LED configuration
STRIP1_COUNT = 2
STRIP1_PIN = 18
LED_FREQ_HZ = 800000
LED_DMA = 10
LED_BRIGHTNESS = 100
LED_INVERT = False
LED_CHANNEL = 0

def run_test(clear=False):
    strip1 = Adafruit_NeoPixel(STRIP1_COUNT, STRIP1_PIN, LED_FREQ_HZ, LED_DMA,
                                LED_INVERT, LED_BRIGHTNESS, LED_CHANNEL)
    strip1.begin()

    # Light up green
    for i in range(strip1.numPixels()):
        strip1.setPixelColor(i, Color(0, 255, 0))
    strip1.show()
    time.sleep(1)

    # Clear if requested
    if clear:
        for i in range(strip1.numPixels()):
            strip1.setPixelColor(i, 0)
        strip1.show()

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--clear', action='store_true', help='Clear LEDs after lighting')
    args = parser.parse_args()

    run_test(clear=args.clear)