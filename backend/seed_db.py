r"""
seed_db.py — Puebla la base de datos MySQL con los datos del catálogo expandido.

Uso:
    cd C:/PROYECTODECIMO/NexotLab/backend
    .venv/Scripts/python.exe seed_db.py

El script:
  1. Limpia todas las tablas relevantes (en orden para respetar FKs)
  2. Inserta los SEED_USERS (30) y SEED_PROPOSALS (25) con sus colaboradores y scores
  3. Inserta los datos sintéticos del generador (500 usuarios / 350 propuestas)
  4. Inserta notificaciones seed
"""

from __future__ import annotations

import hashlib
import sys
import os
from datetime import date
from pathlib import Path

# Añadir el directorio backend al path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import settings

if not settings.connect_database:
    print("ERROR: CONNECT_DATABASE=false en .env — actívalo primero.")
    sys.exit(1)

from app.db.session import engine, SessionLocal
from app.db.models import (
    User, Proposal, WeeklyScore, Collaborator,
    Evaluation, Comment, Notification, ContentReport,
    SimulationRun, MiningRun
)
from app.db.base import Base
from app.data.catalog import SEED_USERS, SEED_PROPOSALS, build_synthetic_frames

import numpy as np

DEFAULT_PASSWORD_HASH = hashlib.sha256(b"nexotlab123").hexdigest()

