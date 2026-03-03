import google.generativeai as genai
from typing import Optional
from decimal import Decimal

from app.core.config import settings

class LLMGeneratorService:
    def __init__(self):
        # Configure Gemini
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel(settings.GEMINI_MODEL)

    def generate_mitigation_drafts(
        self,
        company_name: str,
        disruption_type: str,
        port_name: str,
        delay_days: int,
        affected_skus_count: int,
        revenue_at_risk: Decimal,
        strategy_name: str,
        air_percent: float,
        reroute_percent: float,
        buffer_percent: float,
        risk_tolerance: float,
        sla_target: float,
        working_capital: Decimal
    ) -> dict[str, str]:
        """
        Generate three draft communications using Gemini.
        Returns dict with keys: supplier_email, logistics_email, executive_summary
        """
        
        # Guardrail check for missing API key
        if settings.GEMINI_API_KEY == "MOCK_API_KEY":
            return self._fallback_templates(
                company_name=company_name, 
                port_name=port_name, 
                delay_days=delay_days, 
                strategy_name=strategy_name
            )

        prompt = f"""
        You are a VP of Supply Chain at {company_name}, a mid-market electronics manufacturer.
        A critical supply chain disruption requires immediate action.
        
        DISRUPTION DETAILS:
        - Location: {port_name}
        - Type: {disruption_type.replace('_', ' ').title()}
        - Expected Delay: {delay_days} days
        - Affected SKUs: {affected_skus_count} high-priority items
        - Revenue at Risk: ${revenue_at_risk:,.0f}
        
        COMPANY RISK PROFILE:
        - Risk Tolerance: {'Low' if risk_tolerance < 0.4 else 'Medium' if risk_tolerance < 0.7 else 'High'} ({risk_tolerance:.0%})
        - SLA Target: {sla_target:.0%}
        - Working Capital Available: ${working_capital:,.0f}
        
        SELECTED MITIGATION STRATEGY: {strategy_name}
        - Reroute {reroute_percent:.0%} of shipments via alternate port (Port of Oakland)
        - Air freight {air_percent:.0%} of most critical SKUs
        - Build buffer stock for {buffer_percent:.0%} of affected items
        
        Generate the following three items clearly separated by '---':
        
        1. SUPPLIER EMAIL: Professional email to primary Taiwanese supplier requesting immediate rerouting of specific containers to Port of Oakland. Include reference to contract terms and request confirmation within 4 hours.
        ---
        2. LOGISTICS REQUEST: Formal request to freight forwarder to execute air freight booking for priority SKUs and coordinate rerouting. Specify timeline and handling requirements.
        ---
        3. EXECUTIVE SUMMARY: Three bullet points for COO briefing covering: (a) situation severity, (b) recommended action and financial impact, (c) next steps and timeline.
        
        Use professional supply chain terminology. Be specific and actionable. Do not use placeholders.
        """
        
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=settings.GEMINI_TEMPERATURE,
                    max_output_tokens=settings.GEMINI_MAX_TOKENS,
                )
            )
            
            text = response.text
            sections = [s.strip() for s in text.split("---") if s.strip()]
            
            return {
                "supplier_email": sections[0] if len(sections) > 0 else text[:1000],
                "logistics_email": sections[1] if len(sections) > 1 else text[1000:2000],
                "executive_summary": sections[2] if len(sections) > 2 else text[-500:]
            }
            
        except Exception as e:
            # Fallback templates if LLM fails (e.g. rate limit, network error)
            return self._fallback_templates(
                company_name=company_name, 
                port_name=port_name, 
                delay_days=delay_days, 
                strategy_name=strategy_name
            )

    def _fallback_templates(self, **kwargs) -> dict[str, str]:
        """Hardcoded fallback if Gemini API fails or is not configured."""
        return {
            "supplier_email": f"Subject: Urgent: Reroute Required - {kwargs.get('port_name')} Disruption\n\nDear Supplier,\n\nDue to the ongoing disruption at {kwargs.get('port_name')}, we need to immediately reroute all in-transit containers to Port of Oakland. Please confirm receipt and ETA.\n\nBest regards,\nVP Supply Chain",
            "logistics_email": "Please execute emergency air freight booking and coordinate rerouting per attached manifest.",
            "executive_summary": "• Situation: Port disruption threatening $38M revenue\n• Action: Mitigation strategy selected\n• Timeline: Execute within 24 hours"
        }
