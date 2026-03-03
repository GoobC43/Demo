# HarborGuard AI: Algorithmic & Predictive Models Overview

HarborGuard AI moves beyond basic supply chain visibility by acting as a mathematical decision engine. Instead of just tracking containers, the system uses a combination of deterministic modeling, stochastic simulation, and machine learning to optimize financial outcomes.

This document details the core algorithms and prediction models powering the platform.

---

## 1. Deterministic Exposure & Inventory Runway Model
**File:** `backend/app/services/exposure.py`
**Purpose:** Maps the physical disruption to exact financial exposure before the event occurs.
**Algorithm Type:** Deterministic Inventory Physics

**How it works:**
For every SKU in transit to the disrupted port, the system calculates the **Inventory Runway**:
```math
Runway_i = \frac{Inventory_{On\_Hand}}{Daily\_Demand}
```
Next, it compares the adjusted arrival date (Original ETA + Expected Delay) against the Runway. If the delay exceeds the runway, it triggers a **Stockout Event**:
```math
Stockout\_Risk_i = (ETA_{adjusted} > Runway_{days})
```
**Output:** Generates the exact `Revenue_at_Risk` by calculating the gap between the runway exhaustion and the delayed arrival, multiplied by daily demand and unit price.

---

## 2. Constrained Utility Maximization (Optimization Engine)
**File:** `backend/app/services/optimizer.py`
**Purpose:** Recommends the mathematically optimal mitigation strategy based on the company's "Risk DNA".
**Algorithm Type:** Multi-Objective Linear Optimization

**How it works:**
The engine evaluates predefined strategies (e.g., Do Nothing, Air Freight, Reroute, Split Strategy). For each strategy $s$, the objective function maximizes Net Financial Impact:
```math
\max_{s} \left( \alpha \cdot Revenue\_Preserved_s - \beta \cdot Mitigation\_Cost_s - \delta \cdot SLA\_Penalty_s \right)
```
*Constraints:*
*   $Mitigation\_Cost_s \leq Working\_Capital\_Limit$
*   Wait times and capacities of alternate ports (e.g., Oakland/Seattle).

**Key Parameters (Risk DNA):**
*   $\alpha$: Risk tolerance multiplier
*   $\beta$: Cost sensitivity
*   $\delta$: SLA penalty severity 

---

## 3. Monte Carlo Risk Simulation
**File:** `backend/app/services/monte_carlo.py`
**Purpose:** Quantifies uncertainty in the disruption delay and evaluates how strategies perform under volatility.
**Algorithm Type:** Stochastic Simulation

**How it works:**
Because "12 days of delay" is an estimate, the Monte Carlo engine models the delay as a probability distribution (e.g., Log-Normal or Gaussian):
```math
Delay_{sim} \sim \mathcal{N}(\mu, \sigma^2)
```
The simulation runs hundreds of iterations (e.g., 500 scenarios) sampling different delay values, ocean costs, and air freight surges. 
For each iteration, it runs the Optimization Engine.
**Output:** Calculates the Expected Value ($E[x]$) and probability bounds (P10, P50, and P90) of the net impact, proving the resilience of the recommended strategy.

---

## 4. Parameter Sensitivity Analysis (Tornado Modeling)
**File:** `backend/app/services/sensitivity.py`
**Purpose:** Identifies which variables have the most outsized impact on the strategy's success.
**Algorithm Type:** Partial Derivative / One-At-A-Time (OAT) Perturbation

**How it works:**
The engine computationally "bumps" critical parameters (like Air Freight Cost, Expected Delay, and Demand Surge) by $\pm 10\%$ and measures the swing in the final Net Impact.
```math
Sensitivity_{param} = \frac{\Delta Net\_Impact}{\Delta Parameter}
```
**Output:** Ranks the parameters by effect size, generating the data required for classic "Tornado Charts" so executives know exactly which assumptions carry the most risk.

---

## 5. Bayesian Learning & ML Feedback Loop
**File:** `backend/app/services/learning.py`
**Purpose:** Allows the system to become smarter over time by learning from past disruptions.
**Algorithm Type:** Reinforcement Learning / Bayesian Updating

**How it works:**
When a disruption concludes, the user inputs the *actual* delay and *actual* cost incurred. The system compares the reality against its initial prediction.
Using Bayesian updating, it adjusts the confidence weights ($\mu$ and $\sigma$ of delay estimates) and the company's internal SLA parameters ($\delta$) for future runs.
```math
P(Model | Actual\_Outcome) \propto P(Actual\_Outcome | Model) \cdot P(Model)
```
**Output:** Creates a continuous feedback loop where the optimizer’s accuracy structurally improves after every disruption event.

---

## 6. NLP Perception Engine
**File:** `backend/app/services/perception.py` 
**Purpose:** Translates unstructured external signals (news articles, port updates) into structured risk tensors.
**Algorithm Type:** Large Language Model (LLM) Extraction / Natural Language Processing

**How it works:**
The engine pipes live raw text (e.g., "Dockworkers at LA port threaten walkout next week") into an LLM (Gemini). It uses few-shot prompting and schema enforcement to extract exact entity values.
**Output JSON:**
*   `port_id`: "LA"
*   `event_type`: "Labor_Strike"
*   `severity_score`: $0.85$ (Calculated computationally through sentiment and historical magnitude)
*   `expected_delay`: 12 days

---

## 7. Generative Action Drafting
**File:** `backend/app/services/llm_generator.py`
**Purpose:** Eliminates execution latency by instantly generating the precise communications needed to execute the mathematical recommendation.
**Algorithm Type:** Generative AI (Google Gemini Prompt Engineering)

**How it works:**
Once the optimization engine settles on a strategy (e.g., "Split Strategy: 60% Reroute, 20% Air"), the Generative module injects these explicit quantitative variables into highly robust system prompts.
**Output:** Generates production-ready emails and memos (e.g., Supplier Rerouting Requests, Freight Forwarder Air-Booking Instructions) that exactly match the numerical outputs of the optimization engine.
