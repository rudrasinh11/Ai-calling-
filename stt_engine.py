import os
import sys
import re

# Ensure UTF-8 output on Windows
if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from faster_whisper import WhisperModel

MODEL_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "models", "whisper")
os.makedirs(MODEL_DIR, exist_ok=True)

# Restrict exclusively to Inbound Receptionist Indian store languages
ALLOWED_LANGUAGES = ["gu", "hi", "en"]
DEFAULT_LANGUAGE = "hi"

_model_instance = None

def get_whisper_model(model_size: str = "base"):
    global _model_instance
    if _model_instance is None:
        device = "cuda" if os.environ.get("USE_CUDA", "").lower() == "true" else "cpu"
        compute_type = "float16" if device == "cuda" else "int8"
        try:
            _model_instance = WhisperModel(
                model_size,
                device=device,
                compute_type=compute_type,
                download_root=MODEL_DIR
            )
        except Exception:
            _model_instance = WhisperModel(
                model_size,
                device="cpu",
                compute_type="int8",
                download_root=MODEL_DIR
            )
    return _model_instance

def clean_hallucinations(text: str) -> str:
    """Removes Whisper repetition loops (e.g. 'not going to enjoy today' repeating)."""
    if not text:
        return ""
    # Strip obvious repeating 2-5 word patterns
    words = text.split()
    if len(words) > 6:
        # Check for phrase repeats
        pattern = r"(\b.+\b)( \1){2,}"
        cleaned = re.sub(pattern, r"\1", text, flags=re.IGNORECASE)
        return cleaned.strip()
    return text.strip()

def transcribe_and_detect_language(audio_path_or_buffer, language_hint: str = None):
    """
    Transcribes inbound caller speech strictly constrained to:
    Gujarati (gu), Hindi (hi), and English (en).
    Never outputs Arabic or foreign hallucinations.
    """
    model = get_whisper_model("base")

    # If hint provided and valid, enforce it
    lang = language_hint if language_hint in ALLOWED_LANGUAGES else None

    segments, info = model.transcribe(
        audio_path_or_buffer,
        language=lang,
        beam_size=3,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=400)
    )

    text_parts = []
    for segment in segments:
        text_parts.append(segment.text.strip())

    raw_text = " ".join(text_parts).strip()
    cleaned_text = clean_hallucinations(raw_text)

    detected_lang = info.language
    prob = info.language_probability

    # Strictly disallow foreign languages (like 'ar', 'fa', 'cy')
    if detected_lang not in ALLOWED_LANGUAGES or prob < 0.25:
        # Check text heuristics
        # If Gujarati characters or typical words
        if any(w in cleaned_text.lower() for w in ["che", "bhav", "aaje", "shu", "tamare", "jovu", "kaho"]):
            detected_lang = "gu"
        elif any(w in cleaned_text.lower() for w in ["kya", "hai", "batao", "chahiye", "kitna", "namaste", "bhaiya"]):
            detected_lang = "hi"
        else:
            detected_lang = DEFAULT_LANGUAGE

    return cleaned_text, detected_lang, prob
