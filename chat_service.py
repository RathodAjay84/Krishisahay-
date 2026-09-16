"""Chat, voice, and lightweight conversation storage for KrishiSahay."""

from __future__ import annotations

import html
import io
import json
import os
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

CHAT_LOG_PATH = Path(__file__).with_name("chat_history.json")


def timestamp() -> str:
    """Return a short local timestamp for chat messages."""
    return datetime.now().strftime("%d %b %Y, %I:%M %p")


def transcribe_audio(audio_file) -> str:
    """Transcribe browser-recorded WAV audio without requiring PyAudio."""
    try:
        import speech_recognition as sr
    except ImportError as error:
        raise RuntimeError("SpeechRecognition is not installed") from error

    recognizer = sr.Recognizer()
    with sr.AudioFile(io.BytesIO(audio_file.getvalue())) as source:
        recording = recognizer.record(source)
    return recognizer.recognize_google(recording).strip()


def record_chat_message(role: str, content: str) -> None:
    """Append a compact conversation record to the local JSON history."""
    record = {"role": role, "content": content, "timestamp": timestamp()}
    try:
        history = []
        if CHAT_LOG_PATH.exists():
            history = json.loads(CHAT_LOG_PATH.read_text(encoding="utf-8"))
        history.append(record)
        CHAT_LOG_PATH.write_text(
            json.dumps(history[-200:], ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
    except (OSError, ValueError):
        # Chat should still work if the local folder is read-only or the log is invalid.
        return


def _offline_answer(prompt: str) -> str:
    """Provide concise agriculture guidance when Gemini is not configured."""
    question = prompt.lower()
    if any(word in question for word in ("hello", "hi", "namaste")):
        return "Namaste! I can help with crops, soil, fertilizer, pests, disease, weather, irrigation, schemes, and market planning."
    if question.strip() in {"what is crop", "what is a crop", "define crop", "crop meaning"}:
        return "A **crop** is a plant grown for food, feed, fibre, medicine, or sale. Crop choice depends on soil, season, rainfall, irrigation, temperature, and market demand."
    if "weather" in question:
        return "Live weather needs a `WEATHER_API` key. Until it is configured, check the local forecast before irrigation or spraying and avoid field work during extreme heat."
    if "crop" in question and any(word in question for word in ("recommend", "suggest", "best")):
        return "For Telangana, Kharif options commonly include paddy, cotton, and maize; Rabi options include wheat, chickpea, and maize. Share your soil, season, rainfall, and irrigation access for a specific recommendation."
    if any(word in question for word in ("fertilizer", "urea", "npk")):
        return "Use a soil test before selecting fertilizer. Apply nitrogen in split doses, keep phosphorus near the root zone, and do not apply urea immediately before heavy rain. Share the crop and N-P-K values for a more specific plan."
    if any(word in question for word in ("pest", "disease", "insect", "worm")):
        return "Start with integrated pest management: inspect leaves and stems, remove severely affected parts, use traps or neem-based methods where suitable, and apply only a label-approved product after confirming the pest."
    if "paddy" in question or "rice" in question:
        return "For paddy, manage standing water carefully and confirm fertilizer with a soil test. A common Telangana reference is NPK 120:60:60 kg/ha. Scout for stem borer before choosing any treatment."
    if "cotton" in question:
        return "For cotton, scout squares and bolls for pink bollworm, use pheromone traps and field sanitation, and apply only a locally approved product at the label dose after confirming the pest."
    if "chili" in question or "chilli" in question:
        return "For chilli, inspect new leaves and flowers for thrips. Blue sticky traps, field sanitation, and approved neem-based options can support integrated pest management."
    if "soil" in question:
        return "Black soil commonly supports cotton, soybean, and wheat; red soil can suit groundnut and millets; sandy soil can suit watermelon and sweet potato. Confirm with soil testing and water availability."
    if "irrigat" in question or "water" in question:
        return "Drip irrigation reduces water loss compared with flood irrigation. Check root-zone moisture before watering, irrigate in cooler hours, and use mulch to reduce evaporation."
    if any(word in question for word in ("scheme", "subsidy", "pm-kisan", "insurance")):
        return "Relevant programmes include PM-KISAN, Rythu Bandhu, PMFBY crop insurance, and the Kisan Credit Card. Confirm current eligibility through an official government portal or local agriculture office."
    return "I can help with crop selection, soil, fertilizer, pests, disease, irrigation, weather, schemes, and market planning. Please include your crop, location, season, and the problem you are seeing."


def _clean_response(text: str) -> str:
    """Remove accidental prompt labels while preserving useful Markdown."""
    cleaned = text.strip()
    for prefix in ("Answer:", "Response:", "KrishiSahay:"):
        if cleaned.lower().startswith(prefix.lower()):
            cleaned = cleaned[len(prefix):].strip()
    return cleaned


def generate_response(prompt: str, messages: list[dict], language: str) -> str:
    """Generate a contextual Gemini answer with a deterministic offline fallback."""
    api_key = os.getenv("GEMINI_API")
    if not api_key:
        return _offline_answer(prompt)

    try:
        import google.generativeai as genai

        genai.configure(api_key=api_key)
        model = genai.GenerativeModel("gemini-2.5-flash")
        recent_history = "\n".join(
            f"{item.get('role', 'user').title()}: {item.get('content', '')}"
            for item in messages[-8:]
        )
        instruction = f"""You are KrishiSahay, a careful agricultural assistant for Telangana farmers.
Answer the latest question in {language}. Use the conversation for context, but do not repeat it.
Be practical and structured. Use a short heading and bullets when useful.
Give specific next steps, ask for missing crop/soil/season details, and never invent live weather or prices.
For pesticide or fertilizer advice, mention label directions and local agriculture guidance.
If the question is unrelated to farming, politely say you specialize in agriculture.

Conversation:
{recent_history}

Latest question: {prompt}

Answer:"""
        response = model.generate_content(instruction)
        answer = _clean_response(response.text)
        return answer or _offline_answer(prompt)
    except Exception:
        # Keep the user-facing answer useful when the remote provider rejects a
        # key, reaches a quota, or is temporarily unavailable.
        return _offline_answer(prompt)


def bubble_html(role: str, content: str, message_time: str) -> str:
    """Build a safe, styled chat bubble for the transcript."""
    safe_content = html.escape(content).replace("\n", "<br>")
    safe_time = html.escape(message_time)
    label = "You" if role == "user" else "KrishiSahay"
    return (
        f'<div class="chat-row {role}">'
        f'<div class="chat-bubble"><div class="chat-author">{label}</div>'
        f'<div class="chat-content">{safe_content}</div>'
        f'<div class="chat-time">{safe_time}</div></div></div>'
    )
