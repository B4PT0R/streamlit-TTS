from pathlib import Path

import setuptools

this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

setuptools.setup(
    name="streamlit_TTS",
    version="0.0.2",
    author="Baptiste Ferrand",
    author_email="bferrand.maths@gmail.com.com",
    description="Streamlit component that allows to convert text to speech and play it directly in the browser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/B4PT0R/streamlit-TTS",
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires=">=3.7",
    install_requires=[
        # By definition, a Custom Component depends on Streamlit.
        # If your component has other Python dependencies, list
        # them here.
        "streamlit >= 0.63",
        "pydub",
        "gtts"
    ],
)
