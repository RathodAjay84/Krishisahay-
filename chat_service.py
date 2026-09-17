"""Chat, voice, and lightweight conversation storage for KrishiSahay."""

from __future__ import annotations

import html
import io
import json
import os
import re
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path

from dotenv import load_dotenv
from knowledge_base import retrieve_context

PROJECT_ROOT = Path(__file__).parent
ENV_FILE = PROJECT_ROOT / ".env"
load_dotenv(dotenv_path=ENV_FILE)

CHAT_LOG_PATH = Path(__file__).with_name("chat_history.json")

SCHEMES_CONTEXT = """Relevant India-focused support options:
- PM-KISAN: confirm current eligibility at https://pmkisan.gov.in/
- PMFBY crop insurance: check enrolment and claim rules at https://pmfby.gov.in/
- Kisan Credit Card: ask a bank or agriculture office about eligibility.
- Soil Health Card: https://soilhealth.dac.gov.in/
- PM Krishi Sinchai Yojana: https://pmksy.gov.in/
- mKisan advisories: https://mkisan.gov.in/
Never promise a benefit, amount, subsidy, or approval; schemes and eligibility can change."""

RESPONSE_GUIDANCE = """Answer like a thoughtful agricultural expert, not a form or template.
Write natural short paragraphs with a conversational flow. Explain what you understood,
the likely causes and reasoning, immediate actions, prevention, and an extra insight when
useful. Vary sentence openings and wording; never copy a previous answer. Adapt the
length to the question and use crop, image, sensor, season, location, and conversation
context. Say possible or likely when evidence is incomplete. If an image is unclear, say:
I’m not fully confident from the image. Please upload a clearer photo.
Never invent a link, image finding, weather value, price, diagnosis, pesticide mixture,
or unsafe dose. Follow product labels and suggest a local agriculture officer for product
selection. Include relevant official links from the supplied context when useful."""


def timestamp() -> str:
    """Return a short local timestamp for chat messages."""
    return datetime.now().strftime("%d %b %Y, %I:%M %p")


def get_time_greeting(now: datetime | None = None) -> str:
    hour = (now or datetime.now()).hour
    if hour < 12:
        return "Good Morning"
    if hour < 17:
        return "Good Afternoon"
    return "Good Evening"


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


def _offline_answer(prompt: str, field_context: dict | None = None) -> str:
    """Provide concise agriculture guidance when Gemini is not configured."""
    question = prompt.lower()
    context = field_context or {}
    moisture_text = str(context.get("soil_moisture", ""))
    try:
        moisture = float(moisture_text.replace("%", ""))
    except ValueError:
        moisture = None
    if moisture is not None and moisture < 30:
        return (
            f"The soil moisture reading is low at about {moisture:g}%. This suggests water stress may be limiting root uptake. "
            "Check moisture at root depth in two or three places. If the soil is dry and heavy rain is not expected, irrigate slowly during the cooler hours; avoid flooding and recheck the field afterwards. "
            "Give priority to plants in flowering or fruit filling, repair leaks, and use mulch where suitable. Share the crop and soil type for a more exact schedule."
        )
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


def _openai_response(instructions: str, user_content: str) -> str:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY is not configured")
    payload = json.dumps({
        "model": os.getenv("OPENAI_MODEL", "gpt-4.1-mini"),
        "instructions": instructions,
        "input": user_content,
        "temperature": 0.7,
        "top_p": 1,
        "max_output_tokens": 700,
    }).encode("utf-8")
    request = urllib.request.Request(
        "https://api.openai.com/v1/responses",
        data=payload,
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        method="POST",
    )
    with urllib.request.urlopen(request, timeout=45) as response:
        result = json.loads(response.read().decode("utf-8"))

    answer = result.get("output_text", "").strip()
    if not answer:
        chunks = []
        for item in result.get("output", []) or []:
            if not isinstance(item, dict):
                continue
            if item.get("type") == "message":
                for part in item.get("content", []) or []:
                    if isinstance(part, dict):
                        text = part.get("text") or part.get("output_text")
                        if isinstance(text, str) and text.strip():
                            chunks.append(text.strip())
            elif item.get("type") == "output_text" and isinstance(item.get("text"), str):
                chunks.append(item["text"].strip())
        answer = "\n".join(chunks).strip()

    if not answer:
        raise RuntimeError("OpenAI returned an empty response")
    return answer


def generate_response(prompt: str, messages: list[dict], language: str, field_context: dict | None = None) -> str:
    """Generate a contextual OpenAI answer with a useful offline fallback."""
    context = field_context or {}
    if not os.getenv("OPENAI_API_KEY"):
        return _offline_answer(prompt, field_context)
    try:
        now = datetime.now()
        live_context = "\n".join([
            f"Current date and time: {now.strftime('%Y-%m-%d %H:%M:%S')}",
            f"Greeting: {get_time_greeting(now)}",
            f"Crop: {context.get('crop', 'Not provided')}",
            f"Soil moisture: {context.get('soil_moisture', 'Not provided')}",
            f"Temperature: {context.get('temperature', 'Not provided')}",
            f"Humidity: {context.get('humidity', 'Not provided')}",
            f"pH: {context.get('ph', 'Not provided')}",
            f"NPK: {context.get('npk', 'Not provided')}",
            f"Crop image analysis: {context.get('image_analysis', 'Not available')}",
        ])
        history = "\n".join(
            f"{item.get('role', 'user').title()}: {item.get('content', '')}"
            for item in messages[-8:]
        )
        question_lower = prompt.lower()
        schemes = SCHEMES_CONTEXT if any(word in question_lower for word in ('money', 'loan', 'credit', 'scheme', 'subsid', 'insurance', 'risk', 'fertilizer', 'irrigation')) else ''
        instruction = f"""You are KrishiSahay GPT, a smart farming assistant for Indian farmers.
Answer in {language}. {RESPONSE_GUIDANCE}

Real-time field context:
{live_context}

Retrieved local guidance:
{retrieve_context(prompt)}

Relevant schemes, if any:
{schemes or 'None needed for this question.'}

Conversation:
{history}

Latest farmer question:
{prompt}

Write the best direct answer now."""
        return _clean_response(_openai_response(instruction, prompt))
    except (OSError, ValueError, urllib.error.URLError, RuntimeError):
        return _offline_answer(prompt, context)


def bubble_html(role: str, content: str, message_time: str) -> str:
    """Build a safe, styled chat bubble for the transcript."""
    safe_content = html.escape(content).replace("\n", "<br>")
    safe_content = re.sub(
        r"(https://[^\s<]+)",
        r'<a href="\1" target="_blank" rel="noopener noreferrer">\1</a>',
        safe_content,
    )
    safe_time = html.escape(message_time)
    label = "You" if role == "user" else "KrishiSahay"
    return (
        f'<div class="chat-row {role}">'
        f'<div class="chat-bubble"><div class="chat-author">{label}</div>'
        f'<div class="chat-content">{safe_content}</div>'
        f'<div class="chat-time">{safe_time}</div></div></div>'
    )
