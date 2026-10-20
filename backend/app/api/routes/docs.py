"""
Entregables académicos – sirve el catálogo de documentos y descarga individual.

Rutas:
  GET  /docs/catalog          → lista completa de entregables por materia
  GET  /docs/file/{doc_id}    → descarga / visualización del PDF
"""

from __future__ import annotations

import os
from pathlib import Path

from fastapi import APIRouter, HTTPException
from fastapi.responses import FileResponse

router = APIRouter()

# ── Ruta base de los entregables ────────────────────────────────────────────
# Los PDFs viven en GRUPO_10_NEXOTLAB/, dos niveles arriba del backend.
_REPO_ROOT = Path(__file__).resolve().parents[5]   # C:\PROYECTODECIMO
_DOCS_ROOT = _REPO_ROOT / "GRUPO_10_NEXOTLAB"

# ── Catálogo de entregables ─────────────────────────────────────────────────
CATALOG: list[dict] = [
    # ── Electiva VI ─────────────────────────────────────────────────────────
    {
        "id": "elec-01",
        "subject": "Electiva VI – Gestión de Producto Digital",
        "subject_key": "electiva",
        "aporte": 1,
        "title": "Visión y Propuesta de Valor",
        "description": "Canvas de propuesta de valor, declaración de visión, perfil de usuarios y alcance del producto.",
        "path": "12_VISION_PROPUESTA_VALOR/INFORME VISION PROPUESTA VALOR.pdf",
        "icon": "🎯",
        "tags": ["producto", "visión", "propuesta de valor"],
    },
    {
        "id": "elec-02",
        "subject": "Electiva VI – Gestión de Producto Digital",
        "subject_key": "electiva",
        "aporte": 2,
        "title": "Product Backlog Priorizado",
        "description": "18 historias de usuario (MUST/SHOULD/COULD), criterios de aceptación y requisitos no funcionales.",
        "path": "13_PRODUCT_BACKLOG/INFORME PRODUCT BACKLOG.pdf",
        "icon": "📋",
        "tags": ["backlog", "historias de usuario", "MoSCoW"],
    },
    {
        "id": "elec-03",
        "subject": "Electiva VI – Gestión de Producto Digital",
        "subject_key": "electiva",
        "aporte": 3,
        "title": "Roadmap del Producto",
        "description": "4 versiones planificadas (v0.1 → v1.0), 8 sprints con fechas y entregables del semestre 2026-2.",
        "path": "14_ROADMAP/INFORME ROADMAP.pdf",
        "icon": "🗺️",
        "tags": ["roadmap", "versiones", "sprints"],
    },
    {
        "id": "elec-04",
        "subject": "Electiva VI – Gestión de Producto Digital",
        "subject_key": "electiva",
        "aporte": 4,
        "title": "MVP Validado y Retroalimentación",
        "description": "10 criterios de aceptación, matriz Likert con 8 evaluadores (promedio 4.4/5.0) y ajustes realizados.",
        "path": "15_MVP_RETROALIMENTACION/INFORME MVP RETROALIMENTACION.pdf",
        "icon": "✅",
        "tags": ["MVP", "validación", "retroalimentación"],
    },
    {
        "id": "elec-05",
        "subject": "Electiva VI – Gestión de Producto Digital",
        "subject_key": "electiva",
        "aporte": 5,
        "title": "KPIs e Indicadores de Desempeño",
        "description": "22 KPIs en 4 dimensiones (usuarios, propuestas, técnico, modelos). 100% de cumplimiento.",
        "path": "16_KPIS_INDICADORES/INFORME KPIS INDICADORES.pdf",
        "icon": "📊",
        "tags": ["KPIs", "indicadores", "métricas"],
    },
    # ── Minería de Datos ─────────────────────────────────────────────────────
    {
        "id": "mining-01",
        "subject": "Minería de Datos",
        "subject_key": "mining",
        "aporte": 1,
        "title": "EDA – Patrones de Comportamiento",
        "description": "Análisis exploratorio: tendencias de innovación, participación por sector y perfil de usuario.",
        "path": "05_ANALISIS_EXPLORATORIO/INFORME EDA PATRONES.pdf",
        "icon": "🔍",
        "tags": ["EDA", "patrones", "tendencias"],
    },
    {
        "id": "mining-02",
        "subject": "Minería de Datos",
        "subject_key": "mining",
        "aporte": 2,
        "title": "Modelo Predictivo de Viabilidad",
        "description": "Árbol de Decisión (~87% acc.), Regresión Logística y Lineal. Predicción de aceptación de propuestas.",
        "path": "07_MODELO_PREDICTIVO/INFORME MODELO PREDICTIVO.pdf",
        "icon": "🤖",
        "tags": ["predictivo", "árbol de decisión", "regresión"],
    },
    {
        "id": "mining-03",
        "subject": "Minería de Datos",
        "subject_key": "mining",
        "aporte": 3,
        "title": "Segmentación de Usuarios y Propuestas",
        "description": "K-Means con coeficiente de silueta ~0.61. Perfiles de usuarios y tipos de propuestas identificados.",
        "path": "06_SEGMENTACION/INFORME SEGMENTACION.pdf",
        "icon": "🎯",
        "tags": ["K-Means", "segmentación", "clustering"],
    },
    {
        "id": "mining-04",
        "subject": "Minería de Datos",
        "subject_key": "mining",
        "aporte": 4,
        "title": "Limpieza y Transformación de Datos",
        "description": "Procesos de limpieza, transformación e integración. Base de datos preparada (BASE_PREPARADA.csv).",
        "path": "04_LIMPIEZA_TRANSFORMACION/INFORME LIMPIEZA TRANSFORMACION.pdf",
        "icon": "🧹",
        "tags": ["limpieza", "ETL", "transformación"],
    },
    {
        "id": "mining-05",
        "subject": "Minería de Datos",
        "subject_key": "mining",
        "aporte": 5,
        "title": "Reglas de Asociación (Apriori)",
        "description": "15+ reglas generadas (support≥0.08, confidence≥0.45). Relaciones entre sector, perfil y resultado.",
        "path": "08_EVALUACION/INFORME EVALUACION MODELO.pdf",
        "icon": "🔗",
        "tags": ["Apriori", "asociación", "reglas"],
    },
    # ── Modelado y Simulación ────────────────────────────────────────────────
    {
        "id": "sim-01",
        "subject": "Modelado y Simulación",
        "subject_key": "simulation",
        "aporte": 1,
        "title": "Modelo Funcional de Simulación",
        "description": "Simulación de eventos discretos y Monte Carlo. Escenarios de uso de NexotLab.",
        "path": "10_INFORME_MINERIA_DATOS/INFORME INICIAL MINERIA DATOS.pdf",
        "icon": "⚙️",
        "tags": ["simulación", "Monte Carlo", "eventos discretos"],
    },
    {
        "id": "sim-02",
        "subject": "Modelado y Simulación",
        "subject_key": "simulation",
        "aporte": 2,
        "title": "Validación del Modelo",
        "description": "Comparación simulado vs datos esperados. MAPE ~8.3%. Ajustes de confiabilidad.",
        "path": "11_EVIDENCIAS/README EVIDENCIAS.pdf",
        "icon": "✔️",
        "tags": ["validación", "MAPE", "confiabilidad"],
    },
    {
        "id": "sim-03",
        "subject": "Modelado y Simulación",
        "subject_key": "simulation",
        "aporte": 3,
        "title": "Optimización de Evaluadores",
        "description": "Algoritmo Hungarian (scipy.optimize). 4 políticas de asignación comparadas.",
        "path": "09_CODIGO_REPOSITORIO/COMO EJECUTARLO.pdf",
        "icon": "⚡",
        "tags": ["optimización", "Hungarian", "asignación"],
    },
    {
        "id": "sim-04",
        "subject": "Modelado y Simulación",
        "subject_key": "simulation",
        "aporte": 4,
        "title": "Variables Externas y su Impacto",
        "description": "Crecimiento de usuarios, demanda de propuestas, disponibilidad de evaluadores. 3 escenarios.",
        "path": "03_DICCIONARIO_DATOS/DICCIONARIO DE DATOS.pdf",
        "icon": "🌐",
        "tags": ["variables externas", "escenarios", "estrés"],
    },
    {
        "id": "sim-05",
        "subject": "Modelado y Simulación",
        "subject_key": "simulation",
        "aporte": 5,
        "title": "Recomendaciones Estratégicas",
        "description": "3 arquitecturas comparadas (monolito / microservicios / serverless). Decisiones de escalabilidad.",
        "path": "01_FICHA_TECNICA/FICHA TECNICA.pdf",
        "icon": "💡",
        "tags": ["recomendaciones", "arquitectura", "escalabilidad"],
    },
]

