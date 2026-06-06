import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app

client = TestClient(app)


def test_nlp_high_risk_english():
    r = client.post("/api/nlp/symptom-triage", json={
        "text": "heavy bleeding and fever since yesterday, feeling very dizzy",
    })
    assert r.status_code == 200
    d = r.json()
    assert d["urgency"] == "HIGH"
    assert d["keyword_count"] >= 1
    assert "recommendation" in d


def test_nlp_high_risk_swahili():
    r = client.post("/api/nlp/symptom-triage", json={
        "text": "ana damu nyingi na homa kali sana leo",
    })
    assert r.status_code == 200
    assert r.json()["urgency"] == "HIGH"


def test_nlp_low_risk():
    r = client.post("/api/nlp/symptom-triage", json={
        "text": "mild pain, bleeding has stopped, feeling better today",
    })
    assert r.status_code == 200
    assert r.json()["urgency"] in ["LOW", "MEDIUM"]


def test_nlp_empty_text():
    r = client.post("/api/nlp/symptom-triage", json={"text": "  "})
    assert r.status_code in [400, 422]


def test_nlp_response_structure():
    r = client.post("/api/nlp/symptom-triage", json={
        "text": "some cramping and light bleeding",
    })
    d = r.json()
    for field in ["urgency", "confidence", "symptoms_detected",
                  "keyword_count", "recommendation"]:
        assert field in d, f"Missing: {field}"