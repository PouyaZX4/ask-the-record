#!/usr/bin/env python3
"""ask.py — a question goes in, a bounded answer comes out.

Reads ONLY from the Sanity Context MCP endpoint. No local corpus, no cache, no
fallback to the model's own knowledge. Built to HARNESS_CONTRACT_2026-09-20.md
(frozen c7aeec04..., Amendment 1, custody A10).

    python3 ask.py "Who found finding B1, and what is the comment id?"
    python3 ask.py --all        # run the five frozen questions

Every answer carries ANSWER / SOURCES / EVIDENCE DATE / VERDICT / UNCERTAINTY.
Auth or retrieval failure prints FAILURE and exits non-zero. It never degrades
into a model-written answer.
"""
import json
import os
import re
import sys
import time
import urllib.error
import urllib.request

ENDPOINT = ("https://api.sanity.io/v1/context/organizations/"
            "od9141taf/mcp/self-correcting-systems")
KB = "kbjnxAgyAimV"
MODEL = "gemini-2.5-flash"        # A12: 3.8-flash 503s under load; pro tier limit:0
TEMPERATURE = 0
MAX_TOOL_CALLS = 6                # A2: exceeded -> INSUFFICIENT_EVIDENCE, never a guess
SNAPSHOT_DATE = "2026-09-20"      # A7: asserted by the harness; the endpoint does not prove it

FROZEN_QUESTIONS = [
    "Who found finding B1, and what is the comment id?",
    "Is the patch for finding B1 merged into origin/main?",
    "How many locatable comments support finding B8?",
    "What is the status and expiry of claim-ledger-population?",
    "How many of the 74 articles mention Kubernetes?",
]


class Failure(Exception):
    """Anything that must print FAILURE rather than an answer."""


def load_keys():
    keys = {}
    for path in ("~/.kairos_env", "~/.env"):
        p = os.path.expanduser(path)
        if not os.path.exists(p):
            continue
        for line in open(p):
            if "=" in line and not line.strip().startswith("#"):
                k, v = line.split("=", 1)
                keys.setdefault(k.strip(), v.strip().strip('"').strip("'"))
    for required in ("SANITY_CONTEXT_TOKEN", "GEMINI_API_KEY"):
        if not keys.get(required):
            raise Failure(f"{required} not found in ~/.kairos_env or ~/.env")
    return keys


RETRY_CODES = (429, 500, 502, 503, 504)
RETRIES = 4


def post(url, payload, headers, what):
    """Retries transient upstream failures. An exhausted retry is still a FAILURE —
    it never degrades into an answer."""
    body = json.dumps(payload).encode()
    last = None
    for attempt in range(RETRIES):
        req = urllib.request.Request(url, data=body, method="POST")
        for k, v in headers.items():
            req.add_header(k, v)
        try:
            with urllib.request.urlopen(req, timeout=180) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            detail = e.read()[:300].decode(errors="replace")
            last = f"{what}: HTTP {e.code} — {detail}"
            if e.code not in RETRY_CODES or attempt == RETRIES - 1:
                raise Failure(last)
            wait = 5 * (2 ** attempt)
            print(f"  [retry {attempt + 1}/{RETRIES - 1}] {what} HTTP {e.code}, "
                  f"waiting {wait}s", file=sys.stderr)
            time.sleep(wait)
        except Exception as e:
            last = f"{what}: {e}"
            if attempt == RETRIES - 1:
                raise Failure(last)
            time.sleep(5 * (2 ** attempt))
    raise Failure(last or f"{what}: exhausted retries")


def mcp(token, method, params, req_id):
    d = post(ENDPOINT, {"jsonrpc": "2.0", "id": req_id, "method": method, "params": params},
             {"Authorization": f"Bearer {token}",
              "Content-Type": "application/json",
              "Accept": "application/json, text/event-stream"},
             f"MCP {method}")
    if "error" in d:
        raise Failure(f"MCP {method}: {json.dumps(d['error'])[:300]}")
    return d["result"]


def mcp_text(result):
    return "".join(c.get("text", "") for c in result.get("content", []))


# ---------------------------------------------------------------- Gemini

READ_TOOL = {
    "name": "knowledge_base_read",
    "description": ("Read full entries from the knowledge base by path. Paths come verbatim "
                    "from the outline in the context block. Read several related entries in "
                    "one call rather than many round-trips."),
    "parameters": {
        "type": "object",
        "properties": {
            "paths": {
                "type": "array",
                "items": {"type": "string"},
                "description": "Entry paths taken verbatim from the outline.",
            }
        },
        "required": ["paths"],
    },
}

