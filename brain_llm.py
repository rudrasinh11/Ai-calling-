import os
import sys
import re
import json
import jewellery_db

# Load .env if present
env_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")
if os.path.exists(env_file):
    with open(env_file, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ[k.strip()] = v.strip()

SYSTEM_PROMPT = """You are "Aarohi", the friendly, welcoming, and smart Inbound AI Receptionist for "Shashvat Jewels Pvt Ltd".
Your job is to answer customer phone calls in a simple, friendly, natural tone (NOT overly stiff or robotic).

CRITICAL CONVERSATIONAL RULES:
1. NATURAL CODE-MIXING (GUJLISH & HINGLISH):
   Customers frequently mix English words when speaking Gujarati or Hindi (e.g., "price", "rate", "carat", "gold", "add 3 gram extra", "discount").
   - Always understand code-mixed speech seamlessly!
   - Reply in the customer's primary language in simple, conversational, everyday words.
   - For Gujarati: Speak simple, friendly Gujarati (e.g. "બાવીસ કેરેટ", "સોનું", "રૂપિયા").
   - For Hindi: Speak simple, warm Hindi.
   - For English: Speak clear, polite Indian English.

2. DYNAMIC PRICE & WEIGHT CALCULATIONS:
   If the customer asks for a specific weight, addition, or quantity (e.g., "add 3 gram extra", "5 gram no ketlo bhav", "10 gram necklace"):
   - You MUST compute the exact total price!
   - Multiply the weight in grams by Today's Gold Rate per gram.
     * Today's 24K Gold Rate = ₹7,850 / gram
     * Today's 22K Gold Rate = ₹7,200 / gram
     * Today's 18K Gold Rate = ₹5,890 / gram
     * Today's Silver Rate = ₹95 / gram
   - Example 1: Customer asks "22k gold rate with 3 gram extra" or "3 gram 22k sonana ketla?"
     Calculate: 3 x 7,200 = ₹21,600.
     Reply: "Aaje bavis karat sonano bhav 7,200 rupiya prati gram che. 3 gram sonana lagbhag 21,600 rupiya thase (making charges extra)."
   - Example 2: Customer asks for "5 gram 24k pure gold":
     Calculate: 5 x 7,850 = ₹39,250.
     Reply: "Panch gram chovis karat sonano bhav 39,250 rupiya thase."

3. ULTRA-FAST VOICE CALL CONVERSATION (STRICT 1 SENTENCE):
   - Answer in EXACTLY 1 crisp, natural, spoken sentence (under 15 words).
   - Never output paragraphs, lists, bullet points, or multiple sentences.
   - For prices: State the rate and calculated total directly in 1 short punchy sentence.
   - If customer says goodbye/thank you/aavjo -> Wish them well in 1 short sentence.
   - If customer asks to speak with the manager -> Confirm transfer in 1 short sentence.

4. STRICT ZERO-TOLERANCE PROFANITY RULE (NO GAALI / GAAD):
   - You must NEVER generate, repeat, or validate any vulgar words, cuss words, or 'gaali'/'gaad' under ANY circumstances.
   - If a caller is angry or uses abusive slang, maintain absolute dignity, warmth, and composure.
   - Calmly defuse tension in polite, formal language asking them to speak respectfully.

STORE KNOWLEDGE:
{knowledge_base}
"""

def query_groq(prompt: str, lang: str = "gu"):
    from groq import Groq
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return None

    client = Groq(api_key=api_key)
    knowledge = jewellery_db.get_store_knowledge_summary()
    system = SYSTEM_PROMPT.format(knowledge_base=knowledge)

    chat_completion = client.chat.completions.create(
        messages=[
            {"role": "system", "content": system},
            {"role": "user", "content": f"Customer Language Preference: {lang}\nInbound Customer Query: {prompt}\nRule: Reply in exactly 1 short natural sentence for voice phone call.\nAarohi Spoken Reply:"}
        ],
        model="qwen/qwen3.8-27b",
        temperature=0.2,
        max_tokens=50,
    )
    return chat_completion.choices[0].message.content.strip()

def detect_inbound_action_and_intent(prompt: str):
    p_lower = prompt.lower()
    if any(w in p_lower for w in ["bye", "thank you", "thanks", "dhanyawad", "aavjo", "rakhu chu", "rakhta hoon", "bas", "kahi nahi"]):
        return "HANGUP", "Call Completion"
    if any(w in p_lower for w in ["manager", "owner", "malik", "human", "insan", "staff", "sheth", "complaint"]):
        return "TRANSFER_HUMAN", "Human Escalation"
    if any(w in prompt for w in ["भाव", "कैरेट", "सोना", "चांदी", "રેટ", "ભાવ", "સોનું", "ચાંદી"]) or any(w in p_lower for w in ["rate", "bhav", "bhaav", "price", "kimat", "sone", "chandi", "gold", "silver", "gram"]):
        return "CONTINUE", "Rate & Calculation Inquiry"
    if any(w in prompt for w in ["दुकान", "समय", "पता", "ક્યાં"]) or any(w in p_lower for w in ["time", "timing", "open", "close", "kaha", "address", "location", "kyare", "dukaan"]):
        return "CONTINUE", "Store Info / Timings"
    return "CONTINUE", "Jewellery Inquiry"

def get_inbound_response(prompt: str, lang: str = "gu"):
    action, intent = detect_inbound_action_and_intent(prompt)
    p_lower = prompt.lower()

    # 0. Abuse / Gaad / Gaali Guardrail - Strictly Respectful De-escalation (No Gaali)
    profanity_patterns = [
        r'\bchutiya\b', r'\bgandu\b', r'\bmadarchod\b', r'\bbhosd\w*', r'\bharami\b',
        r'\bkamina\b', r'\bsala\b', r'\bsale\b', r'\bgadheda\b', r'\blund\b', r'\bloda\b',
        r'\blauda\b', r'\bfuck\w*', r'\bbitch\b', r'\bbastard\b', r'\bchod\b', r'\bkutta\b',
        r'\bidiot\b', r'ગાંડુ', r'ચુતિયા', r'ભોસડી', r'હરામી', r'કમીના', r'સાલા', r'ગધેડા'
    ]
    if any(re.search(pat, p_lower) for pat in profanity_patterns):
        if lang == "gu":
            return "કૃપા કરીને નમ્રતાપૂર્વક વાત કરો. હું શાશ્વત જ્વેલર્સ તરફથી આપને પૂરી મદદ કરવા માટે અહીં છું.", "CONTINUE", "Polite De-escalation"
        elif lang == "hi":
            return "कृपया शालीनता और सम्मानपूर्वक बात करें। मैं शाश्वत ज्वेल्स में आपकी पूरी सहायता करने के लिए यहाँ हूँ।", "CONTINUE", "Polite De-escalation"
        else:
            return "I kindly request you to speak respectfully. I am here from Shashvat Jewels to assist you with care.", "CONTINUE", "Polite De-escalation"

    # 1. Instant 0ms Actions: Hangup, Escalation & Language Switch
    if any(w in p_lower for w in ["speak in english", "speak english", "can you speak english", "can you speak in english", "talk in english", "ઇંગલિશ", "इंग्लिश"]):
        return "Yes, I can certainly speak in English. How may I assist you with our gold and diamond jewellery today?", "CONTINUE", "Language Preference"

    if any(w in p_lower for w in ["gujarati ma", "gujarati bolo", "ગુજરાતી બોલો", "speak in gujarati"]):
        return "ચોક્કસ, હું આપની સાથે ગુજરાતીમાં વાત કરીશ. સોનાના ભાવ કે જ્વેલરી બાબતે શું જાણવું છે?", "CONTINUE", "Language Preference"

    if any(w in p_lower for w in ["hindi mein", "hindi bolo", "हिंदी बोलो", "speak in hindi"]):
        return "हाँ बिल्कुल, मैं आपसे हिंदी में बात करूँगी। शाश्वत ज्वेल्स में मैं आपकी क्या सहायता कर सकती हूँ?", "CONTINUE", "Language Preference"

    if action == "HANGUP":
        if lang == "gu":
            return "Shashvat Jewels ma call karva badal aabhar. Tamaro divas shubh rahe, aavjo!", "HANGUP", intent
        elif lang == "hi":
            return "Shashvat Jewels mein call karne ke liye shukriya. Aapka din shubh ho, dhanyawad!", "HANGUP", intent
        else:
            return "Thank you for calling Shashvat Jewels. Have a wonderful day ahead, goodbye!", "HANGUP", intent

    if action == "TRANSFER_HUMAN":
        if lang == "gu":
            return "Chokkas, tame line par raho, hun tamaro call sales manager sathe connect karu chu.", "TRANSFER_HUMAN", intent
        elif lang == "hi":
            return "Ji bilkul, kripya line par bane rahein, main aapki call sales manager ko transfer kar rahi hoon.", "TRANSFER_HUMAN", intent
        else:
            return "Certainly, please hold the line while I transfer your call to our sales manager.", "TRANSFER_HUMAN", intent

    # 2. Instant 0ms Exact Weight Calculations (e.g. "3 gram", "5 gram", "add 3 gram extra")
    conn = jewellery_db.get_connection()
    c = conn.cursor()
    c.execute("SELECT metal, rate_per_gram FROM daily_rates;")
    rates = {row["metal"]: row["rate_per_gram"] for row in c.fetchall()}
    conn.close()

    rate_22k = rates.get("gold_22k", 7200.0)
    rate_24k = rates.get("gold_24k", 7850.0)
    rate_silver = rates.get("silver", 95.0)

    gram_match = re.search(r'(\d+(?:\.\d+)?)\s*(?:gram|g|gm|ગ્રામ|ग्राम)', prompt, re.IGNORECASE)
    weight_grams = float(gram_match.group(1)) if gram_match else None

    if weight_grams:
        is_24k = "24" in prompt
        chosen_rate = rate_24k if is_24k else rate_22k
        carat_name_gu = "ચોવીસ કેરેટ" if is_24k else "બાવીસ કેરેટ"
        carat_name_hi = "चौबीस कैरेट" if is_24k else "बाईस कैरेट"
        total_price = int(weight_grams * chosen_rate)

        if lang == "gu":
            return f"Aaje {carat_name_gu} sonano bhav {int(chosen_rate)} rupiya prati gram che. {weight_grams} gram sonana lagbhag {total_price:,} rupiya thase.", "CONTINUE", "Rate Calculation"
        elif lang == "hi":
            return f"Aaj {carat_name_hi} sone ka rate {int(chosen_rate)} rupaye per gram hai. {weight_grams} gram sone ka total lagbhag {total_price:,} rupaye hoga.", "CONTINUE", "Rate Calculation"
        else:
            return f"Today's {'24K' if is_24k else '22K'} gold rate is ₹{int(chosen_rate)} per gram. For {weight_grams} grams, it will be approximately ₹{total_price:,}.", "CONTINUE", "Rate Calculation"

    # 3. Instant 0ms Daily Rates Inquiries (24k, 22k, silver)
    is_asking_rate = any(k in prompt for k in ["भाव", "સોના", "સોનું", "રેટ", "ચાંદી", "ચાંદીનો", "સોનાનો", "પ્રાઇઝ", "પ્રાઈઝ", "ગોલ્ડ"]) or any(k in p_lower for k in ["rate", "bhav", "price", "kimat", "sone ka", "gold rate", "chandi", "gold price"])
    if is_asking_rate:
        if "24" in prompt:
            if lang == "gu":
                return f"Aaje ચોવીસ કેરેટ શુદ્ધ સોનાનો ભાવ {int(rate_24k)} રૂપિયા પ્રતિ ગ્રામ છે.", "CONTINUE", "Rate Inquiry"
            elif lang == "hi":
                return f"Aaj चौबीस कैरेट शुद्ध सोने का रेट {int(rate_24k)} रुपये प्रति ग्राम है।", "CONTINUE", "Rate Inquiry"
            else:
                return f"Today's 24K pure gold rate is ₹{int(rate_24k):,} per gram.", "CONTINUE", "Rate Inquiry"
        elif "22" in prompt or "20" in prompt:
            if lang == "gu":
                return f"Aaje બાવીસ કેરેટ સોનાનો ભાવ {int(rate_22k)} રૂપિયા પ્રતિ ગ્રામ છે.", "CONTINUE", "Rate Inquiry"
            elif lang == "hi":
                return f"Aaj बाईस कैरेट सोने का रेट {int(rate_22k)} रुपये प्रति ग्राम है।", "CONTINUE", "Rate Inquiry"
            else:
                return f"Today's 22K gold rate is ₹{int(rate_22k):,} per gram.", "CONTINUE", "Rate Inquiry"
        elif "silver" in p_lower or "चांदी" in prompt or "ચાંદી" in prompt:
            if lang == "gu":
                return f"Aaje ચાંદીનો ભાવ {int(rate_silver)} રૂપિયા પ્રતિ ગ્રામ છે.", "CONTINUE", "Rate Inquiry"
            elif lang == "hi":
                return f"Aaj चांदी का रेट {int(rate_silver)} रुपये प्रति ग्राम है।", "CONTINUE", "Rate Inquiry"
            else:
                return f"Today's silver rate is ₹{int(rate_silver)} per gram.", "CONTINUE", "Rate Inquiry"
        else:
            if lang == "gu":
                return f"Aaje બાવીસ કેરેટ સોનાનો ભાવ {int(rate_22k)} રૂપિયા અને ચોવીસ કેરેટનો {int(rate_24k)} રૂપિયા પ્રતિ ગ્રામ છે.", "CONTINUE", "Rate Inquiry"
            elif lang == "hi":
                return f"Aaj बाईस कैरेट सोने का रेट {int(rate_22k)} रुपये और चौबीस कैरेट का {int(rate_24k)} रुपये प्रति ग्राम है।", "CONTINUE", "Rate Inquiry"
            else:
                return f"Today's 22K gold rate is ₹{int(rate_22k)} per gram and 24K is ₹{int(rate_24k)} per gram.", "CONTINUE", "Rate Inquiry"

    # 4. Groq LPU with Qwen 27B for dynamic conversations, diamonds, collections
    try:
        if os.environ.get("GROQ_API_KEY"):
            groq_reply = query_groq(prompt, lang)
            if groq_reply:
                return groq_reply, action, intent
    except Exception as e:
        print(f"[Groq Processing Notice] {e}")

    # 4. Local Fallback Math & Knowledge Engine
    if any(k in prompt for k in ["भाव", "સોના", "સોનું", "રેટ"]) or any(k in p_lower for k in ["rate", "bhav", "gold", "price"]):
        if lang == "gu":
            return f"Aaje બાવીસ કેરેટ sonano bhav {int(rate_22k)} rupiya ane ચોવીસ કેરેટ sonano {int(rate_24k)} rupiya prati gram che. Tamare ketla gram jewellery joveli che?", "CONTINUE", "Rate Inquiry"
        elif lang == "hi":
            return f"Aaj बाईस कैरेट सोने का रेट {int(rate_22k)} रुपये और चौबीस कैरेट का {int(rate_24k)} रुपये प्रति gram hai. Aapko kitne gram ki jankari chahiye?", "CONTINUE", "Rate Inquiry"
        else:
            return f"Today's 22K gold rate is ₹{int(rate_22k)} per gram, and 24K pure gold is ₹{int(rate_24k)} per gram. How many grams are you looking for?", "CONTINUE", "Rate Inquiry"

    # Default friendly greeting
    if lang == "gu":
        return "Namaste! Shashvat Jewels ma aapnu swagat che. Sonana bhav ke diamond jewellery babate hun aapni shu sahay kari shaku chu?", "CONTINUE", intent
    elif lang == "hi":
        return "Namaste! Shashvat Jewels mein aapka swagat hai. Aaj sone ke rate ya diamond jewellery ke baare mein kya jankari chahiye?", "CONTINUE", intent
    else:
        return "Welcome to Shashvat Jewels! How may I assist you with our diamond and gold collections today?", "CONTINUE", intent
