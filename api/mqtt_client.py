"""
MQTT client for iTrash system.
Handles real-time messaging and sensor events.
"""

import json
import threading
import time
from typing import Optional, Callable
from api.state import state

# Try to import paho-mqtt, but don't fail if not available
try:
    import paho.mqtt.client as mqtt
    MQTT_AVAILABLE = True
except ImportError:
    MQTT_AVAILABLE = False
    print("Warning: paho-mqtt not available. MQTT functionality disabled.")

class MQTTClient:
    """MQTT client for iTrash system"""
    
    def __init__(self, broker_host: str = "localhost", broker_port: int = 1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client: Optional[mqtt.Client] = None
        self.is_connected = False
        self.is_running = False
        self.message_handlers: dict = {}
        
        if not MQTT_AVAILABLE:
            print("MQTT not available - using mock client")
            return
        
        self._setup_client()
    
    def _setup_client(self):
        """Setup MQTT client"""
        if not MQTT_AVAILABLE:
            return
            
        self.client = mqtt.Client()
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
    
    def _on_connect(self, client, userdata, flags, rc):
        """Callback when connected to MQTT broker"""
        print(f"Connected to MQTT broker with result code {rc}")
        self.is_connected = True
        
        # Subscribe to topics
        topics = [
            "itrash/start",
            "itrash/sensor/object",
            "itrash/sensor/blue",
            "itrash/sensor/yellow", 
            "itrash/sensor/brown",
            "itrash/classify",
            "itrash/status"
        ]
        
        for topic in topics:
            client.subscribe(topic)
            print(f"Subscribed to {topic}")
    
    def _on_message(self, client, userdata, msg):
        """Callback when message received"""
        try:
            topic = msg.topic
            payload = msg.payload.decode('utf-8')
            
            print(f"MQTT message: {topic} -> {payload}")
            
            # Handle different topics
            if topic == "itrash/start":
                self._handle_start()
            elif topic == "itrash/sensor/object":
                self._handle_object_detection()
            elif topic in ["itrash/sensor/blue", "itrash/sensor/yellow", "itrash/sensor/brown"]:
                bin_type = topic.split("/")[-1]
                self._handle_bin_detection(bin_type)
            elif topic == "itrash/classify":
                self._handle_classify_request(payload)
            elif topic == "itrash/status":
                self._handle_status_request()
            
            # Call custom handlers if registered
            if topic in self.message_handlers:
                self.message_handlers[topic](payload)
                
        except Exception as e:
            print(f"Error handling MQTT message: {e}")
    
    def _on_disconnect(self, client, userdata, rc):
        """Callback when disconnected from MQTT broker"""
        print(f"Disconnected from MQTT broker with result code {rc}")
        self.is_connected = False
    
    def _handle_start(self):
        """Handle start command"""
        state.update("phase", "processing")
        state.update("system_status", "running")
        print("System started via MQTT")
    
    def _handle_object_detection(self):
        """Handle object detection"""
        state.update("phase", "processing")
        state.update_sensor_status("object_detected", True)
        print("Object detected via MQTT")
    
    def _handle_bin_detection(self, bin_type: str):
        """Handle bin detection"""
        state.update_sensor_status(f"{bin_type}_bin", True)
        
        # Check if this matches the last classification
        last_class = state.get("last_classification")
        if last_class == bin_type:
            state.update("reward", True)
            state.update("phase", "reward")
            print(f"Correct bin detected: {bin_type}")
        else:
            state.update("phase", "incorrect")
            print(f"Incorrect bin detected: {bin_type}, expected: {last_class}")
    
    def _handle_classify_request(self, payload: str):
        """Handle classification request"""
        try:
            data = json.loads(payload)
            # This could trigger image capture and classification
            state.update("phase", "processing")
            print("Classification requested via MQTT")
        except json.JSONDecodeError:
            print("Invalid JSON in classify request")
    
    def _handle_status_request(self):
        """Handle status request"""
        # Publish current status
        status = state.all()
        self.publish("itrash/status/response", json.dumps(status))
    
    def connect(self) -> bool:
        """Connect to MQTT broker"""
        if not MQTT_AVAILABLE or not self.client:
            print("MQTT not available")
            return False
        
        try:
            self.client.connect(self.broker_host, self.broker_port, 60)
            return True
        except Exception as e:
            print(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from MQTT broker"""
        if self.client and self.is_connected:
            self.client.disconnect()
            self.is_connected = False
    
    def start(self):
        """Start MQTT client loop"""
        if not MQTT_AVAILABLE or not self.client:
            print("MQTT not available")
            return
        
        if not self.connect():
            return
        
        self.is_running = True
        self.client.loop_start()
        print("MQTT client started")
    
    def stop(self):
        """Stop MQTT client loop"""
        if not MQTT_AVAILABLE or not self.client:
            return
        
        self.is_running = False
        self.client.loop_stop()
        self.disconnect()
        print("MQTT client stopped")
    
    def publish(self, topic: str, payload: str):
        """Publish message to topic"""
        if not MQTT_AVAILABLE or not self.client or not self.is_connected:
            print("MQTT not available or not connected")
            return
        
        try:
            result = self.client.publish(topic, payload)
            if result.rc == mqtt.MQTT_ERR_SUCCESS:
                print(f"Published to {topic}: {payload}")
            else:
                print(f"Failed to publish to {topic}")
        except Exception as e:
            print(f"Error publishing to {topic}: {e}")
    
    def add_message_handler(self, topic: str, handler: Callable[[str], None]):
        """Add custom message handler for topic"""
        self.message_handlers[topic] = handler
    
    def publish_status(self):
        """Publish current system status"""
        status = state.all()
        self.publish("itrash/status", json.dumps(status))

# Global MQTT client instance
mqtt_client: Optional[MQTTClient] = None

def start_mqtt(broker_host: str = "localhost", broker_port: int = 1883):
    """Start MQTT client"""
    global mqtt_client
    mqtt_client = MQTTClient(broker_host, broker_port)
    mqtt_client.start()
    return mqtt_client

def stop_mqtt():
    """Stop MQTT client"""
    global mqtt_client
    if mqtt_client:
        mqtt_client.stop()
        mqtt_client = None

def get_mqtt_client() -> Optional[MQTTClient]:
    """Get MQTT client instance"""
    return mqtt_client 