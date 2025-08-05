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
    
    def set_color_all(self, color):
        """Set all LEDs to the same color"""
        for i in range(HardwareConfig.LED_COUNT):
            self.strip.setPixelColor(i, Color(*color))
        self.strip.show()

    def flash(self, color, wait_ms=100):
        """Flash the LED strip with the given color"""
        self.set_color_all(color)
        time.sleep(wait_ms / 1000)
        self.clear_all()
        time.sleep(wait_ms / 1000)
    
    def clear_all(self):
        """Turn off all LEDs"""
        self.set_color_all(Colors.EMPTY)
    

class ProximitySensors:
    """Proximity sensor controller"""
    
    def __init__(self):
        GPIO.setmode(GPIO.BCM)
        
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
    
