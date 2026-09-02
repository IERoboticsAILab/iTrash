"""
Configuration settings for the iTrash unified system.
"""

import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# MongoDB Configuration
MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION_NAME = "acc"

# API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOLO_API_KEY = os.getenv("YOLO_API_KEY")

# Hardware Configuration
class HardwareConfig:
    # LED Strip Configuration
    LED_COUNT = 60
    LED_PIN = 18
    LED_FREQ_HZ = 800000
    LED_DMA = 10
    LED_BRIGHTNESS = 125
    LED_INVERT = False
    LED_CHANNEL = 0
    
    # Proximity Sensor Pins
    DETECT_OBJECT_SENSOR_PIN = 26
    BLUE_PROXIMITY_PIN = 19
    YELLOW_PROXIMITY_PIN = 12
    BROWN_PROXIMITY_PIN = 16
    
    # Debounce / stability requirements (milliseconds)
    DETECTION_HOLD_MS = 3
    
    # Camera Configuration - Raspberry Pi optimized
    CAMERA_INDEX = -1
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480
    # Raspberry Pi camera specific settings
    CAMERA_FPS = 30
    CAMERA_BUFFER_SIZE = 1

    # Image capture storage
    IMAGE_SAVE_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "captured_images")
    IMAGE_FORMAT = "jpg"  # jpg or png

# LED Colors
class Colors:
    EMPTY = (0, 0, 0)
    BLUE = (0, 0, 255)
    GREEN = (0, 255, 0)
    RED = (255, 0, 0)
    ORANGE = (102, 51, 0)
    YELLOW = (255, 255, 0)
    WHITE = (255, 255, 255)
    BROWN = (139, 69, 19)

# System States (ACC Values)
class SystemStates:
    IDLE = 0
    PROCESSING = 1
    SHOW_TRASH = 2
    USER_CONFIRMATION = 3
    SUCCESS = 4
    QR_CODES = 5
    REWARD = 6
    INCORRECT = 7
    TIMEOUT = 8
    THROW_YELLOW = 9
    THROW_BLUE = 10
    THROW_BROWN = 11

# Trash Classification
class TrashClassification:
    TRASH_DICT = {
        'BIODEGRADABLE': "brown",
        'CARDBOARD': "blue",
        "CLOTH": "blue",
        "GLASS": "blue",
        "METAL": "yellow",
        "PAPER": "blue",
        "PLASTIC": "yellow"
    }
    
    VALID_COLORS = ["blue", "yellow", "brown"]

# Display Configuration
class DisplayConfig:
    WINDOW_WIDTH = 1600
    WINDOW_HEIGHT = 900
    FULLSCREEN = True
    
    # Image paths (relative to display/images/)
    IMAGE_MAPPING = {
        0: 'white.png',
        1: 'processing_new.png',
        2: 'show_trash.png',
        3: 'try_again_green.png',
        4: 'great_job.png',
        5: 'qr_codes.png',
        6: 'reward_received_new.png',
        7: 'incorrect_new.png',
        8: 'timeout_new.png',
        9: 'throw_yellow.png',
        10: 'throw_blue.png',
        11: 'throw_brown.png'
    }

# Timing Configuration
class TimingConfig:
    """
    Timing constants grouped by phase/state. Order and comments are for clarity only.
    Values and names are unchanged to preserve behavior.
    """

    # IDLE/detection
    OBJECT_DETECTION_DELAY = 0.5      # seconds — initial delay before object detection starts
    IDLE_TO_PROCESSING_DELAY = 0.5    # seconds — after object detected, before PROCESSING

    # PROCESSING/classification
    PROCESSING_TO_RESULT_DELAY = 3    # seconds — after classification, before showing THROW_*

    # REWARD / QR codes
    REWARD_DELAY = 0.5                  # seconds — before showing REWARD after correct bin
    REWARD_DISPLAY_TIME = 4           # seconds — show REWARD
    QRCODE_DISPLAY_TIME = 5           # seconds — show QR codes before returning to IDLE

    # INCORRECT flow
    INCORRECT_DISPLAY_TIME = 2        # seconds — show INCORRECT before returning to IDLE

