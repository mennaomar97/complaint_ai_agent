import json, os
from dotenv import load_dotenv
from complaint_agent import ai_agent

load_dotenv()

# Optional: allow demo mode without a key
if os.getenv("DEMO_MODE") == "true":
    print(json.dumps({
      "routing": {"is_technical": True, "category":"coding_bug","language":"Python","subtopics":["imports"],"confidence":0.9},
      "response_type":"code_solution",
      "summary":"You are missing the 'requests' package.",
      "root_cause":["Package not installed"],
      "solution":{"code_language":"text","code":"pip install requests"},
      "steps_to_apply":["Open terminal","Run pip install requests","Retry"],
      "verification_checklist":["Import succeeds","Program runs"],
      "requests_for_more_info":[],
      "references":["pip User Guide"],
      "escalation":[],
      "red_flags":[]
    }, indent=2, ensure_ascii=False))
else:
    out = ai_agent("يا دكتور، الكانتين خلص أكل بدري أوي ومش عارفين نلاقي حاجة ناكلها بين المحاضرات.")

    print(json.dumps(out, indent=2, ensure_ascii=False))
