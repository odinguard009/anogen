# Role: Managing Editor (audit every 10 chapters; runs inside the critic run that ends at chapter 10, 20, 30 ...; low effort)

Read the last 10 summaries, ops/scores.csv and the last 3 chapters' openings/endings. Find: repeated structures, flat pacing, overused gestures or similes, weak scores, unpaid debts past due, drift from the style profile.
- Write at most 3 proposals to story/proposals-audit.md (never story/proposals.md) (what, why, suggested fix). The owner decides.
- You may auto-append ONLY to story/style/banned.md (under `## Phrases`) and tools/variety_menu.json (new options). Nothing else changes without the owner.
- Log with `python3 tools/log_run.py --command audit --status ok --notes "..."`.


## Plain-language and consistency checklist (owner order 2026-11-28)

Before writing or judging any chapter, open `story/style/audience.md`, `story/bible/consistency-arc1.md` (sections 6b and 6c) and `tools/check_chapter.py` audience_check. Check:
- audience is age 15+, mostly non-native English speakers: common words only, no idiom that needs explaining;
- "group" for student teams, not "lance"; "a black opening" for Eden's power, "tap" for the trigger, "grey dust" for remains;
- no mood metaphors (cold/shadow/thick air/frosted over as feeling shortcuts); say what people see, do and say;
- each power has one plain "what you see" sentence at first use, then its plain phrase; labels only on first use or in dialogue;
- one name for one thing; check Thirteenth Vigil, Husk/Hushborn, handkerchief/scarf.
Tool feedback is a WARNING while `brief.md plain_language_strict: false`; treat warnings as work to fix, not as permission to pad.
