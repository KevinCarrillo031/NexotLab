"""Catálogo en memoria — dataset académico expandido (500 usuarios, 350 propuestas)."""

from __future__ import annotations

from copy import deepcopy
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any

import numpy as np
import pandas as pd

from app.config import settings
from app.domain.enums import (
    CollaboratorStatus,
    ProfileType,
    ProposalCategory,
    ProposalStatus,
    Sector,
)

PROFILES = list(ProfileType)
CATEGORIES = list(ProposalCategory)
SECTORS = list(Sector)
STATUSES = list(ProposalStatus)


def status_from_score(score: float) -> str:
    if score >= settings.high_score_threshold:
        return ProposalStatus.GOOD
    if score < settings.low_score_threshold:
        return ProposalStatus.NEEDS_IMPROVEMENT
    return ProposalStatus.EVALUATING


# ── Usuarios semilla (30 perfiles reales) ────────────────────────────────────
SEED_USERS: list[dict[str, Any]] = [
    # Administradores
    {"id": "admin1", "name": "Diego Martínez", "email": "admin@nexotlab.com", "profile_type": "company", "sector": "government", "is_admin": True, "active": True, "joined_at": "2026-01-01"},
    {"id": "admin2", "name": "Sandra Ríos", "email": "sandra.rios@nexotlab.com", "profile_type": "company", "sector": "government", "is_admin": True, "active": True, "joined_at": "2026-01-15"},
    # Emprendedores
    {"id": "user1", "name": "Camila Rodríguez", "email": "camila@nexotlab.com", "profile_type": "entrepreneur", "sector": "agro", "is_admin": False, "active": True, "joined_at": "2026-03-15"},
    {"id": "u6", "name": "Ricardo Soto", "email": "ricardo@nexotlab.com", "profile_type": "entrepreneur", "sector": "energy", "is_admin": False, "active": True, "joined_at": "2026-06-15"},
    {"id": "u7", "name": "Natalia Torres", "email": "natalia@nexotlab.com", "profile_type": "entrepreneur", "sector": "education", "is_admin": False, "active": True, "joined_at": "2026-07-01"},
    {"id": "u11", "name": "Felipe Arango", "email": "felipe.arango@nexotlab.com", "profile_type": "entrepreneur", "sector": "fintech", "is_admin": False, "active": True, "joined_at": "2026-02-10"},
    {"id": "u12", "name": "Manuela Vargas", "email": "manuela.v@nexotlab.com", "profile_type": "entrepreneur", "sector": "health", "is_admin": False, "active": True, "joined_at": "2026-03-22"},
    {"id": "u13", "name": "Esteban Cano", "email": "esteban.cano@nexotlab.com", "profile_type": "entrepreneur", "sector": "mobility", "is_admin": False, "active": True, "joined_at": "2026-04-05"},
    {"id": "u14", "name": "Alejandra Muñoz", "email": "ale.munoz@nexotlab.com", "profile_type": "entrepreneur", "sector": "environment", "is_admin": False, "active": False, "joined_at": "2026-05-18"},
    {"id": "u15", "name": "Gabriel Suárez", "email": "gabriel.s@nexotlab.com", "profile_type": "entrepreneur", "sector": "agro", "is_admin": False, "active": True, "joined_at": "2026-06-02"},
    # Investigadores
    {"id": "u2", "name": "Luis Bermúdez", "email": "luis@nexotlab.com", "profile_type": "researcher", "sector": "fintech", "is_admin": False, "active": True, "joined_at": "2026-04-02"},
    {"id": "u3", "name": "María José Ospina", "email": "maria@nexotlab.com", "profile_type": "researcher", "sector": "agro", "is_admin": False, "active": True, "joined_at": "2026-04-18"},
    {"id": "u8", "name": "Andrés Peña", "email": "andres@nexotlab.com", "profile_type": "researcher", "sector": "health", "is_admin": False, "active": True, "joined_at": "2026-07-20"},
    {"id": "u16", "name": "Cristina Velásquez", "email": "cristina.v@nexotlab.com", "profile_type": "researcher", "sector": "education", "is_admin": False, "active": True, "joined_at": "2026-02-28"},
    {"id": "u17", "name": "Jorge Herrera", "email": "jorge.h@nexotlab.com", "profile_type": "researcher", "sector": "energy", "is_admin": False, "active": True, "joined_at": "2026-03-10"},
    {"id": "u18", "name": "Lucía Patiño", "email": "lucia.p@nexotlab.com", "profile_type": "researcher", "sector": "environment", "is_admin": False, "active": True, "joined_at": "2026-05-05"},
    {"id": "u19", "name": "Rodrigo Escobar", "email": "rodrigo.e@nexotlab.com", "profile_type": "researcher", "sector": "mobility", "is_admin": False, "active": False, "joined_at": "2026-07-14"},
    # Empresas
    {"id": "u9", "name": "Valentina Cruz", "email": "vale@nexotlab.com", "profile_type": "company", "sector": "fintech", "is_admin": False, "active": True, "joined_at": "2026-08-05"},
    {"id": "u20", "name": "TechColombia S.A.S.", "email": "contacto@techcolombia.co", "profile_type": "company", "sector": "government", "is_admin": False, "active": True, "joined_at": "2026-01-20"},
    {"id": "u21", "name": "AgroDigital Ltda.", "email": "info@agrodigital.co", "profile_type": "company", "sector": "agro", "is_admin": False, "active": True, "joined_at": "2026-02-14"},
    {"id": "u22", "name": "SaludTech Corp.", "email": "ops@saludtech.co", "profile_type": "company", "sector": "health", "is_admin": False, "active": True, "joined_at": "2026-03-01"},
    {"id": "u23", "name": "Energía Verde S.A.", "email": "proyectos@energiaverde.co", "profile_type": "company", "sector": "energy", "is_admin": False, "active": True, "joined_at": "2026-04-10"},
    {"id": "u24", "name": "MoviSmart Ltda.", "email": "dev@movismart.co", "profile_type": "company", "sector": "mobility", "is_admin": False, "active": False, "joined_at": "2026-05-25"},
    # Ciudadanos
    {"id": "u4", "name": "Tomás Ávila", "email": "tomas@nexotlab.com", "profile_type": "citizen", "sector": "mobility", "is_admin": False, "active": False, "joined_at": "2026-05-10"},
    {"id": "u5", "name": "Paula Mendoza", "email": "paula@nexotlab.com", "profile_type": "citizen", "sector": "environment", "is_admin": False, "active": True, "joined_at": "2026-06-01"},
    {"id": "u10", "name": "Sebastián Mora", "email": "sebas@nexotlab.com", "profile_type": "citizen", "sector": "government", "is_admin": False, "active": False, "joined_at": "2026-08-20"},
    {"id": "u25", "name": "Isabela Flórez", "email": "isabela.f@nexotlab.com", "profile_type": "citizen", "sector": "education", "is_admin": False, "active": True, "joined_at": "2026-06-20"},
    {"id": "u26", "name": "Camilo Zuluaga", "email": "camilo.z@nexotlab.com", "profile_type": "citizen", "sector": "health", "is_admin": False, "active": True, "joined_at": "2026-07-05"},
    {"id": "u27", "name": "Sofía Morales", "email": "sofia.m@nexotlab.com", "profile_type": "citizen", "sector": "agro", "is_admin": False, "active": True, "joined_at": "2026-07-30"},
    {"id": "u28", "name": "Juliana Acosta", "email": "juliana.a@nexotlab.com", "profile_type": "citizen", "sector": "environment", "is_admin": False, "active": True, "joined_at": "2026-08-12"},
]

