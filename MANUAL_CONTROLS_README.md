# iTrash Raspberry Pi Manual Controls Guide

## Overview

This guide helps you set up and troubleshoot the iTrash system on Raspberry Pi, particularly focusing on manual controls for testing and development.

## Quick Start

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the startup script:**
   ```bash
   python start.py
   ```

3. **Test manual controls:**
   ```bash
   python test_manual_controls.py
   ```

## Manual Controls

The system includes manual controls that simulate proximity sensors using keyboard input:

### Keyboard Controls

- **'o'** - Trigger main object detection
- **'b'** - Trigger blue bin proximity sensor
- **'y'** - Trigger yellow bin proximity sensor  
- **'r'** - Trigger brown bin proximity sensor
- **'c'** - Clear all triggers
- **'q'** - Quit/exit
- **'f'** - Toggle fullscreen mode (display)
- **'r'** - Refresh display

### Testing Manual Controls

1. **Simple test:**
   ```bash
   python test_manual_controls.py
   ```

2. **Development system:**
   ```bash
   python main_dev.py
   ```

3. **Production system:**
   ```bash
   python main.py
   ```

## Troubleshooting

### Camera Issues

**Problem:** Camera doesn't open or shows black screen

**Solutions:**
1. Enable camera in raspi-config:
   ```bash
   sudo raspi-config
   # Navigate to Interface Options > Camera > Enable
   ```

2. Check camera permissions:
   ```bash
   ls -la /dev/video*
   ```

3. Test camera manually:
   ```bash
   python -c "import cv2; cap = cv2.VideoCapture(0); print('Camera opened:', cap.isOpened()); cap.release()"
   ```

4. Reboot after enabling camera:
   ```bash
   sudo reboot
   ```

### GPIO Issues

**Problem:** Permission denied or GPIO not working

**Solutions:**
1. Add user to gpio group:
   ```bash
   sudo usermod -a -G gpio $USER
   ```

2. Create udev rules:
   ```bash
   sudo nano /etc/udev/rules.d/99-gpio.rules
   ```
   
   Add this content:
   ```
   SUBSYSTEM=="bcm2835-gpiomem", GROUP="gpio", MODE="0660"
   SUBSYSTEM=="gpio", GROUP="gpio", MODE="0660"
   ```

3. Reload rules and reboot:
   ```bash
   sudo udevadm control --reload-rules
   sudo udevadm trigger
   sudo reboot
   ```

### LED Strip Issues

**Problem:** LED strip not lighting up

**Solutions:**
1. Check wiring connections
2. Verify power supply (5V, sufficient current)
3. Check GPIO pin configuration in `config/settings.py`
4. Test LED strip directly:
   ```bash
   python test_led_strip.py
   ```

### Display Issues

**Problem:** Display stuck on white screen or fullscreen issues

**Solutions:**
1. Press 'f' to toggle fullscreen mode
2. Press 'r' to refresh display
3. Click mouse to exit (if touchscreen)
4. Press 'q' to quit
5. Check if display images exist:
   ```bash
   ls display/images/
   ```

### Keyboard Input Issues

**Problem:** Keyboard controls not responding

**Solutions:**
1. Make sure you're in the correct terminal window
2. Check if pynput is installed:
   ```bash
   pip install pynput
   ```

3. Test keyboard input:
   ```bash
   python test_manual_controls.py
   ```

4. If running in fullscreen, try windowed mode first

### Dependencies Issues

**Problem:** Import errors or missing modules

**Solutions:**
1. Install all dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Install Raspberry Pi specific packages:
   ```bash
   pip install rpi_ws281x RPi.GPIO
   ```

3. Update pip:
   ```bash
   python -m pip install --upgrade pip
   ```

## System Test

Run the comprehensive system test to check all components:

```bash
python test_system.py
```

This will test:
- Module imports
- GPIO functionality
- LED strip
- Camera
- Manual controls
- Display
- Database
- Hardware controller

## Configuration

### Hardware Configuration

Edit `config/settings.py` to match your hardware setup:

```python
class HardwareConfig:
    # LED Strip
    LED_COUNT = 60          # Number of LEDs
    LED_PIN = 18            # GPIO pin for LED data
    
    # Proximity Sensors
    DETECT_OBJECT_SENSOR_PIN = 26
    BLUE_PROXIMITY_PIN = 19
    YELLOW_PROXIMITY_PIN = 13
    BROWN_PROXIMITY_PIN = 6
    
    # Camera
    CAMERA_INDEX = 0
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
```

### Display Configuration

```python
class DisplayConfig:
    WINDOW_WIDTH = 1600
    WINDOW_HEIGHT = 900
    FULLSCREEN = True       # Set to False for windowed mode
```

## Development vs Production

### Development Mode (`main_dev.py`)
- Uses manual keyboard controls
- Shows camera feed
- Better for testing and debugging
- No real hardware required

### Production Mode (`main.py`)
- Uses real GPIO sensors
- No camera feed display
- Requires proper hardware setup
- Optimized for actual deployment

## Common Commands

```bash
# Start with guided setup
python start.py

# Test specific components
python test_manual_controls.py
python test_led_strip.py
python test_system.py

# Run development system
python main_dev.py

# Run production system
python main.py

# Check system status
python -c "from core.database import db_manager; db_manager.connect(); print('ACC:', db_manager.get_acc_value())"
```

## Getting Help

If you encounter issues:

1. Run the system test first: `python test_system.py`
2. Check the troubleshooting section above
3. Verify your hardware connections
4. Ensure all dependencies are installed
5. Check the console output for error messages

## Hardware Requirements

- Raspberry Pi (3 or 4 recommended)
- Camera module
- WS2812B LED strip
- Proximity sensors (optional for manual mode)
- Power supply (5V, 3A+ recommended)
- Display (HDMI or touchscreen)

## Software Requirements

- Raspberry Pi OS (Bullseye or newer)
- Python 3.7+
- All packages listed in `requirements.txt` 