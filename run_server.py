"""
Unified server runner for iTrash system.
Combines FastAPI and MQTT in a single process.
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
from api.state import state

# Global variables for graceful shutdown
server = None
mqtt_client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan"""
    # Startup
    print("Starting iTrash API server...")
    
    # Initialize state
    state.update("system_status", "starting")
    
    # Start MQTT client
    global mqtt_client
    try:
        mqtt_client = start_mqtt()
        print("MQTT client started")
    except Exception as e:
        print(f"Failed to start MQTT client: {e}")
    
    # Update state
    state.update("system_status", "running")
    print("iTrash API server started successfully")
    
    yield
    
    # Shutdown
    print("Shutting down iTrash API server...")
    
    # Stop MQTT client
    if mqtt_client:
        stop_mqtt()
        print("MQTT client stopped")
    
    # Update state
    state.update("system_status", "stopped")
    print("iTrash API server stopped")

def create_app() -> FastAPI:
    """Create FastAPI application"""
    app = FastAPI(
        title="iTrash API",
        description="API for iTrash smart waste management system",
        version="1.0.0",
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