#!/usr/bin/env python3
"""
Test script to demonstrate the comprehensive logging functionality
of the iTrash system.
"""

import os
import sys
import time
import logging
from datetime import datetime

# Add the project root to the Python path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from main_dev import iTrashSystemDev

def test_logging_functionality():
    """Test the logging functionality of the iTrash system"""
    print("🧪 Testing iTrash Logging Functionality")
    print("=" * 50)
    
    # Create and initialize the system
    print("1. Initializing iTrash system...")
    system = iTrashSystemDev()
    
    # Check if logs directory was created
    if os.path.exists('logs'):
        print("✅ Logs directory created successfully")
        log_files = os.listdir('logs')
        print(f"📁 Log files found: {log_files}")
        
        # Show log file contents
        for log_file in log_files:
            if log_file.endswith('.log'):
                print(f"\n📄 Contents of {log_file}:")
                print("-" * 30)
                try:
                    with open(os.path.join('logs', log_file), 'r') as f:
                        lines = f.readlines()
                        # Show first 10 lines
                        for i, line in enumerate(lines[:10]):
                            print(f"{i+1:2d}: {line.strip()}")
                        if len(lines) > 10:
                            print(f"... and {len(lines) - 10} more lines")
                except Exception as e:
                    print(f"Error reading log file: {e}")
    else:
        print("❌ Logs directory not found")
    
    print("\n2. Testing event logging...")
    
    # Test various events
    events_to_test = [
        ("test_event", {"message": "This is a test event"}),
        ("sensor_trigger", {"sensor_type": "proximity", "value": True}),
        ("image_capture", {"resolution": "1920x1080", "format": "JPEG"}),
        ("classification_result", {"trash_class": "blue", "confidence": 0.95}),
        ("gpt_response", {"model": "gpt-4-vision", "tokens_used": 150}),
        ("error_event", {"error_type": "timeout", "details": "User confirmation timeout"})
    ]
    
    for event_type, details in events_to_test:
        system.log_event(event_type, details)
        print(f"✅ Logged event: {event_type}")
        time.sleep(0.1)  # Small delay to see timestamps
    
    print("\n3. Testing system shutdown...")
    system.stop()
    
    print("\n4. Final log summary:")
    if os.path.exists('logs'):
        log_files = os.listdir('logs')
        for log_file in log_files:
            if log_file.endswith('.log'):
                file_path = os.path.join('logs', log_file)
                file_size = os.path.getsize(file_path)
                print(f"📊 {log_file}: {file_size} bytes")
    
    print("\n🎉 Logging test completed!")
    print("\n📋 What was logged:")
    print("   • System initialization events")
    print("   • Component status (camera, hardware, classifier)")
    print("   • Test events with various data types")
    print("   • System shutdown events")
    print("\n📁 Check the 'logs/' directory for detailed log files:")
    print("   • itrash_system_YYYYMMDD_HHMMSS.log - Main system logs")
    print("   • events_YYYYMMDD_HHMMSS.log - Detailed event logs")

def show_logging_features():
    """Show the logging features that have been implemented"""
    print("\n🔍 Logging Features Implemented:")
    print("=" * 40)
    
    features = [
        "✅ Comprehensive event logging with timestamps",
        "✅ JSON-formatted event data for easy parsing",
        "✅ Separate log files for system logs and events",
        "✅ Logging for all major system components:",
        "   • Camera operations (capture, encode, save)",
        "   • AI classification (YOLO and GPT responses)",
        "   • Sensor triggers (manual keyboard inputs)",
        "   • Hardware operations (LED animations)",
        "   • System state changes",
        "   • Error handling and exceptions",
        "✅ Debug-level logging for detailed troubleshooting",
        "✅ Automatic log file rotation with timestamps",
        "✅ Console and file output simultaneously"
    ]
    
    for feature in features:
        print(f"  {feature}")
    
    print("\n📝 Logged Events Include:")
    events = [
        "system_start/system_stop",
        "component_initialization",
        "image_captured",
        "classification_success/failure",
        "gpt_response_received",
        "sensor_triggers",
        "user_confirmation_events",
        "hardware_animations",
        "error_conditions",
        "database_operations"
    ]
    
    for event in events:
        print(f"   • {event}")

if __name__ == "__main__":
    print("🚀 iTrash Logging System Test")
    print("=" * 50)
    
    show_logging_features()
    
    try:
        test_logging_functionality()
    except KeyboardInterrupt:
        print("\n⏹️  Test interrupted by user")
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        logging.error(f"Test failed: {e}")
    
    print("\n📚 Usage Instructions:")
    print("1. Run 'python main_dev.py' to start the system with logging")
    print("2. Check the 'logs/' directory for log files")
    print("3. Monitor console output for real-time logging")
    print("4. Use keyboard controls to trigger events and see them logged") 