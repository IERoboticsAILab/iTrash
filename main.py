"""
Simplified iTrash system - core hardware loop and display functionality.
Single entry point for the streamlined system.
"""

import signal
import sys
import time
import logging

from global_state import state
from core.hardware_loop import start_hardware_loop, stop_hardware_loop
from display.media_display import DisplayManager
from api.server import start_api_server


logger = logging.getLogger(__name__)

# Global variables for graceful shutdown
hardware_loop = None
display_manager = None
is_running = True

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    global is_running
    logger.info("Received signal %s, shutting down gracefully...", signum)
    is_running = False

def main():
    """Main application entry point"""
    global hardware_loop, display_manager
    
    # Configure root logging once (safe if called as script)
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
        datefmt="%H:%M:%S",
    )

    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    logger.info("Starting simplified iTrash system...")
    
    # Initialize state
    state.update("system_status", "starting")
    state.update("phase", "idle")  # Ensure initial phase is set
    
    # Start display manager first
    try:
        display_manager = DisplayManager()
        display_manager.start_display()
        logger.info("Display manager started")
    except Exception as e:
        logger.exception("Failed to start display manager: %s", e)
        return
    
    # Small delay to ensure display is ready
    time.sleep(0.2)
    
    # Start background hardware loop
    try:
        hardware_loop = start_hardware_loop()
        logger.info("Hardware loop started")
    except Exception as e:
        logger.exception("Failed to start hardware loop: %s", e)
        return

    # Start monitoring API (non-critical)
    try:
        api_thread = start_api_server()
        if api_thread is not None:
            logger.info("API server started. Endpoints: /classification, /disposal")
        else:
            logger.warning("API server not started. Check uvicorn installation and port availability.")
    except Exception as e:
        logger.warning("API server not started: %s", e)
    
    # Update state
    state.update("system_status", "running")
    logger.info("Simplified iTrash system started successfully")
    logger.info("Hardware loop running in background")
    logger.info("Display system monitoring state changes")
    logger.info("System ready for object detection")
    logger.info("Press Ctrl+C to stop the system")
    
    # Main loop - keep the system running and drive display rendering
    try:
        last_status = 0
        while is_running:
            # Drive display rendering from main thread for stability
            if display_manager and display_manager.display:
                try:
                    display_manager.display.tick()
                except Exception as e:
                    # Keep running even if a render error occurs
                    pass
            
            # Light-weight status every 10 seconds
            now = time.time()
            if now - last_status > 10:
                last_status = now
                current_phase = state.get("phase", "unknown")
                logger.info("System status: %s", current_phase)
            
            # Target ~50 FPS for smooth video/images without high CPU
            time.sleep(0.02)
                
    except KeyboardInterrupt:
        logger.info("System interrupted by user")
    except Exception as e:
        logger.exception("System error: %s", e)
    finally:
        # Shutdown
        logger.info("Shutting down simplified iTrash system...")
        
        # Stop display manager
        if display_manager:
            display_manager.stop_display()
            logger.info("Display manager stopped")
        
        # Stop hardware loop
        if hardware_loop:
            stop_hardware_loop()
            logger.info("Hardware loop stopped")
        
        # Update state
        state.update("system_status", "stopped")
        logger.info("Simplified iTrash system stopped")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.exception("Application error: %s", e)
        sys.exit(1)