# app.py
import requests
import os
import pygame
import hashlib
import streamlit as st
import time
import base64
from mutagen.mp3 import MP3

def get_audio_length(file_path):
    """Get the duration of an audio file in seconds."""
    audio = MP3(file_path)
    return audio.info.length

def get_sha256(text):
    """Compute the SHA-256 hash of the text and return it."""
    return hashlib.sha256(text.encode()).hexdigest()

# Given some arbitrary text, create an 
# audio file that can play the text
def create_audio_file(text):
    CHUNK_SIZE = 1024
    # VOICE_ID = "zcAOhNBS3c14rBihAFp1" # swedish
    VOICE_ID = "LcfcDJNUP1GQjkzn1xUU" # Emily
    # VOICE_ID = "oM29XZNJ7O9aApNNeSVY" # Paul
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

    filename = os.path.join('audio', f"{get_sha256(VOICE_ID + text)}.mp3")

    # Check if the file exists, if not, request and save the audio
    if not os.path.exists(filename):
        print("Creating audio file")
        response = requests.post(url, json=data, headers=headers)
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)

    print(f"Returning the audio file {filename} for the text \n{text}")
    return filename

def file_to_data_url(file_path):
    """Convert a file to its corresponding data URL."""
    ext = os.path.splitext(file_path)[1][1:]  # Extract file extension without dot
    with open(file_path, "rb") as f:
        data = f.read()
        base64_data = base64.b64encode(data).decode()
        return f"data:audio/{ext};base64,{base64_data}"

print("Creating audio file")
create_audio_file(f"Hey mom! Everything is ok, you are right where you should be.")

st.title("Help prompt the user")

# UI input
memory_span = st.number_input("Memory Span")

start_speaking = st.button("Start Speaking")

if start_speaking:
    audio_file_path = create_audio_file(f"Hey mom! Everything is ok, you are right where you should be.")
    duration = get_audio_length(audio_file_path)
    data_url = file_to_data_url(audio_file_path)
    html_string = f"<audio controls autoplay><source src='{data_url}' type='audio/mp3'></audio>"
    sound = st.empty()
    sound.markdown(html_string, unsafe_allow_html=True)
    time.sleep(duration + 1)  # Adding 1 second to ensure the audio finishes playing
    sound.empty()