import pytest
from fastapi.testclient import TestClient
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent))
from main import app

client = TestClient(app)


def test_find_facilities_high_risk():
    response = client.post("/api/facilities/find", json={
        "location":     "Within same DSA Slum",
        "risk_level":   "HIGH",
        "slum_context": True,
    })
    assert response.status_code == 200
    data = response.json()
    assert "facilities" in data
    assert len(data["facilities"]) > 0

    # HIGH risk — no stocked-out facilities
    for f in data["facilities"]:
        assert f["stock_status"] != "Out"


def test_find_facilities_returns_max_4():
    response = client.post("/api/facilities/find", json={
        "location":   "Nairobi non-slum",
        "risk_level": "MEDIUM",
    })
    assert response.status_code == 200
    assert len(response.json()["facilities"]) <= 4


def test_facility_response_structure():
    response = client.post("/api/facilities/find", json={
        "location":   "Rural Kenya",
        "risk_level": "HIGH",
    })
    facility = response.json()["facilities"][0]
    required = [
        "id", "name", "type", "level", "location",
        "distance_km", "pac_capacity", "phone",
        "services", "stock_status"
    ]
    for field in required:
        assert field in facility, f"Missing field: {field}"


def test_aftercare_english():
    response = client.post("/api/aftercare/support", json={
        "loss_type":       "Miscarriage",
        "gestational_age": 3.0,
        "risk_level":      "HIGH",
        "language":        "en",
    })
    assert response.status_code == 200
    data = response.json()
    assert data["language"] == "en"
    assert len(data["warning_signs"]) > 0
    assert len(data["resources"]) > 0
    assert "TODAY" in data["follow_up"]   # HIGH risk = urgent message


def test_aftercare_swahili():
    response = client.post("/api/aftercare/support", json={
        "loss_type":       "Abortion",
        "gestational_age": 5.0,
        "risk_level":      "LOW",
        "language":        "sw",
    })
    assert response.status_code == 200
    assert response.json()["language"] == "sw"

