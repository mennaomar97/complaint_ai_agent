from datetime import datetime
from typing import Optional

from sqlalchemy import (
    String, Text, DateTime, Boolean, ForeignKey, Integer
)
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .db import Base


class Student(Base):
    __tablename__ = "students"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    external_id: Mapped[str] = mapped_column(String(64), index=True)  # e.g., "u123"
    name: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)
    email: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    tickets: Mapped[list["Ticket"]] = relationship(back_populates="student")
    ai_records: Mapped[list["AiRecommendation"]] = relationship(back_populates="student")


class AiRecommendation(Base):
    __tablename__ = "ai_recommendations"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    input_text: Mapped[str] = mapped_column(Text)
    category: Mapped[Optional[str]] = mapped_column(String(64))
    is_technical: Mapped[bool] = mapped_column(Boolean, default=True)
    ui_json: Mapped[str] = mapped_column(Text)    # the compact "ui" dict as JSON
    raw_json: Mapped[str] = mapped_column(Text)   # full raw agent JSON
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)

    student: Mapped["Student"] = relationship(back_populates="ai_records")
    ticket: Mapped[Optional["Ticket"]] = relationship(back_populates="source_ai", uselist=False)


class Ticket(Base):
    __tablename__ = "tickets"

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    student_id: Mapped[int] = mapped_column(ForeignKey("students.id"))
    type: Mapped[str] = mapped_column(String(32))  # "technical" | "non-technical"
    status: Mapped[str] = mapped_column(String(32), default="open")  # open|assigned|resolved|closed
    priority: Mapped[str] = mapped_column(String(16), default="normal")  # low|normal|high|urgent
    subject: Mapped[str] = mapped_column(String(200))
    description: Mapped[str] = mapped_column(Text)
    source_ai_id: Mapped[Optional[int]] = mapped_column(ForeignKey("ai_recommendations.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    assigned_to: Mapped[Optional[str]] = mapped_column(String(120), nullable=True)  # staff username/email

    student: Mapped["Student"] = relationship(back_populates="tickets")
    source_ai: Mapped[Optional["AiRecommendation"]] = relationship(back_populates="ticket")
