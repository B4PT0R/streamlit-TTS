import os
import base64
import streamlit.components.v1 as components
from gtts import gTTS
import io
from pydub import AudioSegment

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component("streamlit_TTS",url="http://localhost:3001")
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_TTS", path=build_dir)

def auto_play(audio_bytes,key=None):
    audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
    component_value = _component_func(audio_base64=audio_base64,key=key,default=None)
    return component_value 

def text_to_audio(text, language='en'):
    # Create MP3 audio
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

def text_to_speech(text,language='en'):
    audio=text_to_audio(text,language=language)
    auto_play(audio['bytes'])

if not _RELEASE:
    import streamlit as st
    #from streamlit_TTS import auto_play, text_to_speech, text_to_audio

    from gtts.lang import tts_langs

    langs=tts_langs().keys()

    audio=text_to_audio("Choose a language, type some text, and click 'Speak it out!'.",language='en')
    auto_play(audio['bytes'])

    lang=st.selectbox("Choose a language",options=langs)
    text=st.text_input("Choose a text to speak out:")
    speak=st.button("Speak it out!")

    if lang and text and speak:
        text_to_speech(text=text, language=lang)
