# yapLM

yapLM ( inspired by NotebookLM ) helps you prepare a yap session ( podcast if you prefer ) based on any pdf you plug in so that you can break down complex topics into a fun little audio file.

## How it gets done ?

### Document Preprocessing
- the app uses [PyPDF2](https://pypdf2.readthedocs.io/en/3.x/) for text extraction from the uploaded pdf
- the pdf reader loads the pdf and loops through each page
- all the page texts are appended together + basic normalization

### Forming the context window
- the text is split first to paragraphs ( target size ~ 1200 chars )
- if it exceeds the target size, the paragraph is split into sentences
- an overlap of 200 chars is maintained from previous chunk to the next

### Lexical Retrieval 
- the chunks are vectorized using [TF-IDF](https://scikit-learn.org/stable/modules/generated/sklearn.feature_extraction.text.TfidfVectorizer.html)
- the user's query is embedded in the same vector space
- cosine similarity is used to rank chunks and use the top k 

### RAG grounding ( if enabled )
- the retrieved chunks are appended to the prompt
- the prompt explicitly states the model to use the top k chunks
- here's a nice [article](https://towardsdatascience.com/5-techniques-to-prevent-hallucinations-in-your-rag-question-answering/)

### SSML generation + TTS
- the dialogue generated is converted to SSML and Edge TTS is used to convert the text to speech
- prosody controls : rate/ pitch
- all the segments are concatenated into a final mp3 audio file






## Tech Stack
- Python 3.8+
- Gemini API key 
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


## Web App (PDF to Podcast)

1. **Set your Gemini API key:**
```
setx GEMINI_API_KEY "your-gemini-api-key"
```
For a single PowerShell session, you can also use:
```
$env:GEMINI_API_KEY = "your-gemini-api-key"
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
- Use **Podcast length** to control how detailed the script is.
- Use **Ask a question** to add a focused Q&A segment grounded in the PDF.

## Output
The script generates SSML, synthesizes speech, and combines the segments into `final_output.mp3`.

## Features

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

