import React, { useState } from "react";

type UiOut = {
  status?: string;
  is_technical?: boolean;
  category?: string | null;
  summary?: string | null;
  code_language?: string | null; // kept for support/debug
  code?: string | null;          // kept for support/debug
  steps?: string[];
  verify?: string[];
  ask_more?: string[];
  ticket_prefill?: string;       // pass to ticketing
};

const CODE_PREFIX = "Run the following commands/code:\n";

function renderStepText(s: string) {
  // Render inline `code` spans as <code>
  const parts = s.split("`");
  return (
    <>
      {parts.map((p, i) =>
        i % 2 === 1 ? <code key={i} className="px-1">{p}</code> : <span key={i}>{p}</span>
      )}
    </>
  );
}

export default function AiAssistantPanel() {
  const [text, setText] = useState("");
  const [studentId, setStudentId] = useState("u123");
  const [loading, setLoading] = useState(false);
  const [ui, setUi] = useState<UiOut | null>(null);
  const [error, setError] = useState<string | null>(null);

  async function submit() {
    setLoading(true);
    setError(null);
    setUi(null);
    try {
      const res = await fetch("/api/ai/analyze", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          // Keep if your backend requires it; otherwise remove this line:
          "Authorization": "Bearer some-long-random-token",
        },
        body: JSON.stringify({ student_id: studentId, text }),
      });
      if (!res.ok) {
        const msg = await res.json().catch(() => ({} as any));
        throw new Error((msg as any).detail || `HTTP ${res.status}`);
      }
      const data = await res.json();
      setUi(data.ui as UiOut);
    } catch (e: any) {
      setError(e.message || "Request failed");
    } finally {
      setLoading(false);
    }
  }

  function openTicket(kind: "technical" | "non-technical") {
    const prefill = ui?.ticket_prefill ? `&prefill=${encodeURIComponent(ui.ticket_prefill)}` : "";
  const ai = (ui as any)?.ai_record_id ? `&ai=${(ui as any).ai_record_id}` : "";
  window.location.href =
    `/tickets/new?type=${encodeURIComponent(kind)}&student=${encodeURIComponent(studentId)}&text=${encodeURIComponent(text)}${prefill}${ai}`;
  }

  const isNonTech = ui?.is_technical === false;

  return (
    <div className="max-w-2xl space-y-4">
      <h2 className="text-xl font-semibold">AI Recommendation</h2>

      <div className="space-y-2">
        <textarea
          className="w-full border rounded p-2 h-32"
          placeholder="Describe your issue…"
          value={text}
          onChange={(e: React.ChangeEvent<HTMLTextAreaElement>) => setText(e.target.value)}
        />
        <input
          className="w-full border rounded p-2"
          placeholder="Student ID"
          value={studentId}
          onChange={(e: React.ChangeEvent<HTMLInputElement>) => setStudentId(e.target.value)}
        />
        <button
          className="px-4 py-2 rounded bg-black text-white disabled:opacity-50"
          onClick={submit}
          disabled={loading || text.trim().length < 5}
        >
          {loading ? "Thinking…" : "Get Recommendation"}
        </button>
      </div>

      {error && <div className="text-red-600 text-sm">Error: {error}</div>}

      {ui && (
        <div className="border rounded p-3 space-y-4">
          <div className="text-sm opacity-70">
            Category: {ui.category || "—"} | Technical: {String(ui.is_technical)}
          </div>

          {/* NON-TECHNICAL: Only offer ticket creation */}
          {isNonTech ? (
            <div className="space-y-3">
              <p>This appears to be a <strong>non-technical complaint</strong>.</p>
              <p className="opacity-80">Would you like to open a support ticket?</p>
              <div className="flex gap-2">
                <button
                  className="px-3 py-2 rounded bg-blue-600 text-white"
                  onClick={() => openTicket("non-technical")}
                >
                  Open Ticket (Non-Technical)
                </button>
                <button className="px-3 py-2 rounded border" onClick={() => setUi(null)}>
                  Cancel
                </button>
              </div>
            </div>
          ) : (
            // TECHNICAL: Summary + Steps (with inline code) + separate Verify
            <div className="space-y-4">
              {!!ui.summary && <p className="whitespace-pre-wrap">{ui.summary}</p>}

              <div>
                <h3 className="font-semibold">Steps to apply</h3>
                {ui.steps && ui.steps.length ? (
                  <ol className="list-decimal pl-5">
                    {ui.steps.map((s, i) => {
                      // Unmatched commands arrive as a final explicit code step
                      if (s.startsWith(CODE_PREFIX)) {
                        const code = s.slice(CODE_PREFIX.length);
                        return (
                          <li key={i}>
                            Run the following commands/code:
                            <pre className="bg-gray-100 rounded p-2 overflow-auto text-sm mt-2">
                              {code}
                            </pre>
                          </li>
                        );
                      }
                      // Normal merged steps: render inline `code`
                      return <li key={i}>{renderStepText(s)}</li>;
                    })}
                  </ol>
                ) : (
                  <p className="opacity-70">No specific steps provided.</p>
                )}
              </div>

              {!!(ui.verify && ui.verify.length) && (
                <div>
                  <h3 className="font-semibold">Verify</h3>
                  <ul className="list-disc pl-5">
                    {ui.verify.map((v, i) => <li key={i}>{v}</li>)}
                  </ul>
                </div>
              )}

              <div className="pt-1">
                <button
                  className="px-3 py-2 rounded border"
                  onClick={() => openTicket("technical")}
                >
                  Escalate to Support Team
                </button>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
