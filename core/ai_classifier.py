"""
AI classifier module for iTrash system.
Handles YOLO and GPT-based trash classification.
"""

import asyncio
import json
import requests
import logging
import time
from inference_sdk import InferenceHTTPClient
from config.settings import AIConfig, TrashClassification, OPENAI_API_KEY, YOLO_API_KEY

class YOLOClassifier:
    """YOLO-based trash classifier"""
    
    def __init__(self):
        self.client = InferenceHTTPClient(
            api_url=AIConfig.YOLO_API_URL,
            api_key=YOLO_API_KEY
        )
        self.logger = logging.getLogger(__name__)
    
    def classify(self, image):
        """Classify trash using YOLO model"""
        try:
            self.logger.info("Starting YOLO classification...")
            result = self.client.infer(image, model_id=AIConfig.YOLO_MODEL_ID)
            
            if result["predictions"]:
                # Get prediction with highest confidence
                max_pred = max(result["predictions"], key=lambda x: x["confidence"])
                self.logger.info(f"YOLO Prediction: {max_pred}")
                
                # Log all predictions for debugging
                for i, pred in enumerate(result["predictions"]):
                    self.logger.debug(f"YOLO Prediction {i}: {pred}")
                
                # Map class to color
                trash_class = TrashClassification.TRASH_DICT.get(max_pred['class'], "")
                
                # Log classification result
                self.logger.info(f"YOLO classification result: {trash_class} (confidence: {max_pred['confidence']:.3f})")
                
                return trash_class
            else:
                self.logger.warning("No objects detected by YOLO")
                return ""
                
        except Exception as e:
            self.logger.error(f"Error in YOLO classification: {e}")
            return ""


