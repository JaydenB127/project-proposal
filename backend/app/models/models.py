import uuid
from datetime import datetime, timezone
from sqlalchemy import (
    Column, String, Boolean, Text, ForeignKey, Float,
    Integer, CheckConstraint, UniqueConstraint, Index,
    BigInteger, TIMESTAMP
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from app.db.database import Base


def utcnow():
    return datetime.now(timezone.utc)


class User(Base):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    username = Column(String, unique=True, nullable=False)
    email = Column(String, unique=True, nullable=False)
    password_hash = Column(Text, nullable=False)
    api_key = Column(Text, unique=True, default=lambda: str(uuid.uuid4()))
    is_admin = Column(Boolean, default=False)
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)

    experiments = relationship("Experiment", back_populates="user")
    runs = relationship("Run", back_populates="user")


class Experiment(Base):
    __tablename__ = "experiments"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    description = Column(Text)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    user = relationship("User", back_populates="experiments")
    runs = relationship("Run", back_populates="experiment", cascade="all, delete-orphan")


class Run(Base):
    __tablename__ = "runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    experiment_id = Column(UUID(as_uuid=True), ForeignKey("experiments.id", ondelete="CASCADE"), nullable=False)
    name = Column(Text, nullable=False)
    params = Column(JSONB, nullable=False, default=dict)
    metadata_ = Column("metadata", JSONB, default=dict)
    git_commit = Column(Text)
    data_version = Column(Text)
    status = Column(
        Text,
        CheckConstraint("status IN ('created','running','completed','failed','paused')"),
        default="created",
        nullable=False,
    )
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id", ondelete="SET NULL"))
    created_at = Column(TIMESTAMP(timezone=True), default=utcnow)
    started_at = Column(TIMESTAMP(timezone=True))
    completed_at = Column(TIMESTAMP(timezone=True))
    updated_at = Column(TIMESTAMP(timezone=True), default=utcnow, onupdate=utcnow)

    experiment = relationship("Experiment", back_populates="runs")
    user = relationship("User", back_populates="runs")
    metrics = relationship("Metric", back_populates="run", cascade="all, delete-orphan")
    run_tags = relationship("RunTag", back_populates="run", cascade="all, delete-orphan")

    __table_args__ = (
        Index("idx_runs_experiment", "experiment_id", "created_at"),
        Index("idx_runs_status", "status"),
        Index("idx_runs_git_commit", "git_commit"),
    )


class Metric(Base):
    __tablename__ = "metrics"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id", ondelete="CASCADE"), nullable=False)
    key = Column(Text, nullable=False)
    value = Column(Float, nullable=False)
    step = Column(Integer)
    timestamp = Column(TIMESTAMP(timezone=True), default=utcnow)

    run = relationship("Run", back_populates="metrics")

    __table_args__ = (
        UniqueConstraint("run_id", "key", "step", name="unique_metric_per_run"),
        Index("idx_metrics_lookup", "run_id", "key", "step"),
    )


class Tag(Base):
    __tablename__ = "tags"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    name = Column(Text, nullable=False, unique=True)
    color = Column(Text, default="#3B82F6")

    run_tags = relationship("RunTag", back_populates="tag")


class RunTag(Base):
    __tablename__ = "run_tags"

    run_id = Column(UUID(as_uuid=True), ForeignKey("runs.id", ondelete="CASCADE"), primary_key=True)
    tag_id = Column(UUID(as_uuid=True), ForeignKey("tags.id", ondelete="CASCADE"), primary_key=True)

    run = relationship("Run", back_populates="run_tags")
    tag = relationship("Tag", back_populates="run_tags")
