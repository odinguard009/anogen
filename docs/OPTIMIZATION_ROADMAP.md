# Anogen Optimization Roadmap

Savings are ESTIMATES (chars/4) until `ops/usage.jsonl` holds provider-reported usage. Finding IDs refer to `docs/AUDIT_REPORT.md`; what was actually changed is in `docs/OPTIMIZATION_CHANGELOG.md` (this file is the plan, the changelog is the record).

## Status (updated in the second pass)

| State | Items |
|---|---|
| Done (first pass) | P0-1 to P0-6, P1-1, P1-2 (obsolete prompts archived), P2-3 (`next --no-apply`), P2-4, P3-1 |
| Done (second pass) | A1/A2 explicit per-chapter `rereview` and a blocking re-review task, A3 hardened `verify_batch.py`, A4 per-source usage report, P1-3 incremental delta pack (opt-in, with fallbacks), P1-4 smallest deterministic retrieval (opt-in `--retrieve`), P3-3 CI workflow, `docs/ARCHITECTURE.md`, golden fixture and `ctx_compare.py` |
| Open | P1-5 per-entry memory caps and overflow (the flat 3,000-char files remain), P2-1 (trim the critic prompt using the verify result), P2-2 deterministic continuity pre-check, P3-2 single source of numeric style targets, P3-4 quality baseline protocol, character state still one flat file, arc rolling summaries are still produced by hand-curated archive plus retrieval only |
| Owner order required (not proposed) | batch size, model tiers, one-agent rule, schedule, critic frequency (already set to once per 10 by the owner), conditional critic tier (P2-5) |

## Owner decisions received (resolved)

1. Target length: the 850-chapter plan in `story/outline/series.md` stays (about 1.9M words), so memory work (P1-4/P1-5) matters more than for 300-500k words.
2. Critic for chapters 1-20: not re-run; their current text is recorded as owner-accepted (`engine_state.py baseline-reviewed`). The owner can order a critic run at any time with `engine_state.py rereview ...` after it.
3. Critic frequency: once per 10 chapters (replaces once per 5).
4. Push and merge are authorised (permanent project access, `engine/sop.md` section 0). GitHub Actions workflow added in the second pass.

## P0: reliability and data safety (small, low risk, do first)

| ID | Item | Findings | Complexity | Risk | Validation |
|---|---|---|---|---|---|
| P0-1 | Fail loudly on any pack truncation; build the style section by priority so Human feel / Protagonist voice always reach the writer | F-01 | low | low | unit test: every `##` section present or non-zero exit; diff of before/after static pack (+~1.1k tokens ESTIMATE) |
| P0-2 | Never plan or write over existing chapters: clamp `writer_range` at the next existing chapter, report the gap, refuse overwrite without an explicit rewrite flag | F-03 | low | low | test with a gap (chapter 20 absent, 21-25 present) |
| P0-3 | Reviewed-text tracking: store a hash per chapter at critic time; changed chapters reappear in `critic_pending`; `mark` rejects skips and decreases; audit trigger derived from state not range shape | F-02, F-11 | low-medium | low | tests: edit after review; interrupted batch ending at 28; size-3 batches |
| P0-4 | Atomic writes (temp file + `os.replace`) for JSON/Markdown state; rolling `engine.json.bak`; atomic lock via exclusive create; owner check on release | F-09, F-10 | low | low | kill-during-write test; concurrent acquire test |
| P0-5 | `save.py`: fetch and merge (never force) on rejected push, backoff, stage explicit paths | F-04, F-19 | medium | medium | two clones + bare remote test; dry-run mode |
| P0-6 | `verify_batch.py A-B`: per chapter file exists, word range, summary present, canon names registered, scores row, committed; `check_chapter.py --strict` exit code | F-13 | low | low | fixtures with each failure; run on the real 25 chapters (expect all pass) |

## P1: high-impact efficiency (needs P0-1 and instrumentation first)

