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

## Reference standard (owner order 2026-11-26: "Bab 6 dan 7 sudah lumayan bisa dimengerti. Tetapkan penulisan seperti ini jadi aturan permanen")
The owner read chapters 6 and 7 of his first novel after the repair and said he could follow them. That level is the calibration sample for ANY novel and ANY AI. Do not open another novel to see it (each novel stays closed to the others); the excerpts below ARE the sample. Match this level before writing or judging any chapter.

EXCERPT 1 (opening a scene with where, who, what; defining a word at first use):
> On Friday morning the school put the Year 5 students into teams of five. Each team was called a Lance. ... The number was the student's place on the Ladder, the school's list of the best students in the year.

EXCERPT 2 (a joke that gets a plain beat):
> "We have the second, the third and the fourth. This is the best team in the school." / "On paper," Lysette said. / "What is wrong with paper?" / "Paper does not fall over in a maze."

EXCERPT 3 (a rule explained once, then used lightly):
> "This is a warrant. When a student misses too many classes, we send one to the headmistress. You have missed sixty-one. The office wants a reason, in one word." ... "There is no roof on the form. There is a box for class, a box for drill, a box for meals." / "Then use another box."

EXCERPT 4 (a clue given its reason in the hero's flat voice):
> A man who had died last spring could not sign an order this autumn. Someone had written Master Sorn's name on it, or someone had found a way to use his stamp.

EXCERPT 5 (a dodge named by narration):
> She said it too fast. Felix looked at her, but she was already asking Rowan about the soup. Seraphine had not told the truth. Eden did not know which part was false.

What made them readable:
- Each scene opens with where, who, what is wanted (ch 6: "On Friday morning the school put the Year 5 students into teams of five. Each team was called a Lance.").
- A new word is defined at its first use, in the same sentence or the next ("the Ladder, the school's list of the best students in the year"; "The red band meant the Discipline Committee").
- A paper or rule is explained in one plain sentence, then used (ch 7: the warrant is sent to the headmistress after too many missed classes; the form has no box for a roof, so Lysette writes it in the margin).
- A dodge or lie is named by narration ("Seraphine had not told the truth. Eden did not know which part was false.").
- A clue gets its reason in Eden's flat voice (ch 6: "A man who had died last spring could not sign an order this autumn.").
- Short, linked sentences; one speaker per beat; every reply answers the line before it.

Patterns to REMOVE when found (all were found and cut in arc 1): replies that answer a different question and are left unexplained; a repeated one-line gag across scenes; "That is not an answer." / "It is the only one." (rule 2 allows it at most once, with a plain beat); paperwork talk that never says what the form is for; an object or mark mentioned once and never explained; two names for one person; a number with no noun.
Do not fix this by padding. Add a real beat (an action, a reason, a decision) or cut. Keep 2000-2500 words.

## Stricter rules for low-level learners (owner complaint, 2026-11-27)
The owner (an Indonesian learner of English) said the repaired chapters were still hard. The rules above are the floor, not the ceiling. Apply these on top:

1. TARGET A1-A2 WHEN THE OWNER SAYS "level rendah". If the owner complains of difficulty, lower the chapter_words target (story/brief.md) to 1200-1500 and aim at CEFR A1-A2, not A2-B1. Change only on the owner's order.
2. NO RIDDLE REPLIES. Rule 2 already allows at most one per chapter; for chapters where the owner has asked for plain reading, use zero. Every reply answers the line before it in plain words; a dodge is named by narration in the same sentence ("She did not tell the truth. Eden did not know which part was false.").
3. DEFINE EVERY SURNAME ON THE SAME LINE IT FIRST APPEARS. "Rowan Tallis" before any bare "Tallis", even in dialogue and in letters. The guard now treats a missing link as an ERROR from chapter 51 and as a WARNING before that; do not ship a chapter with the warning.
4. MAXIMUM TWO CLAUSES PER SENTENCE. One main clause and one "and/but/because/when" clause. No "which/that/who" chains. Split anything longer.
5. NO CULTURE-BOUND IDIOMS OR SARCASM THAT NEEDS A GUESS. "Probably" is fine; "It is the only one I have" is not, unless the next sentence says what "it" is.
6. EVERY NEW WORD GETS A PLAIN GLOSS IN THE SAME OR NEXT SENTENCE. Prefer words a learner meets in the first 1000 of English. Avoid "requisition", "physician", "atrium" unless glossed.
7. SHORTER CHAPTERS FOR LOW LEVEL. 1500-1800 words is easier to hold than 2000-2500. Change chapter_words_min/max in story/brief.md only on the owner's order.
8. THE SELF-TEST IS MANDATORY. The writer must print `PLAIN ch N: PASS` with a score out of 10 before the chapter is saved; the critic must fail any chapter below 8/10 and rewrite the scene, not patch one line.
9. THE GUARD IS AN ERROR FROM CHAPTER 51. `tools/check_chapter.py` now returns ERROR (exit 1 with --strict) for any plain_check finding at ch 51 and above. Treat a WARNING in ch 1-50 as if it were an error.
