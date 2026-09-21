"""Judge-facing Ask endpoint.

Same loop as the graded CLI harness (HARNESS_CONTRACT_2026-09-20.md, A19):
the question routes to one instrument, the model picks what to read, and the
answer carries five mandatory fields. Credentials stay server-side; the browser
never sees a key.

Questions are an allowlist — exactly the set the independent reviewer graded.
That fixes WHICH question can be asked, not how many times. The throttle below is
per-instance and was measured failing against parallel load — a speed bump, not a
control. The only hard ceiling is the budget cap on the model project.
"""
import json
import os
import re
import time
import urllib.error
import urllib.request
from http.server import BaseHTTPRequestHandler

ORG = "od9141taf"
KB = "kbjnxAgyAimV"
KB_ENDPOINT = f"https://api.sanity.io/v1/context/organizations/{ORG}/mcp/self-correcting-systems"
DATA_ENDPOINT = f"https://api.sanity.io/v1/context/organizations/{ORG}/mcp/self-correcting-systems-data"
MODEL = "gemini-3.6-flash"
TEMPERATURE = 0
MAX_TOOL_CALLS = 6
SNAPSHOT_DATE = "2026-09-20"

# Allowlist. Index -> question. Nothing else is answerable.
QUESTIONS = [
    "Who found finding B1, and what is the comment id?",
    "Is the patch for finding B1 merged into origin/main?",
    "How many locatable comments support finding B8?",
    "What is the status and expiry of claim-ledger-population?",
    "How many of the 74 articles mention Kubernetes?",
]


class Failure(Exception):
    pass


# Per-instance throttle. MEASURED 2026-09-20: eight simultaneous requests all
# returned 200 because Vercel gave each its own instance, each with its own
# counter. This slows a naive sequential loop and does NOTHING against parallel
# load. It is a speed bump, not a control.
#
# The only hard ceiling is the budget cap on the model project. Do not describe
# this function as rate limited.
_HITS = []
WINDOW_S = 60
MAX_PER_WINDOW = 6
_DAY = {"date": None, "n": 0}
MAX_PER_DAY = 200


def throttle():
    now = time.time()
    global _HITS
    _HITS = [t for t in _HITS if now - t < WINDOW_S]
    if len(_HITS) >= MAX_PER_WINDOW:
        raise Failure(f"rate limit: max {MAX_PER_WINDOW} questions per {WINDOW_S}s on this "
                      f"instance. The record is public — query it directly at "
                      f"https://u58x3mt0.api.sanity.io/v2025-08-15/data/query/production")
    day = time.strftime("%Y-%m-%d", time.gmtime(now))
    if _DAY["date"] != day:
        _DAY.update(date=day, n=0)
    if _DAY["n"] >= MAX_PER_DAY:
        raise Failure(f"daily cap of {MAX_PER_DAY} reached on this instance")
    _HITS.append(now)
    _DAY["n"] += 1


VERDICTS = ("STANDING", "RETRACTED", "SUPERSEDED", "UNBUILT", "EXPIRED",
            "NO_EXPIRY_SET", "INSUFFICIENT_EVIDENCE")


def contract_violations(answer, instrument, retrieved, reads, question):
    """Same checks the graded CLI harness applies (R6/R7/R8). A dirty answer is
    labelled on screen rather than rendered clean.

    Checks that citations are PRESENT and well formed. It does not fetch them —
    no HTTP resolution is performed, and the page says so."""
    v = []
    for f in ("ANSWER:", "SOURCES:", "EVIDENCE DATE:", "VERDICT:", "UNCERTAINTY:"):
        if f not in answer:
            v.append(f"missing field {f.rstrip(':')}")
    unc = re.search(r"UNCERTAINTY:\s*(.*)", answer, re.S)
    if unc is not None and not unc.group(1).strip():
        v.append("UNCERTAINTY is empty")
    m = re.search(r"VERDICT:\s*([A-Z_]+)", answer)
    verdict = m.group(1) if m else None
    if verdict and verdict not in VERDICTS:
        v.append(f"VERDICT '{verdict}' is not a contract value")
    if verdict and verdict != "INSUFFICIENT_EVIDENCE" and reads == 0:
        v.append("answered with a verdict but read nothing")
    src = re.search(r"SOURCES:\s*(.*?)(?=\nEVIDENCE DATE:|$)", answer, re.S)
    src_text = src.group(1) if src else ""
    if verdict and verdict != "INSUFFICIENT_EVIDENCE":
        if instrument == "data" and not re.search(r"https?://\S+", src_text):
            v.append("dataset answer carries no resolvable URL")
        if instrument == "kb":
            if not re.search(r"\b[a-z0-9_]+/[a-z0-9_]+", src_text):
                v.append("KB answer cites no entry path")
            if KB not in src_text:
                v.append("KB answer does not cite the knowledge base id")
    for ident in re.findall(r"\b(claim-[a-z0-9-]+|[AB]\d+)\b", question):
        if verdict != "INSUFFICIENT_EVIDENCE":
            if ident not in retrieved:
                v.append(f"'{ident}' is absent from what was retrieved")
            if ident not in answer:
                v.append(f"the answer never names '{ident}'")
    return v


