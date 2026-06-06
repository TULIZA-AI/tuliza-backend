from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from services.nlp_service import analyse_symptoms

router = APIRouter(prefix="/api/nlp", tags=["NLP"])


class SymptomInput(BaseModel):
    text:     str = Field(..., min_length=3,
                          description="Free text in English or Swahili")
    language: str = Field(default="en")


class SymptomOutput(BaseModel):
    input_text:        str
    urgency:           str
    confidence:        float
    symptoms_detected: list[dict]
    nlp_label:         str
    keyword_count:     int
    recommendation:    str


@router.post("/symptom-triage", response_model=SymptomOutput,
             summary="Analyse free-text symptom description (EN or SW)")
def symptom_triage(data: SymptomInput):
    if not data.text.strip():
        raise HTTPException(status_code=400, detail="Text cannot be empty.")
    return SymptomOutput(**analyse_symptoms(data.text))