\# HarborGuard AI - Product Requirements Document (PRD)\
\
\*\*Version:\*\* 1.0\
\*\*Date:\*\* March 2025\
\*\*Status:\*\* MVP Development\
\*\*Target:\*\* Single coding agent or small dev team\
\
\-\--\
\
\## 1. Document Purpose\
\
This PRD provides exhaustive technical specifications for building
HarborGuard AI, a maritime supply chain disruption decision-support
platform. Every section contains actionable implementation details
including exact data structures, API contracts, algorithmic logic, and
UI specifications.\
\
\*\*After reading this document, a coding agent should be able to:\*\*\
- Generate complete database schemas\
- Implement all backend API endpoints\
- Build frontend components with exact props and state management\
- Configure third-party integrations (Gemini API)\
- Deploy the application using Docker\
\
\-\--\
\
\## 2. Product Overview\
\
\### 2.1 Problem Statement\
Mid-market electronics manufacturers (\$100M-\$300M revenue) lose 10-15%
of annual revenue to preventable supply chain disruptions. When port
disruptions occur, supply chain teams manually scramble across ERP
dashboards, spreadsheets, and email threads. By the time decisions are
made, millions in revenue are already at risk.\
\
\### 2.2 Solution\
HarborGuard AI is a decision-support web application that:\
1. Detects maritime disruption events (starting with manual input, mock
data for MVP)\
2. Automatically calculates financial exposure across inventory SKUs\
3. Simulates 4 predefined mitigation strategies with full financial
modeling\
4. Recommends optimal strategy based on company-specific \"Risk DNA\"
parameters\
5. Generates actionable execution drafts (supplier emails, logistics
requests, executive memos) via LLM\
\
\### 2.3 Core Value Proposition\
Transform a 12-hour manual decision process into a 2-minute AI-assisted
workflow that preserves millions in revenue.\
\
\### 2.4 Target User\
\*\*Primary:\*\* VP of Supply Chain at mid-market US electronics
manufacturer\
\*\*Secondary:\*\* COO, CFO (economic sign-off)\
\
\### 2.5 Demo Scenario (MVP Focus)\
\*\*Event:\*\* Labor strike at Port of Los Angeles\
\*\*Impact:\*\* 12-day delay, 35% capacity reduction\
\*\*Exposure:\*\* 47 containers, 18 high-priority SKUs, \$38.4M revenue
at risk\
\*\*Optimal Strategy:\*\* Split (60% reroute to Oakland, 20% air
freight, 20% buffer stock)\
\*\*Result:\*\* \$9.5M net financial impact preserved\
\
\-\--\
\
\## 3. Technical Architecture\
\
\### 3.1 System Diagram\
\
┌─────────────────────────────────────────────────────────────────┐\
│ CLIENT LAYER │\
│ React + TypeScript + Tailwind CSS + React Router │\
│ ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐ │\
│ │ Dashboard │ │ Disruption │ │ Recommendation │ │\
│ │ Page │ │ Detail Page │ │ Page │ │\
│ └─────────────┘ └──────────────┘ └─────────────────────┘ │\
└─────────────────────────────────────────────────────────────────┘\
│\
▼ HTTP/JSON\
┌─────────────────────────────────────────────────────────────────┐\
│ API LAYER │\
│ FastAPI (Python 3.11+) │\
│ ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐ │\
│ │ Disruption │ │ Strategy │ │ Recommendation │ │\
│ │ Router │ │ Router │ │ Router │ │\
│ └─────────────┘ └──────────────┘ └─────────────────────┘ │\
│ ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐ │\
│ │ Dashboard │ │ Seed │ │ Health │ │\
│ │ Router │ │ Router │ │ Router │ │\
│ └─────────────┘ └──────────────┘ └─────────────────────┘ │\
└─────────────────────────────────────────────────────────────────┘\
│\
▼\
┌─────────────────────────────────────────────────────────────────┐\
│ SERVICE LAYER │\
│ ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐ │\
│ │ Exposure │ │ Optimizer │ │ LLM Generator │ │\
│ │ Service │ │ Service │ │ (Gemini) │ │\
│ │ │ │ (SciPy/numpy)│ │ │ │\
│ └─────────────┘ └──────────────┘ └─────────────────────┘ │\
└─────────────────────────────────────────────────────────────────┘\
│\
▼\
┌─────────────────────────────────────────────────────────────────┐\
│ DATA LAYER │\
│ PostgreSQL 15 (via SQLAlchemy 2.0+) │\
│ ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐ │\
│ │ Company │ │ SKU │ │ Shipment │ │\
│ │ Table │ │ Table │ │ Table │ │\
│ └─────────────┘ └──────────────┘ └─────────────────────┘ │\
│ ┌─────────────┐ ┌──────────────┐ ┌─────────────────────┐ │\
│ │Disruption │ │ Strategy │ │ Recommendation │ │\
│ │ Table │ │ Table │ │ Table │ │\
│ └─────────────┘ └──────────────┘ └─────────────────────┘ │\
└─────────────────────────────────────────────────────────────────┘\
\
\### 3.2 Technology Stack (Fixed)\
\
\| Layer \| Technology \| Version \| Justification \|\
\|\-\-\-\-\-\--\|\-\-\-\-\-\-\-\-\-\--\|\-\-\-\-\-\-\-\--\|\-\-\-\-\-\-\-\-\-\-\-\-\-\--\|\
\| Frontend Framework \| React \| 18.2+ \| Component-based, large
ecosystem \|\
\| Frontend Language \| TypeScript \| 5.0+ \| Type safety, better DX \|\
\| Styling \| Tailwind CSS \| 3.3+ \| Rapid UI development, consistent
design \|\
\| UI Icons \| Lucide React \| 0.294+ \| Clean, modern icon set \|\
\| HTTP Client \| Axios \| 1.6+ \| Interceptors, error handling \|\
\| Routing \| React Router DOM \| 6.20+ \| Declarative routing \|\
\| Backend Framework \| FastAPI \| 0.104+ \| Async, auto-generated docs,
Pydantic integration \|\
\| Backend Language \| Python \| 3.11+ \| Performance, type hints \|\
\| ORM \| SQLAlchemy \| 2.0+ \| Mature, async support \|\
\| Database \| PostgreSQL \| 15+ \| JSON support, reliability \|\
\| Migration Tool \| Alembic \| 1.12+ \| SQLAlchemy-native migrations
\|\
\| Optimization \| SciPy \| 1.11+ \| Scientific computing, optimization
\|\
\| Numerical \| NumPy \| 1.26+ \| Array operations \|\
\| LLM Integration \| Google Generative AI \| 0.3+ \| Gemini API
official SDK \|\
\| HTTP Client (BE) \| HTTPX \| 0.25+ \| Async HTTP for LLM calls \|\
\| Environment \| python-dotenv \| 1.0+ \| Configuration management \|\
\| Validation \| Pydantic \| 2.5+ \| Data validation, settings \|\
\| Server \| Uvicorn \| 0.24+ \| ASGI server \|\
\| Containerization \| Docker \| 24+ \| Consistent environments \|\
\| Orchestration \| Docker Compose \| 2.23+ \| Local development stack
\|\
\
\### 3.3 Infrastructure Requirements\
\
\*\*Development Environment:\*\*\
- Docker Engine 24.0+\
- Docker Compose 2.23+\
- 4GB RAM minimum, 8GB recommended\
- Internet connection (Gemini API)\
\
\*\*Ports:\*\*\
- Frontend: \`3000\`\
- Backend API: \`8000\`\
- PostgreSQL: \`5432\`\
\
\-\--\
\
\## 4. Data Models (Database Schema)\
\
\### 4.1 Entity Relationship Diagram\
\
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐\
│ Company │1 \*│ SKU │1 \*│ Inventory │\
├─────────────────┤───────├─────────────────┤───────├─────────────────┤\
│ PK id (UUID) │ │ PK id (UUID) │ │ PK id (UUID) │\
│ name (str) │ │ FK company_id │ │ FK sku_id │\
│ revenue_millions│ │ sku_code (str) │ │ on_hand (int) │\
│ gross_margin_pct│ │ description │ │ reserved (int) │\
│ risk_tolerance │ │ daily_demand │ │ │\
│ sla_weight │ │ unit_price │ │ │\
│ working_capital │ │ unit_margin │ │ │\
│ churn_sens │ │ criticality │ │ │\
│ sla_target │ │ │ │ │\
└─────────────────┘ └─────────────────┘ └─────────────────┘\
│ │\
│ │\
│ 1 \* │\
└──────────────────┐ │\
│ │\
▼ │\
┌─────────────────┐ │\
│ Shipment │◄────────────────┘\
├─────────────────┤\
│ PK id (UUID) │\
│ FK company_id │\
│ FK sku_id │\
│ FK port_id │\
│ container_id │\
│ quantity (int) │\
│ arrival_date │\
│ status (enum) │\
└─────────────────┘\
│\
│\
┌────────┴────────┐\
│ │\
▼ ▼\
┌─────────────────┐ ┌─────────────────┐\
│ Port │ │ Disruption │\
├─────────────────┤ ├─────────────────┤\
│ PK id (UUID) │ │ PK id (UUID) │\
│ code (str) │ │ FK port_id │\
│ name (str) │ │ type (enum) │\
│ region (str) │ │ severity (float)│\
└─────────────────┘ │ delay_days (int)│\
│ confidence │\
│ is_active │\
│ detected_at │\
└─────────────────┘\
│\
│ 1\
│\
▼ \* (implied)\
┌─────────────────┐\
│ Recommendation │\
├─────────────────┤\
│ PK id (UUID) │\
│ FK disruption_id│\
│ FK strategy_id │\
│ confidence │\
│ reasoning │\
│ email_supplier │\
│ email_logistics │\
│ exec_summary │\
│ requires_approval│\
│ approved_by │\
│ approved_at │\
└─────────────────┘\
\### 4.2 SQL DDL (PostgreSQL)\
\
\`\`\`sql\
\-- Enable UUID extension\
CREATE EXTENSION IF NOT EXISTS \"uuid-ossp\";\
\
\-- Companies table (single tenant for MVP)\
CREATE TABLE companies (\
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),\
name VARCHAR(255) NOT NULL,\
revenue_annual_millions DECIMAL(10, 2) NOT NULL,\
gross_margin_percent DECIMAL(5, 4) NOT NULL CHECK (gross_margin_percent
BETWEEN 0 AND 1),\
risk_tolerance DECIMAL(5, 4) NOT NULL CHECK (risk_tolerance BETWEEN 0
AND 1),\
sla_weight DECIMAL(5, 4) NOT NULL CHECK (sla_weight BETWEEN 0 AND 1),\
working_capital_limit DECIMAL(15, 2) NOT NULL,\
customer_churn_sensitivity DECIMAL(5, 4) NOT NULL CHECK
(customer_churn_sensitivity BETWEEN 0 AND 1),\
sla_target_percent DECIMAL(5, 4) NOT NULL CHECK (sla_target_percent
BETWEEN 0 AND 1),\
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),\
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()\
);\
\
\-- Ports table\
CREATE TABLE ports (\
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),\
code VARCHAR(10) UNIQUE NOT NULL,\
name VARCHAR(255) NOT NULL,\
region VARCHAR(255) NOT NULL,\
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()\
);\
\
\-- SKUs table\
CREATE TABLE skus (\
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),\
company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,\
sku_code VARCHAR(100) NOT NULL,\
description TEXT,\
daily_demand INTEGER NOT NULL CHECK (daily_demand \>= 0),\
unit_price DECIMAL(12, 2) NOT NULL CHECK (unit_price \>= 0),\
unit_margin DECIMAL(12, 2) NOT NULL,\
criticality_score DECIMAL(5, 4) NOT NULL CHECK (criticality_score
BETWEEN 0 AND 1),\
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),\
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),\
UNIQUE(company_id, sku_code)\
);\
\
\-- Inventory table\
CREATE TABLE inventory (\
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),\
sku_id UUID NOT NULL REFERENCES skus(id) ON DELETE CASCADE,\
on_hand_units INTEGER NOT NULL DEFAULT 0 CHECK (on_hand_units \>= 0),\
reserved_units INTEGER NOT NULL DEFAULT 0 CHECK (reserved_units \>= 0),\
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),\
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),\
UNIQUE(sku_id)\
);\
\
\-- Shipments table\
CREATE TABLE shipments (\
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),\
company_id UUID NOT NULL REFERENCES companies(id) ON DELETE CASCADE,\
sku_id UUID NOT NULL REFERENCES skus(id) ON DELETE CASCADE,\
port_id UUID NOT NULL REFERENCES ports(id) ON DELETE RESTRICT,\
container_id VARCHAR(100) NOT NULL,\
quantity INTEGER NOT NULL CHECK (quantity \> 0),\
original_arrival_date DATE NOT NULL,\
status VARCHAR(20) NOT NULL DEFAULT \'in_transit\'\
CHECK (status IN (\'in_transit\', \'delayed\', \'arrived\',
\'cancelled\')),\
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),\
updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()\
);\
\
\-- Disruptions table\
CREATE TABLE disruptions (\
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),\
port_id UUID NOT NULL REFERENCES ports(id) ON DELETE RESTRICT,\
disruption_type VARCHAR(50) NOT NULL\
CHECK (disruption_type IN (\'labor_strike\', \'weather\',
\'congestion\', \'geopolitical\', \'accident\')),\
severity_score DECIMAL(5, 4) NOT NULL CHECK (severity_score BETWEEN 0
AND 1),\
expected_delay_days INTEGER NOT NULL CHECK (expected_delay_days \> 0),\
confidence_score DECIMAL(5, 4) NOT NULL CHECK (confidence_score BETWEEN
0 AND 1),\
is_active BOOLEAN NOT NULL DEFAULT TRUE,\
detected_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),\
resolved_at TIMESTAMP WITH TIME ZONE,\
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()\
);\
\
\-- Strategies table (static/reference data)\
CREATE TABLE strategies (\
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),\
name VARCHAR(100) NOT NULL UNIQUE,\
description TEXT,\
air_freight_percent DECIMAL(5, 4) NOT NULL CHECK (air_freight_percent
BETWEEN 0 AND 1),\
reroute_percent DECIMAL(5, 4) NOT NULL CHECK (reroute_percent BETWEEN 0
AND 1),\
buffer_stock_percent DECIMAL(5, 4) NOT NULL CHECK (buffer_stock_percent
BETWEEN 0 AND 1),\
cost_multiplier_air DECIMAL(5, 2) NOT NULL DEFAULT 8.0,\
cost_multiplier_reroute DECIMAL(5, 2) NOT NULL DEFAULT 1.3,\
holding_cost_per_unit_per_day DECIMAL(10, 4) NOT NULL DEFAULT 0.50,\
is_active BOOLEAN NOT NULL DEFAULT TRUE\
);\
\
\-- Recommendations table\
CREATE TABLE recommendations (\
id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),\
disruption_id UUID NOT NULL REFERENCES disruptions(id) ON DELETE
CASCADE,\
selected_strategy_id UUID NOT NULL REFERENCES strategies(id),\
confidence_score DECIMAL(5, 4) NOT NULL CHECK (confidence_score BETWEEN
0 AND 1),\
reasoning TEXT NOT NULL,\
revenue_preserved DECIMAL(15, 2) NOT NULL,\
mitigation_cost DECIMAL(15, 2) NOT NULL,\
sla_achieved DECIMAL(5, 4) NOT NULL,\
sla_penalty_cost DECIMAL(15, 2) NOT NULL DEFAULT 0,\
net_financial_impact DECIMAL(15, 2) NOT NULL,\
generated_email_supplier TEXT,\
generated_email_logistics TEXT,\
generated_executive_summary TEXT,\
requires_approval BOOLEAN NOT NULL DEFAULT TRUE,\
approved_by VARCHAR(255),\
approved_at TIMESTAMP WITH TIME ZONE,\
created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()\
);\
\
\-- Indexes for performance\
CREATE INDEX idx_shipments_company ON shipments(company_id);\
CREATE INDEX idx_shipments_port ON shipments(port_id);\
CREATE INDEX idx_shipments_arrival ON shipments(original_arrival_date);\
CREATE INDEX idx_skus_company ON skus(company_id);\
CREATE INDEX idx_inventory_sku ON inventory(sku_id);\
CREATE INDEX idx_disruptions_port ON disruptions(port_id);\
CREATE INDEX idx_disruptions_active ON disruptions(is_active);\
CREATE INDEX idx_recommendations_disruption ON
recommendations(disruption_id);\
4.3 Pydantic Schemas (Backend)\
\# schemas.py\
from pydantic import BaseModel, Field, ConfigDict\
from typing import Optional, List, Dict\
from datetime import date, datetime\
from decimal import Decimal\
from uuid import UUID\
from enum import Enum\
\
\# Enums\
class ShipmentStatus(str, Enum):\
IN_TRANSIT = \"in_transit\"\
DELAYED = \"delayed\"\
ARRIVED = \"arrived\"\
CANCELLED = \"cancelled\"\
\
class DisruptionType(str, Enum):\
LABOR_STRIKE = \"labor_strike\"\
WEATHER = \"weather\"\
CONGESTION = \"congestion\"\
GEOPOLITICAL = \"geopolitical\"\
ACCIDENT = \"accident\"\
\
\# Company Schemas\
class CompanyBase(BaseModel):\
name: str = Field(\..., min_length=1, max_length=255)\
revenue_annual_millions: Decimal = Field(\..., gt=0)\
gross_margin_percent: Decimal = Field(\..., ge=0, le=1)\
risk_tolerance: Decimal = Field(\..., ge=0, le=1)\
sla_weight: Decimal = Field(\..., ge=0, le=1)\
working_capital_limit: Decimal = Field(\..., gt=0)\
customer_churn_sensitivity: Decimal = Field(\..., ge=0, le=1)\
sla_target_percent: Decimal = Field(\..., ge=0, le=1)\
\
class CompanyCreate(CompanyBase):\
pass\
\
class CompanyResponse(CompanyBase):\
model_config = ConfigDict(from_attributes=True)\
id: UUID\
created_at: datetime\
updated_at: datetime\
\
\# Port Schemas\
class PortBase(BaseModel):\
code: str = Field(\..., min_length=2, max_length=10)\
name: str = Field(\..., min_length=1, max_length=255)\
region: str = Field(\..., min_length=1, max_length=255)\
\
class PortCreate(PortBase):\
pass\
\
class PortResponse(PortBase):\
model_config = ConfigDict(from_attributes=True)\
id: UUID\
created_at: datetime\
\
\# SKU Schemas\
class SKUBase(BaseModel):\
sku_code: str = Field(\..., min_length=1, max_length=100)\
description: Optional\[str\] = None\
daily_demand: int = Field(\..., ge=0)\
unit_price: Decimal = Field(\..., ge=0)\
unit_margin: Decimal\
criticality_score: Decimal = Field(\..., ge=0, le=1)\
\
class SKUCreate(SKUBase):\
company_id: UUID\
\
class SKUResponse(SKUBase):\
model_config = ConfigDict(from_attributes=True)\
id: UUID\
company_id: UUID\
created_at: datetime\
updated_at: datetime\
\
\# Inventory Schemas\
class InventoryBase(BaseModel):\
on_hand_units: int = Field(default=0, ge=0)\
reserved_units: int = Field(default=0, ge=0)\
\
class InventoryCreate(InventoryBase):\
sku_id: UUID\
\
class InventoryResponse(InventoryBase):\
model_config = ConfigDict(from_attributes=True)\
id: UUID\
sku_id: UUID\
available_units: int \# Computed property\
\
\# Shipment Schemas\
class ShipmentBase(BaseModel):\
container_id: str = Field(\..., min_length=1, max_length=100)\
quantity: int = Field(\..., gt=0)\
original_arrival_date: date\
status: ShipmentStatus = ShipmentStatus.IN_TRANSIT\
\
class ShipmentCreate(ShipmentBase):\
company_id: UUID\
sku_id: UUID\
port_id: UUID\
\
class ShipmentResponse(ShipmentBase):\
model_config = ConfigDict(from_attributes=True)\
id: UUID\
company_id: UUID\
sku_id: UUID\
port_id: UUID\
created_at: datetime\
\
\# Disruption Schemas\
class DisruptionBase(BaseModel):\
disruption_type: DisruptionType\
severity_score: Decimal = Field(\..., ge=0, le=1)\
expected_delay_days: int = Field(\..., gt=0)\
confidence_score: Decimal = Field(\..., ge=0, le=1)\
\
class DisruptionCreate(DisruptionBase):\
port_id: UUID\
\
class DisruptionResponse(DisruptionBase):\
model_config = ConfigDict(from_attributes=True)\
id: UUID\
port_id: UUID\
is_active: bool\
detected_at: datetime\
resolved_at: Optional\[datetime\]\
\
\# Strategy Schemas\
class StrategyResponse(BaseModel):\
model_config = ConfigDict(from_attributes=True)\
id: UUID\
name: str\
description: Optional\[str\]\
air_freight_percent: Decimal\
reroute_percent: Decimal\
buffer_stock_percent: Decimal\
cost_multiplier_air: Decimal\
cost_multiplier_reroute: Decimal\
holding_cost_per_unit_per_day: Decimal\
\
\# Exposure Analysis Schemas\
class SKUExposure(BaseModel):\
sku_id: UUID\
sku_code: str\
description: Optional\[str\]\
daily_demand: int\
unit_price: Decimal\
unit_margin: Decimal\
on_hand_units: int\
inventory_runway_days: int\
stockout_date: date\
revenue_at_risk: Decimal\
margin_at_risk: Decimal\
affected_shipment_ids: List\[UUID\]\
\
class ExposureResult(BaseModel):\
disruption_id: UUID\
company_id: UUID\
affected_skus: List\[SKUExposure\]\
total_revenue_at_risk: Decimal\
total_margin_at_risk: Decimal\
total_affected_shipments: int\
total_affected_quantity: int\
\
\# Strategy Simulation Schemas\
class StrategySimulation(BaseModel):\
strategy_id: UUID\
strategy_name: str\
description: str\
revenue_preserved: Decimal\
mitigation_cost: Decimal\
sla_achieved: Decimal\
sla_penalty_cost: Decimal\
net_financial_impact: Decimal\
working_capital_required: Decimal\
is_feasible: bool\
feasibility_reason: Optional\[str\]\
\
class StrategyComparison(BaseModel):\
disruption_id: UUID\
simulations: List\[StrategySimulation\]\
optimal_strategy_id: UUID\
company_risk_profile: Dict\[str, Decimal\]\
\
\# Recommendation Schemas\
class RecommendationResponse(BaseModel):\
model_config = ConfigDict(from_attributes=True)\
id: UUID\
disruption_id: UUID\
selected_strategy: StrategyResponse\
confidence_score: Decimal\
reasoning: str\
revenue_preserved: Decimal\
mitigation_cost: Decimal\
sla_achieved: Decimal\
sla_penalty_cost: Decimal\
net_financial_impact: Decimal\
generated_email_supplier: Optional\[str\]\
generated_email_logistics: Optional\[str\]\
generated_executive_summary: Optional\[str\]\
requires_approval: bool\
approved_by: Optional\[str\]\
approved_at: Optional\[datetime\]\
created_at: datetime\
\
class ApprovalRequest(BaseModel):\
approver_name: str = Field(\..., min_length=1, max_length=255)\
notes: Optional\[str\] = None\
\
\# Dashboard Schema\
class DashboardSummary(BaseModel):\
company: CompanyResponse\
active_disruption: Optional\[DisruptionResponse\]\
active_recommendation: Optional\[RecommendationResponse\]\
total_revenue_at_risk: Optional\[Decimal\]\
key_metrics: Dict\[str, int\] \# e.g., {\"affected_skus\": 18,
\"affected_shipments\": 47}\
\
\# Seed Data Schema\
class SeedDataResponse(BaseModel):\
success: bool\
message: str\
created_counts: Dict\[str, int\]\
5. API Endpoints (Complete Specification)\
5.1 Endpoint Summary\
\| Method \| Path \| Description \| Request Body \| Response \|\
\| \-\-\-\-\-- \|
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\--
\| \-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-- \|
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-- \|
\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-\-- \|\
\| POST \| \`/api/v1/seed-data\` \| Populate demo data \| None \|
\`SeedDataResponse\` \|\
\| GET \| \`/api/v1/dashboard\` \| Get dashboard summary \| None \|
\`DashboardSummary\` \|\
\| POST \| \`/api/v1/disruptions\` \| Create disruption \|
\`DisruptionCreate\` \| \`DisruptionResponse\` \|\
\| GET \| \`/api/v1/disruptions/{id}\` \| Get disruption details \| None
\| \`DisruptionResponse\` \|\
\| GET \| \`/api/v1/disruptions/{id}/exposure\` \| Calculate exposure \|
None \| \`ExposureResult\` \|\
\| GET \| \`/api/v1/disruptions/{id}/strategies\` \| Simulate strategies
\| None \| \`StrategyComparison\` \|\
\| GET \| \`/api/v1/disruptions/{id}/recommendation\` \| Get
recommendation \| None \| \`RecommendationResponse\` \|\
\| POST \| \`/api/v1/recommendations/{id}/approve\` \| Approve
recommendation \| \`ApprovalRequest\` \| \`RecommendationResponse\` \|\
\| GET \| \`/api/v1/companies/{id}\` \| Get company profile \| None \|
\`CompanyResponse\` \|\
\| GET \| \`/api/v1/health\` \| Health check \| None \| \`{\"status\":
\"ok\"}\` \|\
5.2 Detailed Endpoint Specifications\
POST /api/v1/seed-data\
Purpose: Initialize database with complete demo scenario for testing and
demos.\
Implementation Logic:

1.  Check if data already exists (optional: truncate or skip)

2.  Create Company \"Apex Electronics Inc.\"

3.  Create 3 Ports: LA (Los Angeles), OAK (Oakland), SEA (Seattle)

4.  Create 25 SKUs with realistic electronics component data

5.  Create Inventory positions for each SKU

6.  Create 50 Shipments distributed across 30 days, 45% through LA

7.  Create 4 Strategy templates (S1-S4)

8.  Optionally create one active Disruption\
    Response:\
    {\
    \"success\": true,\
    \"message\": \"Demo data created successfully\",\
    \"created_counts\": {\
    \"companies\": 1,\
    \"ports\": 3,\
    \"skus\": 25,\
    \"inventory\": 25,\
    \"shipments\": 50,\
    \"strategies\": 4,\
    \"disruptions\": 0\
    }\
    }\
    GET /api/v1/dashboard\
    Purpose: Main dashboard data load.\
    Implementation Logic:

```{=html}
<!-- -->
```
1.  Get single company (MVP assumption: single tenant)

2.  Check for active disruption (is_active=true)

3.  If active disruption, get latest recommendation

4.  Calculate summary metrics\
    Response: DashboardSummary schema\
    POST /api/v1/disruptions\
    Purpose: Create new disruption event and trigger analysis pipeline.\
    Implementation Logic:

```{=html}
<!-- -->
```
1.  Validate port exists

2.  Create Disruption record

3.  Trigger async or sync pipeline:

    -   Calculate exposure (call ExposureService)

    -   Simulate strategies (call OptimizerService)

    -   Generate recommendation with LLM (call LLMService)

```{=html}
<!-- -->
```
1.  Return created disruption\
    Business Logic Notes:

-   Pipeline should complete in \< 5 seconds for MVP

-   Store all calculation results in database

-   LLM generation can be async if slow, but MVP should be synchronous\
    GET /api/v1/disruptions/{id}/exposure\
    Purpose: Calculate and return financial exposure for a disruption.\
    GET /api/v1/disruptions/{id}/strategies\
    Purpose: Simulate all 4 strategies and return comparison.\
    GET /api/v1/disruptions/{id}/recommendation\
    Purpose: Get or create final recommendation with LLM-generated
    drafts.\
    Implementation Logic:

1.  Check if recommendation exists for disruption

2.  If not, run strategy simulation

3.  Select optimal strategy

4.  Call LLM service to generate drafts

5.  Store and return recommendation\
    POST /api/v1/recommendations/{id}/approve\
    Purpose: Human-in-the-loop approval workflow.\
    Implementation Logic:

```{=html}
<!-- -->
```
1.  Validate recommendation exists and requires_approval=True

2.  Update record with approver_name, approved_at=timestamp

3.  Set requires_approval=False

4.  Return updated recommendation\
    6. Core Algorithms\
    6.1 Inventory Runway Calculation\
    6.2 Revenue at Risk Calculation\
    6.3 Strategy Simulation Engine\
    6.4 Strategy Selection\
    7. LLM Integration (Google Gemini)\
    7.1 Configuration\
    \# core/config.py\
    import os\
    from pydantic_settings import BaseSettings\
    \
    class Settings(BaseSettings):\
    GEMINI_API_KEY: str\
    GEMINI_MODEL: str = \"gemini-pro\"\
    GEMINI_TEMPERATURE: float = 0.3 \# Low for consistency\
    GEMINI_MAX_TOKENS: int = 2048\
    \
    class Config:\
    env_file = \".env\"\
    \
    settings = Settings()\
    7.2 Service Implementation\
    \# services/llm_generator.py\
    import google.generativeai as genai\
    from typing import Optional\
    from decimal import Decimal\
    \
    class LLMGeneratorService:\
    def \_\_init\_\_(self):\
    genai.configure(api_key=settings.GEMINI_API_KEY)\
    self.model = genai.GenerativeModel(settings.GEMINI_MODEL)\
    \
    def generate_mitigation_drafts(\
    self,\
    company_name: str,\
    disruption_type: str,\
    port_name: str,\
    delay_days: int,\
    affected_skus_count: int,\
    revenue_at_risk: Decimal,\
    strategy_name: str,\
    air_percent: float,\
    reroute_percent: float,\
    buffer_percent: float,\
    risk_tolerance: float,\
    sla_target: float,\
    working_capital: Decimal\
    ) -\> dict\[str, str\]:\
    \"\"\"\
    Generate three draft communications using Gemini.\
    Returns dict with keys: supplier_email, logistics_email,
    executive_summary\
    \"\"\"\
    \
    prompt = f\"\"\"\
    You are a VP of Supply Chain at {company_name}, a mid-market
    electronics manufacturer.\
    A critical supply chain disruption requires immediate action.\
    \
    DISRUPTION DETAILS:\
    - Location: {port_name}\
    - Type: {disruption_type.replace(\'\_\', \' \').title()}\
    - Expected Delay: {delay_days} days\
    - Affected SKUs: {affected_skus_count} high-priority items\
    - Revenue at Risk: \${revenue_at_risk:,.0f}\
    \
    COMPANY RISK PROFILE:\
    - Risk Tolerance: {\'Low\' if risk_tolerance \< 0.4 else \'Medium\'
    if risk_tolerance \< 0.7 else \'High\'} ({risk_tolerance:.0%})\
    - SLA Target: {sla_target:.0%}\
    - Working Capital Available: \${working_capital:,.0f}\
    \
    SELECTED MITIGATION STRATEGY: {strategy_name}\
    - Reroute {reroute_percent:.0%} of shipments via alternate port
    (Port of Oakland)\
    - Air freight {air_percent:.0%} of most critical SKUs\
    - Build buffer stock for {buffer_percent:.0%} of affected items\
    \
    Generate the following three items:\
    \
    1. SUPPLIER EMAIL: Professional email to primary Taiwanese supplier
    requesting immediate rerouting of specific containers to Port of
    Oakland. Include reference to contract terms and request
    confirmation within 4 hours.\
    \
    2. LOGISTICS REQUEST: Formal request to freight forwarder to execute
    air freight booking for priority SKUs and coordinate rerouting.
    Specify timeline and handling requirements.\
    \
    3. EXECUTIVE SUMMARY: Three bullet points for COO briefing
    covering: (a) situation severity, (b) recommended action and
    financial impact, (c) next steps and timeline.\
    \
    Use professional supply chain terminology. Be specific and
    actionable. Do not use placeholders.\
    \"\"\"\
    \
    try:\
    response = self.model.generate_content(\
    prompt,\
    generation_config=genai.types.GenerationConfig(\
    temperature=settings.GEMINI_TEMPERATURE,\
    max_output_tokens=settings.GEMINI_MAX_TOKENS,\
    )\
    )\
    \
    \# Parse response (expecting three sections)\
    text = response.text\
    \
    \# Simple parsing - look for numbered sections or headers\
    \# Fallback: split by double newlines if no clear structure\
    sections = self.\_parse_sections(text)\
    \
    return {\
    \"supplier_email\": sections.get(0, text\[:1000\]), \# First
    section\
    \"logistics_email\": sections.get(1, text\[1000:2000\]), \# Second
    section\
    \"executive_summary\": sections.get(2, text\[-500:\]) \# Last
    section\
    }\
    \
    except Exception as e:\
    \# Fallback templates if LLM fails\
    return self.\_fallback_templates(\
    company_name, port_name, delay_days, strategy_name\
    )\
    \
    def \_parse_sections(self, text: str) -\> dict\[int, str\]:\
    \"\"\"Parse numbered sections from LLM output.\"\"\"\
    sections = {}\
    current_section = 0\
    \
    for line in text.split(\'\\n\'):\
    if line.strip().startswith((\'1.\', \'2.\', \'3.\')):\
    current_section = int(line.strip()\[0\]) - 1\
    sections\[current_section\] = line.strip()\[2:\].strip()\
    elif current_section in sections:\
    sections\[current_section\] += \'\\n\' + line\
    \
    return sections\
    \
    def \_fallback_templates(self, \*\*kwargs) -\> dict\[str, str\]:\
    \"\"\"Hardcoded fallback if Gemini API fails.\"\"\"\
    return {\
    \"supplier_email\": f\"Subject: Urgent: Reroute Required -
    {kwargs.get(\'port_name\')} Disruption\\n\\nDear Supplier,\\n\\nDue
    to the ongoing disruption at {kwargs.get(\'port_name\')}, we need to
    immediately reroute all in-transit containers to Port of Oakland.
    Please confirm receipt and ETA.\\n\\nBest regards,\\nVP Supply
    Chain\",\
    \"logistics_email\": \"Please execute emergency air freight booking
    and coordinate rerouting per attached manifest.\",\
    \"executive_summary\": \"• Situation: Port disruption threatening
    \$38M revenue\\n• Action: Split mitigation strategy selected\\n•
    Timeline: Execute within 24 hours\"\
    }\
    8. Frontend Specification\
    8.1 Project Structure\
    frontend/\
    ├── public/\
    │ └── index.html\
    ├── src/\
    │ ├── api/\
    │ │ ├── client.ts \# Axios instance with interceptors\
    │ │ └── endpoints.ts \# API call functions\
    │ ├── components/\
    │ │ ├── layout/\
    │ │ │ ├── Header.tsx\
    │ │ │ ├── Sidebar.tsx\
    │ │ │ └── Layout.tsx\
    │ │ ├── dashboard/\
    │ │ │ ├── MetricCard.tsx\
    │ │ │ ├── AlertBanner.tsx\
    │ │ │ └── DisruptionSummary.tsx\
    │ │ ├── disruption/\
    │ │ │ ├── ExposureTable.tsx\
    │ │ │ ├── SKURow.tsx\
    │ │ │ └── RiskBadge.tsx\
    │ │ ├── strategy/\
    │ │ │ ├── StrategyCard.tsx\
    │ │ │ ├── StrategyComparison.tsx\
    │ │ │ └── FinancialImpact.tsx\
    │ │ └── recommendation/\
    │ │ ├── DraftEmail.tsx\
    │ │ ├── ApprovalForm.tsx\
    │ │ └── ExplainabilityPanel.tsx\
    │ ├── pages/\
    │ │ ├── DashboardPage.tsx\
    │ │ ├── DisruptionPage.tsx\
    │ │ └── RecommendationPage.tsx\
    │ ├── hooks/\
    │ │ ├── useDashboard.ts\
    │ │ ├── useDisruption.ts\
    │ │ └── useRecommendation.ts\
    │ ├── types/\
    │ │ └── index.ts \# TypeScript interfaces\
    │ ├── utils/\
    │ │ ├── formatters.ts \# Currency, date formatting\
    │ │ └── calculations.ts \# Client-side math helpers\
    │ ├── App.tsx\
    │ └── index.tsx\
    ├── tailwind.config.js\
    ├── tsconfig.json\
    └── package.json\
    11. Testing Checklist\
    11.1 Backend Tests

-   \[ \] Seed data endpoint creates all records correctly

-   \[ \] Exposure calculation returns correct revenue at risk (\$38.4M
    for demo)

-   \[ \] Strategy simulation marks S2 (Full Air) as infeasible due to
    working capital

-   \[ \] Strategy simulation selects S4 (Split) as optimal

-   \[ \] LLM generation returns three non-empty text blocks

-   \[ \] Approval workflow updates database correctly

-   \[ \] All endpoints return proper error codes (404, 422, 500)\
    11.2 Frontend Tests

```{=html}
<!-- -->
```
-   \[ \] Dashboard loads with metric cards

-   \[ \] Active disruption shows red alert banner

-   \[ \] Exposure table renders all SKUs with correct formatting

-   \[ \] Strategy comparison highlights optimal strategy in green

-   \[ \] Infeasible strategies show opacity reduction and warning

-   \[ \] Recommendation page displays all three generated drafts

-   \[ \] Copy to clipboard functionality works

-   \[ \] Approval form submits and updates UI\
    11.3 Integration Tests

```{=html}
<!-- -->
```
-   \[ \] End-to-end flow: Seed → Create Disruption → View Exposure →
    View Strategies → Get Recommendation → Approve

-   \[ \] Demo scenario values match specification exactly

-   \[ \] Page load times \< 2 seconds for all routes

-   \[ \] LLM fallback templates display if API fails\
    \
    12. Deployment Notes\
    12.1 Production Considerations (Post-MVP)

```{=html}
<!-- -->
```
-   Use managed PostgreSQL (AWS RDS, Cloud SQL)

-   Deploy backend to Cloud Run, ECS, or Kubernetes

-   Use Redis for caching frequent calculations

-   Implement proper authentication (OAuth2, SAML)

-   Add comprehensive logging and monitoring (Datadog, New Relic)

-   Set up CI/CD pipelines (GitHub Actions, GitLab CI)\
    12.2 Security Checklist

```{=html}
<!-- -->
```
-   \[ \] All API keys in environment variables, never committed

-   \[ \] Database credentials rotated regularly

-   \[ \] CORS properly configured for production domain

-   \[ \] Input validation on all endpoints (Pydantic)

-   \[ \] SQL injection prevention via SQLAlchemy ORM

-   \[ \] XSS protection via React escaping

-   \[ \] HTTPS only in production\
    \
    13. Appendix: Demo Script\
    13.1 5-Minute Demo Flow\
    Minute 0: Setup

```{=html}
<!-- -->
```
-   Show seeded dashboard with no active disruption

-   Green \"All Systems Normal\" status\
    Minute 1: Trigger Disruption

```{=html}
<!-- -->
```
-   Click \"Simulate Disruption\" or show pre-created one

-   Red alert banner appears: \"Port of Los Angeles - Labor Strike\"

-   Key metrics: \$38.4M revenue at risk, 18 SKUs, 47 shipments\
    Minute 2: Exposure Analysis

```{=html}
<!-- -->
```
-   Navigate to Exposure tab

-   Scroll through table showing SKU-level detail

-   Highlight red \"7 days\" runway indicators

-   Point to stockout dates in March\
    Minute 3: Strategy Comparison

```{=html}
<!-- -->
```
-   Switch to Strategies tab

-   Show four strategy cards

-   Point out S2 (Full Air) marked infeasible - \$11.3M cost exceeds
    \$5M capital

-   Highlight S4 (Split) in green - \$9.5M net impact\
    Minute 4: Recommendation & Drafts

```{=html}
<!-- -->
```
-   Click into Recommendation

-   Show financial summary: \$34.1M preserved - \$2.8M cost = \$9.5M net

-   Expand \"Why this decision?\" - explain Risk DNA weighting

-   Show three generated drafts in tabs\
    Minute 5: Approval

```{=html}
<!-- -->
```
-   Show approval form

-   Enter name, click Approve

-   Success state, dashboard updates

-   Closing: \"From 12 hours of manual analysis to 2 minutes with
    HarborGuard AI\"
