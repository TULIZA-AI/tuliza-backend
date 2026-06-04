from fastapi import APIRouter, HTTPException
from models.schema import TriageInput, TriageOutput
from services.triage_service import predict_risk

router = APIRouter(prefix="/api/triage", tags=["Triage"])


@router.post("/assess", response_model=TriageOutput, summary="Assess care-seeking risk")
def assess_risk(data: TriageInput):
    """
    Takes clinical inputs about a pregnancy loss event and returns
    a structured risk assessment with recommended action.
    """
    try:
        result = predict_risk(
            type_of_loss=data.type_of_loss,
            gestational_age=data.gestational_age,
            place_of_loss=data.place_of_loss,
            slum_resident=data.slum_resident,
        )
        return TriageOutput(**result)
    except RuntimeError as e:
        raise HTTPException(status_code=503, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Inference error: {str(e)}")