# ── Propuestas semilla (25 con datos ricos) ──────────────────────────────────
SEED_PROPOSALS: list[dict[str, Any]] = [
    {
        "id": "p1",
        "title": "Sistema de trazabilidad agrícola con blockchain",
        "category": "agritech",
        "sector": "agro",
        "description": "Propuesta para implementar un sistema descentralizado que permita rastrear el origen, procesamiento y distribución de productos agrícolas usando tecnología blockchain. Se integra con sensores IoT para registro automático de cada etapa.",
        "deliverable": "Prototipo funcional de plataforma web + API REST documentada + informe de viabilidad técnica y económica para el sector cafetero.",
        "author_id": "user1",
        "status": "good",
        "weekly_scores": [3.1, 3.8, 4.2, 4.5, 4.7],
        "current_score": 4.7,
        "collaborators": [
            {"user_id": "u8", "status": "accepted", "applied_at": "2026-08-20"},
            {"user_id": "u5", "status": "pending", "applied_at": "2026-09-01"},
            {"user_id": "u21", "status": "accepted", "applied_at": "2026-08-25"},
        ],
        "created_at": "2026-08-01",
        "evaluations_count": 47,
    },
    {
        "id": "p2",
        "title": "Marketplace de servicios para microempresarios rurales",
        "category": "digital-economy",
        "sector": "fintech",
        "description": "Plataforma digital que conecta microempresarios de zonas rurales con compradores urbanos, eliminando intermediarios y facilitando pagos digitales inclusivos con soporte para zonas sin conectividad estable.",
        "deliverable": "Aplicación móvil multiplataforma con módulo de pagos integrado y soporte offline básico.",
        "author_id": "u2",
        "status": "evaluating",
        "weekly_scores": [2.8, 3.1, 3.3, 3.5],
        "current_score": 3.5,
        "collaborators": [
            {"user_id": "u7", "status": "accepted", "applied_at": "2026-08-25"},
            {"user_id": "u11", "status": "accepted", "applied_at": "2026-09-02"},
        ],
        "created_at": "2026-08-10",
        "evaluations_count": 28,
    },
    {
        "id": "p3",
        "title": "Asistente de IA para diagnóstico de suelos colombianos",
        "category": "agritech",
        "sector": "agro",
        "description": "Modelo de machine learning entrenado con datos edafológicos de 12 regiones de Colombia para recomendar cultivos óptimos según perfil de suelo, temperatura y precipitación histórica.",
        "deliverable": "Modelo ML + API de inferencia + guía de uso para extensionistas agrícolas del ICA.",
        "author_id": "u3",
        "status": "needs-improvement",
        "weekly_scores": [2.5, 2.2, 1.9, 2.1, 2.3],
        "current_score": 2.3,
        "collaborators": [
            {"user_id": "u16", "status": "pending", "applied_at": "2026-09-10"},
        ],
        "created_at": "2026-07-28",
        "evaluations_count": 31,
    },
    {
        "id": "p4",
        "title": "Red de innovación ciudadana para movilidad sostenible",
        "category": "smart-cities",
        "sector": "mobility",
        "description": "Comunidad digital de ciudadanos que co-diseñan soluciones de movilidad sostenible para su municipio, con mapa colaborativo de rutas y puntos críticos.",
        "deliverable": "Portal web + guía metodológica de co-diseño + piloto documentado en 2 municipios del Eje Cafetero.",
        "author_id": "u4",
        "status": "evaluating",
        "weekly_scores": [3.5, 3.6, 3.8],
        "current_score": 3.8,
        "collaborators": [
            {"user_id": "u5", "status": "pending", "applied_at": "2026-09-05"},
            {"user_id": "u6", "status": "pending", "applied_at": "2026-09-08"},
            {"user_id": "u13", "status": "accepted", "applied_at": "2026-09-03"},
        ],
        "created_at": "2026-08-20",
        "evaluations_count": 22,
    },
    {
        "id": "p5",
        "title": "Plataforma de telemedicina rural con IA predictiva",
        "category": "health-tech",
        "sector": "health",
        "description": "Sistema de teleconsulta médica con módulo de IA que analiza síntomas reportados por pacientes rurales y sugiere diagnósticos preliminares, reduciendo desplazamientos innecesarios a centros de salud.",
        "deliverable": "App móvil + dashboard médico web + modelo de triaje predictivo con precisión >82%.",
        "author_id": "u12",
        "status": "good",
        "weekly_scores": [3.8, 4.0, 4.3, 4.5, 4.6],
        "current_score": 4.6,
        "collaborators": [
            {"user_id": "u8", "status": "accepted", "applied_at": "2026-08-30"},
            {"user_id": "u22", "status": "accepted", "applied_at": "2026-09-01"},
            {"user_id": "u26", "status": "pending", "applied_at": "2026-09-12"},
        ],
        "created_at": "2026-08-05",
        "evaluations_count": 52,
    },
    {
        "id": "p6",
        "title": "Sistema de microcréditos algorítmicos para emprendedores",
        "category": "fintech",
        "sector": "fintech",
        "description": "Motor de scoring crediticio alternativo que evalúa el historial de comportamiento digital, ventas en plataformas y reputación en redes para otorgar microcréditos sin historial bancario.",
        "deliverable": "Motor de scoring + panel de riesgo + integración con 2 entidades microfinancistas piloto.",
        "author_id": "u11",
        "status": "good",
        "weekly_scores": [4.0, 4.1, 4.3, 4.5],
        "current_score": 4.5,
        "collaborators": [
            {"user_id": "u9", "status": "accepted", "applied_at": "2026-09-05"},
            {"user_id": "u2", "status": "accepted", "applied_at": "2026-09-08"},
        ],
        "created_at": "2026-08-12",
        "evaluations_count": 39,
    },
    {
        "id": "p7",
        "title": "Hub de energía solar comunitaria descentralizada",
        "category": "sustainability",
        "sector": "energy",
        "description": "Modelo de negocio cooperativo para instalar paneles solares compartidos en comunidades rurales de baja tensión, con facturación automática y distribución de excedentes.",
        "deliverable": "Modelo financiero + prototipo de sistema de medición IoT + estudio de viabilidad para 3 comunidades piloto en Nariño.",
        "author_id": "u6",
        "status": "good",
        "weekly_scores": [3.5, 3.9, 4.1, 4.4, 4.6, 4.8],
        "current_score": 4.8,
        "collaborators": [
            {"user_id": "u17", "status": "accepted", "applied_at": "2026-08-22"},
            {"user_id": "u23", "status": "accepted", "applied_at": "2026-08-28"},
            {"user_id": "u18", "status": "accepted", "applied_at": "2026-09-02"},
        ],
        "created_at": "2026-07-25",
        "evaluations_count": 61,
    },
    {
        "id": "p8",
        "title": "Plataforma adaptativa de educación STEM rural",
        "category": "edtech",
        "sector": "education",
        "description": "LMS adaptativo con contenidos STEM en español y lenguas nativas que se ajusta al nivel y ritmo de cada estudiante. Funciona con conectividad limitada y en dispositivos de gama baja.",
        "deliverable": "Plataforma web-offline + app Android + banco de 200 ejercicios STEM + piloto con 3 instituciones rurales.",
        "author_id": "u7",
        "status": "good",
        "weekly_scores": [3.7, 4.0, 4.2, 4.4],
        "current_score": 4.4,
        "collaborators": [
            {"user_id": "u16", "status": "accepted", "applied_at": "2026-09-01"},
            {"user_id": "u25", "status": "pending", "applied_at": "2026-09-15"},
        ],
        "created_at": "2026-08-18",
        "evaluations_count": 33,
    },
    {
        "id": "p9",
        "title": "Observatorio de datos abiertos territoriales",
        "category": "open-data",
        "sector": "government",
        "description": "Portal de visualización de indicadores socioeconómicos municipales con datos del DANE, DNP y entidades territoriales, actualización automática vía API y panel ciudadano de seguimiento.",
        "deliverable": "Portal web responsive + pipeline de ingesta automatizada + 15 dashboards temáticos + guía de uso ciudadano.",
        "author_id": "u20",
        "status": "evaluating",
        "weekly_scores": [3.2, 3.4, 3.6, 3.7],
        "current_score": 3.7,
        "collaborators": [
            {"user_id": "u3", "status": "accepted", "applied_at": "2026-09-05"},
            {"user_id": "u10", "status": "pending", "applied_at": "2026-09-18"},
        ],
        "created_at": "2026-08-25",
        "evaluations_count": 19,
    },
    {
        "id": "p10",
        "title": "Sistema de gestión de residuos inteligente con IoT",
        "category": "circular-economy",
        "sector": "environment",
        "description": "Red de contenedores con sensores de llenado y clasificación automática que optimiza rutas de recolección y reporta en tiempo real a operadores. Incluye app ciudadana de reporte.",
        "deliverable": "Firmware para microcontroladores + backend de rutas + app móvil + piloto en 1 municipio.",
        "author_id": "u18",
        "status": "evaluating",
        "weekly_scores": [2.9, 3.2, 3.5, 3.6],
        "current_score": 3.6,
        "collaborators": [
            {"user_id": "u5", "status": "accepted", "applied_at": "2026-09-10"},
            {"user_id": "u28", "status": "accepted", "applied_at": "2026-09-12"},
            {"user_id": "u14", "status": "pending", "applied_at": "2026-09-20"},
        ],
        "created_at": "2026-09-01",
        "evaluations_count": 15,
    },
    {
        "id": "p11",
        "title": "App de mapeo comunitario para acceso a servicios públicos",
        "category": "smart-cities",
        "sector": "government",
        "description": "Herramienta de cartografía participativa donde los ciudadanos georreferencia deficiencias en servicios públicos (agua, luz, vías) y las instituciones hacen seguimiento en un panel centralizado.",
        "deliverable": "App móvil offline-first + panel de gestión institucional + API de integración con SIGOT.",
        "author_id": "u5",
        "status": "good",
        "weekly_scores": [3.9, 4.1, 4.3, 4.5, 4.6],
        "current_score": 4.6,
        "collaborators": [
            {"user_id": "u27", "status": "accepted", "applied_at": "2026-08-30"},
            {"user_id": "u20", "status": "pending", "applied_at": "2026-09-08"},
        ],
        "created_at": "2026-08-08",
        "evaluations_count": 44,
    },
    {
        "id": "p12",
        "title": "Motor de recomendación de cultivos con datos climáticos",
        "category": "agritech",
        "sector": "agro",
        "description": "Sistema que cruza datos climáticos del IDEAM, precios de mercado y preferencias del agricultor para recomendar el portafolio de cultivos óptimo por temporada.",
        "deliverable": "API de recomendación + dashboard web + app Android ligera para agricultores.",
        "author_id": "u15",
        "status": "evaluating",
        "weekly_scores": [3.3, 3.5, 3.7],
        "current_score": 3.7,
        "collaborators": [
            {"user_id": "u3", "status": "accepted", "applied_at": "2026-09-05"},
        ],
        "created_at": "2026-09-03",
        "evaluations_count": 12,
    },
    {
        "id": "p13",
        "title": "Red de intercambio de conocimiento entre investigadores",
        "category": "open-data",
        "sector": "education",
        "description": "Plataforma de repositorio y networking para investigadores latinoamericanos con sistema de validación de pares, métricas de impacto y búsqueda semántica de publicaciones.",
        "deliverable": "Portal web + motor de búsqueda semántico + sistema de reputación + piloto con 5 universidades.",
        "author_id": "u16",
        "status": "good",
        "weekly_scores": [4.1, 4.2, 4.4, 4.5],
        "current_score": 4.5,
        "collaborators": [
            {"user_id": "u2", "status": "accepted", "applied_at": "2026-09-01"},
            {"user_id": "u19", "status": "pending", "applied_at": "2026-09-14"},
        ],
        "created_at": "2026-08-22",
        "evaluations_count": 36,
    },
    {
        "id": "p14",
        "title": "Plataforma de economía circular para residuos industriales",
        "category": "circular-economy",
        "sector": "environment",
        "description": "Marketplace B2B que conecta empresas generadoras de residuos industriales aprovechables con transformadores locales, con trazabilidad completa y certificación de impacto ambiental.",
        "deliverable": "Plataforma web B2B + sistema de certificación + dashboard de impacto + integración RNEC.",
        "author_id": "u14",
        "status": "needs-improvement",
        "weekly_scores": [2.3, 2.1, 2.4, 2.2],
        "current_score": 2.2,
        "collaborators": [],
        "created_at": "2026-08-30",
        "evaluations_count": 14,
    },
    {
        "id": "p15",
        "title": "Sistema predictivo de mantenimiento para infraestructura vial",
        "category": "smart-cities",
        "sector": "mobility",
        "description": "Modelo de ML que analiza imágenes satelitales y reportes ciudadanos para priorizar inversión en mantenimiento vial municipal, con un horizonte de predicción de 6 meses.",
        "deliverable": "Modelo predictivo + API de consulta + integración con sistemas de INVIAS + piloto en 2 municipios.",
        "author_id": "u13",
        "status": "evaluating",
        "weekly_scores": [3.4, 3.6, 3.8, 4.0],
        "current_score": 4.0,
        "collaborators": [
            {"user_id": "u24", "status": "accepted", "applied_at": "2026-09-08"},
            {"user_id": "u17", "status": "pending", "applied_at": "2026-09-15"},
        ],
        "created_at": "2026-09-02",
        "evaluations_count": 21,
    },
    {
        "id": "p16",
        "title": "Laboratorio de innovación abierta para pymes manufactureras",
        "category": "digital-transformation",
        "sector": "government",
        "description": "Espacio virtual y físico de co-creación que ofrece a pymes manufactureras acceso a herramientas de diseño, prototipado digital y mentorías de transformación industrial 4.0.",
        "deliverable": "Plataforma de matching mentor-empresa + catálogo de recursos + 3 casos de transformación documentados.",
        "author_id": "u9",
        "status": "evaluating",
        "weekly_scores": [3.0, 3.3, 3.5, 3.7],
        "current_score": 3.7,
        "collaborators": [
            {"user_id": "u20", "status": "accepted", "applied_at": "2026-09-10"},
        ],
        "created_at": "2026-09-05",
        "evaluations_count": 17,
    },
    {
        "id": "p17",
        "title": "Fintech de ahorro programado para trabajadores informales",
        "category": "fintech",
        "sector": "fintech",
        "description": "App de ahorro automático que detecta picos de ingreso en trabajadores informales (conductores, vendedores, domiciliarios) y reserva micro-montos para fondos de emergencia y pensión voluntaria.",
        "deliverable": "App móvil + motor de detección de ingresos + integración PSE/Nequi + prueba con 200 usuarios.",
        "author_id": "u9",
        "status": "good",
        "weekly_scores": [4.2, 4.3, 4.5, 4.6, 4.7],
        "current_score": 4.7,
        "collaborators": [
            {"user_id": "u11", "status": "accepted", "applied_at": "2026-09-01"},
            {"user_id": "u2", "status": "accepted", "applied_at": "2026-09-06"},
            {"user_id": "u26", "status": "pending", "applied_at": "2026-09-18"},
        ],
        "created_at": "2026-08-15",
        "evaluations_count": 58,
    },
    {
        "id": "p18",
        "title": "Red de monitoreo ambiental ciudadano de bajo costo",
        "category": "sustainability",
        "sector": "environment",
        "description": "Dispositivos de medición de calidad del aire y agua de fabricación local (< $30 USD) conectados a una red comunitaria que publica datos abiertos en tiempo real.",
        "deliverable": "Diseño de hardware abierto + firmware + plataforma de datos + piloto con 50 sensores en 3 ciudades.",
        "author_id": "u28",
        "status": "evaluating",
        "weekly_scores": [3.6, 3.8, 3.9],
        "current_score": 3.9,
        "collaborators": [
            {"user_id": "u18", "status": "accepted", "applied_at": "2026-09-12"},
            {"user_id": "u17", "status": "pending", "applied_at": "2026-09-20"},
        ],
        "created_at": "2026-09-08",
        "evaluations_count": 11,
    },
    {
        "id": "p19",
        "title": "Plataforma de gestión de ensayos clínicos en Colombia",
        "category": "health-tech",
        "sector": "health",
        "description": "Sistema digital para gestión, seguimiento y reporting de ensayos clínicos según la normativa INVIMA, con módulos de consentimiento informado electrónico y trazabilidad de muestras.",
        "deliverable": "Plataforma web + app de campo para investigadores + módulo de reportes INVIMA + piloto con 2 IPS.",
        "author_id": "u8",
        "status": "good",
        "weekly_scores": [3.9, 4.1, 4.2, 4.4, 4.5],
        "current_score": 4.5,
        "collaborators": [
            {"user_id": "u22", "status": "accepted", "applied_at": "2026-09-03"},
            {"user_id": "u12", "status": "accepted", "applied_at": "2026-09-07"},
        ],
        "created_at": "2026-08-20",
        "evaluations_count": 40,
    },
    {
        "id": "p20",
        "title": "Sistema de gamificación para educación financiera",
        "category": "edtech",
        "sector": "education",
        "description": "Juego serio para jóvenes de 14-22 años que enseña conceptos de presupuesto, ahorro e inversión mediante simulaciones de decisiones financieras reales, con progresión adaptativa.",
        "deliverable": "Videojuego web + guía docente + integración con currículos MEN + prueba con 500 estudiantes.",
        "author_id": "u25",
        "status": "evaluating",
        "weekly_scores": [3.4, 3.7, 3.8, 4.0],
        "current_score": 4.0,
        "collaborators": [
            {"user_id": "u7", "status": "accepted", "applied_at": "2026-09-05"},
            {"user_id": "u16", "status": "pending", "applied_at": "2026-09-15"},
        ],
        "created_at": "2026-09-04",
        "evaluations_count": 24,
    },
    {
        "id": "p21",
        "title": "Marketplace de carbono para pequeños productores",
        "category": "sustainability",
        "sector": "environment",
        "description": "Plataforma que certifica y monetiza bonos de carbono generados por prácticas sostenibles de pequeños agricultores, con verificación satelital y trazabilidad blockchain.",
        "deliverable": "Plataforma web + módulo de verificación + integración con registros internacionales + piloto con 30 productores.",
        "author_id": "u27",
        "status": "needs-improvement",
        "weekly_scores": [2.6, 2.4, 2.3, 2.5],
        "current_score": 2.5,
        "collaborators": [
            {"user_id": "u18", "status": "pending", "applied_at": "2026-09-22"},
        ],
        "created_at": "2026-09-10",
        "evaluations_count": 9,
    },
    {
        "id": "p22",
        "title": "Plataforma de gestión de proyectos para juntas de acción comunal",
        "category": "digital-transformation",
        "sector": "government",
        "description": "Herramienta digital simple para que las JAC puedan planificar, presupuestar y reportar proyectos comunitarios, con generación automática de informes para alcaldías.",
        "deliverable": "App web + app móvil + plantillas de proyectos + integración con sistema de rendición de cuentas.",
        "author_id": "u10",
        "status": "evaluating",
        "weekly_scores": [3.1, 3.3, 3.4],
        "current_score": 3.4,
        "collaborators": [
            {"user_id": "u5", "status": "pending", "applied_at": "2026-09-20"},
        ],
        "created_at": "2026-09-12",
        "evaluations_count": 8,
    },
    {
        "id": "p23",
        "title": "Sistema de irrigación inteligente con ML para ahorro hídrico",
        "category": "agritech",
        "sector": "agro",
        "description": "Controlador de riego automatizado que combina pronósticos climáticos, humedad del suelo en tiempo real y modelos de evapotranspiración para reducir el consumo de agua hasta un 40%.",
        "deliverable": "Hardware de control + firmware + dashboard agrícola + validación en 5 fincas piloto.",
        "author_id": "u21",
        "status": "good",
        "weekly_scores": [4.0, 4.2, 4.4, 4.5, 4.7],
        "current_score": 4.7,
        "collaborators": [
            {"user_id": "u3", "status": "accepted", "applied_at": "2026-09-02"},
            {"user_id": "u15", "status": "accepted", "applied_at": "2026-09-05"},
            {"user_id": "u23", "status": "pending", "applied_at": "2026-09-18"},
        ],
        "created_at": "2026-08-28",
        "evaluations_count": 35,
    },
    {
        "id": "p24",
        "title": "Hub digital de turismo comunitario en zonas de posconflicto",
        "category": "digital-economy",
        "sector": "government",
        "description": "Plataforma de promoción y reserva de experiencias de turismo rural y comunitario en municipios de posconflicto, con integración de pagos digitales y sistema de calificación.",
        "deliverable": "Portal web + app turista + panel de operadores + integración ProColombia + piloto en 4 municipios PDET.",
        "author_id": "u20",
        "status": "evaluating",
        "weekly_scores": [3.5, 3.8, 4.0],
        "current_score": 4.0,
        "collaborators": [
            {"user_id": "u9", "status": "accepted", "applied_at": "2026-09-10"},
            {"user_id": "u27", "status": "pending", "applied_at": "2026-09-19"},
        ],
        "created_at": "2026-09-07",
        "evaluations_count": 18,
    },
    {
        "id": "p25",
        "title": "Red de bibliotecas digitales comunitarias sin internet",
        "category": "edtech",
        "sector": "education",
        "description": "Sistema de distribución de contenidos educativos (libros, videos, software) mediante redes mesh WiFi locales sin depender de internet externo, administrado por la propia comunidad.",
        "deliverable": "Software de nodo mesh + catálogo de contenidos curado + guía de instalación + piloto en 6 veredas.",
        "author_id": "u25",
        "status": "good",
        "weekly_scores": [4.1, 4.3, 4.5, 4.6],
        "current_score": 4.6,
        "collaborators": [
            {"user_id": "u7", "status": "accepted", "applied_at": "2026-09-08"},
            {"user_id": "u16", "status": "accepted", "applied_at": "2026-09-12"},
        ],
        "created_at": "2026-09-05",
        "evaluations_count": 29,
    },
]

