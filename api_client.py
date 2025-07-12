"""
Simple API client for testing iTrash API endpoints.
"""

import requests
import json
import time
from typing import Optional

class iTrashAPIClient:
    """Simple client for iTrash API"""
    
    def __init__(self, base_url: str = "http://localhost:8000"):
        self.base_url = base_url
        self.api_url = f"{base_url}/api/v1"
    
    def get_status(self) -> dict:
        """Get system status"""
        response = requests.get(f"{self.api_url}/status")
        return response.json()
    
    def reset_system(self) -> dict:
        """Reset system state"""
        response = requests.post(f"{self.api_url}/reset")
        return response.json()
    
    def classify_image(self, image_path: str) -> dict:
        """Classify an image file"""
        with open(image_path, 'rb') as f:
            files = {'file': f}
            response = requests.post(f"{self.api_url}/classify", files=files)
        return response.json()
    
    def trigger_object_sensor(self) -> dict:
        """Trigger object detection sensor"""
        response = requests.post(f"{self.api_url}/sensor/object-detected")
        return response.json()
    
    def trigger_bin_sensor(self, bin_type: str) -> dict:
        """Trigger bin sensor"""
        response = requests.post(f"{self.api_url}/sensor/{bin_type}")
        return response.json()
    
    def capture_image(self) -> dict:
        """Capture image from camera"""
        response = requests.post(f"{self.api_url}/capture")
        return response.json()
    
    def set_led_color(self, color: str) -> dict:
        """Set LED strip color"""
        response = requests.post(f"{self.api_url}/hardware/led/{color}")
        return response.json()
    
    def get_sensor_status(self) -> dict:
        """Get sensor status"""
        response = requests.get(f"{self.api_url}/hardware/sensors")
        return response.json()
    
    def complete_processing(self) -> dict:
        """Complete processing cycle"""
        response = requests.post(f"{self.api_url}/process/complete")
        return response.json()

def test_api():
    """Test the API endpoints"""
    client = iTrashAPIClient()
    
    print("=== iTrash API Test ===")
    
    # Test status
    print("\n1. Getting status...")
    status = client.get_status()
    print(f"Status: {json.dumps(status, indent=2)}")
    
    # Test reset
    print("\n2. Resetting system...")
    reset = client.reset_system()
    print(f"Reset: {json.dumps(reset, indent=2)}")
    
    # Test LED control
    print("\n3. Testing LED control...")
    for color in ["red", "green", "blue", "off"]:
        result = client.set_led_color(color)
        print(f"LED {color}: {result}")
        time.sleep(1)
    
    # Test sensor status
    print("\n4. Getting sensor status...")
    sensors = client.get_sensor_status()
    print(f"Sensors: {json.dumps(sensors, indent=2)}")
    
    # Test object detection
    print("\n5. Triggering object detection...")
    object_detection = client.trigger_object_sensor()
    print(f"Object detection: {json.dumps(object_detection, indent=2)}")
    
    # Test bin sensors
    print("\n6. Testing bin sensors...")
    for bin_type in ["blue", "yellow", "brown"]:
        result = client.trigger_bin_sensor(bin_type)
        print(f"Bin {bin_type}: {result}")
        time.sleep(0.5)
    
    # Test completion
    print("\n7. Completing processing...")
    completion = client.complete_processing()
    print(f"Completion: {json.dumps(completion, indent=2)}")
    
    # Final status
    print("\n8. Final status...")
    final_status = client.get_status()
    print(f"Final status: {json.dumps(final_status, indent=2)}")
    
    print("\n=== Test Complete ===")

if __name__ == "__main__":
    test_api() 