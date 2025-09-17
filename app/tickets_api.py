from typing import Optional, Dict, Any, List
from fastapi import APIRouter, HTTPException, Depends, Query
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import datetime

from .auth import require_bearer
from .db import get_db, Base, engine
from .models import Student, Ticket, AiRecommendation

router = APIRouter(prefix="/api/tickets", tags=["tickets"])

# Create tables on import (simple for dev; use Alembic in prod)
Base.metadata.create_all(bind=engine)


# ---------- Pydantic I/O ----------

class TicketIn(BaseModel):
    student_id: str = Field(..., description="External id, e.g. u123")
    type: str = Field(..., pattern="^(technical|non-technical)$")
    text: str
    ai_context: Optional[Dict[str, Any]] = None   # e.g. { ai_record_id, prefill }

class TicketOut(BaseModel):
    id: int
    student_id: int
    type: str
    status: str
    priority: str
    subject: str
    description: str
    source_ai_id: Optional[int]
    assigned_to: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# ---------- helpers ----------

def _get_or_create_student(db: Session, external_id: str) -> Student:
    st = db.scalar(select(Student).where(Student.external_id == external_id))
    if st:
        return st
    st = Student(external_id=external_id)
    db.add(st)
    db.flush()
    return st


# ---------- routes ----------

@router.post("", response_model=TicketOut, dependencies=[Depends(require_bearer)])
def create_ticket(payload: TicketIn, db: Session = Depends(get_db)) -> Ticket:
    """
    Create and persist a ticket. Keeps your existing request fields.
    - Subject is derived from the first 100 chars of text.
    - Links to the AI recommendation if ai_context.ai_record_id is provided.
    """
    student = _get_or_create_student(db, payload.student_id)

    source_ai_id = None
    if payload.ai_context and isinstance(payload.ai_context, dict):
        source_ai_id = payload.ai_context.get("ai_record_id")
        if source_ai_id:
            # if provided, ensure it exists (optional)
            ai = db.get(AiRecommendation, int(source_ai_id))
            if not ai:
                source_ai_id = None  # ignore if invalid id

    subject = (payload.text.strip().splitlines()[0])[:100] or "Student complaint"
    ticket = Ticket(
        student_id=student.id,
        type=payload.type,
        status="open",
        priority="normal",
        subject=subject,
        description=payload.text.strip(),
        source_ai_id=source_ai_id,
    )
    db.add(ticket)
    db.flush()
    db.refresh(ticket)
    return ticket


@router.get("/{ticket_id}", response_model=TicketOut, dependencies=[Depends(require_bearer)])
def read_ticket(ticket_id: int, db: Session = Depends(get_db)) -> Ticket:
    tk = db.get(Ticket, ticket_id)
    if not tk:
        raise HTTPException(status_code=404, detail="Ticket not found")
    return tk


@router.get("", response_model=List[TicketOut], dependencies=[Depends(require_bearer)])
def list_tickets(
    student_id: Optional[str] = Query(None, description="external id, e.g. u123"),
    status: Optional[str] = Query(None, description="open|assigned|resolved|closed"),
    db: Session = Depends(get_db),
) -> List[Ticket]:
    stmt = select(Ticket)
    if status:
        stmt = stmt.where(Ticket.status == status)
    if student_id:
        st = db.scalar(select(Student).where(Student.external_id == student_id))
        if not st:
            return []
        stmt = stmt.where(Ticket.student_id == st.id)
    return list(db.scalars(stmt).all())
