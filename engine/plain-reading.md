# Plain Reading Contract (locked setting 19; owner order 2026-11-26; applies to every novel)
Owner's complaint (ch 6 and 7): he could not understand the scenes; many sentences and lines had no clear meaning for a reader who has only just learned English. Cause: indirect dialogue (riddles, dodges, jokes that need a guess), surnames with no link to a first name, numbers that do not add up, lines that do not answer the line before, and scenes with no stated purpose. This contract is the permanent fix. It sits ON TOP of the style profile: where the dialogue model (subtext, circling an object) and plain reading disagree, plain reading wins (owner order 2026-11-26).

## Rules
1. EVERY LINE MAKES SENSE FROM ITS OWN WORDS. A reader who knows only the page must be able to say what each line means. A reply must answer the line before it, or the narration shows plainly that it dodges ("Eden did not answer. He looked at the door.").
2. JOKES AND DODGES GET A PLAIN BEAT. After a joke, a dodge or a hidden meaning, one short beat within a line shows what was meant: a visible action, or another person saying it plainly. Others may show feeling in plain words they can be seen to have ("Lysette was angry; her pencil snapped"). Eden stays flat. Maximum 3 jokes or running gags per chapter. No culture-bound jokes. No riddle replies ("That is not an answer." / "It is the only one I have.") more than once per chapter.
3. ONE NAME PER PERSON. Narration and dialogue use the first name. A surname or nickname appears only after narration has linked it once in the same chapter ("Rowan Tallis"). Teachers may use surnames only if the narration says so once.
4. NUMBERS ADD UP AND SAY WHAT THEY COUNT. "Rowan was second on the Ladder (the school's list of the best students)". Counts of people, boxes, bells and days must agree in the whole chapter.
5. EVERY SCENE OPENS WITH ITS PURPOSE IN PLAIN WORDS: where, who, and what someone wants. Every scene ends with one plain change (a fact learned, a plan made).
6. EXPLAIN PAPERWORK AND PROCEDURE ONCE, plainly (what the form is for), then use it lightly. Maximum 6 sentences of procedure talk per scene.
7. NO CLUE IS LEFT AS A RIDDLE. When a clue matters (a date, a name, a mark), one plain sentence says why it matters, in Eden's flat observation ("Sorn was dead. A dead man could not sign.").
8. MAKE THE OBSERVATION PLAIN, NEVER A SCHEDULED SECRET. Before adding any explanation, find it in the bible (reveal-ladder.md, secrets.md); if it is not there or it would run ahead of the reveal ladder, do not add it.
9. ONE THING, ONE NAME across the whole book. Never rename a canon term (Committee, Hushborn, Southern Wall) to fit the name budget; cut surnames and background names instead.
10. KEEP THE CRAFT: speaker habits, objects, humour from plain words all stay. Only the guessing is removed.

## Self-test (writer and critic, per chapter)
1. For each scene write: who and where; what happens; what changed.
2. For each exchange, paraphrase every line from its words alone. A line that cannot be paraphrased fails: rewrite it.
3. Check every number and name against rule 3 and 4.
Critic `plain_reading` score: below 8/10 = FAIL, rewrite the scene.

## Guard (tools/check_chapter.py `plain_check`)
Finds only: riddle replies (more than 1), surnames used before narration links them, runs of 8+ bare short dialogue lines. It cannot tell whether a scene makes sense; the self-test is the real check. WARNING for chapters 1-50, ERROR from chapter 51.
