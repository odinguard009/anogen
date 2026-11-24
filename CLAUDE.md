# Anogen: private AI novel engine

Owner: Odin (Indonesian; not a coder). Talk to him in Indonesian: concise, direct, no flattery, no fabrication. Stories are written in English. The owner never touches code: you run every command, commit and push.

Everything runs strictly sequentially: ONE agent at a time (see 'Production flow' below). Never parallel agents. Batch independent tool calls in one turn.

## Layout
- tools/: scripts (0 tokens). story/: the story pack (brief, style, bible, outline, inbox). roles/: instructions per role, load only the one you need. chapters/: chapter-NNN.md. ops/: engine.json, schedule.json, run-log.md, scores.csv. out/: EPUBs.
- Style lives only in story/style/profile.md (swappable). The engine is genre-neutral.

## Hard rules
- No sexual content, no ecchi, no harem. Pure slow-burn romance, light comedy that never undercuts key scenes.
- Never copy text, scenes, characters or worlds from existing works. Research is for ideas and technique only.
- Never overwrite canon. Conflicts go to story/proposals.md.
- Never enable the schedule unless the owner says "hidupkan jadwal".
- Chapter words: see story/brief.md Machine settings. Chapter format: `# Title`, scene breaks `* * *`.
- An arc EPUB is built ONLY when the arc is complete (tools/build_epub.py enforces the gate).

## Commands (owner's Indonesian phrases)

### "mulai cerita baru" (+ optional seed idea, or "bebas")
Load roles/development-editor.md. Build the story pack (premise, characters, world, series arc, names, canon_names, style tweaks if he asks). Plan arc 1 (default max = arc_default_max). Commit and push. Do NOT write chapters unless asked.

### Production flow (used by "tulis bab berikutnya", "kerjakan N bab", "generate 1 arc", "lanjutkan")
You (main chat, Sonnet) are only the orchestrator. Do not write chapters yourself. Per batch, strictly in this order, one agent at a time:
0. `python3 tools/engine_state.py next` -> JSON: `writer_range` ([A,B], at most 5 chapters; null = nothing to write), `critic_pending` ([A,B] chapters without an independent critic pass), `audit_due_at`. If the lock is busy (`lock.py status`) do not spawn anything; tell the owner.
1. If the outline lacks the chapters or `story/inbox.md` has ideas: development editor first (roles/development-editor.md, model opus, as an agent, under the lock).
2. WRITER: `python3 tools/lock.py acquire write --owner writer`; spawn ONE agent with `model: "sonnet"`. Prompt = contents of ops/batch-writer-prompt.md + "Your range: chapters A-B." (replace `{SESSION_ID}` in the trailers with the current session id from your own commit trailer, and use the real repo path). When it ends: `lock.py release write`. Verify with `git log` and `python3 tools/status.py`; if it died (quota), `engine_state.py batch-stop --reason "..."`, commit what exists, report.
3. CRITIC: `lock.py acquire critic --owner critic`; spawn ONE agent with `model: "opus"`. Prompt = ops/batch-critic-prompt.md + "Your range: chapters A-B." (use `critic_pending`; same `{SESSION_ID}` substitution). Then `lock.py release critic`. Only if `git log -1` shows the "critic pass chapters A-B" commit: `python3 tools/engine_state.py mark critic B`. If it died, `batch-stop --reason`, commit leftovers, report.
4. AUDIT: if `audit_due_at` is set, spawn ONE Opus agent for roles/managing-editor.md (same lock procedure), then `engine_state.py mark audit N` (only if the audit finished; otherwise stop and report). Audit proposals go to story/proposals-audit.md, never to story/proposals.md.
5. Commit/push anything left (`python3 tools/save.py "..."`), run `engine_state.py next`; repeat from step 2 while `continue` is true. After each batch publish the reading page (below) and reply to the owner with one or two lines.
Single chapter ("tulis bab berikutnya"): same flow with a range of one chapter (writer range [N,N]); the critic runs on the next batch or when pending chapters reach 5.
Never run two agents at once, even for different jobs. Do not use `run_in_background` tricks to overlap.
If this session cannot spawn agents with a `model` parameter, or the orchestrator is not Sonnet, stop and tell the owner; do NOT write chapters in the main chat.
Arc end: when `next` says the arc is fully written, run the critic on `critic_pending`, then `arc-complete K` (it refuses until the critic pass covers the whole arc), `build_epub.py --arc K`, save, and send out/arc-K.epub with SendUserFile.

