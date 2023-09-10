import os
import base64
import streamlit.components.v1 as components
from gtts import gTTS
import io
from pydub import AudioSegment

_RELEASE = False

if not _RELEASE:
    _component_func = components.declare_component("component",url="http://localhost:3001")
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend-react/build")
    _component_func = components.declare_component("component", path=build_dir)

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
    audio = AudioSegment.from_file(mp3_buffer,format="mp3")

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
    from streamlit_mic_recorder import mic_recorder, speech_to_text
    from deep_translator import GoogleTranslator

    st.subheader("Traduction voix / texte")

    source=st.text_input("Choissez une langue source:",'en')
    dest=st.text_input("Choissez une langue de destination:",'en')

    st.markdown("----")

    st.write("Enregistrez votre voix:")
    spoken_text=speech_to_text(language=source, just_once=True)

    st.write("Ou entrez du texte à traduire:")

    written_text=st.text_input("")

    st.markdown("----")

    with_sound=st.checkbox("Avec son")
    with_text=st.checkbox("Avec texte")

    if spoken_text:
        text=spoken_text
    elif written_text:
        text=written_text
    else:
        text=None
    
    
    if text:
        translated = GoogleTranslator(source=source, target=dest).translate(text)
        if with_text:
            st.markdown("----")
            st.write("Texte traduit:")
            st.write(translated)
        if with_sound:
            text_to_speech(text=translated,language=dest)

