"""Aporte 4 (minería): limpieza, transformación e integración."""

from __future__ import annotations

import numpy as np
import pandas as pd

from app.config import settings
from app.data.catalog import SYNTHETIC, build_synthetic_frames


def _inject_quality_issues(frames: dict[str, pd.DataFrame], seed: int) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed)
    dirty = {name: df.copy() for name, df in frames.items()}
    users = dirty["users"]
    proposals = dirty["proposals"]

    drop_idx = rng.choice(users.index, size=max(1, len(users) // 40), replace=False)
    users.loc[drop_idx, "sector"] = None
    dup = users.iloc[[0]].copy()
    dirty["users"] = pd.concat([users, dup], ignore_index=True)

    outlier_idx = rng.choice(proposals.index, size=max(1, len(proposals) // 30), replace=False)
    proposals.loc[outlier_idx, "current_score"] = rng.choice([0.2, 7.4, -1.0], size=len(outlier_idx))
    proposals.loc[rng.choice(proposals.index, size=3, replace=False), "title"] = "  "
    dirty["proposals"] = proposals
    return dirty


def prepare_analytical_database(seed: int | None = None) -> dict:
    seed = seed if seed is not None else settings.random_seed
    clean_source = build_synthetic_frames(seed=seed)
    dirty = _inject_quality_issues(clean_source, seed)

    report = {"duplicates_removed": 0, "nulls_imputed": {}, "outliers_capped": 0, "invalid_titles_fixed": 0}

    users = dirty["users"].drop_duplicates(subset=["email"], keep="first").copy()
    report["duplicates_removed"] = int(len(dirty["users"]) - len(users))
    null_sector = int(users["sector"].isna().sum())
    users["sector"] = users["sector"].fillna("government")
    report["nulls_imputed"]["users.sector"] = null_sector

    proposals = dirty["proposals"].copy()
    before = proposals["current_score"].copy()
    proposals["current_score"] = proposals["current_score"].clip(1.0, 5.0)
    report["outliers_capped"] = int((before != proposals["current_score"]).sum())
    bad_titles = proposals["title"].str.strip().eq("")
    report["invalid_titles_fixed"] = int(bad_titles.sum())
    proposals.loc[bad_titles, "title"] = "Propuesta sin título normalizado"

    users["profile_type"] = users["profile_type"].str.strip().str.lower()
    proposals["category"] = proposals["category"].str.strip()
    proposals["sector"] = proposals["sector"].str.strip()

    merged = proposals.merge(
        users.rename(columns={"id": "author_id", "profile_type": "author_profile", "sector": "author_sector", "name": "author_name"}),
        on="author_id",
        how="left",
        suffixes=("", "_user"),
    )
    collab = dirty["collaborators"].copy()
    team = collab.groupby("proposal_id").agg(
        team_size=("user_id", "count"),
        accepted_collaborators=("status", lambda s: int((s == "accepted").sum())),
    )
    integrated = merged.merge(team, left_on="id", right_index=True, how="left", suffixes=("", "_agg"))
    if "team_size_agg" in integrated.columns:
        integrated["team_size"] = integrated["team_size_agg"].fillna(integrated.get("team_size", 0))
        integrated.drop(columns=["team_size_agg"], inplace=True, errors="ignore")
    integrated["team_size"] = integrated["team_size"].fillna(0).astype(int)
    integrated["accepted_collaborators"] = integrated.get("accepted_collaborators", 0)
    if "accepted_collaborators_agg" in integrated.columns:
        integrated["accepted_collaborators"] = integrated["accepted_collaborators_agg"].fillna(0)
        integrated.drop(columns=["accepted_collaborators_agg"], inplace=True, errors="ignore")
    integrated["accepted_collaborators"] = integrated["accepted_collaborators"].fillna(0).astype(int)
    integrated["viable"] = (integrated["current_score"] >= settings.high_score_threshold).astype(int)
    integrated["acceptance_level"] = pd.cut(
        integrated["current_score"],
        bins=[0, settings.low_score_threshold, settings.high_score_threshold, 5.01],
        labels=["baja", "media", "alta"],
        include_lowest=True,
    ).astype(str)

    preview_cols = [
        "id", "title", "category", "sector", "author_profile", "current_score",
        "evaluations_count", "team_size", "viable", "acceptance_level",
    ]
    available = [c for c in preview_cols if c in integrated.columns]

    return {
        "aporte": 4,
        "asignatura": "Minería de datos",
        "entregable": "Base de datos preparada, limpia e integrada",
        "cleaning_report": report,
        "row_counts": {
            "users": int(len(users)),
            "proposals": int(len(proposals)),
            "collaborators": int(len(collab)),
            "evaluations": int(len(dirty["evaluations"])),
            "comments": int(len(dirty["comments"])),
            "integrated_fact_table": int(len(integrated)),
        },
        "preview": integrated[available].head(12).to_dict(orient="records"),
        "ready_for_mining": True,
        "frames": {
            "users": users,
            "proposals": proposals,
            "collaborators": collab,
            "evaluations": dirty["evaluations"],
            "comments": dirty["comments"],
            "integrated": integrated,
        },
    }


def default_prepared() -> dict:
    return prepare_analytical_database()
