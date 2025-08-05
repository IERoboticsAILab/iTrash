"""
Simplified iTrash system - core hardware loop and display functionality.
Single entry point for the streamlined system.
"""

import signal
import sys
import time
import threading

from global_state import state
from core.hardware_loop import start_hardware_loop, stop_hardware_loop
from display.media_display import DisplayManager

# Global variables for graceful shutdown
hardware_loop = None
display_manager = None
is_running = True

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global is_running
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    is_running = False

def main():
    """Main application entry point"""
    global hardware_loop, display_manager
    
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    print("Starting simplified iTrash system...")
    
    # Initialize state
    state.update("system_status", "starting")
    state.update("phase", "idle")  # Ensure initial phase is set
    
    # Start display manager first
    try:
        display_manager = DisplayManager()
        display_manager.start_display()
        print("✅ Display manager started")
    except Exception as e:
        print(f"❌ Failed to start display manager: {e}")
        return
    
    # Small delay to ensure display is ready
    time.sleep(0.2)
    
    # Start background hardware loop
    try:
        hardware_loop = start_hardware_loop()
        print("✅ Hardware loop started")
    except Exception as e:
        print(f"❌ Failed to start hardware loop: {e}")
        return
    
    # Update state
    state.update("system_status", "running")
    print("Simplified iTrash system started successfully")
    print("✅ Hardware loop running in background")
    print("✅ Display system monitoring state changes")
    print("✅ System ready for object detection")
    print("\nPress Ctrl+C to stop the system")
    
    # Main loop - keep the system running
    try:
        while is_running:
            time.sleep(1)
            
            # Optional: Print status every 30 seconds
            if int(time.time()) % 30 == 0:
                current_phase = state.get("phase", "unknown")
                print(f"System status: {current_phase}")
                
    except KeyboardInterrupt:
        print("\nSystem interrupted by user")
    except Exception as e:
        print(f"System error: {e}")
    finally:
        # Shutdown
        print("Shutting down simplified iTrash system...")
        
        # Stop display manager
        if display_manager:
            display_manager.stop_display()
            print("✅ Display manager stopped")
        
        # Stop hardware loop
        if hardware_loop:
            stop_hardware_loop()
            print("✅ Hardware loop stopped")
        
        # Update state
        state.update("system_status", "stopped")
        print("✅ Simplified iTrash system stopped")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("Application stopped by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1) 