# 💎 Shashvat Jewels Pvt Ltd - Multilingual Inbound AI Calling Receptionist

A 100% free, low-latency, multilingual (Gujarati, Hindi, English) Inbound AI Calling Receptionist for **Shashvat Jewels Pvt Ltd** (Diamond & Fine Jewellery Unit).

Designed specifically for handling inbound customer calls with zero delay, conversational natural language, code-mixed Gujlish/Hinglish speech, dynamic gold rate math calculations, and natural jewellery number pronunciation.

---

## 🌟 Key Features

1. **Dedicated Inbound Receptionist:**
   - Pre-cached instant welcome greeting (0ms delay).
   - Greets callers warmly and answers gold, diamond, solitaire, and store questions.
   - Detects call completion ("aavjo", "dhanyawad", "bye") or human manager escalation.

2. **Multilingual 1-2-3 Language Selection:**
   - **1:** Gujarati (ગુજરાતી) — Natural speech via `gu-IN-DhwaniNeural`
   - **2:** Hindi (हिंदी) — Warm receptionist tone via `hi-IN-SwaraNeural`
   - **3:** English (Indian) — Crisp professional voice via `en-IN-NeerjaNeural`

3. **Natural Gujlish & Hinglish Code-Mixing:**
   - Seamlessly handles customers mixing English words (e.g. *"22k gold rate with 3 gram extra"*, *"price"*, *"carat"*, *"discount"*).

4. **Dynamic Price & Weight Math Calculations:**
   - Performs live math: multiplying requested weight by daily gold rates (e.g. 3 grams of 22K = 3 × ₹7,200 = ₹21,600).

5. **Spoken Word Phonetic Normalization:**
   - Automatically fixes robotic digit-by-digit reading (e.g., "22K" is spoken as **"બાવીસ કેરેટ"** or **"बाईस कैरेट"**, never "be-be-k").

6. **SQLite Conversation History:**
   - Every inbound call, transcription, action, and reply is logged to SQLite (`jewellery_store.db`).

7. **LiveKit Real-Time WebRTC Stack:**
   - Includes local LiveKit server (`livekit-server.exe`) and LiveKit Agents framework with Silero VAD for instant barge-in.

---

## 🚀 Quick Start

### 1. Setup Virtual Environment & Dependencies
```powershell
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
```

### 2. Configure Environment Variables
Copy `.env.example` to `.env` and add your free Groq API key:
```env
GROQ_API_KEY=gsk_your_groq_api_key_here
```

### 3. Run the Application
Double-click `run_receptionist.bat` or run:
```powershell
python server.py
```
Open **`http://localhost:8055`** in your browser.

---

## 📁 Repository Structure
```
├── server.py              # FastAPI WebPhone & API backend (Port 8055)
├── brain_llm.py           # Conversational Receptionist Brain & Math Engine
├── jewellery_db.py        # SQLite Database (Products, Rates, Call Logs)
├── tts_engine.py          # Edge-TTS Neural Voice & Spoken Normalizer
├── stt_engine.py          # Speech-to-Text Fallback Engine
├── run_receptionist.bat   # 1-Click Launch Script
├── run_livekit.bat        # 1-Click Launch Script with LiveKit Server
├── static/
│   └── webphone.html      # Hands-free WebPhone UI with 1-2-3 Keypad
├── livekit/               # LiveKit Server binary and configs
├── requirements.txt       # Project Dependencies
└── README.md
```
