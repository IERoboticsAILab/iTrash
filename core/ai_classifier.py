"""
AI classifier module for iTrash system.
Handles YOLO and GPT-based trash classification.
"""

import asyncio
import json
import logging
import time
from typing import Any, Dict, Optional
import requests
from inference_sdk import InferenceHTTPClient
from config.settings import AIConfig, TrashClassification, OPENAI_API_KEY, YOLO_API_KEY

logger = logging.getLogger(__name__)

# Status codes worth retrying. 408/425/429 are throttling/timing related,
# 5xx are server-side. Everything else is treated as a hard failure.
_RETRYABLE_STATUS = {408, 425, 429, 500, 502, 503, 504}
_MAX_HTTP_ATTEMPTS = 3
_BASE_BACKOFF_SECONDS = 0.5
_OPENAI_RESPONSES_URL = "https://api.openai.com/v1/responses"

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
    """GPT-based trash classifier using the OpenAI Responses API.

    The classifier targets reasoning-capable models (GPT-5 family) and uses
    Structured Outputs to guarantee the response is a JSON object whose
    ``trash_class`` field is one of the allowed colors. It also reuses a
    single HTTP session, retries transient failures, and surfaces
    ``incomplete`` responses (e.g. when the token budget is exhausted by
    reasoning).
    """

    # Allowed enum values for the structured output. Empty string means
    # "no object visible" and is intentionally accepted to mirror the prompt.
    _ALLOWED_VALUES = list(TrashClassification.VALID_COLORS) + [""]

    def __init__(self):
        self.api_key = OPENAI_API_KEY
        self.model = AIConfig.GPT_MODEL
        self.max_tokens = AIConfig.GPT_MAX_TOKENS
        self.reasoning_effort = getattr(AIConfig, "GPT_REASONING_EFFORT", "minimal")
        self.prompt = AIConfig.GPT_PROMPT
        self.url = _OPENAI_RESPONSES_URL
        self.timeout = 60
        self._session = requests.Session()

    def _encode_image_to_base64(self, image: Any) -> str:
        """Convert image to a downscaled base64 JPEG suitable for the API.

        Resizing keeps the longest edge at 512px, which is plenty for
        classification while dramatically reducing bandwidth and latency.
        """
        import base64
        import cv2
        from PIL import Image
        from io import BytesIO

        image_rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image_pil = Image.fromarray(image_rgb)
        image_pil.thumbnail((512, 512))

        image_stream = BytesIO()
        image_pil.save(image_stream, format="JPEG", quality=80)
        return base64.b64encode(image_stream.getvalue()).decode("utf-8")

    def _extract_response_text(self, result: Dict[str, Any]) -> str:
        """Extract text from a Responses API payload.

        Reasoning models emit ``reasoning`` items alongside ``message`` items;
        only the latter contain visible text. Filter explicitly so future
        schema additions don't trick us into reading the wrong field.
        """
        if result.get("output_text"):
            return result["output_text"]

        for output_item in result.get("output", []):
            if output_item.get("type") not in (None, "message"):
                continue
            for content_item in output_item.get("content", []):
                if content_item.get("type") not in (None, "output_text"):
                    continue
                text = content_item.get("text", "")
                if text:
                    return text

        return ""

    def _build_payload(self, base64_image: str) -> Dict[str, Any]:
        """Build the Responses API payload with structured outputs."""
        return {
            "model": self.model,
            "input": [
                {
                    "role": "user",
                    "content": [
                        {"type": "input_text", "text": self.prompt},
                        {
                            "type": "input_image",
                            "image_url": f"data:image/jpeg;base64,{base64_image}",
                        },
                    ],
                }
            ],
            "max_output_tokens": self.max_tokens,
            "reasoning": {"effort": self.reasoning_effort},
            "text": {
                "format": {
                    "type": "json_schema",
                    "name": "trash_classification",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "trash_class": {
                                "type": "string",
                                "enum": self._ALLOWED_VALUES,
                            }
                        },
                        "required": ["trash_class"],
                    },
                }
            },
        }

    def _post_with_retries(self, payload: Dict[str, Any]) -> Optional[requests.Response]:
        """POST to the Responses API with backoff on transient failures.

        Returns the final ``Response`` (which may still be a hard error), or
        ``None`` if every attempt failed before getting a response.
        """
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }

        last_response: Optional[requests.Response] = None
        for attempt in range(_MAX_HTTP_ATTEMPTS):
            try:
                response = self._session.post(
                    self.url,
                    headers=headers,
                    json=payload,
                    timeout=self.timeout,
                )
            except (requests.ConnectionError, requests.Timeout) as exc:
                logger.warning(
                    "GPT request network error (attempt %d/%d): %s",
                    attempt + 1, _MAX_HTTP_ATTEMPTS, exc,
                )
                if attempt < _MAX_HTTP_ATTEMPTS - 1:
                    time.sleep(_BASE_BACKOFF_SECONDS * (2 ** attempt))
                continue

            last_response = response
            if response.status_code in _RETRYABLE_STATUS:
                retry_after = response.headers.get("Retry-After")
                try:
                    delay = float(retry_after) if retry_after else _BASE_BACKOFF_SECONDS * (2 ** attempt)
                except ValueError:
                    delay = _BASE_BACKOFF_SECONDS * (2 ** attempt)
                logger.warning(
                    "GPT transient error %s (attempt %d/%d), retrying in %.2fs",
                    response.status_code, attempt + 1, _MAX_HTTP_ATTEMPTS, delay,
                )
                if attempt < _MAX_HTTP_ATTEMPTS - 1:
                    time.sleep(delay)
                continue

            return response

        return last_response

    def classify(self, image: Any) -> str:
        """Classify trash from an image.

        Returns one of ``TrashClassification.VALID_COLORS`` on success, or
        ``""`` if no object was detected or any error/incomplete response
        occurred. Callers can distinguish "no object" from "error" only via
        logs; the ``ClassificationManager`` retries this method a few times,
        so transient empties are absorbed there.
        """
        if not self.api_key:
            logger.error("OPENAI_API_KEY is not configured; skipping GPT classification")
            return ""

        try:
            base64_image = self._encode_image_to_base64(image)
        except Exception:
            logger.exception("Failed to encode image for GPT classification")
            return ""

        payload = self._build_payload(base64_image)

        try:
            response = self._post_with_retries(payload)
        except Exception:
            logger.exception("Unexpected error posting to GPT")
            return ""

        if response is None:
            logger.warning("GPT request failed: no response after retries")
            return ""

        if response.status_code != 200:
            logger.warning(
                "GPT API error: %s - %s", response.status_code, response.text,
            )
            return ""

        try:
            result = response.json()
        except ValueError:
            logger.warning("GPT response was not valid JSON: %s", response.text)
            return ""

        if result.get("status") == "incomplete":
            logger.warning(
                "GPT response incomplete: %s",
                result.get("incomplete_details"),
            )
            return ""

        content = self._extract_response_text(result)
        if not content:
            logger.warning(
                "GPT returned no text. Raw response: %s",
                json.dumps(result, ensure_ascii=False),
            )
            return ""

        try:
            parsed_response = json.loads(content)
        except json.JSONDecodeError:
            logger.warning("Invalid JSON response from GPT: %s", content)
            return ""

        trash_class = parsed_response.get("trash_class", "")
        if trash_class in TrashClassification.VALID_COLORS:
            logger.info("GPT Classification: %s", trash_class)
            return trash_class

        if trash_class == "":
            logger.info("GPT reported no object in frame")
            return ""

        logger.warning("Unexpected trash_class value from GPT: %r", trash_class)
        return ""

