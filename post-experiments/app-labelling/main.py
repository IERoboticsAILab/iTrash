import os
from dotenv import load_dotenv
import cv2
from PIL import Image
from pymongo import MongoClient
import streamlit as st
from utils import decode 

# Load environment variables
load_dotenv()

mongo_connection_string = os.getenv("MONGO_CONNECTION_STRING")
mongo_db_name = os.getenv("MONGO_DB_NAME")
mongo_collection_name = os.getenv("MONGO_COLLECTION_NAME")

# Connect to MongoDB
client = MongoClient(mongo_connection_string)
db = client[mongo_db_name]
collection = db[mongo_collection_name]

# Initialize session state variables
if 'current_index' not in st.session_state:
    st.session_state.current_index = 0
if 'selected_color' not in st.session_state:
    st.session_state.selected_color = None
if "filter" not in st.session_state:
    st.session_state.filter = {}
if "images" not in st.session_state:
    st.session_state.images = list(collection.find({}))  # Load all images initially
if "dates" not in st.session_state:
    st.session_state.dates = list({image['date'] for image in st.session_state.images})

# Sidebar - Filter panel
st.sidebar.title("Filter")
st.sidebar.subheader("Filter by color")
predicted_colors = st.sidebar.multiselect("Select predicted color", ["Yellow", "Blue", "Brown"])
real_colors = st.sidebar.multiselect("Select real color", ["Yellow", "Blue", "Brown"])
day = st.sidebar.multiselect("Select date", st.session_state.dates)

# Apply filters
if st.sidebar.button("Filter"):
    filter_query = {}
    if predicted_colors:
        filter_query['predicted'] = {"$in": predicted_colors}
    if real_colors:
        filter_query['real'] = {"$in": real_colors}
    if day:
        filter_query['date'] = {"$in": day}
    
    st.session_state.filter = filter_query
    st.session_state.images = list(collection.find(st.session_state.filter))  # Fetch filtered images
    st.session_state.current_index = 0  # Reset index after filtering

# Function to display the current image
def display_image(index):
    if index >= len(st.session_state.images):
        st.write("No images found")
        return
    
    query = st.session_state.images[index]
    image_bgr = decode(query)  # Assuming decode returns a BGR image
    image_rgb = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2RGB)  # Convert BGR to RGB
    image_pil = Image.fromarray(image_rgb).resize((700, 500))  # Resize the image
    
    # Display image and details
    st.write(f"ID: {query['_id']}")
    st.write(f"Date: {query['date']}")
    st.write(f"Time: {query['time']}")
    st.write(f"Real color: {query['real']}")
    st.write(f"Predicted color: {query['predicted']}")
    st.write(f"Person thrown: {query['person_thrown']}")
    st.image(image_pil, caption='Current Image')

# Display the current image
display_image(st.session_state.current_index)

# Color selection buttons
col1, col2, col3 = st.columns(3)
with col1:
    if st.button('Yellow'):
        st.session_state.selected_color = 'yellow'
with col2:
    if st.button('Blue'):
        st.session_state.selected_color = 'blue'
with col3:
    if st.button('Brown'):
        st.session_state.selected_color = 'brown'

# Navigation and Save buttons
col4, col5, col6 = st.columns(3)
with col4:
    if st.button('Previous'):
        if st.session_state.current_index > 0:
            st.session_state.current_index -= 1
        else:
            st.write("This is the first image.")

with col5:
    if st.button('Next'):
        if st.session_state.current_index < len(st.session_state.images) - 1:
            st.session_state.current_index += 1
        else:
            st.write("No more images.")

with col6:
    if st.button('Save'):
        current_index = st.session_state.current_index
        query = st.session_state.images[current_index]
        if st.session_state.selected_color:
            st.write(f'Selected Color: {st.session_state.selected_color}')
            collection.update_one({'_id': query['_id']}, {'$set': {'real': st.session_state.selected_color}})
        else:
            st.write('No color selected')
