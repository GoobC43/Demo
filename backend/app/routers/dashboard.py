from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from uuid import UUID
from decimal import Decimal

router = APIRouter()

@router.get("/dashboard", response_model=schemas.DashboardSummary)
def get_dashboard(db: Session = Depends(get_db)):
    """Main dashboard data load."""
    
    # 1. Get single company (MVP assumption)
    company = db.query(models.Company).first()
    if not company:
        raise HTTPException(status_code=404, detail="No company found. Run /seed-data first.")
        
    company_obj = schemas.CompanyResponse.model_validate(company)
    
    # 2. Get ALL active disruptions
    active_disruptions = db.query(models.Disruption).filter(models.Disruption.is_active == True).all()
    
    disruption_objs = [schemas.DisruptionResponse.model_validate(d) for d in active_disruptions]
    
    # Primary disruption (first/highest severity) for backward compat
    primary_disruption = max(active_disruptions, key=lambda d: d.severity_score) if active_disruptions else None
    primary_disruption_obj = schemas.DisruptionResponse.model_validate(primary_disruption) if primary_disruption else None
    
    recommendation_obj = None
    revenue_risk = Decimal("0.0")
    total_affected_skus = set()
    total_affected_shipments = 0
    
    # 3. Aggregate metrics across ALL active disruptions
    for disruption in active_disruptions:
        shipments = db.query(models.Shipment).filter(models.Shipment.port_id == disruption.port_id).all()
        
        if shipments:
            sku_ids = list(set([s.sku_id for s in shipments]))
            total_affected_shipments += len(shipments)
            total_affected_skus.update(sku_ids)
            
            skus = db.query(models.SKU).filter(models.SKU.id.in_(sku_ids)).all()
            inventory = {i.sku_id: i.on_hand_units for i in db.query(models.Inventory).filter(models.Inventory.sku_id.in_(sku_ids)).all()}
            
            for sku in skus:
                on_hand = inventory.get(sku.id, 0)
                runway = int(on_hand / sku.daily_demand) if sku.daily_demand > 0 else 999
                delay_gap = max(0, int(disruption.expected_delay_days) - runway)
                revenue_risk += Decimal(str(delay_gap * sku.daily_demand)) * sku.unit_price
    
    # 4. Get latest recommendation for the primary disruption
    if primary_disruption:
        latest_rec = db.query(models.Recommendation).filter(models.Recommendation.disruption_id == primary_disruption.id).order_by(models.Recommendation.created_at.desc()).first()
        if latest_rec:
            strategy = db.query(models.Strategy).filter(models.Strategy.id == latest_rec.selected_strategy_id).first()
            if strategy:
                rec_dict = {c.key: getattr(latest_rec, c.key) for c in latest_rec.__table__.columns}
                rec_dict["selected_strategy"] = strategy
                recommendation_obj = schemas.RecommendationResponse.model_validate(rec_dict)

    return schemas.DashboardSummary(
        company=company_obj,
        active_disruption=primary_disruption_obj,
        active_disruptions=disruption_objs,
        active_recommendation=recommendation_obj,
        total_revenue_at_risk=revenue_risk if revenue_risk > 0 else None,
        key_metrics={
            "affected_skus": len(total_affected_skus),
            "affected_shipments": total_affected_shipments,
        }
    )