def route(question):
    """A19: dataset only for claim-* field lookups. Everything else stays on the KB."""
    return "data" if re.search(r"\bclaim-[a-z0-9-]+", question) else "kb"


def post(url, payload, headers, what, retries=3):
    body = json.dumps(payload).encode()
    last = None
    for attempt in range(retries):
        req = urllib.request.Request(url, data=body, method="POST")
        for k, v in headers.items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=60) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            detail = e.read()[:200].decode(errors="replace")
            last = f"{what}: HTTP {e.code} — {detail}"
            if e.code not in (429, 500, 502, 503, 504) or attempt == retries - 1:
                raise Failure(last)
            time.sleep(2 * (attempt + 1))
        except Exception as e:
            last = f"{what}: {e}"
            if attempt == retries - 1:
                raise Failure(last)
            time.sleep(2 * (attempt + 1))
    raise Failure(last or what)


def mcp(token, method, params, req_id, endpoint):
    d = post(endpoint, {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params},
             {"Authorization": f"Bearer {token}", "Content-Type": "application/json",
              "Accept": "application/json, text/event-stream"}, f"MCP {method}")
    if "error" in d:
        raise Failure(f"MCP {method}: {json.dumps(d['error'])[:200]}")
    return d["result"]


def mcp_text(result, what):
    """A failed or empty retrieval is a FAILURE. It is never handed to the model."""
    if result.get("isError"):
        body = "".join(c.get("text", "") for c in result.get("content", []))
        raise Failure(f"{what}: endpoint returned isError — {body[:200]}")
    text = "".join(c.get("text", "") for c in result.get("content", []))
    if not text.strip():
        raise Failure(f"{what}: empty retrieval")
    return text


READ_TOOL = {
    "name": "knowledge_base_read",
    "description": "Read full entries from the knowledge base by path, taken verbatim from the outline.",
    "parameters": {"type": "object",
                   "properties": {"paths": {"type": "array", "items": {"type": "string"}}},
                   "required": ["paths"]},
}
GROQ_TOOL = {
    "name": "groq_query",
    "description": "Query the dataset with GROQ. Fetch the exact document by _id when the question names one.",
    "parameters": {"type": "object",
                   "properties": {"query": {"type": "string"}},
                   "required": ["query"]},
}

OUTPUT_RULES = f"""
You are answering ONE question. You have no conversation history.

Fetch what you judge relevant. You choose what to read. At most {MAX_TOOL_CALLS} tool calls.

Answer in EXACTLY this shape, these five labels, nothing before or after:

ANSWER: <the claim, stated plainly>
SOURCES: <what you read, and any source URLs carried in the retrieved text>
EVIDENCE DATE: <the asOf or date recorded IN the record. Never today's date.>
VERDICT: <STANDING, RETRACTED, SUPERSEDED, UNBUILT, EXPIRED, NO_EXPIRY_SET, or INSUFFICIENT_EVIDENCE>
UNCERTAINTY: <what this answer cannot establish. Never empty.>

Hard rules:
- If the retrieved material does not answer the question, VERDICT is INSUFFICIENT_EVIDENCE and
  ANSWER says the record does not contain it. Do not answer from your own knowledge. A number you
  did not read is a fabrication.
- status and expiry are SEPARATE facts. A claim can be standing AND have no expiry set.
- Anything about mutable external state — whether a branch merged, whether an article changed — is
  a SNAPSHOT CLAIM. Say so, give the snapshot date ({SNAPSHOT_DATE}), and say the record cannot see
  changes after it.
- Report the number of receipts that exist, not the number claimed.
"""


