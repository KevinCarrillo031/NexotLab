"""Aporte 5: escenarios comparativos para decisiones de arquitectura y escala."""

from __future__ import annotations

from app.simulation.external import external_variables_report
from app.simulation.optimization import optimize_evaluation_flow
from app.simulation.scenarios import ScenarioParams, run_discrete_event
from app.simulation.validation import validate_model


def architecture_scenarios() -> list[dict]:
    variants = [
        ("monolito_sincrono", ScenarioParams(evaluators=8, review_hours_mean=5.5)),
        ("servicios_asincronos_revision", ScenarioParams(evaluators=12, review_hours_mean=4.0)),
        ("escala_horizontal_evaluadores", ScenarioParams(evaluators=20, review_hours_mean=4.2, users_per_day=6.5)),
    ]
    rows = []
    for name, params in variants:
        result = run_discrete_event(params)
        rows.append(
            {
                "architecture": name,
                "evaluators": params.evaluators,
                "users_per_day": params.users_per_day,
                "mean_wait_days": result["mean_wait_days"],
                "utilization": result["evaluator_utilization"],
                "throughput_per_week": result["throughput_per_week"],
                "capacity_ok": result["capacity_ok"],
            }
        )
    return rows


def strategic_recommendations() -> dict:
    validation = validate_model()
    optimization = optimize_evaluation_flow()
    external = external_variables_report()
    architectures = architecture_scenarios()
    best_arch = min(architectures, key=lambda a: (not a["capacity_ok"], a["mean_wait_days"]))

    recommendations = [
        {
            "priority": "alta",
            "decision": "Desacoplar la evaluación del request HTTP (cola asíncrona semanal).",
            "rationale": "La simulación de eventos discretos muestra que el cuello de botella es la revisión, no el registro.",
        },
        {
            "priority": "alta",
            "decision": f"Adoptar asignación de evaluadores '{optimization['recommended_policy']}'.",
            "rationale": optimization["conclusion"],
        },
        {
            "priority": "media",
            "decision": "Dimensionar evaluadores de forma elástica ante crecimiento de usuarios.",
            "rationale": f"El escenario más estresante es '{external['most_stressful']}'.",
        },
        {
            "priority": "media",
            "decision": f"Preferir arquitectura '{best_arch['architecture']}' para el crecimiento.",
            "rationale": (
                f"Espera media {best_arch['mean_wait_days']:.2f} días y utilización {best_arch['utilization']:.2f}."
            ),
        },
        {
            "priority": "baja",
            "decision": "Mantener umbrales 4.0 / 2.5 y ciclar scores semanales como señal de viabilidad.",
            "rationale": "Calibrados con el frontend y con confiabilidad de validación "
            f"{validation['reliability_after_adjustment']:.2f}.",
        },
    ]

    return {
        "aporte": 5,
        "asignatura": "Modelado y simulación",
        "entregable": "Informe de recomendaciones estratégicas para diseño y crecimiento",
        "architecture_comparison": architectures,
        "preferred_architecture": best_arch,
        "recommendations": recommendations,
        "scalability_guidance": {
            "when_users_double": "Duplicar capacidad de evaluadores o reducir horas medias de revisión un 30%.",
            "when_proposal_demand_spikes": "Activar triaje automático y tope de evaluaciones por propuesta.",
            "data_layer": "El esquema PostgreSQL ya separa users, proposals, evaluations y runs de simulación/minería para crecer sin rediseñar el modelo.",
        },
    }
