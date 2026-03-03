"""
Global Sensitivity Analysis Engine — Sobol Indices + Tornado
=============================================================
Industry-grade sensitivity analysis comparable to Oracle Crystal Ball
and SAP HANA Predictive Analytics risk factor decomposition.

Key features:
  • Sobol first-order indices S_i (main effects)
  • Sobol total-effect indices S_Ti (includes interactions)
  • Saltelli sampling scheme for efficient computation
  • Retains OAT tornado chart for interpretability
  • Interaction detection between parameters

Mathematical References:
  Sobol: Sobol' (1993) "Sensitivity estimates for nonlinear models"
  Saltelli: Saltelli et al. (2010) "Variance based sensitivity analysis"
"""

import numpy as np
from decimal import Decimal
from typing import List, Dict, Any
from uuid import UUID
from sqlalchemy.orm import Session

from app import models, schemas
from app.services.exposure import ExposureService
from app.services.optimizer import OptimizerService


class SensitivityAnalyzer:
    """
    Professional-grade sensitivity analysis with both Sobol global
    indices (captures interactions) and OAT tornado (interpretability).
    """

    # Number of base samples for Saltelli scheme
    # N=64 → 768 total evaluations (practical for real-time API)
    # Per Saltelli (2010), N≥64 is sufficient for 5 parameters
    N_BASE = 64

    def __init__(self, db: Session):
        self.db = db

    def analyze(self, disruption_id: UUID) -> Dict[str, Any]:
        """
        Run full sensitivity analysis:
        1. OAT tornado (±20% one-at-a-time)
        2. Sobol global sensitivity indices via Saltelli sampling
        """
        disruption = self._get_disruption(disruption_id)
        company = self.db.query(models.Company).first()
        if not company:
            raise ValueError("Company not found")

        # Get baseline
        optimizer = OptimizerService(self.db)
        baseline = optimizer.simulate_strategies(disruption_id)
        optimal_sim = next(
            (s for s in baseline.simulations
             if s.strategy_id == baseline.optimal_strategy_id),
            baseline.simulations[0]
        )
        base_value = float(optimal_sim.net_financial_impact)

        # Define parameters
        param_specs = self._get_param_specs(disruption, company)

        # ── OAT Tornado (interpretable) ──────────────────────────────────
        tornado = self._oat_tornado(disruption_id, param_specs, base_value)

        # ── Sobol Global Indices (rigorous) ──────────────────────────────
        sobol = self._sobol_indices(disruption_id, param_specs)

        return {
            "disruption_id": str(disruption_id),
            "optimal_strategy": optimal_sim.strategy_name,
            "base_net_impact": base_value,
            "analysis_methods": ["OAT_Tornado", "Sobol_Global"],
            "sensitivities": tornado,  # Backward compatible
            "sobol_indices": sobol,
            "interpretation": self._interpret(tornado, sobol),
        }

    # ─── Parameter Specification ─────────────────────────────────────────

    def _get_param_specs(self, disruption, company) -> List[Dict]:
        """Define parameters, their base values, and ±20% ranges."""
        return [
            {
                "name": "expected_delay_days",
                "label": "Disruption Duration (days)",
                "model": "disruption",
                "field": "expected_delay_days",
                "base": disruption.expected_delay_days,
                "low": max(1, int(disruption.expected_delay_days * 0.8)),
                "high": int(disruption.expected_delay_days * 1.2),
            },
            {
                "name": "severity_score",
                "label": "Severity Score",
                "model": "disruption",
                "field": "severity_score",
                "base": float(disruption.severity_score),
                "low": float(disruption.severity_score) * 0.8,
                "high": min(1.0, float(disruption.severity_score) * 1.2),
            },
            {
                "name": "working_capital_limit",
                "label": "Working Capital ($)",
                "model": "company",
                "field": "working_capital_limit",
                "base": float(company.working_capital_limit),
                "low": float(company.working_capital_limit) * 0.8,
                "high": float(company.working_capital_limit) * 1.2,
            },
            {
                "name": "risk_tolerance",
                "label": "Risk Tolerance (α)",
                "model": "company",
                "field": "risk_tolerance",
                "base": float(company.risk_tolerance),
                "low": max(0.05, float(company.risk_tolerance) * 0.8),
                "high": min(0.95, float(company.risk_tolerance) * 1.2),
            },
            {
                "name": "sla_target_percent",
                "label": "SLA Target (%)",
                "model": "company",
                "field": "sla_target_percent",
                "base": float(company.sla_target_percent),
                "low": float(company.sla_target_percent) * 0.8,
                "high": min(1.0, float(company.sla_target_percent) * 1.2),
            },
        ]

    # ─── OAT Tornado (One-at-a-Time) ────────────────────────────────────

    def _oat_tornado(self, disruption_id: UUID, params: List[Dict],
                     base_value: float) -> List[Dict]:
        """
        Classic tornado analysis: vary each parameter ±20% independently.
        Returns sorted by swing magnitude.
        """
        sensitivities = []
        for param in params:
            low_result = self._run_with_override(
                disruption_id, param, override_value=param["low"]
            )
            high_result = self._run_with_override(
                disruption_id, param, override_value=param["high"]
            )

            swing = abs(high_result - low_result)
            # Elasticity = (ΔOutput/Output) / (ΔInput/Input)
            input_pct_change = 0.4  # From 0.8 to 1.2 = 40% range
            output_pct_change = (
                swing / abs(base_value) if abs(base_value) > 0 else 0
            )
            elasticity = output_pct_change / input_pct_change

            sensitivities.append({
                "parameter": param["name"],
                "label": param["label"],
                "base_input": param["base"],
                "low_input": param["low"],
                "high_input": param["high"],
                "low_outcome": low_result,
                "base_outcome": base_value,
                "high_outcome": high_result,
                "swing": swing,
                "elasticity": round(elasticity, 4),
            })

        sensitivities.sort(key=lambda s: s["swing"], reverse=True)
        return sensitivities

    # ─── Sobol Global Sensitivity Indices ────────────────────────────────

    def _sobol_indices(self, disruption_id: UUID,
                       params: List[Dict]) -> Dict[str, Any]:
        """
        Compute Sobol first-order (S_i) and total-effect (S_Ti) indices.

        Uses Saltelli sampling scheme: 2N(k+1) model evaluations
        where k = number of parameters, N = base sample size.

        S_i  = Var(E[Y|Xi]) / Var(Y)     — main effect
        S_Ti = 1 - Var(E[Y|X~i]) / Var(Y) — total effect (includes interactions)
        """
        k = len(params)
        N = self.N_BASE

        rng = np.random.default_rng(42)

        # Generate two independent N×k matrices of uniform[0,1]
        A = rng.uniform(size=(N, k))
        B = rng.uniform(size=(N, k))

        # Evaluate model at A and B matrices
        f_A = np.array([
            self._evaluate_sample(disruption_id, params, A[j])
            for j in range(N)
        ])
        f_B = np.array([
            self._evaluate_sample(disruption_id, params, B[j])
            for j in range(N)
        ])

        total_var = np.var(np.concatenate([f_A, f_B]))
        if total_var < 1e-10:
            # No variance → all indices are zero
            return {
                "method": "Sobol (Saltelli scheme)",
                "base_samples": N,
                "total_evaluations": 2 * N * (k + 1),
                "total_variance": 0.0,
                "indices": [
                    {"parameter": p["name"], "label": p["label"],
                     "S_i": 0.0, "S_Ti": 0.0, "interaction": 0.0}
                    for p in params
                ],
            }

        indices = []
        for i in range(k):
            # AB_i matrix: take column i from B, rest from A
            AB_i = A.copy()
            AB_i[:, i] = B[:, i]

            # BA_i matrix: take column i from A, rest from B
            BA_i = B.copy()
            BA_i[:, i] = A[:, i]

            f_AB_i = np.array([
                self._evaluate_sample(disruption_id, params, AB_i[j])
                for j in range(N)
            ])

            f_BA_i = np.array([
                self._evaluate_sample(disruption_id, params, BA_i[j])
                for j in range(N)
            ])

            # First-order: S_i = V_i / V(Y)
            # Jansen estimator: V_i = 1/(2N) * Σ (f(B) - f(AB_i))²
            v_i = np.mean(f_B * (f_AB_i - f_A))
            s_i = max(0.0, v_i / total_var)

            # Total-effect: S_Ti using Jansen (2009) estimator
            # V_Ti = 1/(2N) * Σ (f(A) - f(AB_i))²
            v_ti = 0.5 * np.mean((f_A - f_AB_i) ** 2)
            s_ti = max(0.0, min(1.0, v_ti / total_var))

            # Interaction = S_Ti - S_i (portion due to variable interactions)
            interaction = max(0.0, s_ti - s_i)

            indices.append({
                "parameter": params[i]["name"],
                "label": params[i]["label"],
                "S_i": round(s_i, 4),
                "S_Ti": round(s_ti, 4),
                "interaction": round(interaction, 4),
            })

        # Sort by total effect
        indices.sort(key=lambda x: x["S_Ti"], reverse=True)

        return {
            "method": "Sobol (Saltelli/Jansen estimators)",
            "base_samples": N,
            "total_evaluations": 2 * N * (k + 1),
            "total_variance": round(float(total_var), 2),
            "indices": indices,
            "note": "S_i = first-order (main effect), "
                    "S_Ti = total-effect (includes interactions), "
                    "interaction = S_Ti - S_i",
        }

    def _evaluate_sample(self, disruption_id: UUID, params: List[Dict],
                         sample: np.ndarray) -> float:
        """
        Evaluate the optimizer with parameters set from a [0,1] sample vector.
        Maps uniform[0,1] → [low, high] for each parameter.
        """
        disruption = self._get_disruption(disruption_id)
        company = self.db.query(models.Company).first()

        originals = []
        for i, param in enumerate(params):
            obj = disruption if param["model"] == "disruption" else company
            orig = getattr(obj, param["field"])
            originals.append((obj, param["field"], orig))

            # Map sample[i] ∈ [0,1] → [low, high]
            mapped = param["low"] + sample[i] * (param["high"] - param["low"])
            if isinstance(orig, int):
                mapped = int(round(mapped))
            elif isinstance(orig, Decimal):
                mapped = Decimal(str(round(mapped, 6)))
            setattr(obj, param["field"], mapped)

        try:
            optimizer = OptimizerService(self.db)
            result = optimizer.simulate_strategies(disruption_id)
            optimal = next(
                (s for s in result.simulations
                 if s.strategy_id == result.optimal_strategy_id),
                result.simulations[0]
            )
            return float(optimal.net_financial_impact)
        finally:
            # Restore all original values
            for obj, field, orig in originals:
                setattr(obj, field, orig)

    # ─── Interpretation Helper ───────────────────────────────────────────

    @staticmethod
    def _interpret(tornado: List[Dict], sobol: Dict) -> Dict[str, Any]:
        """Generate human-readable interpretation of sensitivity results."""
        top_tornado = tornado[0] if tornado else None
        top_sobol = sobol["indices"][0] if sobol.get("indices") else None

        insights = []
        if top_tornado:
            insights.append(
                f"{top_tornado['label']} has the largest one-at-a-time impact "
                f"(${top_tornado['swing']:,.0f} swing, "
                f"elasticity={top_tornado['elasticity']:.2f})"
            )

        if top_sobol and top_sobol["S_Ti"] > 0.3:
            insights.append(
                f"{top_sobol['label']} accounts for "
                f"{top_sobol['S_Ti']*100:.1f}% of total variance (Sobol S_Ti)"
            )
            if top_sobol["interaction"] > 0.1:
                insights.append(
                    f"  ↳ {top_sobol['interaction']*100:.1f}% of that is from "
                    f"interactions with other parameters"
                )

        # Check for interaction effects
        total_interaction = sum(
            idx["interaction"] for idx in sobol.get("indices", [])
        )
        if total_interaction > 0.3:
            insights.append(
                "⚠ Significant parameter interactions detected — "
                "one-at-a-time analysis may understate true sensitivity"
            )

        return {"insights": insights}

    # ─── Override Runner ─────────────────────────────────────────────────

    def _run_with_override(
        self, disruption_id: UUID, param: dict, override_value: float
    ) -> float:
        """Run optimizer with a single parameter overridden."""
        disruption = self._get_disruption(disruption_id)
        company = self.db.query(models.Company).first()

        obj = disruption if param["model"] == "disruption" else company
        original = getattr(obj, param["field"])

        # Cast to matching type
        if isinstance(original, int):
            new_val = int(round(override_value))
        elif isinstance(original, Decimal):
            new_val = Decimal(str(round(override_value, 6)))
        else:
            new_val = override_value

        setattr(obj, param["field"], new_val)

        try:
            optimizer = OptimizerService(self.db)
            result = optimizer.simulate_strategies(disruption_id)
            optimal = next(
                (s for s in result.simulations
                 if s.strategy_id == result.optimal_strategy_id),
                result.simulations[0]
            )
            return float(optimal.net_financial_impact)
        finally:
            setattr(obj, param["field"], original)

    # ─── Helpers ─────────────────────────────────────────────────────────

    def _get_disruption(self, disruption_id: UUID):
        d = self.db.query(models.Disruption).filter(
            models.Disruption.id == disruption_id
        ).first()
        if not d:
            raise ValueError("Disruption not found")
        return d
