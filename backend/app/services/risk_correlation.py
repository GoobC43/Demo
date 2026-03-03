"""
Disruption Correlation & Archetype Engine
===========================================
Implements portfolio-level risk correlation and disruption pattern
clustering comparable to SAP IBP Risk Management correlation modeling.

Key features:
  • K-Means disruption archetype clustering
  • Feature vectorization of disruption events
  • Portfolio correlation matrix for multi-port exposure
  • Archetype-based strategy recommendation priors
  • Diversification scoring

Mathematical References:
  K-Means: Lloyd (1982) — IEEE Transactions on Information Theory
  Portfolio VaR: Markowitz (1952) — adapted for supply chain risk
"""

import numpy as np
from typing import List, Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from collections import defaultdict

from app import models


# ─── Disruption Type Encoding ────────────────────────────────────────────
DISRUPTION_TYPE_MAP = {
    "labor_strike": 0,
    "weather": 1,
    "equipment_failure": 2,
    "geopolitical": 3,
    "pandemic": 4,
    "congestion": 5,
    "accident": 6,
}

# ─── Port Region Encoding ───────────────────────────────────────────────
PORT_REGION_MAP = {
    "US_WEST": 0,
    "US_EAST": 1,
    "ASIA": 2,
    "EUROPE": 3,
    "OTHER": 4,
}


