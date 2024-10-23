import base64
import requests
import numpy as np
import cv2

from pymongo import MongoClient
import numpy as np
from PIL import Image
import base64
from io import BytesIO
import cv2


# Connect to MongoDB
from dotenv import load_dotenv
import os


load_dotenv()

mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
mongo_db_name = os.getenv("MONGO_DB_NAME")
mongo_collection_name = os.getenv("MONGO_COLLECTION_NAME")
# Connect to MongoDB
client = MongoClient(mongo_connection_string)
#db
db = client[mongo_db_name]

  
def decode(json_object):
    # Extract the Base64-encoded image from the JSON object
    img_base64 = json_object["image"]

    missing_padding = len(img_base64) % 4
    if missing_padding != 0:
        print("Missing padding")
        img_base64 += '=' * (4 - missing_padding)

    # Decode the Base64 string to binary
    img_binary = base64.b64decode(img_base64)

    # Convert the binary data to a NumPy array
    img_array = np.frombuffer(memoryview(img_binary), dtype=np.uint8)

    # Decode the NumPy array to an OpenCV image
    img_decoded = cv2.imdecode(img_array, cv2.IMREAD_COLOR)

    return img_decoded


## SOME USEFUL FUNCTIONS THAT HAS BEEN USED DURING THE EXPERIMENTS BUT ARE NOT IN THE ACTUAL PIPELINE  ##

def encode_image_to_base64(image):
    # Convert the input image to 'uint8' and create a PIL Image
    image_pil = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))

    # Save PIL Image to BytesIO object
    image_stream = BytesIO()
    image_pil.save(image_stream, format='PNG')

    # Encode the image as base64
    base64_encoded = base64.b64encode(image_stream.getvalue()).decode('utf-8')

    return base64_encoded







def insert_image(image, date, predicted, real, person_thrown):
    collection = db[mongo_collection_name]
    #create random id for the image with a hash of the date
    

    

    # Insert the image into MongoDB with the specified name
    result = collection.insert_one({
                                    
                                    "image": image ,
                                    "date": date,  
                                    "predicted": predicted, 
                                    "real": real,
                                    "person_thrown": person_thrown
                                    })

    print(f"Image inserted with ObjectID: {result.inserted_id}")

