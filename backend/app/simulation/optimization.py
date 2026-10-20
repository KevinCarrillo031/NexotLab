"""Aporte 3: optimización de asignación de evaluadores, tiempos y flujos."""

from __future__ import annotations

import numpy as np
from scipy.optimize import linear_sum_assignment

from app.config import settings
from app.domain.enums import Sector


POLICIES = ("aleatoria", "round_robin", "especialidad", "asignacion_optima")


def _expertise_matrix(rng: np.random.Generator, n_eval: int, n_prop: int) -> np.ndarray:
    sectors = list(Sector)
    evaluator_sector = rng.integers(0, len(sectors), size=n_eval)
    proposal_sector = rng.integers(0, len(sectors), size=n_prop)
    matrix = np.ones((n_eval, n_prop))
    for i, es in enumerate(evaluator_sector):
        for j, ps in enumerate(proposal_sector):
            matrix[i, j] = 1.0 if es == ps else 1.55
    return matrix, evaluator_sector, proposal_sector


def _simulate_policy(policy: str, cost: np.ndarray, capacities: np.ndarray, review_hours: np.ndarray, rng: np.random.Generator) -> dict:
    n_eval, n_prop = cost.shape
    assignment = [[] for _ in range(n_eval)]
    remaining = capacities.copy()

    if policy == "aleatoria":
        order = rng.permutation(n_prop)
        for j in order:
            i = int(rng.integers(0, n_eval))
            assignment[i].append(j)
            remaining[i] -= 1
    elif policy == "round_robin":
        for j in range(n_prop):
            i = j % n_eval
            assignment[i].append(j)
            remaining[i] -= 1
    elif policy == "especialidad":
        for j in range(n_prop):
            ranked = np.argsort(cost[:, j])
            i = int(ranked[0])
            assignment[i].append(j)
            remaining[i] -= 1
    else:
        padded_eval = n_eval
        repeats = int(np.ceil(n_prop / n_eval))
        big_cost = np.vstack([cost + r * 0.02 for r in range(repeats)])
        row_ind, col_ind = linear_sum_assignment(big_cost[:, :n_prop])
        for r, c in zip(row_ind, col_ind):
            if c >= n_prop:
                continue
            i = int(r % n_eval)
            assignment[i].append(int(c))

    loads = np.array([len(a) for a in assignment], dtype=float)
    mismatch = []
    times = []
    for i, props in enumerate(assignment):
        for j in props:
            mismatch.append(float(cost[i, j]))
            times.append(float(review_hours[j] * cost[i, j]))
    mean_time = float(np.mean(times)) if times else 0.0
    max_load = float(loads.max()) if len(loads) else 0.0
    std_load = float(loads.std()) if len(loads) else 0.0
    fairness = 1.0 / (1.0 + std_load)
    efficiency = 1.0 / (mean_time + 0.15 * max_load + 0.2 * (np.mean(mismatch) if mismatch else 1))
    return {
        "policy": policy,
        "mean_review_hours": mean_time,
        "max_load": max_load,
        "load_std": std_load,
        "mean_mismatch_penalty": float(np.mean(mismatch) if mismatch else 0),
        "fairness_index": fairness,
        "efficiency_score": float(efficiency),
        "assigned_reviews": int(sum(len(a) for a in assignment)),
    }


def optimize_evaluation_flow(n_evaluators: int = 10, n_proposals: int = 28, seed: int | None = None) -> dict:
    rng = np.random.default_rng(seed if seed is not None else settings.random_seed)
    cost, _, _ = _expertise_matrix(rng, n_evaluators, n_proposals)
    capacities = np.full(n_evaluators, int(np.ceil(n_proposals / n_evaluators)) + 1)
    review_hours = np.clip(rng.normal(4.5, 1.1, size=n_proposals), 1.5, 9)

    results = [_simulate_policy(policy, cost, capacities, review_hours, rng) for policy in POLICIES]
    best = max(results, key=lambda r: r["efficiency_score"])

    return {
        "aporte": 3,
        "asignatura": "Modelado y simulación",
        "entregable": "Informe de optimización de evaluación y gestión de propuestas",
        "instance": {"evaluators": n_evaluators, "proposals": n_proposals},
        "policies": results,
        "recommended_policy": best["policy"],
        "recommended": best,
        "workflow": {
            "ciclo": "cierre semanal domingo 24:00 (igual que el frontend)",
            "criterios": ["viability", "innovation", "impact", "clarity"],
            "umbrales": {"alto": settings.high_score_threshold, "bajo": settings.low_score_threshold},
            "flujo_eficiente": [
                "Triaje automático por sector y categoría",
                "Asignación óptima (Hungarian) con tope de carga por evaluador",
                "Revisión en paralelo, no secuencial",
                "Reasignación si el tiempo de espera supera 48 h",
            ],
        },
        "conclusion": (
            f"La alternativa más eficiente es '{best['policy']}', con score de eficiencia "
            f"{best['efficiency_score']:.3f}, carga máxima {best['max_load']:.0f} y "
            f"{best['mean_review_hours']:.2f} horas medias de revisión."
        ),
    }
