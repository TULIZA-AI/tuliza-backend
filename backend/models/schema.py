from pydantic import BaseModel, Field, ConfigDict
from typing import Optional
from enum import Enum


class LossType(str, Enum):
    miscarriage = "Miscarriage"
    abortion    = "Abortion"
    still_birth = "Still Birth"
    refusal     = "Refusal"


class PlaceOfLoss(str, Enum):
    within_dsa_slum  = "Within same DSA Slum"
    nairobi_non_slum = "Nairobi non-slum"
    non_dsa_slum     = "Non-DSA Nairobi slum"
    other_dsa_slum   = "Other DSA Nairobi slum"
    other_urban      = "Other Urban area of Kenya"
    rural_kenya      = "Rural Kenya"


class SlumStatus(str, Enum):
    slum     = "Slum"
    non_slum = "Non-slum"


class RiskLevel(str, Enum):
    high   = "HIGH"
    medium = "MEDIUM"
    low    = "LOW"


# ── Triage ────────────────────────────────────────────────────────────────────
class TriageInput(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    type_of_loss:    LossType    = Field(
        ..., json_schema_extra={"example": "Miscarriage"})
    gestational_age: float       = Field(
        ..., ge=0.5, le=9.0, json_schema_extra={"example": 3.0})
    place_of_loss:   PlaceOfLoss = Field(
        ..., json_schema_extra={"example": "Within same DSA Slum"})
    slum_resident:   SlumStatus  = Field(
        ..., json_schema_extra={"example": "Slum"})


class TriageOutput(BaseModel):
    risk_score:       float
    risk_level:       RiskLevel
    risk_percent:     int
    seek_formal_care: bool
    message:          str
    action:           str
    next_step:        str


# ── Facilities ────────────────────────────────────────────────────────────────
class Facility(BaseModel):
    id:           int
    name:         str
    type:         str
    level:        str
    location:     str
    distance_km:  float
    pac_capacity: str
    phone:        str
    services:     list[str]
    stock_status: str


class FacilityQuery(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    location:     str
    risk_level:   RiskLevel
    slum_context: bool = True


class FacilityResponse(BaseModel):
    query_location: str
    facilities:     list[Facility]
    total_found:    int


# ── Aftercare ─────────────────────────────────────────────────────────────────
class AftercareInput(BaseModel):
    model_config = ConfigDict(use_enum_values=True)

    loss_type:       LossType
    gestational_age: float
    risk_level:      RiskLevel
    language:        str = Field(default="en")


class AftercareOutput(BaseModel):
    language:          str
    emotional_support: str
    physical_guidance: str
    warning_signs:     list[str]
    follow_up:         str
    resources:         list[str]
