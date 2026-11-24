# Anogen: private AI novel engine

Owner: Odin (Indonesian; not a coder). Talk to him in Indonesian: concise, direct, no flattery, no fabrication. Stories are written in English. The owner never touches code: you run every command, commit and push.

Everything runs strictly sequentially. No subagents inside the engine, no parallel agents. Batch independent tool calls in one turn.

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

### "tulis bab berikutnya"
0. If precheck warns that the previous chapter lacks bookkeeping, finish it (Canon Keeper) and `python3 tools/save.py "recover"` first.
1. `python3 tools/context_pack.py --extra world` (one call; characters are included; contains precheck, inbox, outline, state, style, last summaries).
2. If inbox has ideas or the outline lacks this chapter: roles/development-editor.md first.
3. Write: roles/lead-writer.md. Check and patch: roles/copy-critic.md.
4. Bookkeep: roles/canon-keeper.md.
5. `python3 tools/log_run.py --chapter N --words W --scores "..."`; then `python3 tools/save.py "chapter N: Title"`.
6. Every 10th chapter: roles/managing-editor.md.
Target 6-8 tool rounds per chapter. Read each file at most once; the pack already holds the context.

### "kerjakan N bab"
`python3 tools/engine_state.py batch-start --mode n --target N`, then loop "tulis bab berikutnya", calling `python3 tools/engine_state.py next` after each chapter; stop when `continue` is false. On quota or error: `batch-stop --reason "..."`, commit what exists, and report. A later "lanjutkan" runs `engine_state.py batch-resume` and continues from the lowest missing chapter.

### "generate 1 arc maksimal N bab"
Plan the arc (development editor) so it finishes within N chapters: `arc-plan K --start S --end E --max N`. Then `batch-start --mode arc --arc K --max N` and loop as above. When the arc is fully written: `engine_state.py arc-complete K`, `python3 tools/build_epub.py --arc K`, commit, push, and send out/arc-K.epub to the owner with the SendUserFile tool.

### "ide: ..." / "belokkan arah: ..."
`python3 tools/inbox.py add "text"`; confirm in one line. It is developed automatically at the next chapter or arc planning (foreshadowing at least 10 chapters ahead).

### "laporan"
`python3 tools/status.py`; summarize in a few lines.

### "hidupkan jadwal" / "matikan jadwal"
Use `python3 tools/schedule.py enable|disable`. Enable: create a scheduled task with the cloud scheduler tool (cron from `schedule.py cron`, prompt from ops/scheduled-task-prompt.md), then `schedule.py set-task-id ID`. Disable: delete that task, then `set-task-id none`. Changing times: `schedule.py set times "08:00,20:00"`. Tell the owner honestly what is unverified (quota use of scheduled runs, push ability).

### "lanjutkan"
`python3 tools/engine_state.py batch-resume`, then continue the loop. If an interrupted chapter exists (precheck warning), finish its bookkeeping first.

## Reading page (owner's standing choice)
The owner reads inside the chat app, not via downloaded files. After each finished chapter (in a batch: after the batch stops, one page with all new chapters), publish the chapter text as a reading page with the Artifact tool (use the Docs type if the session lists it, else a self-contained HTML page; call list_types and the guide first). Update the same artifact for later chapters of the same arc instead of making many pages. The page is a copy for reading; chapters/*.md stays the source of truth. Do not paste the link in text (the card shows it). The EPUB is still built per completed arc.

## Bots, models and the one-bot lock (owner's permanent rule)
- NEVER more than one bot (agent) running per job. Before spawning an agent: `python3 tools/lock.py acquire JOB --owner NAME`; if it says BUSY, do not start another. Release when it ends: `lock.py release JOB`. Stale locks (older than the TTL) are taken over automatically.
- Models per bot are in ops/models.json: development editor, copy critic and managing editor on Opus; lead writer (with canon bookkeeping per chapter) on Sonnet; the main chat is the orchestrator on Sonnet. Pass `model` explicitly when spawning an agent. Quota weight per model is unverified: measure and adjust.
- Chapter production in batches of 5, strictly sequential: (1) lead writer agent (ops/batch-writer-prompt.md) -> (2) copy critic agent (ops/batch-critic-prompt.md) -> commit; every 10 chapters: managing editor agent. One agent at a time, never overlapping.

## Token discipline
In a batch, each chapter should be done in as few rounds as possible; if the conversation grows long, finish the current chapter, commit, and tell the owner to say "lanjutkan" in a fresh chat (state survives in ops/engine.json). Do not re-read files. Do not summarize steps back to the owner. After a chapter, reply with one or two lines only.
