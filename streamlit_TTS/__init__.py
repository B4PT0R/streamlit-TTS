"""Streamlit TTS Component - Text-to-speech audio autoplay for Streamlit apps."""

import os
import base64
import io
import time
import re
from typing import Optional, Dict, Callable

import streamlit.components.v1 as components
import streamlit as st
from gtts import gTTS
from pydub import AudioSegment
import dotenv
from openai import OpenAI

_RELEASE = True

if not _RELEASE:
    _component_func = components.declare_component("streamlit_TTS",url="http://localhost:3001")
else:
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    build_dir = os.path.join(parent_dir, "frontend/build")
    _component_func = components.declare_component("streamlit_TTS", path=build_dir)



def cleanup(text: str) -> str:
    """Remove URLs, LaTeX, code snippets, and markdown syntax from text.

    Args:
        text: The input text to clean

    Returns:
        Cleaned text suitable for text-to-speech conversion
    """
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

def auto_play(
    audio: Optional[Dict[str, any]],
    wait: bool = True,
    lag: float = 0.25,
    key: Optional[str] = None
) -> None:
    """Autoplay audio in the Streamlit app without UI.

    Args:
        audio: Dictionary containing 'bytes', 'sample_rate', and 'sample_width' keys,
               or None if no audio to play
        wait: If True, blocks execution until audio finishes playing
        lag: Additional time (seconds) to add after calculated duration when waiting
        key: Optional unique key for the component
    """
    if audio is None:
        return

    try:
        audio_bytes = audio["bytes"]
        sample_rate = audio["sample_rate"]
        sample_width = audio["sample_width"]

        # Calculate duration
        total_samples = len(audio_bytes) / sample_width
        duration = total_samples / sample_rate

        # Encode and play audio
        audio_base64 = base64.b64encode(audio_bytes).decode('utf-8')
        _component_func(audio_base64=audio_base64, key=key, default=None)

        # Wait for audio to finish if requested
        if wait:
            time.sleep(duration + lag)
    except (KeyError, TypeError, ZeroDivisionError) as e:
        st.error(f"Error playing audio: {e}")

def text_to_audio(
    text: str,
    language: str = 'en',
    cleanup_hook: Optional[Callable[[str], str]] = None
) -> Optional[Dict[str, any]]:
    """Convert text to audio using Google Text-to-Speech.

    Args:
        text: The text to convert to speech
        language: Language code (e.g., 'en', 'fr', 'es')
        cleanup_hook: Optional custom function to clean text before conversion

    Returns:
        Dictionary with 'bytes', 'sample_rate', and 'sample_width' keys, or None if text is empty
    """
    try:
        # Clean the text
        clean = cleanup_hook or cleanup
        text = clean(text)

        if not text.strip():
            return None

        # Generate speech with gTTS
        tts = gTTS(text=text, lang=language, slow=False)
        mp3_buffer = io.BytesIO()
        tts.write_to_fp(mp3_buffer)
        mp3_buffer.seek(0)

        # Convert MP3 to WAV and make it mono
        audio = AudioSegment.from_file(mp3_buffer, format="mp3").set_channels(1)

        # Extract audio properties
        sample_rate = audio.frame_rate
        sample_width = audio.sample_width

        # Export audio to WAV in memory buffer
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")

        return {
            "bytes": wav_buffer.getvalue(),
            "sample_rate": sample_rate,
            "sample_width": sample_width
        }
    except Exception as e:
        st.error(f"Error converting text to audio: {e}")
        return None
    
def openai_text_to_audio(
    text: str,
    openai_api_key: Optional[str] = None,
    language: Optional[str] = None,
    cleanup_hook: Optional[Callable[[str], str]] = None,
    voice: str = "shimmer",
    model: str = "gpt-4o-mini-tts"
) -> Optional[Dict[str, any]]:
    """Convert text to audio using OpenAI Text-to-Speech API.

    Args:
        text: The text to convert to speech
        openai_api_key: OpenAI API key (if not provided, uses OPENAI_API_KEY env var)
        language: Language code (currently unused by OpenAI API)
        cleanup_hook: Optional custom function to clean text before conversion
        voice: Voice to use ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer')
        model: Model to use ('gpt-4o-mini-tts', 'gpt-4o-audio-preview', 'tts-1', 'tts-1-hd')

    Returns:
        Dictionary with 'bytes', 'sample_rate', and 'sample_width' keys, or None if text is empty
    """
    try:
        # Initialize OpenAI client if not already done
        if 'openai_client' not in st.session_state:
            dotenv.load_dotenv()
            api_key = openai_api_key or os.getenv('OPENAI_API_KEY')
            if not api_key:
                st.error("OpenAI API key not found. Please provide it or set OPENAI_API_KEY environment variable.")
                return None
            st.session_state.openai_client = OpenAI(api_key=api_key)

        # Clean the text
        clean = cleanup_hook or cleanup
        text = clean(text)

        if not text.strip():
            return None

        client = st.session_state.openai_client
        mp3_buffer = io.BytesIO()

        # Generate speech with OpenAI
        response = client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )

        for chunk in response.iter_bytes():
            mp3_buffer.write(chunk)

        mp3_buffer.seek(0)

        # Convert MP3 to WAV and make it mono
        audio = AudioSegment.from_file(mp3_buffer, format="mp3").set_channels(1)

        # Extract audio properties
        sample_rate = audio.frame_rate
        sample_width = audio.sample_width

        # Export audio to WAV in memory buffer
        wav_buffer = io.BytesIO()
        audio.export(wav_buffer, format="wav")

        return {
            "bytes": wav_buffer.getvalue(),
            "sample_rate": sample_rate,
            "sample_width": sample_width
        }
    except Exception as e:
        st.error(f"Error converting text to audio with OpenAI: {e}")
        return None

def text_to_speech(
    text: str,
    language: str = 'en',
    wait: bool = True,
    lag: float = 0.25,
    key: Optional[str] = None
) -> None:
    """Convert text to speech and autoplay it using Google TTS.

    This is a convenience function that combines text_to_audio() and auto_play().

    Args:
        text: The text to convert to speech
        language: Language code (e.g., 'en', 'fr', 'es')
        wait: If True, blocks execution until audio finishes playing
        lag: Additional time (seconds) to add after calculated duration when waiting
        key: Optional unique key for the component
    """
    audio = text_to_audio(text, language=language)
    auto_play(audio, wait=wait, lag=lag, key=key)


def openai_text_to_speech(
    text: str,
    language: Optional[str] = None,
    wait: bool = True,
    lag: float = 0.25,
    key: Optional[str] = None,
    voice: str = "shimmer",
    model: str = "gpt-4o-mini-tts"
) -> None:
    """Convert text to speech and autoplay it using OpenAI TTS.

    This is a convenience function that combines openai_text_to_audio() and auto_play().

    Args:
        text: The text to convert to speech
        language: Language code (currently unused by OpenAI API)
        wait: If True, blocks execution until audio finishes playing
        lag: Additional time (seconds) to add after calculated duration when waiting
        key: Optional unique key for the component
        voice: Voice to use ('alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer')
        model: Model to use ('gpt-4o-mini-tts', 'gpt-4o-audio-preview', 'tts-1', 'tts-1-hd')
    """
    audio = openai_text_to_audio(text, language=language, voice=voice, model=model)
    auto_play(audio, wait=wait, lag=lag, key=key)

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
