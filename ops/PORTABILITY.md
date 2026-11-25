# Running Anogen with another AI (owner's order 2026-11-25)

The repo is self-contained: instructions (AGENTS.md), settings (ops/models.json, AGENTS.md LOCKED SETTINGS), state (ops/engine.json, story/), scripts (tools/, Python 3 standard library only). Any AI that can do the following can run it exactly as Claude does.

## What the AI must be able to do
1. Read and write files in the repo, run `python3`, and `git commit` + `git push` (the repo is public on purpose).
2. Run separate, fresh AI sessions for the roles (writer, critic, audit), one at a time. If the host has sub-agents, use them. If not, open a separate fresh session/chat per role and paste the role prompt (ops/batch-writer-prompt.md, ops/batch-critic-prompt.md); never let one session write and then critique its own chapters.
3. Send files (EPUB) and publish a page (reading page) to the owner, or tell the owner where the files are in the repo (out/).
4. Talk to the owner in Indonesian.

## First message to give a new AI
"Read AGENTS.md, ops/sop.md and ops/PORTABILITY.md in the repo odinguard009/anogen and follow them. Then: lanjutkan."

## Mapping
- Model tiers: ops/models.json "tiers". strong = development editor, critic, auditor; standard = writer, canon keeper, orchestrator. Pick the vendor's equivalents; the quota weight is unverified, so measure.
- Commit trailer: use "Co-Authored-By: <model name> <noreply@...>" with your own model name; any session link line is optional.
- Locks: always `tools/lock.py acquire/release` around every agent.
- Tools that are Claude-specific in AGENTS.md are described by function only (spawn an agent, publish a page, send a file).

## Switching checklist
1. `git pull`; `python3 tools/status.py`; `python3 tools/engine_state.py next`.
2. Read ops/blocked.md and ops/decisions.md.
3. Run one batch; compare chapter quality with the previous chapters (style: story/style/profile.md LEVEL).
4. If quality drops, tell the owner which role is weak (do not silently change locked settings).
