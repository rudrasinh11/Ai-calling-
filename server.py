import os
import sys
import uuid
import json
import re

# Ensure UTF-8 output
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from fastapi import FastAPI, UploadFile, File, Response, Body
from fastapi.responses import HTMLResponse, FileResponse, JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import jewellery_db
import tts_engine
import stt_engine
import brain_llm

app = FastAPI(title="Jewellery Inbound AI Voice Receptionist")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
AUDIO_DIR = os.path.join(BASE_DIR, "audio_temp")
STATIC_DIR = os.path.join(BASE_DIR, "static")
ENV_FILE = os.path.join(BASE_DIR, ".env")
os.makedirs(AUDIO_DIR, exist_ok=True)

LANGUAGE_NAMES = {
    "gu": "Gujarati (ગુજરાતી)",
    "hi": "Hindi (हिंदी)",
    "en": "English (Indian)",
}

class InboundQueryRequest(BaseModel):
    text: str
    language_hint: str = "auto"
    voice_mode: str = "fast"  # "fast" for instant browser speech (<0.5s), "studio" for Edge-TTS

class KeySaveRequest(BaseModel):
    groq_api_key: str = ""

@app.on_event("startup")
async def startup_event():
    jewellery_db.init_db()
    print("[INBOUND RECEPTIONIST] Server live on Drive I: Port 8055")
    
    # Pre-cache clean welcome audio
    welcome_path = os.path.join(AUDIO_DIR, "inbound_welcome.mp3")
    if not os.path.exists(welcome_path) or os.path.getsize(welcome_path) == 0:
        print("[STARTUP] Pre-synthesizing inbound_welcome.mp3...")
        await tts_engine.synthesize_speech_file(
            "Namaste! Welcome to Shashvat Jewels. How may I assist you with our diamond and gold collection today?",
            welcome_path,
            "gu"
        )
    print("[STARTUP] Audio cache ready.")

@app.get("/", response_class=HTMLResponse)
@app.get("/webphone", response_class=HTMLResponse)
async def get_inbound_webphone():
    """Serves the Inbound Phone Call simulator."""
    html_path = os.path.join(STATIC_DIR, "webphone.html")
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

@app.get("/audio/{filename}")
async def get_audio_file(filename: str):
    file_path = os.path.join(AUDIO_DIR, filename)
    if os.path.exists(file_path):
        return FileResponse(file_path, media_type="audio/mpeg")
    return JSONResponse(status_code=404, content={"error": "Audio file not found"})

@app.get("/api/welcome-audio")
async def get_welcome_audio():
    """Serves instant pre-cached welcome greeting for Shashvat Jewels (0ms delay)."""
    out_file = os.path.join(AUDIO_DIR, "inbound_welcome.mp3")
    if not os.path.exists(out_file):
        welcome_text = "Namaste! Welcome to Shashvat Jewels. How may I assist you with our diamond and gold collection today?"
        await tts_engine.synthesize_speech_file(welcome_text, out_file, "en")
    return {"audio_url": "/audio/inbound_welcome.mp3"}

