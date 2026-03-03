from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import (
    seed, dashboard, disruptions, recommendations,
    simulation, learning, perception, risk_correlation, auth
)
from app.database import Base, engine
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from app.limiter import limiter

# Auto-create tables (safe for hackathon; production would use Alembic only)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="HarborGuard AI API",
    description=(
        "Industry-grade supply chain risk optimization — "
        "PERT/LHS Monte Carlo, TOPSIS+MILP optimizer, Sobol sensitivity, "
        "Thompson Sampling learning, K-Means disruption clustering"
    ),
    version="3.0.0"
)

# Setup Rate Limiting
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS config — allow all common local dev ports
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:5173",
        "http://localhost:5174",
        "http://127.0.0.1:5173",
        "http://127.0.0.1:5174",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(seed.router, prefix="/api/v1", tags=["Seed"])
app.include_router(dashboard.router, prefix="/api/v1", tags=["Dashboard"])
app.include_router(disruptions.router, prefix="/api/v1/disruptions", tags=["Disruptions"])
app.include_router(recommendations.router, prefix="/api/v1/recommendations", tags=["Recommendations"])
app.include_router(simulation.router, tags=["Simulation"])           # Monte Carlo + Sensitivity
app.include_router(learning.router, tags=["Learning"])               # Feedback loop
app.include_router(perception.router, tags=["Perception"])           # News detection
app.include_router(risk_correlation.router, prefix="/api/v1", tags=["Risk Correlation"])
app.include_router(auth.router, prefix="/api/v1/auth", tags=["Authentication"])

@app.get("/api/v1/health")
def health_check():
    return {"status": "ok", "version": "3.0.0"}


