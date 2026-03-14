import asyncio
import os

from podcast_core import build_podcast_from_text

# Gemini API key
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")

# Voice mapping
voice_map = {
    "Ava": "en-US-AvaMultilingualNeural",
    "Andrew": "en-US-AndrewMultilingualNeural",
}

# Read the input content from content.txt
print("Reading input content from 'content.txt'...")
with open("content.txt", "r") as file:
    text_input = file.read().strip()

async def main():
    await build_podcast_from_text(
        text_input,
        api_key=GEMINI_API_KEY,
        output_path="final_output.mp3",
        speaker1="Ava",
        speaker2="Andrew",
        lang="English",
        voice_map=voice_map,
        ssml_output_path="SSML.txt",
        model="gemini-2.5-flash",
    )


asyncio.run(main())
