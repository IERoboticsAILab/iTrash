from rpi_ws281x import PixelStrip, Color

# LED configuration:
LED_COUNT = 30         # Number of LED pixels
LED_PIN = 13           # GPIO 13
LED_FREQ_HZ = 800000   # LED signal frequency
LED_DMA = 10           # DMA channel
LED_BRIGHTNESS = 255   # Max brightness
LED_INVERT = False     # True if using NPN transistor level shift
LED_CHANNEL = 1        # Channel 1 for GPIO 13

def setup_leds():
    strip = PixelStrip(LED_COUNT, LED_PIN, LED_FREQ_HZ, LED_DMA, LED_INVERT,
                       LED_BRIGHTNESS, LED_CHANNEL)
    strip.begin()
    return strip

def simple_test(strip):
    for i in range(strip.numPixels()):
        strip.setPixelColor(i, Color(255, 0, 0))  # Red
    strip.show()

# Example usage:
if __name__ == '__main__':
    strip = setup_leds()
    simple_test(strip)