OUTPUT_RULES = f"""
You are answering ONE question. You have no conversation history.

Use knowledge_base_read to fetch the entries you judge relevant. You choose the paths — nothing
selected them for you. You may call it at most {MAX_TOOL_CALLS} times.

Then answer in EXACTLY this shape, these five labels, nothing before or after:

ANSWER: <the claim, stated plainly>
SOURCES: <entry path(s) you read, and any source URLs carried in the entry text>
EVIDENCE DATE: <the asOf or date recorded IN the entry. Never today's date. If the entry
carries no date, write: none recorded in the entry>
VERDICT: <one of STANDING, RETRACTED, SUPERSEDED, UNBUILT, EXPIRED, NO_EXPIRY_SET,
INSUFFICIENT_EVIDENCE>
UNCERTAINTY: <what this answer cannot establish. Never empty.>

Hard rules:

- If the retrieved entries do not answer the question, VERDICT is INSUFFICIENT_EVIDENCE and
  ANSWER says the record does not contain it. Do not answer from your own knowledge. Do not
  estimate. A number you did not read is a fabrication.
- Status and expiry are SEPARATE facts. A claim can be STANDING and have no expiry set. Report
  both; never collapse one into the other.
- Anything about mutable external state — whether a branch merged, whether an article changed,
  whether a person replied — is a SNAPSHOT CLAIM. Say so, give the snapshot date
  ({SNAPSHOT_DATE}), and say the record cannot see changes after it.
- Report the number of receipts that exist, not the number claimed.
"""


def gemini(key, system_text, question, call_read):
    url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
           f"{MODEL}:generateContent?key={key}")
    contents = [{"role": "user", "parts": [{"text": question}]}]
    calls = 0
    trace = []

    while True:
        payload = {
            "systemInstruction": {"parts": [{"text": system_text + OUTPUT_RULES}]},
            "contents": contents,
            "tools": [{"functionDeclarations": [READ_TOOL]}],
            "generationConfig": {"temperature": TEMPERATURE},
        }
        d = post(url, payload, {"Content-Type": "application/json"}, "Gemini")
        cands = d.get("candidates") or []
        if not cands:
            raise Failure(f"Gemini returned no candidates: {json.dumps(d)[:300]}")
        parts = cands[0].get("content", {}).get("parts", []) or []

        fcs = [p["functionCall"] for p in parts if "functionCall" in p]
        if not fcs:
            text = "".join(p.get("text", "") for p in parts if "text" in p).strip()
            if not text:
                raise Failure("Gemini returned an empty answer")
            return text, trace

        if calls + len(fcs) > MAX_TOOL_CALLS:
            return (f"ANSWER: The record was not resolved within the {MAX_TOOL_CALLS}-call "
                    f"budget, so no answer is given.\nSOURCES: {', '.join(trace) or 'none'}\n"
                    f"EVIDENCE DATE: none recorded in the entry\n"
                    f"VERDICT: INSUFFICIENT_EVIDENCE\n"
                    f"UNCERTAINTY: The budget stopped retrieval before the question was "
                    f"answered. This is a harness limit, not evidence the record is silent.",
                    trace)

        contents.append({"role": "model", "parts": parts})
        responses = []
        for fc in fcs:
            calls += 1
            paths = (fc.get("args") or {}).get("paths") or []
            trace.extend(paths)
            responses.append({"functionResponse": {
                "name": fc["name"],
                "response": {"content": call_read(paths)},
            }})
        contents.append({"role": "user", "parts": responses})


# ---------------------------------------------------------------- run

def ask(question, keys, context_text, token, state):
    def call_read(paths):
        if not paths:
            return "No paths requested."
        state["id"] += 1
        return mcp_text(mcp(token, "tools/call",
                            {"name": "knowledge_base_read",
                             "arguments": {"knowledgeBase": KB, "paths": paths}},
                            state["id"])) or "Empty retrieval."

    answer, trace = gemini(keys["GEMINI_API_KEY"], context_text, question, call_read)

    missing = [f for f in ("ANSWER:", "SOURCES:", "EVIDENCE DATE:", "VERDICT:", "UNCERTAINTY:")
               if f not in answer]
    unc = re.search(r"UNCERTAINTY:\s*(.*)", answer, re.S)
    if missing:
        answer += f"\n\n[HARNESS] Contract violation — missing field(s): {', '.join(missing)}"
    if unc and not unc.group(1).strip():
        answer += "\n\n[HARNESS] Contract violation — UNCERTAINTY is empty."
    return answer, trace


def main():
    args = sys.argv[1:]
    if not args:
        print(__doc__)
        return 2
    questions = FROZEN_QUESTIONS if args[0] == "--all" else [" ".join(args)]

    try:
        keys = load_keys()
        token = keys["SANITY_CONTEXT_TOKEN"]
        state = {"id": 100}
        mcp(token, "initialize", {"protocolVersion": "2025-06-18", "capabilities": {},
                                  "clientInfo": {"name": "ask.py", "version": "1.0"}}, 1)
        context_text = mcp_text(mcp(token, "tools/call",
                                    {"name": "initial_context", "arguments": {}}, 2))
        if not context_text:
            raise Failure("initial_context returned nothing")
    except Failure as e:
        print(f"FAILURE: {e}")
        return 1

    print(f"model {MODEL} · temp {TEMPERATURE} · kb {KB} · snapshot {SNAPSHOT_DATE} "
          f"· context {len(context_text):,} chars\n")

    bad = 0
    for i, q in enumerate(questions, 1):
        print("=" * 78)
        print(f"Q{i}: {q}")
        print("=" * 78)
        try:
            answer, trace = ask(q, keys, context_text, token, state)
        except Failure as e:
            print(f"FAILURE: {e}\n")
            bad += 1
            continue
        print(answer)
        print(f"\n[entries read: {', '.join(trace) if trace else 'none'}]\n")
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
