"""
Test script for unified iTrash system.
Tests the combined hardware loop, API, and MQTT functionality.
"""

import time
import requests
import json
from global_state import state

def test_unified_system():
    """Test the unified system"""
    print("=== Testing Unified iTrash System ===")
    
    # Test 1: Check if system is running
    print("\n1. Checking system status...")
    try:
        response = requests.get("http://localhost:8000/api/v1/status")
        if response.status_code == 200:
            status = response.json()
            print(f"✅ System is running: {status['system_status']}")
            print(f"   Current phase: {status['phase']}")
        else:
            print(f"❌ System not responding: {response.status_code}")
            return
    except Exception as e:
        print(f"❌ Cannot connect to system: {e}")
        return
    
    # Test 2: Test LED control
    print("\n2. Testing LED control...")
    for color in ["red", "green", "blue", "off"]:
        try:
            response = requests.post(f"http://localhost:8000/api/v1/hardware/led/{color}")
            if response.status_code == 200:
                print(f"✅ LED {color}: {response.json()}")
            else:
                print(f"❌ LED {color} failed: {response.status_code}")
        except Exception as e:
            print(f"❌ LED {color} error: {e}")
        time.sleep(0.5)
    
    # Test 3: Test sensor status
    print("\n3. Testing sensor status...")
    try:
        response = requests.get("http://localhost:8000/api/v1/hardware/sensors")
        if response.status_code == 200:
            sensors = response.json()
            print(f"✅ Sensors: {json.dumps(sensors, indent=2)}")
        else:
            print(f"❌ Sensor status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Sensor status error: {e}")
    
    # Test 4: Test object detection trigger
    print("\n4. Testing object detection trigger...")
    try:
        response = requests.post("http://localhost:8000/api/v1/sensor/object-detected")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Object detection: {result}")
            
            # Wait a moment and check state
            time.sleep(1)
            status_response = requests.get("http://localhost:8000/api/v1/status")
            if status_response.status_code == 200:
                new_status = status_response.json()
                print(f"   New phase: {new_status['phase']}")
        else:
            print(f"❌ Object detection failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Object detection error: {e}")
    
    # Test 5: Test bin sensor triggers
    print("\n5. Testing bin sensor triggers...")
    for bin_type in ["blue", "yellow", "brown"]:
        try:
            response = requests.post(f"http://localhost:8000/api/v1/sensor/{bin_type}")
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Bin {bin_type}: {result}")
            else:
                print(f"❌ Bin {bin_type} failed: {response.status_code}")
        except Exception as e:
            print(f"❌ Bin {bin_type} error: {e}")
        time.sleep(0.5)
    
    # Test 6: Test completion
    print("\n6. Testing completion...")
    try:
        response = requests.post("http://localhost:8000/api/v1/process/complete")
        if response.status_code == 200:
            result = response.json()
            print(f"✅ Completion: {result}")
        else:
            print(f"❌ Completion failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Completion error: {e}")
    
    # Test 7: Final status check
    print("\n7. Final status check...")
    try:
        response = requests.get("http://localhost:8000/api/v1/status")
        if response.status_code == 200:
            final_status = response.json()
            print(f"✅ Final status: {json.dumps(final_status, indent=2)}")
        else:
            print(f"❌ Final status failed: {response.status_code}")
    except Exception as e:
        print(f"❌ Final status error: {e}")
    
    print("\n=== Test Complete ===")

def test_state_monitoring():
    """Test state monitoring"""
    print("\n=== Testing State Monitoring ===")
    
    # Monitor state changes for 10 seconds
    print("Monitoring state changes for 10 seconds...")
    start_time = time.time()
    last_phase = None
    
    while time.time() - start_time < 10:
        current_phase = state.get("phase")
        if current_phase != last_phase:
            print(f"State change: {last_phase} -> {current_phase}")
            last_phase = current_phase
        time.sleep(0.5)
    
    print("State monitoring complete")

if __name__ == "__main__":
    # Wait a moment for system to start
    print("Waiting for system to start...")
    time.sleep(2)
    
    # Run tests
    test_unified_system()
    test_state_monitoring() 