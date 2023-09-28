import os
import time
import json
import streamlit as st
import dotenv
from utils import create_audio_file, file_to_data_url, get_audio_length, call_chatgpt

dotenv.load_dotenv()
ELEVEN_LABS_API_KEY = os.getenv("ELEVEN_LABS_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
VOICE_ID = "LcfcDJNUP1GQjkzn1xUU"
MODEL = 'gpt-4'

def generate_nudge(time, schedule, context):
    # INSERT YOUR PROMPT HERE
    prompt = ("You are Ivan, the son of Maria, an 86 year old woman with Alzheimer's. "
              "Given the context, today's schedule, and the current time, provide a soothing reminder that will "
              "help Maria orient in time and space. Keep the reminder under 3 sentences long. For example “Mom, you "
              "are at the AGI house, you are safe and everything is fine. I'm presenting inside right now, I will "
              "come and get you soon. ")
    return call_chatgpt(f"{prompt} time: {time} schedule: {schedule} context: {context}", OPENAI_API_KEY, MODEL)


def display_ui():
    """Render Streamlit UI elements."""
    st.title("Lethelink AI")
    
    # CAREGIVER PROVIDES CONTEXT HERE
    context = st.text_area("Context")
    schedule = st.text_area("Schedule")
    time_str = st.text_input("Current Time")
    

    if st.button("Create Anchor"):
        text = generate_nudge(time_str, schedule, context)
        audio_file_path = create_audio_file(text, ELEVEN_LABS_API_KEY, VOICE_ID)
        audio_length = get_audio_length(audio_file_path)
        data_url = file_to_data_url(audio_file_path)
        html_string = f"<audio controls autoplay><source src='{data_url}' type='audio/mp3'></audio>"
        sound = st.empty()
        sound.markdown(html_string, unsafe_allow_html=True)
        time.sleep(int(audio_length) + 1)
        sound.empty()


def main():
    display_ui()


if __name__ == '__main__':
    main()
