import os
import cv2
import base64
import asyncio
from time import sleep
from datetime import datetime
from io import BytesIO
from PIL import Image

import RPi.GPIO as GPIO
from dotenv import load_dotenv
from pymongo import MongoClient


from utils import * # Contains initialInductive, detect_qr, apply_gpt, wait_to_user, insert_image, detectObject_proximity, etc.
from rpi_ws281x import *
from strip_led import strip


#Load environment variables
load_dotenv()

MONGO_CONNECTION_STRING = os.getenv("MONGO_CONNECTION_STRING")
MONGO_DB_NAME = os.getenv("MONGO_DB_NAME")
MONGO_COLLECTION_NAME = "acc"


#Connect to MongoDB
client = MongoClient(MONGO_CONNECTION_STRING)
db = client[MONGO_DB_NAME]
collection = db[MONGO_COLLECTION_NAME]

def update_accumulator(value: int) -> None:
    """
    Update the accumulator value in the MongoDB collection.
    """
    collection.update_one({}, {"$set": {"acc": value}})
    print("Accumulator updated to:", value)

def get_accumulator() -> int:
    """
    Retrieve the accumulator value from MongoDB.
    """
    doc = collection.find_one({})
    if doc and "acc" in doc:
        return doc["acc"]
    return 0

#Helper functions
def encode_frame_to_base64(frame) -> str:
    """
    Converts an OpenCV BGR frame to a base64-encoded PNG image.
    """
    image_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    image_pil = Image.fromarray(image_rgb)
    buffer = BytesIO()
    image_pil.save(buffer, format="PNG")
    return base64.b64encode(buffer.getvalue()).decode("utf-8")

def flash_leds(strip_leds, color: Color, times: int = 3, on_duration: float = 0.5, off_duration: float = 0.5) -> None:
    """
    Flash the LED strip with the specified color for a given number of times.
    """
    for _ in range(times):
        strip_leds.set_color_all(color)
        sleep(on_duration)
        strip_leds.set_color_all(Color(0, 0, 0)) # Turn off the LEDs
        sleep(off_duration)

#Main function

def main():
    # LED color constants (using rpi_ws281x Color format)
    EMPTY = Color(0, 0, 0)
    BLUE = Color(0, 0, 255)
    GREEN = Color(0, 255, 0)
    RED = Color(255, 0, 0)
    ORANGE = Color(255, 71, 0)
    YELLOW = Color(255, 255, 0)
    WHITE = Color(255, 255, 255)
    # Initialize the LED strip and clear any previous settings.
    strip_leds = strip()
    strip_leds.clear_all()

    # Proximity sensor GPIO pins (using BCM numbering)
    DETECT_OBJECT_PIN = 26
    BLUE_PROXIMITY_PIN = 19
    YELLOW_PROXIMITY_PIN = 12
    BROWN_PROXIMITY_PIN = 16

    # Initialize sensors (using a function from utils)
    detect_object_sensor = initialInductive(DETECT_OBJECT_PIN)
    blue_proximity_sensor = initialInductive(BLUE_PROXIMITY_PIN)
    yellow_proximity_sensor = initialInductive(YELLOW_PROXIMITY_PIN)
    brown_proximity_sensor = initialInductive(BROWN_PROXIMITY_PIN)

    # Initialize video capture (camera)
    cap = cv2.VideoCapture(0)
    if not cap.isOpened():
        print("Error: Unable to initialize camera.")
        return

    # Optional: QR Code detection block 
    """
    qr_identified = False
    while not qr_identified:
        ret, frame = cap.read()
        if not ret:
            continue
        data = detect_qr(frame)
        print("QR Data:", data)
        if data is not None:
            qr_identified = True
            strip_leds.set_color_all(GREEN)
        cv2.imshow("QR Code Reader", frame)
        if cv2.waitKey(1) == ord('q'):
            break
    """

    # Initial LED sequence: flash white to indicate readiness.
    sleep(4)
    strip_leds.set_color_all(WHITE)
    sleep(0.5)
    strip_leds.set_color_all(EMPTY)

    # Set initial accumulator value in MongoDB.
    update_accumulator(0)

    detection_timer = 0  # Local timer for processing delay after object detection.
    object_detected = False

    print("System ready. Awaiting object detection...")

    try:
        while True:
            ret, frame = cap.read()
            if not ret:
                print("Warning: Failed to capture frame.")
                continue

            if object_detected:
                # Countdown until ready to process the trash object.
                if detection_timer > 1:
                    detection_timer -= 1
                elif detection_timer == 1:
                    detection_timer = 0
                    sleep(1)

                    # Process trash classification (using GPT-based analysis)
                    trash_class = apply_gpt(frame).lower()

                    current_time = datetime.now()
                    date_str = current_time.strftime("%Y-%m-%d")
                    time_str = current_time.strftime("%H:%M:%S")
                    encoded_image = encode_frame_to_base64(frame)
                    person_thrown = True

                    # Log image and classification to the database (insert_image should be defined)
                    insert_image(encoded_image, date_str, time_str, trash_class, "", person_thrown)

                    if trash_class:
                        # Update accumulator based on trash class.
                        if trash_class == "yellow":
                            update_accumulator(9)
                        elif trash_class == "blue":
                            update_accumulator(10)
                        else:  # Assume brown or other default
                            update_accumulator(11)

                        # Wait for user confirmation
                        confirmation_message = asyncio.run(wait_to_user(trash_class, strip_leds))
                        print("User confirmation:", confirmation_message)

                        if confirmation_message == "correct":
                            update_accumulator(4)
                            sleep(5)
                            update_accumulator(5)
                            sleep(15)
                            if get_accumulator() == 5:
                                update_accumulator(0)
                        elif confirmation_message == "incorrect":
                            update_accumulator(7)
                            sleep(3)
                            update_accumulator(0)
                        else:  # Timeout or unspecified response
                            update_accumulator(8)
                            sleep(3)
                            update_accumulator(0)

                        object_detected = False
                        sleep(2)
                        strip_leds.clear_all()
                    else:
                        # Trash classification failed.
                        print("Trash not recognized. Please try again.")
                        update_accumulator(3)
                        flash_leds(strip_leds, WHITE, times=3)
                        object_detected = False

            else:
                # Check the proximity sensor for object detection.
                if detectObject_proximity(detect_object_sensor):
                    object_detected = True
                    print("Object detected.")
                    update_accumulator(1)
                    strip_leds.set_color_all(WHITE)
                    detection_timer = 30  # Set countdown for processing

            # Handle graceful exit on pressing 'q'
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break

    finally:
        # Cleanup resources
        cap.release()
        cv2.destroyAllWindows()
        GPIO.cleanup()

if __name__ == "__main__":
    main()