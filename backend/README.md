# NexotLab Backend

Backend académico de NexotLab en **FastAPI + Python 3.14**.
Cubre los 10 aportes de las dos asignaturas del proyecto:

- **Asignatura 1**: Modelado y Simulación (5 aportes)
- **Asignatura 2**: Minería de Datos (5 aportes)

---

## Arranque rápido

```bash
cd backend
# activar entorno virtual
.venv\Scripts\activate          # Windows
# source .venv/bin/activate    # macOS/Linux

# levantar servidor
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

Documentación interactiva: [http://localhost:8443/docs](http://localhost:8443/docs)

---

## Variables de entorno

Copiar `.env.example` → `.env` y ajustar si es necesario.

| Variable | Default | Descripción |
|---|---|---|
| `CONNECT_DATABASE` | `false` | `true` para activar PostgreSQL real |
| `DATABASE_URL` | `postgresql+psycopg://nexotlab:nexotlab@localhost:5432/nexotlab` | Cadena de conexión |
| `HIGH_SCORE_THRESHOLD` | `4.0` | Umbral alto de score |
| `LOW_SCORE_THRESHOLD` | `2.5` | Umbral bajo de score |
| `RANDOM_SEED` | `42` | Semilla reproducibilidad |
| `CORS_ORIGINS` | `http://localhost:5173,...` | Orígenes permitidos (separados por coma) |

Con `CONNECT_DATABASE=false` (default), toda la plataforma usa datos en memoria y los módulos de simulación/minería usan el dataset sintético calibrado.

---

## Endpoints

### Salud
| Método | Ruta | Descripción |
|---|---|---|
| GET | `/api/v1/health` | Estado del sistema, thresholds, enums disponibles |

### Plataforma

| Método | Ruta | Descripción |
|---|---|---|
| POST | `/api/v1/platform/auth/login` | Login stub (email → perfil de usuario) |
| GET | `/api/v1/platform/users` | Listar usuarios (filtros: profile_type, sector, active) |
| GET | `/api/v1/platform/users/{id}` | Obtener usuario |
| POST | `/api/v1/platform/users` | Crear usuario |
| PATCH | `/api/v1/platform/users/{id}/toggle-active` | Activar/desactivar usuario |
| GET | `/api/v1/platform/proposals` | Listar propuestas (filtros: category, sector, status, min_score) |
| GET | `/api/v1/platform/proposals/{id}` | Obtener propuesta |
| POST | `/api/v1/platform/proposals` | Crear propuesta |
| PATCH | `/api/v1/platform/proposals/{id}` | Actualizar propuesta |
| DELETE | `/api/v1/platform/proposals/{id}` | Eliminar propuesta (autor o admin) |
| GET | `/api/v1/platform/proposals/{id}/evaluations` | Historial de evaluaciones |
| GET | `/api/v1/platform/proposals/{id}/comments` | Comentarios de propuesta |
| POST | `/api/v1/platform/evaluations` | Registrar evaluación (actualiza score automáticamente) |
| POST | `/api/v1/platform/comments` | Agregar comentario |
| POST | `/api/v1/platform/collaborators/apply` | Postularse como colaborador |
| PATCH | `/api/v1/platform/collaborators/{pid}/{uid}/accept` | Aceptar colaborador |
| PATCH | `/api/v1/platform/collaborators/{pid}/{uid}/reject` | Rechazar colaborador |
| GET | `/api/v1/platform/notifications` | Listar notificaciones (filtro user_id, unread_only) |
| PATCH | `/api/v1/platform/notifications/{id}/read` | Marcar notificación como leída |
| PATCH | `/api/v1/platform/notifications/read-all` | Marcar todas como leídas |
| GET | `/api/v1/platform/stats` | Estadísticas públicas de la plataforma |
| GET | `/api/v1/platform/admin/overview` | Panel de administración con métricas |
| GET | `/api/v1/platform/admin/reports` | Reportes de contenido |
| POST | `/api/v1/platform/admin/reports` | Crear reporte de contenido |
| PATCH | `/api/v1/platform/admin/reports/{id}/dismiss` | Desestimar reporte (admin) |
| POST | `/api/v1/platform/admin/reset-store` | Reiniciar store (solo desarrollo, admin) |

---

### Asignatura 1 – Modelado y Simulación

| Método | Ruta | Aporte | Entregable |
|---|---|---|---|
| POST/GET | `/api/v1/simulation/scenarios` | 1 | Modelo funcional: eventos discretos + Monte Carlo |
| GET | `/api/v1/simulation/validation` | 2 | Documento técnico de validación del modelo |
| GET | `/api/v1/simulation/optimization?n_evaluators=10&n_proposals=28` | 3 | Informe de optimización de evaluadores y flujos |
| GET | `/api/v1/simulation/external-variables` | 4 | Informe de variables externas y su impacto |
| GET | `/api/v1/simulation/recommendations` | 5 | Recomendaciones estratégicas de arquitectura |

