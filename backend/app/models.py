from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, Text,
    DateTime, ForeignKey, Float
)
from sqlalchemy.orm import relationship

from app.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)
    instruction = Column(Text, nullable=False)
    status = Column(String(30), default="planned")
    created_at = Column(DateTime, default=datetime.utcnow)

    actions = relationship(
        "ActionStep",
        back_populates="task",
        cascade="all, delete-orphan",
        order_by="ActionStep.step_number",
    )


class ActionStep(Base):
    __tablename__ = "action_steps"

    id = Column(Integer, primary_key=True, index=True)
    task_id = Column(
        Integer,
        ForeignKey("tasks.id"),
        nullable=False,
    )

    step_number = Column(Integer, nullable=False)
    action = Column(String(50), nullable=False)
    object_name = Column(String(100), nullable=True)
    target = Column(String(100), nullable=True)
    status = Column(String(30), default="pending")
    duration_seconds = Column(Float, nullable=True)
    error_message = Column(Text, nullable=True)

    task = relationship("Task", back_populates="actions")