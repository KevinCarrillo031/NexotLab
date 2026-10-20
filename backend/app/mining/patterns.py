"""Aporte 1 (minería): patrones de comportamiento y tendencias de innovación."""

from __future__ import annotations

import pandas as pd

from app.mining.cleaning import default_prepared


def behavior_patterns() -> dict:
    prepared = default_prepared()
    frames = prepared["frames"]
    users = frames["users"]
    proposals = frames["integrated"]
    comments = frames["comments"]
    evaluations = frames["evaluations"]

    by_profile = (
        proposals.groupby("author_profile")
        .agg(n=("id", "count"), mean_score=("current_score", "mean"), high_share=("viable", "mean"))
        .reset_index()
        .sort_values("mean_score", ascending=False)
    )
    by_sector = (
        proposals.groupby("sector")
        .agg(n=("id", "count"), mean_score=("current_score", "mean"), mean_team=("team_size", "mean"))
        .reset_index()
        .sort_values("mean_score", ascending=False)
    )
    by_category = (
        proposals.groupby("category")
        .agg(n=("id", "count"), mean_score=("current_score", "mean"), viable_rate=("viable", "mean"))
        .reset_index()
    )

    trend = None
    if "created_at" in proposals.columns:
        tmp = proposals.copy()
        tmp["month"] = pd.to_datetime(tmp["created_at"]).dt.to_period("M").astype(str)
        trend = (
            tmp.groupby("month")
            .agg(propuestas=("id", "count"), score_medio=("current_score", "mean"))
            .reset_index()
            .to_dict(orient="records")
        )

    comment_intensity = float(len(comments) / max(len(proposals), 1))
    eval_intensity = float(len(evaluations) / max(len(proposals), 1))

    patterns = [
        {
            "name": "Perfiles con mayor calidad percibida",
            "detail": by_profile.head(2)[["author_profile", "mean_score"]].to_dict(orient="records"),
        },
        {
            "name": "Sectores con más innovación (score medio)",
            "detail": by_sector.head(3)[["sector", "mean_score", "n"]].to_dict(orient="records"),
        },
        {
            "name": "Equipos y desempeño",
            "detail": {
                "correlacion_team_size_score": float(proposals["team_size"].corr(proposals["current_score"]))
                if len(proposals) > 2
                else None
            },
        },
        {
            "name": "Participación discursiva",
            "detail": {"comentarios_por_propuesta": comment_intensity, "evaluaciones_muestra_por_propuesta": eval_intensity},
        },
    ]

    serializable_profile = by_profile.round(3).to_dict(orient="records")
    serializable_sector = by_sector.round(3).to_dict(orient="records")
    serializable_category = by_category.round(3).to_dict(orient="records")

    return {
        "aporte": 1,
        "asignatura": "Minería de datos",
        "entregable": "Informe de patrones de comportamiento y tendencias de innovación",
        "patterns": patterns,
        "tables": {
            "by_profile": serializable_profile,
            "by_sector": serializable_sector,
            "by_category": serializable_category,
            "monthly_trend": trend,
        },
        "user_mix": users["profile_type"].value_counts(normalize=True).round(3).to_dict(),
        "innovation_reading": (
            "Las tendencias de innovación se leen como sectores y perfiles con score alto sostenido "
            "y mayor tasa de propuestas viables (umbral 4.0)."
        ),
    }
