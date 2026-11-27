# Writing Rules (PERMANENT — locked, owner order 2026-11-27)

## Rule 1: One chapter at a time.
Write one chapter. Check it. Fix if needed. Only then move to next.

## Rule 2: Gate check after every chapter.
Run: python tools/check_chapter.py --strict chapters/chapter-XXX.md
If FAIL: fix before writing next chapter. No exceptions.

## Rule 3: Word count 2000-3000 (hard fail).
No chapter below 2000 or above 3000 words.

## Rule 4: Sentence length mean 9-12 (hard fail).
Join short sentences with and/but/because/when. No sentence under 6 words in a row.

## Rule 5: No repeated phrases.
No "he always...", "not X but Y" (>2), rule-of-three lists (>1), em-dashes, repeated 5-grams.

## Rule 6: Opener variety.
No word starts >22% of sentences. Vary with place, object, sound, time, number, others' actions.

## Rule 7: Dialogue share 25-40%.
At least 25% dialogue. Do not pad. Add real exchanges only if scene needs it.

## Rule 8: Armor and weapon labels in battle chapters.
Every battle chapter must mention armor labels and weapon labels.

## Rule 9: First-use descriptions.
First use of named weapon/armor/ability: 2-4 sentences (look, body use, effect, limit).

## Rule 10: No sexual/ecchi/harem content.
Romance pure and genuine.

## Rule 11: Max 3 chapters per batch, then critic pass.
After 3 chapters: critic pass. After 10 chapters: full audit.

## Rule 12: No chapter published without critic pass.
Every 10 chapters: critic pass. Every arc: audit.

## Rule 13: No milestone moved without owner approval.
Mother truth: ch ~400. Confession: ch ~500. Identity secret. Graduation ball: Arc 4.

## Rule 14: Process
- Write one chapter
- Run check_chapter.py --strict
- If FAIL: fix and re-check
- If PASS: commit and push
- Every 3 chapters: critic pass
- Every 10 chapters: full audit

## Rule 15: No bypass.
No --force. No skipping. No "close enough." No exceptions.

## Enforcement
- tools/check_chapter.py: strict by default
- tools/build_epub.py: strict gate before build
- tools/milestone_check.py: verifies milestones
- ops/quality-contract.md: permanent rules
- .github/workflows/quality-check.yml: CI blocks merge (fallback in tools/)
