# iTrash System Logging Documentation

## Overview

The iTrash system now includes comprehensive logging functionality that tracks all system events, including images taken, GPT responses, sensor triggers, and other important operations. This logging system provides detailed insights into system behavior and helps with debugging and monitoring.

## Features

### 🔍 Comprehensive Event Tracking
- **System Events**: Startup, shutdown, initialization
- **Camera Operations**: Image capture, encoding, saving
- **AI Classification**: YOLO predictions, GPT responses, confidence scores
- **Sensor Triggers**: Manual keyboard inputs, bin detection
- **Hardware Operations**: LED animations, color changes
- **User Interactions**: Confirmation events, timeouts
- **Error Handling**: Exceptions, failures, timeouts

### 📁 Multiple Log Outputs
- **Console Output**: Real-time logging to terminal
- **System Log File**: `logs/itrash_system_YYYYMMDD_HHMMSS.log`
- **Events Log File**: `logs/events_YYYYMMDD_HHMMSS.log`
- **JSON Format**: Structured event data for easy parsing

### ⏰ Timestamped Events
All events include precise timestamps in ISO format for accurate tracking and analysis.

## Log File Structure

### System Log (`itrash_system_*.log`)
Contains standard logging output with different levels:
- **INFO**: General system information
- **WARNING**: Non-critical issues
- **ERROR**: Critical errors and failures
- **DEBUG**: Detailed debugging information

### Events Log (`events_*.log`)
Contains structured JSON events with detailed information:
```json
{
  "timestamp": "2024-01-15T10:30:45.123456",
  "event_type": "image_captured",
  "details": {
    "frame_shape": [1080, 1920, 3],
    "timestamp": "2024-01-15T10:30:45.123456"
  },
  "data": null
}
```

## Logged Events

### System Events
- `system_start` - System initialization
- `system_stop` - System shutdown
- `system_initialized` - All components ready
- `component_initialized` - Individual component ready

### Camera Events
- `camera_initialized` - Camera setup complete
- `image_captured` - Image successfully captured
- `image_capture_failed` - Image capture failure
- `image_encoded` - Image converted to base64
- `image_saved` - Image saved to file

### AI Classification Events
- `classification_started` - AI processing begins
- `yolo_prediction` - YOLO model results
- `gpt_response_received` - GPT API response
- `classification_success` - Successful classification
- `classification_failed` - Classification failure

### Sensor Events
- `object_detected` - Main object detection
- `bin_detected` - Bin proximity detection
- `user_confirmation_started` - Waiting for user input
- `user_confirmation_success` - User confirmed correctly
- `user_confirmation_failed` - User failed or timed out

### Hardware Events
- `led_color_set` - LED color changes
- `leds_cleared` - LEDs turned off
- `animation_shown` - LED animations
- `hardware_initialized` - Hardware setup

### Error Events
- `processing_error` - General processing errors
- `camera_error` - Camera-related errors
- `classification_error` - AI classification errors
- `hardware_error` - Hardware-related errors

## Usage

### Running with Logging
```bash
python main_dev.py
```

The system will automatically:
1. Create a `logs/` directory
2. Generate timestamped log files
3. Output logs to both console and files
4. Track all system events

### Testing Logging
```bash
python test_logging.py
```

This will demonstrate the logging functionality and show sample log outputs.

### Monitoring Logs
```bash
# Watch system logs in real-time
tail -f logs/itrash_system_*.log

# Watch event logs in real-time
tail -f logs/events_*.log

# Search for specific events
grep "image_captured" logs/events_*.log

# Count events by type
grep -o '"event_type":"[^"]*"' logs/events_*.log | sort | uniq -c
```

## Log Analysis

### Example Log Analysis Script
```python
import json
import glob
from collections import Counter

# Load all event logs
events = []
for log_file in glob.glob('logs/events_*.log'):
    with open(log_file, 'r') as f:
        for line in f:
            try:
                event = json.loads(line.split(' - ')[-1])
                events.append(event)
            except:
                continue

# Analyze event types
event_types = Counter([e['event_type'] for e in events])
print("Event Type Counts:")
for event_type, count in event_types.most_common():
    print(f"  {event_type}: {count}")

# Find classification results
classifications = [e for e in events if e['event_type'] == 'classification_success']
print(f"\nSuccessful Classifications: {len(classifications)}")

# Find errors
errors = [e for e in events if 'error' in e['event_type']]
print(f"Errors: {len(errors)}")
```

## Configuration

### Log Level Control
The logging level can be adjusted in `main_dev.py`:
```python
logging.basicConfig(
    level=logging.INFO,  # Change to logging.DEBUG for more detail
    # ... other settings
)
```

### Log File Retention
Log files are automatically created with timestamps. You can implement log rotation by:
1. Monitoring log file sizes
2. Archiving old logs
3. Deleting logs older than a certain age

### Custom Event Logging
Add custom events in your code:
```python
# In any component with access to self.logger
self.log_event("custom_event", {
    "custom_data": "value",
    "additional_info": "details"
})
```

## Troubleshooting

### Common Issues

1. **No logs directory created**
   - Check file permissions
   - Ensure the script has write access to the current directory

2. **Empty log files**
   - Verify the system is actually running
   - Check for errors in console output

3. **Missing events**
   - Ensure logging is properly initialized
   - Check that components are calling log_event()

### Debug Mode
Enable debug logging for more detailed information:
```python
# In main_dev.py, change logging level to DEBUG
logging.basicConfig(level=logging.DEBUG)
```

## Performance Considerations

- Log files can grow large over time
- Consider implementing log rotation
- Monitor disk space usage
- JSON parsing adds minimal overhead
- Logging is asynchronous and doesn't block main operations

## Integration with Monitoring

The structured JSON logs can be easily integrated with:
- **Log aggregation systems** (ELK Stack, Splunk)
- **Monitoring dashboards** (Grafana, Kibana)
- **Alert systems** (for error events)
- **Analytics platforms** (for usage statistics)

## Future Enhancements

Potential improvements to the logging system:
- **Log compression** for long-term storage
- **Remote logging** to external systems
- **Log filtering** by event type or severity
- **Performance metrics** logging
- **User behavior analytics**
- **Predictive maintenance** based on error patterns 