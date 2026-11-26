# Running Anogen with another AI (owner's order 2026-11-25)

The repo is self-contained: instructions (AGENTS.md), settings (engine/models.json, AGENTS.md LOCKED SETTINGS), state (ops/engine.json, story/), scripts (tools/, Python 3 standard library only). Any AI that can do the following can run it exactly as Claude does.

## What the AI must be able to do
1. Read and write files in the repo, run `python3`, and `git commit` + `git push`.
2. Perform every role yourself, inline, one stage at a time, in the one main session (owner order 2026-11-25, locked setting 13). Never start sub-agents, extra sessions or parallel runs; if the host offers them, do NOT use them. The same session writes and critiques, so the critic stage is a cold read of the text (engine/batch-critic-prompt.md) backed by tools/prepass.py, tools/verify_batch.py and the written checklists; it is not an independent reviewer.
3. Send files (EPUB) and publish a page (reading page) to the owner, or tell the owner where the files are in the repo (out/).
4. Talk to the owner in Indonesian.
5. Respect the HOLD flag (ops/engine.json; `python3 tools/start.py` and `engine_state.py next` show `hold`): write nothing until the owner clears it.
6. If the host offers an advisor or reviewer consult, use it often as advice only (AGENTS.md section Advisor consult; owner order 2026-11-26). It is not permission to start sub-agents.

## First message to give a new AI
"Read AGENTS.md, engine/sop.md and engine/PORTABILITY.md in the repo odinguard009/anogen and follow them. Then: lanjutkan."

## Mapping
- Model tiers: engine/models.json "tiers". strong = development editor, critic, auditor; standard = writer, canon keeper, orchestrator. Pick the vendor's equivalents; the quota weight is unverified, so measure.
- Commit trailer: use "Co-Authored-By: <model name> <noreply@...>" with your own model name; any session link line is optional.
- Mechanical work (renames, formatting, bookkeeping, archive) is done by the scripts in tools/, never by a separate AI session or a second model.
- Locks: always `tools/lock.py acquire/release` around every agent.
- Tools that are Claude-specific in AGENTS.md are described by function only (run a role stage, publish a page, send a file).

## Switching checklist
0. Run `python3 tools/start.py` first (it shows the HOLD state, due work, validation errors and the NEXT step).
1. `git pull`; `python3 tools/status.py`; `python3 tools/engine_state.py next`.
2. Read ops/blocked.md and ops/decisions.md.
3. Run one batch; compare chapter quality with the previous chapters (style: story/style/profile.md LEVEL).
4. If quality drops, tell the owner which role is weak (do not silently change locked settings).

## Entry files, capabilities and self-check (owner order 2026-11-26: any AI can be the brain)
- Entry files: AGENTS.md (read natively by Codex and most agents), CLAUDE.md (Claude Code), GEMINI.md (Gemini CLI). All three only point to AGENTS.md. For a chat AI with no file access, paste the "First message" above and give it the repo files (it needs a host that can read, write and run commands; without that it cannot run Anogen).
- Capabilities the host maps by function, never by product name: (a) run a shell command; (b) read/write files; (c) git commit and push; (d) publish the reading page (any page tool; if none, leave out/reading-page.html in the repo and tell the owner); (e) send a file (if none, say its path in out/); (f) an advisor or reviewer consult, optional (AGENTS.md, Advisor consult); (g) a scheduler, optional and only on "hidupkan jadwal".
- Style, POV, labels and dates live in the novel's files (story/style/profile.md, story/bible/calendar.md), not in any vendor setting. Where an instruction is not clear, pick the default, log it in ops/decisions.md, continue (sop.md section 1).
- Self-check before the first chapter: `python3 tools/test_tools.py` (expect ALL TESTS PASSED), `python3 tools/policy_check.py` (expect POLICY: OK), `python3 tools/engine_state.py next` (read the hold), `python3 tools/context_pack.py --part static --peek` (expect no TRUNCATED line). If one fails, fix or report it before writing.
- Never edit chapters, canon or locked settings from memory of a previous AI's chat: the repo is the only memory. At the end of every session: `python3 tools/save.py "..."` so the next AI sees everything.
