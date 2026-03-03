"""
Learning Router — Decision Outcomes & Feedback Loop Endpoints
==============================================================
Records actual disruption outcomes, retrieves history,
and provides Risk DNA calibration suggestions.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
from typing import Optional

from app.database import get_db
from app import schemas
from app.services.learning import LearningService

router = APIRouter(prefix="/api/v1", tags=["learning"])


@router.post("/outcomes/{recommendation_id}", response_model=schemas.DecisionOutcomeResponse)
def record_outcome(
    recommendation_id: UUID,
    outcome: schemas.DecisionOutcomeCreate,
    db: Session = Depends(get_db),
):
    """Record the actual outcome after a disruption resolves."""
    try:
        svc = LearningService(db)
        result = svc.record_outcome(
            recommendation_id=recommendation_id,
            actual_delay_days=outcome.actual_delay_days,
            actual_revenue_lost=outcome.actual_revenue_lost,
            actual_cost_incurred=outcome.actual_cost_incurred,
            actual_sla_achieved=outcome.actual_sla_achieved,
            feedback_notes=outcome.feedback_notes,
        )
        return result
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@router.get("/outcomes/history")
def get_outcome_history(
    company_id: Optional[UUID] = None,
    limit: int = 20,
    db: Session = Depends(get_db),
):
    """Retrieve past decision outcomes and prediction accuracy."""
    svc = LearningService(db)
    return svc.get_outcome_history(company_id=company_id, limit=limit)


@router.get("/strategies/{strategy_id}/confidence")
def get_strategy_confidence(
    strategy_id: UUID,
    disruption_type: str = "labor_strike",
    db: Session = Depends(get_db),
):
    """Get Bayesian confidence score for a strategy + disruption type combo."""
    svc = LearningService(db)
    return svc.get_strategy_confidence(strategy_id, disruption_type)


@router.get("/companies/{company_id}/calibration")
def get_risk_dna_calibration(
    company_id: UUID,
    db: Session = Depends(get_db),
):
    """Get Risk DNA calibration suggestions based on historical outcomes."""
    svc = LearningService(db)
    return svc.calibrate_risk_dna(company_id)
