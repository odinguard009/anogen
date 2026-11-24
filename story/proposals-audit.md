# Audit proposals (managing editor, max 3 per audit; owner decides)
(story/proposals.md is the approved bible decision record; do not append to it.)

## Audit through chapter 10 (2026-11-25)
Scores ch 1-10: tension 3 in 7/10 chapters, never above 4; surprise 3-4; voice and freshness steady at 4 (ch 7 freshness 3). No debts past due (earliest: gray-coat man ch 11-24, Seal/hooded youth ch 13-24).
Auto-applied: banned.md (+"for a long moment", "something went/crossed across his/her face", caps on "for a long time", "for some time", "the way it/she/he did", "the way some", "as people do"); variety_menu.json (+13 options: comic devices away from Rowan/Felix, uneven pacing, late-cost hook, etc.).

### A1. Rest the food gag; give Rowan a second note
- What: food/"eaten" beats in ch 2, 5, 6, 7, 9, 10 (Felix's "Eaten today?", honey-cake, Lance lunch, King's eggs). Rowan has appeared only as loud, warm, friendly (ch 6, 7, 10).
- Why: a running gag touched in 6 of 10 chapters stops being a gag; Rowan reads as one note just before his circled-name debt (ch 18-24) needs the reader to fear for him.
- Fix: the outlined food beats in ch 12, 14, 15 are the gag's whole quota for ch 11-20; no incidental food jokes elsewhere in that span. Give Rowan one quiet or off-key beat (alone, tired, or wrong about something) by ch 17, inside existing outline scenes; no plot change.

### A2. Break the even rhythm and the "and..., and..." chains
- What: polysyndeton chains (", and ..., and") hit 12-14 times in ch 7, 9, 10; stare-duration beats ("for a long time/moment", "for some time") in 5 of 10 chapters, including the ch 9 climax; ch 10 check: sentence-length variation flagged by check_chapter.py.
- Why: the owner's top priority is prose that does not read as AI-written; these are the main tells left after the critic passes.
- Fix: add to ops/batch-writer-prompt.md a self-check: max 5 "and..., and" chains per chapter; one deliberate rhythm break (fragment run or racing run-on) per scene. Optional tool change: have check_chapter.py warn on more than 6 chains.

### A3. A real spike with a cost by ch 13
- What: ch 8, 9, 10 all end on a quiet line or held object (Strent's line, "Watch the Tallis boy", folded handkerchief); fights so far are flex/puzzle (battle_clarity 3 in ch 4, 9, 10); no strained or costly fight yet against the profile's 25%/10% mix.
- Why: tension sits at 3; three quiet hooks in a row flatten the run into ch 11.
- Fix: keep the ch 11 "threat" hook sharp (shown, not reported); in ch 13 the Long Stair kill should cost Eden something visible (an injury, a lost tool, or a near-miss Lysette later reads). Battle clarity: one sentence of terrain/geometry before each exchange.
