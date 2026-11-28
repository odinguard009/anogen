# Self-review checklist (one chapter; run right after writing it; same session, no extra agent)
COLD READ first: judge the manuscript text itself as a first-time reader; use only the outline line and canon rows in the pack; do not assume your writing reasoning was right and do not defend it; report concrete problems only (quote the line); no line to point at = not a finding.
Answer each line for the chapter in `review_pack.py`. Judge the TEXT, not your intentions. Do not re-analyse at length.
1. Does it follow the outline line (goal, conflict, payoff, hook)?
2. Do characters act in character and like normal people (emotions controlled unless the bible says eccentric)?
3. Is the dialogue natural, each speaker different?
4. Does the story move (something changes)?
5. Any repeated scene, gesture, joke or phrase from recent chapters?
6. Pacing: no rush, no padding.
7. Continuity: names, places, injuries, who-knows-what match State, Debts, Secrets and the pack.
8. Does the ending pull the reader on?
9. Length in range; heading format right (check_chapter.py).
10. Canon kept: no new power, armor or reveal outside the ladder and first-use rules.
Output format (max 6 lines): `REVIEW ch N: PASS | WARNING | NEEDS_REVISION` then only the important findings. Fix NEEDS_REVISION items with targeted patches (tools/patch.py), re-run check_chapter.py, then write one line in ops/run-log.md. Risk level from tools/risk.py sets the depth: LOW = lines 1, 5, 7, 9 only; MEDIUM = all ten; HIGH = all ten plus read the whole chapter twice and check every reveal, death, power change against the ladder and first-use ledger.


## Plain-language and consistency checklist (owner order 2026-11-28)

Before writing or judging any chapter, open `story/style/audience.md`, `story/bible/consistency-arc1.md` (sections 6b and 6c) and `tools/check_chapter.py` audience_check. Check:
- audience is age 15+, mostly non-native English speakers: common words only, no idiom that needs explaining;
- "group" for student teams, not "lance"; "a black opening" for Eden's power, "tap" for the trigger, "grey dust" for remains;
- no mood metaphors (cold/shadow/thick air/frosted over as feeling shortcuts); say what people see, do and say;
- each power has one plain "what you see" sentence at first use, then its plain phrase; labels only on first use or in dialogue;
- one name for one thing; check Thirteenth Vigil, Husk/Hushborn, handkerchief/scarf.
Tool feedback is a WARNING while `brief.md plain_language_strict: false`; treat warnings as work to fix, not as permission to pad.
