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
    YELLOW_PROXIMITY_PIN = 13
    BROWN_PROXIMITY_PIN = 6
    
    # Camera Configuration
    CAMERA_INDEX = 0
    FRAME_WIDTH = 640
    FRAME_HEIGHT = 480

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
    OBJECT_DETECTION_DELAY = 4  # seconds
    PROCESSING_TIMEOUT = 10     # seconds
    USER_CONFIRMATION_TIMEOUT = 30  # seconds
    LED_BLINK_INTERVAL = 0.5    # seconds
    IMAGE_DISPLAY_DELAY = 5     # seconds

# AI Configuration
class AIConfig:
    YOLO_MODEL_ID = "garbage-classification-3/2"
    YOLO_API_URL = "https://detect.roboflow.com"
    GPT_MODEL = "gpt-4o-mini"
    GPT_MAX_TOKENS = 50
    
    # GPT Prompt for trash classification
    GPT_PROMPT = '''Im going to give you an image and you have to tell me in which bin I should throw the trash. 
    You can choose among 3 different colors of the bin I should throw it: blue ( cardboard and paper), yellow (platic and metal) and brown(organic).  
    You will return just a diccionary, with "trash_class" as the key, and the color you choose as the value.(e.g. {"trash_class":<color>}). 
    If there are no object, the value will be "", but if there is an object, you are forced to choose among one of the 3 colors.
    '''

# Analytics Configuration
class AnalyticsConfig:
    DATA_EXPORT_PATH = "analytics/data/"
    IMAGE_STORAGE_PATH = "analytics/images/"
    CSV_FILENAME = "itrash_data.csv"
    ANALYTICS_PORT = 8501 