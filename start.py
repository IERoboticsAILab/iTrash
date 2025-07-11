#!/usr/bin/env python3
"""
iTrash Raspberry Pi Startup Script
Handles system initialization and provides user guidance.
"""

import os
import sys
import time
import subprocess
from pathlib import Path

def check_raspberry_pi():
    """Check if running on Raspberry Pi"""
    try:
        with open('/proc/cpuinfo', 'r') as f:
            if 'Raspberry Pi' in f.read():
                return True
    except:
        pass
    return False

def check_camera():
    """Check if camera is available"""
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            ret, frame = cap.read()
            cap.release()
            if ret:
                return True
    except:
        pass
    return False

def check_gpio_permissions():
    """Check if GPIO permissions are set up"""
    try:
        import RPi.GPIO as GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        # Test a pin
        GPIO.setup(18, GPIO.OUT)
        GPIO.cleanup()
        return True
    except:
        return False

def setup_gpio_permissions():
    """Setup GPIO permissions"""
    print("🔧 Setting up GPIO permissions...")
    try:
        # Add user to gpio group
        subprocess.run(['sudo', 'usermod', '-a', '-G', 'gpio', os.getenv('USER')], check=True)
        print("✅ User added to gpio group")
        
        # Create udev rules
        udev_rules = '''SUBSYSTEM=="bcm2835-gpiomem", GROUP="gpio", MODE="0660"
SUBSYSTEM=="gpio", GROUP="gpio", MODE="0660"
SUBSYSTEM=="gpio", KERNEL=="gpiochip*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys/class/gpio/export /sys/class/gpio/unexport ; chmod 220 /sys/class/gpio/export /sys/class/gpio/unexport'"
SUBSYSTEM=="gpio", KERNEL=="gpio*", ACTION=="add", PROGRAM="/bin/sh -c 'chown root:gpio /sys/%p/active_low /sys/%p/direction /sys/%p/edge /sys/%p/value ; chmod 660 /sys/%p/active_low /sys/%p/direction /sys/%p/edge /sys/%p/value'"
'''
        
        with open('/tmp/99-gpio.rules', 'w') as f:
            f.write(udev_rules)
        
        subprocess.run(['sudo', 'cp', '/tmp/99-gpio.rules', '/etc/udev/rules.d/'], check=True)
        subprocess.run(['sudo', 'udevadm', 'control', '--reload-rules'], check=True)
        subprocess.run(['sudo', 'udevadm', 'trigger'], check=True)
        
        print("✅ GPIO udev rules installed")
        print("⚠️  Please reboot your Raspberry Pi for GPIO permissions to take effect")
        return True
        
    except subprocess.CalledProcessError as e:
        print(f"❌ Failed to setup GPIO permissions: {e}")
        return False

def run_system_test():
    """Run the system test"""
    print("🧪 Running system test...")
    try:
        result = subprocess.run([sys.executable, 'test_system.py'], capture_output=True, text=True)
        print(result.stdout)
        if result.stderr:
            print("Errors:", result.stderr)
        return result.returncode == 0
    except Exception as e:
        print(f"❌ Failed to run system test: {e}")
        return False

def start_system():
    """Start the iTrash system"""
    print("🚀 Starting iTrash system...")
    print("Choose an option:")
    print("1. Run production system (main.py)")
    print("2. Run development system with manual controls (main_dev.py)")
    print("3. Run system test")
    print("4. Exit")
    
    while True:
        try:
            choice = input("\nEnter your choice (1-4): ").strip()
            
            if choice == '1':
                print("Starting production system...")
                subprocess.run([sys.executable, 'main.py'])
                break
            elif choice == '2':
                print("Starting development system...")
                subprocess.run([sys.executable, 'main_dev.py'])
                break
            elif choice == '3':
                run_system_test()
                break
            elif choice == '4':
                print("Goodbye!")
                break
            else:
                print("Invalid choice. Please enter 1-4.")
                
        except KeyboardInterrupt:
            print("\nGoodbye!")
            break
        except Exception as e:
            print(f"Error: {e}")

def main():
    """Main startup function"""
    print("🎯 iTrash Raspberry Pi Startup")
    print("=" * 40)
    
    # Check if running on Raspberry Pi
    if not check_raspberry_pi():
        print("⚠️  Warning: This script is designed for Raspberry Pi")
        print("   Some features may not work on other systems")
        response = input("Continue anyway? (y/N): ").strip().lower()
        if response != 'y':
            return
    
    # Check camera
    if not check_camera():
        print("⚠️  Camera not detected or not accessible")
        print("   Make sure camera is connected and enabled in raspi-config")
        response = input("Continue without camera? (y/N): ").strip().lower()
        if response != 'y':
            return
    
    # Check GPIO permissions
    if not check_gpio_permissions():
        print("⚠️  GPIO permissions not set up")
        response = input("Setup GPIO permissions? (Y/n): ").strip().lower()
        if response != 'n':
            if not setup_gpio_permissions():
                print("❌ Failed to setup GPIO permissions")
                print("   You may need to run with sudo or setup permissions manually")
                return
        else:
            print("⚠️  GPIO features may not work without proper permissions")
    
    # Start system
    print("\n✅ System ready!")
    start_system()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 Goodbye!")
    except Exception as e:
        print(f"💥 Startup failed: {e}")
        print("Please check the error and try again") 