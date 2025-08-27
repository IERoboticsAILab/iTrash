"""
AI classifier module for iTrash system.
Handles YOLO and GPT-based trash classification.
"""

import asyncio
import json
import logging
from typing import Any, Dict
import requests
from inference_sdk import InferenceHTTPClient
from config.settings import AIConfig, TrashClassification, OPENAI_API_KEY, YOLO_API_KEY

logger = logging.getLogger(__name__)

class YOLOClassifier:
    """YOLO-based trash classifier"""
    
    def __init__(self):
        self.client = InferenceHTTPClient(
            api_url=AIConfig.YOLO_API_URL,
            api_key=YOLO_API_KEY
        )
    
    def classify(self, image: Any) -> str:
        """Classify trash using YOLO model"""
        try:
            result = self.client.infer(image, model_id=AIConfig.YOLO_MODEL_ID)
            
            if result["predictions"]:
                # Get prediction with highest confidence
                max_pred = max(result["predictions"], key=lambda x: x["confidence"])
                logger.info("YOLO Prediction: %s", max_pred)
                
                # Map class to color
                trash_class = TrashClassification.TRASH_DICT.get(max_pred['class'], "")
                return trash_class
            else:
                logger.info("No objects detected by YOLO")
                return ""
                
        except Exception as e:
            logger.exception("Error in YOLO classification: %s", e)
            return ""


class GPTClassifier:
    """GPT-based trash classifier"""
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.model = AIConfig.GPT_MODEL
        self.max_tokens = AIConfig.GPT_MAX_TOKENS
        self.prompt = AIConfig.GPT_PROMPT
    
    def _encode_image_to_base64(self, image: Any) -> str:
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
    
    def classify(self, image: Any) -> str:
        """Classify trash using GPT-4 Vision - single attempt only"""
        try:
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
            
            response = requests.post(
                "https://api.openai.com/v1/chat/completions",
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                content = result['choices'][0]['message']['content']
                
                # Parse JSON response
                try:
                    parsed_response = json.loads(content)
                    trash_class = parsed_response.get('trash_class', '')
                    
                    # Validate color
                    if trash_class in TrashClassification.VALID_COLORS:
                        logger.info("GPT Classification: %s", trash_class)
                        return trash_class
                    else:
                        logger.warning("GPT Response (unexpected): %s", content)
                        logger.warning("Invalid color returned by GPT: %s", trash_class)
                        return ""
                        
                except json.JSONDecodeError:
                    logger.warning("Invalid JSON response from GPT: %s", content)
                    return ""
                    
            else:
                logger.warning("GPT API error: %s - %s", response.status_code, response.text)
                return ""
                
        except Exception as e:
            logger.exception("Error in GPT classification: %s", e)
            return ""

class ClassificationManager:
    """Manages the classification process with LED feedback"""
    
    def __init__(self, led_strip: Any = None):
        self.classifier = GPTClassifier()
        self.led_strip = led_strip
    
    def set_led_strip(self, led_strip: Any) -> None:
        """Set LED strip for visual feedback"""
        self.led_strip = led_strip
    
    async def process_image_with_feedback(self, image: Any) -> str:
        """Process image with LED feedback during classification

        Retries classification up to 3 times if an invalid result is returned.
        """
        loop = asyncio.get_event_loop()

        max_attempts = 3
        for attempt_index in range(max_attempts):
            result = await loop.run_in_executor(None, self.classifier.classify, image)

            # Return immediately on valid classification
            if result in TrashClassification.VALID_COLORS:
                return result

            # Optional small delay between attempts to avoid hammering the API
            if attempt_index < max_attempts - 1:
                await asyncio.sleep(0.5)

        # All attempts failed; return empty to signal error handling upstream
        return ""
    
    def get_classification_stats(self) -> Dict[str, Any]:
        """Get classification statistics"""
        # This could be expanded to track accuracy, response times, etc.
        return {
            "classifier_type": "gpt",
            "yolo_available": False,
            "gpt_available": bool(OPENAI_API_KEY),
            "valid_colors": TrashClassification.VALID_COLORS
        }


# Utility functions for backward compatibility
def apply_yolo(image: Any) -> str:
    """Legacy function for YOLO classification"""
    classifier = YOLOClassifier()
    return classifier.classify(image)


def apply_gpt(image: Any) -> str:
    """Legacy function for GPT classification"""
    classifier = GPTClassifier()
    return classifier.classify(image)


async def process_image(image: Any, led_strip: Any) -> str:
    """Legacy async function for image processing"""
    manager = ClassificationManager(led_strip)
    return await manager.process_image_with_feedback(image) 