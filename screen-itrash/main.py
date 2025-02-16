from tkinter import Tk, Label, Frame
from PIL import Image, ImageTk
import threading
import time
import os
import subprocess
import sys
from dotenv import load_dotenv
from pymongo import MongoClient
import pyautogui

# Load environment variables
load_dotenv()

# MongoDB connection details
mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
mongo_db_name = os.getenv("MONGO_DB_NAME")
mongo_collection_name = "acc"

# Connect to MongoDB
client = MongoClient(mongo_connection_string)
db = client[mongo_db_name]
collection = db[mongo_collection_name]

# Retrieve all the images from the database
cursor = collection.find({})


def update_acc(value):
    # Update the accumulator with new acc value
    collection.update_one({}, {"$set": {"acc": value}})
    print("Accumulator updated")


class MediaDisplay:
    def __init__(self, media, acc):
        self.media = media
        self.acc = acc
        self.last_acc = acc  # Initialize last_acc
        self.browser_opened = False
        self.root = Tk()
        self.initUI()
        self.showMedia()

        # Start a separate thread to update acc periodically
        self.timer_thread = threading.Thread(target=self.get_acc_mongo)
        self.timer_thread.daemon = True
        self.timer_thread.start()

        self.root.mainloop()

    def initUI(self):
        self.root.title("Media Display")
        self.root.attributes('-fullscreen', True)
        self.frame = Frame(self.root)
        self.frame.pack(fill='both', expand=True)
        self.label = Label(self.frame)
        self.label.pack(fill='both', expand=True)
        self.root.bind("<Escape>", lambda event: self.root.quit())

    def showMedia(self):
        if not (0 <= self.acc < len(self.media)):
            print(f"Index {self.acc} out of range.")
            return

        if self.acc == 0:
            self.switch_to_chromium()
        elif self.acc == 6:
            # Show the image for ACC == 6
            self.restore_and_show_image()

            # Wait for 1-2 seconds
            time.sleep(5)

            # Reset ACC to 0 after the delay
            update_acc(0)
        else:
            if self.browser_opened:
                self.minimize_chromium()
            if self.acc != self.last_acc:
                self.restore_and_show_image()
                self.last_acc = self.acc  # Update last_acc only when the image is changed

    def switch_to_chromium(self):
        try:
            # Use xdotool to find and focus on the Chromium window
            window_id = subprocess.check_output(["xdotool", "search", "--onlyvisible", "--class", "chromium"]).strip().decode()
            subprocess.call(["xdotool", "windowactivate", window_id])
            self.browser_opened = True
            time.sleep(0.5)  # Allow some time for the switch to complete
        except subprocess.CalledProcessError:
            print("Chromium window not found.")

    def minimize_chromium(self):
        try:
            # Use xdotool to find and minimize the Chromium window
            window_id = subprocess.check_output(["xdotool", "search", "--onlyvisible", "--class", "chromium"]).strip().decode()
            subprocess.call(["xdotool", "windowminimize", window_id])
            self.browser_opened = False
        except subprocess.CalledProcessError:
            print("Failed to minimize Chromium window.")

    def restore_and_show_image(self):
        self.root.deiconify()  # Restore the Tkinter window if it was minimized
        media_item = self.media[self.acc]
        self.showImage(media_item['file'])

    def showImage(self, file):
        try:
            image = Image.open(file)
            image = image.convert("RGB")
            image = image.resize((1600, 900), Image.Resampling.LANCZOS) #1920, 1080
            self.tk_image = ImageTk.PhotoImage(image)
            self.label.config(image=self.tk_image)
        except Exception as e:
            print(f"Error loading image {file}: {e}")
            self.nextMedia()

    def nextMedia(self):
        self.acc = (self.acc + 1) % len(self.media)
        self.showMedia()

    def set_acc(self, value):
        if 0 <= value < len(self.media):
            self.acc = value
            self.showMedia()
        else:
            print(f"Invalid index: {value}. Must be between 0 and {len(self.media) - 1}.")

    def get_acc_mongo(self):
        acc_timer = None

        while True:
            time.sleep(0.1)
            new_acc = cursor[0]["acc"]

            if new_acc == 3:
                if acc_timer is None:
                    acc_timer = time.time()  # Start the timer
                elif time.time() - acc_timer >= 10:  # Check if 10 seconds have passed
                    update_acc(0)
                    acc_timer = None  # Reset the timer
            else:
                acc_timer = None  # Reset the timer if acc changes

            self.set_acc(new_acc)


if __name__ == '__main__':
    media = [
        {'type': 'image', 'file': 'images/white.png'},  # 0
        {'type': 'image', 'file': 'images/processing.png'},  # 1
        {'type': 'image', 'file': 'images/show_trash.png'},  # 2
        {'type': 'image', 'file': 'images/try_again.png'},  # 3
        {'type': 'image', 'file': 'images/great_job.png'},  # 4
        {'type': 'image', 'file': 'images/qr_codes.png'},  # 5
        {'type': 'image', 'file': 'images/reward_received.png'},  # 6
        {'type': 'image', 'file': 'images/incorrect.png'},  # 7
        {'type': 'image', 'file': 'images/timeout.png'},  # 8
        {'type': 'image', 'file': 'images/throw_yellow.png'},  # 9
        {'type': 'image', 'file': 'images/throw_blue.png'},  # 10
        {'type': 'image', 'file': 'images/throw_brown.png'}  # 11
    ]
    acc = 0
    display = MediaDisplay(media, acc)