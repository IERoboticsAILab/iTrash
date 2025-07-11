"""
Camera module for iTrash system.
Handles video capture, image processing, and QR code detection.
"""

import cv2
import numpy as np
from PIL import Image
import base64
from io import BytesIO
from config.settings import HardwareConfig

class CameraController:
    """Camera controller for video capture and image processing"""
    
    def __init__(self, camera_index=HardwareConfig.CAMERA_INDEX):
        self.camera_index = camera_index
        self.cap = None
        self.is_initialized = False
    
    def initialize(self):
        """Initialize the camera"""
        try:
            self.cap = cv2.VideoCapture(self.camera_index)
            if not self.cap.isOpened():
                print(f"Error: Could not open camera at index {self.camera_index}")
                return False
            
            # Set camera properties
            self.cap.set(cv2.CAP_PROP_FRAME_WIDTH, HardwareConfig.FRAME_WIDTH)
            self.cap.set(cv2.CAP_PROP_FRAME_HEIGHT, HardwareConfig.FRAME_HEIGHT)
            self.cap.set(cv2.CAP_PROP_FPS, 30)
            
            self.is_initialized = True
            print("Camera initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing camera: {e}")
            return False
    
    def read_frame(self):
        """Read a frame from the camera"""
        if not self.is_initialized or self.cap is None:
            return None, None
        
        ret, frame = self.cap.read()
        if not ret:
            print("Error reading frame from camera")
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
            print("Camera not initialized")
            return
        
        while True:
            ret, frame = self.read_frame()
            if not ret:
                break
            
            cv2.imshow(window_name, frame)
            
            # Press 'q' to quit
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    
    def capture_image(self):
        """Capture a single image from the camera"""
        ret, frame = self.read_frame()
        if ret:
            return frame
        return None
    
    def encode_image_to_base64(self, image):
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
            print(f"Error encoding image to base64: {e}")
            return None
    
    def save_image(self, image, filename):
        """Save image to file"""
        try:
            cv2.imwrite(filename, image)
            print(f"Image saved as {filename}")
            return True
        except Exception as e:
            print(f"Error saving image: {e}")
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
        
        resized = cv2.resize(image, (width, height), interpolation=cv2.INTER_AREA)
        return resized
    
    def apply_filters(self, image, filters=None):
        """Apply image filters"""
        if filters is None:
            return image
        
        processed = image.copy()
        
        for filter_name, params in filters.items():
            if filter_name == "blur":
                kernel_size = params.get("kernel_size", 5)
                processed = cv2.GaussianBlur(processed, (kernel_size, kernel_size), 0)
            
            elif filter_name == "sharpen":
                kernel = np.array([[-1, -1, -1],
                                  [-1,  9, -1],
                                  [-1, -1, -1]])
                processed = cv2.filter2D(processed, -1, kernel)
            
            elif filter_name == "brightness":
                beta = params.get("beta", 0)
                processed = cv2.convertScaleAbs(processed, alpha=1, beta=beta)
            
            elif filter_name == "contrast":
                alpha = params.get("alpha", 1.0)
                processed = cv2.convertScaleAbs(processed, alpha=alpha, beta=0)
        
        return processed
    
    def detect_qr_code(self, image):
        """Detect QR code in image"""
        try:
            detector = cv2.QRCodeDetector()
            data, bbox, straight_qrcode = detector.detectAndDecode(image)
            
            if data:
                print(f"QR Code detected: {data}")
                return data
            else:
                return None
                
        except Exception as e:
            print(f"Error detecting QR code: {e}")
            return None
    
    def wait_for_qr_code(self, timeout=30):
        """Wait for QR code to be detected"""
        import time
        
        start_time = time.time()
        while time.time() - start_time < timeout:
            ret, frame = self.read_frame()
            if not ret:
                continue
            
            qr_data = self.detect_qr_code(frame)
            if qr_data:
                return qr_data
            
            # Show frame for debugging
            cv2.imshow("QR Code Detection", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        
        cv2.destroyAllWindows()
        return None
    
    def get_camera_info(self):
        """Get camera information"""
        if not self.is_initialized:
            return None
        
        info = {
            "camera_index": self.camera_index,
            "frame_width": int(self.cap.get(cv2.CAP_PROP_FRAME_WIDTH)),
            "frame_height": int(self.cap.get(cv2.CAP_PROP_FRAME_HEIGHT)),
            "fps": self.cap.get(cv2.CAP_PROP_FPS),
            "brightness": self.cap.get(cv2.CAP_PROP_BRIGHTNESS),
            "contrast": self.cap.get(cv2.CAP_PROP_CONTRAST),
            "saturation": self.cap.get(cv2.CAP_PROP_SATURATION)
        }
        
        return info
    
    def release(self):
        """Release camera resources"""
        if self.cap is not None:
            self.cap.release()
            self.is_initialized = False
        
        cv2.destroyAllWindows()
        print("Camera released")


class ImageProcessor:
    """Image processing utilities"""
    
    @staticmethod
    def preprocess_for_classification(image):
        """Preprocess image for AI classification"""
        # Resize to standard size
        resized = cv2.resize(image, (224, 224))
        
        # Normalize pixel values
        normalized = resized.astype(np.float32) / 255.0
        
        return normalized
    
    @staticmethod
    def enhance_image(image):
        """Enhance image quality for better classification"""
        # Convert to LAB color space
        lab = cv2.cvtColor(image, cv2.COLOR_BGR2LAB)
        
        # Apply CLAHE to L channel
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        lab[:, :, 0] = clahe.apply(lab[:, :, 0])
        
        # Convert back to BGR
        enhanced = cv2.cvtColor(lab, cv2.COLOR_LAB2BGR)
        
        return enhanced
    
    @staticmethod
    def crop_center(image, crop_size):
        """Crop image from center"""
        h, w = image.shape[:2]
        crop_h, crop_w = crop_size
        
        start_h = (h - crop_h) // 2
        start_w = (w - crop_w) // 2
        
        cropped = image[start_h:start_h + crop_h, start_w:start_w + crop_w]
        return cropped 