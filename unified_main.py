"""
Unified iTrash system - combines hardware loop, FastAPI, and MQTT.
Single entry point for the complete hybrid system.
"""

import asyncio
import signal
import sys
import uvicorn
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from api.endpoints import router
from api.mqtt_client import start_mqtt, stop_mqtt
from core.hardware_loop import start_hardware_loop, stop_hardware_loop
from display.media_display import DisplayManager
from global_state import state

# Global variables for graceful shutdown
server = None
mqtt_client = None
hardware_loop = None
display_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    print("Starting unified iTrash system...")
    
    # Initialize state
    state.update("system_status", "starting")
    state.update("phase", "idle")  # Ensure initial phase is set
    
    # Start display manager first
    global display_manager
    try:
        display_manager = DisplayManager()
        display_manager.start_display()
        print("Display manager started")
    except Exception as e:
        print(f"Failed to start display manager: {e}")
    
    # Small delay to ensure display is ready
    import time
    time.sleep(0.2)
    
    # Start background hardware loop
    global hardware_loop
    try:
        hardware_loop = start_hardware_loop()
        print("Hardware loop started")
    except Exception as e:
        print(f"Failed to start hardware loop: {e}")
    
    # Start MQTT client
    global mqtt_client
    try:
        mqtt_client = start_mqtt()
        print("MQTT client started")
    except Exception as e:
        print(f"Failed to start MQTT client: {e}")
    
    # Update state
    state.update("system_status", "running")
    print("Unified iTrash system started successfully")
    print("✅ Hardware loop running in background")
    print("✅ FastAPI server available at http://localhost:8000")
    print("✅ MQTT client listening for messages")
    print("✅ Display system monitoring state changes")
    
    yield
    
    # Shutdown
    print("Shutting down unified iTrash system...")
    
    # Stop display manager
    if display_manager:
        display_manager.stop_display()
        print("Display manager stopped")
    
    # Stop hardware loop
    if hardware_loop:
        stop_hardware_loop()
        print("Hardware loop stopped")
    
    # Stop MQTT client
    if mqtt_client:
        stop_mqtt()
        print("MQTT client stopped")
    
    # Update state
    state.update("system_status", "stopped")
    print("Unified iTrash system stopped")

def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="iTrash Unified System",
        description="Unified iTrash system with hardware loop, API, and MQTT",
        version="2.0.0",
        lifespan=lifespan
    )
    
    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Include API routes
    app.include_router(router, prefix="/api/v1")
    
    return app

def signal_handler(signum, frame):
    """Handle shutdown signals"""
    print(f"\nReceived signal {signum}, shutting down gracefully...")
    sys.exit(0)

async def main():
    """Main application entry point"""
    # Set up signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Create FastAPI app
    app = create_app()
    
    # Configure uvicorn
    config = uvicorn.Config(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info",
        access_log=True
    )
    
    # Create and run server
    global server
    server = uvicorn.Server(config)
    
    try:
        await server.serve()
    except KeyboardInterrupt:
        print("Server interrupted by user")
    except Exception as e:
        print(f"Server error: {e}")
    finally:
        print("Server shutdown complete")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Application stopped by user")
    except Exception as e:
        print(f"Application error: {e}")
        sys.exit(1) 