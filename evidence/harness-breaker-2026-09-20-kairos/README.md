# First breaker review — BLOCK

Controlling breaker: an independent seat that did not write the harness.
Candidate `0e9631f6…`, contract through A12.

## Read these

| file | what it is |
|---|---|
| `VERDICT.md` | the BLOCK, with observed reasons and the repair boundary |
| `live-network-transcript.txt` | **the real graded run**, unedited, 3,557 bytes |
| `control-probes.json` | synthetic fixtures that found unenforced rules |
| `claim-ledger-population.json` | the claim checked directly against the public dataset, independent of the model |

## Ignore this one

`sandbox-dns-failure-not-the-graded-run.txt` — 96 bytes. A first attempt died on DNS
before reaching the endpoint. It is kept because deleting a failed attempt would be
the thing this review exists to catch, but it is **not** the graded run and contains
no answers.

## What was found

Question four answered the **wrong claim** and matched `STANDING` by accident — a right
answer for the wrong reason. Synthetic fixtures showed failed retrievals reaching the
model and producing answers that exited zero.

The repair was not a better prompt. See `../harness-graded-v6-2026-09-20-aethar/` for
the later run against the repaired candidate.
