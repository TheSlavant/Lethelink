import requests
import os
import pygame

def speak_text(text):
    CHUNK_SIZE = 1024
    VOICE_ID = "LcfcDJNUP1GQjkzn1xUU"
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

    # Emily
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

    response = requests.post(url, json=data, headers=headers)
    filename = 'output.mp3'
    with open(filename, 'wb') as f:
        for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
            if chunk:
                f.write(chunk)

    # Play the audio
    pygame.mixer.init()
    pygame.mixer.music.load(filename)
    pygame.mixer.music.play()
    while pygame.mixer.music.get_busy():
        pygame.time.Clock().tick(10)

speak_text("You are at the A. G. I. House.")
speak_text("All things are good")