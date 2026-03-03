"""
Simulation Router — Monte Carlo + Sensitivity Analysis Endpoints
=================================================================
Provides probabilistic strategy outcome analysis.
"""

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID

from app.database import get_db
from app.services.monte_carlo import MonteCarloSimulator
from app.services.sensitivity import SensitivityAnalyzer

router = APIRouter(prefix="/api/v1", tags=["simulation"])


@router.get("/disruptions/{disruption_id}/simulation")
def run_monte_carlo(disruption_id: UUID, scenarios: int = 1000, db: Session = Depends(get_db)):
    """
    Monte Carlo simulation: sample delay from N(μ,σ²) and evaluate
    each strategy across N scenarios. Returns P5/P50/P95 bands.
    """
    try:
        n = min(max(scenarios, 100), 10000)  # Clamp to reasonable range
        simulator = MonteCarloSimulator(db, n_scenarios=n)
        return simulator.simulate(disruption_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")


@router.get("/disruptions/{disruption_id}/sensitivity")
def run_sensitivity_analysis(disruption_id: UUID, db: Session = Depends(get_db)):
    """
    Sensitivity (tornado) analysis: vary key parameters ±20% and measure
    impact on optimal strategy's net financial outcome.
    """
    try:
        analyzer = SensitivityAnalyzer(db)
        return analyzer.analyze(disruption_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Sensitivity analysis failed: {str(e)}")
