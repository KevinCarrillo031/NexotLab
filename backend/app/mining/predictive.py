"""Aporte 2 (minería): modelos predictivos de viabilidad/aceptación."""

from __future__ import annotations

from pathlib import Path

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.linear_model import LinearRegression, LogisticRegression
from sklearn.metrics import accuracy_score, f1_score, r2_score
from sklearn.model_selection import train_test_split
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.tree import DecisionTreeClassifier

from app.config import settings
from app.mining.cleaning import default_prepared

ARTIFACTS = Path(__file__).resolve().parents[2] / "artifacts"
CATEGORICAL = ["category", "sector", "author_profile"]
NUMERIC = ["evaluations_count", "team_size", "accepted_collaborators", "description_length"]


def _xy(df: pd.DataFrame) -> tuple[pd.DataFrame, pd.Series, pd.Series]:
    work = df.copy()
    if "description_length" not in work.columns:
        work["description_length"] = work.get("description", pd.Series([""] * len(work))).astype(str).str.len()
    for col in NUMERIC:
        if col not in work.columns:
            work[col] = 0
    features = work[CATEGORICAL + NUMERIC].fillna(0)
    y_class = work["viable"].astype(int)
    y_reg = work["current_score"].astype(float)
    return features, y_class, y_reg


def _pre() -> ColumnTransformer:
    return ColumnTransformer(
        [
            ("cat", OneHotEncoder(handle_unknown="ignore"), CATEGORICAL),
            ("num", StandardScaler(), NUMERIC),
        ]
    )


def train_predictive_models(persist: bool = True) -> dict:
    df = default_prepared()["frames"]["integrated"]
    features, y_class, y_reg = _xy(df)
    x_train, x_test, y_train, y_test = train_test_split(
        features, y_class, test_size=0.25, random_state=settings.random_seed, stratify=y_class
    )

    tree = Pipeline(
        [
            ("pre", _pre()),
            ("model", DecisionTreeClassifier(max_depth=5, min_samples_leaf=8, random_state=settings.random_seed)),
        ]
    )
    logit = Pipeline(
        [
            ("pre", _pre()),
            ("model", LogisticRegression(max_iter=400)),
        ]
    )
    reg = Pipeline([("pre", _pre()), ("model", LinearRegression())])

    tree.fit(x_train, y_train)
    logit.fit(x_train, y_train)
    # usar el mismo split de features para regresión
    x_train_r, x_test_r, y_train_r, y_test_r = train_test_split(
        features, y_reg, test_size=0.25, random_state=settings.random_seed
    )
    reg.fit(x_train_r, y_train_r)

    tree_pred = tree.predict(x_test)
    logit_pred = logit.predict(x_test)
    score_pred = reg.predict(x_test_r)

    tree_acc = float(accuracy_score(y_test, tree_pred))
    logit_acc = float(accuracy_score(y_test, logit_pred))
    winner = "decision_tree" if tree_acc >= logit_acc else "logistic_regression"

    if persist:
        ARTIFACTS.mkdir(parents=True, exist_ok=True)
        joblib.dump({"tree": tree, "logit": logit, "reg": reg, "winner": winner}, ARTIFACTS / "viability_models.joblib")

    importances = []
    tree_model: DecisionTreeClassifier = tree.named_steps["model"]
    try:
        names = tree.named_steps["pre"].get_feature_names_out()
        importances = sorted(
            [{"feature": str(n), "importance": float(v)} for n, v in zip(names, tree_model.feature_importances_)],
            key=lambda x: x["importance"],
            reverse=True,
        )[:12]
    except Exception:
        importances = []

    sample = features.head(8).copy()
    sample["viable_pred"] = tree.predict(sample)
    sample["score_pred"] = np.round(reg.predict(sample), 2)

    return {
        "aporte": 2,
        "asignatura": "Minería de datos",
        "entregable": "Modelo predictivo de viabilidad / aceptación",
        "target": "viable = current_score >= 4.0; score continuo 1–5",
        "techniques": ["regresión lineal", "árbol de decisión", "regresión logística", "clustering auxiliar"],
        "metrics": {
            "decision_tree": {"accuracy": tree_acc, "f1": float(f1_score(y_test, tree_pred, zero_division=0))},
            "logistic_regression": {"accuracy": logit_acc, "f1": float(f1_score(y_test, logit_pred, zero_division=0))},
            "linear_regression_score": {"r2": float(r2_score(y_test_r, score_pred))},
        },
        "selected_classifier": winner,
        "feature_importances": importances,
        "sample_predictions": sample.to_dict(orient="records"),
        "artifact": str(ARTIFACTS / "viability_models.joblib") if persist else None,
    }


def predict_proposal(payload: dict) -> dict:
    path = ARTIFACTS / "viability_models.joblib"
    if not path.exists():
        train_predictive_models(persist=True)
    bundle = joblib.load(path)
    row = pd.DataFrame(
        [
            {
                "category": payload.get("category", "digital-transformation"),
                "sector": payload.get("sector", "agro"),
                "author_profile": payload.get("author_profile", "entrepreneur"),
                "evaluations_count": payload.get("evaluations_count", 10),
                "team_size": payload.get("team_size", 1),
                "accepted_collaborators": payload.get("accepted_collaborators", 0),
                "description_length": payload.get("description_length", 180),
            }
        ]
    )
    clf = bundle["tree"] if bundle["winner"] == "decision_tree" else bundle["logit"]
    viable = int(clf.predict(row)[0])
    score = float(np.clip(bundle["reg"].predict(row)[0], 1, 5))
    proba = None
    if hasattr(clf, "predict_proba"):
        proba = float(clf.predict_proba(row)[0][1])
    return {
        "viable": bool(viable),
        "acceptance_level": "alta" if score >= settings.high_score_threshold else "media" if score >= settings.low_score_threshold else "baja",
        "predicted_score": round(score, 2),
        "probability_viable": proba,
        "model": bundle["winner"],
    }
