from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from uuid import UUID
from datetime import datetime

from app.services.exposure import ExposureService
from app.services.optimizer import OptimizerService
from app.services.llm_generator import LLMGeneratorService

router = APIRouter()

@router.get("/ports")
def get_ports(db: Session = Depends(get_db)):
    """Return all ports for name resolution."""
    ports = db.query(models.Port).all()
    return [{"id": str(p.id), "code": p.code, "name": p.name, "region": p.region} for p in ports]


@router.post("", response_model=schemas.DisruptionResponse)
def create_disruption(disruption: schemas.DisruptionCreate, db: Session = Depends(get_db)):
    """Create new disruption event."""
    
    port = db.query(models.Port).filter(models.Port.id == disruption.port_id).first()
    if not port:
        raise HTTPException(status_code=404, detail="Port not found")
        
    db_disruption = models.Disruption(**disruption.model_dump())
    db.add(db_disruption)
    db.commit()
    db.refresh(db_disruption)
    return db_disruption

@router.get("/{id}", response_model=schemas.DisruptionResponse)
def get_disruption(id: UUID, db: Session = Depends(get_db)):
    disruption = db.query(models.Disruption).filter(models.Disruption.id == id).first()
    if not disruption:
        raise HTTPException(status_code=404, detail="Disruption not found")
    return disruption

@router.get("/{id}/exposure", response_model=schemas.ExposureResult)
def get_exposure(id: UUID, db: Session = Depends(get_db)):
    """Calculate and return financial exposure."""
    svc = ExposureService(db)
    try:
        return svc.calculate_exposure(id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{id}/strategies", response_model=schemas.StrategyComparison)
def get_strategies(id: UUID, db: Session = Depends(get_db)):
    """Simulate all 4 strategies and return comparison."""
    svc = OptimizerService(db)
    try:
        return svc.simulate_strategies(id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))

@router.get("/{id}/recommendation", response_model=schemas.RecommendationResponse)
def get_recommendation(id: UUID, db: Session = Depends(get_db)):
    """Get or create recommendation with LLM-generated drafts."""
    
    # 1. Check if exists
    existing = db.query(models.Recommendation).filter(models.Recommendation.disruption_id == id).first()
    if existing:
        strategy = db.query(models.Strategy).filter(models.Strategy.id == existing.selected_strategy_id).first()
        rec_dict = {c.key: getattr(existing, c.key) for c in existing.__table__.columns}
        rec_dict["selected_strategy"] = strategy
        return schemas.RecommendationResponse.model_validate(rec_dict)
        
    # 2. Generate if not
    opt_svc = OptimizerService(db)
    try:
        comparison = opt_svc.simulate_strategies(id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
        
    optimal_sim = next((s for s in comparison.simulations if s.strategy_id == comparison.optimal_strategy_id), None)
    if not optimal_sim:
        raise HTTPException(status_code=500, detail="Could not simulate optimal strategy")
        
    strategy = db.query(models.Strategy).filter(models.Strategy.id == comparison.optimal_strategy_id).first()
    disruption = db.query(models.Disruption).filter(models.Disruption.id == id).first()
    port = db.query(models.Port).filter(models.Port.id == disruption.port_id).first()
    
    # Needs exposure for SKU counts
    exp_svc = ExposureService(db)
    exposure = exp_svc.calculate_exposure(id)
    company = db.query(models.Company).filter(models.Company.id == exposure.company_id).first()
    
    # 3. LLM Drafts
    llm = LLMGeneratorService()
    drafts = llm.generate_mitigation_drafts(
        company_name=company.name,
        disruption_type=disruption.disruption_type,
        port_name=port.name,
        delay_days=disruption.expected_delay_days,
        affected_skus_count=len(exposure.affected_skus),
        revenue_at_risk=exposure.total_revenue_at_risk,
        strategy_name=strategy.name,
        air_percent=float(strategy.air_freight_percent),
        reroute_percent=float(strategy.reroute_percent),
        buffer_percent=float(strategy.buffer_stock_percent),
        risk_tolerance=float(company.risk_tolerance),
        sla_target=float(company.sla_target_percent),
        working_capital=company.working_capital_limit
    )

    reasoning = "\n".join([
        f"Selected optimal strategy based on net financial impact of ${float(optimal_sim.net_financial_impact):,.0f}.",
        f"Maintains minimum viable working capital (Requires ${float(optimal_sim.mitigation_cost):,.0f} of ${float(company.working_capital_limit):,.0f}).",
        f"Protects {float(optimal_sim.sla_achieved):.1%} service level against {float(company.sla_target_percent):.1%} target."
    ])

    rec = models.Recommendation(
        disruption_id=id,
        selected_strategy_id=strategy.id,
        confidence_score=disruption.confidence_score,  # Align with disruption detection confidence
        reasoning=reasoning,
        revenue_preserved=optimal_sim.revenue_preserved,
        mitigation_cost=optimal_sim.mitigation_cost,
        sla_achieved=optimal_sim.sla_achieved,
        sla_penalty_cost=optimal_sim.sla_penalty_cost,
        net_financial_impact=optimal_sim.net_financial_impact,
        generated_email_supplier=drafts.get('supplier_email'),
        generated_email_logistics=drafts.get('logistics_email'),
        generated_executive_summary=drafts.get('executive_summary'),
        requires_approval=True
    )
    
    db.add(rec)
    db.commit()
    db.refresh(rec)
    
    rec_dict = {c.key: getattr(rec, c.key) for c in rec.__table__.columns}
    rec_dict["selected_strategy"] = strategy
    return schemas.RecommendationResponse.model_validate(rec_dict)
