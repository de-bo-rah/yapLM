# yapLM

YapLM helps you create a yap session ( podcast if you prefer ) with two speakers ( inspired by notebooklm ) based on any pdf you plug in so you can summarise any complex topic into a fun little audio file

## Tech Stack
- Language: Python 3.8+

- LLM: [Google Gemini](https://ai.google.dev/) API (Default: gemini-1.5-flash)

- Speech: [EdgeTTS](https://pypi.org/project/edge-tts/) (Microsoft Edge Neural Voices)

- Audio Processing: [Pydub](https://pypi.org/project/pydub/) (requires FFmpeg)

- Web Framework: [Flask](https://flask.palletsprojects.com/)


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

Run the script:
```
python podcast_script.py
```

## Web App 

1. **Set your Gemini API key:**
```
$env:GEMINI_API_KEY = "your_api_key"
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

Fine-tune voice realism by adjusting rate and pitch in the web UI:
```
rate = "+0%"
pitch = "+0Hz"
```

### Gemini notes
You can change the model in the web UI (default: `gemini-2.5-flash`).
