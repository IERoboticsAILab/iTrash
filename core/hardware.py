"""
Hardware control module for iTrash system.
Handles LED strip and proximity sensor operations.
"""

import time
import math
import random
import RPi.GPIO as GPIO
from rpi_ws281x import *
from config.settings import HardwareConfig, Colors

class LEDStrip:
    """WS2812B LED strip controller"""
    
    def __init__(self):
        self.strip = Adafruit_NeoPixel(
            HardwareConfig.LED_COUNT,
            HardwareConfig.LED_PIN,
            HardwareConfig.LED_FREQ_HZ,
            HardwareConfig.LED_DMA,
            HardwareConfig.LED_INVERT,
            HardwareConfig.LED_BRIGHTNESS,
            HardwareConfig.LED_CHANNEL
        )
        self.strip.begin()
        self.clear_all()
    
    def set_pixel_color(self, pixel_index, color):
        """Set color of a specific pixel"""
        self.strip.setPixelColor(pixel_index, Color(*color))
        self.strip.show()
    
    def set_color_all(self, color):
        """Set all LEDs to the same color"""
        for i in range(HardwareConfig.LED_COUNT):
            self.strip.setPixelColor(i, Color(*color))
        self.strip.show()
    
    def clear_all(self):
        """Turn off all LEDs"""
        self.set_color_all(Colors.EMPTY)
    
    def set_white_all(self):
        """Set all LEDs to white"""
        self.set_color_all(Colors.WHITE)
    
    def set_colors(self, colors):
        """Set multiple LEDs to different colors"""
        for i, color in enumerate(colors):
            if i < HardwareConfig.LED_COUNT:
                self.strip.setPixelColor(i, Color(*color))
        self.strip.show()
    
    def set_color_range_percent(self, color, start_percent, end_percent):
        """Set colors based on start and end percentages"""
        start_index = int(HardwareConfig.LED_COUNT * start_percent)
        end_index = int(HardwareConfig.LED_COUNT * end_percent)
        index_range = end_index - start_index
        
        if end_index < start_index:
            index_range = HardwareConfig.LED_COUNT - end_index + start_index
        
        for i in range(index_range):
            self.strip.setPixelColor((start_index + i) % HardwareConfig.LED_COUNT, Color(*color))
        
        self.strip.show()
    
    def set_color_range_exact(self, color, start_index, end_index):
        """Set colors based on exact start and end indices"""
        index_range = end_index - start_index
        
        if end_index < start_index:
            index_range = HardwareConfig.LED_COUNT - end_index + start_index
        
        for i in range(index_range):
            self.strip.setPixelColor((start_index + i) % HardwareConfig.LED_COUNT, Color(*color))
        
        self.strip.show()
    
    def wheel(self, pos):
        """Generate rainbow colors across 0-255 positions"""
        if pos < 85:
            return Color(pos * 3, 255 - pos * 3, 0)
        elif pos < 170:
            pos -= 85
            return Color(255 - pos * 3, 0, pos * 3)
        else:
            pos -= 170
            return Color(0, pos * 3, 255 - pos * 3)
    
    def glow(self, color, wait_ms=10):
        """Glowing effect - fade in and out"""
        # Fade In
        for i in range(0, 256):
            r = int(math.floor((i / 256.0) * color[0]))
            g = int(math.floor((i / 256.0) * color[1]))
            b = int(math.floor((i / 256.0) * color[2]))
            self.set_color_all((r, g, b))
            time.sleep(wait_ms / 1000.0)
        
        # Fade Out
        for i in range(256, 0, -1):
            r = int(math.floor((i / 256.0) * color[0]))
            g = int(math.floor((i / 256.0) * color[1]))
            b = int(math.floor((i / 256.0) * color[2]))
            self.set_color_all((r, g, b))
            time.sleep(wait_ms / 1000.0)
    
    def color_wipe(self, color, wait_ms=50):
        """Wipe color across the display one pixel at a time"""
        for i in range(self.strip.numPixels()):
            self.strip.setPixelColor(i, Color(*color))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)
    
    def sparkle(self, color, wait_ms=50, cumulative=False):
        """Display random pixels across the display"""
        self.clear_all()
        for i in range(0, HardwareConfig.LED_COUNT):
            self.strip.setPixelColor(random.randrange(0, HardwareConfig.LED_COUNT), Color(*color))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)
            if not cumulative:
                self.clear_all()
        time.sleep(wait_ms / 1000.0)
    
    def rainbow(self, wait_ms=50, iterations=1):
        """Draw rainbow that fades across all pixels at once"""
        for j in range(256 * iterations):
            for i in range(self.strip.numPixels()):
                self.strip.setPixelColor(i, self.wheel((i + j) & 255))
            self.strip.show()
            time.sleep(wait_ms / 1000.0)
    
    def theater_chase(self, color, wait_ms=50, iterations=10):
        """Movie theater light style chaser animation"""
        for j in range(iterations):
            for q in range(3):
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, Color(*color))
                self.strip.show()
                time.sleep(wait_ms / 1000.0)
                for i in range(0, self.strip.numPixels(), 3):
                    self.strip.setPixelColor(i + q, 0)
    
    def running(self, wait_ms=10, duration_ms=6000, width=1):
        """Running light effect"""
        self.clear_all()
        index = 0
        while duration_ms > 0:
            self.strip.setPixelColor((index - width) % HardwareConfig.LED_COUNT, Color(0, 0, 0))
            self.strip.setPixelColor(index, Color(255, 0, 0))
            self.strip.show()
            index = (index + 1) % HardwareConfig.LED_COUNT
            duration_ms -= wait_ms
            time.sleep(wait_ms / 1000)


