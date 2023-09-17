# app.py
import requests
import os
import pygame
import openai
import hashlib
import streamlit as st
import time
import base64
from mutagen.mp3 import MP3
import json
from datetime import datetime, timedelta

ELEVEN_LABS_API_KEY = os.environ['ELEVEN_LABS_API_KEY']
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
# MODEL_NAME = 'gpt-3.5-turbo'
MODEL_NAME = 'gpt-4'
# VOICE_ID = "LcfcDJNUP1GQjkzn1xUU" # Emily
# VOICE_ID = "zcAOhNBS3c14rBihAFp1" # swedish
VOICE_ID = "oM29XZNJ7O9aApNNeSVY" # Paul
CHUNK_SIZE = 1024


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
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{VOICE_ID}"

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

def get_text_from_time(input_time):
    # Load the prompts from the JSON file
    with open('prompts.json', 'r') as file:
        prompts = json.load(file)

    # Convert the list of dictionaries into a single dictionary
    # with the time as the key and the message as the value
    time_message_dict = {entry['time']: entry['message'] for entry in prompts}

    # Iterate through the dictionary keys to find the corresponding message
    for time, prompt in time_message_dict.items():
        # if the input time is less than or equal to the current time in the iteration, return the corresponding prompt
        if input_time <= time:
            return prompt
    
    # Return a default message if the input time doesn't match any key in the dictionary
    return "Time not found in predefined prompts."

# Example

print("Creating audio file")

st.title("Lethelink AI")

# UI input
memory_window = st.number_input("Memory Span (minutes)")
schedule = st.text_area("Schedule")
context = st.text_area("Context")

start_speaking = st.button("Start Speaking")

def call_chatgpt(content):
    # Make sure the 'audio' folder exists
    if not os.path.exists('prompts'):
        os.makedirs('prompts')
    filename = os.path.join('prompts', f"{get_sha256(content)}).txt")
    result = ''
    if os.path.exists(filename):
        print("Loading completion from file: ", filename)
        with open(filename, 'r') as f:
            result = f.read()
    else:
        print("Calling chatGPT: ", content)
        completion = openai.ChatCompletion.create(model=MODEL_NAME, messages=[{
            "role": "user", 
            "content": content}])
        result = completion.choices[0].message.content
        print("Writing completion to file: ", result)
        with open(filename, 'w') as f:
            f.write(result)

    print("returning result: ", result)
    return result

call_chatgpt("Hello how are you?")

def generate_intervals(n, start_time='6:00am', end_time='8:00am'):
    # Convert start and end times to datetime objects
    start = datetime.strptime(start_time, '%I:%M%p')
    end = datetime.strptime(end_time, '%I:%M%p')
    
    intervals = []
    current_time = start

    while current_time <= end:
        intervals.append(current_time.strftime('%I:%M%p').lstrip('0'))  # Format and remove leading zeros
        current_time += timedelta(minutes=n)

    return intervals

def generate_nudge(time, schedule, context):
    prompt = "You are Paul, the son of Ann, an 86 year old woman with Alzheimer's. Given the context, today's schedule, and the current time, provide a soothing reminder that will help Ann orient in time and space. Keep the reminder under 3 sentences long. For example “Mom, you are at the AGI house, you are safe and everything is fine. I'm presenting inside right now, I will come and get you soon. We will have lunch soon. "
    return call_chatgpt(f"{prompt} time: {time} schedule: {schedule} context: {context}")

# Generate an interval to prompt the user every n minutes
# times = generate_intervals(memory_window)

times = ['11:45am', '6:30pm']

if start_speaking:
    current_time = st.title(f"Current time: {times[0]}")
    for time_str in times:
        current_time.empty()
        current_time = st.title(f"Current time: {time_str}")
        text = generate_nudge(time_str, schedule, context)
        # text = get_text_from_time(time_str)
        audio_file_path = create_audio_file(text)
        audio_length = get_audio_length(audio_file_path)
        data_url = file_to_data_url(audio_file_path)
        html_string = f"<audio controls autoplay><source src='{data_url}' type='audio/mp3'></audio>"
        sound = st.empty()
        sound.markdown(html_string, unsafe_allow_html=True)
        print(f"duration {int(audio_length) + 1}")
        time.sleep(int(audio_length) + 1)  # Adding 1 second to ensure the audio finishes playing
        sound.empty()
        # time.sleep(memory_window * 60)