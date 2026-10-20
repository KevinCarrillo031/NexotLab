"""NexotLab Backend – entrypoint principal de FastAPI."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any, Callable, cast

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import __version__
from app.api.router import api_router
from app.config import settings
from app.db.session import (
    database_status as _database_status,  # type: ignore[reportUnknownVariableType]
)


database_status: Callable[[], dict[str, Any]] = cast(
    Callable[[], dict[str, Any]], _database_status
)


@asynccontextmanager
async def lifespan(application: FastAPI):  # type: ignore[type-arg]
    """Arranque: verifica imports críticos y reporta estado."""
    import importlib

    importlib.import_module("app.mining")
    importlib.import_module("app.simulation")
    yield


app = FastAPI(
    title=settings.app_name,
    version=__version__,
    description=(
        "**NexotLab API** – backend académico con dos módulos principales:\n\n"
        "## Asignatura 1: Modelado y Simulación\n"
        "- **Aporte 1** `POST /api/v1/simulation/scenarios` — Simulación de escenarios (eventos discretos + Monte Carlo)\n"
        "- **Aporte 2** `GET /api/v1/simulation/validation` — Validación del modelo vs datos del proyecto\n"
        "- **Aporte 3** `GET /api/v1/simulation/optimization` — Optimización de asignación de evaluadores\n"
        "- **Aporte 4** `GET /api/v1/simulation/external-variables` — Variables externas y su impacto\n"
        "- **Aporte 5** `GET /api/v1/simulation/recommendations` — Recomendaciones estratégicas\n\n"
        "## Asignatura 2: Minería de Datos\n"
        "- **Aporte 1** `GET /api/v1/mining/patterns` — Patrones de comportamiento y tendencias\n"
        "- **Aporte 2** `POST /api/v1/mining/predictive/train` + `POST /mining/predictive/predict` — Modelos predictivos\n"
        "- **Aporte 3** `GET /api/v1/mining/segmentation` — Segmentación k-means\n"
        "- **Aporte 4** `GET /api/v1/mining/cleaning` — Limpieza, transformación e integración\n"
        "- **Aporte 5** `GET /api/v1/mining/association` — Reglas de asociación (Apriori)\n"
    ),
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api/v1")


@app.get("/", tags=["raíz"])
def root() -> dict[str, Any]:
    return {
        "app": settings.app_name,
        "version": __version__,
        "docs": "/docs",
        "redoc": "/redoc",
        "database": database_status(),
        "modules": {
            "modelado_y_simulacion": {
                "aporte_1_escenarios": "POST/GET /api/v1/simulation/scenarios",
                "aporte_2_validacion": "GET /api/v1/simulation/validation",
                "aporte_3_optimizacion": "GET /api/v1/simulation/optimization",
                "aporte_4_variables_externas": "GET /api/v1/simulation/external-variables",
                "aporte_5_recomendaciones": "GET /api/v1/simulation/recommendations",
            },
            "mineria_de_datos": {
                "aporte_1_patrones": "GET /api/v1/mining/patterns",
                "aporte_2_predictivo": "POST /api/v1/mining/predictive/train | POST /api/v1/mining/predictive/predict | GET /api/v1/mining/predictive/models",
                "aporte_3_segmentacion": "GET /api/v1/mining/segmentation",
                "aporte_4_limpieza": "GET /api/v1/mining/cleaning",
                "aporte_5_asociacion": "GET /api/v1/mining/association",
            },
            "plataforma": {
                "auth": "POST /api/v1/platform/auth/login",
                "usuarios": "GET/POST /api/v1/platform/users | PATCH /api/v1/platform/users/{id}/toggle-active",
                "propuestas": "GET/POST /api/v1/platform/proposals | PATCH/DELETE /api/v1/platform/proposals/{id}",
                "evaluaciones": "POST /api/v1/platform/evaluations | GET /api/v1/platform/proposals/{id}/evaluations",
                "comentarios": "POST /api/v1/platform/comments | GET /api/v1/platform/proposals/{id}/comments",
                "colaboradores": "POST /api/v1/platform/collaborators/apply | PATCH /api/v1/platform/collaborators/{pid}/{uid}/accept|reject",
                "notificaciones": "GET /api/v1/platform/notifications | PATCH /api/v1/platform/notifications/{id}/read | PATCH /api/v1/platform/notifications/read-all",
                "admin": "GET /api/v1/platform/admin/overview | GET/POST /api/v1/platform/admin/reports | PATCH /api/v1/platform/admin/reports/{id}/dismiss",
                "stats": "GET /api/v1/platform/stats",
            },
        },
    }
