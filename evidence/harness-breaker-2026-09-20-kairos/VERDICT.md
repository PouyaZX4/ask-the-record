# Kairos controlling breaker — BLOCK

Owner assigned Kairos, with Aethar fallback. Review date: 2026-09-20. Candidate source and contract were copied and hashed before execution; maker files were not edited. This verdict concerns this candidate, not a general model-quality comparison or product readiness rate.

## Frozen objects

- Contract SHA-256: `b03efb5b01e4e128031a35b68507aba750c0417aacaaf21db9111b01673a3cc4` (through A12).
- Harness SHA-256: `0e9631f6eb339276e571de1d1aac5c5f2d2df9db15f7adbbb6d5012ee29cf2e3`.
- Source: `/Users/kenielmaldonado/agent_harness/ask.py`.
- Copies, timestamps: `manifest.json`, `contract.md`, `ask.py` in this directory.

## Live supervised run

Executed the frozen source with `--all`, model `gemini-2.5-flash`, temperature 0, five independent questions. First sandbox attempt failed DNS before answering; retained in `live-transcript.txt` and `live-run.json`. Network-enabled rerun retained in `live-network-transcript.txt` and `live-network-run.json`. No answers were regenerated for better results or edited. The harness's own bounded retries remain visible.

| Question | Observed reason | Assessment |
|---|---|---|
| Q1 B1 finder/comment | pm25coder and 3eanf both present. SOURCES contains an entry path but no source URL. | A4 content requirements met; A6 citation requirement fails. |
| Q2 B1 merge | Says not in origin/main and bounds knowledge to 2026-09-19. Does not explicitly give the configured 2026-09-20 snapshot or the required phrase "snapshot claim". No source URL. | Temporal caution is present; do not misreport this as claiming a live merge check. Frozen A4/A7 snapshot presentation and A6 fail. |
| Q3 B8 receipts | Says one locatable comment and distinguishes three recorded finders, but omits both Pushpendra and 3ee98. No source URL. | Count distinction succeeds; A4 required receipt identity and A6 fail. |
| Q4 specific claim | Answers an external-verification/customer-outcome claim, with 2026-09-19 evidence and 2026-12-31 expiry, instead of claim-ledger-population. | Substantive wrong-object failure. Matching STANDING alone is a wrong-reason pass. |

| Q5 Kubernetes count | Refuses a count and reports INSUFFICIENT_EVIDENCE, with no entries read. | Required abstention response met; no evidence of a corpus search. The harness accepts this without a read. |

**Process result: exit 0 despite the failures above.** All five questions returned answers; Q4/Q5 include recovered HTTP429 retries. The successful exit is not a passing breaker verdict.

Q4 was checked against the public dataset, independently of the model. `claim-ledger-population.json` contains the exact query and response: the requested claim concerns the ledger's three-article comment population, is standing, has expiryStatus no_expiry_set and expiresOn null, asOf 2026-09-11. This source verification establishes the requested object's values; it does not establish why the model selected the wrong object inside the KB.

The harness does not save full MCP responses and model request/response payloads. Its printed selected paths are useful but are not a complete retrieval trace. No claim is made that the independent public dataset response was shown to the model.

## Independent synthetic control fixtures

Run `python3 agent_outputs/harness-breaker-2026-09-20-kairos/probe_controls.py` from the workspace root. These fixtures import the frozen candidate and replace network responses and keys with synthetic values; they make no external calls. Their deliberately unsupported model outputs test enforcement, not whether Gemini actually fabricated these particular outputs.

| Fixture | Intended behavior | Observed behavior | Result |
|---|---|---|---|
| Empty MCP entry content | Explicit FAILURE; no model answer (A6) | Converted to "Empty retrieval.", sent to model; fabricated answer printed; exit 0 | BLOCK |
| MCP tool result isError=true | Reject failed retrieval before answering | isError ignored; error text sent to model; fabricated answer printed; exit 0 | BLOCK |
| Model answers without reading any entries | Enforce declared retrieve-then-answer loop | Unsupported answer accepted, entries read none; exit 0 | BLOCK |
| Empty UNCERTAINTY | Run fails under output contract | Violation appended after answer; exit 0 | BLOCK |
| Injected transport Failure/HTTP401 control | FAILURE, no model call, nonzero exit | FAILURE; zero model calls; exit 1 | Control behaves as intended |

Detailed outputs and call events: `control-probes.json`.

## Mechanisms and repair boundary

- `ask.py:93–105`: only JSON-RPC top-level error is checked; tool-result isError is not checked.
- `ask.py:209–217`: no paths and empty retrieval become strings passed to the model instead of a failure.
- `ask.py:178–183`: a text answer can return with zero successful reads.
- `ask.py:221–228` and `255–268`: invalid output receives a warning but never increments the failure count or raises Failure. Source URLs, source membership, and verdict fields are not validated.
- `ask.py:242–245`: initialize proceeds directly to initial_context; required tools/list step is absent.

Maker repair should reject failed/empty retrieval before another model call; require successful evidence retrieval for evidence-bearing answers; enforce output failure status and resolvable source URLs; ensure exact claim identity is available and checked, abstaining when unavailable; and perform the contracted tool discovery. Keep source dates distinct from the configured KB snapshot date. Preserve this failed run, freeze the successor, and rerun the declared questions plus the failed controls. Do not patch expected answers into routing or treat a model upgrade as the demonstrated fix.

A5 and A6 differ on empty retrieval (INSUFFICIENT_EVIDENCE versus explicit FAILURE). The observed affirmative STANDING answer satisfies neither, so the blocker does not depend on choosing one interpretation. A dated amendment can clarify failure formatting without erasing this evidence.

## Limits

Synthetic control failures are independent breaker fixtures. The network questions are one supervised live run against the owner's provisioned services. Neither establishes judge access using unrelated credentials, general reliability, or model independence. Judge authentication remains untested by this review. Code inspection plus probes identify unenforced rules; no candidate repair was performed by the breaker.
