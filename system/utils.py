from time import sleep, time
import RPi.GPIO as GPIO
import cv2 
#from ultralytics import YOLO
from inference_sdk import InferenceHTTPClient
import asyncio
from rpi_ws281x import *
import datetime
from dotenv import load_dotenv

from pymongo import MongoClient
from PIL import Image
import base64
from io import BytesIO
import requests
import json
import os


load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
YOLO_API_KEY = os.getenv("YOLO_API_KEY")



### QR DETECTOR ##

def detect_qr(image):
    detector = cv2.QRCodeDetector()
    data, bbox, straight_qrcode = detector.detectAndDecode(image)
    if data:
        #print("QR Code detected:", data)
        return data
    return None

## PROXIMITY SENSOR FUNCTIONS ##


def initialInductive(pin): 
  GPIOpin = pin
  GPIO.setmode(GPIO.BCM)
  GPIO.setup(GPIOpin,GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
  #print("Finished Initiation")
  #print(GPIOpin)
  return GPIOpin



# Detect Object
def detectObject_proximity(pin):
    state = GPIO.input(pin)
    #print(state)
    # 0 --> object detected
    # 1 --> no object
    if state==0:
      print("Object Detected")
      print(pin)
    
      return True
    else:
        return False


## YOLO FUNCTION ##

def apply_yolo(image): 
    
    

    trash_dicc = {'BIODEGRADABLE': "brown",
                    'CARDBOARD': "blue",
                    "CLOTH": "blue",
                    "GLASS": "blue",
                    "METAL": "yellow",
                    "PAPER": "blue",
                    "PLASTIC": "yellow"
    }

    CLIENT = InferenceHTTPClient(
        api_url="https://detect.roboflow.com",
        api_key= YOLO_API_KEY
    )

    trash_class = ""
    result = CLIENT.infer(image, model_id="garbage-classification-3/2")
    if result["predictions"] != []:
        max_pred = max(result["predictions"], key=lambda x: x["confidence"])
        print(max_pred)
        trash_class = trash_dicc[max_pred['class']]
    
    
    return trash_class


def gpt_cleaner(image):
    api_key = OPENAI_API_KEY
    prompt = '''Im going to give you an image and you have to tell me in which bin I should throw the trash. 
    You can choose among 3 different colors of the bin I should throw it: blue ( cardboard and paper), yellow (platic and metal) and brown(organic).  
    You will return just a diccionary, with “trash_class” as the key, and the color you choose as the value.(e.g. {“trash_class”:<color>}). 
    If there are no object, the value will be “”, but if there is an object, you are forced to choose among one of the 3 colors.
   
     '''
    
    base64_image = encode_image_to_base64(image)
    headers = {
                "Content-Type": "application/json",
                "Authorization": f"Bearer {api_key}"
            }
    
    payload = {
  "model": "gpt-4o-mini",
  "messages": [
    {
      "role": "user",
      "content": [
        {
          "type": "text",
          "text": prompt
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
  "max_tokens": 50
}

    response = requests.post("https://api.openai.com/v1/chat/completions", headers=headers, json=payload)

    #print(response.json())
    return response.json()


def apply_gpt(image):
    while True:
        answer = gpt_cleaner(image)
        
        try:
            # Attempt to parse the GPT response
            real_answer = json.loads(answer['choices'][0]['message']['content'])
            
            return real_answer['trash_class']
        except (json.JSONDecodeError, KeyError):
            # Handle JSON decoding error or missing key
            pass

        # If the structure is incorrect or an exception is raised, retry
        print("Retrying due to incorrect structure...")

async def process_image(image, strip_leds):
    strip_leds.set_color_all(Color(0,0,0))
    charging_light_task = asyncio.create_task(sequential_lights(strip_leds, 60, Color(255,255,255), interval=0.5))
    trash_class = apply_yolo(image)

    # Cancel the blink task if it's still running
    if not charging_light_task.done():
        charging_light_task.cancel()

    #await charging_light_task
    return trash_class





async def sequential_lights(strip_leds, num_leds, color, interval=0.5):
    for i in range(num_leds):
        
        # Create a list with the current LED turned on and the rest turned off
        strip_leds.set_pixel_color(i, color)
        await asyncio.sleep(interval)

    # Ensure all LEDs are on at the end
    strip_leds.set_colors([color] * num_leds)

## LEDS FUNCTIONS ##


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

def turn_led_on(led_pin): 
    GPIO.setup(led_pin ,GPIO.OUT)
    print("LED on")
    GPIO.output(led_pin,GPIO.HIGH)




def turn_led_off(led_pin):
    GPIO.setup(led_pin ,GPIO.OUT)
    print("LED off")
    GPIO.output(led_pin,GPIO.LOW)



async def waiting(led_pin):
    GPIO.setup(led_pin, GPIO.OUT)
    for i in range(0,5):
        print(f"LED {led_pin} on")
        GPIO.output(led_pin, GPIO.HIGH)
        await asyncio.sleep(0.5)
        print(f"LED {led_pin} off")
        GPIO.output(led_pin, GPIO.LOW)
        await asyncio.sleep(0.5)



    

######

async def waiting(led_pin):
    GPIO.setup(led_pin, GPIO.OUT)
    for i in range(0,5):
        print(f"LED {led_pin} on")
        GPIO.output(led_pin, GPIO.HIGH)
        await asyncio.sleep(0.5)
        print(f"LED {led_pin} off")
        GPIO.output(led_pin, GPIO.LOW)
        await asyncio.sleep(0.5)








def wait_to_user_2(color, strip_leds):
    empty = Color(0,0,0)
    blue = Color(0,0,255)
    green = Color(0, 255, 0)
    red = Color(255, 0, 0)
    orange = Color(255, 71, 0)
    yellow = Color(255, 255, 0)
    white = Color(255, 255, 255)

    color_pin_proximity = {
        "blue": [blue, 19],  
        "yellow":[yellow, 12],
        "brown":[orange, 16] # todo: look for a new pin for brown prox sensor
    }
    strip_leds.set_color_all(color_pin_proximity[color][0])
    colors = ["blue", "yellow", "brown"]


    
    correct_color = color
    colors.remove(correct_color)
    incorrect_color_1 = colors[0]
    incorrect_color_2 = colors[1]

    start = time()
    while  True: #todo: make asyncronous

        if detectObject_proximity(color_pin_proximity[correct_color][1]):
            strip_leds.set_color_all(green)
            break
        elif detectObject_proximity(color_pin_proximity[incorrect_color_1][1]) or detectObject_proximity(color_pin_proximity[incorrect_color_2][1]):
            strip_leds.set_color_all(red)
            break

async def blink_leds(strip_leds, color, duration):
    """
    Blink the LEDs with the given color for a specific duration.
    The blinking speed increases as time runs out.
    """
    strip_leds.set_color_all(color)
    await asyncio.sleep(3)
    end_time = time() + duration
    blink_speed = 1.0  # initial blink speed in seconds

    while time() < end_time:
        strip_leds.set_color_all(color)
        await asyncio.sleep(blink_speed)
        strip_leds.set_color_all(Color(0, 0, 0))  # turn off LEDs
        await asyncio.sleep(blink_speed)

        # Increase blink speed as time runs out
        remaining_time = end_time - time()
        if remaining_time < 5:
            blink_speed = 0.2  # fast blinking in the last 5 seconds
        elif remaining_time < 8:
            blink_speed = 0.5  # moderate blinking in the last 8 seconds

async def wait_to_user(color, strip_leds):
    empty = Color(0,0,0)
    blue = Color(0,0,255)
    green = Color(0, 255, 0)
    red = Color(255, 0, 0)
    orange = Color(102, 51, 0)
    yellow = Color(255, 255, 0)
    white = Color(255, 255, 255)

    color_pin_proximity = {
        "blue": [blue, 19],  
        "yellow": [yellow, 12],
        "brown": [orange, 16]  # todo: look for a new pin for brown prox sensor
    }
    print(color)
    strip_leds.set_color_all(color_pin_proximity[color][0])
    colors = ["blue", "yellow", "brown"]

    correct_color = color
    colors.remove(correct_color)
    incorrect_color_1 = colors[0]
    incorrect_color_2 = colors[1]

    start_time = time()
    max_duration = 10  # max waiting time in seconds

    # Run the blinking in parallel with detection
    blink_task = asyncio.create_task(blink_leds(strip_leds, color_pin_proximity[color][0], max_duration))

    result = None
    while True:
        if detectObject_proximity(color_pin_proximity[correct_color][1]):
            strip_leds.set_color_all(green)
            result = "correct"
            break
        elif (detectObject_proximity(color_pin_proximity[incorrect_color_1][1]) or
              detectObject_proximity(color_pin_proximity[incorrect_color_2][1])):
            strip_leds.set_color_all(red)
            result = "incorrect"
            break

        # Stop if max duration is reached
        if time() - start_time > max_duration:
            strip_leds.set_color_all(empty)
            result = "timeout"
            break

        await asyncio.sleep(0.1)  # small delay to prevent tight loop

    # Cancel the blink task if it's still running
    if not blink_task.done():
        blink_task.cancel()

    return result  # Return the result of the function


## MONGO PART ##

def encode_image_to_base64(image):
    # Convert the input image to 'uint8' and create a PIL Image
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Save PIL Image to BytesIO object
    image_stream = BytesIO()
    image_pil.save(image_stream, format='PNG')

    # Encode the image as base64
    base64_encoded = base64.b64encode(image_stream.getvalue()).decode('utf-8')

    return base64_encoded




# Connect to MongoDB



load_dotenv()

mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
mongo_db_name = os.getenv("MONGO_DB_NAME")
mongo_collection_name = os.getenv("MONGO_COLLECTION_NAME")
# Connect to MongoDB
client = MongoClient(mongo_connection_string)
#db
db = client[mongo_db_name]



def insert_image(image, date, time,  predicted, real, person_thrown):
    # Collection name
    # Collection name
    collection = db[mongo_collection_name]
    #create random id for the image with a hash of the date
    

    

    # Insert the image into MongoDB with the specified name
    result = collection.insert_one({
                                    
                                    "image": image ,
                                    "date": date, 
                                    "time": time, 
                                    "predicted": predicted, 
                                    "real": real,
                                    "person_thrown": person_thrown
                                    })

    print(f"Image inserted with ObjectID: {result.inserted_id}")
