import asyncio
import os
import re
import tempfile
import xml.etree.ElementTree as ET

import edge_tts
from google import genai
from pydub import AudioSegment
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def _add_sentence_breaks(text):
    sentences = [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]
    if len(sentences) <= 1:
        return text.strip()
    return " <break time=\"0.2s\"/> ".join(sentences)


def _length_profile(length_choice):
    choice = (length_choice or "medium").strip().lower()
    profiles = {
        "short": {
            "minutes": "2-3",
            "turns": "6-8",
            "detail": "concise and punchy",
        },
        "medium": {
            "minutes": "5-7",
            "turns": "10-12",
            "detail": "balanced depth with clear explanations",
        },
        "long": {
            "minutes": "10-12",
            "turns": "16-20",
            "detail": "deep and thorough with extra context",
        },
    }
    return profiles.get(choice, profiles["medium"])


def _split_sentences(text):
    return [s.strip() for s in re.split(r"(?<=[.!?])\s+", text) if s.strip()]


def _chunk_text(text, max_chars=1200, overlap=200):
    paragraphs = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    chunks = []
    current = ""

    def flush_chunk(value):
        if value:
            chunks.append(value.strip())

    for para in paragraphs:
        if len(para) > max_chars:
            sentences = _split_sentences(para)
            buf = ""
            for sentence in sentences:
                if len(buf) + len(sentence) + 1 <= max_chars:
                    buf = f"{buf} {sentence}".strip()
                else:
                    flush_chunk(buf)
                    buf = sentence
            flush_chunk(buf)
            continue

        if len(current) + len(para) + 2 <= max_chars:
            current = f"{current}\n\n{para}".strip()
        else:
            flush_chunk(current)
            current = para

    flush_chunk(current)

    if overlap > 0 and len(chunks) > 1:
        overlapped = []
        for idx, chunk in enumerate(chunks):
            if idx == 0:
                overlapped.append(chunk)
                continue
            prev = chunks[idx - 1]
            tail = prev[-overlap:] if len(prev) > overlap else prev
            overlapped.append(f"{tail}\n{chunk}")
        return overlapped

    return chunks


def _build_rag_context(text, query, top_k=6):
    chunks = _chunk_text(text)
    if not chunks:
        return "", []

    safe_query = (query or "").strip()
    if not safe_query:
        safe_query = "main points, key ideas, important details"

    vectorizer = TfidfVectorizer(stop_words="english", max_features=5000)
    chunk_vectors = vectorizer.fit_transform(chunks)
    query_vector = vectorizer.transform([safe_query])
    scores = cosine_similarity(query_vector, chunk_vectors).ravel()
    top_k = max(1, min(int(top_k or 6), len(chunks)))
    top_indices = scores.argsort()[::-1][:top_k]

    sources = []
    for rank, idx in enumerate(top_indices, start=1):
        sources.append((f"CHUNK {rank}", chunks[idx]))

    context_lines = []
    for label, chunk in sources:
        context_lines.append(f"[{label}]\n{chunk}")

    return "\n\n".join(context_lines), sources


def generate_ssml_conversation(
    client,
    text,
    speaker1,
    speaker2,
    lang,
    model,
    length,
    question,
    rag_context=None,
):
    print("Generating SSML conversation...")
    profile = _length_profile(length)
    question_note = ""
    if question:
        question_note = (
            f"Include a focused Q&A segment where {speaker2} asks: '{question}', "
            f"and {speaker1} answers clearly using only information from the source text."
        )
    dialogue_prompt = (
        f"Create a detailed, highly intellectual podcast conversation based on the following text: '{text}'. "
        f"The first person is {speaker1}, and the second person is {speaker2}. They should philosophize and "
        f"intellectualize the content as much as possible while keeping the tone fun and energetic with Gen Z lingo. "
        f"They should affirm each other and include short pauses, but do not include stage directions or actions "
        f"like (smiling) or (pausing). Let {speaker1} introduce the podcast and {speaker2} at the start. "
        f"Keep it insightful yet playful, mixing deep analysis with modern slang, and avoid being cringe. "
        f"Text in {lang}. Aim for ~{profile['minutes']} minutes and about {profile['turns']} total turns. "
        f"Keep the level of detail {profile['detail']}. {question_note}\n\n"
        f"IMPORTANT FORMAT: Return ONLY dialogue lines, each line must start with '{speaker1}:' or '{speaker2}:' exactly."
    )
    if rag_context:
        dialogue_prompt += (
            "\n\nUse ONLY the information in the source chunks below. "
            "If a detail is missing, say 'that's outside the scope of the PDF.'\n\n"
            f"{rag_context}"
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
            content = _add_sentence_breaks(content)
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
            sentence = _add_sentence_breaks(sentence)
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


async def synthesize_text(text, voice_name, voice_map, filename, rate, pitch):
    edge_voice = voice_map.get(voice_name)
    if edge_voice is None:
        raise ValueError(f"Unknown voice name: {voice_name}")
    print(f"Generating audio for voice: {edge_voice}")
    communicate = edge_tts.Communicate(text, voice=edge_voice, rate=rate, pitch=pitch)
    await communicate.save(filename)
    print(f"Audio saved to '{filename}'.")


async def synthesize_segments(segments, voice_map, out_dir, rate, pitch):
    for i, (voice_name, text) in enumerate(segments):
        mp3_filename = os.path.join(out_dir, f"output_segment_{i + 1}.mp3")
        await synthesize_text(text, voice_name, voice_map, mp3_filename, rate, pitch)


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
    rate="+0%",
    pitch="+0Hz",
    ssml_output_path=None,
    model="gemini-2.5-flash",
    length="medium",
    question="",
    rag_enabled=False,
    rag_query="",
    rag_top_k=6,
):
    with tempfile.TemporaryDirectory() as tmpdir:
        client = genai.Client(api_key=api_key) if api_key else genai.Client()
        print("Gemini client ready.")

        rag_context = None
        if rag_enabled:
            rag_context, _ = _build_rag_context(text, rag_query, top_k=rag_top_k)

        ssml_conversation = generate_ssml_conversation(
            client,
            text,
            speaker1=speaker1,
            speaker2=speaker2,
            lang=lang,
            model=model,
            length=length,
            question=question,
            rag_context=rag_context,
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
        await synthesize_segments(segments, voice_map, tmpdir, rate, pitch)
        combine_segments(len(segments), tmpdir, output_path)
