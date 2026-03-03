"""
Perception Layer — LLM-Based Disruption Detection
===================================================
Per Arch.tex §3.1: Detect disruption events, assign severity score.

Uses Gemini to classify raw news text and extract structured
disruption parameters (port, type, severity, delay, confidence).
"""

import json
import google.generativeai as genai
from typing import Optional, Dict, Any
from sqlalchemy.orm import Session

from app.core.config import settings
from app import models


class PerceptionService:
    """Classify news text as maritime disruptions using LLM."""

    def __init__(self, db: Session):
        self.db = db
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def classify_news(self, headline: str, body: str = "") -> Dict[str, Any]:
        """
        Classify whether text describes a maritime supply chain disruption.
        Returns structured detection result.
        """
        # Guardrail: fallback if no real API key
        if settings.GEMINI_API_KEY == "MOCK_API_KEY":
            return self._fallback_classification(headline)

        prompt = f"""You are a maritime supply chain risk analyst.
Analyze the following news and determine if it describes a maritime supply chain disruption.

HEADLINE: {headline}
BODY: {body}

Respond with ONLY a JSON object (no markdown, no explanation):
{{
    "is_disruption": true/false,
    "port_name": "name of affected port or null",
    "port_code": "2-3 letter code like LA, OAK, SEA or null",
    "disruption_type": "labor_strike|weather|congestion|equipment_failure|security|null",
    "severity_score": 0.0-1.0,
    "expected_delay_days": integer or null,
    "confidence": 0.0-1.0,
    "summary": "one-line summary of the disruption"
}}"""

        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.1,  # Very low for classification
                    max_output_tokens=512,
                )
            )
            text = response.text.strip()
            # Strip markdown fences if present
            if text.startswith("```"):
                text = text.split("\n", 1)[1].rsplit("```", 1)[0].strip()

            result = json.loads(text)
            return self._validate_result(result)

        except Exception as e:
            return self._fallback_classification(headline)

    def detect_and_create(self, headline: str, body: str = "") -> Optional[models.Disruption]:
        """
        Classify news and, if a disruption is detected, create a Disruption record.
        Returns the created Disruption or None.
        """
        classification = self.classify_news(headline, body)

        if not classification.get("is_disruption"):
            return None

        # Find or create port
        port_code = classification.get("port_code", "LA")
        port = self.db.query(models.Port).filter(
            models.Port.code == port_code
        ).first()

        if not port:
            # If port not found, use the first available port
            port = self.db.query(models.Port).first()
            if not port:
                return None

        from decimal import Decimal
        from datetime import datetime

        disruption = models.Disruption(
            port_id=port.id,
            disruption_type=classification.get("disruption_type", "unknown"),
            severity_score=Decimal(str(classification.get("severity_score", 0.5))),
            expected_delay_days=classification.get("expected_delay_days", 7),
            confidence_score=Decimal(str(classification.get("confidence", 0.5))),
            is_active=True,
            detected_at=datetime.utcnow(),
        )
        self.db.add(disruption)
        self.db.commit()
        self.db.refresh(disruption)
        return disruption

    def _validate_result(self, result: dict) -> dict:
        """Ensure result has required fields with valid types."""
        return {
            "is_disruption": bool(result.get("is_disruption", False)),
            "port_name": result.get("port_name"),
            "port_code": result.get("port_code"),
            "disruption_type": result.get("disruption_type", "unknown"),
            "severity_score": min(1.0, max(0.0, float(result.get("severity_score", 0.5)))),
            "expected_delay_days": int(result.get("expected_delay_days") or 7),
            "confidence": min(1.0, max(0.0, float(result.get("confidence", 0.5)))),
            "summary": result.get("summary", ""),
        }

    def _fallback_classification(self, headline: str) -> dict:
        """Simple keyword-based fallback when LLM is unavailable."""
        headline_lower = headline.lower()
        keywords = {
            "strike": ("labor_strike", 0.8),
            "storm": ("weather", 0.7),
            "hurricane": ("weather", 0.9),
            "typhoon": ("weather", 0.9),
            "congestion": ("congestion", 0.6),
            "closure": ("congestion", 0.7),
            "shutdown": ("labor_strike", 0.85),
        }

        for keyword, (dtype, severity) in keywords.items():
            if keyword in headline_lower:
                return {
                    "is_disruption": True,
                    "port_name": "Port of Los Angeles",
                    "port_code": "LA",
                    "disruption_type": dtype,
                    "severity_score": severity,
                    "expected_delay_days": 10,
                    "confidence": 0.6,
                    "summary": f"Keyword '{keyword}' detected in headline",
                }

        return {
            "is_disruption": False,
            "port_name": None,
            "port_code": None,
            "disruption_type": None,
            "severity_score": 0.0,
            "expected_delay_days": None,
            "confidence": 0.8,
            "summary": "No maritime disruption detected",
        }