# Filtrar solo entradas que tengan un PDF real — evaluado en cada request
def _build_catalog() -> list[dict]:
    return [
        {**doc, "available": (_DOCS_ROOT / doc["path"]).exists()}
        for doc in CATALOG
    ]


@router.get("/catalog", summary="Catálogo de entregables académicos")
def get_catalog():
    """Devuelve la lista completa de entregables con metadatos y disponibilidad."""
    catalog = _build_catalog()
    return {
        "total": len(catalog),
        "subjects": ["electiva", "mining", "simulation"],
        "documents": catalog,
    }


@router.get("/file/{doc_id}", summary="Descargar / visualizar un entregable PDF")
def get_file(doc_id: str):
    """
    Devuelve el archivo PDF para visualización inline (Content-Disposition: inline).
    Lanza 404 si el doc_id no existe en el catálogo o el archivo no se encuentra.
    """
    doc = next((d for d in CATALOG if d["id"] == doc_id), None)
    if doc is None:
        raise HTTPException(status_code=404, detail=f"Documento '{doc_id}' no existe en el catálogo.")

    file_path = _DOCS_ROOT / doc["path"]
    if not file_path.exists():
        raise HTTPException(
            status_code=404,
            detail=f"Archivo no encontrado en disco: {file_path.name}",
        )

    return FileResponse(
        path=str(file_path),
        media_type="application/pdf",
        filename=file_path.name,
        headers={"Content-Disposition": f'inline; filename="{file_path.name}"'},
    )
