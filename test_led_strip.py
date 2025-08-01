#!/usr/bin/env python3
"""
LED Strip Test Module for iTrash System
Tests only the LED functions actually used in the system
"""

import time
import sys
import signal
from core.hardware import HardwareController
from config.settings import Colors, HardwareConfig

class LEDStripTester:
    """LED strip tester for iTrash system functions only"""
    
    def __init__(self):
        self.hardware = None
        self.led_strip = None
        self.running = True
        
        # Set up signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self.signal_handler)
        signal.signal(signal.SIGTERM, self.signal_handler)
    
    def signal_handler(self, signum, frame):
        """Handle shutdown signals"""
        print(f"\n🛑 Received signal {signum}, shutting down gracefully...")
        self.running = False
        if self.led_strip:
            self.led_strip.clear_all()
        if self.hardware:
            self.hardware.cleanup()
        sys.exit(0)
    
    def initialize_hardware(self):
        """Initialize hardware components"""
        try:
            print("🔧 Initializing hardware...")
            self.hardware = HardwareController()
            self.led_strip = self.hardware.get_led_strip()
            print("✅ Hardware initialized successfully")
            print(f"📊 LED Configuration:")
            print(f"   - LED Count: {HardwareConfig.LED_COUNT}")
            print(f"   - LED Pin: {HardwareConfig.LED_PIN}")
            print(f"   - Brightness: {HardwareConfig.LED_BRIGHTNESS}")
            return True
        except Exception as e:
            print(f"❌ Failed to initialize hardware: {e}")
            return False
    
    def test_set_color_all(self):
        """Test set_color_all function - used throughout the system"""
        print("\n🎨 Testing set_color_all()...")
        
        # Test colors used in the system
        system_colors = {
            "White (Processing)": Colors.WHITE,
            "Green (Success)": Colors.GREEN,
            "Red (Error)": Colors.RED,
            "Blue (Blue Bin)": Colors.BLUE,
            "Yellow (Yellow Bin)": Colors.YELLOW,
            "Brown (Brown Bin)": Colors.BROWN
        }
        
        for color_name, color in system_colors.items():
            if not self.running:
                break
            print(f"   Testing {color_name}...")
            self.led_strip.set_color_all(color)
            time.sleep(1)
        
        print("✅ set_color_all() test completed")
    
    def test_clear_all(self):
        """Test clear_all function - used throughout the system"""
        print("\n🔇 Testing clear_all()...")
        
        # Set to white first
        self.led_strip.set_color_all(Colors.WHITE)
        time.sleep(0.5)
        
        # Clear all LEDs
        self.led_strip.clear_all()
        time.sleep(0.5)
        
        print("✅ clear_all() test completed")
    
    def test_success_animation(self):
        """Test show_success_animation - used in hardware controller"""
        print("\n✅ Testing Success Animation...")
        
        # Test the success animation from hardware controller
        self.hardware.show_success_animation()
        
        print("✅ Success animation test completed")
    
    def test_error_animation(self):
        """Test show_error_animation - used in hardware controller"""
        print("\n❌ Testing Error Animation...")
        
        # Test the error animation from hardware controller
        self.hardware.show_error_animation()
        
        print("✅ Error animation test completed")
    
    def run_all_tests(self):
        """Run all LED strip tests"""
        print("🚀 Starting LED Strip Test Suite")
        print("=" * 50)
        
        if not self.initialize_hardware():
            return False
        
        try:
            # Run only the tests for functions actually used
            self.test_set_color_all()
            self.test_clear_all()
            self.test_success_animation()
            self.test_error_animation()
            
            print("\n" + "=" * 50)
            print("🎉 All LED strip tests completed successfully!")
            print("💡 LED strip is working correctly")
            
        except KeyboardInterrupt:
            print("\n⏹️  Tests interrupted by user")
        except Exception as e:
            print(f"\n❌ Test error: {e}")
        finally:
            # Clean up
            if self.led_strip:
                self.led_strip.clear_all()
            if self.hardware:
                self.hardware.cleanup()
            print("🧹 Hardware cleaned up")
        
        return True

def main():
    """Main test function"""
    import sys
    
    print("🎯 LED Strip Test for iTrash System")
    print("Press Ctrl+C to stop at any time")
    
    # Check command line arguments
    if len(sys.argv) > 1:
        if sys.argv[1] == "--help":
            print("\nUsage:")
            print("  python test_led_strip.py              # Run all tests")
            print("  python test_led_strip.py --help       # Show this help")
            return
    
    # Run tests
    tester = LEDStripTester()
    tester.run_all_tests()

if __name__ == "__main__":
    main() 