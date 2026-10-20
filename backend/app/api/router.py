"""Router raíz de la API v1."""

from fastapi import APIRouter

from app.api.routes import docs, health, mining, platform, simulation

api_router = APIRouter()

api_router.include_router(health.router, tags=["salud"])
api_router.include_router(
    platform.router,
    prefix="/platform",
    tags=["plataforma"],
)
api_router.include_router(
    simulation.router,
    prefix="/simulation",
    tags=["modelado-y-simulacion"],
)
api_router.include_router(
    mining.router,
    prefix="/mining",
    tags=["mineria-de-datos"],
)
api_router.include_router(
    docs.router,
    prefix="/docs",
    tags=["entregables-academicos"],
)
