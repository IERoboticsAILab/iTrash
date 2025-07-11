"""
Test script for manual controls module.
Tests keyboard triggers and camera feed display.
"""

import time
import sys
from core.camera import CameraController
from core.manual_controls import ManualProximitySensors, CameraFeedDisplay

def test_manual_proximity_sensors():
    """Test manual proximity sensors"""
    print("Testing manual proximity sensors...")
    print("Press the following keys to test:")
    print("  'o' - Trigger object detection")
    print("  'b' - Trigger blue bin")
    print("  'y' - Trigger yellow bin")
    print("  'r' - Trigger brown bin")
    print("  'c' - Clear all triggers")
    print("  'q' - Quit test")
    
    sensors = ManualProximitySensors()
    
    try:
        while True:
            # Test each sensor
            if sensors.detect_object_proximity():
                print("✅ Object detection sensor triggered")
            
            if sensors.detect_blue_bin():
                print("✅ Blue bin sensor triggered")
            
            if sensors.detect_yellow_bin():
                print("✅ Yellow bin sensor triggered")
            
            if sensors.detect_brown_bin():
                print("✅ Brown bin sensor triggered")
            
            time.sleep(0.1)
            
    except KeyboardInterrupt:
        print("\nTest interrupted by user")
    finally:
        sensors.cleanup()
        print("Manual proximity sensors test completed")

def test_camera_feed():
    """Test camera feed display"""
    print("Testing camera feed display...")
    
    # Initialize camera
    camera = CameraController()
    if not camera.initialize():
        print("❌ Failed to initialize camera")
        return
    
    print("✅ Camera initialized")
    
    # Create camera feed display
    feed_display = CameraFeedDisplay(camera)
    
    try:
        # Start camera feed
        feed_display.start_feed()
        
        # Keep running until user quits
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\nCamera feed test interrupted by user")
    finally:
        feed_display.stop_feed()
        camera.release()
        print("Camera feed test completed")

def main():
    """Main test function"""
    print("Manual Controls Test")
    print("===================")
    
    if len(sys.argv) > 1:
        test_type = sys.argv[1].lower()
        
        if test_type == "sensors":
            test_manual_proximity_sensors()
        elif test_type == "camera":
            test_camera_feed()
        else:
            print("Invalid test type. Use 'sensors' or 'camera'")
    else:
        print("Usage: python test_manual_controls.py [sensors|camera]")
        print("  sensors - Test manual proximity sensors")
        print("  camera  - Test camera feed display")

if __name__ == "__main__":
    main() 