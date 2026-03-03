from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Dict, Any
from datetime import date, datetime
from decimal import Decimal
from uuid import UUID
from enum import Enum

# Enums
class ShipmentStatus(str, Enum):
    IN_TRANSIT = "in_transit"
    DELAYED = "delayed"
    ARRIVED = "arrived"
    CANCELLED = "cancelled"

class DisruptionType(str, Enum):
    LABOR_STRIKE = "labor_strike"
    WEATHER = "weather"
    CONGESTION = "congestion"
    GEOPOLITICAL = "geopolitical"
    ACCIDENT = "accident"

# Auth & User Schemas
class Token(BaseModel):
    access_token: str
    token_type: str
    requires_mfa: bool = False

class TokenData(BaseModel):
    email: Optional[str] = None
    role: Optional[str] = None

class MFAVerify(BaseModel):
    email: str
    totp_code: str = Field(..., min_length=6, max_length=6)

class UserBase(BaseModel):
    email: str
    full_name: str
    role: str = "viewer"
    company_id: Optional[UUID] = None

class UserCreate(UserBase):
    password: str

class UserResponse(UserBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    is_active: bool
    mfa_enabled: bool
    created_at: datetime
    
class MFASetupResponse(BaseModel):
    secret: str
    qr_code_uri: str
    
# Company Schemas
class CompanyBase(BaseModel):
    name: str = Field(..., min_length=1, max_length=255)
    revenue_annual_millions: Decimal = Field(..., gt=0)
    gross_margin_percent: Decimal = Field(..., ge=0, le=1)
    risk_tolerance: Decimal = Field(..., ge=0, le=1)
    sla_weight: Decimal = Field(..., ge=0, le=1)
    working_capital_limit: Decimal = Field(..., gt=0)
    customer_churn_sensitivity: Decimal = Field(..., ge=0, le=1)
    sla_target_percent: Decimal = Field(..., ge=0, le=1)

class CompanyCreate(CompanyBase):
    pass

class CompanyResponse(CompanyBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime
    updated_at: datetime

# Port Schemas
class PortBase(BaseModel):
    code: str = Field(..., min_length=2, max_length=10)
    name: str = Field(..., min_length=1, max_length=255)
    region: str = Field(..., min_length=1, max_length=255)

class PortCreate(PortBase):
    pass

class PortResponse(PortBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    created_at: datetime

# SKU Schemas
class SKUBase(BaseModel):
    sku_code: str = Field(..., min_length=1, max_length=100)
    description: Optional[str] = None
    daily_demand: int = Field(..., ge=0)
    unit_price: Decimal = Field(..., ge=0)
    unit_margin: Decimal
    criticality_score: Decimal = Field(..., ge=0, le=1)

class SKUCreate(SKUBase):
    company_id: UUID

class SKUResponse(SKUBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    company_id: UUID
    created_at: datetime
    updated_at: datetime

# Inventory Schemas
class InventoryBase(BaseModel):
    on_hand_units: int = Field(default=0, ge=0)
    reserved_units: int = Field(default=0, ge=0)

class InventoryCreate(InventoryBase):
    sku_id: UUID

class InventoryResponse(InventoryBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    sku_id: UUID

# Shipment Schemas
class ShipmentBase(BaseModel):
    container_id: str = Field(..., min_length=1, max_length=100)
    quantity: int = Field(..., gt=0)
    original_arrival_date: date
    status: ShipmentStatus = ShipmentStatus.IN_TRANSIT

class ShipmentCreate(ShipmentBase):
    company_id: UUID
    sku_id: UUID
    port_id: UUID

class ShipmentResponse(ShipmentBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    company_id: UUID
    sku_id: UUID
    port_id: UUID
    created_at: datetime

# Disruption Schemas
class DisruptionBase(BaseModel):
    disruption_type: DisruptionType
    severity_score: Decimal = Field(..., ge=0, le=1)
    expected_delay_days: int = Field(..., gt=0)
    confidence_score: Decimal = Field(..., ge=0, le=1)

class DisruptionCreate(DisruptionBase):
    port_id: UUID

class DisruptionResponse(DisruptionBase):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    port_id: UUID
    is_active: bool
    detected_at: datetime
    resolved_at: Optional[datetime]

# Strategy Schemas
class StrategyResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    name: str
    description: Optional[str]
    air_freight_percent: Decimal
    reroute_percent: Decimal
    buffer_stock_percent: Decimal
    cost_multiplier_air: Decimal
    cost_multiplier_reroute: Decimal
    holding_cost_per_unit_per_day: Decimal

# Exposure Analysis Schemas
class SKUExposure(BaseModel):
    sku_id: UUID
    sku_code: str
    description: Optional[str]
    daily_demand: int
    unit_price: Decimal
    unit_margin: Decimal
    on_hand_units: int
    inventory_runway_days: int
    stockout_date: date
    revenue_at_risk: Decimal
    margin_at_risk: Decimal
    affected_shipment_ids: List[UUID]

class ExposureResult(BaseModel):
    disruption_id: UUID
    company_id: UUID
    affected_skus: List[SKUExposure]
    total_revenue_at_risk: Decimal
    total_margin_at_risk: Decimal
    total_affected_shipments: int
    total_affected_quantity: int

# Strategy Simulation Schemas
class StrategySimulation(BaseModel):
    strategy_id: UUID
    strategy_name: str
    description: str
    revenue_preserved: Decimal
    mitigation_cost: Decimal
    sla_achieved: Decimal
    sla_penalty_cost: Decimal
    net_financial_impact: Decimal
    working_capital_required: Decimal
    is_feasible: bool
    feasibility_reason: Optional[str]

class StrategyComparison(BaseModel):
    disruption_id: UUID
    simulations: List[StrategySimulation]
    optimal_strategy_id: UUID
    company_risk_profile: Dict[str, Any]

# Recommendation Schemas
class RecommendationResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    disruption_id: UUID
    selected_strategy: StrategyResponse
    confidence_score: Decimal
    reasoning: str
    revenue_preserved: Decimal
    mitigation_cost: Decimal
    sla_achieved: Decimal
    sla_penalty_cost: Decimal
    net_financial_impact: Decimal
    generated_email_supplier: Optional[str]
    generated_email_logistics: Optional[str]
    generated_executive_summary: Optional[str]
    requires_approval: bool
    approved_by: Optional[str]
    approved_at: Optional[datetime]
    created_at: datetime

class ApprovalRequest(BaseModel):
    approver_name: str = Field(..., min_length=1, max_length=255)
    notes: Optional[str] = None

# Dashboard Schema
class DashboardSummary(BaseModel):
    company: CompanyResponse
    active_disruption: Optional[DisruptionResponse]
    active_disruptions: List[DisruptionResponse] = []
    active_recommendation: Optional[RecommendationResponse]
    total_revenue_at_risk: Optional[Decimal]
    key_metrics: Dict[str, int]
    
class SeedDataResponse(BaseModel):
    success: bool
    message: str
    created_counts: Dict[str, int]

# Decision Outcome Schemas (ML Feedback Loop)
class DecisionOutcomeCreate(BaseModel):
    actual_delay_days: int = Field(..., gt=0)
    actual_revenue_lost: Decimal = Field(..., ge=0)
    actual_cost_incurred: Decimal = Field(..., ge=0)
    actual_sla_achieved: Decimal = Field(..., ge=0, le=1)
    feedback_notes: Optional[str] = None

class DecisionOutcomeResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: UUID
    recommendation_id: UUID
    disruption_id: UUID
    predicted_net_impact: Optional[Decimal]
    actual_net_impact: Optional[Decimal]
    prediction_error_pct: Optional[Decimal]
    was_optimal_in_hindsight: Optional[bool]
    feedback_notes: Optional[str]
    resolved_at: Optional[datetime]

# Explainability Schemas
class ExplainabilityTrace(BaseModel):
    risk_dna_weights: Dict[str, float]     # {"alpha": 0.3, "beta": 0.7, "delta": 0.72}
    decision_drivers: List[str]             # ["SLA risk exceeded threshold", ...]
    confidence_interval: Dict[str, float]   # {"low": ..., "expected": ..., "high": ...}
    alternative_considered: str
    override_risk: str

# Perception / News Detection Schemas
class NewsDetectionInput(BaseModel):
    headline: str = Field(..., min_length=5, max_length=500)
    body: Optional[str] = Field(default="", max_length=5000)

class NewsDetectionResult(BaseModel):
    is_disruption: bool
    port_name: Optional[str]
    port_code: Optional[str]
    disruption_type: Optional[str]
    severity_score: float
    expected_delay_days: Optional[int]
    confidence: float
    summary: str
    created_disruption_id: Optional[UUID] = None

