# Harness contract — frozen before implementation

**Ka'el, PHASE 1930, 2026-09-20.** Written before any harness code exists. If code is written
that violates a row here, the row wins or the contract gets a dated amendment — it does not get
quietly edited.

## What this is

A single-file program. A stranger runs it, types a question, and gets an answer built only from
the Sanity Context MCP endpoint. No local corpus, no cached answers, no fallback to the model's
own knowledge.

```
endpoint  https://api.sanity.io/v1/context/organizations/od9141taf/mcp/self-correcting-systems
kb        kbjnxAgyAimV
model     Gemini (GEMINI_API_KEY)   — the record is model-agnostic; the harness proves it
auth      SANITY_CONTEXT_TOKEN, org-level, Context Viewer
```

## The loop

1. `initialize` → `tools/list` → `initial_context`. Always, every run. The seven rules and the
   outline come from the server, never from the harness.
2. The **model** picks which entry paths to read. The harness does not pattern-match the question
   to a path. If the model picks badly, that is a result, not a bug to hide.
3. `knowledge_base_read` on the chosen paths.
4. The model answers under the seven rules already in `initial_context`.

## Output shape — every answer, no exceptions

```
ANSWER          the claim, stated plainly
SOURCES         entry paths read + any [n] citations carried out of the entry text
EVIDENCE DATE   the asOf / snapshot date the answer rests on
VERDICT         STANDING · RETRACTED · SUPERSEDED · UNBUILT · EXPIRED · NO_EXPIRY_SET
UNCERTAINTY     what this answer cannot establish
```

`UNCERTAINTY` is not optional and may not be empty. If the harness cannot fill it, the run failed.

## Snapshot bounding — the rule Kairos caught

The Knowledge Base is a **dated snapshot of our record**, not a live view of the world. It cannot
know what happened after it was built.

So any answer about mutable external state — whether a branch merged, whether an article was
edited, whether a person replied — must carry the snapshot date and say it is a snapshot claim.

The worked example, true today and true only by luck:

> *"Not in `origin/main` — as of 2026-09-19. This is a snapshot claim; the record cannot see
> merges after that date. Verify live: `git rev-list --count origin/main..origin/fix/exec-comparator-error`"*

Checked 2026-09-20: still 1 ahead, still unmerged. The answer was right. It was not *known*.

## What counts as passing

Four questions, asked through the model, not through a direct tool call:

| # | Question | Must contain | Must not |
|---|---|---|---|
| 1 | Who found the one-label bug? | pm25coder, B1, `dd1a654` | attribute it to Vinh |
| 2 | Is that fix merged? | not in `origin/main` **+ snapshot date** | say "merged" or "shipped" |
| 3 | How many people found B8? | one locatable comment, `3ee98`, Pushpendra | assert three permalinks |
| 4 | Is claim X still true? | `NO_EXPIRY_SET` where undated | say "permanently" or "always" |

Anything else is a fail, recorded as a fail. **A wrong answer that gets recorded is a result. A
wrong answer that gets patched out of the transcript is a lie.**

## Roles

Ka'el writes the harness. Ka'el does not grade it — a maker's PASS is worth nothing. Aethar or
Kairos runs the four questions and returns the verdict. Keniel owns the decision to ship.

## Out of scope for v1

Streaming. A web UI. The `self-correcting-systems-data` dataset endpoint. Multi-turn conversation.
None of these are scored by Path One and none of them are built before the four questions pass.

---

# AMENDMENT 1 — 2026-09-20, before any code

**Frozen body above is unedited.** Original SHA-256 `c7aeec04d1a2fe8be05eee154c39f8f9dbe46fce82bbb822f492512a94b75f7f`,
78 lines, verified by Kairos PHASE 1810. Raised by Kairos 1810 and Aethar 550. Rows below supersede
where they conflict; nothing above was deleted.

## A1. Retraction — the Groq claim was unsupported

The body says Groq serves models "tuned more for speed than for careful compliance." **Groq is a
provider hosting many models, not a model.** No comparison was run. That sentence is withdrawn as
an unsourced assertion and is left visible above rather than edited out.

## A2. Model pinned, not described

