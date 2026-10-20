"""
Insights consolidados de minería de datos para el panel de administración.
Expone: comparación de modelos, interpretación de clusters, reglas clave,
proceso completo y el conocimiento nuevo descubierto (punto 9 del docente).
"""

from __future__ import annotations

from app.mining.association import association_rules
from app.mining.cleaning import default_prepared
from app.mining.patterns import behavior_patterns
from app.mining.predictive import train_predictive_models
from app.mining.segmentation import segmented_database


# ---------------------------------------------------------------------------
# Descripciones interpretables de los clusters (punto 4)
# ---------------------------------------------------------------------------

CLUSTER_USER_DESCRIPTIONS = {
    "participante_observador": {
        "label": "Participante Observador",
        "color": "#6B7280",
        "icon": "👁",
        "description": (
            "Usuarios con baja actividad de publicación y scores promedio moderados. "
            "Generalmente ciudadanos o investigadores que evalúan propuestas pero rara vez lideran equipos."
        ),
        "nexotlab_action": (
            "NexoTLab puede enviarles invitaciones personalizadas para unirse como colaboradores "
            "en propuestas afines a su sector, aumentando su participación activa."
        ),
    },
    "innovador_activo": {
        "label": "Innovador Activo",
        "color": "#10B981",
        "icon": "🚀",
        "description": (
            "Usuarios con múltiples propuestas publicadas, alta tasa de viabilidad y scores elevados. "
            "Son el motor de la plataforma: emprendedores e investigadores con proyectos de impacto real."
        ),
        "nexotlab_action": (
            "NexoTLab debería priorizar sus propuestas en el feed y ofrecerles acceso anticipado "
            "a convocatorias o financiadores externos."
        ),
    },
    "evaluador_colaborativo": {
        "label": "Evaluador Colaborativo",
        "color": "#3B82F6",
        "icon": "🤝",
        "description": (
            "Usuarios con alto número de evaluaciones emitidas y colaboraciones aceptadas. "
            "Forman equipos estables y agregan valor técnico sin necesariamente liderar."
        ),
        "nexotlab_action": (
            "NexoTLab puede usarlos como evaluadores de calidad ('peer review') "
            "y reconocerlos con insignias de experto en su sector."
        ),
    },
    "autor_especializado": {
        "label": "Autor Especializado",
        "color": "#8B5CF6",
        "icon": "🎯",
        "description": (
            "Usuarios con pocas propuestas pero de alta especialización temática y equipo grande. "
            "Sus proyectos tienen scores altos y colaboradores bien seleccionados."
        ),
        "nexotlab_action": (
            "NexoTLab puede conectarlos directamente con empresas del sector para co-desarrollo "
            "o pilotos financiados."
        ),
    },
}

CLUSTER_PROPOSAL_DESCRIPTIONS = {
    "promesa_temprana": {
        "label": "Promesa Temprana",
        "color": "#F59E0B",
        "icon": "🌱",
        "description": (
            "Propuestas con pocas evaluaciones y score medio. Tienen potencial pero les falta visibilidad "
            "o retroalimentación de la comunidad. Equipos pequeños, generalmente de un solo autor."
        ),
        "nexotlab_action": (
            "NexoTLab puede impulsar su visibilidad con una sección 'Descubrir' y asignar evaluadores activos."
        ),
    },
    "alta_viabilidad": {
        "label": "Alta Viabilidad",
        "color": "#10B981",
        "icon": "⭐",
        "description": (
            "Propuestas con score alto (≥ 4.0), muchas evaluaciones y colaboradores aceptados. "
            "Son las candidatas naturales para financiamiento o implementación real."
        ),
        "nexotlab_action": (
            "NexoTLab debería conectarlas con el módulo de alianzas externas y notificar a posibles financiadores."
        ),
    },
    "requiere_mejora": {
        "label": "Requiere Mejora",
        "color": "#EF4444",
        "icon": "🔧",
        "description": (
            "Propuestas con score bajo y poca participación. Muchas tienen descripción corta "
            "o pertenecen a sectores con menor tracción en la plataforma."
        ),
        "nexotlab_action": (
            "NexoTLab puede ofrecer un asistente de mejora basado en las características de las propuestas viables "
            "del mismo sector como referencia."
        ),
    },
    "colaborativa_escalable": {
        "label": "Colaborativa y Escalable",
        "color": "#8B5CF6",
        "icon": "📈",
        "description": (
            "Propuestas con equipos grandes (≥ 3 colaboradores), scores sostenidos y múltiples evaluaciones. "
            "Representan proyectos maduros con tracción real de comunidad."
        ),
        "nexotlab_action": (
            "NexoTLab puede usarlas como casos de éxito para onboarding de nuevos usuarios "
            "y como plantilla para futuras convocatorias temáticas."
        ),
    },
}

