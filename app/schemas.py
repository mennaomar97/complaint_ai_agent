# app/schemas.py
from datetime import datetime
from typing import Optional, List
from pydantic import BaseModel, Field


# --------- Students ---------
class StudentCreate(BaseModel):
    external_id: str
    name: Optional[str] = None
    email: Optional[str] = None


class StudentOut(BaseModel):
    id: int
    external_id: str
    name: Optional[str]
    email: Optional[str]
    created_at: datetime
    class Config:
        from_attributes = True


# --------- AI Recommendation ---------
class AiRecOut(BaseModel):
    id: int
    student_id: int
    input_text: str
    category: Optional[str]
    is_technical: bool
    ui_json: str
    raw_json: str
    created_at: datetime
    class Config:
        from_attributes = True


# --------- Tickets ---------
class TicketCreate(BaseModel):
    student_external_id: str = Field(..., description="e.g., u123")
    type: str = Field(..., pattern="^(technical|non-technical)$")
    subject: str
    description: str
    priority: Optional[str] = Field(default="normal")
    source_ai_id: Optional[int] = None  # link to AiRecommendation.id if created from the AI panel


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


class TicketQuery(BaseModel):
    status: Optional[str] = None
    student_external_id: Optional[str] = None