# ── Nombres para el generador ────────────────────────────────────────────────
FIRST_NAMES = [
    "Ana", "Carlos", "Laura", "Julián", "Daniela", "Mateo", "Isabella", "Santiago",
    "Valeria", "Nicolás", "Alejandro", "Mariana", "David", "Catalina", "Andrés",
    "Sofía", "Sebastián", "Natalia", "Felipe", "Camila", "Jorge", "Paula", "Luis",
    "Claudia", "Javier", "Marcela", "Esteban", "Diana", "Mauricio", "Ximena",
]
LAST_NAMES = [
    "Gómez", "Restrepo", "Castaño", "Mejía", "Henao", "Cardona", "Giraldo",
    "Quintero", "López", "Ramírez", "Vargas", "Molina", "Herrera", "Castro",
    "Gutiérrez", "Torres", "Flores", "Medina", "Ramos", "Cruz", "Ríos", "Morales",
    "Ortiz", "Díaz", "Suárez", "Rojas", "Muñoz", "Jiménez", "Pardo", "Cano",
]

# ── Vocabulario rico para generador de propuestas ───────────────────────────
PROPOSAL_TEMPLATES = [
    ("Plataforma de {tema} para {actor}", "Sistema digital que permite a {actor} acceder y gestionar {tema} de forma eficiente."),
    ("Sistema inteligente de {tema} con IA", "Solución basada en inteligencia artificial para optimizar procesos de {tema} en el sector {sector}."),
    ("Red colaborativa de {tema} territorial", "Ecosistema de actores locales articulados para impulsar {tema} en territorios priorizados."),
    ("Marketplace de {tema} entre pares", "Plataforma P2P que conecta ofertantes y demandantes de {tema}, reduciendo fricciones y costos."),
    ("Observatorio de {tema} con datos abiertos", "Portal de visualización y análisis de indicadores de {tema} con fuentes de datos públicas actualizadas."),
    ("Laboratorio de innovación en {tema}", "Espacio virtual de co-creación y prototipado rápido enfocado en {tema} para comunidades locales."),
    ("Hub de {tema} para pymes del sector {sector}", "Plataforma de recursos, herramientas y conexiones especializadas en {tema} para pequeñas y medianas empresas."),
    ("App de {tema} offline-first para zonas rurales", "Aplicación móvil que funciona sin conectividad permanente y resuelve necesidades de {tema} en zonas apartadas."),
    ("Motor de predicción de {tema} con ML", "Modelo de machine learning que anticipa tendencias y riesgos en {tema} para apoyar la toma de decisiones."),
    ("Ecosistema de {tema} bajo economía circular", "Modelo de negocio regenerativo que integra los principios de economía circular en la cadena de {tema}."),
]

