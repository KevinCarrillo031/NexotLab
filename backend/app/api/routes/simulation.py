"""Rutas de Modelado y Simulación – los 5 aportes de la asignatura."""

from __future__ import annotations

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.simulation.external import external_variables_report
from app.simulation.optimization import optimize_evaluation_flow
from app.simulation.recommendations import strategic_recommendations
from app.simulation.scenarios import functional_simulation_model
from app.simulation.validation import validate_model

router = APIRouter()


class ScenarioOverrides(BaseModel):
    horizon_days: int | None = Field(default=None, ge=7, le=365)
    users_per_day: float | None = Field(default=None, ge=0.1)
    evaluators: int | None = Field(default=None, ge=1, le=80)
    monte_carlo_runs: int | None = Field(default=None, ge=30, le=2000)
    proposals_per_active_user_year: float | None = Field(default=None, ge=0.1)
    review_hours_mean: float | None = Field(default=None, ge=0.5, le=24.0)


# ---------------------------------------------------------------------------
# Aporte 1 – Modelo funcional de simulación (eventos discretos + Monte Carlo)
# ---------------------------------------------------------------------------
@router.post(
    "/scenarios",
    summary="Aporte 1: simulación de escenarios (eventos discretos + Monte Carlo)",
)
def simulation_scenarios(body: ScenarioOverrides | None = None) -> dict:
    overrides = {k: v for k, v in (body.model_dump() if body else {}).items() if v is not None}
    return functional_simulation_model(overrides)


@router.get(
    "/scenarios",
    summary="Aporte 1: simulación con parámetros por defecto (GET conveniente)",
)
def simulation_scenarios_default() -> dict:
    return functional_simulation_model()


# ---------------------------------------------------------------------------
# Aporte 2 – Validación del modelo
# ---------------------------------------------------------------------------
@router.get(
    "/validation",
    summary="Aporte 2: validación del modelo de simulación frente a datos del proyecto",
)
def simulation_validation() -> dict:
    return validate_model()


# ---------------------------------------------------------------------------
# Aporte 3 – Optimización de asignación de evaluadores y flujos
# ---------------------------------------------------------------------------
@router.get(
    "/optimization",
    summary="Aporte 3: optimización de asignación de evaluadores y flujos de trabajo",
)
def simulation_optimization(
    n_evaluators: int = Query(default=10, ge=2, le=80),
    n_proposals: int = Query(default=28, ge=4, le=500),
) -> dict:
    return optimize_evaluation_flow(n_evaluators=n_evaluators, n_proposals=n_proposals)


# ---------------------------------------------------------------------------
# Aporte 4 – Variables externas y su impacto
# ---------------------------------------------------------------------------
@router.get(
    "/external-variables",
    summary="Aporte 4: simulación de variables externas (crecimiento, demanda, disponibilidad)",
)
def simulation_external() -> dict:
    return external_variables_report()


# ---------------------------------------------------------------------------
# Aporte 5 – Recomendaciones estratégicas
# ---------------------------------------------------------------------------
@router.get(
    "/recommendations",
    summary="Aporte 5: recomendaciones estratégicas para arquitectura y escalabilidad",
)
def simulation_recommendations() -> dict:
    return strategic_recommendations()