### "kerjakan N bab"
`python3 tools/engine_state.py batch-start --mode n --target N`, then loop the production flow; stop when `continue` is false. On quota or error: `batch-stop --reason "..."`, commit what exists, report.

### "generate 1 arc maksimal N bab"
Development editor plans the arc within N chapters (`arc-plan K --start S --end E --max N`). Then `batch-start --mode arc --arc K --max N` and loop the production flow. When the arc is fully written AND `critic_pending` is null: `engine_state.py arc-complete K`, `python3 tools/build_epub.py --arc K`, commit, push, send out/arc-K.epub with SendUserFile.

### "ide: ..." / "belokkan arah: ..."
`python3 tools/inbox.py add "text"`; confirm in one line. It is developed automatically at the next chapter or arc planning (foreshadowing at least 10 chapters ahead).

### "laporan"
`python3 tools/status.py`; summarize in a few lines.

### "hidupkan jadwal" / "matikan jadwal"
Use `python3 tools/schedule.py enable|disable`. Enable: create a scheduled task with the cloud scheduler tool (cron from `schedule.py cron`, prompt from ops/scheduled-task-prompt.md), then `schedule.py set-task-id ID`. Disable: delete that task, then `set-task-id none`. Changing times: `schedule.py set times "08:00,20:00"`. Tell the owner honestly what is unverified (quota use of scheduled runs, push ability).

### "lanjutkan"
`python3 tools/engine_state.py batch-resume`, then check for a half-written last chapter: `python3 tools/check_chapter.py chapters/chapter-NNN.md` on the highest chapter and `python3 tools/precheck.py` (summary/bookkeeping warning); if it fails, give that chapter [N,N] to the writer first. Then `python3 tools/lock.py status` (release a stale lock only if no agent is running), `python3 tools/engine_state.py next`, then continue the production flow. If critic_pending exists, run the critic before more writing. If precheck warns that a chapter lacks bookkeeping, have the writer agent finish it first.

## Reading page (owner's standing choice)
The owner reads inside the chat app, not via downloaded files. After each finished chapter (in a batch: after the batch stops, one page with all new chapters), publish the chapter text as a reading page with the Artifact tool (use the Docs type if the session lists it, else a self-contained HTML page; call list_types and the guide first). Update the same artifact for later chapters of the same arc instead of making many pages: record its slug/URL in ops/reading-page.txt (commit it) and reuse it. The page is a copy for reading; chapters/*.md stays the source of truth. Do not paste the link in text (the card shows it). The EPUB is still built per completed arc.

## LOCKED SETTINGS (owner's order, 2026-11-25; change only if the owner explicitly says so)
1. One bot at a time per job (tools/lock.py). 2. Model per bot as in ops/models.json. 3. Sequential batches of 5: writer (Sonnet) -> critic (Opus) -> commit; every 10 chapters managing editor (Opus). 4. Schedule OFF unless the owner says "hidupkan jadwal". 5. Story text in English; chat replies to the owner in Indonesian. 6. Content limits (no sexual content/ecchi/harem). 7. Arc EPUB only when the arc is complete (partial EPUB only when the owner asks for it). 8. Never re-open settled bible decisions (story/proposals.md approved by the owner) without his order.

## Bots, models and the one-bot lock (owner's permanent rule)
- NEVER more than one bot (agent) running per job. Before spawning an agent: `python3 tools/lock.py acquire JOB --owner NAME`; if it says BUSY, do not start another. Release when it ends: `lock.py release JOB`. Stale locks (older than the TTL) are taken over automatically.
- Models per bot are in ops/models.json: development editor, copy critic and managing editor on Opus; lead writer (with canon bookkeeping per chapter) on Sonnet; the main chat is the orchestrator on Sonnet. Pass `model` explicitly when spawning an agent. Quota weight per model is unverified: measure and adjust.
- Chapter production in batches of 5, strictly sequential: (1) lead writer agent (ops/batch-writer-prompt.md) -> (2) copy critic agent (ops/batch-critic-prompt.md) -> commit; every 10 chapters: managing editor agent. One agent at a time, never overlapping.

## Token discipline
In a batch, each chapter should be done in as few rounds as possible; if the conversation grows long, finish the current chapter, commit, and tell the owner to say "lanjutkan" in a fresh chat (state survives in ops/engine.json). Do not re-read files. Do not summarize steps back to the owner. After a chapter, reply with one or two lines only.
