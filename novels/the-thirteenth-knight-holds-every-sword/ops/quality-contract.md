# Quality Contract (PERMANENT — locked)

## Rule 1: No chapter may be published without passing all gates.
Every chapter must pass check_chapter.py --strict (exit 0), word count 2000-3000, sentence length mean >= 8.5, opener variety (no word >22%), no banned phrases exceeded, no repeated 5-grams, no shared 6-grams with previous 5 chapters, "not X but Y" <= 2, rule-of-three lists <= 1, no em-dashes, capitalized names <= 16 (target 12), dialogue share 25-40%, armor labels in battle chapters, weapon labels in battle chapters, first-use descriptions, no sexual/ecchi/harem content.

## Rule 2: No rule may be waived without owner approval in writing.

## Rule 3: No EPUB may be built with failing chapters.

## Rule 4: No chapter published without critic pass. Every 10 chapters: critic pass. Every arc: audit.

## Rule 5: No milestone moved without owner approval. Mother truth: ch ~400. Confession: ch ~500. Identity secret. Graduation ball: Arc 4.

## Rule 6: Process. One chapter at a time. check_chapter.py --strict after each. If FAIL: fix before next. Max 3 per batch, then critic. Every commit must pass CI. No force push.

## Enforcement
- tools/check_chapter.py: strict by default
- tools/build_epub.py: strict gate before build
- .github/workflows/quality-check.yml: CI blocks merge
- tools/milestone_check.py: verifies story milestones
- ops/engine.json: tracks checker/critic/audit per chapter
