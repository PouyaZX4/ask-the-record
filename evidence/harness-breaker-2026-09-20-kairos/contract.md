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
