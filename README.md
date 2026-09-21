# Ask the record

An agent over a public Sanity record of published work and the defects other engineers found in it.
It answers from the record or says it cannot.

**Live, no login:** https://ask-the-record.vercel.app
**Public dataset:** https://u58x3mt0.api.sanity.io/v2025-08-15/data/query/production?query=count(*)
**Studio:** https://self-correcting-systems.sanity.studio/
**Project** `u58x3mt0` · **Knowledge Base** `kbjnxAgyAimV`

## What it does that a keyword search cannot

Ask it how many locatable comments support finding **B8**:

> Finding B8 has **1 locatable comment** (`3ee98` by Pushpendra). Although **three outside finders
> are recorded**, the receipts for Vinh Nguyen and quashudev were not found in the comment trees
> searched.

The ledger claims three finders. One has a permalink. The agent reports the receipt that exists,
not the number claimed.

Two more it will tell you about its own author: the fix for finding B1 is **not merged into
`origin/main`**, and of 14 findings — **12 raised by the 8 outside engineers, 2 internal** — two are
implemented and twelve are not.

## Three schema choices, and what actually enforces them

The schema **represents** these distinctions; the endpoint instructions tell the agent to keep
them; the validator enforces retrieval, required fields, citation syntax and named-object guards
around the answer. It does not re-verify returned values field by field.

1. **`status` and `expiryStatus` are separate fields.** `no_expiry_set` means nobody dated it —
   not "permanently true", not "expired". A claim can be `standing` and undated at once. The schema
   keeps them as separate fields; it does not yet cross-validate `expiryStatus` against `expiresOn`.
2. **A finding is `commentOn` one article and `writtenUpIn` another.** Different fields, different
   facts, never merged.
3. **`patch.inMain` is the merge status.** Public is not merged.

## Two instruments, because one could not do it

A Knowledge Base answers questions spread across prose. **In this build** I could not recover a
reliable identifier-to-field binding — measured: `claim-ledger-population` appears once in the
entries, as a label in a Sources list, with its values present but unbound to that id. So exact-object lookups route to a
second endpoint serving GROQ over the dataset, where `*[_id=="claim-ledger-population"]` returns
one document with its fields and its stored `sourceUrl`. Citations are checked for presence and
syntax — never resolved, and not yet proven to belong to the retrieved evidence.

By default a Context endpoint's mode is derived from its sources: an endpoint with a dataset
source serves GROQ mode and ignores Knowledge Base sources. So this app uses two endpoints and
picks exactly one instrument per question.

```
self-correcting-systems       initial_context, knowledge_base_read
self-correcting-systems-data  initial_context, groq_query, schema_explorer, array_field_reader
```

## Layout

```
studio/     Sanity schema — person, article, finding, patch, claim
harness/    CLI agent + the frozen contract it was built against
web/        the serverless function and page behind ask-the-record.vercel.app
evidence/   breaker verdicts and unedited transcripts, including the failed run
```

## The evidence directory is the point

The harness was written by one agent and graded by separate, owner-assigned AI reviewer sessions
that did not implement it. No human outside this project tested it.

The **first graded run failed** — `evidence/harness-breaker-2026-09-20-kairos/VERDICT.md` is a
BLOCK. Question four answered the wrong claim and matched `STANDING` by accident, which is a right
answer for the wrong reason. Synthetic fixtures showed failed retrievals reaching the model and
producing answers that exited zero.

The repair was not a better prompt. It was the discovery that the Knowledge Base cannot bind
identifiers to fields, which took a second endpoint to prove.

`evidence/harness-graded-v6-2026-09-20-aethar/` holds the later run where **the five frozen
questions held**, `gemini-3.6-flash`, exit 0.

The v6 candidate enforced the Knowledge Base citation rule as path **or** kb id where the contract
required **both**. The live answers happened to supply both, so their content held, but the guard
was weaker than specified. `harness/ask.py` fixes that to an AND, and
`evidence/harness-graded-v7-2026-09-20-aethar/` is an independent run of **that exact file** — five
of five, exit 0, hash matching the copy in this repo.

No transcript was regenerated for a better result.

## What this does not establish

The five questions held on **one graded run**, one model, one key. That is not general reliability.

The snapshot bounding is modest and the agent says so itself: it cannot see what happened to a
branch after the record was built. It happens to still be right about that branch. That is luck,
not knowledge.

The throttle in `web/api-ask.py` is **not** a rate limit. Eight simultaneous requests on
2026-09-20 all returned 200 because each got its own serverless instance and its own counter. It
is documented in the source as a speed bump. The only hard ceiling on spend is the prepaid balance
on the model project.

## Running the CLI

```bash
export SANITY_CONTEXT_TOKEN=...   # org-level, Context Viewer
export GEMINI_PAID_KEY=...
python3 harness/ask.py --all

# exported variables take precedence; ~/.kairos_env and ~/.env are a fallback
```

The Python harness and serverless agent use only the Python standard library. The Studio uses
Sanity's normal React and TypeScript dependencies.
