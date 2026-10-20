from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Query
from pydantic import BaseModel, Field

from app.mining.association import association_rules
from app.mining.cleaning import prepare_analytical_database
from app.mining.insights import mining_insights
from app.mining.patterns import behavior_patterns
from app.mining.predictive import ARTIFACTS, predict_proposal, train_predictive_models
from app.mining.segmentation import segmented_database

router = APIRouter()


class PredictIn(BaseModel):
    category: str = "digital-transformation"
    sector: str = "agro"
    author_profile: str = "entrepreneur"
    evaluations_count: int = Field(default=12, ge=0)
    team_size: int = Field(default=1, ge=0)
    accepted_collaborators: int = Field(default=0, ge=0)
    description_length: int = Field(default=180, ge=10)


def _without_frames(payload: dict) -> dict:
    data = dict(payload)
    data.pop("frames", None)
    return data


# ---------------------------------------------------------------------------
# Aporte 1 – Patrones de comportamiento y tendencias de innovación
# ---------------------------------------------------------------------------
@router.get("/patterns", summary="Aporte 1: patrones de comportamiento y tendencias")
def mining_patterns() -> dict:
    return behavior_patterns()


# ---------------------------------------------------------------------------
# Aporte 2 – Modelos predictivos de viabilidad
# ---------------------------------------------------------------------------
@router.post("/predictive/train", summary="Aporte 2: entrenar modelos predictivos")
def mining_train() -> dict:
    return train_predictive_models(persist=True)


@router.post("/predictive/predict", summary="Aporte 2: predecir viabilidad de propuesta")
def mining_predict(body: PredictIn) -> dict:
    return predict_proposal(body.model_dump())


@router.get("/predictive/models", summary="Aporte 2: inspeccionar modelos entrenados")
def mining_models_info() -> dict:
    model_path = ARTIFACTS / "viability_models.joblib"
    if not model_path.exists():
        return {
            "trained": False,
            "message": "Modelos no entrenados aún. Llame POST /mining/predictive/train primero.",
            "artifact_path": str(model_path),
        }
    import joblib

    bundle = joblib.load(model_path)
    return {
        "trained": True,
        "artifact_path": str(model_path),
        "selected_classifier": bundle.get("winner"),
        "models_available": [k for k in bundle.keys() if k != "winner"],
        "note": "Llame POST /mining/predictive/predict con un payload para inferir viabilidad.",
    }


# ---------------------------------------------------------------------------
# Aporte 3 – Segmentación de usuarios y propuestas
# ---------------------------------------------------------------------------
@router.get("/segmentation", summary="Aporte 3: segmentación k-means de usuarios y propuestas")
def mining_segmentation() -> dict:
    return segmented_database()


# ---------------------------------------------------------------------------
# Aporte 4 – Limpieza, transformación e integración
# ---------------------------------------------------------------------------
@router.get("/cleaning", summary="Aporte 4: limpieza, transformación e integración de datos")
def mining_cleaning() -> dict:
    return _without_frames(prepare_analytical_database())


# ---------------------------------------------------------------------------
# Aporte 5 – Reglas de asociación y repositorio de procedimientos
# ---------------------------------------------------------------------------
@router.get("/association", summary="Aporte 5: reglas de asociación Apriori")
def mining_association(
    min_support: float = Query(default=0.08, ge=0.01, le=0.5),
    min_confidence: float = Query(default=0.45, ge=0.1, le=1.0),
) -> dict:
    return association_rules(min_support=min_support, min_confidence=min_confidence)


# ---------------------------------------------------------------------------
# Insights consolidados – Panel admin (puntos 2-9 del docente)
# ---------------------------------------------------------------------------
@router.get("/insights", summary="Insights consolidados para el panel de administración")
def mining_insights_endpoint() -> dict:
    return mining_insights()
