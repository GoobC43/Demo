"""
Perception Router — LLM-Based Disruption Detection Endpoint
=============================================================
Per Arch.tex §3.1: Detect disruption events from news text.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app import schemas
from app.services.perception import PerceptionService

router = APIRouter(prefix="/api/v1", tags=["perception"])


@router.post("/disruptions/detect", response_model=schemas.NewsDetectionResult)
def detect_disruption_from_news(
    payload: schemas.NewsDetectionInput,
    auto_create: bool = True,
    db: Session = Depends(get_db),
):
    """
    Classify news text as a maritime disruption using LLM.
    If auto_create=True and a disruption is detected, creates a Disruption record.
    """
    svc = PerceptionService(db)
    classification = svc.classify_news(payload.headline, payload.body or "")

    result = schemas.NewsDetectionResult(
        is_disruption=classification["is_disruption"],
        port_name=classification.get("port_name"),
        port_code=classification.get("port_code"),
        disruption_type=classification.get("disruption_type"),
        severity_score=classification.get("severity_score", 0.0),
        expected_delay_days=classification.get("expected_delay_days"),
        confidence=classification.get("confidence", 0.0),
        summary=classification.get("summary", ""),
    )

    if auto_create and classification["is_disruption"]:
        disruption = svc.detect_and_create(payload.headline, payload.body or "")
        if disruption:
            result.created_disruption_id = disruption.id

    return result