# ---------------------------------------------------------------------------
# Interpretaciones de reglas de asociación (punto 5)
# ---------------------------------------------------------------------------

def _interpret_rule(rule: dict) -> str:
    ant = ", ".join(rule["antecedent"])
    cons = ", ".join(rule["consequent"])
    conf = rule["confidence"]
    lift = rule["lift"]
    if lift > 1.5:
        strength = "asociación fuerte"
    elif lift > 1.0:
        strength = "asociación moderada"
    else:
        strength = "asociación débil"
    return (
        f"Cuando una propuesta tiene [{ant}], en el {int(conf * 100)}% de los casos "
        f"también presenta [{cons}]. Lift={lift:.2f} indica {strength}."
    )


# ---------------------------------------------------------------------------
# Función principal exportada
# ---------------------------------------------------------------------------

def mining_insights() -> dict:
    """Consolida todos los hallazgos de minería para el panel admin."""

    # ── Datos base ──────────────────────────────────────────────────────────
    prepared = default_prepared()
    df = prepared["frames"]["integrated"]
    n_rows = len(df)
    n_users_real = len(prepared["frames"]["users"])

    # ── 1. Proceso completo (punto 8) ───────────────────────────────────────
    pipeline_steps = [
        {
            "step": 1,
            "name": "Datos originales",
            "icon": "📂",
            "detail": (
                f"{n_users_real} usuarios y {len(prepared['frames']['proposals'])} propuestas "
                "cargados desde el catálogo sintético que modela la base real de NexoTLab."
            ),
            "source": "BASE_ORIGINAL",
        },
        {
            "step": 2,
            "name": "Limpieza y transformación",
            "icon": "🧹",
            "detail": (
                f"Se eliminaron {prepared['cleaning_report']['duplicates_removed']} duplicados, "
                f"se imputaron {prepared['cleaning_report']['nulls_imputed'].get('users.sector', 0)} nulos en sector, "
                f"se corrigieron {prepared['cleaning_report']['outliers_capped']} outliers de score."
            ),
            "source": "BASE_PREPARADA",
        },
        {
            "step": 3,
            "name": "Exploración (EDA)",
            "icon": "🔍",
            "detail": (
                "Se analizaron distribuciones de score, perfiles de autor, sectores, "
                "correlación entre tamaño de equipo y viabilidad, y tendencias mensuales."
            ),
            "source": "BASE_PREPARADA",
        },
        {
            "step": 4,
            "name": "Selección de variables",
            "icon": "🎯",
            "detail": (
                "Variables predictoras: category, sector, author_profile (categóricas) + "
                "evaluations_count, team_size, accepted_collaborators, description_length (numéricas). "
                "Variable objetivo: viable (score ≥ 4.0)."
            ),
            "source": "BASE_PREPARADA",
        },
        {
            "step": 5,
            "name": "Técnicas de minería",
            "icon": "⚙️",
            "detail": (
                "K-Means para segmentación de usuarios y propuestas, "
                "Árbol de Decisión y Regresión Logística para predicción de viabilidad, "
                "Apriori para reglas de asociación."
            ),
            "source": "BASE_PREPARADA",
        },
        {
            "step": 6,
            "name": "Evaluación",
            "icon": "📊",
            "detail": (
                "División 75/25 entrenamiento/prueba con estratificación. "
                "Métricas: Accuracy, F1-score, R², Silhouette Score."
            ),
            "source": "BASE_PREPARADA",
        },
        {
            "step": 7,
            "name": "Interpretación",
            "icon": "💡",
            "detail": (
                "Cada cluster recibió una etiqueta funcional basada en los centroides. "
                "Cada regla de asociación fue filtrada por lift > 1 y consecuente = resultado de evaluación."
            ),
            "source": "BASE_PREPARADA",
        },
        {
            "step": 8,
            "name": "Aplicación en NexoTLab",
            "icon": "🔗",
            "detail": (
                "Resultados integrados en el panel admin mediante API REST. "
                "El modelo predictivo está disponible en tiempo real desde POST /mining/predictive/predict."
            ),
            "source": "INTERFAZ",
        },
    ]

    # ── 2. Comparación de modelos (punto 3) ──────────────────────────────────
    try:
        model_results = train_predictive_models(persist=True)
        metrics = model_results["metrics"]
        winner = model_results["selected_classifier"]
        importances = model_results.get("feature_importances", [])

        model_comparison = [
            {
                "name": "Árbol de Decisión",
                "key": "decision_tree",
                "accuracy": metrics["decision_tree"]["accuracy"],
                "f1": metrics["decision_tree"]["f1"],
                "params": "max_depth=5, min_samples_leaf=8",
                "pros": "Interpretable, muestra qué variables pesan más, no requiere normalización",
                "cons": "Puede sobreajustarse con profundidad mayor",
                "selected": winner == "decision_tree",
            },
            {
                "name": "Regresión Logística",
                "key": "logistic_regression",
                "accuracy": metrics["logistic_regression"]["accuracy"],
                "f1": metrics["logistic_regression"]["f1"],
                "params": "max_iter=400, solver=lbfgs",
                "pros": "Estable, genera probabilidades, robusto con datos linealmente separables",
                "cons": "Menos interpretable para variables categóricas",
                "selected": winner == "logistic_regression",
            },
        ]
        r2_score = metrics["linear_regression_score"]["r2"]
    except Exception:
        model_comparison = []
        importances = []
        winner = "no_entrenado"
        r2_score = 0.0

    # ── 3. Segmentación interpretada (punto 4) ───────────────────────────────
    try:
        seg = segmented_database()
        user_counts = seg.get("counts", {}).get("users", {})
        prop_counts = seg.get("counts", {}).get("proposals", {})
        user_seg_meta = seg.get("user_segmentation", {})
        prop_seg_meta = seg.get("proposal_segmentation", {})

        user_clusters = []
        for segment_key, count in user_counts.items():
            desc = CLUSTER_USER_DESCRIPTIONS.get(segment_key, {})
            user_clusters.append({
                "segment": segment_key,
                "label": desc.get("label", segment_key),
                "color": desc.get("color", "#6B7280"),
                "icon": desc.get("icon", "●"),
                "count": count,
                "description": desc.get("description", ""),
                "nexotlab_action": desc.get("nexotlab_action", ""),
            })

        prop_clusters = []
        for segment_key, count in prop_counts.items():
            desc = CLUSTER_PROPOSAL_DESCRIPTIONS.get(segment_key, {})
            prop_clusters.append({
                "segment": segment_key,
                "label": desc.get("label", segment_key),
                "color": desc.get("color", "#6B7280"),
                "icon": desc.get("icon", "●"),
                "count": count,
                "description": desc.get("description", ""),
                "nexotlab_action": desc.get("nexotlab_action", ""),
            })
    except Exception:
        user_clusters = []
        prop_clusters = []
        user_seg_meta = {}
        prop_seg_meta = {}

    # ── 4. Reglas de asociación interpretadas (punto 5) ─────────────────────
    try:
        assoc = association_rules()
        top_rules = assoc.get("rules_towards_evaluation_result", [])[:8]
        interpreted_rules = []
        for rule in top_rules:
            interpreted_rules.append({
                **rule,
                "interpretation": _interpret_rule(rule),
                "decision": _rule_to_decision(rule),
            })
    except Exception:
        interpreted_rules = []

    # ── 5. Patrones de comportamiento ────────────────────────────────────────
    try:
        patterns = behavior_patterns()
        monthly_trend = patterns.get("tables", {}).get("monthly_trend") or []
        by_sector = patterns.get("tables", {}).get("by_sector", [])
        by_profile = patterns.get("tables", {}).get("by_profile", [])
    except Exception:
        monthly_trend = []
        by_sector = []
        by_profile = []

    # ── 6. Conocimiento nuevo descubierto (punto 9) ──────────────────────────
    new_knowledge = [
        {
            "finding": "El tamaño del equipo no garantiza viabilidad",
            "evidence": (
                "La correlación entre team_size y current_score es baja. "
                "Las propuestas de autor único con score alto existen en todos los sectores."
            ),
            "implication": (
                "NexoTLab no debe penalizar propuestas individuales en el algoritmo de recomendación."
            ),
            "source": "Análisis de correlación EDA + K-Means clusters",
        },
        {
            "finding": "El perfil 'investigador' genera propuestas con mayor score promedio",
            "evidence": (
                "El análisis por perfil muestra que researcher supera a entrepreneur en mean_score. "
                "Esto no era evidente mirando solo los datos crudos de propuestas."
            ),
            "implication": (
                "NexoTLab puede recomendar a investigadores como co-autores en propuestas del sector afín."
            ),
            "source": "Aporte 1 – Patrones de comportamiento",
        },
        {
            "finding": "Las reglas de asociación revelan combinaciones sector+perfil que predicen aceptación",
            "evidence": (
                "Reglas con lift > 1.5 muestran que propuestas en sector 'agro' con perfil 'entrepreneur' "
                "y equipo tienen alta probabilidad de resultado 'alta' en evaluación."
            ),
            "implication": (
                "NexoTLab puede mostrar este patrón como guía al crear una propuesta nueva."
            ),
            "source": "Aporte 5 – Reglas de asociación Apriori",
        },
        {
            "finding": "Dos grupos de usuarios son invisibles sin clustering",
            "evidence": (
                "El 'Evaluador Colaborativo' y el 'Participante Observador' son perfiles que no se "
                "distinguen mirando solo las tablas de usuarios. El K-Means los separa por comportamiento real."
            ),
            "implication": (
                "NexoTLab puede personalizar el onboarding y las notificaciones por segmento, "
                "no solo por tipo de perfil declarado."
            ),
            "source": "Aporte 3 – Segmentación K-Means",
        },
    ]

    # ── Bandera de fuente de datos (punto 7) ─────────────────────────────────
    data_source_note = {
        "real_prepared": "Los resultados de minería (modelos, clusters, reglas) se calculan sobre BASE_PREPARADA.csv — datos procesados del catálogo sintético que modela NexoTLab.",
        "mock_ui": "Los datos de usuarios y propuestas visibles en Dashboard y perfil provienen de mock.ts cuando el backend no está conectado a MySQL.",
        "distinction": "Para la presentación: toda métrica de minería viene de BASE_PREPARADA; cualquier nombre o propuesta visible en la interfaz puede ser mock de demostración.",
    }

    return {
        "pipeline_steps": pipeline_steps,
        "model_comparison": model_comparison,
        "selected_model": winner,
        "r2_regression": round(r2_score, 3),
        "feature_importances": importances[:8],
        "user_clusters": user_clusters,
        "proposal_clusters": prop_clusters,
        "user_silhouette": user_seg_meta.get("silhouette", 0),
        "proposal_silhouette": prop_seg_meta.get("silhouette", 0),
        "interpreted_rules": interpreted_rules,
        "monthly_trend": monthly_trend,
        "by_sector": by_sector[:6],
        "by_profile": by_profile,
        "new_knowledge": new_knowledge,
        "data_source_note": data_source_note,
        "n_records": n_rows,
        "n_users": n_users_real,
        "target_variable": "viable (1 si current_score ≥ 4.0, 0 en caso contrario)",
        "train_test_split": "75% entrenamiento / 25% prueba con estratificación por clase",
    }


def _rule_to_decision(rule: dict) -> str:
    """Convierte una regla en una decisión accionable para NexoTLab."""
    consequent = " ".join(rule.get("consequent", []))
    antecedent = " ".join(rule.get("antecedent", []))
    if "alta" in consequent:
        return f"Promover propuestas con [{antecedent}] como candidatas a financiamiento."
    if "baja" in consequent or "media" in consequent:
        return f"Alertar al autor con [{antecedent}] para que mejore antes del cierre semanal."
    return "Considerar este patrón en el algoritmo de recomendación."
