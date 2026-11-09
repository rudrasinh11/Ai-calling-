import os
import sys
import uuid
import json

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

class KeySaveRequest(BaseModel):
    groq_api_key: str = ""

@app.on_event("startup")
def startup_event():
    jewellery_db.init_db()
    print("[INBOUND RECEPTIONIST] Server live on Drive I: Port 8055")

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

@app.post("/api/inbound-query")
async def handle_inbound_query(req: InboundQueryRequest):
    """
    Handles fast 1-second inbound caller text queries.
    Detects language -> Queries DB -> Speaks back in same language.
    """
    raw_text = req.text.strip()
    hint = req.language_hint

    # Determine language
    if hint in ["gu", "hi", "en"]:
        lang = hint
    else:
        lower = raw_text.lower()
        if any(w in lower for w in ["che", "bhav", "aaje", "shu", "tamare", "jovu", "kaho", "shukriya", "aavjo", "ભાવ", "રેટ"]):
            lang = "gu"
        elif any(w in lower for w in ["kya", "hai", "batao", "chahiye", "kitna", "namaste", "bhaiya", "sone", "सोना", "कैरेट", "भाव"]):
            lang = "hi"
        else:
            lang = "en"

    # Process through Inbound Brain (Groq LLM or Resilient DB matcher)
    reply_text, action, intent = brain_llm.get_inbound_response(raw_text, lang)

    # Synthesize Audio Speech
    temp_id = str(uuid.uuid4())[:8]
    output_filename = f"reply_{temp_id}.mp3"
    output_path = os.path.join(AUDIO_DIR, output_filename)
    await tts_engine.synthesize_speech_file(reply_text, output_path, lang)

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
        "audio_url": f"/audio/{output_filename}"
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
    print("💎 ROYAL HERITAGE JEWELLERS - INBOUND AI RECEPTIONIST 💎")
    print("💎 SHASHVAT JEWELS PVT LTD - INBOUND AI RECEPTIONIST 💎")
    print("Live on: http://localhost:8055")
    print("===========================================================\n")
    uvicorn.run("server:app", host="0.0.0.0", port=8055, reload=False)
