# Anogen: private AI novel engine (vendor-neutral instructions)

This file is the single source of truth for ANY AI that operates this repo (Claude, ChatGPT/Codex, Gemini, etc.). CLAUDE.md only points here. Read ops/sop.md and ops/PORTABILITY.md as well.

Owner: Odin (Indonesian; not a coder). Talk to him in Indonesian: concise, direct, no flattery, no fabrication, phone-friendly. Stories are written in English at LEARNER LEVEL (see story/style/profile.md, section LEVEL). The owner never touches code: you run every command, commit and push.

Words used here: "agent" = a separate AI run (own context) that does one job and returns a report. "strong tier" / "standard tier" = model classes mapped to real models in ops/models.json. The "orchestrator" = the AI the owner talks to; it runs scripts, spawns agents, commits, sends files, and never writes chapters itself.

## Layout
- tools/: scripts (0 tokens). story/: story pack (brief, style, bible, outline, inbox). roles/: instructions per role. chapters/: chapter-NNN.md. ops/: engine.json, models.json, schedule.json, run-log.md, scores.csv, sop.md, decisions.md, blocked.md. out/: EPUBs and the reading page.
- Style lives only in story/style/profile.md (swappable). The engine is genre-neutral.

## Hard rules
- No sexual content, no ecchi, no harem. Pure slow-burn romance, light comedy that never undercuts key scenes.
- Never copy text, scenes, characters or worlds from existing works. Research is for ideas and technique only.
- Never overwrite canon. Conflicts go to story/proposals-audit.md (approved decisions are in story/proposals.md and are never re-opened without the owner's order).
- Never enable the schedule unless the owner says "hidupkan jadwal".
- Chapter words: see story/brief.md Machine settings. Chapter format: `# Title`, scene breaks `* * *`.
- An arc EPUB is built ONLY when the arc is complete (tools/build_epub.py enforces the gate). A partial EPUB only when the owner asks.

## Commands (owner's Indonesian phrases)
- "mulai cerita baru" (+ seed or "bebas"): development editor (strong tier) builds the story pack and plans arc 1 (roles/development-editor.md); commit and push; do not write chapters unless asked.
- "tulis bab berikutnya", "kerjakan N bab" (`engine_state.py batch-start --mode n --target N`), "generate 1 arc maksimal N bab" (development editor plans the arc: `engine_state.py arc-plan K --start S --end E --max N`; then `batch-start --mode arc --arc K --max N`): run the Production flow.
- "ide: ..." / "belokkan arah: ...": `python3 tools/inbox.py add "text"`; confirm in one line.
- "laporan": `python3 tools/status.py`; 3-6 lines.
- "hidupkan jadwal" / "matikan jadwal": `python3 tools/schedule.py enable|disable` (scheduler tool of the host AI; tell the owner what is unverified).
- "lanjutkan": FIRST check ops/rewrite-queue.md: if any range is not DONE, run the rewrite for the first such range (prompt ops/rewrite-prompt.md, one agent, standard tier, under the lock); keep going batch after batch with no per-session limit (owner order 2026-11-25). Otherwise: `engine_state.py batch-resume`; retry items in ops/blocked.md first; `check_chapter.py` on the highest chapter and `precheck.py`; `lock.py status`; `engine_state.py next`; continue the Production flow. If critic_pending exists, run the critic before more writing.

## Production flow (strictly sequential: ONE agent at a time, never parallel, never a sub-agent inside an agent)
0. `python3 tools/engine_state.py next` -> `writer_range` (at most 5 chapters; clamped before any existing chapter, see `gap_note`), `critic_pending` (only set when a critic range of 10 chapters is due; `critic_waiting` otherwise), `critic_changed_after_review`, `audit_with_critic`, `audit_due_at`. If `lock.py status` is busy, spawn nothing.
1. If the outline lacks the chapters or story/inbox.md has ideas: development editor first (strong tier, under the lock).
2. WRITER: `python3 tools/lock.py acquire write --owner writer`; spawn ONE agent, standard tier. Prompt = ops/batch-writer-prompt.md + "Your range: chapters A-B." + the commit trailer lines (see ops/PORTABILITY.md). When it ends: `lock.py release write --owner writer`; log its usage with `python3 tools/usage_log.py add --role writer --range A-B ...` (token counts only if the host reports them; otherwise omit, never guess); verify with `git log`, `git status`, `python3 tools/verify_batch.py A-B`; if it died (quota): `engine_state.py batch-stop --reason "..."`, commit what exists, report.
3. CRITIC (+ AUDIT), once per 10 chapters (owner order 2026-11-25: critic per 10 chapters, i.e. after every second writer batch; replaces the earlier "after each 5-chapter batch"): run it only when `critic_pending` is set (it is, when 10 chapters are ready, when a batch ends, or at arc end). First `python3 tools/verify_batch.py A-B` (deterministic go/no-go; fix or retry the writer on problems). Then `lock.py acquire critic --owner critic`; spawn ONE agent, strong tier. Prompt = ops/batch-critic-prompt.md + "Your range: A-B." (use `critic_pending`; add "Audit duty: yes" when `audit_with_critic` or `audit_due_at` is set). The critic runs `tools/prepass.py` first. Then `lock.py release critic --owner critic`; only if `git log` shows the "critic pass chapters A-B" commit: `engine_state.py mark critic B`; if an audit commit exists: `engine_state.py mark audit B`. Chapters changed after their review (`critic_changed_after_review` = `rereview_pending`) are an editorial task that blocks `writer_range` until done: spawn the critic (strong tier, under the lock) with "Re-review only: X, Y" (no full 10-chapter pass needed; if `critic_pending` is also set, add them to that run), then record exactly those chapters with `engine_state.py rereview X Y` (it updates hashes only for the chapters listed; `mark critic` never blesses edited chapters).
4. `python3 tools/save.py "..."` for anything left; `engine_state.py next`.
5. Reading page: `python3 tools/build_reading_page.py` and publish out/reading-page.html with the host AI's page tool; record the URL in ops/reading-page.txt. If blocked, log it in ops/blocked.md.
6. NO SESSION LIMIT (owner order 2026-11-25): keep running batches until the target or `continue` is false, a quota/limit is hit, or a STOP-list case happens. State survives in ops/engine.json. Report only at the end, in 3-6 lines.
Arc end: when `next` says the arc is fully written, run the critic on `critic_pending` (all of it still unreviewed), then `arc-complete K`, `build_epub.py --arc K`, save, and send out/arc-K.epub to the owner.
If the AI cannot spawn separate agents at all, run each role as a fresh, separate session of the correct tier, one at a time (ops/PORTABILITY.md). Never let the same session write and critique the same chapters.

## LOCKED SETTINGS (owner's orders 2026-11-25; change only if the owner explicitly says so in plain words)
1. One agent at a time per job (tools/lock.py). 2. Model tier per role as in ops/models.json. 3. Sequential writer batches of 5 chapters, commit per chapter; critic pass per 10 chapters (owner order 2026-11-25, replaces critic per 5); the managing-editor audit runs inside the critic run that ends at chapter 10, 20, 30... (merged by the owner's order). 4. Schedule OFF unless the owner says "hidupkan jadwal". 5. Story text in English at learner level; chat replies to the owner in Indonesian. 6. Content limits (no sexual content/ecchi/harem). 7. Arc EPUB only when the arc is complete. 8. Never re-open settled bible decisions. 9. Style changes apply forward only; rewrite old chapters only on the owner's explicit order. 10. (REMOVED by the owner 2026-11-25: no limit on batches per session; run to completion without dialog.) 11. The owner's standing authorization for all project actions is in ops/sop.md section 0. 12. Permanent style orders (2026-11-25), all in story/style/profile.md and never to be weakened by any writer: LEVEL (simple English, at most one easy idiom per chapter), CLARITY AND PICTURE (name budget, linked sentences, dialogue 25-40%, scene/character/fight description, say the plan), SCENE FEEL AND ARMOR (one clear mood per scene; every armor moment shown per story/bible/armor.md), HUMAN FEEL (must not read as AI-written).

## Token discipline
Agents read only what their prompt lists. Writers use `context_pack.py --part static` once per batch and `--part delta` per chapter. Critics start from `prepass.py`. Archive old summaries and logs with `tools/archive.py` at each audit. Do not re-read files; do not recap steps to the owner.
