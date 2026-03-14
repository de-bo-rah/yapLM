# yapLM

Generate a detailed, two-speaker podcast from a PDF or plain text using Gemini + Edge TTS.

## Requirements
- Python 3.8 or higher
- A Gemini API key to generate the conversational dialogue
- [EdgeTTS](https://pypi.org/project/edge-tts/) to generate text-to-speech
- [Pydub](https://pypi.org/project/pydub/) to make the final MP3

## Installation

### macOS/Linux

1. **Clone the repository:**
```
git clone https://github.com/de-bo-rah/yapLM.git
cd yapLM
```

2. **Create a virtual environment:**
```
python3 -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**
```
pip install -r requirements.txt
```

### Windows

1. **Clone the repository:**
```
git clone https://github.com/de-bo-rah/yapLM.git
cd yapLM
```

2. **Create a virtual environment:**
```
python -m venv venv
venv\Scripts\activate
```

3. **Install dependencies:**
```
pip install -r requirements.txt
```

## Usage (CLI)

Set your Gemini API key:
```
setx GEMINI_API_KEY "your-gemini-api-key"
```

Prepare your input:
Create a `content.txt` file with the text you want to turn into a podcast.

Run the script:
```
python podcast_script.py
```

## Web App (PDF to Podcast)

1. **Set your Gemini API key:**
```
setx GEMINI_API_KEY "your-gemini-api-key"
```

2. **Run the web app:**
```
python app.py
```

3. **Open the app:**
Visit `http://127.0.0.1:5000` and upload a PDF.

### Notes for the web app
- `pydub` requires `ffmpeg` installed and available on your PATH.
- Large PDFs can take several minutes to process.

## Output
The script generates SSML, synthesizes speech, and combines the segments into `final_output.mp3`.

## Customization

Change speakers and language by editing the fields in the web UI, or update defaults in `app.py`:
```
speaker1 = "Elliott"
speaker2 = "Clementine"
lang = "English"
```

Change Edge TTS voices by editing the `voice_map` defaults:
```
voice_map = {
    "Elliott": "en-US-GuyNeural",
    "Clementine": "en-US-JennyNeural"
}
```

### Gemini notes
You can change the model in the web UI (default: `gemini-2.5-flash`).