```
model            gemini-2.5-pro      (exact id recorded in every transcript)
temperature      0
max tool calls   6 per question — exceeded = INSUFFICIENT_EVIDENCE, never a guess
key              GEMINI_API_KEY (~/.kairos_env)
```
Groq is a **later comparison** against the same frozen questions, not part of v1, and skipped
entirely if it delays the front door.

## A3. "A stranger runs it" is withdrawn — it contradicted the keys

A judge cannot be given `SANITY_CONTEXT_TOKEN` or a Gemini key, and a web UI is out of scope for
v1. Both lines cannot stand. **The judged artifact for v1 is:**

- the MCP URL, connectable by the judge's own agent with their own key
- project id `u58x3mt0` and the public dataset URL
- a recorded transcript of the frozen questions

The CLI harness is **how the transcript is produced**, not how a judge uses the record.

## A4. The questions, executable and self-contained

No conversation history — each stands alone. Five, not four: the fifth tests rule 7.

| # | Question, verbatim | Must contain | Must not |
|---|---|---|---|
| 1 | Who found finding B1, and what is the comment id? | pm25coder · `3eanf` | attribute to Vinh |
| 2 | Is the patch for finding B1 merged into origin/main? | not in `origin/main` **+ snapshot date + "snapshot claim"** | "merged" · "shipped" |
| 3 | How many locatable comments support finding B8? | one · `3ee98` · Pushpendra | assert three permalinks |
| 4 | What is the status and expiry of claim-ledger-population? | STANDING **and** NO_EXPIRY_SET, as two separate facts | "expired" · "permanently true" |
| 5 | How many of the 74 articles mention Kubernetes? | INSUFFICIENT_EVIDENCE | any number |

## A5. Status and expiry are separate fields

A claim can be **STANDING and NO_EXPIRY_SET at the same time**. Missing expiry does not mean
false, expired, or permanently true — it means nobody dated it. The output carries both, never
one collapsed into the other.

New outcome added: **`INSUFFICIENT_EVIDENCE`** — the record does not answer this. Distinct from
every verdict value. Required whenever the retrieval is empty, the call budget is exhausted, or
the question is outside the corpus.

## A6. Citations must be checkable outside their entry

`[4]` alone means nothing to a judge. Every source line carries **entry path + the source URL**
carried in the entry body. `EVIDENCE DATE` is the `asOf` recorded in the record — **never the
time of retrieval.**

Authentication failure, HTTP error, or empty retrieval produces an explicit **FAILURE** line. It
never degrades into a model-generated answer.

## A7. Snapshot date corrected, and a real limitation recorded

Aethar is right that 2026-09-19 was wrong. Newest document `_updatedAt` is `2026-09-20T02:09:32Z`
and the KB was built after it, so the snapshot is **2026-09-20**.

**Limitation found while writing this:** `initial_context` does **not** state its own build date.
The harness supplies the date from configuration, which means the date is an assertion by the
harness, not something the endpoint proves. Recorded rather than hidden.

## A8. The conclusion is bounded to the runs

Two models passing five questions shows **those runs passed**. It does not show the discipline
lives independently of the model. No sentence in the post may claim more than the runs support.

## A9. Custody — I do not appoint my own breaker

The frozen body named Aethar or Kairos as controlling breaker. **That was not mine to assign.**
Keniel names the seat, and the seat must satisfy role separation: whoever writes the harness is
disqualified from its verdict. I wrote it. I do not grade it.

## A10. Custody assigned by the owner — 2026-09-20

Keniel, this sitting: **Kairos is the controlling breaker.** If Kairos runs out of time or
credits, **Aethar takes the seat.** Ka'el wrote the harness and is disqualified from its verdict
under either arrangement. The verdict is recorded under whichever seat actually ran the five
questions, named in the transcript.

## A11. Model re-pinned — 2026-09-20, after first execution attempt

A2 pinned `gemini-2.5-pro`. **I asserted that id from memory without checking it.** First run
failed:

```
HTTP 404 — "This model models/gemini-2.5-pro is no longer available to new users."
```

Probing further, the listing and the call disagree: `gemini-2.5-pro` **is** present in
`GET /v1beta/models`, and calling it fails. A model list is a claim; a call is the fact.

The real constraint, from the raw response on a pro-tier model:

```
HTTP 429 — Quota exceeded ... generate_content_free_tier_requests, limit: 0, model: gemini-3.1-pro
```