| ID | Item | Findings | Est. benefit (ESTIMATE) | Complexity | Risk | Validation |
|---|---|---|---|---|---|---|
| P1-1 (done) | **Usage instrumentation**: orchestrator appends `ops/usage.jsonl` per agent run (role, tier, range, provider-reported tokens if the host exposes them, wall time, outcome); `tools/usage_report.py` for cost per chapter / 1,000 words / arc, token share by role, retry count | F-08 | enables every claim; no direct saving | low | none | fixture run; first real batch with owner approval |
| P1-2 | Single parameterised rewrite prompt + style-change protocol (canary chapter, deterministic check, owner read, then bulk); retire two obsolete prompts; remove hard-coded paths and session URLs | F-07, F-15 | avoids a repeat of ~66 rewrites for 25 drafts; only measurable at the next style change | low | low | next style change: count of rewrite passes |
| P1-3 (done, opt-in) | Per-chapter pack as a delta: full bundle for the first chapter of a batch; later chapters get changes since the previous chapter and hashes for unchanged files | F-20 | ~10-13k tokens per 5-chapter batch (35-45% of repo-injected floor) | medium | medium (drift if the agent forgets unchanged state) | A/B on fixed chapters; critic-found canon errors per batch must not rise |
| P1-4 (smallest version done, opt-in) | Deterministic context selection from the outline line: names in the line pull matching `threads.md`, `timeline.md`, `twists-*.md`, `armor.md`, character entries; arc rolling summary replaces the unread archive; chapter provenance tags (`[ch 12]`) added to existing memory lines | F-05, F-22 | bounded context at 136-850 chapters; quality, not tokens, is the point | medium-high | medium | golden fixtures: expected facts retrieved for chapters 26-30; feature flag; blind comparison of two drafts of the same outline line (human read) |
| P1-5 | Replace flat 3,000-char caps with per-entry line caps and an overflow file the retriever can reach | F-05 | removes forced silent loss | medium | medium | fixtures at 2x cap |

## P2: workflow optimisation

| ID | Item | Findings | Notes |
|---|---|---|---|
| P2-1 | Orchestrator runs `verify_batch.py` before the critic and passes only the residual mechanical list; critic still reads every chapter and judges canon, human feel, continuity (agent count and tier unchanged) | F-21 | ESTIMATE: shorter critic prompt/reading of mechanical output; tier unchanged so no OWNER ORDER |
| P2-2 | Deterministic continuity pre-check: numbers/days/places recorded in state vs chapter text; produces a short list for the critic | F-05, F-11 | catches classes seen in the run-log (day count, headcount) earlier and cheaper |
| P2-3 | Make `engine_state next` pure (`--apply` writes); context pack never logs the variety draw | F-12 | removes hidden writes |
| P2-4 | Idempotent `log_run.py` (replace by chapter) | F-23 | |
| P2-5 | **OWNER ORDER, only if the owner asks**: conditional critic tier (for example strong-tier only when prepass or verify flags), merge or skip steps | F-21 | not proposed; locked settings |
| P2-6 | Parallelism: **none recommended**. Script work is under 0.3 s per call at 500 chapters; dependent chapters must stay sequential | | |

## P3: maintainability and polish

| ID | Item | Findings |
|---|---|---|
| P3-1 | Remove verified dead code and unused imports; merge the two Markdown converters and the duplicated break regex | F-17 |
| P3-2 | Single source for numeric style targets (read by checker and prompts); remove contradictions | F-14 |
| P3-3 | Tests for each new behaviour; GitHub Action running `tools/test_tools.py` (owner authorisation) | F-18 |
| P3-4 | Quality baseline protocol: deterministic metrics plus a fixed blind-read sample reviewed by the owner; scores.csv kept as a coarse signal only | F-16 |
| P3-5 | `docs/ARCHITECTURE.md` and `docs/OPTIMIZATION_CHANGELOG.md` maintained during Phase Two | |

---

## Safety rules for Phase Two (restated)

- One change at a time, each with tests; run `python3 tools/test_tools.py` before and after (baseline: 51 PASS, 0 FAIL).
- No live generation without the owner's approval; use fixtures and dry runs. Live testing, when needed, is a single approved batch compared against the usage log.
- Never overwrite chapters; any migration is documented and reversible through git.
- No push without the owner's explicit authorisation. No claim of savings without a measured before/after from `usage.jsonl`.
