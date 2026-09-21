"""v6 synthetic fixtures. No network. Imports the copied ask.py in this directory."""
import contextlib, importlib.util, io, json, sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
Q1 = "Who found finding B1, and what is the comment id?"
Q4 = "What is the status and expiry of claim-ledger-population?"
Q5 = "How many of the 74 articles mention Kubernetes?"

KB_CONTENT = (
    "claim-ledger-population: The ledger draws from three article comment threads, "
    "not all 74 articles. Finding B1 was found by pm25coder, comment 3eanf. "
    "status standing; expiryStatus no_expiry_set; asOf 2026-09-11."
)
GROQ_JSON = json.dumps({
    "result": {
        "_id": "claim-ledger-population",
        "status": "standing",
        "expiryStatus": "no_expiry_set",
        "asOf": "2026-09-11",
        "sourceUrl": "https://example.org/ledger",
    }
})
KB_ANS = (
    "ANSWER: Finding B1 was found by pm25coder. The comment ID is 3eanf.\n"
    "SOURCES: claim_registry/b_series kbjnxAgyAimV\n"
    "EVIDENCE DATE: 2026-09-06\n"
    "VERDICT: STANDING\n"
    "UNCERTAINTY: Snapshot only."
)
DATA_ANS = (
    "ANSWER: claim-ledger-population is standing and no_expiry_set.\n"
    "SOURCES: claim-ledger-population https://example.org/ledger\n"
    "EVIDENCE DATE: 2026-09-11\n"
    "VERDICT: STANDING\n"
    "UNCERTAINTY: Snapshot only; no_expiry_set is not permanence."
)


def run(case, question):
    spec = importlib.util.spec_from_file_location("candidate", ROOT / "ask.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    m.load_keys = lambda: {
        "SANITY_CONTEXT_TOKEN": "synthetic-token",
        "GEMINI_PAID_KEY": "synthetic-key",
        "_model_key": "synthetic-key",
        "_key_tier": "synthetic",
    }
    model_calls = 0

    def fake_post(url, payload, headers, what):
        nonlocal model_calls
        is_data = "self-correcting-systems-data" in url
        if what == "Gemini":
            model_calls += 1
            if model_calls == 1 and case not in ("no_retrieval", "empty_verdict"):
                if is_data or m.route(question) == "data":
                    q = "" if case == "no_paths" else '*[_id=="claim-ledger-population"]'
                    return {"candidates": [{"content": {"parts": [
                        {"functionCall": {"name": "groq_query", "args": {"query": q}}}
                    ]}}]}
                paths = [] if case == "no_paths" else ["claim_registry/b_series"]
                return {"candidates": [{"content": {"parts": [
                    {"functionCall": {"name": "knowledge_base_read", "args": {"paths": paths}}}
                ]}}]}
            if m.route(question) == "data":
                answer = DATA_ANS
                if case == "missing_source_url":
                    answer = DATA_ANS.replace(" https://example.org/ledger", "")
            else:
                answer = KB_ANS
                if case == "kb_path_only":
                    answer = KB_ANS.replace(" kbjnxAgyAimV", "")
                if case == "kb_neither":
                    answer = KB_ANS.replace("SOURCES: claim_registry/b_series kbjnxAgyAimV",
                                            "SOURCES: none")
            if case == "empty_uncertainty":
                answer = answer.split("UNCERTAINTY:")[0] + "UNCERTAINTY: "
            if case == "empty_verdict":
                answer = answer.replace("VERDICT: STANDING", "VERDICT:")
            return {"candidates": [{"content": {"parts": [{"text": answer}]}}]}

        method = payload["method"]
        name = payload.get("params", {}).get("name")
        if case == "http_failure" and method == "initialize":
            raise m.Failure("Synthetic HTTP 401")
        if method == "initialize":
            return {"result": {}}
        if method == "tools/list":
            if is_data:
                tools = [{"name": "initial_context"}, {"name": "groq_query"}]
            else:
                tools = [{"name": "initial_context"}, {"name": "knowledge_base_read"}]
            return {"result": {"tools": tools}}
        if name == "initial_context":
            return {"result": {"content": [{"type": "text", "text": "Synthetic outline"}]}}
        if name == "knowledge_base_read":
            if case == "empty_retrieval":
                return {"result": {"content": []}}
            if case == "mcp_tool_error":
                return {"result": {"isError": True, "content": [{"type": "text", "text": "nope"}]}}
            return {"result": {"content": [{"type": "text", "text": KB_CONTENT}]}}
        if name == "groq_query":
            if case == "empty_retrieval":
                return {"result": {"content": []}}
            if case == "mcp_tool_error":
                return {"result": {"isError": True, "content": [{"type": "text", "text": "nope"}]}}
            return {"result": {"content": [{"type": "text", "text": GROQ_JSON}]}}
        raise AssertionError((method, name, is_data))

    m.post = fake_post
    old = sys.argv
    sys.argv = ["ask.py", question]
    output = io.StringIO()
    try:
        with contextlib.redirect_stdout(output):
            code = m.main()
    finally:
        sys.argv = old
    return {
        "case": case,
        "question": question,
        "exit_code": code,
        "model_calls": model_calls,
        "stdout": output.getvalue(),
    }


CASES = [
    ("valid_kb", Q1, 0),
    ("valid_data", Q4, 0),
    ("empty_retrieval", Q1, 1),
    ("mcp_tool_error", Q1, 1),
    ("no_paths", Q1, 1),
    ("no_retrieval", Q1, 1),
    ("empty_uncertainty", Q1, 1),
    ("http_failure", Q1, 1),
    ("missing_source_url", Q4, 1),
    ("kb_neither", Q1, 1),
    ("kb_path_only", Q1, 0),  # current code is OR; A19 asked AND — expect 0, flag as hole
    ("empty_verdict", Q1, 1),
    ("q5_routes_kb", Q5, 0),
]

results = []
print("case                     exit  want  model  observed")
for case, q, want in CASES:
    r = run(case, q)
    r["want"] = want
    lines = [s for s in r["stdout"].splitlines()
             if "FAILURE:" in s or "CONTRACT VIOLATION" in s or "[instrument:" in s]
    r["observed_reason"] = lines
    results.append(r)
    ok = "OK" if r["exit_code"] == want else "MISS"
    print(f"{case:24} {r['exit_code']:>4}  {want:>4}  {r['model_calls']:>5}  {ok}  {lines[:2]}")

# routing table, no model
spec = importlib.util.spec_from_file_location("candidate", ROOT / "ask.py")
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)
print("\nrouting frozen five:")
for q in m.FROZEN_QUESTIONS:
    print(f"  {m.route(q):4}  {q}")

(ROOT / "control-probes.json").write_text(json.dumps(results, indent=2) + "\n")