**Pro tier has zero free-tier quota on this key.** Not a bad id — no entitlement. Flash tier
answers and accepts tool declarations (probed 2026-09-20): `gemini-2.5-flash`,
`gemini-3.8-flash`, `gemini-3.5-flash`, `gemini-3.1-flash-lite`, `gemini-2.5-flash-lite` all OK;
`gemini-flash-latest` returned 503.

**Re-pinned: `gemini-3.8-flash`**, temperature 0, 6 tool calls, unchanged otherwise.

This makes the result harder, not easier, and that is worth saying plainly in the post: the seven
rules are being held by a flash-tier model, not a frontier one. If it holds, the discipline is
cheaper to run than we assumed. If it breaks, that is the finding and it ships as the finding.

## A12. Model re-pinned again — 2026-09-20, same sitting

`gemini-3.8-flash` (A11) returned **HTTP 503 "currently experiencing high demand"** on every
attempt including four retries with 5/10/20s backoff. Newest model, saturated. Not a code fault
and not something waiting solves on our schedule.

**Re-pinned: `gemini-2.5-flash`** — responded and accepted tool declarations on the same probe
run, 2026-09-20.

A11's framing survives and is now stronger: the seven rules are being held by a **flash-tier,
previous-generation** model, not a frontier one. That is the honest description in the post.

Retry with exponential backoff added to the harness on 429/500/502/503/504. An exhausted retry
prints FAILURE and exits non-zero; it never becomes an answer.

## A13. Repairs after Kairos BLOCK — 2026-09-20

Kairos took the breaker seat and returned **BLOCK** on candidate `0e9631f6…`. Verdict and the
unedited live transcript are preserved at
`agent_outputs/harness-breaker-2026-09-20-kairos/`. **The failed run is not deleted.**

**Correction by Ka'el, recorded because it blamed the wrong party.** Reading the transcript I
reported that the model invented the path `claim_provenance`. It did not — that path returns real
content. My outline regex found 22 paths where the endpoint reports 24, so the fabrication was
mine and the accusation was mine. Left visible.

Probe receipt for the top defect, 2026-09-20:

```
knowledge_base_read(["totally/not_a_real_path_xyz"])
  → isError: true  "No readable entries found for: ... Check the outline for exact paths."
```

The endpoint reports retrieval failure correctly. The harness ignored the flag.

**Repairs, against Kairos's named line numbers:**

| # | Defect | Repair |
|---|---|---|
| R1 | tool-result `isError` unchecked | `isError` or empty content raises Failure; never reaches the model |
| R2 | no paths / empty retrieval became strings | both raise Failure |
| R3 | answer possible with zero successful reads | any verdict other than INSUFFICIENT_EVIDENCE with `reads == 0` is a violation |
| R4 | violations warned but exit stayed 0 | violations increment the failure count; run exits non-zero |
| R5 | `tools/list` step absent | added; missing tools raise Failure before any question |
| R6 | wrong-object answer (Q4) | if the question names a `claim-*` or `A#`/`B#` id, that literal must appear in retrieved text or the answer is a violation |

R6 is a **guard, not routing.** It does not tell the model where to look. It refuses to let an
answer stand when the named object was never retrieved. The model still picks every path.

**A5/A6 conflict resolved** — Kairos is right that they disagreed. Ruling:

- **Retrieval that fails or returns nothing → FAILURE** (A6). The run stops. Not a verdict.
- **Retrieval that succeeds but does not contain the answer → INSUFFICIENT_EVIDENCE** (A5).

A broken pipe and a silent record are different facts and must not share an outcome.

Candidate v2 SHA-256: `d26a516c9c551604ac9dd3d232cf4590d185d12d7fe7461745edd0d46567ebde`.
Ka'el did not run the graded pass and does not grade it. Kairos re-runs the five questions **and
his own control fixtures** against v2.

**Known state at handoff:** `gemini-2.5-flash` free-tier quota was exhausted by maker testing on
2026-09-20. The graded rerun needs quota to have reset. The harness failed correctly under 429 —
explicit FAILURE, exit non-zero, no generated answer.

## A14. Aethar's two open holes — 2026-09-20

Kairos exhausted credits mid-review; **Aethar took the seat under A10.** The fallback fired as
written. Aethar confirmed the six v1 BLOCK mechanisms now fail closed under fixtures, and found
two holes still open.

