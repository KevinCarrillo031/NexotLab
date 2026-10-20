"""Aporte 4: simulación de variables externas y su impacto."""

from __future__ import annotations

from copy import deepcopy

from app.simulation.scenarios import ScenarioParams, run_discrete_event


def _impact(baseline: dict, scenario: dict) -> dict:
    def delta(key: str) -> dict:
        b, s = baseline[key], scenario[key]
        return {
            "baseline": b,
            "scenario": s,
            "abs_change": s - b,
            "pct_change": (s - b) / b if b else None,
        }

    return {
        "mean_wait_days": delta("mean_wait_days"),
        "throughput_per_week": delta("throughput_per_week"),
        "evaluator_utilization": delta("evaluator_utilization"),
        "published_proposals": delta("published_proposals"),
        "registered_users": delta("registered_users"),
        "queue_peak": delta("queue_peak"),
    }


def external_variables_report(seed: int | None = None) -> dict:
    base = ScenarioParams()
    if seed is not None:
        base.seed = seed
    baseline = run_discrete_event(base)

    scenarios = {
        "crecimiento_usuarios_exponencial": deepcopy(base),
        "pico_demanda_propuestas": deepcopy(base),
        "escasez_evaluadores": deepcopy(base),
        "doble_presion": deepcopy(base),
    }
    scenarios["crecimiento_usuarios_exponencial"].users_per_day *= 2.2
    scenarios["pico_demanda_propuestas"].proposals_per_active_user_year *= 2.5
    scenarios["escasez_evaluadores"].evaluators = max(3, base.evaluators // 2)
    scenarios["doble_presion"].users_per_day *= 1.8
    scenarios["doble_presion"].evaluators = max(4, int(base.evaluators * 0.7))

    rows = []
    for name, params in scenarios.items():
        result = run_discrete_event(params)
        rows.append(
            {
                "name": name,
                "parameters": {
                    "users_per_day": params.users_per_day,
                    "proposals_per_active_user_year": params.proposals_per_active_user_year,
                    "evaluators": params.evaluators,
                },
                "kpis": {
                    "mean_wait_days": result["mean_wait_days"],
                    "throughput_per_week": result["throughput_per_week"],
                    "evaluator_utilization": result["evaluator_utilization"],
                    "queue_peak": result["queue_peak"],
                    "capacity_ok": result["capacity_ok"],
                },
                "impact_vs_baseline": _impact(baseline, result),
            }
        )

    worst = max(rows, key=lambda r: r["kpis"]["mean_wait_days"])
    return {
        "aporte": 4,
        "asignatura": "Modelado y simulación",
        "entregable": "Informe de simulación de variables externas",
        "baseline": {
            "users_per_day": base.users_per_day,
            "evaluators": base.evaluators,
            "kpis": {
                "mean_wait_days": baseline["mean_wait_days"],
                "throughput_per_week": baseline["throughput_per_week"],
                "evaluator_utilization": baseline["evaluator_utilization"],
                "queue_peak": baseline["queue_peak"],
            },
        },
        "scenarios": rows,
        "most_stressful": worst["name"],
        "effect_on_collaboration": (
            "Cuando crece la demanda o cae la disponibilidad de evaluadores, "
            "aumenta la cola de revisión y se retrasa la aceptación de colaboradores, "
            "reduciendo la capacidad de gestión y de trabajo en equipo de NexotLab."
        ),
    }
