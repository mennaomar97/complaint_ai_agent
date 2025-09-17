from fastapi import FastAPI, HTTPException, Depends, Header
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import Optional
from dotenv import load_dotenv
import os, time, json

from .auth import require_bearer
from .complaint_agent import ai_agent, for_frontend

# NEW: DB imports
from sqlalchemy.orm import Session
from sqlalchemy import select
from .db import get_db
from .models import Student, AiRecommendation

load_dotenv()  # reads OPENAI_API_KEY and DATABASE_URL from environment/.env (server-side only)

# ---- Basic auth token for your frontend <-> backend call (optional but recommended)
API_BEARER = os.getenv("INTERNAL_API_TOKEN")  # set this in the server env/secrets

# ---- FastAPI app
app = FastAPI(title="Complaint AI Recommendation Agent", version="1.1.0")

# CORS: allow your web origin(s)
origins = os.getenv("CORS_ORIGINS", "*").split(",")
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
)

# ---- Schemas
class AnalyzeIn(BaseModel):
    student_id: str = Field(..., min_length=2, max_length=64)
    text: str = Field(..., min_length=5, max_length=8000)

class AnalyzeOut(BaseModel):
    raw: dict
    ui: dict
    latency_ms: int

# ---- Endpoint
@app.post("/api/ai/analyze", response_model=AnalyzeOut)
def analyze(
    payload: AnalyzeIn,
    db: Session = Depends(get_db),
    _=Depends(require_bearer),
):
    t0 = time.time()

    # 1) Call the agent for strict JSON
    result = ai_agent(
        payload.text,
        model="gpt-4o-mini",
        temperature=0.0,
        max_tokens=1400,
    )
    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])

    # 2) Shape for UI
    ui = for_frontend(result)

    # 3) Persist student + AI record
    student = db.scalar(select(Student).where(Student.external_id == payload.student_id))
    if not student:
        student = Student(external_id=payload.student_id)
        db.add(student)
        db.flush()

    ai_row = AiRecommendation(
        student_id=student.id,
        input_text=payload.text,
        category=ui.get("category"),
        is_technical=bool(ui.get("is_technical", True)),
        ui_json=json.dumps(ui, ensure_ascii=False),
        raw_json=json.dumps(result, ensure_ascii=False),
    )
    db.add(ai_row)
    db.flush()
    db.refresh(ai_row)

    # Return the db id so the frontend can attach it when creating a ticket
    ui = {**ui, "ai_record_id": ai_row.id}

    return AnalyzeOut(
        raw=result,
        ui=ui,
        latency_ms=int((time.time() - t0) * 1000),
    )

# ---- Mount tickets router (DB-backed tickets API)
from .tickets_api import router as tickets_router
app.include_router(tickets_router)
