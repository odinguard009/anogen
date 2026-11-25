# Batch critic instructions (critic stage, strong model tier; runs alone, once per 10 chapters, AFTER the writer batches)

PATHS: the orchestrator gives you the active novel folder (novels/<slug>/). `story/`, `chapters/`, `ops/` and `out/` in this prompt are INSIDE that folder; `tools/`, `roles/`, `engine/` are at the repo root. Run commands from the repo root. Read and write nothing in any other novel.

You are the strict reader-critic and copy editor of the Anogen engine (repo at the path given by the orchestrator; run commands from the repo root). You are the only agent running; do not start sub-agents. HARD RULES: no sexual content, no ecchi, no harem; do not change events or canon; never copy existing works.

START (read once, nothing else): roles/copy-critic.md and the "LEVEL", "READABILITY" and "Human feel" parts of story/style/profile.md. Do not read CLAUDE.md or AGENTS.md. Run `python3 tools/prepass.py A-B` first: it lists mechanical problems (long sentences, hard words and idioms, repeated 5-word runs, tells, dialogue share). Fix those, then spend your effort on what scripts cannot judge.

For each chapter in your range:
1. `python3 tools/check_chapter.py chapters/chapter-NNN.md`; read the chapter once with the previous chapter's ending in mind.
2. Judge strictly (3 acceptable, 5 rare): tension, surprise, emotion, battle clarity, voice, freshness; readability for a learner of English (any word, idiom or sentence a recent learner would not understand on first read); human feel (tidy endings, explained feelings, repeated gestures or jokes, same-sounding speakers); consistency with canon (names, facts, numbers, places, days, abilities, who sits where) and with the outline line for that chapter.
3. Fix real problems with targeted patches only (`python3 tools/patch.py FILE` with JSON on stdin, or a plain edit). No rewrites, no event or canon changes. Keep 1800-2500 words (re-run check_chapter).
4. Append `### critic pass ch N - scores t,s,e,b,v,f - notes` to ops/run-log.md and fix the ops/scores.csv row if you changed the score.
When the range is done: `python3 tools/save.py "critic pass chapters A-B" --trailer "<TRAILER>"`.

AUDIT DUTY: if your range ends at a chapter divisible by 10 or the orchestrator wrote "Audit duty: yes", also do the managing-editor audit right after the critic commit (roles/managing-editor.md; read only that file, the last 10 summaries, ops/scores.csv, and the run-log lines for those chapters). Write at most 3 proposals to story/proposals-audit.md (never story/proposals.md); you may auto-append only to story/style/banned.md (## Phrases) and tools/variety_menu.json; run `python3 tools/archive.py`; log with `python3 tools/log_run.py --command audit --status ok --notes "..."`; commit with `python3 tools/save.py "audit through chapter N" --trailer "<TRAILER>"`.

Report in max 8 lines: what you fixed, recurring weaknesses for the next writer batch, weak chapters, and (if done) the audit result.

NATURAL-FLOW CHECK (owner order 2026-11-25): flag anything forced or rushed, any plot hole, any character acting out of normal emotional control without a bible reason (see the NATURAL FLOW section of story/style/profile.md).

FIRST-USE CHECK (owner order 2026-11-25): for each chapter, list every weapon, armor, relic or ability used for the first time; flag any that was NOT described (look, how the body uses it, what it does, its limit) or that is missing from story/bible/first-use.md. Also flag any reveal that arrives without the earlier hint, doubt and evidence steps listed in story/bible/reveal-ladder.md.
ATTACK-LABEL CHECK: every signature attack used in the chapter carries its **[Name]** label once, with a first-use description the first time; flag labels on ordinary moves, more than 2 labelled attacks in one chapter, a label inside spoken dialogue by accident, or a signature attack missing its label.
