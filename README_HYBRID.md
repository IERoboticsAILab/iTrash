# iTrash Hybrid System

The iTrash system has been refactored into a hybrid architecture that supports both traditional hardware operation and modern API-based control.

## Architecture Overview

The new system consists of:

- **Local State Manager** (`api/state.py`) - Replaces MongoDB with in-memory state
- **FastAPI Endpoints** (`api/endpoints.py`) - REST API for external control
- **MQTT Client** (`api/mqtt_client.py`) - Real-time messaging support
- **Unified Server** (`run_server.py`) - Combines FastAPI + MQTT
- **Modified Core** - Updated to work with both traditional and API modes

## Running Modes

### 1. Traditional Mode (Hardware Loop)

Run the system in the original hardware-based mode:

```bash
python main.py --mode traditional
```

This runs the original hardware detection loop with local state management.

### 2. API Mode (FastAPI Server)

Run the system as an API server:

```bash
python main.py --mode api --port 8000
```

Or use the dedicated server runner:

```bash
python run_server.py
```

## API Endpoints

### System Status
- `GET /api/v1/status` - Get current system status
- `POST /api/v1/reset` - Reset system state

### Image Classification
- `POST /api/v1/classify` - Classify uploaded image
- `POST /api/v1/capture` - Capture image from camera

### Sensor Control
- `POST /api/v1/sensor/object-detected` - Trigger object detection
- `POST /api/v1/sensor/{bin_type}` - Trigger bin sensor (blue/yellow/brown)
- `GET /api/v1/hardware/sensors` - Get sensor status

### Hardware Control
- `POST /api/v1/hardware/led/{color}` - Set LED color
- `POST /api/v1/process/complete` - Complete processing cycle

## MQTT Topics

The system subscribes to these MQTT topics:

- `itrash/start` - Start system
- `itrash/sensor/object` - Object detection
- `itrash/sensor/blue` - Blue bin detection
- `itrash/sensor/yellow` - Yellow bin detection
- `itrash/sensor/brown` - Brown bin detection
- `itrash/classify` - Classification request
- `itrash/status` - Status request

## State Management

The system uses a local state manager with these key fields:

```python
{
    "phase": "idle|processing|classified|user_confirmation|reward|timeout|error",
    "last_classification": "blue|yellow|brown|null",
    "reward": true|false,
    "system_status": "ready|running|stopped",
    "sensor_status": {
        "object_detected": false,
        "blue_bin": false,
        "yellow_bin": false,
        "brown_bin": false
    }
}
```

## Testing

### API Testing

Use the provided test client:

```bash
python api_client.py
```

### Manual Testing

1. Start the API server:
   ```bash
   python run_server.py
   ```

2. Test endpoints with curl:
   ```bash
   # Get status
   curl http://localhost:8000/api/v1/status
   
   # Trigger object detection
   curl -X POST http://localhost:8000/api/v1/sensor/object-detected
   
   # Set LED color
   curl -X POST http://localhost:8000/api/v1/hardware/led/red
   ```

### MQTT Testing

Use an MQTT client to publish messages:

```bash
# Install mosquitto-clients
sudo apt-get install mosquitto-clients

# Publish start command
mosquitto_pub -h localhost -t "itrash/start" -m "start"

# Publish sensor event
mosquitto_pub -h localhost -t "itrash/sensor/object" -m "detected"
```

## Configuration

### Dependencies

The new system requires additional dependencies:

```bash
pip install fastapi uvicorn[standard] paho-mqtt python-multipart
```

### Environment Variables

Create a `.env` file based on `env.template`:

```bash
cp env.template .env
```

## Integration Examples

### Web Interface

Create a simple web interface to control the system:

```html
<!DOCTYPE html>
<html>
<head>
    <title>iTrash Control</title>
</head>
<body>
    <h1>iTrash Control Panel</h1>
    <button onclick="triggerObject()">Trigger Object Detection</button>
    <button onclick="setLED('red')">Red LED</button>
    <button onclick="setLED('green')">Green LED</button>
    <button onclick="setLED('blue')">Blue LED</button>
    <button onclick="setLED('off')">Off</button>
    
    <script>
        async function triggerObject() {
            await fetch('/api/v1/sensor/object-detected', {method: 'POST'});
        }
        
        async function setLED(color) {
            await fetch(`/api/v1/hardware/led/${color}`, {method: 'POST'});
        }
    </script>
</body>
</html>
```

### Python Integration

```python
from api_client import iTrashAPIClient

# Create client
client = iTrashAPIClient("http://localhost:8000")

# Get status
status = client.get_status()
print(f"Current phase: {status['phase']}")

# Trigger object detection
result = client.trigger_object_sensor()
print(f"Object detected: {result}")

# Set LED color
client.set_led_color("green")
```

## Migration from Old System

The refactoring maintains backward compatibility:

1. **Traditional mode** works exactly like before
2. **Database operations** are replaced with local state
3. **Hardware control** remains the same
4. **Display system** updated to use local state

## Troubleshooting

### Common Issues

1. **MQTT Connection Failed**
   - Ensure MQTT broker is running: `sudo systemctl start mosquitto`
   - Check broker configuration in `/etc/mosquitto/mosquitto.conf`

2. **Hardware Not Available**
   - Check GPIO permissions
   - Verify hardware connections
   - Run with `--mode api` to test without hardware

3. **API Server Won't Start**
   - Check port availability
   - Verify dependencies are installed
   - Check firewall settings

### Logs

The system provides detailed logging:

```bash
# Traditional mode logs
python main.py --mode traditional

# API mode logs
python run_server.py
```

## Future Enhancements

- WebSocket support for real-time updates
- Database integration for analytics
- Mobile app integration
- Cloud-based monitoring
- Machine learning model updates via API 