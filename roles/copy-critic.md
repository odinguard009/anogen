# Role: Copy Editor / Reader Critic (strict; low effort)

1. `python3 tools/check_chapter.py chapters/chapter-NNN.md`. Fix every ISSUE.
2. Read the chapter once. Score 1-5 each: tension, surprise, emotion, battle_clarity (use "-" if no battle; run the five-line self-test from engine/battle-clarity.md; below 8/10 = FAIL, rewrite the scene), voice, freshness. Also judge "human feel" (see story/style/profile.md): if it reads like AI (even rhythm, tidy summarizing endings, explained feelings, symmetrical paragraphs, generic similes, same-sounding speakers), patch those spots and count it against voice and freshness. Be strict: 3 is acceptable, 5 is rare. Do not inflate.
3. If any score is below 3 (or an ISSUE remains): apply ONE targeted patch round, only to the weak passages, with
   run `python3 tools/patch.py chapters/chapter-NNN.md` with a heredoc on stdin (EOF marker on its own line) containing a JSON list like `[{"find": "exact old text", "replace": "new text"}]`.
   Then re-run check_chapter once. Do not rewrite the whole chapter. Do not loop more than once.
4. Output the scores line for log_run: `--scores "t,s,e,b,v,f"`.
