# iTrash Unified System

The iTrash system has been unified into a single cohesive system that combines traditional hardware operation with modern API and MQTT capabilities.

## 🎯 **What You Get**

Running `python unified_main.py` gives you:

- ✅ **Hardware Loop** - Real-time sensor detection and LED control
- ✅ **FastAPI Server** - REST API for external control
- ✅ **MQTT Client** - Real-time messaging support
- ✅ **Display System** - Automatic image updates based on state
- ✅ **Shared State** - All components use the same state instance

## 🏗️ **Architecture**

```
┌─────────────────────────────────────────────────────────────┐
│                    Unified iTrash System                    │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐        │
│  │   FastAPI   │  │    MQTT     │  │   Display   │        │
│  │   Server    │  │   Client    │  │   Manager   │        │
│  └─────────────┘  └─────────────┘  └─────────────┘        │
│         │               │               │                  │
│         └───────────────┼───────────────┘                  │
│                         │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Global State Manager                   │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │ Phase   │ │ Sensors │ │ Reward  │ │ System  │   │   │
│  │  │         │ │ Status  │ │ Status  │ │ Status  │   │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
│                         │                                  │
│  ┌─────────────────────────────────────────────────────┐   │
│  │              Background Hardware Loop               │   │
│  │  ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐   │   │
│  │  │ Object  │ │ Camera  │ │   AI    │ │   LED   │   │   │
│  │  │Detection│ │ Capture │ │Classifier│ │ Control │   │   │
│  │  └─────────┘ └─────────┘ └─────────┘ └─────────┘   │   │
│  └─────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 **Quick Start**

### **1. Start the Unified System**
```bash
python unified_main.py
```

### **2. What Happens**
```
Starting unified iTrash system...
Display manager started
Hardware loop started
MQTT client started
Unified iTrash system started successfully
✅ Hardware loop running in background
✅ FastAPI server available at http://localhost:8000
✅ MQTT client listening for messages
✅ Display system monitoring state changes
```

### **3. Test the System**
```bash
python test_unified.py
```

## 📡 **API Endpoints**

All endpoints are available at `http://localhost:8000/api/v1/`

### **System Control**
- `GET /status` - Get current system status
- `POST /reset` - Reset system state

### **Hardware Control**
- `POST /hardware/led/{color}` - Set LED color (red/green/blue/yellow/white/off)
- `GET /hardware/sensors` - Get sensor status

### **Sensor Simulation**
- `POST /sensor/object-detected` - Trigger object detection
- `POST /sensor/{bin_type}` - Trigger bin sensor (blue/yellow/brown)

### **Image Processing**
- `POST /classify` - Classify uploaded image
- `POST /capture` - Capture image from camera

### **Process Control**
- `POST /process/complete` - Complete processing cycle

## 🔄 **State Flow**

The system automatically transitions through these phases:

1. **`idle`** - Waiting for objects
2. **`processing`** - AI analyzing image
3. **`user_confirmation`** - Waiting for user to throw in correct bin
4. **`reward`** - Success! (auto-resets after 2 seconds)
5. **`incorrect`** - Wrong bin (auto-resets after 2 seconds)
6. **`error`** - Something went wrong

## 🎮 **Control Methods**

### **Method 1: Hardware Sensors (Automatic)**
- Place object near sensor → automatic detection
- Throw in correct bin → automatic reward
- System runs completely autonomously

### **Method 2: REST API (Manual Control)**
```bash
# Trigger object detection
curl -X POST http://localhost:8000/api/v1/sensor/object-detected

# Set LED color
curl -X POST http://localhost:8000/api/v1/hardware/led/red

# Check status
curl http://localhost:8000/api/v1/status
```

### **Method 3: MQTT Messages (Real-time)**
```bash
# Start system
mosquitto_pub -h localhost -t "itrash/start" -m "start"

# Trigger object detection
mosquitto_pub -h localhost -t "itrash/sensor/object" -m "detected"

# Trigger bin detection
mosquitto_pub -h localhost -t "itrash/sensor/blue" -m "detected"
```

