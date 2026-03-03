import uuid
from decimal import Decimal
from datetime import datetime
from sqlalchemy import Column, String, Integer, Numeric, Boolean, DateTime, ForeignKey, Date
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from app.database import Base
from enum import Enum as PyEnum

class UserRole(str, PyEnum):
    VIEWER = "viewer"
    PLANNER = "planner"
    VP_SUPPLY_CHAIN = "vp_supply_chain"

class User(Base):
    __tablename__ = 'users'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String(255), nullable=False)
    role = Column(String(50), default=UserRole.VIEWER.value, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    totp_secret = Column(String(32), nullable=True) # For Google Authenticator
    mfa_enabled = Column(Boolean, default=False, nullable=False)
    # Optional: tie to a specific company for multi-tenancy
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='SET NULL'), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Company(Base):
    __tablename__ = 'companies'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(255), nullable=False)
    revenue_annual_millions = Column(Numeric(10, 2), nullable=False)
    gross_margin_percent = Column(Numeric(5, 4), nullable=False)
    risk_tolerance = Column(Numeric(5, 4), nullable=False)
    sla_weight = Column(Numeric(5, 4), nullable=False)
    working_capital_limit = Column(Numeric(15, 2), nullable=False)
    customer_churn_sensitivity = Column(Numeric(5, 4), nullable=False)
    sla_target_percent = Column(Numeric(5, 4), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Port(Base):
    __tablename__ = 'ports'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    code = Column(String(10), unique=True, nullable=False)
    name = Column(String(255), nullable=False)
    region = Column(String(255), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class SKU(Base):
    __tablename__ = 'skus'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    sku_code = Column(String(100), nullable=False)
    description = Column(String)
    daily_demand = Column(Integer, nullable=False)
    unit_price = Column(Numeric(12, 2), nullable=False)
    unit_margin = Column(Numeric(12, 2), nullable=False)
    criticality_score = Column(Numeric(5, 4), nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Inventory(Base):
    __tablename__ = 'inventory'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sku_id = Column(UUID(as_uuid=True), ForeignKey('skus.id', ondelete='CASCADE'), unique=True, nullable=False)
    on_hand_units = Column(Integer, default=0, nullable=False)
    reserved_units = Column(Integer, default=0, nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Shipment(Base):
    __tablename__ = 'shipments'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    sku_id = Column(UUID(as_uuid=True), ForeignKey('skus.id', ondelete='CASCADE'), nullable=False)
    port_id = Column(UUID(as_uuid=True), ForeignKey('ports.id', ondelete='RESTRICT'), nullable=False)
    container_id = Column(String(100), nullable=False)
    quantity = Column(Integer, nullable=False)
    original_arrival_date = Column(Date, nullable=False)
    status = Column(String(20), default='in_transit', nullable=False)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at = Column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

class Disruption(Base):
    __tablename__ = 'disruptions'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    port_id = Column(UUID(as_uuid=True), ForeignKey('ports.id', ondelete='RESTRICT'), nullable=False)
    disruption_type = Column(String(50), nullable=False)
    severity_score = Column(Numeric(5, 4), nullable=False)
    expected_delay_days = Column(Integer, nullable=False)
    confidence_score = Column(Numeric(5, 4), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    detected_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class Strategy(Base):
    __tablename__ = 'strategies'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(String(100), unique=True, nullable=False)
    description = Column(String)
    air_freight_percent = Column(Numeric(5, 4), nullable=False)
    reroute_percent = Column(Numeric(5, 4), nullable=False)
    buffer_stock_percent = Column(Numeric(5, 4), nullable=False)
    cost_multiplier_air = Column(Numeric(5, 2), default=8.0, nullable=False)
    cost_multiplier_reroute = Column(Numeric(5, 2), default=1.3, nullable=False)
    holding_cost_per_unit_per_day = Column(Numeric(10, 4), default=0.50, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)

class Recommendation(Base):
    __tablename__ = 'recommendations'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    disruption_id = Column(UUID(as_uuid=True), ForeignKey('disruptions.id', ondelete='CASCADE'), nullable=False)
    selected_strategy_id = Column(UUID(as_uuid=True), ForeignKey('strategies.id'), nullable=False)
    confidence_score = Column(Numeric(5, 4), nullable=False)
    reasoning = Column(String, nullable=False)
    revenue_preserved = Column(Numeric(15, 2), nullable=False)
    mitigation_cost = Column(Numeric(15, 2), nullable=False)
    sla_achieved = Column(Numeric(5, 4), nullable=False)
    sla_penalty_cost = Column(Numeric(15, 2), default=0, nullable=False)
    net_financial_impact = Column(Numeric(15, 2), nullable=False)
    generated_email_supplier = Column(String, nullable=True)
    generated_email_logistics = Column(String, nullable=True)
    generated_executive_summary = Column(String, nullable=True)
    requires_approval = Column(Boolean, default=True, nullable=False)
    approved_by = Column(String(255), nullable=True)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)

class DecisionOutcome(Base):
    """ML Feedback Loop: tracks predicted vs actual results for learning."""
    __tablename__ = 'decision_outcomes'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    recommendation_id = Column(UUID(as_uuid=True), ForeignKey('recommendations.id', ondelete='CASCADE'), nullable=False)
    disruption_id = Column(UUID(as_uuid=True), ForeignKey('disruptions.id', ondelete='CASCADE'), nullable=False)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=True)

    # Predicted values (snapshot at recommendation time)
    predicted_delay_days = Column(Integer, nullable=True)
    predicted_revenue_risk = Column(Numeric(15, 2), nullable=True)
    predicted_net_impact = Column(Numeric(15, 2), nullable=True)
    selected_strategy_id = Column(UUID(as_uuid=True), ForeignKey('strategies.id'), nullable=True)

    # Actual values (filled post-resolution)
    actual_delay_days = Column(Integer, nullable=True)
    actual_revenue_lost = Column(Numeric(15, 2), nullable=True)
    actual_cost_incurred = Column(Numeric(15, 2), nullable=True)
    actual_sla_achieved = Column(Numeric(5, 4), nullable=True)
    actual_net_impact = Column(Numeric(15, 2), nullable=True)

    # Learning metadata
    prediction_error_pct = Column(Numeric(8, 4), nullable=True)
    was_optimal_in_hindsight = Column(Boolean, nullable=True)
    feedback_notes = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
    resolved_at = Column(DateTime(timezone=True), nullable=True)

class AuditLog(Base):
    """Immutable audit trail for all business-critical actions."""
    __tablename__ = 'audit_logs'
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    company_id = Column(UUID(as_uuid=True), ForeignKey('companies.id', ondelete='CASCADE'), nullable=True)
    user_email = Column(String(255), nullable=True) # Identifying who did it (even if user is deleted)
    action_type = Column(String(100), nullable=False) # e.g. "APPROVE_RECOMMENDATION"
    resource_id = Column(String(255), nullable=True)  # ID of the affected resource (Disruption/Recommendation)
    previous_state = Column(String, nullable=True)    # JSON string representation
    new_state = Column(String, nullable=True)         # JSON string representation
    ip_address = Column(String(50), nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow)
