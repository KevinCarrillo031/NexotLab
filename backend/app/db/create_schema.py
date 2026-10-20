"""Crea tablas en MySQL/MariaDB y siembra datos iniciales.

Uso:
    cd backend
    python -m app.db.create_schema
    # o con datos semilla:
    python -m app.db.create_schema --seed
"""

from __future__ import annotations

import argparse
import sys
import uuid
from datetime import date


def create_all_tables() -> None:
    from app.config import settings
    from app.db.base import Base
    from app.db.session import engine

    if not settings.connect_database or engine is None:
        raise RuntimeError(
            "CONNECT_DATABASE está deshabilitado. "
            "Asegúrese de que .env tenga CONNECT_DATABASE=true y DATABASE_URL configurado."
        )

    from app.db import models  # noqa: F401 — registra metadatos ORM

    print(f"Creando tablas en: {settings.database_url.split('@')[-1]} ...")
    Base.metadata.create_all(bind=engine)
    print("Tablas creadas:")
    for table in sorted(Base.metadata.tables.keys()):
        print(f"  ✓ {table}")


def seed_data() -> None:
    from app.data.catalog import SEED_PROPOSALS, SEED_USERS
    from app.db.models import (
        Collaborator,
        Comment,
        Evaluation,
        Notification,
        Proposal,
        User,
        WeeklyScore,
    )
    from app.db.session import SessionLocal

    if SessionLocal is None:
        raise RuntimeError("SessionLocal no está inicializado.")

    db = SessionLocal()
    try:
        # Verificar si ya hay datos
        if db.query(User).count() > 0:
            print("La base ya tiene datos — se omite el seed para no duplicar.")
            return

        print("Sembrando usuarios ...")
        for raw in SEED_USERS:
            user = User(
                id=raw["id"],
                name=raw["name"],
                email=raw["email"],
                profile_type=raw["profile_type"],
                sector=raw.get("sector"),
                is_admin=raw.get("is_admin", False),
                active=raw.get("active", True),
                joined_at=date.fromisoformat(raw["joined_at"]),
            )
            db.merge(user)
        db.flush()

        print("Sembrando propuestas ...")
        for raw in SEED_PROPOSALS:
            proposal = Proposal(
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
                created_at=date.fromisoformat(raw["created_at"]),
            )
            db.merge(proposal)
        db.flush()

        print("Sembrando scores semanales ...")
        for raw in SEED_PROPOSALS:
            for week_idx, score in enumerate(raw["weekly_scores"]):
                ws = WeeklyScore(
                    proposal_id=raw["id"],
                    week_index=week_idx,
                    score=score,
                    recorded_at=date.fromisoformat(raw["created_at"]),
                )
                db.add(ws)
        db.flush()

        print("Sembrando colaboradores ...")
        for raw in SEED_PROPOSALS:
            for collab in raw.get("collaborators", []):
                c = Collaborator(
                    proposal_id=raw["id"],
                    user_id=collab["user_id"],
                    status=collab["status"],
                    applied_at=date.fromisoformat(collab["applied_at"]),
                )
                db.add(c)
        db.flush()

        print("Sembrando notificaciones ...")
        notifications = [
            {
                "id": "n1",
                "user_id": "user1",
                "type": "positive",
                "message": "Tu propuesta superó el umbral alto esta semana con un score de 4.7.",
                "proposal_title": "Sistema de trazabilidad agrícola con blockchain",
                "date": "2026-09-08",
                "read": False,
            },
            {
                "id": "n2",
                "user_id": "user1",
                "type": "social",
                "message": "Sofía Vargas se postuló como colaboradora en tu propuesta.",
                "proposal_title": "Sistema de trazabilidad agrícola con blockchain",
                "date": "2026-09-01",
                "read": False,
            },
            {
                "id": "n3",
                "user_id": "u3",
                "type": "improvement",
                "message": "Tu propuesta no alcanzó el umbral mínimo esta semana.",
                "proposal_title": "Asistente de IA para diagnóstico de suelos colombianos",
                "date": "2026-09-01",
                "read": True,
            },
        ]
        for n in notifications:
            notif = Notification(
                id=n["id"],
                user_id=n.get("user_id"),
                type=n["type"],
                message=n["message"],
                proposal_title=n.get("proposal_title"),
                date=date.fromisoformat(n["date"]),
                read=n.get("read", False),
            )
            db.merge(notif)

        db.commit()
        print("Seed completado.")

    except Exception:
        db.rollback()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Crea tablas y siembra datos en MySQL/MariaDB.")
    parser.add_argument("--seed", action="store_true", help="Sembrar datos iniciales tras crear tablas")
    args = parser.parse_args()

    try:
        create_all_tables()
        if args.seed:
            seed_data()
        print("\nListo. Verifique las tablas en phpMyAdmin: http://localhost/phpmyadmin")
    except Exception as e:
        print(f"\nError: {e}")
        sys.exit(1)
