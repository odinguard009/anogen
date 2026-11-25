# Rewrite queue v3 (owner's order 2026-11-25: rewrite chapters 1-22 with the new style rules; none may be skipped)
Prompt: ops/rewrite-prompt.md. One agent at a time, standard tier (Sonnet). Ranges of 5 chapters = one batch. No per-session batch limit (owner order 2026-11-25). "lanjutkan" runs the first range not marked DONE here BEFORE any new chapter is written. Nothing new is written (chapter 23+) until every range below is DONE.

- 1-5: DONE (2026-11-25)
- 6-10: DONE (2026-11-25)
- 11-15: DONE (2026-11-25)
- 16-20: DONE (2026-11-25)
- 21-22: DONE (2026-11-25)

Rewrites change the chapter text, so the chapters are marked as edited after their critic review (`engine_state.py next` lists them in `rereview_pending` and writes nothing new until they are re-reviewed). A rewrite therefore costs the rewrite agent PLUS a strong-tier critic re-review of those chapters (`engine_state.py rereview N ...` afterwards). Owner decision 2026-11-25 for the already finished 1-22 rewrite: accepted without re-review (baseline-reviewed).
