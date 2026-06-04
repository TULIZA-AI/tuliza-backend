import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app

client = TestClient(app)


def test_health_check():
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["api_status"] == "ok"
    assert data["model_status"] == "loaded"


def test_triage_high_risk():
    """Slum resident, miscarriage — expected HIGH risk."""
    response = client.post("/api/triage/assess", json={
        "type_of_loss":    "Miscarriage",
        "gestational_age": 3.0,
        "place_of_loss":   "Within same DSA Slum",
        "slum_resident":   "Slum",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] in ["HIGH", "MEDIUM"]
    assert 0.0 <= data["risk_score"] <= 1.0
    assert isinstance(data["seek_formal_care"], bool)
    assert data["action"] in ["REFER_NOW", "SCHEDULE_FOLLOWUP", "PROVIDE_INFO"]


def test_triage_lower_risk():
    """Non-slum, abortion — expected lower risk."""
    response = client.post("/api/triage/assess", json={
        "type_of_loss":    "Abortion",
        "gestational_age": 6.0,
        "place_of_loss":   "Nairobi non-slum",
        "slum_resident":   "Non-slum",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["risk_level"] in ["LOW", "MEDIUM", "HIGH"]


def test_triage_invalid_gestational_age():
    """Gestational age out of range should return 422."""
    response = client.post("/api/triage/assess", json={
        "type_of_loss":    "Miscarriage",
        "gestational_age": 15.0,          # max is 9
        "place_of_loss":   "Rural Kenya",
        "slum_resident":   "Slum",
    })
    assert response.status_code == 422


def test_triage_invalid_loss_type():
    """Unknown loss type should return 422."""
    response = client.post("/api/triage/assess", json={
        "type_of_loss":    "Unknown Type",
        "gestational_age": 3.0,
        "place_of_loss":   "Rural Kenya",
        "slum_resident":   "Slum",
    })
    assert response.status_code == 422


def test_triage_all_loss_types():
    """All valid loss types should return 200."""
    for loss_type in ["Miscarriage", "Abortion", "Still Birth", "Refusal"]:
        response = client.post("/api/triage/assess", json={
            "type_of_loss":    loss_type,
            "gestational_age": 4.0,
            "place_of_loss":   "Nairobi non-slum",
            "slum_resident":   "Non-slum",
        })
        assert response.status_code == 200, f"Failed for loss type: {loss_type}"


def test_triage_response_structure():
    """Response must contain all required fields."""
    response = client.post("/api/triage/assess", json={
        "type_of_loss":    "Miscarriage",
        "gestational_age": 3.0,
        "place_of_loss":   "Within same DSA Slum",
        "slum_resident":   "Slum",
    })
    data = response.json()
    required_fields = [
        "risk_score", "risk_level", "risk_percent",
        "seek_formal_care", "message", "action", "next_step"
    ]
    for field in required_fields:
        assert field in data, f"Missing field: {field}"

