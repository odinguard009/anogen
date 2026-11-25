# Anogen Performance Baseline (Phase One, 2026-11-25)

Rule: **MEASURED** = observed in this repo/container. **ESTIMATE** = derived, not observed. **UNMEASURED** = no data exists; the figure is not invented. Provider token counts, costs, retries and failure rates are UNMEASURED because the repo never calls a provider and `ops/run-log.md` has 13/13 empty `quota_note` fields.

## 1. Corpus

| Metric | Value | Status |
|---|---|---|
| Chapters | 25 (arc 1 plan: 1-50) | MEASURED |
| Words | 55,096 (`status.py`); raw `wc -w` 55,560 | MEASURED |
| Words per chapter | mean 2,204 (task range 1,800-2,500); min 1,915; max 2,511 | MEASURED |
| Chapters per 100k words | ≈ 45 | derived |
| 300k / 500k words | ≈ 136 / ≈ 227 chapters | derived |
| Series plan | ~850 chapters ≈ 1.9M words | MEASURED from `series.md:1`, derived words |

## 2. LLM calls per chapter (by design, from prompts)

| Role | Agent runs | Per chapter |
|---|---|---|
| Writer + Canon Keeper | 1 per 5 chapters | 0.2 runs |
| Critic | 1 per 5 chapters | 0.2 runs |
| Managing Editor | inside critic run, 1 per 10 chapters | 0.1 additional duties, 0 extra runs |
| Development Editor | 1 per arc / inbox intake | ≈ 0.02 (1 per 50) |
| **Total spawned agents** | | **≈ 0.42 agent runs per chapter (ESTIMATE from design; actual retries UNMEASURED)** |

Direct API calls from code: 0 (MEASURED by search). Web searches: at most 1 per arc planning (`roles/development-editor.md` step 2).

## 3. Context injected by the repo (ESTIMATE = chars / 4; floor only)

| Item | Chars (MEASURED) | Tokens (ESTIMATE) |
|---|---|---|
| Static pack (`--part static --extra combat-style`) | 23,617 | ~5.9k per batch |
| Delta pack (`--part delta`) | 16,362 | ~4.1k per chapter |
| Full pack | 39,991 (cap 40,000) | ~10.0k |
| Writer prompt + 2 roles | 3,787 + 1,908 + 941 = 6,636 | ~1.7k |
| Critic prompt + role | 2,617 + 1,046 = 3,663 | ~0.9k |
| Writer batch floor (5 chapters) | | **~28k** (before output, reads and accumulation) |
| Critic batch floor (5 chapters) | | **~19k** (5 chapters × ~2.9k + prompts + profile) |
| Chapter text | 2,204 words | ~2.9k tokens (1.33 tokens/word ESTIMATE) |

Known defect inside these figures: the style profile in the static pack is cut at 9,000 of 13,816 chars (F-01).

## 4. Wall-clock (MEASURED from timestamps; commit/log times, not agent start times)

| Activity | Observed | Source |
|---|---|---|
| First-draft chapter | ≈ 2.0-2.4 min | run-log 02:08→02:30 WIB for ch 1-10; commits 11:05:18, 11:07:13, 11:09:29 for ch 23-25 |
| Critic pass | 2 min 43 s for 3 chapters (23-25) | commits 11:09:29 → 11:12:12 |
| Readability rewrite | ≈ 30 s per chapter (ch 11-22 in 5 min 55 s) | commits 07:24:03 → 07:29:58 |
| Style rewrite v3 | ≈ 71 s per chapter average (ch 1-22 in ~26 min, incl. retry) | commits 10:34:53 → 11:00:47 |
| 10 / 20 / 30 chapters | UNMEASURED as a single run; arithmetic from the first-draft rate: ~21-24 / ~42-48 / ~63-72 min writer time only (derived, excludes critic) | derived |
| Recovery after interruption | UNMEASURED | |
| Failure rate, retries | UNMEASURED (one visible retry: "style rewrite v3 retry chapter 1", `1070ba3`) | |

History is shallow (50 commits); early first-draft commits are not available.

## 5. Process volume (rewrite churn)

| Metric | Value | Status |
|---|---|---|
| Rewrite orders covering chapters 1-22 | 3 (readability, simple English, v3) | MEASURED from `ops/decisions.md` |
| Visible rewrite commits | 12 "readability rewrite" + 24 "style rewrite v3" | MEASURED (lower bound, shallow history) |
| Chapter rewrites vs first drafts | up to ~66 vs 25 (≈ 2.6x) | derived |
| Chapter files with ≥ 3 commits | 17 of 22 rewritten chapters (lower bound) | MEASURED |
| Critic pass covering the current text of chapters 1-20 | none | MEASURED (git + run-log) |

## 6. Script performance (MEASURED, median of 3)

| Tool | 25 chapters | 500 synthetic chapters |
|---|---|---|
| `check_chapter.py` | 52 ms | 65 ms |
| `prepass.py` (5 chapters) | 210 ms | 242 ms |
| `context_pack.py --part delta` | 43 ms | 73 ms |
| `status.py` | 46 ms | 286 ms |
| `engine_state.py show` | 37 ms | 44 ms |
| `test_tools.py` (51 checks) | 2.5 s total | n/a |

Synthetic chapters are the 25 real chapters repeated; this proves tool scaling only.

## 7. Quality baseline (what exists)

| Metric | Value | Status / caveat |
|---|---|---|
| `check_chapter.py` OK | 25/25 | MEASURED; gate is satisfied near its own lower limits |
| Mean sentence length | 9.0 words (range 8.5-10.2; limit 8.5-13.5) | MEASURED |
| Dialogue share | mean 29%, range 25-45% (limit ≥ 25%) | MEASURED |
| Critic scores (`scores.csv`) | 25 rows; 69 threes, 72 fours, no other value | MEASURED; not discriminating; rows 1-22 refer to pre-v3 text |
| Canon errors found by critic, chapters 23-25 | day count, attacker count 40→20, character facts (run-log lines 80-82) | MEASURED (qualitative, 3 chapters) |
| Repetition, character consistency, plot continuity rates | UNMEASURED | |

## 8. Cost

| Metric | Status |
|---|---|
| Cost per chapter, per 1,000 words, per 100k words, per arc | **UNMEASURED.** Needs provider usage per agent run (roadmap P1-1). Do not quote the token floors above as cost. |
| Token distribution by role | UNMEASURED; relative floors only (writer ~28k vs critic ~19k per 5 chapters, ESTIMATE) |
| Cache hit rate | UNMEASURED |

## 9. Gaps to close before Phase Two comparisons

1. Per-run usage log (P1-1).
2. A fixed 5-chapter fixture set (outline lines, memory files) for repeatable A/B of context changes; recorded agent responses for dry runs.
3. A blind human-read sample for quality, because the 3-or-4 scores cannot detect regressions.
4. Timing of an interrupted-and-resumed batch (one controlled test with owner approval).

## 10. Reproducing the measurements

```bash
python3 tools/test_tools.py                                   # 51 PASS expected
python3 tools/status.py
python3 tools/context_pack.py --part static --extra combat-style --peek | wc -c
python3 tools/context_pack.py --part delta --peek | wc -c     # --peek avoids writing variety_log.json
```

Timing and synthetic-scale runs used scratch copies (`ANOGEN_ROOT` pointing at a copy of the tree); the repository itself was not modified by any measurement.
