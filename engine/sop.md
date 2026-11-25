# SOP: autonomous operation (owner's order 2026-11-25)

Goal: the owner gives one command ("lanjutkan", "kerjakan N bab", "generate 1 arc ...") and the engine runs to the end with NO questions and NO approval requests. This SOP never overrides LOCKED SETTINGS in CLAUDE.md or the hard content rules.

## 0. Owner's standing authorization (2026-11-25)
The owner always grants permission for any access and any action needed for the Anogen project (repo read/write/push, web access, editing any project file, publishing the reading page, running scripts, committing). Do not ask for approval for these; just do them. Scope: the Anogen project only. It does not unlock the hard content limits, the LOCKED SETTINGS, the STOP list in section 4 (irreversible and ambiguous actions), or anything outside the project. Note: the owner's authorization is recorded here, but a denial by the tool permission system can still happen; it is not something this file can override. When it happens, follow section 5 (one safer variant, log in ops/blocked.md, continue, tell the owner once what to allow).

## 1. Golden rules
1. Do not ask the owner anything unless a case in section 4 (STOP list) applies. For every other doubt: pick the default in section 3, log it in ops/decisions.md (one line: date, doubt, choice), continue.
2. Never end a turn with an offer or a question ("mau saya ...?"). End with a result report (section 6) or, if work remains and nothing blocks it, keep working.
3. OWNER ORDER 2026-11-25 (permanent): NEVER spawn sub-agents; the orchestrator performs each role itself, inline, one role at a time (AGENTS.md locked setting 13). Older text in this file about agents applies to roles done inline. Original rule: use an agent only when the step needs one (writer, critic, audit, development editor, readability rewrite). Maximum ONE agent at a time, never a sub-agent inside an agent (put "Do not spawn any subagent" in every agent prompt). Anything a script can do (checks, status, commits, EPUB, state) is done by the orchestrator with scripts, not by an agent.
4. Locked settings (one bot per job, model per bot, batches of 5, schedule OFF, content limits, arc EPUB only when complete, no re-opening approved bible decisions) are never changed by this SOP or by the orchestrator's own judgment.

## 2. Standard loop (every command)
1. `engine_state.py batch-resume` (or batch-start for a new batch), `lock.py status`, `precheck.py`, `engine_state.py next`.
2. Run the Production flow in CLAUDE.md: dev editor if needed -> writer(5) -> writer(5) -> verify_batch -> critic over those 10 (+ audit) -> save -> next batch. Repeat while `continue` is true.
3. After each agent: release its lock, verify with `git status -sb`, `git log`, `check_chapter.py` on its chapters. Fix mechanical failures by giving the same agent range a retry once; if it still fails, log it in ops/blocked.md and move on.
4. After each batch: publish/update the reading page (section 5). Commit and push everything (`tools/save.py`).
5. Stop only when `continue` is false, a quota/limit is hit, or a STOP-list case happens. Then report.

## 3. Defaults for common doubts (decide, log, continue)
- Chapter slightly outside word range: fix with the checker's advice; do not ask.
- Conflict between a chapter idea and canon: canon wins; write the conflict to story/proposals-audit.md (never into approved proposals).
- Owner style feedback in chat (language too hard, too slow, too much X): update story/style/profile.md (and brief.md if the audience changes). The new style applies to chapters written from now on. Do NOT rewrite already written chapters unless the owner explicitly orders a rewrite (a rewrite costs about as much as four writer batches).
- Owner idea ("ide: ..."): `inbox.py add`, one-line confirmation, it is developed at the next planning.
- Agent report says "short chapter", "quiet ending", "debt dropped from cap": log in ops/decisions.md; the next critic/audit handles it. No question to the owner.
- The critic runs once per 10 chapters (owner order 2026-11-25); never skip it silently. If quota is short, run the critic first and the writer later.
- Readability targets (checker values): average sentence 8-13 words, dialogue 25-35% in normal chapters, words 1800-2500.
- Quota hit or agent died: `batch-stop --reason`, commit what exists, report; resume later with "lanjutkan".

## 4. STOP list (the only reasons to ask the owner)
- Anything irreversible and ambiguous: deleting repo/branches/history, force-push, enabling the schedule (only on "hidupkan jadwal"), changing locked settings, re-opening approved bible decisions.
- A content-limit question (sexual content, ecchi, harem) or copying an existing work.
- The permission system denies an action (see below). Never work around a denial.

## 5. Blocked actions (permission denied, tool missing, publish fails)
1. Do not retry in a loop and do not look for a workaround that bypasses the denial. Try at most one safer variant of the same action (for example read access instead of push).
2. Write the blocked item to ops/blocked.md (date, action, reason, what is needed), commit it, and continue every step that does not depend on it. Example: if the reading page cannot be published, the chapters stay in the repo and the batch continues.
3. Report the blocked items once, at the end, with the single thing the owner needs to do (for example, allow the action in the permission prompt). When the owner says "lanjutkan" again, retry blocked items first.
4. Reading page: run `python3 tools/build_reading_page.py` (builds out/reading-page.html from chapters/*.md; chapter text never passes through the model) and publish that file with whatever page-hosting tool the AI has; record the URL in ops/reading-page.txt. If publishing is blocked, treat it as a blocked action.

## 6. Reporting format (Indonesian, phone-friendly)
- 3-6 lines: what was finished (chapters, state), what is blocked or unverified, the one action needed from the owner (or "tidak ada"). No flattery, no step-by-step recap, no questions unless STOP list.
- Never state results of an agent before its report is read and verified with git/scripts.

## 7. Session hygiene
- NO per-session batch limit (owner order 2026-11-25, replaces the earlier two-batch rule). Run to completion with no dialog; report once at the end. If quota hits or the chat grows too long, commit, push, `batch-stop`, and report.
- Token discipline in CLAUDE.md applies. If the conversation grows long, finish the current chapter, commit, push, and tell the owner to say "lanjutkan" in a fresh chat (state lives in ops/engine.json).
- SAVING TOKENS (owner order 2026-11-25): (a) never re-read a file already read in this session unless it changed; (b) the writer reads story/bible/writer-digest.md instead of long bible files (keep it in sync with power-system.md); (c) run `tools/archive.py` at every audit; (d) one fresh session per two writer batches (about 10 chapters, the critic range) rather than one huge session: before ending, commit, push, and say "lanjutkan" in a new chat; (e) mechanical jobs (rename, format, bookkeeping) are done with tools/ scripts, not by rewriting text.
- Keep ops/decisions.md and ops/blocked.md short; the managing editor trims them at each audit.
