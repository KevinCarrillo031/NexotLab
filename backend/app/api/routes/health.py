"""Health check y diagnóstico del sistema."""

from fastapi import APIRouter

from app import __version__
from app.config import settings
from app.db.session import database_status
from app.domain.enums import ProfileType, ProposalCategory, ProposalStatus, Sector

router = APIRouter()


@router.get("/health", summary="Estado del sistema y diagnóstico")
def health() -> dict:
    db = database_status()
    return {
        "status": "ok",
        "app": settings.app_name,
        "version": __version__,
        "env": settings.app_env,
        "database": db,
        "thresholds": {
            "high_score": settings.high_score_threshold,
            "low_score": settings.low_score_threshold,
        },
        "enums": {
            "profile_types": [e.value for e in ProfileType],
            "sectors": [e.value for e in Sector],
            "categories": [e.value for e in ProposalCategory],
            "proposal_statuses": [e.value for e in ProposalStatus],
        },
    }