def detect_user_language(text: str, hint: str = "auto") -> str:
    """
    Intelligently detects language between English, Gujarati, and Hindi.
    Correctly recognizes English queries even when transcribed by Gujarati STT phonetically.
    """
    raw = text.strip()
    lower = raw.lower()

    # 1. Explicit Language Switch Requests
    if any(w in lower for w in ["english", "ઇંગલિશ", "इंग्लिश", "speak english", "speak in english", "talk in english", "can you speak english", "can you speak in english"]):
        return "en"
    if any(w in lower for w in ["gujarati", "ગુજરાતી", "गुजराती", "gujarati ma", "gujarati bolo", "speak gujarati"]):
        return "gu"
    if any(w in lower for w in ["hindi", "हिंदी", "હિન્દી", "hindi mein", "hindi bolo", "speak hindi"]):
        return "hi"

    # 2. Phonetic English in Gujarati Script (e.g. "વોટ ઈઝ ટૂ ડે ગોલ્ડ પ્રાઇઝ")
    if any(w in raw for w in ["વોટ ઈઝ", "વોટ ઇઝ", "વોટ", "પ્રાઇઝ", "પ્રાઈઝ", "કેન યુ", "ગિવ મી"]):
        return "en"

    # 3. Gujarati Unique Indicators
    gu_unique = [
        "che", "chhe", "shu", "bhav", "aaje", "tamare", "ketla", "thase", "sonana",
        "sonu", "aavjo", "kaho", "jovu", "છે", "શું", "ભાવ", "સોનું", "સોના",
        "કેટલા", "થશે", "આજે", "તમારે", "આવજો", "મારે", "જોઈએ", "મળશે"
    ]
    if any(w in lower for w in gu_unique):
        return "gu"

    # 4. Hindi Unique Indicators
    hi_unique = [
        "kya", "hai", "batao", "chahiye", "kitna", "kitne", "hoga", "sone", "sona",
        "chandi", "aaj", "kaise", "dukaan", "bhaiya", "namaste", "क्या", "है",
        "बताओ", "चाहिए", "कितना", "कितने", "होगा", "सोना", "सोने", "चांदी", "दीजिए"
    ]
    if any(w in lower for w in hi_unique):
        return "hi"

    # 5. English Unique Indicators (not shared jewellery loan words)
    en_unique = [
        "what", "is", "today", "todays", "price", "how", "much", "can", "you",
        "give", "me", "tell", "show", "hello", "hi", "hey", "please", "thank",
        "available", "store", "shop", "address", "timing", "open", "close"
    ]
    if any(re.search(rf'\b{w}\b', lower) for w in en_unique):
        return "en"

    # 6. Fallback to conversation hint or Gujarati
    if hint in ["gu", "hi", "en"] and hint != "auto":
        return hint

    return "gu"

@app.post("/api/inbound-query")
async def handle_inbound_query(req: InboundQueryRequest):
    """
    Handles ultra-fast inbound caller text queries.
    - If voice_mode == 'fast': Returns response in <0.5s for instant browser speech!
    - If voice_mode == 'studio': Synthesizes high-fidelity Edge-TTS audio.
    """
    raw_text = req.text.strip()
    hint = req.language_hint

    # Accurately classify language for current utterance
    lang = detect_user_language(raw_text, hint)

    # Process through Inbound Brain (Groq LLM or Resilient DB matcher)
    reply_text, action, intent = brain_llm.get_inbound_response(raw_text, lang)

    # Audio synthesis based on voice_mode
    audio_url = ""
    if req.voice_mode == "studio":
        temp_id = str(uuid.uuid4())[:8]
        output_filename = f"reply_{temp_id}.mp3"
        output_path = os.path.join(AUDIO_DIR, output_filename)
        await tts_engine.synthesize_speech_file(reply_text, output_path, lang)
        audio_url = f"/audio/{output_filename}"

    # Log to Inbound Call Logs
    jewellery_db.log_inbound_call(
        caller_phone="Inbound-Web-Caller",
        language=lang,
        inquiry_type=intent,
        caller_query=raw_text,
        reply=reply_text,
        action=action
    )

    return {
        "reply": reply_text,
        "action": action,
        "intent": intent,
        "language_code": lang,
        "language_name": LANGUAGE_NAMES.get(lang, lang.upper()),
        "audio_url": audio_url
    }

@app.post("/api/save-key")
async def save_groq_key(req: KeySaveRequest):
    """Saves Groq API Key to .env and updates environment."""
    key = req.groq_api_key.strip()
    if key:
        os.environ["GROQ_API_KEY"] = key
        with open(ENV_FILE, "w", encoding="utf-8") as f:
            f.write(f"GROQ_API_KEY={key}\n")
        return {"status": "success", "message": "Groq API Key saved and active!"}
    return {"status": "error", "message": "No key provided"}

@app.get("/api/key-status")
async def get_key_status():
    has_groq = bool(os.environ.get("GROQ_API_KEY", "").strip())
    return {"has_groq": has_groq}

if __name__ == "__main__":
    import uvicorn
    print("\n===========================================================")
    print("💎 SHASHVAT JEWELS PVT LTD - INBOUND AI RECEPTIONIST 💎")
    print("Live on: http://localhost:8055")
    print("===========================================================\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8055, reload=False)
