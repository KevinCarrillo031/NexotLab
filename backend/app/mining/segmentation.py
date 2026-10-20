"""Aporte 3 (minería): segmentación de usuarios, propuestas y proyectos."""

from __future__ import annotations

import pandas as pd
from sklearn.cluster import KMeans
from sklearn.metrics import silhouette_score
from sklearn.preprocessing import StandardScaler

from app.config import settings
from app.mining.cleaning import default_prepared


PROFILE_LABELS = {
    0: "participante_observador",
    1: "innovador_activo",
    2: "evaluador_colaborativo",
    3: "autor_especializado",
}

PROPOSAL_LABELS = {
    0: "promesa_temprana",
    1: "alta_viabilidad",
    2: "requiere_mejora",
    3: "colaborativa_escalable",
}


def _kmeans_table(df: pd.DataFrame, cols: list[str], k: int, prefix: str) -> tuple[pd.DataFrame, dict]:
    work = df[cols].fillna(0).astype(float)
    scaled = StandardScaler().fit_transform(work)
    best_k = k
    best_score = -1.0
    best_model = None
    scores = {}
    for candidate in range(2, min(6, max(3, len(df) // 8))):
        model = KMeans(n_clusters=candidate, random_state=settings.random_seed, n_init=10)
        labels = model.fit_predict(scaled)
        sil = float(silhouette_score(scaled, labels)) if len(set(labels)) > 1 else -1
        scores[candidate] = sil
        if sil > best_score:
            best_score = sil
            best_k = candidate
            best_model = model
    if best_model is None:
        best_model = KMeans(n_clusters=k, random_state=settings.random_seed, n_init=10).fit(scaled)
        best_k = k
        best_score = 0.0
    labels = best_model.predict(scaled)
    out = df.copy()
    out[f"{prefix}_cluster"] = labels
    summary = (
        out.groupby(f"{prefix}_cluster")[cols]
        .mean(numeric_only=True)
        .round(3)
        .reset_index()
        .to_dict(orient="records")
    )
    return out, {"k": best_k, "silhouette": best_score, "scores_by_k": scores, "centroids": summary}


def segmented_database() -> dict:
    prepared = default_prepared()
    users = prepared["frames"]["users"].copy()
    proposals = prepared["frames"]["integrated"].copy()

    user_metrics = proposals.groupby("author_id").agg(
        authored_proposals=("id", "count"),
        mean_score=("current_score", "mean"),
        mean_team=("team_size", "mean"),
        viable_rate=("viable", "mean"),
    )
    users = users.merge(user_metrics, left_on="id", right_index=True, how="left")
    metric_cols = ["authored_proposals", "mean_score", "mean_team", "viable_rate"]
    users[metric_cols] = users[metric_cols].fillna(0)

    users_seg, user_meta = _kmeans_table(users, metric_cols, 3, "user")
    users_seg["user_profile_segment"] = users_seg["user_cluster"].map(
        lambda c: PROFILE_LABELS.get(int(c), f"segmento_{c}")
    )

    prop_cols = ["current_score", "evaluations_count", "team_size", "accepted_collaborators"]
    for col in prop_cols:
        if col not in proposals.columns:
            proposals[col] = 0
    props_seg, prop_meta = _kmeans_table(proposals, prop_cols, 3, "proposal")
    props_seg["proposal_type"] = props_seg["proposal_cluster"].map(
        lambda c: PROPOSAL_LABELS.get(int(c), f"tipo_{c}")
    )

    preview_users = users_seg[["id", "name", "profile_type", "sector", "user_cluster", "user_profile_segment"]].head(15)
    preview_props = props_seg[["id", "title", "sector", "current_score", "proposal_cluster", "proposal_type"]].head(15)

    return {
        "aporte": 3,
        "asignatura": "Minería de datos",
        "entregable": "Base de datos segmentada con perfiles de usuarios y tipos de propuestas",
        "user_segmentation": user_meta,
        "proposal_segmentation": prop_meta,
        "profile_definitions": PROFILE_LABELS,
        "proposal_type_definitions": PROPOSAL_LABELS,
        "counts": {
            "users": users_seg["user_profile_segment"].value_counts().to_dict(),
            "proposals": props_seg["proposal_type"].value_counts().to_dict(),
        },
        "preview_users": preview_users.to_dict(orient="records"),
        "preview_proposals": preview_props.to_dict(orient="records"),
        "ready_for_analysis": True,
    }