class GPTClassifier:
    """GPT-based trash classifier"""
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.model = AIConfig.GPT_MODEL
        self.max_tokens = AIConfig.GPT_MAX_TOKENS
        self.prompt = AIConfig.GPT_PROMPT
        self.logger = logging.getLogger(__name__)
        self.last_response = None
        self.last_confidence = None
    
    def _encode_image_to_base64(self, image):
        """Convert image to base64 for GPT API"""
        import base64
        import cv2
        from PIL import Image
        from io import BytesIO
        
        # Convert BGR to RGB
        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        
        # Convert to PIL Image
        image_pil = Image.fromarray(image_rgb)
        
        # Convert to base64
        image_stream = BytesIO()
        image_pil.save(image_stream, format='JPEG')
        base64_encoded = base64.b64encode(image_stream.getvalue()).decode('utf-8')
        
        return base64_encoded
    
    def classify(self, image, max_retries=3):
        """Classify trash using GPT-4 Vision"""
        self.logger.info("Starting GPT classification...")
        
        for attempt in range(max_retries):
            try:
                self.logger.info(f"GPT classification attempt {attempt + 1}/{max_retries}")
                base64_image = self._encode_image_to_base64(image)
                
                headers = {
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {self.api_key}"
                }
                
                payload = {
                    "model": self.model,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {
                                    "type": "text",
                                    "text": self.prompt
                                },
                                {
                                    "type": "image_url",
                                    "image_url": {
                                        "url": f"data:image/jpeg;base64,{base64_image}"
                                    }
                                }
                            ]
                        }
                    ],
                    "max_tokens": self.max_tokens
                }
                
                self.logger.info(f"Sending request to GPT API (model: {self.model})")
                response = requests.post(
                    "https://api.openai.com/v1/chat/completions",
                    headers=headers,
                    json=payload,
                    timeout=30
                )
                
                if response.status_code == 200:
                    result = response.json()
                    content = result['choices'][0]['message']['content']
                    
                    # Store the full response for logging
                    self.last_response = {
                        'content': content,
                        'model': result.get('model', 'unknown'),
                        'usage': result.get('usage', {}),
                        'finish_reason': result['choices'][0].get('finish_reason', 'unknown')
                    }
                    
                    self.logger.info(f"GPT API response received: {content[:100]}...")
                    self.logger.debug(f"Full GPT response: {json.dumps(result, indent=2)}")
                    
                    # Parse JSON response
                    try:
                        parsed_response = json.loads(content)
                        trash_class = parsed_response.get('trash_class', '')
                        confidence = parsed_response.get('confidence', None)
                        
                        # Store confidence for external access
                        self.last_confidence = confidence
                        
                        self.logger.info(f"Parsed GPT response - trash_class: {trash_class}, confidence: {confidence}")
                        
                        # Validate color
                        if trash_class in TrashClassification.VALID_COLORS:
                            self.logger.info(f"GPT Classification successful: {trash_class}")
                            return trash_class
                        else:
                            self.logger.warning(f"Invalid color returned by GPT: {trash_class}")
                            continue
                            
                    except json.JSONDecodeError as e:
                        self.logger.error(f"Invalid JSON response from GPT: {content}")
                        self.logger.error(f"JSON decode error: {e}")
                        continue
                        
                else:
                    self.logger.error(f"GPT API error: {response.status_code} - {response.text}")
                    continue
                    
            except Exception as e:
                self.logger.error(f"Error in GPT classification (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    continue
                else:
                    break
        
        self.logger.error("GPT classification failed after all retries")
        return ""
    
    def get_last_response(self):
        """Get the last GPT response for logging purposes"""
        return self.last_response


class HybridClassifier:
    """Hybrid classifier that combines YOLO and GPT"""
    
    def __init__(self):
        self.yolo_classifier = YOLOClassifier()
        self.gpt_classifier = GPTClassifier()
        self.logger = logging.getLogger(__name__)
        self.classification_history = []
    
    def classify(self, image, use_gpt_fallback=True):
        """Classify trash using hybrid approach"""
        self.logger.info("Starting hybrid classification...")
        
        # Try YOLO first
        self.logger.info("Attempting YOLO classification...")
        yolo_result = self.yolo_classifier.classify(image)
        
        if yolo_result and yolo_result in TrashClassification.VALID_COLORS:
            self.logger.info(f"Using YOLO result: {yolo_result}")
            
            # Log classification history
            classification_record = {
                'timestamp': asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else time.time(),
                'method': 'yolo',
                'result': yolo_result,
                'success': True
            }
            self.classification_history.append(classification_record)
            
            return yolo_result
        
        # Fallback to GPT if YOLO fails or returns invalid result
        if use_gpt_fallback:
            self.logger.info("YOLO failed, attempting GPT fallback...")
            gpt_result = self.gpt_classifier.classify(image)
            
            if gpt_result and gpt_result in TrashClassification.VALID_COLORS:
                self.logger.info(f"Using GPT fallback result: {gpt_result}")
                
                # Log classification history
                classification_record = {
                    'timestamp': asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else time.time(),
                    'method': 'gpt',
                    'result': gpt_result,
                    'success': True,
                    'gpt_response': self.gpt_classifier.get_last_response()
                }
                self.classification_history.append(classification_record)
                
                return gpt_result
            else:
                # Log failed GPT attempt
                classification_record = {
                    'timestamp': asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else time.time(),
                    'method': 'gpt',
                    'result': gpt_result,
                    'success': False,
                    'gpt_response': self.gpt_classifier.get_last_response()
                }
                self.classification_history.append(classification_record)
        
        self.logger.error("Both YOLO and GPT failed to classify")
        
        # Log failed classification
        classification_record = {
            'timestamp': asyncio.get_event_loop().time() if asyncio.get_event_loop().is_running() else time.time(),
            'method': 'hybrid',
            'result': None,
            'success': False
        }
        self.classification_history.append(classification_record)
        
        return ""
    
    async def classify_async(self, image, use_gpt_fallback=True):
        """Async version of classification"""
        loop = asyncio.get_event_loop()
        result = await loop.run_in_executor(None, self.classify, image, use_gpt_fallback)
        return result
    
    def get_classification_history(self):
        """Get classification history for logging purposes"""
        return self.classification_history


class ClassificationManager:
    """Manages the classification process with LED feedback"""
    
    def __init__(self, led_strip=None):
        self.classifier = HybridClassifier()
        self.led_strip = led_strip
        self.logger = logging.getLogger(__name__)
        self.last_confidence = None
    
    def set_led_strip(self, led_strip):
        """Set LED strip for visual feedback"""
        self.led_strip = led_strip
    
    async def process_image_with_feedback(self, image):
        """Process image with LED feedback during classification"""
        self.logger.info("Starting image processing with feedback...")
        
        if self.led_strip:
            # Start processing animation
            self.led_strip.set_color_all((255, 255, 255))  # White for processing
            self.logger.debug("Set LEDs to white for processing")
        
        # Perform classification
        result = await self.classifier.classify_async(image)
        
        # Get confidence from GPT if available
        if hasattr(self.classifier.gpt_classifier, 'last_confidence'):
            self.last_confidence = self.classifier.gpt_classifier.last_confidence
        
        if self.led_strip:
            if result:
                # Success - show green briefly
                self.led_strip.set_color_all((0, 255, 0))
                self.logger.debug("Set LEDs to green for success")
                await asyncio.sleep(0.5)
            else:
                # Error - show red briefly
                self.led_strip.set_color_all((255, 0, 0))
                self.logger.debug("Set LEDs to red for error")
                await asyncio.sleep(0.5)
            
            # Clear LEDs
            self.led_strip.clear_all()
            self.logger.debug("Cleared LEDs")
        
        self.logger.info(f"Image processing completed. Result: {result}")
        return result
    
    def get_classification_stats(self):
        """Get classification statistics"""
        # This could be expanded to track accuracy, response times, etc.
        return {
            "classifier_type": "hybrid",
            "yolo_available": True,
            "gpt_available": bool(OPENAI_API_KEY),
            "valid_colors": TrashClassification.VALID_COLORS,
            "classification_history_count": len(self.classifier.classification_history),
            "last_confidence": self.last_confidence
        }


# Utility functions for backward compatibility
def apply_yolo(image):
    """Legacy function for YOLO classification"""
    classifier = YOLOClassifier()
    return classifier.classify(image)


def apply_gpt(image):
    """Legacy function for GPT classification"""
    classifier = GPTClassifier()
    return classifier.classify(image)


async def process_image(image, led_strip):
    """Legacy async function for image processing"""
    manager = ClassificationManager(led_strip)
    return await manager.process_image_with_feedback(image) 