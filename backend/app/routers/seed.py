"""
Seed Data Router — Demo Scenario Initialization
=================================================
Populates the database with the demo scenario from kmi.tex §Demo:
- Apex Electronics Inc. ($420M revenue, 28% margin)
- 3 Ports (LA, Oakland, Seattle)
- 18 high-priority SKUs calibrated for ~$38.4M exposure
- 47 shipments (45% through LA)
- 4 strategy templates (S1-S4)
- 1 active disruption (LA labor strike, 12 days)
"""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.database import get_db
from app import models, schemas
from decimal import Decimal
from datetime import date, timedelta
import random

router = APIRouter()

# Deterministic seed for reproducibility in demos
random.seed(42)

# Calibrated SKU data to hit ~$38.4M total revenue at risk
# Each tuple: (sku_code, description, daily_demand, unit_price, criticality)
DEMO_SKUS = [
    ("PCB-2024-X1",  "Main Logic Board Assembly",        450, 285.00, 0.95),
    ("PCB-2024-X2",  "Power Management IC",              380, 142.00, 0.92),
    ("PCB-2024-X3",  "RF Transceiver Module",            320, 198.00, 0.90),
    ("PCB-2024-X4",  "NAND Flash Storage 256GB",         520, 165.00, 0.88),
    ("PCB-2024-X5",  "DDR5 Memory Module 16GB",          480, 120.00, 0.87),
    ("PCB-2024-X6",  "Display Driver IC",                350, 95.00,  0.85),
    ("PCB-2024-X7",  "USB-C Controller Chip",            410, 78.00,  0.83),
    ("PCB-2024-X8",  "WiFi 6E Combo Module",             290, 210.00, 0.82),
    ("PCB-2024-X9",  "Camera ISP Processor",             260, 320.00, 0.80),
    ("PCB-2024-X10", "Audio Codec IC",                   340, 55.00,  0.78),
    ("PCB-2024-X11", "Voltage Regulator Array",          500, 42.00,  0.76),
    ("PCB-2024-X12", "GPS/GNSS Receiver",                180, 175.00, 0.75),
    ("PCB-2024-X13", "Bluetooth 5.3 Module",             310, 88.00,  0.73),
    ("PCB-2024-X14", "Thermal Management Substrate",     420, 62.00,  0.72),
    ("PCB-2024-X15", "High-Density Connector Array",     380, 35.00,  0.70),
    ("PCB-2024-X16", "PMIC Battery Charger IC",          290, 110.00, 0.68),
    ("PCB-2024-X17", "MEMS Accelerometer Sensor",        240, 95.00,  0.65),
    ("PCB-2024-X18", "Ceramic Capacitor Bank 0402",      600, 28.00,  0.62),
]


