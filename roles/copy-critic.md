# Role: Copy Editor / Reader Critic (strict; low effort)

1. `python3 tools/check_chapter.py chapters/chapter-NNN.md`. Fix every ISSUE.
2. Read the chapter once. Score 1-5 each: tension, surprise, emotion, plain_reading (engine/plain-reading.md; paraphrase test; below 8/10 = FAIL), battle_clarity (use "-" if no battle; run the five-line self-test from engine/battle-clarity.md; below 8/10 = FAIL, rewrite the scene), voice, freshness. Also judge "human feel" (see story/style/profile.md): if it reads like AI (even rhythm, tidy summarizing endings, explained feelings, symmetrical paragraphs, generic similes, same-sounding speakers), patch those spots and count it against voice and freshness. Be strict: 3 is acceptable, 5 is rare. Do not inflate.
3. If any score is below 3 (or an ISSUE remains): apply ONE targeted patch round, only to the weak passages, with
   run `python3 tools/patch.py chapters/chapter-NNN.md` with a heredoc on stdin (EOF marker on its own line) containing a JSON list like `[{"find": "exact old text", "replace": "new text"}]`.
   Then re-run check_chapter once. Do not rewrite the whole chapter. Do not loop more than once.
4. Output the scores line for log_run: `--scores "t,s,e,b,v,f"`.


## Plain-language and consistency checklist (owner order 2026-11-28)

Before writing or judging any chapter, open `story/style/audience.md`, `story/bible/consistency-arc1.md` (sections 6b and 6c) and `tools/check_chapter.py` audience_check. Check:
- audience is age 15+, mostly non-native English speakers: common words only, no idiom that needs explaining;
- "group" for student teams, not "lance"; "a black opening" for Eden's power, "tap" for the trigger, "grey dust" for remains;
- no mood metaphors (cold/shadow/thick air/frosted over as feeling shortcuts); say what people see, do and say;
- each power has one plain "what you see" sentence at first use, then its plain phrase; labels only on first use or in dialogue;
- one name for one thing; check Thirteenth Vigil, Husk/Hushborn, handkerchief/scarf.
Tool feedback is a WARNING while `brief.md plain_language_strict: false`; treat warnings as work to fix, not as permission to pad.
