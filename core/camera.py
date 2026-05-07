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

    def flush_stale_frames(self, count: Optional[int] = None) -> int:
        """Read and discard stale frames before the final capture."""
        if not self.is_initialized or self.cap is None:
            return 0

        flush_count = HardwareConfig.STALE_FRAME_FLUSH_COUNT if count is None else count
        frames_read = 0
        for _ in range(max(0, flush_count)):
            ret, _frame = self.read_frame()
            if not ret:
                break
            frames_read += 1
        return frames_read
    
    def capture_image(self, save_debug: Optional[bool] = None) -> Optional[np.ndarray]:
        """Capture a single image from the camera"""
        ret, frame = self.read_frame()
        if ret:
            should_save = HardwareConfig.CAPTURE_DEBUG_SAVE_ENABLED if save_debug is None else save_debug
            if should_save:
                self._save_debug_capture(frame)
            return frame
        return None

    def capture_for_classification(self) -> Optional[np.ndarray]:
        """Capture and preprocess one image for the classifier."""
        frame = self.capture_image()
        if frame is None:
            return None
        return self.prepare_for_classification(frame)

    @staticmethod
    def apply_configured_crop(frame: np.ndarray) -> np.ndarray:
        """Apply the configured ROI crop, if enabled."""
        if not HardwareConfig.CROP_ENABLED:
            return frame

        height, width = frame.shape[:2]
        x = max(0, min(HardwareConfig.CROP_X, width))
        y = max(0, min(HardwareConfig.CROP_Y, height))
        crop_width = max(0, HardwareConfig.CROP_WIDTH)
        crop_height = max(0, HardwareConfig.CROP_HEIGHT)

        if crop_width == 0 or crop_height == 0:
            return frame

        x2 = max(x, min(x + crop_width, width))
        y2 = max(y, min(y + crop_height, height))
        if x2 == x or y2 == y:
            return frame
        return frame[y:y2, x:x2].copy()

    @staticmethod
    def resize_for_classifier(frame: np.ndarray) -> np.ndarray:
        """Resize frame so the longest edge stays within classifier config."""
        long_edge = max(1, HardwareConfig.CLASSIFIER_IMAGE_LONG_EDGE)
        height, width = frame.shape[:2]
        current_long_edge = max(height, width)
        if current_long_edge <= long_edge:
            return frame

        scale = long_edge / current_long_edge
        resized_size = (max(1, int(width * scale)), max(1, int(height * scale)))
        return cv2.resize(frame, resized_size, interpolation=cv2.INTER_AREA)

    @classmethod
    def prepare_for_classification(cls, frame: np.ndarray) -> np.ndarray:
        """Crop and resize a copy of the captured frame for classification."""
        prepared = frame.copy()
        prepared = cls.apply_configured_crop(prepared)
        prepared = cls.resize_for_classifier(prepared)
        return prepared

    def _save_debug_capture(self, frame: np.ndarray) -> None:
        try:
            save_dir = HardwareConfig.IMAGE_SAVE_DIR
            os.makedirs(save_dir, exist_ok=True)
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
            filename = f"frame_{timestamp}.{HardwareConfig.IMAGE_FORMAT}"
            path = os.path.join(save_dir, filename)
            if HardwareConfig.IMAGE_FORMAT.lower() == "png":
                cv2.imwrite(path, frame, [int(cv2.IMWRITE_PNG_COMPRESSION), 3])
            else:
                cv2.imwrite(path, frame, [int(cv2.IMWRITE_JPEG_QUALITY), 90])
            logger.info("Saved debug capture: %s", path)
        except Exception as e:
            logger.warning("Could not save debug capture: %s", e)
    
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
