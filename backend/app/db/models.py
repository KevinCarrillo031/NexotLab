"""ORM SQLAlchemy compatible con MySQL/MariaDB (pymysql) y PostgreSQL."""

from datetime import date, datetime

from sqlalchemy import (
    Boolean,
    Date,
    DateTime,
    Float,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.db.base import Base


class User(Base):
    __tablename__ = "users"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    email: Mapped[str] = mapped_column(String(180), unique=True, nullable=False, index=True)
    password_hash: Mapped[str | None] = mapped_column(String(255), nullable=True)
    profile_type: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    sector: Mapped[str | None] = mapped_column(String(32), nullable=True, index=True)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    joined_at: Mapped[date] = mapped_column(Date, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    proposals: Mapped[list["Proposal"]] = relationship(back_populates="author")
    evaluations: Mapped[list["Evaluation"]] = relationship(back_populates="evaluator")
    comments: Mapped[list["Comment"]] = relationship(back_populates="author")


class Proposal(Base):
    __tablename__ = "proposals"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    title: Mapped[str] = mapped_column(String(240), nullable=False)
    category: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    sector: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    deliverable: Mapped[str] = mapped_column(Text, nullable=False)
    author_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    status: Mapped[str] = mapped_column(String(32), nullable=False, index=True)
    current_score: Mapped[float] = mapped_column(Float, default=0.0, nullable=False)
    evaluations_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)

    author: Mapped["User"] = relationship(back_populates="proposals")
    weekly_scores: Mapped[list["WeeklyScore"]] = relationship(back_populates="proposal", cascade="all, delete-orphan")
    collaborators: Mapped[list["Collaborator"]] = relationship(back_populates="proposal", cascade="all, delete-orphan")
    evaluations: Mapped[list["Evaluation"]] = relationship(back_populates="proposal", cascade="all, delete-orphan")
    comments: Mapped[list["Comment"]] = relationship(back_populates="proposal", cascade="all, delete-orphan")


class WeeklyScore(Base):
    __tablename__ = "weekly_scores"
    __table_args__ = (UniqueConstraint("proposal_id", "week_index", name="uq_weekly_score_week"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    proposal_id: Mapped[str] = mapped_column(ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    week_index: Mapped[int] = mapped_column(Integer, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    recorded_at: Mapped[date | None] = mapped_column(Date, nullable=True)

    proposal: Mapped["Proposal"] = relationship(back_populates="weekly_scores")


class Collaborator(Base):
    __tablename__ = "collaborators"
    __table_args__ = (UniqueConstraint("proposal_id", "user_id", name="uq_collaborator_membership"),)

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    proposal_id: Mapped[str] = mapped_column(ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    status: Mapped[str] = mapped_column(String(16), nullable=False, default="pending")
    applied_at: Mapped[date] = mapped_column(Date, nullable=False)

    proposal: Mapped["Proposal"] = relationship(back_populates="collaborators")
    user: Mapped["User"] = relationship()


class Evaluation(Base):
    __tablename__ = "evaluations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    proposal_id: Mapped[str] = mapped_column(ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False, index=True)
    evaluator_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    viability: Mapped[float] = mapped_column(Float, nullable=False)
    innovation: Mapped[float] = mapped_column(Float, nullable=False)
    impact: Mapped[float] = mapped_column(Float, nullable=False)
    clarity: Mapped[float] = mapped_column(Float, nullable=False)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)

    proposal: Mapped["Proposal"] = relationship(back_populates="evaluations")
    evaluator: Mapped["User"] = relationship(back_populates="evaluations")


class Comment(Base):
    __tablename__ = "comments"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    proposal_id: Mapped[str] = mapped_column(ForeignKey("proposals.id", ondelete="CASCADE"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[date] = mapped_column(Date, nullable=False)

    proposal: Mapped["Proposal"] = relationship(back_populates="comments")
    author: Mapped["User"] = relationship(back_populates="comments")


class Notification(Base):
    __tablename__ = "notifications"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    user_id: Mapped[str | None] = mapped_column(ForeignKey("users.id"), nullable=True, index=True)
    type: Mapped[str] = mapped_column(String(32), nullable=False)
    message: Mapped[str] = mapped_column(Text, nullable=False)
    proposal_title: Mapped[str | None] = mapped_column(String(240), nullable=True)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    read: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class ContentReport(Base):
    __tablename__ = "content_reports"

    id: Mapped[str] = mapped_column(String(36), primary_key=True)
    proposal_title: Mapped[str] = mapped_column(String(240), nullable=False)
    reason: Mapped[str] = mapped_column(Text, nullable=False)
    reporter_name: Mapped[str] = mapped_column(String(160), nullable=False)
    date: Mapped[date] = mapped_column(Date, nullable=False)
    dismissed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)


class PlatformSetting(Base):
    __tablename__ = "platform_settings"

    key: Mapped[str] = mapped_column(String(64), primary_key=True)
    value: Mapped[str] = mapped_column(String(255), nullable=False)


class SimulationRun(Base):
    __tablename__ = "simulation_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    params_json: Mapped[str] = mapped_column(Text, nullable=False)
    results_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())


class MiningRun(Base):
    __tablename__ = "mining_runs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    kind: Mapped[str] = mapped_column(String(64), nullable=False, index=True)
    params_json: Mapped[str] = mapped_column(Text, nullable=False)
    results_json: Mapped[str] = mapped_column(Text, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())
