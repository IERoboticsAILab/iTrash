"""
AI classifier module for iTrash system.
Handles YOLO and GPT-based trash classification.
"""

import asyncio
import json
import requests
from inference_sdk import InferenceHTTPClient
from config.settings import AIConfig, TrashClassification, OPENAI_API_KEY, YOLO_API_KEY

class YOLOClassifier:
    """YOLO-based trash classifier"""
    
    def __init__(self):
        self.client = InferenceHTTPClient(
            api_url=AIConfig.YOLO_API_URL,
            api_key=YOLO_API_KEY
        )
    
    def classify(self, image):
        """Classify trash using YOLO model"""
        try:
            result = self.client.infer(image, model_id=AIConfig.YOLO_MODEL_ID)
            
            if result["predictions"]:
                # Get prediction with highest confidence
                max_pred = max(result["predictions"], key=lambda x: x["confidence"])
                print(f"YOLO Prediction: {max_pred}")
                
                # Map class to color
                trash_class = TrashClassification.TRASH_DICT.get(max_pred['class'], "")
                return trash_class
            else:
                print("No objects detected by YOLO")
                return ""
                
        except Exception as e:
            print(f"Error in YOLO classification: {e}")
            return ""


class GPTClassifier:
    """GPT-based trash classifier"""
    
    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.model = AIConfig.GPT_MODEL
        self.max_tokens = AIConfig.GPT_MAX_TOKENS
        self.prompt = AIConfig.GPT_PROMPT
    
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
        for attempt in range(max_retries):
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
                            print(f"GPT Classification: {trash_class}")
                            return trash_class
                        else:
                            print(f"GPT Response: {content}")
                            print(f"Invalid color returned by GPT: {trash_class}")
                            continue
                            
                    except json.JSONDecodeError:
                        print(f"Invalid JSON response from GPT: {content}")
                        continue
                        
                else:
                    print(f"GPT API error: {response.status_code} - {response.text}")
                    continue
                    
            except Exception as e:
                print(f"Error in GPT classification (attempt {attempt + 1}): {e}")
                if attempt < max_retries - 1:
                    continue
                else:
                    break
        
        print("GPT classification failed after all retries")
        return ""

class ClassificationManager:
    """Manages the classification process with LED feedback"""
    
    def __init__(self, led_strip=None):
        self.classifier = GPTClassifier()
        self.led_strip = led_strip
    
    def set_led_strip(self, led_strip):
        """Set LED strip for visual feedback"""
        self.led_strip = led_strip
    
    async def process_image_with_feedback(self, image):
        """Process image with LED feedback during classification"""
        if self.led_strip:
            # Start processing animation
            self.led_strip.set_color_all((255, 255, 255))  # White for processing
        
        # Perform classification
        result = await self.classifier.classify(image)
        
        if self.led_strip:
            if result:
                # Success - show green briefly
                self.led_strip.set_color_all((0, 255, 0))
                await asyncio.sleep(0.5)
            else:
                # Error - show red briefly
                self.led_strip.set_color_all((255, 0, 0))
                await asyncio.sleep(0.5)
            
            # Clear LEDs
            self.led_strip.clear_all()
        
        return result
    
    def get_classification_stats(self):
        """Get classification statistics"""
        # This could be expanded to track accuracy, response times, etc.
        return {
            "classifier_type": "gpt",
            "yolo_available": False,
            "gpt_available": bool(OPENAI_API_KEY),
            "valid_colors": TrashClassification.VALID_COLORS
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