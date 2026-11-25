# Golden 5-chapter fixture (context packs for chapters 23-27)

Frozen snapshot used by `tools/ctx_compare.py` and `tools/test_tools.py`. Do not edit by hand.

- `root/`: static story files, outline, threads/twists/timeline, archived summaries, canon names, chapters 22-25 (earlier chapters are stubs so numbering is continuous). Copied from main at 2026-11-25.
- `memory/pack23` ... `pack26`: REAL `state.md`, `debts.md`, `secrets.md` as they stood before each chapter's pack (taken from the chapter 23, 24 and 25 commits of this repo). In these real transitions debts and secrets did not change; only state changed.
- `memory/pack27`: SYNTHETIC. State got one extra marked line, one debt flipped from `[open]` to `[paid ch 26]`, secrets unchanged. It exists only to exercise the diff path for debts; it is not story text.
- `expected_retrieval.json`: sources that `memory_retrieve.py` must return for chapters 26 and 28 (hand-checked against the outline lines).