TEMAS = [
    "gestión del agua", "acceso a crédito", "cadena de frío", "salud preventiva",
    "movilidad urbana", "residuos sólidos", "energía renovable", "empleo juvenil",
    "exportaciones agropecuarias", "turismo cultural", "formación técnica",
    "transparencia fiscal", "inclusión financiera", "datos de salud", "logística rural",
    "seguridad alimentaria", "biodiversidad", "vivienda social", "comercio electrónico",
    "trazabilidad de alimentos", "calidad del aire", "gestión de riesgos",
    "economía solidaria", "innovación social", "acceso a justicia", "identidad digital",
    "capacitación docente", "adaptación climática", "mipymes rurales", "patrimonio cultural",
]

ACTORES = [
    "agricultores", "microempresarios", "jóvenes rurales", "mujeres emprendedoras",
    "instituciones educativas", "alcaldías municipales", "cooperativas", "pymes",
    "pacientes crónicos", "transportadores", "artesanos", "organizaciones sociales",
    "investigadores", "comunidades indígenas", "trabajadores informales",
]

ENTREGABLES_TEMPLATES = [
    "Prototipo funcional + documentación técnica + piloto en {n} municipios.",
    "App móvil + API REST + informe de validación con {n} usuarios reales.",
    "Plataforma web + modelo ML entrenado + manual de implementación.",
    "Dashboard de datos + pipeline automatizado + guía metodológica.",
    "Hardware prototipo + firmware + aplicación de gestión + piloto de {n} semanas.",
    "Portal web responsive + {n} dashboards temáticos + datos abiertos vinculados.",
    "Motor de recomendación + integración con {n} sistemas existentes + informe de impacto.",
]

