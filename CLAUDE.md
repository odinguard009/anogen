# Anogen (Claude entry point)

All instructions are in AGENTS.md (single source of truth, vendor-neutral). Read it fully first, then engine/sop.md and engine/PORTABILITY.md. @AGENTS.md

In Claude Code: NEVER start sub-agents (owner order 2026-11-25, permanent; do not use the Agent tool): perform each role yourself, inline, one at a time. Commit trailers use the lines the session supplies; the reading page is published with the Artifact tool.
Advisor exception (owner order 2026-11-26): the `advisor` tool may be used often (one consult at a time, advice only). It is the only exception. Never use the Agent tool. HOLD: run `python3 tools/engine_state.py next` first; if it reports a hold, write nothing.
