import pickle
import pandas as pd
from pathlib import Path

MODEL_DIR = Path(__file__).parent.parent / "tuliza_model"


def _load_artifacts():
    with open(MODEL_DIR / "triage_pipeline.pkl", "rb") as f:
        pipeline = pickle.load(f)
    with open(MODEL_DIR / "model_meta.pkl", "rb") as f:
        meta = pickle.load(f)
    return pipeline, meta


# Load once at import time — not on every request
try:
    _pipeline, _meta = _load_artifacts()
    MODEL_LOADED = True
except Exception as e:
    print(f"  Model load failed: {e}")
    MODEL_LOADED = False
    _pipeline, _meta = None, None


def predict_risk(
    type_of_loss:    str,
    gestational_age: float,
    place_of_loss:   str,
    slum_resident:   str,
) -> dict:
    """
    Run inference and return structured risk result.
    """
    if not MODEL_LOADED:
        raise RuntimeError("Model not loaded. Check tuliza_model/ directory.")

    df = pd.DataFrame([{
        "q4_05": gestational_age,
        "q4_04": type_of_loss,
        "q4_09": place_of_loss,
        "slum":  slum_resident,
    }])

    prob_formal_care = float(_pipeline.predict_proba(df)[0][1])
    risk_score       = round(1.0 - prob_formal_care, 3)
    risk_percent     = int(risk_score * 100)

    # Thresholds — tuned for high recall (clinical priority)
    if risk_score >= 0.60:
        risk_level       = "HIGH"
        seek_formal_care = True
        message = (
            "This woman is at high risk of not accessing formal care. "
            "Immediate CHV follow-up and referral to the nearest "
            "equipped facility is strongly recommended."
        )
        action    = "REFER_NOW"
        next_step = (
            "Contact the nearest health facility immediately. "
            "Use the Facility Finder below to locate the closest "
            "post-abortion care provider."
        )

    elif risk_score >= 0.40:
        risk_level       = "MEDIUM"
        seek_formal_care = False
        message = (
            "Moderate risk of delayed or missed care. Provide information "
            "on the nearest facility and schedule a follow-up "
            "check within 24 hours."
        )
        action    = "SCHEDULE_FOLLOWUP"
        next_step = (
            "Share facility information with the woman. Schedule a "
            "follow-up call or visit within 24 hours to confirm "
            "she has accessed care."
        )

    else:
        risk_level       = "LOW"
        seek_formal_care = False
        message = (
            "Lower risk profile. Provide emotional support, "
            "post-loss care information, and monitor for any "
            "change in condition."
        )
        action    = "PROVIDE_INFO"
        next_step = (
            "Offer aftercare resources and emotional support. "
            "Check in within 48–72 hours."
        )

    return {
        "risk_score":       risk_score,
        "risk_level":       risk_level,
        "risk_percent":     risk_percent,
        "seek_formal_care": seek_formal_care,
        "message":          message,
        "action":           action,
        "next_step":        next_step,
    }


def get_model_info() -> dict:
    if not MODEL_LOADED:
        return {"status": "unavailable"}
    return {
        "status":       "loaded",
        "model_type":   _meta.get("best_model", "unknown"),
        "auc":          _meta.get("auc", 0),
        "recall":       _meta.get("recall", 0),
        "features":     (_meta.get("numeric_features", []) +
                         _meta.get("categorical_features", [])),
    }