### **Method 4: Python Client**
```python
from api_client import iTrashAPIClient

client = iTrashAPIClient()
status = client.get_status()
client.trigger_object_sensor()
client.set_led_color("green")
```

## 🖥️ **Display System**

The display automatically updates based on system state:

- **State 0** (`idle`) → `white.png`
- **State 1** (`processing`) → `processing_new.png`
- **State 2** (`show_trash`) → `show_trash.png`
- **State 3** (`user_confirmation`) → `try_again_green.png`
- **State 4** (`reward`) → `great_job.png`
- **State 5** (`timeout`) → `timeout_new.png`
- **State 6** (`error`) → `incorrect_new.png`

Images are copied to `/tmp/itrash_current.png` for easy display.

## 🔧 **Configuration**

### **Hardware Settings** (`config/settings.py`)
```python
class HardwareConfig:
    LED_COUNT = 60
    LED_PIN = 18
    DETECT_OBJECT_SENSOR_PIN = 26
    BLUE_PROXIMITY_PIN = 19
    YELLOW_PROXIMITY_PIN = 13
    BROWN_PROXIMITY_PIN = 6
```

### **Timing Settings**
```python
class TimingConfig:
    OBJECT_DETECTION_DELAY = 4  # seconds
    USER_CONFIRMATION_TIMEOUT = 30  # seconds
```

## 🧪 **Testing**

### **Automated Test**
```bash
python test_unified.py
```

### **Manual Testing**
1. Start system: `python unified_main.py`
2. Open browser: `http://localhost:8000/docs`
3. Test endpoints interactively
4. Monitor state changes in real-time

### **Hardware Testing**
1. Place object near sensor
2. Watch LED colors change
3. Throw in correct bin
4. See reward animation

## 🔍 **Monitoring**

### **Real-time Status**
```bash
# Monitor state changes
watch -n 0.5 'curl -s http://localhost:8000/api/v1/status | jq .phase'
```

### **Logs**
The system provides detailed logging:
- Hardware loop events
- API requests
- MQTT messages
- State transitions

## 🚨 **Troubleshooting**

### **Common Issues**

1. **Hardware Not Available**
   ```
   Error initializing hardware: [Errno 13] Permission denied
   ```
   - Run with sudo or add user to gpio group
   - Check hardware connections

2. **MQTT Connection Failed**
   ```
   Failed to start MQTT client: Connection refused
   ```
   - Install and start MQTT broker: `sudo systemctl start mosquitto`
   - Or ignore - system works without MQTT

3. **Camera Not Available**
   ```
   Warning: Camera initialization failed
   ```
   - Check camera connection
   - Install camera drivers
   - System works without camera (API mode only)

### **Debug Mode**
```python
# Add to unified_main.py for more verbose logging
import logging
logging.basicConfig(level=logging.DEBUG)
```

## 🔄 **Migration from Old System**

The unified system is **100% backward compatible**:

- **Traditional mode** still works: `python main.py --mode traditional`
- **API mode** still works: `python main.py --mode api`
- **New unified mode**: `python unified_main.py`

## 🎯 **Benefits**

1. **Single Command** - Everything starts with one command
2. **Real-time Operation** - Hardware sensors work automatically
3. **API Control** - External systems can control via REST
4. **MQTT Integration** - IoT devices can send commands
5. **Shared State** - All components stay synchronized
6. **Auto-reset** - System automatically returns to idle
7. **Graceful Degradation** - Works without hardware/MQTT

## 🚀 **Next Steps**

- Add WebSocket support for real-time updates
- Implement database logging
- Add mobile app integration
- Create web dashboard
- Add machine learning model updates via API

The unified system gives you the best of both worlds: autonomous hardware operation AND modern API control! 