# AI Configuration
class AIConfig:
    # Which classifier backend to use: "gpt" (OpenAI, needs network) or
    # "smolvlm" (local llama-server, fully offline). Override with AI_BACKEND.
    BACKEND = os.getenv("AI_BACKEND", "gpt")

    YOLO_MODEL_ID = "garbage-classification-3/2"
    YOLO_API_URL = "https://detect.roboflow.com"
    GPT_MODEL = "gpt-5.4-nano"
    # On the Responses API for reasoning models, this budget covers reasoning
    # tokens too, so it must be generous enough for both the chain of thought
    # and the small JSON answer.
    GPT_MAX_TOKENS = 2048
    # Reasoning effort for GPT-5 family. Valid: "low" | "medium" | "high".
    GPT_REASONING_EFFORT = "medium"
    
    # GPT Prompt for trash classification
    GPT_PROMPT = '''You will be given an image. Your task is to determine which recycling bin the trash in the image should be thrown into, based on its material. 

    The recycling bins are organized by the following colors and materials:
    - blue: for cardboard and paper items only 
    - yellow: for plastic and metal items only 
    - brown: for organic waste and biodegradable items only

    Carefully analyze the objects in the image. If there is a visible object, you must choose exactly one color from blue, yellow, or brown that most closely matches the trash type based on the materials described above. If multiple items are present, select the bin corresponding to the most prominent or largest piece, prioritizing according to the list above.

    Return your answer ONLY as a JSON dictionary with the key "trash_class", and the assigned color as the value, like this: {"trash_class":"yellow"}. Do not include any explanation, commentary, or additional text.

    If there is no object or the image is empty, return {"trash_class":""}.

    Use this mapping strictly:
    - Only "blue", "yellow", or "brown" are valid values for "trash_class" (except for an empty bin, which is "").
    - "blue" is for paper/cardboard, "yellow" is for plastic/metal, "brown" is for organic waste.

    Choose the color that best fits the object, even if it is ambiguous. You must always choose one (unless there is clearly nothing in the image).
    '''

    # --- Local SmolVLM2 backend (llama.cpp llama-server) ---
    # Served by scripts/setup_smolvlm.sh. Chat Completions, not Responses.
    LLAMA_SERVER_URL = os.getenv(
        "LLAMA_SERVER_URL", "http://127.0.0.1:8081/v1/chat/completions"
    )
    # llama-server serves whatever model it was launched with and ignores this
    # field; it exists only because the OpenAI wire format requires it.
    SMOLVLM_MODEL = "smolvlm"
    # The reply is ~10 tokens of JSON and the grammar forbids anything else.
    SMOLVLM_MAX_TOKENS = 32
    # A Pi 4 has no dotprod/i8mm, so image prefill dominates. Generous, but
    # still under the hardware loop's 30s classify_thread timeout.
    SMOLVLM_TIMEOUT = 25

    # Deliberately far shorter than GPT_PROMPT: a 500M model degrades badly on
    # long instructions, and the JSON schema is enforced by grammar anyway, so
    # the prompt does not need to beg for the output format.
    SMOLVLM_PROMPT = (
        "Which recycling bin does the object in this image belong in?\n"
        "blue = paper, cardboard\n"
        "yellow = plastic, metal\n"
        "brown = food scraps, organic waste\n"
        "If the image shows no object, answer with an empty string."
    )

    # "cnn" backend: local MobileNetV3 (ONNX) fine-tuned on kiosk captures.
    # Fully offline, ~100-300ms on a Pi 4 CPU. Model + labels are produced by
    # scripts/train_cnn.py and are gitignored (see models/).
    CNN_MODEL_PATH = os.getenv("CNN_MODEL_PATH", "models/trash_cnn.onnx")
    CNN_LABELS_PATH = os.getenv("CNN_LABELS_PATH", "models/trash_cnn.json")
    # Below this softmax confidence the frame is treated as "no confident bin"
    # (returns ""), which the hardware loop surfaces as the error phase.
    CNN_MIN_CONFIDENCE = float(os.getenv("CNN_MIN_CONFIDENCE", "0.45"))

class APIConfig:
    # Lightweight monitoring API server config
    HOST = "0.0.0.0"
    PORT = 8080

 