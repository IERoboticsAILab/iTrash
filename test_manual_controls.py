#!/usr/bin/env python3
"""
Simple manual controls test for iTrash system.
Tests keyboard input for proximity sensor simulation.
"""

import time
import sys
from core.manual_controls import ManualProximitySensors

def main():
    """Test manual proximity sensors"""
    print("🎮 Manual Controls Test")
    print("=" * 30)
    print("This test simulates proximity sensors using keyboard input.")
    print("Press the following keys to test:")
    print("  'o' - Trigger object detection")
    print("  'b' - Trigger blue bin")
    print("  'y' - Trigger yellow bin")
    print("  'r' - Trigger brown bin")
    print("  'c' - Clear all triggers")
    print("  'q' - Quit test")
    print("=" * 30)
    
    try:
        # Initialize manual proximity sensors
        sensors = ManualProximitySensors()
        print("✅ Manual proximity sensors initialized")
        
        # Test loop
        start_time = time.time()
        while time.time() - start_time < 60:  # Run for 60 seconds
            # Check for triggers
            if sensors.detect_object_proximity():
                print("🔍 Object detection triggered!")
            
            if sensors.detect_blue_bin():
                print("🔵 Blue bin triggered!")
            
            if sensors.detect_yellow_bin():
                print("🟡 Yellow bin triggered!")
            
            if sensors.detect_brown_bin():
                print("🟤 Brown bin triggered!")
            
            time.sleep(0.1)  # Small delay to prevent high CPU usage
        
        print("⏰ Test completed (60 seconds)")
        
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"❌ Test failed: {e}")
    finally:
        # Cleanup
        if 'sensors' in locals():
            sensors.cleanup()
        print("🧹 Cleanup completed")

if __name__ == "__main__":
    main() 