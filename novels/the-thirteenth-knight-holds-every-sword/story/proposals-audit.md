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

## Audit through chapter 20 (2026-11-25)
Scores ch 11-20: tension 4 only in 13, 16, 17 (3 elsewhere; ch 18-20 flat at 3); freshness 3 in 8/10 (ch 1-10: 4 in 9/10); voice 3 in ch 18 and 20. Readability: sentence mean 7.6-8.7 (ok), no semicolons, no hard words found; but dialogue under 30% in 7/10 chapters (ch 18: 23%), and 2-5 sentences over 30 words in ch 14, 17, 19, 20. Days to the Ball are consistent in the text (ch 18 Sunday = 9 days; ch 19-20 Wednesday = 6 days). Lysette's red ears/stare are now under control (1 use in ch 11, critic cut the rest). No debt past due; due soon: Ashen card (24), Ledger/Ball (24-26), Seal and the hooded youth (by 24).
Auto-applied: banned.md (+caps: "eaten today" 1, "very" 8, "like a" 6, "nobody" 5, "ears went red" 1, "went pink" 1; ch 18-19 exceed these, ch 20 passes); variety_menu.json (+11 options: off-key loud character, no-food/no-forms comedy, countdown hook, etc.).

### B1. Chapters sit at the floor; freshness is slipping
- What: ch 16-20 were drafted at 1810-1873 words and only reached 1851-1937 after critic padding; 7/10 chapters under 1950. Freshness fell from 4 to 3. "very" 18-21 times in ch 18-19, "like a" 10 times in ch 19. Profile (30-45% dialogue) and ops/sop.md (25-35%) give different dialogue targets.
- Why: thin chapters plus filler intensifiers are the fastest way to read as AI-written and flat to a teen reader.
- Fix: in ops/batch-writer-prompt.md set the draft target to 2000-2300 words and require one world-only surprising detail plus one narrator opinion per scene. Align ops/sop.md's dialogue target to the profile (30-45% quiet, 25%+ fights). Writer self-check: no sentence over 30 words (ch 17, 20 broke it). Ch 21 (emotional) must still end on a sharp hook to lift tension before the 22-25 run.

### B2. Rest "Eaten today?" and the food beat for real
- What: audit A1 limited food beats in ch 11-20 to ch 12, 14, 15. Actual: 12 (catchphrase x2), 14, 15, 16 ("Eaten today?" + bun), 18 (pretzel), 19 (whole bake). Rowan's quiet/off-key beat (A1, due by ch 17) did not happen.
- Why: romance.md saves "Eaten today?" for the ch 349 payoff ("I'm not fine"); spending it every few chapters kills that moment. Rowan still reads one-note before the Ball, where the reader must fear for him.
- Fix: "Eaten today?" at most once per arc from now until ch 349 (next: ch 47 middle-name payoff); no incidental food jokes in ch 21-30 (ch 28 comic excepted). Give Rowan one quiet beat in ch 21 or 24 (e.g. alone before the Ball, knowing he is watched), inside existing scenes.

