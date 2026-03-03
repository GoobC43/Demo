"""
Risk Correlation API Router
=============================
Exposes disruption clustering, archetype matching, and portfolio risk endpoints.
"""

from fastapi import APIRouter, Depends, Query
from uuid import UUID
from sqlalchemy.orm import Session
from typing import Optional

from app.database import get_db
from app.services.risk_correlation import RiskCorrelationEngine

router = APIRouter(prefix="/risk", tags=["Risk Correlation"])


@router.get("/archetypes")
def get_disruption_archetypes(
    n_clusters: Optional[int] = Query(4, ge=2, le=10),
    db: Session = Depends(get_db),
):
    """Get K-Means disruption archetype clusters."""
    engine = RiskCorrelationEngine(db)
    return engine.cluster_disruptions(n_clusters=n_clusters)


@router.get("/archetypes/{disruption_id}/match")
def match_disruption_archetype(
    disruption_id: UUID,
    db: Session = Depends(get_db),
):
    """Find the closest archetype match for a given disruption."""
    engine = RiskCorrelationEngine(db)
    return engine.match_archetype(disruption_id)


@router.get("/portfolio")
def get_portfolio_risk(db: Session = Depends(get_db)):
    """
    Get portfolio-level risk analysis: correlation matrix,
    diversification benefit, and concentration risk.
    """
    engine = RiskCorrelationEngine(db)
    return engine.portfolio_risk()
