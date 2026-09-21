# Surface recheck — 2026-09-21

The v7 verdict ends "Do not ship yet." That blocker referred to **stale census copy** on two public
surfaces at the time it was written: `README.md` and `web/index.html` still said "fourteen findings
from eight outside engineers."

Corrected afterward. Current state:

```
README.md         12 raised by the 8 outside engineers, 2 internal
web/index.html    12 raised by eight outside engineers, 2 internal
```

**The v7 verdict is left unedited as historical evidence.** It was accurate when written.

## Latency

`../web-latency-2026-09-21.json` records five anonymous POSTs to the live deployment with wall-clock
timing around each request. Range on that run: **13.8–33.8 seconds**. An earlier informal set of
runs produced a narrower range; the article cites the recorded one.
