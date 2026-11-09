import os
import re
import asyncio
import edge_tts

VOICE_MAP = {
    "gu": "gu-IN-DhwaniNeural",      # Natural Gujarati female
    "hi": "hi-IN-SwaraNeural",       # Warm Hindi female receptionist
    "en": "en-IN-NeerjaNeural",      # Indian English professional female
}
DEFAULT_VOICE = "gu-IN-DhwaniNeural"

def get_voice_for_language(lang_code: str) -> str:
    if not lang_code:
        return DEFAULT_VOICE
    code = lang_code.lower().strip()[:2]
    return VOICE_MAP.get(code, DEFAULT_VOICE)

def normalize_text_for_speech(text: str, lang_code: str = "gu") -> str:
    """
    Normalizes numbers and jewellery terminology into natural spoken words.
    Fixes the issue where '22K' was pronounced digit-by-digit ('be be k' / 'two two k').
    """
    if not text:
        return text

    t = text
    lang = lang_code.lower().strip()[:2]

    if lang == "gu":
        # Gujarati Natural Pronunciation
        t = re.sub(r'\b24\s*[kK]\b|\b24\s*carat\b|\b24\s*karat\b|\b24\s*કેરેટ\b', 'ચોવીસ કેરેટ', t, flags=re.IGNORECASE)
        t = re.sub(r'\b22\s*[kK]\b|\b22\s*carat\b|\b22\s*karat\b|\b22\s*કેરેટ\b', 'બાવીસ કેરેટ', t, flags=re.IGNORECASE)
        t = re.sub(r'\b18\s*[kK]\b|\b18\s*carat\b|\b18\s*karat\b|\b18\s*કેરેટ\b', 'અઢાર કેરેટ', t, flags=re.IGNORECASE)
        t = re.sub(r'\b14\s*[kK]\b|\b14\s*carat\b|\b14\s*karat\b|\b14\s*કેરેટ\b', 'ચૌદ કેરેટ', t, flags=re.IGNORECASE)
        t = t.replace("₹", "રૂપિયા ")
        t = re.sub(r'/(?:gm|g|gram)\b', ' પ્રતિ ગ્રામ ', t, flags=re.IGNORECASE)
        t = re.sub(r'\bper gram\b', 'પ્રતિ ગ્રામ', t, flags=re.IGNORECASE)
    elif lang == "hi":
        # Hindi Natural Pronunciation
        t = re.sub(r'\b24\s*[kK]\b|\b24\s*carat\b|\b24\s*karat\b|\b24\s*कैरेट\b', 'चौबीस कैरेट', t, flags=re.IGNORECASE)
        t = re.sub(r'\b22\s*[kK]\b|\b22\s*carat\b|\b22\s*karat\b|\b22\s*कैरेट\b', 'बाईस कैरेट', t, flags=re.IGNORECASE)
        t = re.sub(r'\b18\s*[kK]\b|\b18\s*carat\b|\b18\s*karat\b|\b18\s*कैरेट\b', 'अट्ठारह कैरेट', t, flags=re.IGNORECASE)
        t = re.sub(r'\b14\s*[kK]\b|\b14\s*carat\b|\b14\s*karat\b|\b14\s*कैरेट\b', 'चौदह कैरेट', t, flags=re.IGNORECASE)
        t = t.replace("₹", "रुपये ")
        t = re.sub(r'/(?:gm|g|gram)\b', ' प्रति ग्राम ', t, flags=re.IGNORECASE)
        t = re.sub(r'\bper gram\b', 'प्रति ग्राम', t, flags=re.IGNORECASE)
    else:
        # English Natural Pronunciation
        t = re.sub(r'\b24\s*[kK]\b', 'twenty-four karat', t, flags=re.IGNORECASE)
        t = re.sub(r'\b22\s*[kK]\b', 'twenty-two karat', t, flags=re.IGNORECASE)
        t = re.sub(r'\b18\s*[kK]\b', 'eighteen karat', t, flags=re.IGNORECASE)
        t = t.replace("₹", "rupees ")
        t = re.sub(r'/(?:gm|g|gram)\b', ' per gram ', t, flags=re.IGNORECASE)

    return t

async def synthesize_speech_file(text: str, output_path: str, lang_code: str = "gu") -> str:
    """
    Synthesizes speech with natural phonetic word normalization and human conversational pacing.
    """
    if not text or not text.strip():
        text = "Namaste! Welcome to Shashvat Jewels."

    spoken_text = normalize_text_for_speech(text, lang_code)
    voice = get_voice_for_language(lang_code)

    try:
        communicate = edge_tts.Communicate(spoken_text, voice, rate="-3%", pitch="+0Hz")
        await communicate.save(output_path)
        return output_path
    except Exception as e:
        print(f"[TTS Notice] Primary voice {voice} notice: {e}, falling back...")
        try:
            communicate = edge_tts.Communicate(spoken_text, "en-IN-NeerjaNeural", rate="-3%")
            await communicate.save(output_path)
            return output_path
        except Exception as e2:
            print(f"[TTS Fallback Notice] {e2}")
            return output_path
