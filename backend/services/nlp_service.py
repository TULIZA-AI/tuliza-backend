from transformers import pipeline
from functools import lru_cache

# ── Symptom keyword map ───────────────────────────────────────────────────────
KEYWORDS = {
    # HIGH risk — English
    "heavy bleeding":   {"flag": "HIGH",   "clinical": "Haemorrhage risk"},
    "bleeding a lot":   {"flag": "HIGH",   "clinical": "Haemorrhage risk"},
    "severe pain":      {"flag": "HIGH",   "clinical": "Severe complication"},
    "intense pain":     {"flag": "HIGH",   "clinical": "Severe complication"},
    "fever":            {"flag": "HIGH",   "clinical": "Infection / sepsis risk"},
    "high temperature": {"flag": "HIGH",   "clinical": "Infection risk"},
    "fainting":         {"flag": "HIGH",   "clinical": "Haemodynamic instability"},
    "fainted":          {"flag": "HIGH",   "clinical": "Haemodynamic instability"},
    "dizzy":            {"flag": "HIGH",   "clinical": "Possible blood loss"},
    "can't stand":      {"flag": "HIGH",   "clinical": "Severe weakness"},
    "foul smell":       {"flag": "HIGH",   "clinical": "Sepsis risk"},
    "smells bad":       {"flag": "HIGH",   "clinical": "Sepsis risk"},
    "no movement":      {"flag": "HIGH",   "clinical": "Fetal concern"},
    # HIGH risk — Swahili
    "damu nyingi":      {"flag": "HIGH",   "clinical": "Haemorrhage (SW)"},
    "kutokwa damu":     {"flag": "HIGH",   "clinical": "Bleeding (SW)"},
    "maumivu makali":   {"flag": "HIGH",   "clinical": "Severe pain (SW)"},
    "homa":             {"flag": "HIGH",   "clinical": "Fever (SW)"},
    "kizunguzungu":     {"flag": "HIGH",   "clinical": "Dizziness (SW)"},
    "harufu mbaya":     {"flag": "HIGH",   "clinical": "Foul discharge (SW)"},
    "kuzirai":          {"flag": "HIGH",   "clinical": "Fainting (SW)"},
    # MEDIUM risk — English
    "cramping":         {"flag": "MEDIUM", "clinical": "Normal post-loss symptom"},
    "some bleeding":    {"flag": "MEDIUM", "clinical": "Monitor bleeding"},
    "light bleeding":   {"flag": "MEDIUM", "clinical": "Monitor bleeding"},
    "nausea":           {"flag": "MEDIUM", "clinical": "GI symptom"},
    "tired":            {"flag": "MEDIUM", "clinical": "Fatigue"},
    "passed tissue":    {"flag": "MEDIUM", "clinical": "Possible incomplete loss"},
    "tissue":           {"flag": "MEDIUM", "clinical": "Possible incomplete loss"},
    # MEDIUM risk — Swahili
    "maumivu kidogo":   {"flag": "MEDIUM", "clinical": "Mild pain (SW)"},
    "kichefuchefu":     {"flag": "MEDIUM", "clinical": "Nausea (SW)"},
    "uchovu":           {"flag": "MEDIUM", "clinical": "Fatigue (SW)"},
    # LOW risk — English
    "no bleeding":      {"flag": "LOW",    "clinical": "No haemorrhage sign"},
    "bleeding stopped": {"flag": "LOW",    "clinical": "Haemorrhage resolving"},
    "feeling better":   {"flag": "LOW",    "clinical": "Improving"},
    "mild pain":        {"flag": "LOW",    "clinical": "Manageable discomfort"},
    # LOW risk — Swahili
    "damu imesimama":   {"flag": "LOW",    "clinical": "Bleeding stopped (SW)"},
    "najisikia vizuri": {"flag": "LOW",    "clinical": "Feeling better (SW)"},
}

URGENCY_LABELS = [
    "medical emergency requiring immediate care",
    "moderate symptoms needing follow-up care",
    "mild symptoms requiring monitoring only",
]

LABEL_TO_RISK = {
    "medical emergency requiring immediate care": "HIGH",
    "moderate symptoms needing follow-up care":   "MEDIUM",
    "mild symptoms requiring monitoring only":    "LOW",
}

RECOMMENDATIONS = {
    "HIGH":   "Immediate referral required. Use the Facility Finder now.",
    "MEDIUM": "Schedule follow-up within 24 hours. Monitor closely.",
    "LOW":    "Provide aftercare information. Check in within 48–72 hours.",
}


@lru_cache(maxsize=1)
def _load_classifier():
    print("Loading NLP model — this happens once...")
    clf = pipeline(
        "zero-shot-classification",
        model="typeform/distilbart-mnli-12-3",  # 250MB — fast on CPU
        device=-1,
    )
    print("NLP model loaded.")
    return clf


def analyse_symptoms(text: str) -> dict:
    text_lower = text.lower().strip()

    # 1. Fast keyword scan
    detected     = []
    keyword_flags = []
    for kw, meta in KEYWORDS.items():
        if kw in text_lower:
            detected.append({
                "term":     kw,
                "flag":     meta["flag"],
                "clinical": meta["clinical"],
            })
            keyword_flags.append(meta["flag"])

    # 2. Zero-shot NLP
    nlp_risk   = "MEDIUM"
    confidence = 0.0
    nlp_label  = "keyword-only"

    try:
        clf    = _load_classifier()
        result = clf(text, URGENCY_LABELS, multi_label=False)
        nlp_label  = result["labels"][0]
        confidence = round(float(result["scores"][0]), 3)
        nlp_risk   = LABEL_TO_RISK[nlp_label]
    except Exception as e:
        print(f" NLP model error: {e}")

    # 3. Reconcile — keywords override if HIGH detected
    if "HIGH" in keyword_flags:
        final_risk = "HIGH"
    elif nlp_risk == "HIGH" and confidence >= 0.65:
        final_risk = "HIGH"
    elif "MEDIUM" in keyword_flags or nlp_risk == "MEDIUM":
        final_risk = "MEDIUM"
    elif "LOW" in keyword_flags and nlp_risk == "LOW":
        final_risk = "LOW"
    else:
        final_risk = nlp_risk

    return {
        "input_text":        text,
        "urgency":           final_risk,
        "confidence":        confidence,
        "symptoms_detected": detected,
        "nlp_label":         nlp_label,
        "keyword_count":     len(detected),
        "recommendation":    RECOMMENDATIONS[final_risk],
    }