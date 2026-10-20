"""Rutas de plataforma — todos los datos vienen de MySQL via SQLAlchemy ORM."""

from __future__ import annotations

import hashlib
import json
import uuid
from datetime import date
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from app.config import settings
from app.db.models import (
    Collaborator,
    Comment,
    Evaluation,
    Notification,
    Proposal,
    User,
    WeeklyScore,
    ContentReport,
)
from app.db.session import get_db
from app.domain.enums import (
    CollaboratorStatus,
    ProfileType,
    ProposalCategory,
    ProposalStatus,
    Sector,
)

router = APIRouter()


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _today() -> date:
    return date.today()


def _new_id() -> str:
    return str(uuid.uuid4())


def _status_from_score(score: float) -> str:
    if score >= settings.high_score_threshold:
        return ProposalStatus.GOOD
    if score < settings.low_score_threshold:
        return ProposalStatus.NEEDS_IMPROVEMENT
    return ProposalStatus.EVALUATING


def _require_db(db: Session | None) -> Session:
    if db is None:
        raise HTTPException(
            status_code=503,
            detail="Base de datos no disponible. Verifique CONNECT_DATABASE=true en .env y que MySQL esté corriendo.",
        )
    return db


def _proposal_to_dict(p: Proposal, db: Session) -> dict[str, Any]:
    collabs = db.query(Collaborator).filter(Collaborator.proposal_id == p.id).all()
    collab_list = []
    for c in collabs:
        member = db.query(User).filter(User.id == c.user_id).first()
        if member:
            collab_list.append({
                "id": member.id,
                "name": member.name,
                "profileType": member.profile_type,
                "status": c.status,
                "appliedAt": c.applied_at.isoformat() if c.applied_at else None,
            })
    scores = (
        db.query(WeeklyScore)
        .filter(WeeklyScore.proposal_id == p.id)
        .order_by(WeeklyScore.week_index)
        .all()
    )
    author = db.query(User).filter(User.id == p.author_id).first()
    return {
        "id": p.id,
        "title": p.title,
        "category": p.category,
        "sector": p.sector,
        "description": p.description,
        "deliverable": p.deliverable,
        "authorId": p.author_id,
        "authorName": author.name if author else "",
        "authorProfile": author.profile_type if author else "",
        "status": p.status,
        "weeklyScores": [ws.score for ws in scores],
        "currentScore": p.current_score,
        "collaborators": collab_list,
        "createdAt": p.created_at.isoformat() if p.created_at else None,
        "evaluationsCount": p.evaluations_count,
    }


def _user_to_dict(u: User, db: Session) -> dict[str, Any]:
    count = db.query(Proposal).filter(Proposal.author_id == u.id).count()
    return {
        "id": u.id,
        "name": u.name,
        "email": u.email,
        "profile_type": u.profile_type,
        "sector": u.sector,
        "is_admin": u.is_admin,
        "active": u.active,
        "joined_at": u.joined_at.isoformat() if u.joined_at else None,
        "proposals_count": count,
    }


def _notif_to_dict(n: Notification) -> dict[str, Any]:
    return {
        "id": n.id,
        "userId": n.user_id,
        "type": n.type,
        "message": n.message,
        "proposalTitle": n.proposal_title,
        "date": n.date.isoformat() if n.date else None,
        "read": n.read,
    }


# ---------------------------------------------------------------------------
# AUTH
# ---------------------------------------------------------------------------

class LoginIn(BaseModel):
    email: str
    password: str = ""


def _hash_password(password: str) -> str:
    """SHA-256 simple sin dependencias externas."""
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


def _check_password(password: str, stored_hash: str | None) -> bool:
    if stored_hash is None:
        # Usuario sin hash asignado: acepta cualquier contraseña
        return True
    return _hash_password(password) == stored_hash


