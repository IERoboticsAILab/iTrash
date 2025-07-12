"""
FastAPI endpoints for iTrash system.
Provides REST API interface for system control and monitoring.
"""

import asyncio
import base64
import io
from typing import Optional
from fastapi import APIRouter, UploadFile, File, HTTPException, BackgroundTasks
from fastapi.responses import JSONResponse
from PIL import Image
import cv2
import numpy as np

from api.state import state
from core.ai_classifier import ClassificationManager
from core.camera import CameraController
from core.hardware import HardwareController

router = APIRouter()

# Initialize components (will be lazy-loaded)
_hardware: Optional[HardwareController] = None
_camera: Optional[CameraController] = None
_classifier: Optional[ClassificationManager] = None

def get_hardware() -> Optional[HardwareController]:
    """Get hardware controller instance"""
    global _hardware
    if _hardware is None:
        try:
            _hardware = HardwareController()
        except Exception as e:
            print(f"Hardware initialization failed: {e}")
    return _hardware

def get_camera() -> Optional[CameraController]:
    """Get camera controller instance"""
    global _camera
    if _camera is None:
        try:
            _camera = CameraController()
            if not _camera.initialize():
                _camera = None
        except Exception as e:
            print(f"Camera initialization failed: {e}")
    return _camera

def get_classifier() -> Optional[ClassificationManager]:
    """Get classifier instance"""
    global _classifier
    if _classifier is None:
        try:
            hardware = get_hardware()
            led_strip = hardware.get_led_strip() if hardware else None
            _classifier = ClassificationManager(led_strip)
        except Exception as e:
            print(f"Classifier initialization failed: {e}")
    return _classifier

@router.get("/")
async def root():
    """Root endpoint"""
    return {"message": "iTrash API", "version": "1.0.0"}

@router.get("/status")
async def get_status():
    """Get current system status"""
    return state.all()

@router.post("/reset")
async def reset_system():
    """Reset system state"""
    state.reset()
    return {"message": "System reset", "status": state.all()}

@router.post("/classify")
async def classify_image(file: UploadFile = File(...)):
    """Classify uploaded image"""
    try:
        # Read and validate image
        contents = await file.read()
        image = Image.open(io.BytesIO(contents))
        
        # Convert PIL to OpenCV format
        image_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Update state
        state.update("phase", "processing")
        
        # Get classifier and process
        classifier = get_classifier()
        if not classifier:
            raise HTTPException(status_code=500, detail="Classifier not available")
        
        # Classify image
        result = await classifier.process_image_with_feedback(image_cv)
        
        if result:
            state.update("last_classification", result)
            state.update("phase", "classified")
            return {
                "status": "classified",
                "result": result,
                "phase": "classified"
            }
        else:
            state.update("phase", "error")
            raise HTTPException(status_code=400, detail="Classification failed")
            
    except Exception as e:
        state.update("phase", "error")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/sensor/object-detected")
async def trigger_sensor():
    """Trigger object detection sensor"""
    state.update("phase", "processing")
    state.update_sensor_status("object_detected", True)
    
    # Simulate processing delay
    await asyncio.sleep(0.5)
    
    return {
        "status": "object detected",
        "phase": "processing",
        "sensor": "object_detected"
    }

@router.post("/sensor/{bin_type}")
async def trigger_bin_sensor(bin_type: str):
    """Trigger bin sensor (blue, yellow, brown)"""
    if bin_type not in ["blue", "yellow", "brown"]:
        raise HTTPException(status_code=400, detail="Invalid bin type")
    
    state.update_sensor_status(f"{bin_type}_bin", True)
    
    # Check if this matches the last classification
    last_class = state.get("last_classification")
    if last_class == bin_type:
        state.update("reward", True)
        state.update("phase", "reward")
        return {
            "status": "correct_bin",
            "bin_type": bin_type,
            "reward": True,
            "phase": "reward"
        }
    else:
        state.update("phase", "incorrect")
        return {
            "status": "incorrect_bin",
            "bin_type": bin_type,
            "expected": last_class,
            "phase": "incorrect"
        }

@router.post("/capture")
async def capture_image():
    """Capture image from camera"""
    camera = get_camera()
    if not camera:
        raise HTTPException(status_code=500, detail="Camera not available")
    
    try:
        frame = camera.capture_image()
        if frame is None:
            raise HTTPException(status_code=500, detail="Failed to capture image")
        
        # Convert to base64 for response
        _, buffer = cv2.imencode('.jpg', frame)
        image_base64 = base64.b64encode(buffer).decode('utf-8')
        
        state.update("current_image", image_base64)
        state.update("phase", "captured")
        
        return {
            "status": "captured",
            "image": image_base64,
            "phase": "captured"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/hardware/led/{color}")
async def set_led_color(color: str):
    """Set LED strip color"""
    hardware = get_hardware()
    if not hardware:
        raise HTTPException(status_code=500, detail="Hardware not available")
    
    try:
        led_strip = hardware.get_led_strip()
        
        # Color mapping
        color_map = {
            "red": (255, 0, 0),
            "green": (0, 255, 0),
            "blue": (0, 0, 255),
            "yellow": (255, 255, 0),
            "white": (255, 255, 255),
            "off": (0, 0, 0)
        }
        
        if color not in color_map:
            raise HTTPException(status_code=400, detail="Invalid color")
        
        led_strip.set_color_all(color_map[color])
        
        return {
            "status": "led_updated",
            "color": color
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/hardware/sensors")
async def get_sensor_status():
    """Get current sensor status"""
    hardware = get_hardware()
    if not hardware:
        raise HTTPException(status_code=500, detail="Hardware not available")
    
    try:
        sensors = hardware.get_proximity_sensors()
        
        return {
            "object_detected": sensors.detect_object_proximity(),
            "blue_bin": sensors.detect_blue_bin(),
            "yellow_bin": sensors.detect_yellow_bin(),
            "brown_bin": sensors.detect_brown_bin()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/process/complete")
async def complete_processing():
    """Complete processing cycle and reset to idle"""
    state.update("phase", "idle")
    state.update("reward", False)
    state.update("last_classification", None)
    
    # Clear LEDs
    hardware = get_hardware()
    if hardware:
        try:
            hardware.get_led_strip().clear_all()
        except:
            pass
    
    return {
        "status": "processing_complete",
        "phase": "idle"
    } 