COMENTARIOS_POOL = [
    "Hay potencial de escalamiento territorial importante.",
    "Falta claridad en el modelo de sostenibilidad financiera.",
    "El equipo interdisciplinario fortalece la propuesta.",
    "El impacto social es alto pero la viabilidad técnica requiere más detalle.",
    "Se observa alineación clara con los ejes de transformación digital.",
    "La propuesta necesita una estrategia de apropiación comunitaria más robusta.",
    "Excelente identificación del problema, la solución es pertinente.",
    "El modelo de negocio no está suficientemente validado con el mercado objetivo.",
    "La metodología de implementación es sólida y replicable.",
    "Se recomienda ampliar el alcance geográfico del piloto.",
    "La propuesta muestra madurez tecnológica superior al promedio.",
    "Los indicadores de éxito propuestos son medibles y realistas.",
    "Falta articulación con actores institucionales clave del sector.",
    "El enfoque diferencial y de género agrega valor significativo.",
    "La propuesta tiene componente de formación de capacidades locales, lo cual es positivo.",
    "Se sugiere explorar alianzas con el sector privado para asegurar la sostenibilidad.",
    "El análisis de riesgos es insuficiente para una propuesta de esta escala.",
    "La experiencia previa del equipo proponente aumenta la credibilidad.",
    "La propuesta responde a una necesidad verificada con datos primarios.",
    "Se recomienda fortalecer el componente de privacidad y protección de datos.",
]