def hash_pw(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()

def parse_date(s: str) -> date:
    return date.fromisoformat(s)

def main() -> None:
    print("Conectando a la base de datos...")
    
    # Crear tablas si no existen
    Base.metadata.create_all(bind=engine)
    
    db = SessionLocal()
    try:
        print("Limpiando tablas existentes...")
        # Orden inverso de dependencias FK
        db.query(Comment).delete()
        db.query(Evaluation).delete()
        db.query(WeeklyScore).delete()
        db.query(Collaborator).delete()
        db.query(Notification).delete()
        db.query(Proposal).delete()
        db.query(User).delete()
        db.commit()
        print("  Tablas limpias.")

        # ── 1. Insertar usuarios seed ─────────────────────────────────────────
        print(f"Insertando {len(SEED_USERS)} usuarios seed...")
        user_map: dict[str, User] = {}
        for raw in SEED_USERS:
            u = User(
                id=raw["id"],
                name=raw["name"],
                email=raw["email"],
                password_hash=DEFAULT_PASSWORD_HASH,
                profile_type=raw["profile_type"],
                sector=raw["sector"],
                is_admin=raw["is_admin"],
                active=raw["active"],
                joined_at=parse_date(raw["joined_at"]),
            )
            db.add(u)
            user_map[raw["id"]] = u
        db.flush()

        # ── 2. Insertar propuestas seed con scores y colaboradores ────────────
        print(f"Insertando {len(SEED_PROPOSALS)} propuestas seed...")
        for raw in SEED_PROPOSALS:
            p = Proposal(
                id=raw["id"],
                title=raw["title"],
                category=raw["category"],
                sector=raw["sector"],
                description=raw["description"],
                deliverable=raw["deliverable"],
                author_id=raw["author_id"],
                status=raw["status"],
                current_score=raw["current_score"],
                evaluations_count=raw["evaluations_count"],
                created_at=parse_date(raw["created_at"]),
            )
            db.add(p)
            db.flush()

            for i, score in enumerate(raw["weekly_scores"]):
                db.add(WeeklyScore(
                    proposal_id=raw["id"],
                    week_index=i,
                    score=score,
                    recorded_at=parse_date(raw["created_at"]),
                ))

            for item in raw["collaborators"]:
                if item["user_id"] in user_map:
                    db.add(Collaborator(
                        proposal_id=raw["id"],
                        user_id=item["user_id"],
                        status=item["status"],
                        applied_at=parse_date(item["applied_at"]),
                    ))
        db.flush()

        # ── 3. Datos sintéticos ───────────────────────────────────────────────
        print("Generando dataset sintético (500 usuarios / 350 propuestas)...")
        frames = build_synthetic_frames(n_users=500, n_proposals=350)

        users_df     = frames["users"]
        proposals_df = frames["proposals"]
        collab_df    = frames["collaborators"]
        evals_df     = frames["evaluations"]
        comments_df  = frames["comments"]

        # Filtrar solo los sintéticos (no los seeds que ya están)
        seed_user_ids = {u["id"] for u in SEED_USERS}
        seed_prop_ids = {p["id"] for p in SEED_PROPOSALS}

        synth_users = users_df[~users_df["id"].isin(seed_user_ids)]
        synth_props = proposals_df[~proposals_df["id"].isin(seed_prop_ids)]

        print(f"  Insertando {len(synth_users)} usuarios sintéticos...")
        for _, row in synth_users.iterrows():
            u = User(
                id=str(row["id"]),
                name=str(row["name"]),
                email=str(row["email"]),
                password_hash=DEFAULT_PASSWORD_HASH,
                profile_type=str(row["profile_type"]),
                sector=str(row["sector"]),
                is_admin=bool(row["is_admin"]),
                active=bool(row["active"]),
                joined_at=parse_date(str(row["joined_at"])),
            )
            db.add(u)

        db.flush()

        print(f"  Insertando {len(synth_props)} propuestas sintéticas...")
        for _, row in synth_props.iterrows():
            p = Proposal(
                id=str(row["id"]),
                title=str(row["title"]),
                category=str(row["category"]),
                sector=str(row["sector"]),
                description=str(row["description"]),
                deliverable=str(row["deliverable"]),
                author_id=str(row["author_id"]),
                status=str(row["status"]),
                current_score=float(row["current_score"]),
                evaluations_count=int(row["evaluations_count"]),
                created_at=parse_date(str(row["created_at"])),
            )
            db.add(p)
            db.flush()

            scores = row["weekly_scores"]
            if isinstance(scores, list):
                for i, sc in enumerate(scores):
                    db.add(WeeklyScore(
                        proposal_id=str(row["id"]),
                        week_index=i,
                        score=float(sc),
                        recorded_at=parse_date(str(row["created_at"])),
                    ))

        db.flush()

        # Colaboradores sintéticos
        print(f"  Insertando {len(collab_df)} colaboraciones sintéticas...")
        inserted_collabs = 0
        for _, row in collab_df.iterrows():
            pid = str(row["proposal_id"])
            uid = str(row["user_id"])
            if pid in seed_prop_ids:
                continue  # los seed ya están
            try:
                db.add(Collaborator(
                    proposal_id=pid,
                    user_id=uid,
                    status=str(row["status"]),
                    applied_at=parse_date(str(row["applied_at"])),
                ))
                inserted_collabs += 1
            except Exception:
                db.rollback()
        db.flush()
        print(f"    {inserted_collabs} colaboraciones insertadas.")

        # Evaluaciones sintéticas
        print(f"  Insertando {len(evals_df)} evaluaciones sintéticas...")
        for _, row in evals_df.iterrows():
            pid = str(row["proposal_id"])
            if pid in seed_prop_ids:
                continue
            db.add(Evaluation(
                id=str(row["id"]),
                proposal_id=pid,
                evaluator_id=str(row["evaluator_id"]),
                viability=float(row["viability"]),
                innovation=float(row["innovation"]),
                impact=float(row["impact"]),
                clarity=float(row["clarity"]),
                score=float(row["score"]),
                created_at=parse_date(str(row["created_at"])),
            ))
        db.flush()

        # Comentarios sintéticos
        print(f"  Insertando {len(comments_df)} comentarios sintéticos...")
        for _, row in comments_df.iterrows():
            pid = str(row["proposal_id"])
            if pid in seed_prop_ids:
                continue
            db.add(Comment(
                id=str(row["id"]),
                proposal_id=pid,
                user_id=str(row["user_id"]),
                body=str(row["body"]),
                created_at=parse_date(str(row["created_at"])),
            ))
        db.flush()

        # ── 4. Notificaciones seed ────────────────────────────────────────────
        NOTIFS = [
            ("n1",  "user1",  "positive",   "Tu propuesta superó el umbral alto esta semana con score 4.7.",                       "Sistema de trazabilidad agrícola con blockchain",         "2026-09-08", False),
            ("n2",  "user1",  "social",     "Andrés Peña se postuló como colaborador en tu propuesta.",                            "Sistema de trazabilidad agrícola con blockchain",         "2026-09-01", False),
            ("n3",  "u3",     "improvement","Tu propuesta no alcanzó el umbral mínimo esta semana. Revisa los criterios.",          "Asistente de IA para diagnóstico de suelos colombianos",  "2026-09-01", True),
            ("n4",  "u6",     "positive",   "¡Felicitaciones! Tu propuesta es la mejor calificada de la semana con 4.8.",           "Hub de energía solar comunitaria descentralizada",        "2026-09-08", False),
            ("n5",  "user1",  "social",     "AgroDigital Ltda. se unió como colaboradora en tu propuesta.",                        "Sistema de trazabilidad agrícola con blockchain",         "2026-08-25", True),
            ("n6",  "u11",    "social",     "Valentina Cruz se postuló como colaboradora en tu propuesta.",                        "Sistema de microcréditos algorítmicos para emprendedores","2026-09-05", False),
            ("n7",  "u12",    "positive",   "Tu propuesta alcanzó 52 evaluaciones, un récord en la plataforma.",                   "Plataforma de telemedicina rural con IA predictiva",      "2026-09-10", True),
            ("n8",  "u27",    "improvement","Tu propuesta bajó al umbral de mejora. Considera revisar la propuesta de valor.",      "Marketplace de carbono para pequeños productores",        "2026-09-15", False),
            ("n9",  "u11",    "social",     "Luis Bermúdez aceptó tu invitación para colaborar.",                                  "Sistema de microcréditos algorítmicos para emprendedores","2026-09-08", True),
            ("n10", "u9",     "positive",   "Tu propuesta fue destacada en el informe semanal de innovación.",                     "Fintech de ahorro programado para trabajadores informales","2026-09-09", False),
            ("n11", "u16",    "social",     "Cristina Velásquez se postuló como colaboradora.",                                    "Red de intercambio de conocimiento entre investigadores", "2026-09-01", True),
            ("n12", "u14",    "improvement","La propuesta necesita mejoras en el criterio de innovación.",                         "Plataforma de economía circular para residuos industriales","2026-09-12",False),
        ]
        print(f"Insertando {len(NOTIFS)} notificaciones seed...")
        for nid, uid, ntype, msg, ptitle, ndate, read in NOTIFS:
            db.add(Notification(
                id=nid,
                user_id=uid,
                type=ntype,
                message=msg,
                proposal_title=ptitle,
                date=parse_date(ndate),
                read=read,
            ))

        db.commit()

        # ── Resumen final ──────────────────────────────────────────────────────
        total_users     = db.query(User).count()
        total_proposals = db.query(Proposal).count()
        total_collabs   = db.query(Collaborator).count()
        total_evals     = db.query(Evaluation).count()
        total_comments  = db.query(Comment).count()
        total_notifs    = db.query(Notification).count()

        print("\n=== SEEDING COMPLETADO ===")
        print(f"  Usuarios:       {total_users}")
        print(f"  Propuestas:     {total_proposals}")
        print(f"  Colaboraciones: {total_collabs}")
        print(f"  Evaluaciones:   {total_evals}")
        print(f"  Comentarios:    {total_comments}")
        print(f"  Notificaciones: {total_notifs}")
        print("\nReinicia el servidor FastAPI para reflejar los cambios.")

    except Exception as e:
        db.rollback()
        print(f"\nERROR: {e}")
        import traceback; traceback.print_exc()
        sys.exit(1)
    finally:
        db.close()


if __name__ == "__main__":
    main()
