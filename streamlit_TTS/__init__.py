import os
import base64
import streamlit.components.v1 as components
from gtts import gTTS
import io
from pydub import AudioSegment
import time
import streamlit as st
import dotenv
from openai import OpenAI

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component("streamlit_TTS",url="http://localhost:3001")
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_TTS", path=build_dir)



def cleanup(text):
    import re
    # Removes URLs
    text = re.sub(r'http\S+|www.\S+', ' ', text, flags=re.MULTILINE)
    # Removes LaTeX formulas
    text = re.sub(r'\$\$.*?\$\$', ' ', text, flags=re.MULTILINE)
    text = re.sub(r'\$.+?\$', ' ', text, flags=re.MULTILINE)
    # Removes code snippets
    text = re.sub(r'(```.*?```)', ' ', text, flags=re.DOTALL)
    # Removes special characters from markdown syntax
    text = re.sub(r'(\*\*|\*|__|_|>|\"|~~|``|`|#|\[|\]|\(|\)|!\[|\])', ' ', text)
    return text

def auto_play(audio,wait=True,lag=0.25,key=None):
    height_hack = """
<script>
    var hide_me_list = window.parent.document.querySelectorAll('iframe');
    for (let i = 0; i < hide_me_list.length; i++) { 
        if (hide_me_list[i].height == 0) {
            hide_me_list[i].parentNode.style.height = 0;
            hide_me_list[i].parentNode.style.marginBottom = '-1rem';
        };
    };
</script>
"""
    if audio:
        audio_bytes = audio["bytes"]
        sample_rate = audio["sample_rate"]
        sample_width = audio["sample_width"]
        total_samples = len(audio_bytes) / sample_width
        duration = total_samples / sample_rate
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        _component_func(audio_base64=audio_base64,key=key,default=None)
        components.html(height_hack, height=0)
        if wait:
            time.sleep(duration+lag)

def text_to_audio(text, language='en',cleanup_hook=None):
    # Create MP3 audio
    clean= cleanup_hook or cleanup
    text=clean(text)
    if text.strip():
        tts = gTTS(text=text, lang=language, slow=False)
        mp3_buffer = io.BytesIO()
        tts.write_to_fp(mp3_buffer)

        mp3_buffer.seek(0)

        # Convert MP3 to WAV and make it mono
        audio = AudioSegment.from_file(mp3_buffer,format="mp3").set_channels(1)

        # Extract audio properties
        sample_rate = audio.frame_rate
        sample_width = audio.sample_width

        # Export audio to WAV in memory buffer
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")

        # Return the required dictionary
        return {
            "bytes": wav_buffer.getvalue(),
            "sample_rate": sample_rate,
            "sample_width": sample_width
        }
    else:
        return None
    
def openai_text_to_audio(text, openai_api_key=None,language=None,cleanup_hook=None):
    
    if not 'openai_client' in st.session_state:
        dotenv.load_dotenv()
        st.session_state.openai_client=OpenAI(api_key=openai_api_key or os.getenv('OPENAI_API_KEY'))
    
    # Create MP3 audio
    clean= cleanup_hook or cleanup
    text=clean(text)
    if text.strip():

        client=st.session_state.openai_client

        mp3_buffer = io.BytesIO()

        response = client.audio.speech.create(
        model="tts-1",
        voice="shimmer",
        input=text
        )

        for chunk in response.iter_bytes():
            mp3_buffer.write(chunk)

        mp3_buffer.seek(0)

        # Convert MP3 to WAV and make it mono
        audio = AudioSegment.from_file(mp3_buffer,format="mp3").set_channels(1)

        # Extract audio properties
        sample_rate = audio.frame_rate
        sample_width = audio.sample_width

        # Export audio to WAV in memory buffer
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")

        # Return the required dictionary
        return {
            "bytes": wav_buffer.getvalue(),
            "sample_rate": sample_rate,
            "sample_width": sample_width
        }
    else:
        return None

def text_to_speech(text,language='en',wait=True,lag=0.25,key=None):
    audio=text_to_audio(text,language=language)
    auto_play(audio,wait=wait,lag=lag,key=key)

def openai_text_to_speech(text,language=None,wait=True,lag=0.25,key=None):
    audio=openai_text_to_audio(text,language=language)
    auto_play(audio,wait=wait,lag=lag,key=key)

if not _RELEASE:
    import streamlit as st
    #from streamlit_TTS import auto_play, text_to_speech, text_to_audio

    from gtts.lang import tts_langs

    langs=tts_langs().keys()

    audio=text_to_audio("Choose a language, type some text, and click 'Speak it out!'.",language='en')
    auto_play(audio)

    lang=st.selectbox("Choose a language",options=langs)
    text=st.text_input("Choose a text to speak out:")
    speak=st.button("Speak it out!")

    if lang and text and speak:
        text_to_speech(text=text, language=lang)
