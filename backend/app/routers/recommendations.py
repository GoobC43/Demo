from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from uuid import UUID
from datetime import datetime
import json
from app.auth import get_current_user

router = APIRouter()

@router.post("/{id}/approve", response_model=schemas.RecommendationResponse)
def approve_recommendation(
    id: UUID, 
    req: schemas.ApprovalRequest, 
    db: Session = Depends(get_db),
    current_user: dict = Depends(get_current_user)
):
    """Human-in-the-loop approval workflow."""
    rec = db.query(models.Recommendation).filter(models.Recommendation.id == id).first()
    if not rec:
        raise HTTPException(status_code=404, detail="Recommendation not found")

    if not rec.requires_approval:
        raise HTTPException(status_code=400, detail="Already approved")

    rec.requires_approval = False
    rec.approved_by = req.approver_name
    rec.approved_at = datetime.utcnow()

    # Resolve the disruption implicitly
    disruption = db.query(models.Disruption).filter(models.Disruption.id == rec.disruption_id).first()
    if disruption:
        disruption.is_active = False
        disruption.resolved_at = datetime.utcnow()


    # Create Audit Log Entry
    audit_entry = models.AuditLog(
        user_email=current_user.get("email", req.approver_name),
        action_type="APPROVE_RECOMMENDATION",
        resource_id=str(rec.id),
        previous_state=json.dumps({"requires_approval": True, "disruption_active": True}),
        new_state=json.dumps({
            "requires_approval": False, 
            "approved_by": req.approver_name,
            "disruption_active": False
        })
    )
    db.add(audit_entry)

    db.commit()
    db.refresh(rec)

    strategy = db.query(models.Strategy).filter(models.Strategy.id == rec.selected_strategy_id).first()
    rec_dict = {c.key: getattr(rec, c.key) for c in rec.__table__.columns}
    rec_dict["selected_strategy"] = strategy
    return schemas.RecommendationResponse.model_validate(rec_dict)
