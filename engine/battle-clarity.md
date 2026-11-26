# Battle Clarity Contract (locked setting 18; owner order 2026-11-26; applies to every novel)
Owner's complaint: fights are confusing and do not feel cool. Cause: no map, mechanics explained late, long action sentences, too many actors, no visible peak. This contract is the permanent fix. The scripts are only a supporting guard (they count sentence length and crowding; they cannot tell if a fight is clear). The fight card is the real fix.

## 1. Fight card (before the action, 3-4 plain sentences, in narration or in the writer's notes and obvious on the page)
- PLACE and POSITIONS: where everyone stands (left/right/behind, step distances), light and shadow.
- OPPONENT: what it is and what it can do.
- STAKES: what is lost if the hero fails.
- CLOCK: how long, or what is about to happen.
The outline line of every battle chapter carries `card: place=...; foe=...; stakes=...; clock=...; beats=bait>ahead>turn>finish>witness; new=one mechanic`.

## 2. Beat order (mandatory)
bait (the hero lets the enemy see a weakness or a plan) -> enemy ahead (the enemy looks like it is winning) -> hero turns it (the setup the reader SAW pays off) -> clear finishing move (one picture) -> witness reaction (someone sees, flinches or says one line).
Show the setup, surprise with the result: never hide what the hero is doing; hide only what it will cost the enemy.

## 3. Limits
- At most 3 active characters per scene; others are named only to be placed (behind the wall).
- At most 1 new mechanic per scene, stated plainly at or before use as: what is seen, what happens, what follows (see story/bible/mechanics.md).
- Action sentences: one action each, about 12 words, never over 25.
- Never "something happened out of sight": the reader sees the cause of every result.
- Cool comes from a distinctive object or sound, a confident enemy, and witness reactions. The hero stays flat.

## 4. Self-test (writer and critic)
From the text alone, write the positions and the five beats in five lines. If a line cannot be written, the fight is not clear: rewrite it. Critic `battle_clarity` score: below 8/10 = FAIL, rewrite the scene.

## 5. Guard (tools/check_chapter.py `battle_check`)
For chapters marked `type: battle` in the outline: action sentence mean > 14 words, more than 2 action sentences of 25+ words, more than 6 mentions of "Door", missing `card:` in the outline. WARNING for chapters 1-50 (arc 1 is being repaired); ERROR from chapter 51.
