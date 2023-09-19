# Lethelink

## Installation

1. Create an account at [elevenlabs](https://elevenlabs.io/) and [OpenAI](https://platform.openai.com/overview)

Set the following environment variables `ELEVEN_LABS_API_KEY` and `OPENAI_API_KEY`.

The `ELEVEN_LABS_API_KEY` should be the API key that you generated from https://elevenlabs.io/

The `OPENAI_API_KEY` is the API key generated api openAI.  If this is not set, this will not work.

2. Set the VOICE_ID variable.  In the `main.py` file, the VOICE_ID for "Emily" is used.  This is a default voice created by elevenlabs.  If you want a different voice, you will need to set a different one.

3. Install needed dependencies

```
pip install openai
pip install streamlit
pip install mutagen
pip install requests
```

4. Run the App

The app is ran with streamlit.  To run

```
streamlit run main.py
```

It should be running by default at http://localhost:8501