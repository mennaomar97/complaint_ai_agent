# ==============================================
# JSON-structured Technical Complaint AI Agent
# ==============================================
from __future__ import annotations
import os
import json
import sys
from dotenv import load_dotenv
from openai import OpenAI, OpenAIError
from typing import Any

# For Windows consoles with Arabic/Unicode text
try:
    sys.stdout.reconfigure(encoding="utf-8")
except Exception:
    pass

# ==============================================
# 1) Load API key from .env
# ==============================================
load_dotenv()
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise RuntimeError("OPENAI_API_KEY not found in .env")

client = OpenAI(api_key=api_key)
print("OpenAI Key loaded:", True)

# ==============================================
# 2) JSON schema (as text) + strict system rules
# ==============================================
RESPONSE_SCHEMA = r"""
You are an AI teaching assistant.
Always return your answers in the following JSON schema ONLY (no markdown, no extra text):

{
  "routing": {
    "is_technical": true,
    "category": "coding_bug | coding_how_to | dev_env_tooling | data_ml_dl | sys_networks | theory_concept | other_technical | non_technical",
    "language": "Python|Java|C++|... or null",
    "subtopics": ["..."],
    "confidence": 0.0
  },
  "response_type": "code_solution | theory_guidance | env_tooling | reject_non_technical",
  "summary": "One-paragraph plain summary tailored to the student.",
  "root_cause": ["bullet", "bullet"],
  "solution": {
    "code_language": "Python|Java|text",
    "code": "full corrected/runnable snippet OR step-by-step commands; use comments for key lines."
  },
  "steps_to_apply": ["step 1", "step 2", "step 3"],
  "verification_checklist": ["what the student should observe to confirm the fix"],
  "requests_for_more_info": ["ask up to 3 missing items or empty array"],
  "references": ["official docs only, with titles (no raw URLs needed)"],
  "escalation": ["when/how to escalate to human TA/admin if blocked"],
  "red_flags": ["policy or safety concerns if any, else empty array"]
}
"""

SYSTEM_PROMPT = (
    "You are an AI teaching assistant. "
    "Return STRICT JSON ONLY (no markdown, no surrounding text). "
    "The JSON MUST match the provided schema exactly: keys, types, and field names. "
    "If something is unknown, use null, an empty string, or an empty array—do NOT invent. "
    "Keep code minimal and runnable when possible."
)

# ==============================================
# 3) Agent function
# ==============================================
def ai_agent(student_complaint: str, *,model: str = "gpt-4o-mini", temperature: float = 0.0, max_tokens: int = 1000) -> dict[str, Any]:
    """
    Takes a student's complaint and returns a structured JSON dict.
    """
    
    try:
        resp = client.chat.completions.create(
            model=model,
            temperature=0,             
            max_tokens=1000,
            # Forces the model to emit a single JSON object (no prose)
            response_format={"type": "json_object"},
            messages= [
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{RESPONSE_SCHEMA}\n\nStudent complaint:\n{student_complaint}"},
                ],
            # request lower latency
            timeout=30,
        )
        raw = resp.choices[0].message.content
        parsed = json.loads(raw)
        return parsed

    except OpenAIError as api_err:
        return {"error": f"OpenAI API error: {str(api_err)}", "raw": ""}
    except Exception as e:
        return {"error": f"Unexpected error: {str(e)}", "raw": ""}


# ---- 4) helper to pick display fields in your UI
def for_frontend(agent_result: dict[str, Any]) -> dict[str, Any]:
    """
    Extract the most display-relevant bits for the frontend.
    """
    if "error" in agent_result:
        return {"status": "error", "message": agent_result["error"]}

    sol = (agent_result.get("solution") or {})
    return {
        "status": "ok",
        "is_technical": agent_result.get("routing", {}).get("is_technical", True),
        "category": agent_result.get("routing", {}).get("category"),
        "summary": agent_result.get("summary", ""),
        "code_language": sol.get("code_language"),
        "code": sol.get("code", ""),
        "steps": agent_result.get("steps_to_apply", []),
        "verify": agent_result.get("verification_checklist", []),
        "ask_more": agent_result.get("requests_for_more_info", []),
    }

