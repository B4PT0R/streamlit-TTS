# streamlit-TTS

Streamlit component providing tools to convert text to speech and autoplay audio directly in the browser without any visible UI elements.

## Features

- **UI-less Audio Autoplay**: Plays audio invisibly without disrupting your app's layout
- **Cross-Browser Compatibility**: Robust autoplay with fallback strategies for Chrome, Safari, Firefox, and mobile browsers
- **Dual TTS Engines**: Support for both Google TTS (gTTS) and OpenAI TTS
- **Smart Text Cleanup**: Automatically removes markdown, LaTeX, code snippets, and URLs before synthesis
- **Type-Safe**: Full type hints for better IDE support and code quality

## Installation

```sh
pip install streamlit-TTS
```

## API Reference

Five main functions are provided:

### 1. `auto_play(audio, wait=True, lag=0.25, key=None)`

Plays audio directly in the browser without showing any UI element.

**Parameters:**
- `audio` (Optional[Dict]): Audio dictionary with keys `'bytes'`, `'sample_rate'`, and `'sample_width'`, or `None`
- `wait` (bool): If True, blocks execution until audio finishes playing (default: True)
- `lag` (float): Additional wait time in seconds to account for network latency (default: 0.25)
- `key` (Optional[str]): Unique key for the component

**Audio Dictionary Format:**
```python
audio = {
    'bytes': bytes,              # WAV audio bytes
    'sample_rate': int,          # Sample rate (e.g., 44100)
    'sample_width': int,         # Sample width in bytes (e.g., 2)
}
```

**Example:**
```python
from streamlit_TTS import auto_play
auto_play(audio_dict, wait=True)
```

### 2. `text_to_audio(text, language='en', cleanup_hook=None)`

Converts text to audio using Google Text-to-Speech (gTTS).

**Parameters:**
- `text` (str): The text to convert to speech
- `language` (str): Language code (e.g., 'en', 'fr', 'es') (default: 'en')
- `cleanup_hook` (Optional[Callable]): Custom text cleaning function (default: built-in cleanup)

**Returns:** Audio dictionary or None if text is empty

**Example:**
```python
from streamlit_TTS import text_to_audio
audio = text_to_audio("Hello world!", language='en')
```

### 3. `text_to_speech(text, language='en', wait=True, lag=0.25, key=None)`

Convenience function combining `text_to_audio()` and `auto_play()` using Google TTS.

**Parameters:**
- `text` (str): The text to convert to speech
- `language` (str): Language code (default: 'en')
- `wait` (bool): If True, blocks until audio finishes (default: True)
- `lag` (float): Additional wait time in seconds (default: 0.25)
- `key` (Optional[str]): Unique key for the component

**Example:**
```python
from streamlit_TTS import text_to_speech
text_to_speech("Welcome to my app!", language='en')
```

### 4. `openai_text_to_audio(text, openai_api_key=None, language=None, cleanup_hook=None, voice='shimmer', model='gpt-4o-mini-tts')`

Converts text to audio using OpenAI's Text-to-Speech API.

**Parameters:**
- `text` (str): The text to convert to speech
- `openai_api_key` (Optional[str]): OpenAI API key (uses `OPENAI_API_KEY` env var if not provided)
- `language` (Optional[str]): Language code (currently unused by OpenAI API)
- `cleanup_hook` (Optional[Callable]): Custom text cleaning function
- `voice` (str): Voice name - 'alloy', 'echo', 'fable', 'onyx', 'nova', or 'shimmer' (default: 'shimmer')
- `model` (str): Model to use - 'gpt-4o-mini-tts', 'gpt-4o-audio-preview', 'tts-1', or 'tts-1-hd' (default: 'gpt-4o-mini-tts')

**Returns:** Audio dictionary or None if text is empty

**Example:**
```python
from streamlit_TTS import openai_text_to_audio
audio = openai_text_to_audio("Hello!", voice='nova', model='gpt-4o-mini-tts')
```

### 5. `openai_text_to_speech(text, language=None, wait=True, lag=0.25, key=None, voice='shimmer', model='gpt-4o-mini-tts')`

Convenience function combining `openai_text_to_audio()` and `auto_play()`.

**Parameters:**
- `text` (str): The text to convert to speech
- `language` (Optional[str]): Language code (currently unused)
- `wait` (bool): If True, blocks until audio finishes (default: True)
- `lag` (float): Additional wait time in seconds (default: 0.25)
- `key` (Optional[str]): Unique key for the component
- `voice` (str): Voice name (default: 'shimmer')
- `model` (str): Model to use (default: 'gpt-4o-mini-tts')

**Example:**
```python
from streamlit_TTS import openai_text_to_speech
openai_text_to_speech("Welcome!", voice='nova')


```

## Examples

### Basic Usage (Google TTS)

```python
import streamlit as st
from streamlit_TTS import text_to_speech

# Simple text-to-speech
text_to_speech("Hello! Welcome to my Streamlit app!", language='en')

# With user input
text = st.text_input("Enter text to speak:")
if st.button("Speak") and text:
    text_to_speech(text, language='en')
```

### Using OpenAI TTS

```python
import streamlit as st
from streamlit_TTS import openai_text_to_speech
import os

# Set your OpenAI API key
os.environ['OPENAI_API_KEY'] = 'your-api-key-here'

# Use OpenAI TTS with different voices
voice = st.selectbox("Choose voice", ['alloy', 'echo', 'fable', 'onyx', 'nova', 'shimmer'])
text = st.text_input("Enter text:")

if st.button("Speak") and text:
    openai_text_to_speech(text, voice=voice, model='gpt-4o-mini-tts')
```

### Advanced Usage with Custom Cleanup

```python
import streamlit as st
from streamlit_TTS import text_to_audio, auto_play

# Custom text cleanup function
def my_cleanup(text):
    # Remove specific patterns
    text = text.replace("[SPEAKER]", "")
    return text.strip()

# Generate audio with custom cleanup
audio = text_to_audio(
    "Some text with [SPEAKER] tags",
    language='en',
    cleanup_hook=my_cleanup
)

# Play the audio
if audio:
    auto_play(audio, wait=True, lag=0.5)
```

### Multi-Language Example

```python
import streamlit as st
from streamlit_TTS import text_to_speech
from gtts.lang import tts_langs

# Get available languages
langs = tts_langs()

# Welcome message
text_to_speech(
    "Choose a language, type some text, and click 'Speak it out!'",
    language='en'
)

# Language selection
lang = st.selectbox("Choose a language", options=list(langs.keys()))
text = st.text_input("Enter text to speak:")

if st.button("Speak it out!") and lang and text:
    text_to_speech(text=text, language=lang)
```

## Browser Compatibility

This component includes robust autoplay with fallback strategies for maximum browser compatibility:

- ✅ Chrome (Desktop & Mobile)
- ✅ Safari (Desktop & Mobile)
- ✅ Firefox
- ✅ Edge
- ✅ Opera

The component automatically handles browser autoplay restrictions with multiple fallback strategies.

## Requirements

- Python >= 3.7
- streamlit >= 0.63
- gtts
- pydub
- openai (optional, for OpenAI TTS features)

## License

MIT