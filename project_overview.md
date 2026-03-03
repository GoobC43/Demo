# HarborGuard AI: Project Overview

## 1. What is HarborGuard AI?
HarborGuard AI is an AI-native maritime disruption decision-support platform built specifically for U.S.-based mid-market electronics manufacturers ($100M–$300M revenue). 

When supply chain disruptions occur (e.g., a port labor strike or severe weather), supply chain teams typically scramble across ERP dashboards and spreadsheets, delaying critical decisions and risking millions in revenue. Existing visibility tools tell you a container is late, but they don't tell you the optimal financial trade-off to fix it. 

HarborGuard AI acts as an operational control tower. It detects disruptions, maps exposure down to the SKU level, simulates mitigation strategies (like air freight vs. rerouting), and recommends financially optimized actions tailored to a company's unique "Risk DNA" (SLA commitments, working capital limits, and risk tolerance). 

**The result:** A 12-hour manual, stressful decision process is transformed into a 2-minute AI-assisted workflow that preserves millions in revenue and protects customer relationships.

## 2. Core Features (The MVP)
Based on what we have built so far, HarborGuard AI operates as a fully functional decision-support system:
*   **Disruption Engine:** Ingests disruption events (e.g., Port of LA labor strike, Oakland weather delays) and assigns severity and confidence scores.
*   **Exposure Mapping:** Matches disrupted ports to inbound shipments in transit, calculating inventory runway (days of stock left) and predicting exact stockout dates by SKU.
*   **Revenue-at-Risk Computation:** Calculates the precise financial impact if no action is taken, based on SKU daily demand, unit price, and predicted delay gaps.
*   **Strategy Simulation & Optimization:** Compares default mitigation strategies (e.g., Do Nothing, Full Air Freight, Port Reroute, or a Split Strategy). It evaluates each strategy mathematically by maximizing *Revenue Preserved* minus *Mitigation Costs* and *SLA Penalties*, strictly bound by working capital constraints.
*   **Actionable LLM Generation:** Uses Google Gemini AI to translate the optimal strategy into instant, actionable drafts:
    *   Professional emails to overseas suppliers requesting reroutes.
    *   Logistics rebooking requests for freight forwarders.
    *   Concise executive summary memos.
*   **Control Tower Dashboard:** A highly polished, artistic, and user-centric web interface featuring an authentic design philosophy (moving away from generic SaaS templates) to present complex data cleanly. Features active disruption alerts, exposure tables, and a seamless approval flow.

## 3. System Architecture
HarborGuard AI is built with a modern, scalable, and responsive technology stack:

### Logical Layers
1.  **Perception Layer:** Monitors external signals (mocked for MVP) to detect port disruptions, categorizing them and extracting key parameters (expected delay, severity).
2.  **Exposure Engine:** Cross-references the disruption with the local database of shipments, SKU demands, and current inventory positions.
3.  **Optimization Core:** The mathematical heart of the system. Evaluates the objective function $\max (R_s - C_s - P_s)$ where $R_s$ is Revenue Preserved, $C_s$ is Mitigation Cost, and $P_s$ is the SLA Penalty.
4.  **Action Layer:** Interfaces with Google Gemini to produce context-aware execution drafts based on the optimal strategy block.
5.  **Control Tower UI:** The human-in-the-loop interface where the Supply Chain VP reviews the math and approves the strategy.

### Technical Stack
*   **Backend:** Python with FastAPI for high-performance, asynchronous API endpoints.
*   **Database:** PostgreSQL (managed locally) accessed via SQLAlchemy ORM.
*   **Frontend:** React, TypeScript, and Vite. Styled with custom, typography-driven CSS (Vanilla CSS & Tailwind utility approaches) following a warm, light-mode authentic design philosophy.
*   **AI/LLM:** Google Gemini API for high-quality, professional text generation (emails and memos) based on the deterministic optimization outputs.

## 4. The Selling Point
**Proactive Optimization vs. Passive Visibility.** 
Legacy tools like SAP IBP, Oracle SCM Cloud, and visibility platforms like FourKites or project44 excel at telling you *where* your container is, but they stumble when telling you *what to do about it financially*. 

HarborGuard AI bridges the gap between tracking and action. It introduces the concept of **Risk DNA**, meaning the AI recommendations respect the specific financial realities of the business. It won't recommend a $\$2M$ pure air-freight strategy if the company's working capital limit is $\$1.5M$. 

By reducing decision latency from days to minutes, a mid-market manufacturer with $\$200M$ in revenue and 8% disruption volatility can see a $9\times$ ROI simply by optimizing their mitigation spend and preserving gross profit that would otherwise be lost to SLA penalties and stockouts.

## 5. Future Roadmap & Vision
While the MVP establishes the core mathematical framework and execution loop for maritime disruptions, the venture-scale vision for HarborGuard AI expands significantly:

*   **Phase 1: Maritime Disruption Optimization (Current MVP)**
*   **Phase 2: Tariff & Geopolitical Risk Modeling.** Expanding the perception layer to ingest policy changes and compute immediate supply chain margin impacts.
*   **Phase 3: Supplier Insolvency Intelligence.** Predictive modeling of tier-1 and tier-2 supplier financial health based on global market signals.
*   **Phase 4: Full Disruption Intelligence Platform.** An end-to-end resilient supply chain operating system.

**Long-Term Technical Extensions:**
*   Moving from deterministic rule-based optimization to **Stochastic Dynamic Programming** to handle constantly shifting lead times.
*   Implementing **Bayesian updating** for disruption probability.
*   Utilizing **Reinforcement Learning** to learn from past mitigation successes and failures, continuously tuning the company's Risk DNA weights.