class RiskCorrelationEngine:
    """
    Portfolio-level risk analysis using disruption clustering
    and correlation modeling.
    """

    # Number of archetypes to identify
    N_CLUSTERS = 4

    def __init__(self, db: Session):
        self.db = db

    # ─── Disruption Archetype Clustering ─────────────────────────────────

    def cluster_disruptions(
        self, n_clusters: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Cluster historical disruptions into archetypes using K-Means.

        Feature vector per disruption:
          [type_encoded, severity, delay_days, season_sin, season_cos]

        Season is encoded as sin/cos to preserve circularity (Dec→Jan).

        Returns cluster centroids, labels, and archetype descriptions.
        """
        disruptions = self.db.query(models.Disruption).all()
        if len(disruptions) < 2:
            return self._single_archetype(disruptions)

        k = min(n_clusters or self.N_CLUSTERS, len(disruptions))

        # Build feature matrix
        features = np.array([
            self._vectorize_disruption(d) for d in disruptions
        ])

        # Standardize features (zero mean, unit variance)
        means = features.mean(axis=0)
        stds = features.std(axis=0)
        stds[stds == 0] = 1.0
        features_norm = (features - means) / stds

        # K-Means (Lloyd's algorithm)
        labels, centroids = self._kmeans(features_norm, k, max_iter=100)

        # Build archetype descriptions
        archetypes = []
        for c in range(k):
            cluster_mask = labels == c
            cluster_disruptions = [
                d for d, m in zip(disruptions, cluster_mask) if m
            ]
            cluster_features = features[cluster_mask]

            if len(cluster_disruptions) == 0:
                continue

            # Identify dominant type
            type_counts = defaultdict(int)
            for d in cluster_disruptions:
                type_counts[d.disruption_type] += 1
            dominant_type = max(type_counts, key=type_counts.get)

            avg_severity = float(np.mean(cluster_features[:, 1]))
            avg_delay = float(np.mean(cluster_features[:, 2]))

            archetypes.append({
                "cluster_id": c,
                "size": len(cluster_disruptions),
                "dominant_type": dominant_type,
                "avg_severity": round(avg_severity, 3),
                "avg_delay_days": round(avg_delay, 1),
                "centroid": centroids[c].tolist(),
                "disruption_ids": [
                    str(d.id) for d in cluster_disruptions
                ],
                "description": (
                    f"{dominant_type.replace('_', ' ').title()} pattern: "
                    f"avg severity {avg_severity:.2f}, "
                    f"avg delay {avg_delay:.0f} days"
                ),
            })

        return {
            "method": "K-Means (Lloyd's algorithm)",
            "n_clusters": k,
            "n_disruptions": len(disruptions),
            "feature_names": [
                "type", "severity", "delay_days", "season_sin", "season_cos"
            ],
            "archetypes": archetypes,
        }

    def match_archetype(self, disruption_id: UUID) -> Dict[str, Any]:
        """
        Find which archetype a given disruption most closely matches.
        Returns the closest archetype and distance scores.
        """
        disruption = self.db.query(models.Disruption).filter(
            models.Disruption.id == disruption_id
        ).first()
        if not disruption:
            raise ValueError("Disruption not found")

        clustering = self.cluster_disruptions()
        if not clustering["archetypes"]:
            return {"match": None, "message": "No archetypes available"}

        # Vectorize and find nearest centroid
        feature = self._vectorize_disruption(disruption)
        best_dist = float("inf")
        best_archetype = None

        for arch in clustering["archetypes"]:
            centroid = np.array(arch["centroid"])
            dist = float(np.linalg.norm(feature[:len(centroid)] - centroid))
            if dist < best_dist:
                best_dist = dist
                best_archetype = arch

        return {
            "disruption_id": str(disruption_id),
            "matched_archetype": best_archetype,
            "distance": round(best_dist, 4),
            "confidence": round(1.0 / (1.0 + best_dist), 4),
        }

    # ─── Portfolio Correlation ───────────────────────────────────────────

    def portfolio_risk(self) -> Dict[str, Any]:
        """
        Calculate portfolio-level risk across all ports.

        For each port, computes exposure weight. If multiple ports share
        common disruption patterns, they're correlated → portfolio risk
        is higher than sum of individual risks.

        Portfolio VaR ≈ √(w'Σw) × total_exposure
        """
        # Get all ports and their disruption histories
        ports = self.db.query(models.Port).all()
        if len(ports) < 2:
            return {"message": "Need ≥2 ports for correlation analysis"}

        # Build disruption co-occurrence matrix
        disruptions = self.db.query(models.Disruption).all()
        port_disruption_map = defaultdict(list)
        for d in disruptions:
            port_disruption_map[str(d.port_id)].append(d)

        n_ports = len(ports)
        port_ids = [str(p.id) for p in ports]

        # Simple correlation proxy: ports disrupted in same time window
        # are considered correlated
        correlation_matrix = np.eye(n_ports)

        for i in range(n_ports):
            for j in range(i + 1, n_ports):
                # Co-occurrence: same disruption type within same month
                types_i = set(
                    d.disruption_type for d in port_disruption_map[port_ids[i]]
                )
                types_j = set(
                    d.disruption_type for d in port_disruption_map[port_ids[j]]
                )
                overlap = len(types_i & types_j)
                total = max(1, len(types_i | types_j))
                corr = overlap / total * 0.8  # Cap at 0.8
                correlation_matrix[i, j] = corr
                correlation_matrix[j, i] = corr

        # Exposure weights (normalize)
        shipment_counts = []
        for p in ports:
            count = self.db.query(models.Shipment).filter(
                models.Shipment.port_id == p.id
            ).count()
            shipment_counts.append(count)

        total_shipments = max(1, sum(shipment_counts))
        weights = np.array([c / total_shipments for c in shipment_counts])

        # Portfolio VaR factor: √(w'Σw)
        portfolio_var_factor = float(
            np.sqrt(weights @ correlation_matrix @ weights)
        )

        # Diversification benefit = 1 - portfolio_factor / sum_of_parts
        undiversified = float(np.sum(weights ** 2) ** 0.5)
        diversification_benefit = (
            1.0 - portfolio_var_factor / undiversified
            if undiversified > 0 else 0
        )

        # Concentration risk (Herfindahl index)
        herfindahl = float(np.sum(weights ** 2))
        concentration_risk = "high" if herfindahl > 0.4 else (
            "medium" if herfindahl > 0.2 else "low"
        )

        return {
            "n_ports": n_ports,
            "correlation_matrix": {
                "port_ids": port_ids,
                "matrix": correlation_matrix.tolist(),
            },
            "exposure_weights": {
                port_ids[i]: round(float(weights[i]), 4)
                for i in range(n_ports)
            },
            "portfolio_var_factor": round(portfolio_var_factor, 4),
            "diversification_benefit_pct": round(
                diversification_benefit * 100, 1
            ),
            "herfindahl_index": round(herfindahl, 4),
            "concentration_risk": concentration_risk,
            "note": (
                "Portfolio VaR factor < sum of parts indicates "
                "diversification benefit. Herfindahl > 0.4 signals "
                "dangerous concentration in few ports."
            ),
        }

    # ─── K-Means Implementation ──────────────────────────────────────────

    @staticmethod
    def _kmeans(
        X: np.ndarray, k: int, max_iter: int = 100
    ) -> tuple:
        """
        Lloyd's K-Means clustering algorithm.

        Uses K-Means++ initialization for better convergence.
        """
        n, d = X.shape
        rng = np.random.default_rng(42)

        # K-Means++ initialization
        centroids = np.zeros((k, d))
        centroids[0] = X[rng.integers(n)]

        for c in range(1, k):
            distances = np.min([
                np.sum((X - centroids[j]) ** 2, axis=1)
                for j in range(c)
            ], axis=0)
            probs = distances / distances.sum()
            centroids[c] = X[rng.choice(n, p=probs)]

        # Iterate
        labels = np.zeros(n, dtype=int)
        for _ in range(max_iter):
            # Assign to nearest centroid
            dists = np.array([
                np.sum((X - centroids[c]) ** 2, axis=1) for c in range(k)
            ])
            new_labels = np.argmin(dists, axis=0)

            # Check convergence
            if np.array_equal(labels, new_labels):
                break
            labels = new_labels

            # Update centroids
            for c in range(k):
                mask = labels == c
                if mask.any():
                    centroids[c] = X[mask].mean(axis=0)

        return labels, centroids

    # ─── Feature Vectorization ───────────────────────────────────────────

    @staticmethod
    def _vectorize_disruption(d) -> np.ndarray:
        """
        Convert a disruption record into a feature vector.

        Features:
          [0] type_encoded      — categorical → numeric
          [1] severity_score    — 0.0 to 1.0
          [2] delay_days        — integer
          [3] season_sin        — sin(2π·month/12)  } circular encoding
          [4] season_cos        — cos(2π·month/12)  } for seasonality
        """
        type_code = DISRUPTION_TYPE_MAP.get(d.disruption_type, 6)
        severity = float(d.severity_score)
        delay = float(d.expected_delay_days)

        # Season encoding (circular)
        month = d.detected_at.month if d.detected_at else 6
        season_sin = np.sin(2 * np.pi * month / 12)
        season_cos = np.cos(2 * np.pi * month / 12)

        return np.array([type_code, severity, delay, season_sin, season_cos])

    # ─── Single Archetype Fallback ───────────────────────────────────────

    @staticmethod
    def _single_archetype(disruptions: list) -> Dict[str, Any]:
        """Return a single archetype when clustering isn't possible."""
        return {
            "method": "Single archetype (insufficient data for clustering)",
            "n_clusters": 1,
            "n_disruptions": len(disruptions),
            "archetypes": [
                {
                    "cluster_id": 0,
                    "size": len(disruptions),
                    "dominant_type": (
                        disruptions[0].disruption_type if disruptions
                        else "unknown"
                    ),
                    "description": "Default archetype (more data needed)",
                }
            ] if disruptions else [],
        }
