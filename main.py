# app.py
import requests
import os
import pygame
import hashlib
import streamlit as st
import time
import base64

def get_sha256(text):
    """Compute the SHA-256 hash of the text and return it."""
    return hashlib.sha256(text.encode()).hexdigest()

# Given some arbitrary text, create an 
# audio file that can play the text
def create_audio_file(text):
    CHUNK_SIZE = 1024
    VOICE_ID = "LcfcDJNUP1GQjkzn1xUU"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    ELEVEN_LABS_API_KEY = os.environ['ELEVEN_LABS_API_KEY']

    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": ELEVEN_LABS_API_KEY
    }

    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    # Make sure the 'audio' folder exists
    if not os.path.exists('audio'):
        os.makedirs('audio')

    filename = os.path.join('audio', f"{get_sha256(text)}.mp3")

    # Check if the file exists, if not, request and save the audio
    if not os.path.exists(filename):
        response = requests.post(url, json=data, headers=headers)
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

    return filename

def file_to_data_url(file_path):
    """Convert a file to its corresponding data URL."""
    ext = os.path.splitext(file_path)[1][1:]  # Extract file extension without dot
    with open(file_path, "rb") as f:
        data = f.read()
        base64_data = base64.b64encode(data).decode()
        return f"data:audio/{ext};base64,{base64_data}"

st.title("Help prompt the user")

# UI input
memory_span = st.number_input("Memory Span")

start_speaking = st.button("Start Speaking")

if start_speaking:
    while True:
        audio_file_path = create_audio_file(f"All things are good")
        data_url = file_to_data_url(audio_file_path)
        html_string = f"<audio controls autoplay><source src='{data_url}' type='audio/mp3'></audio>"
        sound = st.empty()
        sound.markdown(html_string, unsafe_allow_html=True)
        time.sleep(2)
        sound.empty()