@router.post("/auth/login", summary="Login (valida email y contraseña en BD)")
def login(body: LoginIn, db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    user = db.query(User).filter(User.email == body.email.lower().strip()).first()
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    if not user.active:
        raise HTTPException(status_code=403, detail="Cuenta desactivada")
    if not _check_password(body.password, user.password_hash):
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    # Si el usuario no tenía hash, lo guardamos ahora
    if user.password_hash is None and body.password:
        user.password_hash = _hash_password(body.password)
        db.commit()
    return {
        "authenticated": True,
        "user": _user_to_dict(user, db),
        "token": "stub-token-" + user.id,
    }


# ---------------------------------------------------------------------------
# USUARIOS
# ---------------------------------------------------------------------------

class UserCreateIn(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    email: str = Field(min_length=5, max_length=180)
    profile_type: ProfileType
    sector: Sector = Sector.GOVERNMENT
    is_admin: bool = False
    password: str = "nexotlab123"


@router.get("/users", summary="Listar usuarios")
def list_users(
    profile_type: str | None = Query(default=None),
    sector: str | None = Query(default=None),
    active: bool | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> dict:
    db = _require_db(db)
    q = db.query(User)
    if profile_type:
        q = q.filter(User.profile_type == profile_type)
    if sector:
        q = q.filter(User.sector == sector)
    if active is not None:
        q = q.filter(User.active == active)
    total = q.count()
    users = q.offset(skip).limit(limit).all()
    return {
        "source": "mysql",
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [_user_to_dict(u, db) for u in users],
    }


@router.get("/users/{user_id}", summary="Obtener usuario por ID")
def get_user(user_id: str, db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return _user_to_dict(user, db)


@router.post("/users", status_code=201, summary="Crear usuario")
def create_user(body: UserCreateIn, db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    if db.query(User).filter(User.email == body.email.lower().strip()).first():
        raise HTTPException(status_code=409, detail="El email ya está registrado")
    user = User(
        id=_new_id(),
        name=body.name,
        email=body.email.lower().strip(),
        password_hash=_hash_password(body.password),
        profile_type=body.profile_type,
        sector=body.sector,
        is_admin=body.is_admin,
        active=True,
        joined_at=_today(),
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return _user_to_dict(user, db)


@router.patch("/users/{user_id}/toggle-active", summary="Activar/desactivar usuario")
def toggle_user_active(user_id: str, db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if user.is_admin:
        raise HTTPException(status_code=403, detail="No se puede desactivar un administrador")
    user.active = not user.active
    db.commit()
    return {"user_id": user_id, "active": user.active}


# ---------------------------------------------------------------------------
# PROPUESTAS
# ---------------------------------------------------------------------------

class ProposalCreateIn(BaseModel):
    title: str = Field(min_length=4, max_length=240)
    category: ProposalCategory
    sector: Sector
    description: str = Field(min_length=20)
    deliverable: str = Field(min_length=10)
    author_id: str


class ProposalPatchIn(BaseModel):
    title: str | None = Field(default=None, min_length=4, max_length=240)
    description: str | None = Field(default=None, min_length=20)
    deliverable: str | None = Field(default=None, min_length=10)
    status: ProposalStatus | None = None


@router.get("/proposals", summary="Listar propuestas")
def list_proposals(
    category: str | None = Query(default=None),
    sector: str | None = Query(default=None),
    status: str | None = Query(default=None),
    author_id: str | None = Query(default=None),
    min_score: float | None = Query(default=None, ge=0, le=5),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=1000),
    db: Session = Depends(get_db),
) -> dict:
    db = _require_db(db)
    q = db.query(Proposal)
    if category:
        q = q.filter(Proposal.category == category)
    if sector:
        q = q.filter(Proposal.sector == sector)
    if status:
        q = q.filter(Proposal.status == status)
    if author_id:
        q = q.filter(Proposal.author_id == author_id)
    if min_score is not None:
        q = q.filter(Proposal.current_score >= min_score)
    total = q.count()
    proposals = q.order_by(Proposal.created_at.desc()).offset(skip).limit(limit).all()
    return {
        "source": "mysql",
        "total": total,
        "skip": skip,
        "limit": limit,
        "items": [_proposal_to_dict(p, db) for p in proposals],
    }


@router.get("/proposals/{proposal_id}", summary="Obtener propuesta por ID")
def get_proposal(proposal_id: str, db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    p = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    return _proposal_to_dict(p, db)


@router.post("/proposals", status_code=201, summary="Crear propuesta")
def create_proposal(body: ProposalCreateIn, db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    author = db.query(User).filter(User.id == body.author_id).first()
    if not author:
        raise HTTPException(status_code=404, detail="Autor no encontrado")
    if not author.active:
        raise HTTPException(status_code=403, detail="Usuario inactivo no puede publicar propuestas")
    proposal = Proposal(
        id=_new_id(),
        title=body.title,
        category=body.category,
        sector=body.sector,
        description=body.description,
        deliverable=body.deliverable,
        author_id=body.author_id,
        status=ProposalStatus.EVALUATING,
        current_score=0.0,
        evaluations_count=0,
        created_at=_today(),
    )
    db.add(proposal)
    db.commit()
    db.refresh(proposal)
    return _proposal_to_dict(proposal, db)


@router.patch("/proposals/{proposal_id}", summary="Actualizar propuesta")
def patch_proposal(proposal_id: str, body: ProposalPatchIn, db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    p = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    if body.title is not None:
        p.title = body.title
    if body.description is not None:
        p.description = body.description
    if body.deliverable is not None:
        p.deliverable = body.deliverable
    if body.status is not None:
        p.status = body.status
    db.commit()
    return _proposal_to_dict(p, db)


@router.delete("/proposals/{proposal_id}", summary="Eliminar propuesta")
def delete_proposal(
    proposal_id: str,
    requesting_user_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict:
    db = _require_db(db)
    p = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    user = db.query(User).filter(User.id == requesting_user_id).first()
    if not user or (not user.is_admin and p.author_id != requesting_user_id):
        raise HTTPException(status_code=403, detail="Sin permiso para eliminar esta propuesta")
    db.delete(p)
    db.commit()
    return {"deleted": True, "proposal_id": proposal_id}


# ---------------------------------------------------------------------------
# EVALUACIONES
# ---------------------------------------------------------------------------

class EvaluationIn(BaseModel):
    proposal_id: str
    evaluator_id: str
    viability: float = Field(ge=1, le=5)
    innovation: float = Field(ge=1, le=5)
    impact: float = Field(ge=1, le=5)
    clarity: float = Field(ge=1, le=5)


@router.post("/evaluations", status_code=201, summary="Registrar evaluación")
def create_evaluation(body: EvaluationIn, db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    proposal = db.query(Proposal).filter(Proposal.id == body.proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    evaluator = db.query(User).filter(User.id == body.evaluator_id).first()
    if not evaluator:
        raise HTTPException(status_code=404, detail="Evaluador no encontrado")
    if proposal.author_id == body.evaluator_id:
        raise HTTPException(status_code=409, detail="El autor no puede evaluar su propia propuesta")

    score = round((body.viability + body.innovation + body.impact + body.clarity) / 4, 2)
    evaluation = Evaluation(
        id=_new_id(),
        proposal_id=body.proposal_id,
        evaluator_id=body.evaluator_id,
        viability=body.viability,
        innovation=body.innovation,
        impact=body.impact,
        clarity=body.clarity,
        score=score,
        created_at=_today(),
    )
    db.add(evaluation)

    # Actualizar score de la propuesta (media incremental)
    n = proposal.evaluations_count
    new_score = round((proposal.current_score * n + score) / (n + 1), 2)
    proposal.evaluations_count = n + 1
    proposal.current_score = new_score
    proposal.status = _status_from_score(new_score)

    # Score semanal
    week_index = n  # cada evaluación = semana consecutiva para el gráfico
    ws = WeeklyScore(
        proposal_id=body.proposal_id,
        week_index=week_index,
        score=new_score,
        recorded_at=_today(),
    )
    db.add(ws)

    # Notificación al autor
    notif = Notification(
        id=_new_id(),
        user_id=proposal.author_id,
        type="positive" if new_score >= settings.high_score_threshold else "improvement",
        message=f"Tu propuesta recibió una evaluación (score {score}). Score actual: {new_score}.",
        proposal_title=proposal.title,
        date=_today(),
        read=False,
    )
    db.add(notif)
    db.commit()

    return {
        "evaluation_id": evaluation.id,
        "score": score,
        "updated_proposal_score": new_score,
        "new_status": proposal.status,
    }


@router.get("/proposals/{proposal_id}/evaluations", summary="Evaluaciones de una propuesta")
def get_proposal_evaluations(proposal_id: str, db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    p = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not p:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    evals = (
        db.query(Evaluation)
        .filter(Evaluation.proposal_id == proposal_id)
        .order_by(Evaluation.created_at)
        .all()
    )
    scores = (
        db.query(WeeklyScore)
        .filter(WeeklyScore.proposal_id == proposal_id)
        .order_by(WeeklyScore.week_index)
        .all()
    )
    return {
        "proposal_id": proposal_id,
        "evaluations_count": p.evaluations_count,
        "current_score": p.current_score,
        "weekly_scores": [ws.score for ws in scores],
        "status": p.status,
        "evaluations": [
            {
                "id": e.id,
                "evaluator_id": e.evaluator_id,
                "viability": e.viability,
                "innovation": e.innovation,
                "impact": e.impact,
                "clarity": e.clarity,
                "score": e.score,
                "created_at": e.created_at.isoformat() if e.created_at else None,
            }
            for e in evals
        ],
    }


# ---------------------------------------------------------------------------
# COMENTARIOS
# ---------------------------------------------------------------------------

class CommentIn(BaseModel):
    proposal_id: str
    user_id: str
    body: str = Field(min_length=3, max_length=2000)


@router.post("/comments", status_code=201, summary="Agregar comentario")
def create_comment(body: CommentIn, db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    if not db.query(Proposal).filter(Proposal.id == body.proposal_id).first():
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    user = db.query(User).filter(User.id == body.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    comment = Comment(
        id=_new_id(),
        proposal_id=body.proposal_id,
        user_id=body.user_id,
        body=body.body,
        created_at=_today(),
    )
    db.add(comment)
    db.commit()
    return {
        "id": comment.id,
        "proposalId": comment.proposal_id,
        "userId": comment.user_id,
        "userName": user.name,
        "body": comment.body,
        "createdAt": comment.created_at.isoformat(),
    }


@router.get("/proposals/{proposal_id}/comments", summary="Comentarios de una propuesta")
def get_proposal_comments(proposal_id: str, db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    if not db.query(Proposal).filter(Proposal.id == proposal_id).first():
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    comments = (
        db.query(Comment)
        .filter(Comment.proposal_id == proposal_id)
        .order_by(Comment.created_at.desc())
        .all()
    )
    result = []
    for c in comments:
        u = db.query(User).filter(User.id == c.user_id).first()
        result.append({
            "id": c.id,
            "userId": c.user_id,
            "userName": u.name if u else "",
            "body": c.body,
            "createdAt": c.created_at.isoformat() if c.created_at else None,
        })
    return {"proposal_id": proposal_id, "comments": result}


# ---------------------------------------------------------------------------
# COLABORADORES
# ---------------------------------------------------------------------------

class CollaboratorApplyIn(BaseModel):
    proposal_id: str
    user_id: str


@router.post("/collaborators/apply", status_code=201, summary="Postularse como colaborador")
def apply_collaborator(body: CollaboratorApplyIn, db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    proposal = db.query(Proposal).filter(Proposal.id == body.proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    user = db.query(User).filter(User.id == body.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    if proposal.author_id == body.user_id:
        raise HTTPException(status_code=409, detail="El autor no puede postularse como colaborador")
    existing = (
        db.query(Collaborator)
        .filter(Collaborator.proposal_id == body.proposal_id, Collaborator.user_id == body.user_id)
        .first()
    )
    if existing:
        raise HTTPException(status_code=409, detail="Ya estás en la lista de colaboradores")
    collab = Collaborator(
        proposal_id=body.proposal_id,
        user_id=body.user_id,
        status=CollaboratorStatus.PENDING,
        applied_at=_today(),
    )
    db.add(collab)
    notif = Notification(
        id=_new_id(),
        user_id=proposal.author_id,
        type="social",
        message=f"{user.name} se postuló como colaborador en tu propuesta.",
        proposal_title=proposal.title,
        date=_today(),
        read=False,
    )
    db.add(notif)
    db.commit()
    return {
        "id": user.id,
        "name": user.name,
        "profileType": user.profile_type,
        "status": CollaboratorStatus.PENDING,
        "appliedAt": collab.applied_at.isoformat(),
    }


@router.patch("/collaborators/{proposal_id}/{user_id}/accept", summary="Aceptar colaborador")
def accept_collaborator(
    proposal_id: str,
    user_id: str,
    requesting_user_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict:
    db = _require_db(db)
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    if proposal.author_id != requesting_user_id:
        raise HTTPException(status_code=403, detail="Solo el autor puede aceptar colaboradores")
    collab = (
        db.query(Collaborator)
        .filter(Collaborator.proposal_id == proposal_id, Collaborator.user_id == user_id)
        .first()
    )
    if not collab:
        raise HTTPException(status_code=404, detail="Colaborador no encontrado")
    collab.status = CollaboratorStatus.ACCEPTED
    db.commit()
    return {"proposal_id": proposal_id, "user_id": user_id, "status": collab.status}


@router.patch("/collaborators/{proposal_id}/{user_id}/reject", summary="Rechazar colaborador")
def reject_collaborator(
    proposal_id: str,
    user_id: str,
    requesting_user_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict:
    db = _require_db(db)
    proposal = db.query(Proposal).filter(Proposal.id == proposal_id).first()
    if not proposal:
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    if proposal.author_id != requesting_user_id:
        raise HTTPException(status_code=403, detail="Solo el autor puede gestionar colaboradores")
    collab = (
        db.query(Collaborator)
        .filter(Collaborator.proposal_id == proposal_id, Collaborator.user_id == user_id)
        .first()
    )
    if not collab:
        raise HTTPException(status_code=404, detail="Colaborador no encontrado")
    db.delete(collab)
    db.commit()
    return {"proposal_id": proposal_id, "user_id": user_id, "removed": True}


# ---------------------------------------------------------------------------
# NOTIFICACIONES
# ---------------------------------------------------------------------------

@router.get("/notifications", summary="Listar notificaciones")
def list_notifications(
    user_id: str | None = Query(default=None),
    unread_only: bool = Query(default=False),
    db: Session = Depends(get_db),
) -> dict:
    db = _require_db(db)
    q = db.query(Notification)
    if user_id:
        q = q.filter(Notification.user_id == user_id)
    if unread_only:
        q = q.filter(Notification.read == False)  # noqa: E712
    notifications = q.order_by(Notification.date.desc()).all()
    return {
        "source": "mysql",
        "total": len(notifications),
        "items": [_notif_to_dict(n) for n in notifications],
    }


@router.patch("/notifications/{notification_id}/read", summary="Marcar como leída")
def mark_notification_read(notification_id: str, db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    notif = db.query(Notification).filter(Notification.id == notification_id).first()
    if not notif:
        raise HTTPException(status_code=404, detail="Notificación no encontrada")
    notif.read = True
    db.commit()
    return {"notification_id": notification_id, "read": True}


@router.patch("/notifications/read-all", summary="Marcar todas como leídas")
def mark_all_notifications_read(user_id: str = Query(...), db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    count = (
        db.query(Notification)
        .filter(Notification.user_id == user_id, Notification.read == False)  # noqa: E712
        .update({"read": True})
    )
    db.commit()
    return {"marked_read": count, "user_id": user_id}


# ---------------------------------------------------------------------------
# ADMIN
# ---------------------------------------------------------------------------

class ContentReportIn(BaseModel):
    proposal_id: str
    proposal_title: str
    reason: str = Field(min_length=10)
    reporter_name: str = Field(min_length=2)


@router.get("/admin/overview", summary="Panel de administración")
def admin_overview(db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    total_users = db.query(User).count()
    active_users = db.query(User).filter(User.active == True).count()  # noqa: E712
    total_proposals = db.query(Proposal).count()
    good = db.query(Proposal).filter(Proposal.status == ProposalStatus.GOOD).count()
    evaluating = db.query(Proposal).filter(Proposal.status == ProposalStatus.EVALUATING).count()
    needs_improvement = db.query(Proposal).filter(Proposal.status == ProposalStatus.NEEDS_IMPROVEMENT).count()

    from sqlalchemy import func as sqlfunc
    by_profile = db.query(User.profile_type, sqlfunc.count(User.id)).group_by(User.profile_type).all()
    by_sector = db.query(Proposal.sector, sqlfunc.count(Proposal.id)).group_by(Proposal.sector).all()
    total_evals = db.query(sqlfunc.sum(Proposal.evaluations_count)).scalar() or 0
    avg_score_row = db.query(sqlfunc.avg(Proposal.current_score)).filter(Proposal.current_score > 0).scalar()
    avg_score = round(float(avg_score_row), 2) if avg_score_row else 0.0
    pending_reports = db.query(ContentReport).filter(ContentReport.dismissed == False).count()  # noqa: E712

    return {
        "source": "mysql",
        "users_total": total_users,
        "users_active": active_users,
        "proposals_total": total_proposals,
        "proposals_by_status": {"good": good, "evaluating": evaluating, "needs_improvement": needs_improvement},
        "users_by_profile": {r[0]: r[1] for r in by_profile},
        "proposals_by_sector": {r[0]: r[1] for r in by_sector},
        "total_evaluations": int(total_evals),
        "average_proposal_score": avg_score,
        "pending_reports": pending_reports,
        "thresholds": {"high": settings.high_score_threshold, "low": settings.low_score_threshold},
    }


@router.get("/admin/reports", summary="Reportes de contenido")
def list_content_reports(dismissed: bool | None = Query(default=None), db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    q = db.query(ContentReport)
    if dismissed is not None:
        q = q.filter(ContentReport.dismissed == dismissed)
    reports = q.order_by(ContentReport.date.desc()).all()
    return {
        "total": len(reports),
        "items": [
            {
                "id": r.id,
                "proposalTitle": r.proposal_title,
                "reason": r.reason,
                "reporterName": r.reporter_name,
                "date": r.date.isoformat() if r.date else None,
                "dismissed": r.dismissed,
            }
            for r in reports
        ],
    }


@router.post("/admin/reports", status_code=201, summary="Crear reporte de contenido")
def create_content_report(body: ContentReportIn, db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    if not db.query(Proposal).filter(Proposal.id == body.proposal_id).first():
        raise HTTPException(status_code=404, detail="Propuesta no encontrada")
    report = ContentReport(
        id=_new_id(),
        proposal_title=body.proposal_title,
        reason=body.reason,
        reporter_name=body.reporter_name,
        date=_today(),
        dismissed=False,
    )
    db.add(report)
    db.commit()
    return {"id": report.id, "proposalTitle": report.proposal_title, "dismissed": False}


@router.patch("/admin/reports/{report_id}/dismiss", summary="Desestimar reporte")
def dismiss_report(
    report_id: str,
    requesting_user_id: str = Query(...),
    db: Session = Depends(get_db),
) -> dict:
    db = _require_db(db)
    user = db.query(User).filter(User.id == requesting_user_id).first()
    if not user or not user.is_admin:
        raise HTTPException(status_code=403, detail="Solo administradores pueden desestimar reportes")
    report = db.query(ContentReport).filter(ContentReport.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")
    report.dismissed = True
    db.commit()
    return {"report_id": report_id, "dismissed": True}


# ---------------------------------------------------------------------------
# ESTADÍSTICAS PÚBLICAS
# ---------------------------------------------------------------------------

@router.get("/stats", summary="Estadísticas públicas")
def public_stats(db: Session = Depends(get_db)) -> dict:
    db = _require_db(db)
    from sqlalchemy import func as sqlfunc
    total_users = db.query(User).count()
    total_proposals = db.query(Proposal).count()
    total_evals = db.query(sqlfunc.sum(Proposal.evaluations_count)).scalar() or 0
    viable = db.query(Proposal).filter(Proposal.status == ProposalStatus.GOOD).count()
    avg = db.query(sqlfunc.avg(Proposal.current_score)).filter(Proposal.current_score > 0).scalar()
    sectors = db.query(Proposal.sector).distinct().count()
    categories = db.query(Proposal.category).distinct().count()
    return {
        "total_users": total_users,
        "total_proposals": total_proposals,
        "total_evaluations": int(total_evals),
        "viable_proposals": viable,
        "average_score": round(float(avg), 2) if avg else 0.0,
        "sectors_represented": sectors,
        "categories_represented": categories,
    }
