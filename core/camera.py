"""
Camera module for iTrash system.
Handles video capture, image processing, and QR code detection.
"""

import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
import logging
from typing import Optional, Tuple
from config.settings import HardwareConfig
import os
from datetime import datetime

logger = logging.getLogger(__name__)

class CameraController:
    """Camera controller for video capture and image processing"""
    
    def __init__(self, camera_index=HardwareConfig.CAMERA_INDEX):
        self.camera_index = camera_index
        self.cap = None
        self.is_initialized = False
    
    def initialize(self) -> bool:
        """Initialize the camera"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                logger.error("Could not open camera at index %s", self.camera_index)
                return False
            
            # Set camera properties for Raspberry Pi
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, HardwareConfig.FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HardwareConfig.FRAME_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, HardwareConfig.CAMERA_FPS)
            self.cap.set(cv2.CAP_PROP_BUFFERSIZE, HardwareConfig.CAMERA_BUFFER_SIZE)
            
            # Additional Raspberry Pi camera optimizations
            self.cap.set(cv2.CAP_PROP_FOURCC, cv2.VideoWriter_fourcc('M', 'J', 'P', 'G'))
            
            # Test camera by reading a frame
            ret, test_frame = self.cap.read()
            if not ret:
                logger.error("Could not read test frame from camera")
                return False
            
            self.is_initialized = True
            logger.info("Camera initialized successfully")
            logger.info("Camera resolution: %sx%s", HardwareConfig.FRAME_WIDTH, HardwareConfig.FRAME_HEIGHT)
            logger.info("Camera FPS: %s", HardwareConfig.CAMERA_FPS)
            return True
            
        except Exception as e:
            logger.exception("Error initializing camera: %s", e)
            return False
    
    def read_frame(self) -> Tuple[Optional[bool], Optional[np.ndarray]]:
        """Read a frame from the camera"""
        if not self.is_initialized or self.cap is None:
            return None, None
        
        ret, frame = self.cap.read()
        if not ret:
            logger.error("Error reading frame from camera")
            return None, None
        
        return ret, frame
    
    def capture_image(self) -> Optional[np.ndarray]:
        """Capture a single image from the camera"""
        ret, frame = self.read_frame()
        if ret:
            # Save image to disk
            try:
                save_dir = HardwareConfig.IMAGE_SAVE_DIR
                os.makedirs(save_dir, exist_ok=True)
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
                filename = f"frame_{timestamp}.{HardwareConfig.IMAGE_FORMAT}"
                path = os.path.join(save_dir, filename)
                # Encode and save using OpenCV
                if HardwareConfig.IMAGE_FORMAT.lower() == "png":
                    cv2.imwrite(path, frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 3])
                else:
                    cv2.imwrite(path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
                logger.info("Saved captured image: %s", path)
            except Exception as e:
                logger.warning("Could not save captured image: %s", e)
            return frame
        return None
    
    def encode_image_to_base64(self, image: np.ndarray) -> Optional[str]:
        """Convert OpenCV image to base64 string"""
        try:
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            image_pil = Image.fromarray(image_rgb)
            
            # Convert to base64
            image_stream = BytesIO()
            image_pil.save(image_stream, format='PNG')
            base64_encoded = base64.b64encode(image_stream.getvalue()).decode('utf-8')
            
            return base64_encoded
            
        except Exception as e:
            logger.exception("Error encoding image to base64: %s", e)
            return None
    
    def release(self) -> None:
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.is_initialized = False
        
        cv2.destroyAllWindows()
        logger.info("Camera released")

