from fastapi import APIRouter
from models.schema import FacilityQuery, FacilityResponse, Facility

router = APIRouter(prefix="/api/facilities", tags=["Facilities"])

# Static facility data based on APHRC Nairobi coverage areas
# In a real pilot this would be a database query
FACILITIES: list[dict] = [
    {
        "id": 1,
        "name": "Kenyatta National Hospital",
        "type": "Public Hospital",
        "level": "Level 6 — National Referral",
        "location": "Nairobi non-slum",
        "distance_km": 4.2,
        "pac_capacity": "High",
        "phone": "+254 20 272 6300",
        "services": ["PAC", "MVA", "Medical management",
                     "Counselling", "Family planning"],
        "stock_status": "Available",
    },
    {
        "id": 2,
        "name": "Mathare North Health Centre",
        "type": "Public Health Centre",
        "level": "Level 3",
        "location": "Non-DSA Nairobi slum",
        "distance_km": 1.1,
        "pac_capacity": "Medium",
        "phone": "+254 20 000 0001",
        "services": ["PAC", "Counselling", "Family planning",
                     "Referral support"],
        "stock_status": "Available",
    },
    {
        "id": 3,
        "name": "Korogocho Health Centre",
        "type": "Public Health Centre",
        "level": "Level 3",
        "location": "Within same DSA Slum",
        "distance_km": 0.8,
        "pac_capacity": "Medium",
        "phone": "+254 20 000 0002",
        "services": ["PAC", "Counselling", "Family planning"],
        "stock_status": "Limited",
    },
    {
        "id": 4,
        "name": "Marie Stopes Kenya — Nairobi",
        "type": "Private NGO Clinic",
        "level": "Level 4",
        "location": "Nairobi non-slum",
        "distance_km": 3.5,
        "pac_capacity": "High",
        "phone": "+254 709 992 000",
        "services": ["PAC", "MVA", "Medical management",
                     "Counselling", "Family planning", "SGBV support"],
        "stock_status": "Available",
    },
    {
        "id": 5,
        "name": "Pumwani Maternity Hospital",
        "type": "Public Hospital",
        "level": "Level 5",
        "location": "Non-DSA Nairobi slum",
        "distance_km": 2.3,
        "pac_capacity": "High",
        "phone": "+254 20 222 3000",
        "services": ["PAC", "Emergency obstetric care",
                     "Counselling", "Family planning"],
        "stock_status": "Available",
    },
    {
        "id": 6,
        "name": "Mombasa County Referral Hospital",
        "type": "Public Hospital",
        "level": "Level 5",
        "location": "Other Urban area of Kenya",
        "distance_km": 8.0,
        "pac_capacity": "High",
        "phone": "+254 41 231 0000",
        "services": ["PAC", "MVA", "Emergency care",
                     "Counselling", "Family planning"],
        "stock_status": "Available",
    },
    {
        "id": 7,
        "name": "Homa Bay County Hospital",
        "type": "Public Hospital",
        "level": "Level 5",
        "location": "Rural Kenya",
        "distance_km": 12.0,
        "pac_capacity": "Medium",
        "phone": "+254 59 000 0001",
        "services": ["PAC", "Counselling", "Family planning"],
        "stock_status": "Limited",
    },
]

# Priority order for stock status
STOCK_PRIORITY = {"Available": 0, "Limited": 1, "Out": 2}


def _score_facility(f: dict, risk_level: str) -> float:
    """
    Score a facility for a given risk level.
    HIGH risk → prioritise PAC capacity + stock + distance.
    MEDIUM/LOW → distance + services.
    """
    score = 0.0
    if risk_level == "HIGH":
        score -= f["distance_km"] * 2.0
        score += {"High": 30, "Medium": 15, "Low": 5}.get(f["pac_capacity"], 0)
        score -= STOCK_PRIORITY[f["stock_status"]] * 10
    else:
        score -= f["distance_km"] * 1.0
        score += len(f["services"]) * 2
        score -= STOCK_PRIORITY[f["stock_status"]] * 5
    return score


@router.post("/find", response_model=FacilityResponse,
             summary="Find nearest equipped facilities")
def find_facilities(query: FacilityQuery):
    """
    Returns ranked facilities based on location, risk level,
    and stock availability.  HIGH risk cases get PAC-capable
    facilities ranked first regardless of distance.
    """
    scored = [
        (f, _score_facility(f, query.risk_level))
        for f in FACILITIES
        if f["stock_status"] != "Out"          # never send to stocked-out facility
    ]
    ranked = [f for f, _ in sorted(scored, key=lambda x: x[1], reverse=True)]

    return FacilityResponse(
        query_location=query.location,
        facilities=[Facility(**f) for f in ranked[:4]],   # top 4
        total_found=len(ranked),
    )

