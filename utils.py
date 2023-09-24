import os
import requests
import hashlib
import base64
from mutagen.mp3 import MP3
import openai

CHUNK_SIZE = 1024

def get_sha256(text):
    """
    Compute the SHA-256 hash of the given text.

    Args:
        text (str): The text to hash.

    Returns:
        str: The SHA-256 hash of the text.
    """
    return hashlib.sha256(text.encode()).hexdigest()

def create_audio_file(text, api_key, voice_id="LcfcDJNUP1GQjkzn1xUU"):
    """
    Create an audio file from given text using the Eleven Labs API.

    Args:
        text (str): The text to convert to audio.
        api_key (str): The API key for Eleven Labs.
        voice_id (str): The ID for the desired voice. Default is Emily. If you fine-tune on the caregiver's voice, use that voice ID here.

    Returns:
        str: The path to the created audio file.
    """
    # Endpoint for Eleven Labs text-to-speech API
    url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
    
    # Headers required for the API request
    headers = {
        "Accept": "audio/mpeg",
        "Content-Type": "application/json",
        "xi-api-key": api_key
    }
    
    # Payload data for the request
    data = {
        "text": text,
        "model_id": "eleven_monolingual_v1",
        "voice_settings": {
            "stability": 0.5,
            "similarity_boost": 0.5
        }
    }

    # Determine filename using hash to avoid duplicates
    filename = os.path.join('audio', f"{get_sha256(voice_id + text)}.mp3")
    
    # If the file doesn't exist, request and save the audio
    if not os.path.exists(filename):
        response = requests.post(url, json=data, headers=headers)
        if response.status_code != 200:
            raise ValueError("Failed to generate audio.")
        with open(filename, 'wb') as f:
            for chunk in response.iter_content(chunk_size=CHUNK_SIZE):
                if chunk:
                    f.write(chunk)
    
    return filename

def file_to_data_url(file_path):
    """
    Convert a file to its corresponding data URL.

    Args:
        file_path (str): The path to the file.

    Returns:
        str: The data URL representation of the file.
    """
    # Extract the file extension for MIME type determination
    ext = os.path.splitext(file_path)[1][1:]
    with open(file_path, "rb") as f:
        data = f.read()
        base64_data = base64.b64encode(data).decode()
        return f"data:audio/{ext};base64,{base64_data}"

def get_audio_length(file_path):
    """
    Get the duration of an audio file in seconds.

    Args:
        file_path (str): The path to the audio file.

    Returns:
        float: The duration of the audio file in seconds.
    """
    audio = MP3(file_path)
    return audio.info.length

def call_chatgpt(content, api_key, model_name='gpt-4'):
    """
    Fetch a completion from OpenAI's chatGPT.

    Args:
        content (str): The prompt/content to get a completion for.
        model_name (str): The model to use for the completion.

    Returns:
        str: The completion returned by chatGPT.
    """
    openai.api_key = api_key

    # Determine filename using hash to avoid duplicates
    filename = os.path.join('prompts', f"{get_sha256(content)}.txt")

    # If completion is already saved, read and return it
    if os.path.exists(filename):
        with open(filename, 'r') as f:
            return f.read()
    else:
        # Otherwise, call the API for a new completion
        completion = openai.ChatCompletion.create(model=model_name, messages=[{
            "role": "user", 
            "content": content}])
        result = completion.choices[0].message.content
        
        # Save the completion for future use
        with open(filename, 'w') as f:
            f.write(result)
        return result
