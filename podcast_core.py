import asyncio
import os
import re
import tempfile
import xml.etree.ElementTree as ET

import edge_tts
from google import genai
from pydub import AudioSegment


def generate_ssml_conversation(client, text, speaker1, speaker2, lang, model):
    print("Generating SSML conversation...")
    dialogue_prompt = (
        f"Create a detailed, light-hearted podcast conversation between two people based on the following text: '{text}'. "
        f"The first person is {speaker1}, and the second person is {speaker2}. They should affirm each other "
        f"and include pauses, but do not include stage directions or actions like (smiling) or (pausing). "
        f"Let {speaker1} introduce the podcast and {speaker2} at the start. "
        f"Text in {lang} and at least 10 turns of every speaker.\n\n"
        f"IMPORTANT FORMAT: Return ONLY dialogue lines, each line must start with '{speaker1}:' or '{speaker2}:' exactly."
    )

    try:
        response = client.models.generate_content(
            model=model,
            contents=dialogue_prompt,
        )
        dialogue_text = (response.text or "").strip()
    except Exception as exc:
        print(f"Error: Gemini request failed: {exc}")
        return None

    dialogue_text = re.sub(r"\([^)]*\)", "", dialogue_text).strip()
    ssml_output = "<speak>\n"

    speaker_pattern = re.compile(
        rf"(?m)^\s*({re.escape(speaker1)}|{re.escape(speaker2)})\s*[:\-]\s*"
    )
    matches = list(speaker_pattern.finditer(dialogue_text))

    if matches:
        for idx, match in enumerate(matches):
            speaker = match.group(1)
            start = match.end()
            end = matches[idx + 1].start() if idx + 1 < len(matches) else len(dialogue_text)
            content = dialogue_text[start:end].strip()
            if not content:
                continue
            ssml_output += f'<voice name="{speaker}">\n'
            ssml_output += f"    {content}\n"
            ssml_output += "    <break time=\"0.5s\"/>\n" if speaker == speaker1 else "    <break time=\"0.3s\"/>\n"
            ssml_output += "</voice>\n"
    else:
        # Fallback: split into sentences and alternate speakers so both voices are used.
        sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", dialogue_text) if s.strip()]
        if not sentences:
            sentences = [dialogue_text] if dialogue_text else []
        for i, sentence in enumerate(sentences):
            speaker = speaker1 if i % 2 == 0 else speaker2
            ssml_output += f'<voice name="{speaker}">\n'
            ssml_output += f"    {sentence}\n"
            ssml_output += "    <break time=\"0.5s\"/>\n" if speaker == speaker1 else "    <break time=\"0.3s\"/>\n"
            ssml_output += "</voice>\n"

    ssml_output += "</speak>"
    print("SSML conversation generated successfully.")
    return ssml_output


def parse_ssml(file_path):
    print(f"Parsing SSML from '{file_path}'...")
    tree = ET.parse(file_path)
    root = tree.getroot()
    segments = []

    for elem in root:
        if elem.tag == "voice":
            voice_name = elem.attrib["name"]
            text = "".join(elem.itertext()).strip()
            segments.append((voice_name, text))

    print("SSML parsing completed.")
    return segments


async def synthesize_text(text, voice_name, voice_map, filename, rate):
    edge_voice = voice_map.get(voice_name)
    if edge_voice is None:
        raise ValueError(f"Unknown voice name: {voice_name}")
    print(f"Generating audio for voice: {edge_voice}")
    communicate = edge_tts.Communicate(text, voice=edge_voice, rate=rate)
    await communicate.save(filename)
    print(f"Audio saved to '{filename}'.")


async def synthesize_segments(segments, voice_map, out_dir, rate):
    for i, (voice_name, text) in enumerate(segments):
        mp3_filename = os.path.join(out_dir, f"output_segment_{i + 1}.mp3")
        await synthesize_text(text, voice_name, voice_map, mp3_filename, rate)


def combine_segments(segment_count, out_dir, output_path):
    print("Combining audio segments...")
    combined = AudioSegment.empty()
    for i in range(segment_count):
        mp3_filename = os.path.join(out_dir, f"output_segment_{i + 1}.mp3")
        audio_segment = AudioSegment.from_mp3(mp3_filename)
        combined += audio_segment
    combined.export(output_path, format="mp3")
    print(f"Final audio file '{output_path}' has been created.")


async def build_podcast_from_text(
    text,
    api_key,
    output_path,
    speaker1,
    speaker2,
    lang,
    voice_map,
    rate="+15%",
    ssml_output_path=None,
    model="gemini-2.5-flash",
):
    with tempfile.TemporaryDirectory() as tmpdir:
        client = genai.Client(api_key=api_key) if api_key else genai.Client()
        print("Gemini client ready.")

        ssml_conversation = generate_ssml_conversation(
            client, text, speaker1=speaker1, speaker2=speaker2, lang=lang, model=model
        )
        if ssml_conversation is None:
            raise RuntimeError("SSML generation failed due to Gemini error.")

        ssml_path = os.path.join(tmpdir, "SSML.txt")
        with open(ssml_path, "w", encoding="utf-8") as file:
            file.write(ssml_conversation)

        if ssml_output_path:
            with open(ssml_output_path, "w", encoding="utf-8") as file:
                file.write(ssml_conversation)

        segments = parse_ssml(ssml_path)
        print(f"Found {len(segments)} segments to synthesize.")
        await synthesize_segments(segments, voice_map, tmpdir, rate)
        combine_segments(len(segments), tmpdir, output_path)