class ProximitySensors:
    """Proximity sensor controller"""
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        
        # Initialize all proximity sensors
        self.detect_object_sensor = self._initialize_sensor(HardwareConfig.DETECT_OBJECT_SENSOR_PIN)
        self.blue_proximity = self._initialize_sensor(HardwareConfig.BLUE_PROXIMITY_PIN)
        self.yellow_proximity = self._initialize_sensor(HardwareConfig.YELLOW_PROXIMITY_PIN)
        self.brown_proximity = self._initialize_sensor(HardwareConfig.BROWN_PROXIMITY_PIN)
    
    def _initialize_sensor(self, pin):
        """Initialize a proximity sensor on the specified pin"""
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        return pin
    
    def detect_object(self, sensor_pin):
        """Detect if an object is present on the specified sensor"""
        state = GPIO.input(sensor_pin)
        # 0 --> object detected
        # 1 --> no object
        if state == 0:
            print(f"Object Detected on pin {sensor_pin}")
            return True
        else:
            return False
    
    def detect_object_proximity(self):
        """Detect object on the main object detection sensor"""
        return self.detect_object(self.detect_object_sensor)
    
    def detect_blue_bin(self):
        """Detect object in blue bin"""
        return self.detect_object(self.blue_proximity)
    
    def detect_yellow_bin(self):
        """Detect object in yellow bin"""
        return self.detect_object(self.yellow_proximity)
    
    def detect_brown_bin(self):
        """Detect object in brown bin"""
        return self.detect_object(self.brown_proximity)
    
    def cleanup(self):
        """Clean up GPIO resources"""
        GPIO.cleanup()


class HardwareController:
    """Main hardware controller that combines LED strip and proximity sensors"""
    
    def __init__(self):
        self.led_strip = LEDStrip()
        self.proximity_sensors = ProximitySensors()
    
    def get_led_strip(self):
        """Get LED strip instance"""
        return self.led_strip
    
    def get_proximity_sensors(self):
        """Get proximity sensors instance"""
        return self.proximity_sensors
    
    def cleanup(self):
        """Clean up all hardware resources"""
        self.led_strip.clear_all()
        self.proximity_sensors.cleanup()
    
    def blink_leds(self, color, duration=1.0, interval=0.5):
        """Blink all LEDs with specified color"""
        start_time = time.time()
        while time.time() - start_time < duration:
            self.led_strip.set_color_all(color)
            time.sleep(interval)
            self.led_strip.clear_all()
            time.sleep(interval)
    
    def show_processing_animation(self):
        """Show processing animation on LED strip"""
        self.led_strip.running(wait_ms=50, duration_ms=3000, width=3)
    
    def show_success_animation(self):
        """Show success animation on LED strip"""
        self.led_strip.glow(Colors.GREEN, wait_ms=20)
    
    def show_error_animation(self):
        """Show error animation on LED strip"""
        start_time = time.time()
        while time.time() - start_time < 2.0:
            self.led_strip.set_color_all(Colors.RED)
            time.sleep(0.3)
            self.led_strip.clear_all()
            time.sleep(0.3) 