def _clip_score(value: float) -> float:
    return float(np.clip(round(value, 2), 1.0, 5.0))


def build_synthetic_frames(
    n_users: int = 500, n_proposals: int = 350, seed: int | None = None
) -> dict[str, pd.DataFrame]:
    rng = np.random.default_rng(seed if seed is not None else settings.random_seed)

    # ── Usuarios ─────────────────────────────────────────────────────────────
    users: list[dict[str, Any]] = []
    for raw in SEED_USERS:
        users.append({**raw, "proposals_count": 0})

    profile_probs = [0.30, 0.20, 0.28, 0.22]
    while len(users) < n_users:
        idx = len(users)
        profile = str(rng.choice(PROFILES, p=profile_probs))
        sector = str(rng.choice(SECTORS))
        users.append({
            "id": f"su{idx:04d}",
            "name": f"{rng.choice(FIRST_NAMES)} {rng.choice(LAST_NAMES)}",
            "email": f"user{idx}@nexotlab.com",
            "profile_type": profile,
            "sector": sector,
            "is_admin": False,
            "active": bool(rng.random() > 0.07),
            "joined_at": (date(2026, 1, 1) + timedelta(days=int(rng.integers(0, 270)))).isoformat(),
            "proposals_count": 0,
        })
    users_df = pd.DataFrame(users)

    author_ids = users_df.loc[~users_df["is_admin"], "id"].tolist()
    proposals: list[dict[str, Any]] = []
    collaborators: list[dict[str, Any]] = []
    evaluations: list[dict[str, Any]] = []
    comments: list[dict[str, Any]] = []

    # Cargar seeds
    for raw in SEED_PROPOSALS:
        proposals.append({k: v for k, v in raw.items() if k != "collaborators"})
        for collab in raw["collaborators"]:
            collaborators.append({"proposal_id": raw["id"], **collab})

    # ── Propuestas sintéticas ────────────────────────────────────────────────
    base_scores: dict[str, float] = {
        "entrepreneur": 3.4, "company": 3.6, "researcher": 3.75, "citizen": 3.1,
    }
    sector_boost: dict[str, float] = {
        "agro": 0.20, "fintech": 0.25, "energy": 0.20, "health": 0.15,
        "education": 0.10, "mobility": 0.05, "government": 0.0, "environment": 0.10,
    }

    while len(proposals) < n_proposals:
        idx = len(proposals)
        author_id = str(rng.choice(author_ids))
        author_row = users_df.loc[users_df["id"] == author_id].iloc[0]
        profile = str(author_row["profile_type"])
        sector = str(author_row["sector"]) if rng.random() < 0.65 else str(rng.choice(SECTORS))
        category = str(rng.choice(CATEGORIES))
        weeks = int(rng.integers(2, 7))

        base = base_scores.get(profile, 3.3) + sector_boost.get(sector, 0.0)
        trend = rng.choice([-0.05, 0.0, 0.10, 0.15], p=[0.15, 0.25, 0.40, 0.20])
        noise = rng.normal(0, 0.45, size=weeks)
        weekly = [_clip_score(base + trend * i + n) for i, n in enumerate(noise)]
        current = weekly[-1]

        template_idx = int(rng.integers(0, len(PROPOSAL_TEMPLATES)))
        title_tpl, desc_tpl = PROPOSAL_TEMPLATES[template_idx]
        tema = str(rng.choice(TEMAS))
        actor = str(rng.choice(ACTORES))
        title = title_tpl.format(tema=tema, actor=actor, sector=sector)
        description = (
            desc_tpl.format(actor=actor, tema=tema, sector=sector)
            + f" Propuesta del sector {sector} con enfoque en {tema}, orientada a {actor}."
        )
        entregable_tpl = str(rng.choice(ENTREGABLES_TEMPLATES))
        deliverable = entregable_tpl.format(n=int(rng.integers(2, 6)))

        n_eval = int(max(3, rng.normal(18, 9)))
        proposals.append({
            "id": f"sp{idx:04d}",
            "title": title,
            "category": category,
            "sector": sector,
            "description": description,
            "deliverable": deliverable,
            "author_id": author_id,
            "status": status_from_score(current),
            "weekly_scores": weekly,
            "current_score": current,
            "created_at": (date(2026, 2, 1) + timedelta(days=int(rng.integers(0, 210)))).isoformat(),
            "evaluations_count": n_eval,
        })

        # Colaboradores
        n_collab = int(rng.choice([0, 1, 2, 3, 4], p=[0.25, 0.30, 0.25, 0.12, 0.08]))
        candidates = [uid for uid in author_ids if uid != author_id]
        chosen = rng.choice(candidates, size=min(n_collab, len(candidates)), replace=False)
        for user_id in chosen:
            collaborators.append({
                "proposal_id": f"sp{idx:04d}",
                "user_id": str(user_id),
                "status": CollaboratorStatus.ACCEPTED if rng.random() < 0.68 else CollaboratorStatus.PENDING,
                "applied_at": (date(2026, 5, 1) + timedelta(days=int(rng.integers(0, 120)))).isoformat(),
            })

        # Evaluaciones
        ev_pool = [uid for uid in author_ids if uid != author_id]
        for e_i in range(min(n_eval, 15)):
            ev_id = str(rng.choice(ev_pool))
            viability  = _clip_score(current + rng.normal(0,    0.35))
            innovation = _clip_score(current + rng.normal(0.10, 0.40))
            impact     = _clip_score(current + rng.normal(0,    0.40))
            clarity    = _clip_score(current + rng.normal(-0.05,0.30))
            ev_score   = _clip_score((viability + innovation + impact + clarity) / 4)
            evaluations.append({
                "id": f"ev{idx:04d}_{e_i}",
                "proposal_id": f"sp{idx:04d}",
                "evaluator_id": ev_id,
                "viability":  viability,
                "innovation": innovation,
                "impact":     impact,
                "clarity":    clarity,
                "score":      ev_score,
                "created_at": (date(2026, 5, 1) + timedelta(days=int(rng.integers(0, 120)))).isoformat(),
            })
            if rng.random() < 0.38:
                comments.append({
                    "id": f"c{idx:04d}_{e_i}",
                    "proposal_id": f"sp{idx:04d}",
                    "user_id": ev_id,
                    "body": str(rng.choice(COMENTARIOS_POOL)),
                    "created_at": (date(2026, 5, 1) + timedelta(days=int(rng.integers(0, 120)))).isoformat(),
                })

    proposals_df = pd.DataFrame(proposals)
    counts = proposals_df.groupby("author_id").size().to_dict()
    users_df["proposals_count"] = users_df["id"].map(lambda uid: int(counts.get(uid, 0)))

    collab_df = pd.DataFrame(collaborators)
    team_size = collab_df.groupby("proposal_id").size().to_dict() if not collab_df.empty else {}
    accepted_map = (
        collab_df[collab_df["status"] == CollaboratorStatus.ACCEPTED]
        .groupby("proposal_id").size().to_dict()
        if not collab_df.empty else {}
    )
    proposals_df["team_size"] = proposals_df["id"].map(lambda pid: int(team_size.get(pid, 0)))
    proposals_df["accepted_collaborators"] = proposals_df["id"].map(lambda pid: int(accepted_map.get(pid, 0)))
    proposals_df["description_length"] = proposals_df["description"].str.len()
    proposals_df["viable"] = (proposals_df["current_score"] >= settings.high_score_threshold).astype(int)
    proposals_df["acceptance_level"] = pd.cut(
        proposals_df["current_score"],
        bins=[0, settings.low_score_threshold, settings.high_score_threshold, 5.01],
        labels=["baja", "media", "alta"],
        include_lowest=True,
    )

    return {
        "users": users_df,
        "proposals": proposals_df,
        "collaborators": collab_df,
        "evaluations": pd.DataFrame(evaluations),
        "comments": pd.DataFrame(comments),
    }