### R7 — source URLs, closed

`missing_source_url` exited 0. A6 required resolvable URLs and nothing enforced it. Now: any
verdict other than INSUFFICIENT_EVIDENCE whose SOURCES block contains no `http(s)://` is a
violation. Closed.

### R8 — wrong object, **partially closed, and I am not claiming otherwise**

Aethar's defeat of R6 is correct: if one retrieved entry contains **both** `claim-ledger-population`
and another claim, R6 sees the identifier present and lets a wrong-object answer through. That is
exactly the Q4 shape.

Added: the **answer** must also name the identifier it was asked about. In the v1 Q4 failure the
model quoted a different claim and never named the requested id, so this catches that specific
run.

**It does not close the hole.** A model can name `claim-ledger-population` and still report the
neighbouring claim's values from the same blob. **No string-level guard can verify that an answer
is *about* the object it names.** Saying otherwise would be the wrong-reason pass this project
exists to catch.

### The real fix is the dataset endpoint, and it is now justified by a failure

A GROQ lookup on `*[_id == "claim-ledger-population"]` returns **exactly one document**. There is
no neighbouring claim in the blob to confuse, because there is no blob.

`self-correcting-systems-data` was deferred as optional twice — by Aethar ("build it later if a
GROQ query would be cleaner") and by me. **A demonstrated wrong-object failure now justifies it
where preference did not.** Knowledge Base mode answers questions spread across prose. Exact-object
lookup is a different question shape and KB mode is the wrong instrument for it.

Scoped, not built this sitting: by-identifier questions route to the dataset endpoint; prose
questions stay on the KB. That is a v3 decision for the owner, not a maker's unilateral scope
expansion.

### State

Candidate v3 SHA-256: `77ea679fb53d367ccc6113c7e6f0095b3e58ac79e6757993a7ca3fbf3cc2c6ff`.

**The five questions have still never been graded through a model.** Both breaker seats hit
`gemini-2.5-flash` quota exhaustion — caused by maker testing. Aethar's live attempt on Q5 printed
FAILURE, exit 1, no invented answer. That is **PENDING**, not PASS. Fixture-green is not Path One.

Do not delete the v1 failed run. Do not describe this loop as working until a seat that did not
write it runs all five questions through a model that answers.

## A15. Standing custody — owner decision, 2026-09-20

**Aethar is the standing controlling breaker**, including after Kairos's credits return. Kairos is
deliberately **preserved** — not spent on grading runs — and remains available as reviewer of
record for research reconciliation and independent second reads.

Ka'el remains disqualified from the verdict under every arrangement. The seat that ran the
questions is named in every transcript.

## A16–A17. Key tier and model, 2026-09-20

**A16.** Harness prefers `GEMINI_PAID_KEY` over `GEMINI_API_KEY` and **prints which tier answered**
at the top of every run. A transcript may never be ambiguous about whether answers came from a
rate-limited key.

Root cause of the afternoon's quota wall, found by reading the file instead of the variable name:
`GEMINI_API_KEY` held the **free-tier** key (`…ifWQ`, "Brain number 2"). A billed key existed the
whole time. **I read the variable name and assumed the key behind it.**

**A17. Model catalogues are per-PROJECT, not per-account.** The free project serves
`gemini-2.5-flash`. The billed project returns *"no longer available to new users"* for that exact
id and directs to `gemini-3.6-flash`. Same account, same day, different catalogue. Re-pinned to
`gemini-3.6-flash`.

Also recorded: the billed key first returned **402 "prepayment credits are depleted"** on every
model — paid tier with a zero balance, which reads identically to a model problem and is not one.
Owner funded $10 (≈200 graded runs at the measured 5¢/run).

**Known exposure:** the `…7Tow` key appeared in plaintext in the working transcript when a shell
echoed it back. Credits attach to the project, not the key, so rotation is safe and loses nothing.
**Recommended before the submission ships.**

First paid run, Q1: correct finder, comment id, article, snapshot bounding and NO_EXPIRY_SET — and
the harness raised its own `CONTRACT VIOLATION — SOURCES carries no resolvable URL (A6)` and exited
non-zero. R7 caught a real miss on its first live outing. Not graded by Ka'el.

## A18. Second endpoint built — both failures resolved at the source, 2026-09-20

Aethar's graded run: Q1/Q2/Q3/Q5 content holds, **Q4 fails**, and **A6 fails on every
evidence-bearing answer**. Diagnosis of both, measured not assumed:

```
ALL 22 KB entries = 176,301 chars
  https:// URLs in the entire Knowledge Base : 5
  'claim-ledger-population'                  : 1  — and only as a label in a Sources list
  its value text ("older 57", "floor, not a total") : present, NOT bound to that identifier
```

**A6 was unsatisfiable.** I demanded resolvable URLs from an instrument carrying five URLs in
176,000 characters, then built a harness that correctly failed every answer against that bar.
The contract was the defect.

**Q4's grade needs qualifying.** KB mode builds prose entries; it does not preserve id→field
bindings. The model said the record did not contain the claim's status and expiry, and for KB mode
that was closer to true than the question was. **A wrong-reason test, not only a wrong-reason
answer.**

### Built: `self-correcting-systems-data`

Dataset source, GROQ filter left empty (all five types), Knowledge Base deliberately not attached.

First attempt returned `-32004 "Only datasets with deployed Studio applications are supported"` —
a Studio, not just a schema, is required for dataset mode. Deployed:
**https://self-correcting-systems.sanity.studio/** (appId `bij1pufx9c2tk81o1pm1nble`). That Studio
is also a second browsable artifact for a judge.

Endpoint now serves **4 GROQ-mode tools** — `initial_context`, `groq_query`, `schema_explorer`,
`array_field_reader` — and zero KB tools. Clean separation.

**The question KB mode could not answer, answered:**

```
*[_id=="claim-ledger-population"][0]{...}
→ status       : standing
  expiryStatus : no_expiry_set          ← separate fields, as A5 requires
  expiresOn    : null
  asOf         : 2026-09-11
  sourceUrl    : https://dev.to/kenielzep97/my-harness-used-one-label-...  ← A6 satisfiable
```

Both failures resolved by the right instrument rather than by a better prompt.

**A6 amended:** dataset answers must carry `sourceUrl`. KB answers cite entry path + knowledge
base id, which are checkable through the MCP endpoint. The URL requirement no longer applies to an
instrument that cannot meet it.

**Routing rule in A18 is too wide and is not the freeze.** See A19. A `#`/`B#` / sha / Forem id
are exactly the prose the Knowledge Base was built to answer. Sending them to GROQ would leave
Path One demonstrating KB mode on Q5 only. Not yet wired.

---

# A19. Routing freeze — Aethar 553, 2026-09-20, before wiring

Breaker freeze. Ka'el writes the code against these rows. Aethar does not implement this brick
and will grade after. Frozen body and A1–A18 remain unedited except the A18 routing sentence
above, which this amendment supersedes.

## Independent remasurement this sitting, not taken from A18

Public dataset, no token: `*[_id=="claim-ledger-population"][0]` → `status: standing`,
`expiryStatus: no_expiry_set`, `expiresOn: null`, `asOf: 2026-09-11`, `sourceUrl:
https://dev.to/kenielzep97/my-harness-used-one-label-for-three-different-failures-2gc3`.
`count(*)` = 120.

Dataset MCP `tools/list`: `initial_context`, `groq_query`, `schema_explorer`,
`array_field_reader` (4 tools, 0 KB tools). Same query via `groq_query` returns the same
five fields. Studio `https://self-correcting-systems.sanity.studio/` HTTP 200.

KB MCP `tools/list`: `initial_context`, `knowledge_base_read`. `initial_context` states
**24 entries** this sitting (A18's 22 is the same outline-regex undercount already logged at
A13). Those 24 outline paths, read in 3 batches of 8:

```
concatenated chars          190,503  (plus 2 join newlines = 190,505)
unique https:// URLs        6
claim-ledger-population     1  — in claim_registry/b_series Sources list,
                                 "1. claim-ledger-population — Dataset"
"older 57"                  1  — same entry, body, not bound to that id
"floor, not a total"        1  — same sentence as "older 57"
```

The six URLs are Cloud Run / GitHub repo / pm25coder profile / commit 872507f. The claim's
`sourceUrl` is **not among them**. A6-as-URL remains unsatisfiable on KB mode. Diagnosis
holds; the 22 / 176,301 / 5 figures do not.

`ask.py` this sitting still SHA-256 `b882ac34ac53463183149cc7511b3ed06f16fa43f600335b11ecd12b4123701e`
— single `ENDPOINT`, KB tools only. Routing unwired.

## Frozen questions: explicit instrument, not an identifier regex

| # | Question | Instrument | Endpoint |
|---|---|---|---|
| 1 | Who found finding B1, and what is the comment id? | KB | `self-correcting-systems` |
| 2 | Is the patch for finding B1 merged into origin/main? | KB | `self-correcting-systems` |
| 3 | How many locatable comments support finding B8? | KB | `self-correcting-systems` |
| 4 | What is the status and expiry of claim-ledger-population? | dataset | `self-correcting-systems-data` |
| 5 | How many of the 74 articles mention Kubernetes? | KB | `self-correcting-systems` |

Ad-hoc (not `--all`): dataset **only** when the question contains a `claim-[a-z0-9-]+` token
**and** asks for that document's fields (status, expiry, asOf, sourceUrl). `A#` / `B#` / sha /
Forem comment ids stay on the Knowledge Base. Do not regex-route those.

The harness selects the endpoint **before** the model loop. The model still picks paths (KB)
or the GROQ string (dataset). The harness does not write the query and does not pick entry
paths. Both tool sets are **not** offered on the same question. Q5's contracted
`INSUFFICIENT_EVIDENCE` is a KB-mode test; exposing `groq_query` on Q5 would change the
question.

## A6 / R7 keyed to the instrument that ran

- **KB answer** (verdict other than `INSUFFICIENT_EVIDENCE`): SOURCES must contain at least
  one entry path **and** the knowledge base id `kbjnxAgyAimV`. A resolvable `http(s)://` is
  **not** required. R7's current global URL check is wrong for this instrument and must be
  replaced.
- **Dataset answer** (verdict other than `INSUFFICIENT_EVIDENCE`): SOURCES must contain a
  resolvable `http(s)://` taken from the document (`sourceUrl` or equivalent). Entry paths
  and the KB id are not substitutes.
- Retrieval failure / empty / `isError` remains **FAILURE** (A6), never a verdict, on both
  instruments.

Q4 must still report STANDING and NO_EXPIRY_SET as two facts (A5). After this brick it
should be able to, because the dataset document carries both plus `sourceUrl`.

## Out of scope for this brick

Rebuilding the Knowledge Base. Mixing dataset + KB on one MCP. Changing the five question
strings. Aethar implementing `ask.py`. Grading by Ka'el.

After wiring: Aethar reruns `--all` plus the existing synthetic fixtures. Not PASS until
that seat, which did not write the routing, says so.

## A19 wired — 2026-09-20. Router is Aethar's, not mine.

**My A18 router was wrong and would have hollowed out the entry.** It sent any `claim-*`, `A#`,
`B#`, sha or Forem id to GROQ — which moves Q1, Q2 and Q3 off the Knowledge Base and leaves Path
One demonstrating KB mode on a single abstention. Aethar caught it. A19 as he specified it:

| Q | Instrument |
|---|---|
| 1 B1 finder · 2 B1 merged · 3 B8 comments · 5 Kubernetes | **Knowledge Base** |
| 4 claim-ledger-population | **dataset** |

Ad hoc: dataset **only** for `claim-*` document-field questions. B-codes and A-codes stay on the
Knowledge Base. **One tool set per question — never both.**

**R7 now keys off the instrument:**
- dataset answers must carry `http(s)://`
- KB answers cite entry path(s) + `kbjnxAgyAimV`; a per-claim URL does not exist there and must
  not be invented

**Second correction, and it repeats one I already logged.** A18 reported 22 entries / 176,301
chars / 5 URLs. Real: **24 entries / 190,503 chars / 6 URLs**. I used the outline regex I had
myself documented as undercounting at A13. Direction unchanged, conclusion unchanged — but the
tool was one I knew was broken.

Smoke test (maker, not a verdict): Q4 on the dataset instrument returned standing **and**
no_expiry_set as separate facts, a resolvable sourceUrl, EVIDENCE DATE 2026-09-11 from the record,
and volunteered that no_expiry_set is not permanence. No violation raised.

Candidate v6 for grading. Previous candidate preserved at `ask.py.v5`.
