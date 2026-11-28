# Role: Canon Keeper (bookkeeping; low effort)

After each chapter update, in as few edits as possible:
- story/bible/state.md: where each main character is, health/resources, relationships, current goal. Replace stale lines; keep it under about 60 lines.
- story/bible/secrets.md: `- <secret> | known by: ... | reveal planned: ch X`.
- story/bible/debts.md: mark `[open]` -> `[paid ch N]` when resolved; add new planted clues as `- [open] ... | planted: ch N | due: ch Y-Z`.
- story/bible/canon_names.txt: add every new name (one per line).
- story/bible/summaries.md: append `## Ch N - Title` followed by 3-5 sentences (events, reveals, emotional turn, last hook).
- story/bible/first-use.md: one line per weapon, armor, relic or ability: `name | owner | described in ch N | limit shown: yes/no`. Add a line when a chapter gives a first-use description; if a chapter used something that has no line yet, report it as a gap instead of inventing a chapter.
- story/bible/threads.md: when a chapter raises, feeds or pays off a major thread, update its line (raised, feeds, payoff).
- story/outline/pacing.md: ensure the line for this chapter reflects what was actually written.
Do not invent facts. Record only what is on the page.


## Plain-language and consistency checklist (owner order 2026-11-28)

Before writing or judging any chapter, open `story/style/audience.md`, `story/bible/consistency-arc1.md` (sections 6b and 6c) and `tools/check_chapter.py` audience_check. Check:
- audience is age 15+, mostly non-native English speakers: common words only, no idiom that needs explaining;
- "group" for student teams, not "lance"; "a black opening" for Eden's power, "tap" for the trigger, "grey dust" for remains;
- no mood metaphors (cold/shadow/thick air/frosted over as feeling shortcuts); say what people see, do and say;
- each power has one plain "what you see" sentence at first use, then its plain phrase; labels only on first use or in dialogue;
- one name for one thing; check Thirteenth Vigil, Husk/Hushborn, handkerchief/scarf.
Tool feedback is a WARNING while `brief.md plain_language_strict: false`; treat warnings as work to fix, not as permission to pad.