# ── Store de plataforma (API REST) ───────────────────────────────────────────
@dataclass
class MemoryStore:
    users: list[dict[str, Any]] = field(default_factory=list)
    proposals: list[dict[str, Any]] = field(default_factory=list)
    notifications: list[dict[str, Any]] = field(default_factory=list)

    def snapshot(self) -> dict[str, Any]:
        return {
            "users": deepcopy(self.users),
            "proposals": deepcopy(self.proposals),
            "notifications": deepcopy(self.notifications),
        }


def build_platform_store() -> MemoryStore:
    user_by_id = {u["id"]: u for u in SEED_USERS}
    counts: dict[str, int] = {}
    for p in SEED_PROPOSALS:
        counts[p["author_id"]] = counts.get(p["author_id"], 0) + 1

    users = [
        {**u, "proposals_count": counts.get(u["id"], 0)}
        for u in SEED_USERS
    ]
    user_map = {u["id"]: u for u in users}

    proposals = []
    for raw in SEED_PROPOSALS:
        author = user_map[raw["author_id"]]
        collabs = []
        for item in raw["collaborators"]:
            member = user_map.get(item["user_id"], user_by_id.get(item["user_id"]))
            if member:
                collabs.append({
                    "id": member["id"],
                    "name": member["name"],
                    "profileType": member["profile_type"],
                    "status": item["status"],
                    "appliedAt": item["applied_at"],
                })
        proposals.append({
            "id": raw["id"],
            "title": raw["title"],
            "category": raw["category"],
            "sector": raw["sector"],
            "description": raw["description"],
            "deliverable": raw["deliverable"],
            "authorId": raw["author_id"],
            "authorName": author["name"],
            "authorProfile": author["profile_type"],
            "status": raw["status"],
            "weeklyScores": list(raw["weekly_scores"]),
            "currentScore": raw["current_score"],
            "collaborators": collabs,
            "createdAt": raw["created_at"],
            "evaluationsCount": raw["evaluations_count"],
        })

    notifications = [
        {"id": "n1",  "type": "positive",    "message": "Tu propuesta superó el umbral alto esta semana con score 4.7.",                      "proposalTitle": "Sistema de trazabilidad agrícola con blockchain",      "date": "2026-09-08", "read": False},
        {"id": "n2",  "type": "social",       "message": "Andrés Peña se postuló como colaborador en tu propuesta.",                           "proposalTitle": "Sistema de trazabilidad agrícola con blockchain",      "date": "2026-09-01", "read": False},
        {"id": "n3",  "type": "improvement",  "message": "Tu propuesta no alcanzó el umbral mínimo esta semana. Revisa los criterios.",        "proposalTitle": "Asistente de IA para diagnóstico de suelos colombianos","date": "2026-09-01", "read": True},
        {"id": "n4",  "type": "positive",     "message": "¡Felicitaciones! Tu propuesta es la mejor calificada de la semana con 4.8.",         "proposalTitle": "Hub de energía solar comunitaria descentralizada",      "date": "2026-09-08", "read": False},
        {"id": "n5",  "type": "social",       "message": "AgroDigital Ltda. se unió como colaboradora en tu propuesta.",                       "proposalTitle": "Sistema de trazabilidad agrícola con blockchain",      "date": "2026-08-25", "read": True},
        {"id": "n6",  "type": "social",       "message": "Valentina Cruz se postuló como colaboradora en tu propuesta de fintech.",            "proposalTitle": "Sistema de microcréditos algorítmicos para emprendedores","date": "2026-09-05","read": False},
        {"id": "n7",  "type": "positive",     "message": "Tu propuesta alcanzó 52 evaluaciones esta semana, un récord en la plataforma.",      "proposalTitle": "Plataforma de telemedicina rural con IA predictiva",   "date": "2026-09-10", "read": True},
        {"id": "n8",  "type": "improvement",  "message": "Tu propuesta bajó al umbral de mejora. Considera revisar la propuesta de valor.",    "proposalTitle": "Marketplace de carbono para pequeños productores",     "date": "2026-09-15", "read": False},
        {"id": "n9",  "type": "social",       "message": "Luis Bermúdez aceptó tu invitación para colaborar.",                                 "proposalTitle": "Sistema de microcréditos algorítmicos para emprendedores","date": "2026-09-08","read": True},
        {"id": "n10", "type": "positive",     "message": "Tu propuesta fue destacada en el informe semanal de innovación.",                    "proposalTitle": "Fintech de ahorro programado para trabajadores informales","date": "2026-09-09","read": False},
        {"id": "n11", "type": "social",       "message": "Cristina Velásquez se postuló como colaboradora.",                                   "proposalTitle": "Red de intercambio de conocimiento entre investigadores","date": "2026-09-01","read": True},
        {"id": "n12", "type": "improvement",  "message": "La propuesta necesita mejoras en el criterio de innovación.",                        "proposalTitle": "Plataforma de economía circular para residuos industriales","date": "2026-09-12","read": False},
    ]

    return MemoryStore(users=users, proposals=proposals, notifications=notifications)


STORE = build_platform_store()
SYNTHETIC = build_synthetic_frames()
