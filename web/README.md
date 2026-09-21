# Ask the record

A judge-facing front door for a public Sanity record. Three things it does that a keyword search
cannot:

- answers from the record or returns `INSUFFICIENT_EVIDENCE` — never from the model's own knowledge
- keeps `status` and `expiry` as separate facts (`no_expiry_set` is not "permanently true")
- reports the receipts that exist, not the number claimed

Questions are an allowlist — the five an independent reviewer graded. That fixes *which* question
can be asked; it does not limit how many times.

**On rate limiting, measured rather than assumed.** `api/ask.py` carries a per-instance throttle.
Eight simultaneous requests on 2026-09-20 all returned 200, because Vercel gave each request its
own instance and therefore its own counter. It slows a naive sequential loop and does nothing
against parallel load. **It is a speed bump, not a control, and is documented as one.** The only
hard ceiling on spend is the budget cap set on the model project.

    api/ask.py     serverless function; holds the credentials, runs the MCP + model loop
    index.html     static page; never sees a key

Environment variables (set in Vercel, never committed):

    SANITY_CONTEXT_TOKEN   org-level, Context Viewer
    GEMINI_PAID_KEY        model key

Routing follows the frozen contract: identifier lookups (`claim-*`) go to the GROQ dataset
endpoint, prose questions go to the Knowledge Base. One instrument per question — Sanity silently
drops a Knowledge Base if a dataset is attached to the same endpoint.

Project `u58x3mt0` · Knowledge Base `kbjnxAgyAimV` · Studio https://self-correcting-systems.sanity.studio/
