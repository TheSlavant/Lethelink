# app.py
import requests
import os
import pygame
import hashlib
import streamlit as st

def get_sha256(text):
    """Compute the SHA-256 hash of the text and return it."""
    return hashlib.sha256(text.encode()).hexdigest()

def speak_text(text):
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

st.title("Retrograde Window Audio Player")

# UI input
memory_span = st.number_input("Memory Span")

if st.button("Play Audio"):
    audio_file = speak_text(f"You entered retrograde window value: {memory_span}")
    st.audio(audio_file, format='audio/mp3')

if __name__ == "__main__":
    st.write("Enter a number for the retrograde window and press 'Play Audio' to hear it.")
