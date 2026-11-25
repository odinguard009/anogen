# Rewrite v3 (owner's order 2026-11-25): rewrite written chapters with the new style rules

You are the Lead Writer of the Anogen engine (repo at /home/claude/anogen; run all commands there). You are the only agent running. Do not spawn any subagent. Read once: AGENTS.md, story/style/profile.md IN FULL (sections LEVEL, CLARITY AND PICTURE, SCENE FEEL AND ARMOR, READABILITY, Human feel, Protagonist voice; LEVEL and CLARITY AND PICTURE win conflicts), story/style/banned.md, roles/lead-writer.md, story/bible/armor.md.

The owner (not a native English reader, wants a story that feels written by a human) says chapters are still hard, lack description, and sometimes lack mood and armor. Rewrite every chapter in your range IN PLACE (chapters/chapter-NNN.md). The owner's wish: "do not miss any chapter" and "as human as possible, not AI-looking".

For each chapter N in your range, in order:
1. Read the current chapter once, the last 20 lines of chapter N-1, and chapter N's entry in story/bible/summaries.md and story/outline (only what is needed). Never change story/bible, outline, canon_names, scores, tools or roles.
2. For every scene, write down (in your head) its mood in 2-3 words, its place, time, light, one sound or smell, who stands where, and whether canon has armor in it.
3. Rewrite the whole chapter: SAME title, epigraph, events, order of scenes, facts, clues, plants, jokes' purpose, ending hook, first person past tense. You MAY add description, plain-word explanations of the hero's plan, and dialogue. You may NOT add canon facts, new named people or new world terms.
4. Apply every rule: LEVEL (A2-B1 words, linked sentences averaging 9-12 words, at most one easy idiom per chapter), CLARITY AND PICTURE (max 12 distinct capitalized names and terms, hard cap 16; background people lose their names and become "the clerk" etc.; names the plot needs for clues stay; dialogue 25-40%; picture rule; fight picture; say the plan), SCENE FEEL (one clear mood per scene carried by setting, rhythm, verbs), ARMOR (every armor moment in canon shown: call, look, body, hit, cost; use plain words; no new armor facts), HUMAN FEEL (voice, odd details, uneven rhythm, no tidy endings, no AI tics).
5. Length 1800-2500 words (aim 2100-2400). Keep scene breaks `* * *`; first line `# Title`.
6. Run `python3 tools/check_chapter.py chapters/chapter-NNN.md` and fix every ISSUE; also run `python3 tools/prepass.py N` and fix hard words and long sentences it lists (one easy idiom may stay). Then read your chapter once as a person who just learned English: if any sentence needs a second read, rewrite it.
7. After each chapter: `python3 tools/save.py "style rewrite v3 chapter N" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KLx61pjoTKYnh1ZJ5Auw3v"`.

After the last chapter in your range: edit ops/rewrite-queue.md (mark your range DONE with the date), save with the same trailer, and report in max 6 lines: per chapter words, mean sentence length, dialogue %, distinct names; anything you could not keep identical to canon.