def run(question, sanity_token, gemini_key):
    instrument = route(question)
    endpoint = DATA_ENDPOINT if instrument == "data" else KB_ENDPOINT
    tool = GROQ_TOOL if instrument == "data" else READ_TOOL
    extra = ("\n\nThis endpoint queries the dataset with GROQ. When the question names a document "
             "id, fetch that exact document. SOURCES must include its sourceUrl field.\n"
             if instrument == "data" else
             f"\n\nThis endpoint serves a Knowledge Base. SOURCES must cite the entry path(s) you "
             f"read and the knowledge base id {KB}. A per-claim URL does not exist here; do not "
             f"invent one.\n")

    mcp(sanity_token, "initialize",
        {"protocolVersion": "2025-06-18", "capabilities": {},
         "clientInfo": {"name": "ask-page", "version": "1.0"}}, 1, endpoint)
    context = mcp_text(mcp(sanity_token, "tools/call",
                           {"name": "initial_context", "arguments": {}}, 2, endpoint),
                       "initial_context")

    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{MODEL}:generateContent?key={gemini_key}")
    contents = [{"role": "user", "parts": [{"text": question}]}]
    calls, trace, rid = 0, [], 10
    reads, retrieved = 0, ""

    while True:
        d = post(url, {"systemInstruction": {"parts": [{"text": context + OUTPUT_RULES + extra}]},
                       "contents": contents,
                       "tools": [{"functionDeclarations": [tool]}],
                       "generationConfig": {"temperature": TEMPERATURE}},
                 {"Content-Type": "application/json"}, "model")
        parts = (d.get("candidates") or [{}])[0].get("content", {}).get("parts", []) or []
        fcs = [p["functionCall"] for p in parts if "functionCall" in p]

        if not fcs:
            text = "".join(p.get("text", "") for p in parts if "text" in p).strip()
            if not text:
                raise Failure("model returned an empty answer")
            return {"instrument": instrument, "answer": text, "read": trace,
                    "model": MODEL, "snapshot": SNAPSHOT_DATE,
                    "violations": contract_violations(text, instrument, retrieved,
                                                      reads, question)}

        if calls + len(fcs) > MAX_TOOL_CALLS:
            return {"instrument": instrument, "read": trace, "model": MODEL,
                    "snapshot": SNAPSHOT_DATE,
                    "violations": ["call budget exhausted before an answer"],
                    "answer": (f"ANSWER: Not resolved within the {MAX_TOOL_CALLS}-call budget.\n"
                               f"SOURCES: {', '.join(trace) or 'none'}\n"
                               f"EVIDENCE DATE: none recorded\nVERDICT: INSUFFICIENT_EVIDENCE\n"
                               f"UNCERTAINTY: A harness limit stopped retrieval, which is not "
                               f"evidence the record is silent.")}

        contents.append({"role": "model", "parts": parts})
        responses = []
        for fc in fcs:
            calls += 1
            rid += 1
            args = fc.get("args") or {}
            if instrument == "data":
                qy = args.get("query")
                if not qy:
                    raise Failure("model called groq_query with no query")
                trace.append(qy[:120])
                out = mcp_text(mcp(sanity_token, "tools/call",
                                   {"name": "groq_query", "arguments": {"query": qy}},
                                   rid, endpoint), "groq_query")
                reads += 1
                retrieved += out
            else:
                paths = args.get("paths") or []
                if not paths:
                    raise Failure("model called knowledge_base_read with no paths")
                trace.extend(paths)
                out = mcp_text(mcp(sanity_token, "tools/call",
                                   {"name": "knowledge_base_read",
                                    "arguments": {"knowledgeBase": KB, "paths": paths}},
                                   rid, endpoint), "knowledge_base_read")
                reads += 1
                retrieved += out
            responses.append({"functionResponse": {"name": fc["name"],
                                                   "response": {"content": out}}})
        contents.append({"role": "user", "parts": responses})


class handler(BaseHTTPRequestHandler):
    def _send(self, code, payload):
        body = json.dumps(payload).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        self._send(200, {"questions": QUESTIONS, "model": MODEL, "snapshot": SNAPSHOT_DATE})

    def do_POST(self):
        try:
            length = int(self.headers.get("Content-Length") or 0)
            body = json.loads(self.rfile.read(length) or b"{}")
            idx = body.get("index")
            if not isinstance(idx, int) or not (0 <= idx < len(QUESTIONS)):
                return self._send(400, {"error": "index must be one of the listed questions"})

            throttle()

            token = os.environ.get("SANITY_CONTEXT_TOKEN")
            key = os.environ.get("GEMINI_PAID_KEY") or os.environ.get("GEMINI_API_KEY")
            if not token or not key:
                return self._send(500, {"error": "server is missing credentials"})

            result = run(QUESTIONS[idx], token, key)
            result["question"] = QUESTIONS[idx]
            self._send(200, result)
        except Failure as e:
            msg = str(e)
            code = 429 if msg.startswith(("rate limit", "daily cap")) else 502
            self._send(code, {"error": msg,
                              "note": "no answer was generated" if code == 502 else "throttled"})
        except Exception as e:
            self._send(500, {"error": f"{type(e).__name__}: {e}"})
