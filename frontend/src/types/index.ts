// types/index.ts
export interface Company {
    id: string;
    name: string;
    revenue_annual_millions: number;
    gross_margin_percent: number;
    risk_tolerance: number;
    sla_weight: number;
    working_capital_limit: number;
    customer_churn_sensitivity: number;
    sla_target_percent: number;
    created_at: string;
    updated_at: string;
}

export interface Disruption {
    id: string;
    port_id: string;
    disruption_type: string;
    severity_score: number;
    expected_delay_days: number;
    confidence_score: number;
    is_active: boolean;
    detected_at: string;
    resolved_at?: string;
}

export interface Strategy {
    id: string;
    name: string;
    description: string;
    air_freight_percent: number;
    reroute_percent: number;
    buffer_stock_percent: number;
    cost_multiplier_air: number;
    cost_multiplier_reroute: number;
    holding_cost_per_unit_per_day: number;
}

export interface StrategySimulation {
    strategy_id: string;
    strategy_name: string;
    description: string;
    revenue_preserved: number;
    mitigation_cost: number;
    sla_achieved: number;
    sla_penalty_cost: number;
    net_financial_impact: number;
    working_capital_required: number;
    is_feasible: boolean;
    feasibility_reason?: string;
}

export interface StrategyComparison {
    disruption_id: string;
    simulations: StrategySimulation[];
    optimal_strategy_id: string;
    company_risk_profile: {
        risk_tolerance: number;
        working_capital_limit: number;
        sla_target_percent: number;
        sla_weight: number;
    };
}

export interface Recommendation {
    id: string;
    disruption_id: string;
    selected_strategy: Strategy;
    confidence_score: number;
    reasoning: string;
    revenue_preserved: number;
    mitigation_cost: number;
    sla_achieved: number;
    sla_penalty_cost: number;
    net_financial_impact: number;
    generated_email_supplier?: string;
    generated_email_logistics?: string;
    generated_executive_summary?: string;
    requires_approval: boolean;
    approved_by?: string;
    approved_at?: string;
    created_at: string;
}

export interface DashboardSummary {
    company: Company;
    active_disruption?: Disruption;
    active_disruptions: Disruption[];
    active_recommendation?: Recommendation;
    total_revenue_at_risk?: number;
    key_metrics: {
        affected_skus: number;
        affected_shipments: number;
    };
}

export interface SKUExposure {
    sku_id: string;
    sku_code: string;
    description?: string;
    daily_demand: number;
    unit_price: number;
    unit_margin: number;
    on_hand_units: number;
    inventory_runway_days: number;
    stockout_date: string;
    revenue_at_risk: number;
    margin_at_risk: number;
    affected_shipment_ids: string[];
}

export interface ExposureResult {
    disruption_id: string;
    company_id: string;
    affected_skus: SKUExposure[];
    total_revenue_at_risk: number;
    total_margin_at_risk: number;
    total_affected_shipments: number;
    total_affected_quantity: number;
}
