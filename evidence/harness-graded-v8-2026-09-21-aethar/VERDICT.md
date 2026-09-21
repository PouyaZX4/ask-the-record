# Aethar 560 — v8 graded run after VERDICT-parse fix

Overnight gap 9h 37m. Battery 100% discharging this sitting.

## Candidate

`ask.py` SHA-256 `98dc0e2c7c0027fd2e83f8ccfcccd5b9ea97485e00fc9ee5036b06b9de6e7e08`
MATCH local CLI, `ask-the-record-repo/harness/ask.py`, and GitHub
`keniel13-ui/ask-the-record` `harness/ask.py` this sitting.

`web/api-ask.py` SHA-256 `f2c9f122f4a1784c3fbde18cac557c0c8246cd954775335c504bc1ba1f49a158`
MATCH local ask-page and GitHub `web/api-ask.py`.

v7 (`330a94ab…`) does not transfer.

## Bug, reproduced here before trusting the fix

Old pattern `VERDICT:\s*([A-Z_]+)` this sitting:

| line | parsed | gated checks skipped? |
|---|---|---|
| `STANDING` | STANDING | no |
| `standing` | None | **yes** |
| `Standing` | `S` | no (wrong-reason parse) |
| `123` | None | **yes** |

New `contract_violations` on a fabricated Kubernetes count with zero reads:

- `STANDING` → 3 violations (zero reads + missing path + missing kb id)
- `standing` / `Standing` / `123` → 4 each (bad verdict **and** the evidence-bearing checks)
- `INSUFFICIENT_EVIDENCE` with a real path + kb id → `[]`

Valid abstention still passes.

v7 transcript VERDICT lines are all in the contract set (`STANDING`×3, `UNBUILT`, `INSUFFICIENT_EVIDENCE`). A full R6 replay of those answers needs the retrieved blobs, which the transcript does not store. I did not re-confirm Ka'el's "five answers replay clean" beyond the verdict tokens.

## Live `--all`

```
python3 /Users/kenielmaldonado/agent_harness/ask.py --all
```

09:34:36–09:36:07 EDT · `gemini-3.6-flash` · billed key · exit **0** · stderr empty.

| Q | Instrument | A4 |
|---|---|---|
| 1 | kb | **hold** pm25coder · `3eanf` |
| 2 | kb | **hold** not in origin/main; snapshot claim |
| 3 | kb | **hold** 1 · `3ee98` · Pushpendra |
| 4 | data | **hold** standing **and** `no_expiry_set` + URL |
| 5 | kb | **hold** `INSUFFICIENT_EVIDENCE`; no count |

No `CONTRACT VIOLATION` line. Transcript unedited in this directory.

## Not verified this sitting

- Isolated-home `load_keys()` export-precedence (Ka'el's claim; I did not rerun it).
- That Vercel is serving `f2c9f122…` (GitHub has it; I did not hash the live lambda).
- Key rotation.

This is a breaker-clean loop on the changed CLI. Copy into `evidence/` if the article should cite v8.
