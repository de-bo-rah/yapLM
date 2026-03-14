import asyncio
import os
import shutil
import tempfile

from flask import Flask, after_this_request, render_template, request, send_file
from PyPDF2 import PdfReader
from werkzeug.utils import secure_filename

from podcast_core import build_podcast_from_text


app = Flask(__name__)
app.config["MAX_CONTENT_LENGTH"] = 20 * 1024 * 1024


def extract_text_from_pdf(file_path):
    reader = PdfReader(file_path)
    parts = []
    for page in reader.pages:
        page_text = page.extract_text() or ""
        parts.append(page_text)
    return "\n".join(parts).strip()


@app.route("/", methods=["GET"])
def index():
    return render_template("index.html", error=None)


@app.route("/generate", methods=["POST"])
def generate():
    gemini_api_key = os.getenv("GEMINI_API_KEY", "").strip()
    if not gemini_api_key:
        return render_template(
            "index.html",
            error=(
                "Server is missing GEMINI_API_KEY. "
                "Set it as an environment variable before running the app."
            ),
        )

    file = request.files.get("pdf")
    if not file or file.filename == "":
        return render_template("index.html", error="Please upload a PDF file.")
    if not file.filename.lower().endswith(".pdf"):
        return render_template("index.html", error="Only PDF files are supported.")

    speaker1 = (request.form.get("speaker1") or "Elliott").strip()
    speaker2 = (request.form.get("speaker2") or "Clementine").strip()
    lang = (request.form.get("lang") or "English").strip()
    voice1 = (request.form.get("voice1") or "en-US-GuyNeural").strip()
    voice2 = (request.form.get("voice2") or "en-US-JennyNeural").strip()
    voice_map = {speaker1: voice1, speaker2: voice2}
    model = (request.form.get("model") or "gemini-2.5-flash").strip()

    tmpdir = tempfile.mkdtemp()

    @after_this_request
    def cleanup(response):
        shutil.rmtree(tmpdir, ignore_errors=True)
        return response

    filename = secure_filename(file.filename) or "input.pdf"
    pdf_path = os.path.join(tmpdir, filename)
    file.save(pdf_path)

    text = extract_text_from_pdf(pdf_path)
    if not text:
        return render_template(
            "index.html", error="Could not extract any text from that PDF."
        )

    output_path = os.path.join(tmpdir, "final_output.mp3")
    try:
        asyncio.run(
            build_podcast_from_text(
                text,
                api_key=gemini_api_key,
                output_path=output_path,
                speaker1=speaker1,
                speaker2=speaker2,
                lang=lang,
                voice_map=voice_map,
                model=model,
            )
        )
    except Exception as exc:
        return render_template(
            "index.html",
            error=f"Podcast generation failed: {exc}",
        )

    return send_file(
        output_path,
        as_attachment=True,
        download_name="final_output.mp3",
        mimetype="audio/mpeg",
    )


if __name__ == "__main__":
    app.run(debug=True)
