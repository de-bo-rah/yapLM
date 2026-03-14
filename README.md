# AI Podcast Generator

This script generates an AI-powered podcast based on a given text.
It transforms a conversation between two AI personalities into a fully synthesized audio file. You can customize the speakers, language, and voices for your podcast.
Inspired by the audio overview option of Google's [NotebookLM](https://notebooklm.google.com) experiment, and inspired by [AnthusAI/Podcastic](https://github.com/AnthusAI/Podcastic) to make a script of it.

![Animated gif of the script in action](https://github.com/user-attachments/assets/46139154-0a4a-4491-89a4-5ea3984985a3)


  
## Requirements
Before running the script, make sure you have the following installed/configured:

- Python 3.8 or higher
- A Gemini API key to generate the conversational dialogues
- [EdgeTTS](https://pypi.org/project/edge-tts/) to generate the Text to speech
- [Pydub](https://pypi.org/project/pydub/) to make the final output mp3

## Installation

### macOS/Linux

1. **Clone the repository:**
   ```
   git clone https://github.com/timonvanhasselt/AI-podcast-generator.git
   cd ai-podcast-generator
   ```

2. **Create a virtual environment:**
```
python3 -m venv venv
source venv/bin/activate
```

3. **Install the required Python packages:**
`pip install -r requirements.txt`

### Windows
1. **Clone the repository:**
```git clone https://github.com/timonvanhasselt/AI-podcast-generator.git
cd ai-podcast-generator
```
2. **Create a virtual environment:**

```
python -m venv venv
venv\Scripts\activate
```

3. **Install the required Python packages:**

`pip install -r requirements.txt`

### Usage

Set your Gemini API key as an environment variable:
```
setx GEMINI_API_KEY "your-gemini-api-key"
```

**Prepare your input:** 
The script reads text input from a file named content.txt. 
Create a content.txt file in the project directory and input the text you want to be transformed into dialogue.

**Run the script:** 
Once everything is set up, you can run the script as follows:

**On macOS/Linux:**
`python3 podcast_script.py`

**On Windows:**
`python podcast_script.py`

## Web App (PDF to Podcast)

This project now includes a simple Flask web app so anyone can upload a PDF and receive a podcast MP3.

1. **Set your Gemini API key as an environment variable:**
```
setx GEMINI_API_KEY "your-gemini-api-key"
```

2. **Run the web app:**
```
python app.py
```

3. **Open the app in your browser:**
Visit `http://127.0.0.1:5000` and upload a PDF.

### Notes for the web app
- `pydub` requires `ffmpeg` installed and available on your PATH.
- Large PDFs can take several minutes to process.


### Output
The script will generate an SSML conversation between the speakers, convert it into speech, and combine the segments into a final MP3 file named final_output.mp3.

### Gemini notes
You can change the model in the web UI (default: `gemini-2.5-flash`).

### Customization

**Change Speakers and Language**
You can customize the speakers and their voices by modifying the following variables in the script:

```
speaker1 = "Ava"  # Change to your preferred speaker name
speaker2 = "Andrew"  # Change to your preferred speaker name
lang = "English"  # Change to your preferred language
```

You can also map different voices using EdgeTTS by updating the voice_map dictionary:

```
voice_map = {
    "Ava": "en-US-AvaMultilingualNeural",  # Change to your desired voice from EdgeTTS
    "Andrew": "en-US-AndrewMultilingualNeural"
}
```


### Notes
Make sure you are logged into Hugging Face and have the proper credentials for API access.
If you encounter any issues with model overload, wait and try again later.