class SmolVLMClassifier(GPTClassifier):
    """Local SmolVLM2 classifier served by llama.cpp's ``llama-server``.

    llama-server exposes an OpenAI-compatible ``/v1/chat/completions`` endpoint
    that accepts base64 image_url parts, so everything GPTClassifier already
    does -- image downscaling, session reuse, retry/backoff, result validation
    -- is inherited unchanged. Only the request body and the location of the
    reply text differ.

    Structured output is enforced server-side: llama.cpp compiles the JSON
    schema into a GBNF grammar, so a 500M model physically cannot emit a
    ``trash_class`` outside the enum. That guarantee is what makes a model
    this small usable here at all.
    """

    def __init__(self):
        super().__init__()
        self.url = AIConfig.LLAMA_SERVER_URL
        self.model = AIConfig.SMOLVLM_MODEL
        self.prompt = AIConfig.SMOLVLM_PROMPT
        self.max_tokens = AIConfig.SMOLVLM_MAX_TOKENS
        self.timeout = AIConfig.SMOLVLM_TIMEOUT
        # llama-server ignores auth, but the inherited classify() refuses to
        # send when api_key is falsy. A placeholder keeps that guard honest.
        self.api_key = "local"

    def _build_payload(self, base64_image: str) -> Dict[str, Any]:
        """Chat Completions body with a grammar-constrained JSON schema."""
        return {
            "model": self.model,
            "messages": [
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.prompt},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": f"data:image/jpeg;base64,{base64_image}"
                            },
                        },
                    ],
                }
            ],
            "max_tokens": self.max_tokens,
            # Greedy decoding: this is a classification, not a creative task.
            "temperature": 0.0,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "trash_classification",
                    "strict": True,
                    "schema": {
                        "type": "object",
                        "additionalProperties": False,
                        "properties": {
                            "trash_class": {
                                "type": "string",
                                "enum": self._ALLOWED_VALUES,
                            }
                        },
                        "required": ["trash_class"],
                    },
                },
            },
        }

    def _extract_response_text(self, result: Dict[str, Any]) -> str:
        """Pull the reply out of a Chat Completions payload."""
        choices = result.get("choices") or []
        if not choices:
            return ""
        return (choices[0].get("message") or {}).get("content") or ""


