# Student Complaint AI Agent

An AI module that classifies student complaints, suggests fixes, and returns **strict JSON** (summary, solution code, steps to apply, verification checklist) using OpenAI models. Designed to plug into a complaint/ticketing system backend or run as a small microservice.

> ✅ No secrets in Git: ships with `.env.example`; keep your real `.env` local.

---

## Features

- 🔎 **Routing:** detect if a complaint is technical / non-technical + category & language hints
- 🧠 **Actionable output:** summary, root cause bullets, solution (code or steps), steps to apply, verification checklist
- 🧱 **JSON-only contract:** reliable machine-readable responses (`response_format={"type": "json_object"}`)
- 🧩 **Easy integration:** simple `ai_agent()` function; optional `for_frontend()` for frontends
- 🔒 **Secrets-safe:** uses environment variables / `.env` (never commit your key)

---

## Project Structure

```
TechnicalSupport_Ai_Agent/
├─ complaint_agent.py             # core AI functions: ai_agent(), for_frontend()
├─ demo.py                        # quick demo runner
├─ requirements.txt
├─ .env.example                   # template for local secrets (NO real keys)
├─ .gitignore
└─ README.md
```

---

## Quick Start

### 1) Clone & install

```bash
git clone https://github.com/<you>/complaint_ai_agent.git
cd complaint_ai_agent
pip install -r requirements.txt
```

### 2) Configure your API key (choose ONE)

- **Option A – .env (local only):**

  1. Copy the example and edit it:
     ```bash
     # Windows (PowerShell)
     copy .env.example .env
     ```
  2. Open `.env` and set:
     ```
     OPENAI_API_KEY=sk-xxxxx...
     ```

- **Option B – Environment variable (no file):**
  ```powershell
  setx OPENAI_API_KEY "sk-xxxxx..."
  # restart terminal so it's visible to Python
  ```

> ❗ Never commit your real `.env`. The repo includes a `.gitignore` that excludes `.env`.

---

## Run a Demo

```bash
python demo.py
```

- To run a **demo without a key**, enable a dry run in `demo.py` (or export `DEMO_MODE=true`) to print a canned JSON response:

```powershell
set DEMO_MODE=true
python demo.py
```

---

## Using the Module in Your Backend

Import and call the agent:

```python
# example_backend.py
import json
from complaint_agent import ai_agent, for_frontend

result = ai_agent(
    "My Python code throws ModuleNotFoundError: requests on Windows.",
    model="gpt-4o-mini",
    temperature=0.0,
    max_tokens=1000,
    student_context={"student_id": "u123", "course": "CS101"},
)

print("Full JSON:\n", json.dumps(result, indent=2, ensure_ascii=False))
print("\nUI subset:\n", json.dumps(for_frontend(result), indent=2, ensure_ascii=False))
```

**What `ai_agent()` returns (shape):**

```json
{
  "routing": {
    "is_technical": true,
    "category": "coding_bug",
    "language": "Python",
    "subtopics": ["imports"],
    "confidence": 0.92
  },
  "response_type": "code_solution",
  "summary": "...",
  "root_cause": ["...", "..."],
  "solution": { "code_language": "text", "code": "pip install requests" },
  "steps_to_apply": ["...", "..."],
  "verification_checklist": ["..."],
  "requests_for_more_info": [],
  "references": ["official docs ..."],
  "escalation": [],
  "red_flags": []
}
```

---

## Optional: Expose as a Microservice (FastAPI)

> Only if your team wants an HTTP endpoint. (Not required to use the module.)

**requirements.txt** already includes `fastapi` and `uvicorn`.

Create `api.py`:

```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from complaint_agent import ai_agent, for_frontend

load_dotenv()
app = FastAPI(title="AI Agent Service", version="0.1.0")

class ComplaintIn(BaseModel):
    student_id: str = Field(..., min_length=2, max_length=64)
    text: str = Field(..., min_length=8, max_length=5000)

@app.post("/analyze")
def analyze(payload: ComplaintIn):
    result = ai_agent(
        payload.text,
        model="gpt-4o-mini",
        temperature=0.0,
        max_tokens=1000,
        student_context={"student_id": payload.student_id},
    )
    if "error" in result:
        raise HTTPException(status_code=502, detail=result["error"])
    return {"raw": result, "ui": for_frontend(result)}
```

Run:

```bash
uvicorn app.api:app --reload --port 8001
```

Test:

```bash
curl -X POST http://localhost:8001/analyze  -H "Content-Type: application/json"  -d "{"student_id":"u123","text":"My Python code throws ModuleNotFoundError: requests"}"
```

---

## Security

- 🔐 Never commit `.env` or keys; use `.env.example` + local `.env`.
- 🧯 If a key is committed accidentally, **rotate it immediately** in your provider’s dashboard and purge the file from git history (`git filter-repo` / BFG).
- 🚫 Don’t expose API keys to the browser—calls must go **server → OpenAI**.
- 🧱 Consider rate limiting and input size limits in production.

**`.gitignore` (already provided) includes:**

```
.env
.env.*
__pycache__/
*.py[cod]
.venv/
venv/
...
```

---

## Troubleshooting

- **`OpenAIError: The api_key client option must be set…`**  
  The env var isn’t visible. Set `OPENAI_API_KEY` (or `.env`) and restart your terminal/IDE.

- **`AuthenticationError: Incorrect API key provided`**  
  You’re using a placeholder. Paste your real `sk-...` key locally (never commit it).

- **GitHub push blocked (secret scanning)**  
  You committed a secret. Rotate the key, add `.env` to `.gitignore`, remove it from history, then push again.

---

## Tech Stack

- Python 3.11+ (works on 3.10–3.13)
- `openai>=1.0.0`
- `python-dotenv` for local secrets
- (Optional) `fastapi` + `uvicorn` for an HTTP service

---
