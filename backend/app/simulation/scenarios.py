"""Aporte 1: simulación de escenarios de participación (eventos discretos + Monte Carlo)."""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np

from app.config import settings
from app.domain.enums import ProfileType


@dataclass
class ScenarioParams:
    horizon_days: int = 90
    users_per_day: float = 3.2
    proposals_per_active_user_year: float = 1.4
    evaluations_per_proposal: float = 18.0
    evaluators: int = 12
    review_hours_mean: float = 4.5
    review_hours_sd: float = 1.4
    work_hours_per_day: float = 6.0
    monte_carlo_runs: int = 250
    seed: int = settings.random_seed


PROFILE_MIX = {
    ProfileType.ENTREPRENEUR: 0.32,
    ProfileType.COMPANY: 0.18,
    ProfileType.RESEARCHER: 0.28,
    ProfileType.CITIZEN: 0.22,
}


def _poisson_arrivals(rng: np.random.Generator, rate: float, horizon: int) -> np.ndarray:
    counts = rng.poisson(rate, size=horizon)
    times = []
    for day, n in enumerate(counts):
        if n == 0:
            continue
        offsets = rng.random(n)
        times.extend(day + offsets)
    return np.sort(np.array(times, dtype=float))


def run_discrete_event(params: ScenarioParams) -> dict:
    rng = np.random.default_rng(params.seed)
    register_times = _poisson_arrivals(rng, params.users_per_day, params.horizon_days)
    proposal_rate = (params.users_per_day * params.proposals_per_active_user_year) / 365
    proposal_times = _poisson_arrivals(rng, max(proposal_rate, 0.05), params.horizon_days)

    n_eval = int(round(len(proposal_times) * params.evaluations_per_proposal))
    if len(proposal_times) == 0:
        eval_times = np.array([])
    else:
        eval_times = np.sort(
            proposal_times[rng.integers(0, len(proposal_times), size=n_eval)]
            + rng.exponential(0.6, size=n_eval)
        )
        eval_times = eval_times[eval_times <= params.horizon_days]

    service = np.clip(
        rng.normal(params.review_hours_mean, params.review_hours_sd, size=len(eval_times)),
        0.5,
        None,
    ) / params.work_hours_per_day

    free_at = np.zeros(params.evaluators)
    waits: list[float] = []
    busy_time = 0.0
    queued = 0
    queue_peak = 0

    for arrival, duration in zip(eval_times, service):
        queued = int(np.sum(free_at > arrival))
        queue_peak = max(queue_peak, max(0, queued - params.evaluators + 1))
        server = int(np.argmin(free_at))
        start = max(arrival, free_at[server])
        wait = start - arrival
        end = start + duration
        free_at[server] = end
        waits.append(wait)
        busy_time += duration

    utilization = busy_time / (params.evaluators * params.horizon_days) if params.horizon_days else 0
    profiles = rng.choice(list(PROFILE_MIX.keys()), size=len(register_times), p=list(PROFILE_MIX.values()))
    profile_counts = {str(p): int(np.sum(profiles == p)) for p in PROFILE_MIX}

    return {
        "method": "simulación de eventos discretos (llegadas Poisson + múltiples servidores)",
        "horizon_days": params.horizon_days,
        "registered_users": int(len(register_times)),
        "published_proposals": int(len(proposal_times)),
        "evaluations_processed": int(len(eval_times)),
        "users_by_profile": profile_counts,
        "mean_wait_days": float(np.mean(waits)) if waits else 0.0,
        "p95_wait_days": float(np.quantile(waits, 0.95)) if waits else 0.0,
        "throughput_per_week": float(len(waits) / (params.horizon_days / 7)) if params.horizon_days else 0.0,
        "evaluator_utilization": float(min(utilization, 1.5)),
        "queue_peak": int(queue_peak),
        "capacity_ok": bool((np.mean(waits) if waits else 0) < 2.0),
    }


def run_monte_carlo(params: ScenarioParams) -> dict:
    rng = np.random.default_rng(params.seed + 7)
    proposal_n = max(40, int(params.users_per_day * params.horizon_days * 0.35))
    scores = []
    accepted = []
    review_loads = []
    for _ in range(params.monte_carlo_runs):
        quality = rng.beta(4.2, 2.4, size=proposal_n) * 4 + 1
        noise = rng.normal(0, 0.25, size=proposal_n)
        simulated = np.clip(quality + noise, 1, 5)
        scores.append(simulated.mean())
        accepted.append((simulated >= settings.high_score_threshold).mean())
        evals = rng.poisson(params.evaluations_per_proposal, size=proposal_n).sum()
        review_loads.append(evals / max(params.evaluators, 1))

    scores_a = np.array(scores)
    accepted_a = np.array(accepted)
    load_a = np.array(review_loads)
    return {
        "method": "Monte Carlo",
        "runs": params.monte_carlo_runs,
        "proposals_per_run": proposal_n,
        "mean_score": {"mean": float(scores_a.mean()), "std": float(scores_a.std()), "ci95": [float(np.quantile(scores_a, 0.025)), float(np.quantile(scores_a, 0.975))]},
        "high_acceptance_rate": {"mean": float(accepted_a.mean()), "std": float(accepted_a.std()), "ci95": [float(np.quantile(accepted_a, 0.025)), float(np.quantile(accepted_a, 0.975))]},
        "reviews_per_evaluator": {"mean": float(load_a.mean()), "p95": float(np.quantile(load_a, 0.95))},
    }


def functional_simulation_model(overrides: dict | None = None) -> dict:
    data = asdict(ScenarioParams())
    if overrides:
        data.update({k: v for k, v in overrides.items() if k in data})
    params = ScenarioParams(**data)
    discrete = run_discrete_event(params)
    monte = run_monte_carlo(params)
    return {
        "aporte": 1,
        "asignatura": "Modelado y simulación",
        "entregable": "Modelo funcional de simulación de escenarios de uso de NexotLab",
        "parameters": data,
        "discrete_event": discrete,
        "monte_carlo": monte,
        "interpretation": (
            "El modelo representa registro, publicación y evaluación. "
            "Si la utilización de evaluadores supera ~0.85 o la espera media supera 2 días, "
            "el sistema se satura ante el volumen simulado de propuestas."
        ),
    }
