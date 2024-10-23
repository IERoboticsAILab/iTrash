import base64
import cv2
import numpy as np

  

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




