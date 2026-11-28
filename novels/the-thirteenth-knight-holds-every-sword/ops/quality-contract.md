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

## Rule 7: Plain-language contract (owner order 2026-11-28)
Audience: minimum age 15, mostly non-native English speakers. Every chapter must also satisfy:
- zero idioms unless the meaning is visible in the same sentence;
- `like a` max 1, `as if` = 0, no mood metaphors (*cold/shadow/thick air/frosted over* as feeling shortcuts);
- the word **group** for student teams; no bare *lance* as a team name;
- **door** = a real door, **a black opening** = Eden's power; **tap** = the power trigger, **knock** = a real door;
- **ash** = fire remains, **grey dust** = enemy remains, **dirt** = floor dust, **stone dust** = stone powder;
- every special word and power has one plain 'what you see' sentence at first use, then a plain phrase (consistency-arc1.md section 6c);
- no two names for one thing (Thirteenth Vigil, Husk/Hushborn, etc.).

Enforcement is staged: brief.md `plain_language_strict: false` makes these WARNINGS while chapters 1-50 are still old. After the rewrite, set `plain_language_strict: true`; then violations become ERRORS. The owner orders the switch.
