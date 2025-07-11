# Manual Controls for iTrash Development

This document explains how to use the manual controls for testing the iTrash system without physical proximity sensors.

## Overview

The manual controls module provides keyboard-based triggers to simulate proximity sensors and a continuous camera feed display for development and testing purposes.

## Features

- **Keyboard Triggers**: Simulate proximity sensor events using keyboard keys
- **Continuous Camera Feed**: Real-time camera display with overlay information
- **LED Strip Control**: Full LED strip functionality for visual feedback
- **Development Mode**: Complete system testing without physical hardware

## Installation

1. Install the required dependencies:
```bash
pip install -r requirements.txt
```

2. Make sure you have a camera connected to your system.

## Usage

### Running the Development System

To run the complete iTrash system with manual controls:

```bash
python main_dev.py
```

This will start:
- Continuous camera feed display
- Manual proximity sensor controls
- LED strip feedback
- AI classification system
- Display manager

### Testing Individual Components

#### Test Manual Proximity Sensors Only

```bash
python test_manual_controls.py sensors
```

This will start a simple test that only tests the keyboard triggers for proximity sensors.

#### Test Camera Feed Only

```bash
python test_manual_controls.py camera
```

This will start a simple test that only shows the camera feed with overlay information.

## Keyboard Controls

### Proximity Sensor Triggers

| Key | Function | Description |
|-----|----------|-------------|
| `o` | Object Detection | Triggers the main object detection sensor |
| `b` | Blue Bin | Triggers the blue bin proximity sensor |
| `y` | Yellow Bin | Triggers the yellow bin proximity sensor |
| `r` | Brown Bin | Triggers the brown bin proximity sensor |
| `c` | Clear All | Clears all active triggers |

### Camera Feed Controls

| Key | Function | Description |
|-----|----------|-------------|
| `q` | Quit | Closes the camera feed window |

## System Workflow

1. **Start the system**: Run `python main_dev.py`
2. **Camera feed appears**: You'll see a window with the camera feed and instructions
3. **Trigger object detection**: Press `o` to simulate an object being placed in front of the sensor
4. **System processes**: The system will capture an image and classify the trash
5. **LED feedback**: LEDs will show the appropriate color for the classified trash type
6. **User confirmation**: Press the appropriate bin key (`b`, `y`, or `r`) to confirm the classification
7. **Success/Error feedback**: LEDs will show success or error animations

## Development Workflow

### Testing the Complete System

1. Start the development system
2. Press `o` to trigger object detection
3. Wait for AI classification
4. Press the correct bin key to confirm
5. Observe LED animations and system state changes

### Testing Individual Sensors

1. Start the sensor test: `python test_manual_controls.py sensors`
2. Press different keys to test each sensor
3. Observe console output for trigger confirmations

### Testing Camera Feed

1. Start the camera test: `python test_manual_controls.py camera`
2. Observe the camera feed with overlay information
3. Press `q` to quit

## Troubleshooting

### Camera Not Working

- Make sure your camera is connected and accessible
- Check if other applications are using the camera
- Try different camera indices in `config/settings.py`

### Keyboard Not Responding

- Make sure the terminal window has focus
- Check if you have permission to capture keyboard events
- On some systems, you may need to run with sudo for keyboard capture

### LED Strip Not Working

- Make sure you're running on a Raspberry Pi with the LED strip connected
- Check GPIO pin configurations in `config/settings.py`
- Ensure you have the required permissions for GPIO access

## Configuration

You can modify the keyboard mappings in `core/manual_controls.py`:

```python
self.key_mapping = {
    'o': 'object_detection',      # Change 'o' to any key
    'b': 'blue_bin',              # Change 'b' to any key
    'y': 'yellow_bin',            # Change 'y' to any key
    'r': 'brown_bin',             # Change 'r' to any key
    'c': 'clear_all'              # Change 'c' to any key
}
```

## Integration with Production System

The manual controls are designed to be a drop-in replacement for the physical proximity sensors. To switch between development and production modes:

- **Development**: Use `main_dev.py` with `ManualHardwareController`
- **Production**: Use `main.py` with `HardwareController`

Both systems use the same interface, so your application logic remains unchanged.

## File Structure

```
core/
├── manual_controls.py          # Manual controls implementation
├── hardware.py                 # Physical hardware controller
├── camera.py                   # Camera controller
└── ...

main_dev.py                     # Development system entry point
main.py                         # Production system entry point
test_manual_controls.py         # Manual controls test script
```

## Notes

- The manual controls are designed for development and testing only
- Keyboard events are captured globally, so make sure the terminal has focus
- The camera feed runs in a separate thread to avoid blocking the main system
- All sensor triggers are automatically reset after detection to prevent multiple triggers 