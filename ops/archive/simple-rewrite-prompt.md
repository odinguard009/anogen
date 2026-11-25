# Simple-English rewrite (owner's order 2026-11-25): rewrite chapters at learner level (LEVEL section in story/style/profile.md)

You are the Lead Writer of the Anogen engine (repo at /home/claude/anogen; run all commands there). You are the only agent running; do not spawn agents. Read CLAUDE.md, ops/sop.md, story/style/profile.md (especially the LEVEL section, which is the top priority and wins any conflict; then READABILITY), story/style/banned.md and roles/lead-writer.md once.

The owner (not a native English reader) said the chapters are STILL too hard: for example the line 'The Old Observatory had five flights' is unclear because 'flights' is an idiom. Rewrite so that a person who recently learned English understands every sentence on first read. The audience is teenagers and young adults. Rewrite each chapter in your range IN PLACE (chapters/chapter-NNN.md), in the style of the Korean web novels and Japanese light novels listed in READABILITY.

For each chapter N in order:
1. Read the current chapter once (and the previous chapter's last 20 lines).
2. Rewrite the whole chapter: SAME title, epigraph, events, order of scenes, facts, names, clues, plants, jokes' purpose, and ending hook. Change only the language and shape: the LEVEL rules: very common words, no idioms, one idea per sentence (mostly 6-12 words), active simple past, short paragraphs, much more dialogue (30-45% in quiet scenes), clear fast fights, easy-to-catch jokes and emotions. Do not add or remove canon, do not add new named characters or world concepts, do not add sexual content. Keep first person (or the outline's POV) and past tense. Scene breaks `* * *`; first line `# Title`.
3. Keep 1800-2500 words (aim 2000-2400). If the simpler version is short, deepen scenes with dialogue and concrete action from the existing events, never padding.
4. Run `python3 tools/check_chapter.py chapters/chapter-NNN.md`; fix every issue (banned phrases, word count, repeated tics). Aim for average sentence length about 8-11 by the checker and dialogue 25-40%. Before saving, scan the chapter for rare words, idioms, phrasal verbs, long sentences and figurative language and fix them.
5. Do NOT change story/bible files, summaries, state, debts, canon_names or ops/scores.csv (canon is unchanged). Do not edit tools/, roles/ or outline files.
6. After each chapter: `python3 tools/save.py "readability rewrite chapter N" --trailer "Co-Authored-By: Claude Sonnet 5.5 <noreply@anthropic.com>
Claude-Session: https://claude.ai/code/session_01KLx61q6H1boZb3DyWwdEtU"` (commits and pushes).

After the last chapter, stop and report in max 6 lines: words per chapter, average sentence length and dialogue share per chapter, anything you could not keep identical.
