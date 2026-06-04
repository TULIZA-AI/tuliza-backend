from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers import triage, facilities, aftercare
from services.triage_service import get_model_info

app = FastAPI(
    title="Tuliza AI API",
    description=(
        "AI-powered early pregnancy loss care navigation platform. "
        "Built for the AI for Reproductive Health in Africa Innovation Challenge."
    ),
    version="1.0.0",
    contact={
        "name": "Team Tuliza AI",
        "email": "team@tuliza.ai",
    },
)

# Allow React dev server to talk to FastAPI
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
app.include_router(triage.router)
app.include_router(facilities.router)
app.include_router(aftercare.router)


@app.get("/", tags=["Health"])
def root():
    return {
        "service": "Tuliza AI API",
        "version": "1.0.0",
        "status":  "running",
        "docs":    "/docs",
    }


@app.get("/health", tags=["Health"])
def health_check():
    model_info = get_model_info()
    return {
        "api_status":   "ok",
        "model_status": model_info["status"],
        "model_type":   model_info.get("model_type"),
        "model_auc":    model_info.get("auc"),
        "model_recall": model_info.get("recall"),
    }