### B3. Bookkeeping holes: the debts cap, state.md, Isolde/Ysolde
- What: (a) the ch 11 writer dropped "Concord map: front bends | ch 20 | due 280-285" from debts.md to stay under the 2900-char cap; ch 20 then planted it and did not re-add it (only threads.md #11 keeps it). Also dropped: "core dust" detail (ch 5-8), Merrow's "which hall" plant (ch 20) was never logged. debts.md is at 2865/2900, so every new plant now pushes an old one out. (b) state.md header says both "Ball in ~5 days" and "~3 weeks before the Lantern Ball"; text says 6 days (Ball on Tuesday). (c) Isolde (ch 19 cooking-club president, minor) vs Ysolde (spymaster, major): one letter apart on a phone screen.
- Why: dropped plants become broken promises at ch 285; a wrong countdown in state.md will mislead the ch 21-24 writer.
- Fix: split debts.md into near (due within the next 60 chapters, keeps the cap) and a capless story/bible/debts-far.md for long-range plants; re-add the Concord map bend (ch 20 -> 285/290) and Merrow's hall question (ch 20 -> 25). Correct the state.md header to "Ball in 6 days (Tuesday)". Rename the minor Isolde (e.g. "Hedda Brune", check canon_names first) in ch 19 and canon_names.txt, and remove Isolde from the names.md pool. Owner decides; nothing renamed by the audit.

### C1 (critic pass 23-25). New debt: Eden owes Lysette ONE true answer "tomorrow"
- What: ch 25 adds Eden's promise to answer one question truthfully the next day (state.md has it; debts.md does not). The ch 26 outline (roof dance, handkerchief) does not include the answer.
- Why: a promise to the heroine made at the arc's peak must be paid, and the answer must not leak secrets due later (Witness light ch 50; true name and mother far later; secrets.md).
- Fix (owner/dev editor decides): add to debts.md as due ch 26-27, and add to the ch 26 or 27 outline line which question she asks and which true but limited answer he gives. Canon not changed by the critic.

### Owner orders 2026-11-25: power system, tech, reveals (dev editor)
- 2026-11-25 owner order: Bells 1-7 as grades (soldier, knight, officer, captain, master) (mana.md) -> Bells measure tank size only, never rank or who wins (power-system.md 1).
- 2026-11-25 owner order: Tenet tiers Spark/Shape/Edge/Crown/Sovereign as depth tiers (mana.md) -> descriptive stages of use (reacts, obeys, invents, spreads, rewrites), never a rank; avoid the words Spark/Edge/Crown for them on the page.
- 2026-11-25 owner order: "aura beats = a sliver of the Emperor's authority" (battle-craft.md, profile.md Battles and aura) -> aura is every trained knight's body field; an "aura moment" is a full raise; Eden's carries the Emperor's weight under it.
- 2026-11-25 owner order: "No guns" (mana.md) -> guns and cannon exist (Meridian Age, tech.md), fouled by mana fields and turned aside by aura. mana.md sentence edited.
- 2026-11-25 owner order: no class/job layer -> registry readings (Class, Jobs) assigned at the Bell Assessment, seen only by the owner; Eden registered Black Lancer, White Swordsman; live reading as the Thirteenth Vigil: Void Heir.
- 2026-11-25 owner order: gods.md "the Ten made worlds before worlds" -> deeper layer: the planet-mind Aiwa dreamed the Ten first; Myrrhen is her eldest; the Refusal is Aiwa's immune reaction (mother.md). No event changes.
- 2026-11-25 owner order: Trail "sees the path" (mana.md, cast-combat-1.md) -> he hears and feels the path, as in ch 11 (canon follows the chapter; no patch).
- 2026-11-25 owner order: forms named only (combat-style.md) -> technique vs signature attacks with **[Label]** (power-system.md 13); Eden's signatures: Lintel (25), Lampwick (49), Threshold (180).
- 2026-11-25 owner order: no peak state -> Unbind awakenings (power-system.md 14).
- 2026-11-25 owner order: Corentin reader reveal ch 38 (twists-1, arc-1) -> Thirteenth Vigil link ch 36, reader reveal ch 45; ch 4 and 10 patched (reveal-ladder.md).
- 2026-11-25 owner order: Seraphine rescue told as a joke in ch 4/7/10 -> told plainly in ch 35; ch 4/7/10 softened.
- 2026-11-25 owner order: Inead "short bright sword" that glows (ch 25) -> canon look (pale hand-and-a-half blade, does not shine); patch item 17.
- 2026-11-25 owner order: twists-1 T1-17 E 255 -> 254; T1-22 E 164 -> 162 (ladder gaps). T2-39 E 598 -> 593 pending arc 12 planning (twists-2 not edited).

- 2026-11-25 owner order: Door/Gate are names only (Door = Shadow Legions, Gate = Vault summoning); armor is anti-invader (power-system.md sections 15-16). powers.md, armor.md, invaders.md carry pointer notes. Shadow-door tricks in ch 1-25 are read as the army's exits; no chapter text changed.

## Audit through chapter 10 (2026-11-25, same-session audit, not independent)
1. Dialogue share: ch 8, 9, 10 first drafts came out at 17-21% and needed several patch rounds. Suggest the writer plans at least 6 dialogue exchanges per chapter before drafting. No engine change made.
2. Repeated device: Gorrath holds a door in ch 8 and again in ch 9. Suggest a different use of the retainers before ch 20 (Mirelle or Vesk carry the next action beat).
3. Ledger: the debt "Seal seeks hooded door-shield; Beatrix" says planted ch 10 but ch 10 (Lysette POV) does not plant it. Plant it by ch 13 or move the date; owner/planner to decide.

## Audit through chapter 10 (2026-11-26 new draft, same session, not independent)
Scores ch 1-10: tension never above 4, surprise 3-4, voice/freshness steady at 4, one 5 for emotion in ch 10 (Lysette POV). No debt is past due. Chapters 8/9/10 sit 21-24% dialogue by prepass (warning only); no filler added. No auto-append to banned.md or variety_menu.json this round.

### A1. Too many object endings
- What: ch 6-10 each end on a paper or small object (wrong date, card, written line, envelope, handkerchief).
- Why: the profile asks for varied action/object/line endings; five in a row reads as a habit.
- Fix: in ch 11-15, end at least two chapters on a line of dialogue or an action, unless the outline line itself names an object hook.

### A2. Low tension in the quiet chapters
- What: tension scored 3 in ch 6, 7, 9 and 10.
- Why: these chapters follow the outline, but four quiet chapters in a row slow the run before the Ball clock starts.
- Fix: where the outline already gives a clock (ch 11 graded run, ch 12-15 Ball week), state the clock in the first scene; do not add danger the outline lacks.

### A3. Several chapters sit on the word-count floor
- What: ch 7, 9 and 10 are 1801-1807 words.
- Why: expansions late in drafting tend to be dialogue, which pushes the share up while the count stays near the floor.
- Fix: when a chapter is short, add one concrete action or object beat before adding another line of talk.
