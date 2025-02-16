
from time import sleep
from pymongo import MongoClient
from dotenv import load_dotenv
import os

load_dotenv()

mongo_connection_string = ""
mongo_db_name = ""
mongo_collection_name = "acc"
collection_images_name = "images"
# Connect to MongoDB
client = MongoClient(mongo_connection_string,  tls=True, tlsAllowInvalidCertificates=True)
#db
db = client[mongo_db_name]
# Collection name
collection = db[mongo_collection_name]
#collecion images
collection_images = db[collection_images_name]

# Retrieve all the images from the database
cursor = collection.find({})



def update_acc(value):
    # Update the accumulator with new acc value
    collection.update_one({}, {"$set": {"acc": value}})
    #collection.update_one({}, {"$inc": {"acc": 3}})
    print("Accumulator updated")


def get_acc():
    # Retrieve the accumulator value
    acc = cursor[0]["acc"]
    return acc


#get last record from mongo and update the qr parameter

def update_qr(value):
    # Update qr value of the last record in collection_images
    last_item = collection_images.find_one(sort=[("_id", -1)])  # Get the last item based on _id
    if last_item:
        collection_images.update_one({"_id": last_item["_id"]}, {"$set": {"qr_scanned": value}})
        print("QR updated")
    else:
        print("No records found")