**POST `/api/v1/simulation/scenarios`** acepta body JSON con overrides opcionales:
```json
{
  "horizon_days": 90,
  "users_per_day": 3.2,
  "evaluators": 12,
  "monte_carlo_runs": 250,
  "proposals_per_active_user_year": 1.4,
  "review_hours_mean": 4.5
}
```

---

### Asignatura 2 – Minería de Datos

| Método | Ruta | Aporte | Entregable |
|---|---|---|---|
| GET | `/api/v1/mining/patterns` | 1 | Patrones de comportamiento y tendencias de innovación |
| POST | `/api/v1/mining/predictive/train` | 2 | Entrena árbol de decisión, regresión logística y lineal |
| POST | `/api/v1/mining/predictive/predict` | 2 | Predice viabilidad de una propuesta nueva |
| GET | `/api/v1/mining/predictive/models` | 2 | Inspecciona modelos entrenados |
| GET | `/api/v1/mining/segmentation` | 3 | Segmentación k-means de usuarios y propuestas |
| GET | `/api/v1/mining/cleaning` | 4 | Limpieza, transformación e integración de datos |
| GET | `/api/v1/mining/association?min_support=0.08&min_confidence=0.45` | 5 | Reglas de asociación (Apriori) |

**POST `/api/v1/mining/predictive/predict`** acepta:
```json
{
  "category": "digital-transformation",
  "sector": "agro",
  "author_profile": "entrepreneur",
  "evaluations_count": 12,
  "team_size": 2,
  "accepted_collaborators": 1,
  "description_length": 350
}
```

---

## Estructura del proyecto

```
backend/
├── app/
│   ├── main.py               # FastAPI app + lifespan
│   ├── config.py             # Settings (pydantic-settings)
│   ├── api/
│   │   ├── router.py         # Router raíz /api/v1
│   │   └── routes/
│   │       ├── health.py     # GET /health
│   │       ├── platform.py   # Plataforma completa (CRUD + admin)
│   │       ├── simulation.py # 5 aportes Modelado y Simulación
│   │       └── mining.py     # 5 aportes Minería de Datos
│   ├── data/
│   │   └── catalog.py        # Dataset sintético + MemoryStore
│   ├── db/
│   │   ├── base.py           # DeclarativeBase
│   │   ├── models.py         # ORM SQLAlchemy (listo para PostgreSQL)
│   │   ├── session.py        # Engine/SessionLocal condicional
│   │   └── create_schema.py  # python -m app.db.create_schema
│   ├── domain/
│   │   └── enums.py          # StrEnum: ProfileType, Sector, Category, Status
│   ├── simulation/
│   │   ├── scenarios.py      # Aporte 1: DES + Monte Carlo
│   │   ├── validation.py     # Aporte 2: MAPE + recalibración
│   │   ├── optimization.py   # Aporte 3: Hungarian + políticas
│   │   ├── external.py       # Aporte 4: escenarios de estrés
│   │   └── recommendations.py# Aporte 5: recomendaciones estratégicas
│   └── mining/
│       ├── cleaning.py       # Aporte 4: limpieza e integración
│       ├── patterns.py       # Aporte 1: patrones y tendencias
│       ├── predictive.py     # Aporte 2: árbol/logit/regresión
│       ├── segmentation.py   # Aporte 3: k-means silhouette
│       └── association.py    # Aporte 5: Apriori
├── sql/
│   ├── 001_create_schema.sql # DDL PostgreSQL
│   └── 002_seed_platform.sql # Datos iniciales
├── artifacts/                # Modelos ML serializados (joblib)
├── requirements.txt
├── .env                      # Variables de entorno
└── .env.example
```

---

## Activar PostgreSQL (opcional)

1. Crear base de datos: `createdb nexotlab`
2. En `.env`: `CONNECT_DATABASE=true`
3. Crear tablas: `python -m app.db.create_schema`
   — o ejecutar `sql/001_create_schema.sql` directamente.

---

## Dataset sintético

El catálogo en memoria (`app/data/catalog.py`) incluye:
- **11 usuarios semilla** (admin, entrepreneurs, researchers, companies, citizens)
- **4 propuestas semilla** calibradas con el frontend
- **220 usuarios sintéticos** generados deterministicamente (seed=42)
- **160 propuestas sintéticas** con evaluaciones, colaboradores y comentarios

Este dataset alimenta todos los módulos de minería sin necesidad de PostgreSQL.
