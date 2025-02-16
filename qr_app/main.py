import qrcode
from PIL import Image, ImageDraw, ImageFont
import io
import base64
from flask import Flask, request, send_file
from utils import update_acc, get_acc, update_qr
import threading
from functools import lru_cache
import time
import os
import sys
sys.path.append('/Users/mintaekim/Desktop/HRL/Flappy/Integrated/Flappy_Integrated/flappy_v2')
from blockchain_part.xrp.utils import load_wallet_from_json, send_xrp


app = Flask(__name__)

server_url = "" # put the server url here exmaple in localhost : http://localhost:5000


wallet_scan1 = load_wallet_from_json("../blockchain_part/xrp/wallets/wallet1.json")
wallet_scan2 = load_wallet_from_json("../blockchain_part/xrp/wallets/wallet2.json")
wallet_scan3 = load_wallet_from_json("../blockchain_part/xrp/wallets/wallet3.json")
wallet_scan4 = load_wallet_from_json("../blockchain_part/xrp/wallets/wallet4.json")
wallet_itrash = load_wallet_from_json("../blockchain_part/xrp/wallets/wallet_itrash.json")

organizations = ["Save the Children", "Doctors Without Borders", "Greenpeace", "Cruz Roja"]
wallets = [wallet_scan1, wallet_scan2, wallet_scan3, wallet_scan4]

# Function to create QR codes for each organization
def create_qr_codes(num_codes):
    qr_codes = []
    for i in range(num_codes):
        qr = qrcode.QRCode(version=1, box_size=10, border=5)
        url = f'{server_url}/scan/{i+1}'
        qr.add_data(url)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        # Add the organization's name below the QR code
        img_with_text = Image.new('RGB', (img.size[0], img.size[1] + 30), color='white')
        img_with_text.paste(img, (0, 0))
        
        d = ImageDraw.Draw(img_with_text)
        font = ImageFont.load_default()
        d.text((10, img.size[1] + 5), organizations[i], fill='black', font=font)

        qr_codes.append(img_with_text)
    return qr_codes

# Function to combine multiple QR codes into a single image
def combine_qr_codes(qr_codes):
    total_width = sum(img.size[0] for img in qr_codes)
    max_height = max(img.size[1] for img in qr_codes)
    
    combined_image = Image.new('RGB', (total_width, max_height), color='white')
    
    x_offset = 0
    for img in qr_codes:
        combined_image.paste(img, (x_offset, 0))
        x_offset += img.size[0]
    
    return combined_image

# Cache images for each organization for efficiency
@lru_cache(maxsize=4)
def generate_response_image(organization_name):
    img = Image.new('RGB', (400, 200), color='white')
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    d.text((50, 100), f"The reward has been sent to {organization_name}!", fill='black', font=font)
    return img

# Cache a "You are not recycling!" image
@lru_cache(maxsize=1)
def generate_not_recycling_image():
    img = Image.new('RGB', (400, 200), color='white')
    d = ImageDraw.Draw(img)
    font = ImageFont.load_default()
    d.text((50, 100), "You are not recycling!", fill='red', font=font)
    return img

# Function to handle delayed operations
def handle_update(number):
    time.sleep(25)
    update_qr(number)

# Main route for displaying the QR codes
@app.route('/')
def index():
    num_codes = len(organizations)
    qr_codes = create_qr_codes(num_codes)
    combined_image = combine_qr_codes(qr_codes)
    
    # Convert the combined image into base64 for HTML embedding
    img_byte_arr = io.BytesIO()
    combined_image.save(img_byte_arr, format='PNG')
    img_byte_arr = img_byte_arr.getvalue()
    
    data_uri = base64.b64encode(img_byte_arr).decode('utf-8')
    
    return f'''
    <html>
        <head><title>Who do you want to send the reward to?</title></head>
        <body>
            <h1>Who do you want to send the reward to?</h1>
            <img src="data:image/png;base64,{data_uri}" alt="QR Codes">
        </body>
    </html>
    '''

# Route for scanning a QR code and showing the result
@app.route('/scan/<int:number>')
def scan(number):
    if number < 1 or number > len(organizations):
        return "Invalid organization number", 400
    
    organization_name = organizations[number - 1]
    organization_wallet = wallets[number - 1]
    #send xrp to the organization
    send_xrp(sender=wallet_itrash, receiver = organization_wallet, amount="1000")

    # Determine which image to show based on account status
    if get_acc() == 5:
        # Show reward image and trigger async QR update
        response_image = generate_response_image(organization_name)
        update_acc(6)
        threading.Thread(target=handle_update, args=(number,)).start()
    else:
        # Show "You are not recycling!" image
        response_image = generate_not_recycling_image()

    # Serve the selected image
    img_io = io.BytesIO()
    response_image.save(img_io, 'PNG')
    img_io.seek(0)

    return send_file(img_io, mimetype='image/png')

if __name__ == '__main__':
    app.run(debug=True)