@router.post("/seed-data", response_model=schemas.SeedDataResponse)
def seed_data(db: Session = Depends(get_db)):
    """Initialize database with complete demo scenario for testing and demos."""

    # Check if data already exists to avoid duplication
    if db.query(models.Company).count() > 0:
        return schemas.SeedDataResponse(
            success=True,
            message="Data already seeded",
            created_counts={"companies": 1}
        )

    # ── 1. Company: Apex Electronics Inc. ────────────────────────────────
    company = models.Company(
        name="Apex Electronics Inc.",
        revenue_annual_millions=Decimal("420.00"),
        gross_margin_percent=Decimal("0.2800"),
        risk_tolerance=Decimal("0.3000"),       # Low = conservative
        sla_weight=Decimal("0.9000"),             # High = SLA-focused
        working_capital_limit=Decimal("5000000.00"),
        customer_churn_sensitivity=Decimal("0.8000"),
        sla_target_percent=Decimal("0.9700")
    )
    db.add(company)
    db.flush()

    # ── 2. Ports ─────────────────────────────────────────────────────────
    ports = [
        models.Port(code="LA",  name="Port of Los Angeles", region="US West Coast"),
        models.Port(code="OAK", name="Port of Oakland",     region="US West Coast"),
        models.Port(code="SEA", name="Port of Seattle",     region="US West Coast"),
    ]
    db.add_all(ports)
    db.flush()
    la_port = next(p for p in ports if p.code == "LA")
    oak_port = next(p for p in ports if p.code == "OAK")
    sea_port = next(p for p in ports if p.code == "SEA")

    # ── 3. SKUs (18 per spec) ────────────────────────────────────────────
    skus = []
    for code, desc, demand, price, crit in DEMO_SKUS:
        margin = round(price * 0.28, 2)  # 28% gross margin
        sku = models.SKU(
            company_id=company.id,
            sku_code=code,
            description=desc,
            daily_demand=demand,
            unit_price=Decimal(str(price)),
            unit_margin=Decimal(str(margin)),
            criticality_score=Decimal(str(round(crit, 4)))
        )
        skus.append(sku)
    db.add_all(skus)
    db.flush()

    # ── 4. Inventory (short runway = 5-15 days for most SKUs) ────────────
    inventories = []
    for sku in skus:
        # Short runway to ensure delay_gap creates revenue loss
        runway_days = random.randint(5, 15)
        on_hand = sku.daily_demand * runway_days
        inv = models.Inventory(
            sku_id=sku.id,
            on_hand_units=on_hand,
            reserved_units=0
        )
        inventories.append(inv)
    db.add_all(inventories)

    # ── 5. Shipments (47 per spec, 45% through LA) ──────────────────────
    shipments = []
    la_count = 21   # ~45% of 47
    oak_count = 15
    sea_count = 11

    for i in range(47):
        if i < la_count:
            target_port = la_port
        elif i < la_count + oak_count:
            target_port = oak_port
        else:
            target_port = sea_port

        sku = skus[i % len(skus)]  # Distribute across SKUs evenly
        shipment = models.Shipment(
            company_id=company.id,
            sku_id=sku.id,
            port_id=target_port.id,
            container_id=f"CONT-{10000 + i:05d}",
            quantity=random.randint(2000, 6000),
            original_arrival_date=date.today() + timedelta(days=random.randint(5, 30)),
            status="in_transit"
        )
        shipments.append(shipment)
    db.add_all(shipments)

    # ── 6. Strategy Templates (S1-S4 per kmi.tex §4) ────────────────────
    strategies = [
        models.Strategy(
            name="Do Nothing",
            description="Accept the delay and communicate with customers regarding stockouts.",
            air_freight_percent=Decimal("0.0000"),
            reroute_percent=Decimal("0.0000"),
            buffer_stock_percent=Decimal("0.0000"),
        ),
        models.Strategy(
            name="Full Air Freight",
            description="Air freight 100% of the affected volume to bypass port disruption.",
            air_freight_percent=Decimal("1.0000"),
            reroute_percent=Decimal("0.0000"),
            buffer_stock_percent=Decimal("0.0000"),
        ),
        models.Strategy(
            name="Port Reroute (Oakland)",
            description="Divert all vessels entirely to Port of Oakland.",
            air_freight_percent=Decimal("0.0000"),
            reroute_percent=Decimal("1.0000"),
            buffer_stock_percent=Decimal("0.0000"),
        ),
        models.Strategy(
            name="Split Strategy",
            description="Reroute 60% via Oakland, air freight top 20% critical SKUs, buffer remaining 20%.",
            air_freight_percent=Decimal("0.2000"),
            reroute_percent=Decimal("0.6000"),
            buffer_stock_percent=Decimal("0.2000"),
        ),
    ]
    db.add_all(strategies)

    # ── 7. Active Disruptions ────────────────────────────────────────────
    from datetime import datetime
    
    # Disruption 1: LA labor strike (original)
    disruption_la = models.Disruption(
        port_id=la_port.id,
        disruption_type="labor_strike",
        severity_score=Decimal("0.8200"),
        expected_delay_days=12,
        confidence_score=Decimal("0.7400"),
        is_active=True,
        detected_at=datetime.utcnow(),
    )
    db.add(disruption_la)
    
    # Disruption 2: Oakland weather event
    disruption_oak = models.Disruption(
        port_id=oak_port.id,
        disruption_type="weather",
        severity_score=Decimal("0.7400"),
        expected_delay_days=8,
        confidence_score=Decimal("0.8100"),
        is_active=True,
        detected_at=datetime.utcnow() - timedelta(hours=6),
    )
    db.add(disruption_oak)
    
    # Disruption 3: Seattle congestion
    disruption_sea = models.Disruption(
        port_id=sea_port.id,
        disruption_type="congestion",
        severity_score=Decimal("0.6500"),
        expected_delay_days=6,
        confidence_score=Decimal("0.6800"),
        is_active=True,
        detected_at=datetime.utcnow() - timedelta(hours=18),
    )
    db.add(disruption_sea)

    db.commit()

    return schemas.SeedDataResponse(
        success=True,
        message="Demo data created — 3 active disruptions: LA labor strike, Oakland weather, Seattle congestion",
        created_counts={
            "companies": 1,
            "ports": 3,
            "skus": 18,
            "inventory": 18,
            "shipments": 47,
            "strategies": 4,
            "disruptions": 3,
        }
    )