class CNNClassifier:
    """Local MobileNetV3 trash classifier (ONNX), fine-tuned on kiosk captures.

    No HTTP, no torch: onnxruntime + numpy only, so it runs offline on the Pi
    in ~100-300ms. The model was distilled from the GPT backend by auto-labeling
    ``captured_images/`` (see scripts/train_cnn.py) to close the domain gap that
    made off-the-shelf garbage classifiers useless on real kiosk frames.

    Shares the ``classify(image) -> str`` contract with GPTClassifier: returns a
    color in ``TrashClassification.VALID_COLORS`` or ``""`` (no object / low
    confidence / error).
    """

    def __init__(self):
        import json as _json
        import numpy as np
        import onnxruntime as ort

        self._np = np
        meta = _json.load(open(AIConfig.CNN_LABELS_PATH))
        self.classes = meta["classes"]
        self.mean = np.array(meta["mean"], dtype=np.float32).reshape(3, 1, 1)
        self.std = np.array(meta["std"], dtype=np.float32).reshape(3, 1, 1)
        self.min_conf = AIConfig.CNN_MIN_CONFIDENCE
        self.session = ort.InferenceSession(
            AIConfig.CNN_MODEL_PATH, providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name
        logger.info(
            "Loaded CNN backend %s (classes=%s)", AIConfig.CNN_MODEL_PATH, self.classes
        )

    def _preprocess(self, image: Any):
        """cv2 BGR array -> normalized NCHW float32, matching eval transforms
        (resize shorter edge to 256, center-crop 224, ImageNet normalize)."""
        import cv2

        np = self._np
        h, w = image.shape[:2]
        scale = 256 / min(h, w)
        image = cv2.resize(image, (round(w * scale), round(h * scale)))
        h, w = image.shape[:2]
        top, left = (h - 224) // 2, (w - 224) // 2
        image = image[top:top + 224, left:left + 224]
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        image = image.transpose(2, 0, 1)  # HWC -> CHW
        image = (image - self.mean) / self.std
        return image[np.newaxis, :].astype(np.float32)

    def classify(self, image: Any) -> str:
        np = self._np
        try:
            x = self._preprocess(image)
            logits = self.session.run(None, {self.input_name: x})[0][0]
        except Exception:
            logger.exception("CNN inference failed")
            return ""
        e = np.exp(logits - logits.max())
        probs = e / e.sum()
        i = int(probs.argmax())
        cls, conf = self.classes[i], float(probs[i])
        logger.info("CNN prediction: %s (%.2f)", cls, conf)
        if conf < self.min_conf:
            return ""
        return cls if cls in TrashClassification.VALID_COLORS else ""


def _build_classifier() -> GPTClassifier:
    """Pick the classifier backend named by ``AIConfig.BACKEND``."""
    backend = getattr(AIConfig, "BACKEND", "gpt").lower()
    if backend == "smolvlm":
        logger.info("Using local SmolVLM backend at %s", AIConfig.LLAMA_SERVER_URL)
        return SmolVLMClassifier()
    if backend == "cnn":
        logger.info("Using local CNN backend at %s", AIConfig.CNN_MODEL_PATH)
        return CNNClassifier()
    if backend != "gpt":
        logger.warning("Unknown AI backend %r, falling back to gpt", backend)
    logger.info("Using OpenAI GPT backend (%s)", AIConfig.GPT_MODEL)
    return GPTClassifier()


class ClassificationManager:
    """Manages the classification process with LED feedback"""

    def __init__(self, led_strip: Any = None):
        self.classifier = _build_classifier()
        self.led_strip = led_strip
    
    def set_led_strip(self, led_strip: Any) -> None:
        """Set LED strip for visual feedback"""
        self.led_strip = led_strip
    
    async def process_image_with_feedback(self, image: Any) -> str:
        """Process image with LED feedback during classification.

        Retries classification up to 3 times if an invalid result is returned.
        Uses ``asyncio.to_thread`` so the blocking HTTP call doesn't stall the
        event loop and avoids the deprecated ``get_event_loop`` API.
        """
        max_attempts = 3
        for attempt_index in range(max_attempts):
            result = await asyncio.to_thread(self.classifier.classify, image)

            if result in TrashClassification.VALID_COLORS:
                return result

            if attempt_index < max_attempts - 1:
                await asyncio.sleep(0.5)

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