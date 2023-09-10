# streamlit-custom-component

Streamlit component that allows you to convert text to speech and autoplay the audio directly.

## Installation instructions

```sh
pip install streamlit-TTS
```

## Usage instructions

```python
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
```