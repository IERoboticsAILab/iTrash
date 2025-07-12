"""
Camera module for iTrash system.
Handles video capture, image processing, and QR code detection.
"""

import cv2
import numpy as np
from PIL import Image
import base64
import logging
from io import BytesIO
from config.settings import HardwareConfig

class CameraController:
    """Camera controller for video capture and image processing"""
    
    def __init__(self, camera_index=HardwareConfig.CAMERA_INDEX):
        self.camera_index = camera_index
        self.cap = None
        self.is_initialized = False
        self.logger = logging.getLogger(__name__)
        self.capture_count = 0
    
    def initialize(self):
        """Initialize the camera"""
        try:
            self.logger.info(f"Initializing camera at index {self.camera_index}")
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                self.logger.error(f"Could not open camera at index {self.camera_index}")
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
                self.logger.error("Could not read test frame from camera")
                return False
            
            self.is_initialized = True
            self.logger.info("Camera initialized successfully")
            self.logger.info(f"Camera resolution: {HardwareConfig.FRAME_WIDTH}x{HardwareConfig.FRAME_HEIGHT}")
            self.logger.info(f"Camera FPS: {HardwareConfig.CAMERA_FPS}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error initializing camera: {e}")
            return False
    
    def read_frame(self):
        """Read a frame from the camera"""
        if not self.is_initialized or self.cap is None:
            self.logger.warning("Attempted to read frame from uninitialized camera")
            return None, None
        
        ret, frame = self.cap.read()
        if not ret:
            self.logger.error("Error reading frame from camera")
            return None, None
        
        return ret, frame
    
    def get_frame(self):
        """Get current frame from camera"""
        ret, frame = self.read_frame()
        if ret:
            return frame
        return None
    
    def show_frame(self, window_name="Camera Feed"):
        """Display the camera feed in a window"""
        if not self.is_initialized:
            self.logger.warning("Camera not initialized")
            return
        
        self.logger.info(f"Starting camera feed display: {window_name}")
        while True:
            ret, frame = self.read_frame()
            if not ret:
                break
            
            cv2.imshow(window_name, frame)
            
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        self.logger.info("Camera feed display stopped")
    
    def capture_image(self):
        """Capture a single image from the camera"""
        self.logger.info("Capturing image from camera...")
        ret, frame = self.read_frame()
        if ret:
            self.capture_count += 1
            self.logger.info(f"Image captured successfully (capture #{self.capture_count})")
            self.logger.debug(f"Captured image shape: {frame.shape}")
            return frame
        else:
            self.logger.error("Failed to capture image from camera")
            return None
    
    def encode_image_to_base64(self, image):
        """Convert OpenCV image to base64 string"""
        try:
            self.logger.debug("Encoding image to base64...")
            # Convert BGR to RGB
            image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            
            # Convert to PIL Image
            image_pil = Image.fromarray(image_rgb)
            
            # Convert to base64
            image_stream = BytesIO()
            image_pil.save(image_stream, format='PNG')
            base64_encoded = base64.b64encode(image_stream.getvalue()).decode('utf-8')
            
            self.logger.debug("Image encoded to base64 successfully")
            return base64_encoded
            
        except Exception as e:
            self.logger.error(f"Error encoding image to base64: {e}")
            return None
    
    def save_image(self, image, filename):
        """Save image to file"""
        try:
            self.logger.info(f"Saving image to {filename}")
            cv2.imwrite(filename, image)
            self.logger.info(f"Image saved successfully as {filename}")
            return True
        except Exception as e:
            self.logger.error(f"Error saving image: {e}")
            return False
    
    def resize_image(self, image, width=None, height=None):
        """Resize image while maintaining aspect ratio"""
        if width is None and height is None:
            return image
        
        h, w = image.shape[:2]
        
        if width is None:
            # Calculate width based on height
            aspect_ratio = w / h
            width = int(height * aspect_ratio)
        elif height is None:
            # Calculate height based on width
            aspect_ratio = h / w
            height = int(width * aspect_ratio)
        
        self.logger.debug(f"Resizing image from {w}x{h} to {width}x{height}")
        resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
        return resized
    
    def apply_filters(self, image, filters=None):
        """Apply image filters"""
        if filters is None:
            return image
        
        self.logger.debug(f"Applying filters: {list(filters.keys())}")
        processed = image.copy()
        
        for filter_name, params in filters.items():
            if filter_name == "blur":
                kernel_size = params.get("kernel_size", 5)
                processed = cv2.GaussianBlur(processed, (kernel_size, kernel_size), 0)
                self.logger.debug(f"Applied blur filter with kernel size {kernel_size}")
            
            elif filter_name == "sharpen":
                kernel = np.array([[-1, -1, -1],
                                  [-1,  9, -1],
                                  [-1, -1, -1]])
                processed = cv2.filter2D(processed, -1, kernel)
                self.logger.debug("Applied sharpen filter")
            
            elif filter_name == "brightness":
                beta = params.get("beta", 0)
                processed = cv2.convertScaleAbs(processed, alpha=1, beta=beta)
                self.logger.debug(f"Applied brightness filter with beta {beta}")
            
            elif filter_name == "contrast":
                alpha = params.get("alpha", 1.0)
                processed = cv2.convertScaleAbs(processed, alpha=alpha, beta=0)
                self.logger.debug(f"Applied contrast filter with alpha {alpha}")
        
        return processed
    
    def detect_qr_code(self, image):
        """Detect QR code in image"""
        try:
            self.logger.debug("Detecting QR code in image...")
            detector = cv2.QRCodeDetector()
            data, bbox, straight_qrcode = detector.detectAndDecode(image)
            
            if data:
                self.logger.info(f"QR Code detected: {data}")
                return data
            else:
                self.logger.debug("No QR code detected in image")
                return None
                
        except Exception as e:
            self.logger.error(f"Error detecting QR code: {e}")
            return None
    
    def wait_for_qr_code(self, timeout=30):
        """Wait for QR code to be detected"""
        import time
        
        self.logger.info(f"Waiting for QR code detection (timeout: {timeout}s)")
        start_time = time.time()
        while time.time() - start_time < timeout:
            ret, frame = self.read_frame()
            if not ret:
                continue
            
            qr_data = self.detect_qr_code(frame)
            if qr_data:
                self.logger.info(f"QR code found after {time.time() - start_time:.2f}s")
                return qr_data
        
        self.logger.warning(f"QR code detection timed out after {timeout}s")
        return None
    
    def get_camera_info(self):
        """Get camera information"""
        if not self.is_initialized or self.cap is None:
            return None
        
        try:
            info = {
                'camera_index': self.camera_index,
                'frame_width': int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
                'frame_height': int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
                'fps': self.cap.get(cv2.CAP_PROP_FPS),
                'buffer_size': int(self.cap.get(cv2.CAP_PROP_BUFFERSIZE)),
                'capture_count': self.capture_count
            }
            self.logger.debug(f"Camera info: {info}")
            return info
        except Exception as e:
            self.logger.error(f"Error getting camera info: {e}")
            return None
    
    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.logger.info("Releasing camera resources")
            self.cap.release()
            self.cap = None
            self.is_initialized = False
            self.logger.info("Camera resources released")


class ImageProcessor:
    """Image processing utilities"""
    
    @staticmethod
    def preprocess_for_classification(image):
        """Preprocess image for classification"""
        # Add preprocessing logic here
        return image
    
    @staticmethod
    def enhance_image(image):
        """Enhance image quality"""
        # Add enhancement logic here
        return image
    
    @staticmethod
    def crop_center(image, crop_size):
        """Crop image from center"""
        h, w = image.shape[:2]
        crop_h, crop_w = crop_size
        
        start_h = (h - crop_h) // 2
        start_w = (w - crop_w) // 2
        
        return image[start_h:start_h + crop_h, start_w:start_w + crop_w] 