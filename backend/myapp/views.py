from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import ensure_csrf_cookie
from .models import Ticket

# If you already copied your AI file to backend/myapp/ai/complaint_agent.py:
try:
    from myapp.ai.complaint_agent import ai_agent, for_frontend
    AI_OK = True
except Exception as _e:
    # Fallback stub so the page still loads even if AI file isn't ready yet
    AI_OK = False
    def ai_agent(text, **kwargs):
        return {"summary": "AI not wired yet.", "routing": {"is_technical": False}, "steps_to_apply": []}
    def for_frontend(result):
        return {
            "is_technical": result.get("routing", {}).get("is_technical", False),
            "category": result.get("routing", {}).get("category", "unknown"),
            "summary": result.get("summary", ""),
            "steps": result.get("steps_to_apply", []),
            "ai_record_id": None,
        }

def ping(request):
    return HttpResponse("pong from myapp")

@ensure_csrf_cookie
def new_query(request):
    # Renders the template below; change path if your template file is elsewhere
    return render(request, "student/new_query.html")

@require_POST
def ai_analyze(request):
    body = request.body.decode("utf-8") if request.body else ""
    text = (request.POST.get("text") or body).strip()
    if not text:
        return HttpResponseBadRequest("text required")
    try:
        result = ai_agent(text, model="gpt-4o-mini", temperature=0.0, max_tokens=1200)
        # if your real ai_agent returns strict JSON dict with 'error', handle it:
        if isinstance(result, dict) and "error" in result:
            return JsonResponse({"error": result["error"]}, status=502)
        ui = for_frontend(result) if callable(for_frontend) else result
        return JsonResponse({"ui": ui, "raw": result})
    except Exception as e:
        return JsonResponse({"error": str(e)}, status=502)
    
@require_POST
def ticket_create(request):
    text            = request.POST.get("complaint_text", "")
    ai_is_technical = request.POST.get("ai_is_technical") == "true"
    ai_category     = request.POST.get("ai_category", "")
    ai_record_id    = request.POST.get("ai_record_id", "")

    ticket = Ticket.objects.create(
        student=request.user if request.user.is_authenticated else None,
        type="technical" if ai_is_technical else "non-technical",
        text=text,
        ai_category=ai_category,
        ai_is_technical=ai_is_technical,
        ai_record_id=ai_record_id,
    )
    return redirect("ticket_detail", pk=ticket.pk)

def ticket_detail(request, pk):
    ticket = get_object_or_404(Ticket, pk=pk)
    return render(request, "tickets/detail.html", {"ticket": ticket})
