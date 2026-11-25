# Anogen Optimization Roadmap (proposal, awaiting owner review)

Nothing here is implemented. Every item needs the owner's go-ahead for Phase Two. Items marked **OWNER ORDER** touch a LOCKED SETTING (`AGENTS.md`, `ops/models.json`) and must not be changed without the owner saying so in plain words. Savings are ESTIMATES (chars/4) until instrumentation (P0-4) provides provider-reported usage. Finding IDs refer to `docs/AUDIT_REPORT.md`.

Order logic: first stop silent quality loss and unsafe state, then make cost measurable, then optimise what the measurements show.

## Decisions needed from the owner before Phase Two

1. **Target length** (F-06): 300-500k words (136-227 chapters) or the series plan of ~850 chapters (~1.9M words)? Decides how much memory redesign (P1-3/P1-4) is worth building.
2. **Critic pass over chapters 1-20** (F-02): the current v3 text was never reviewed. This costs strong-tier tokens (≈ 4 critic batches, ESTIMATE ~19k tokens floor each plus output), so it is the owner's spend decision. Alternative: accept the risk and only add the guard.
3. **Authorise a GitHub Action** for tests (F-18) and any change to push behaviour (F-04).
4. **Any change to batch size, tiers, one-agent rule, schedule**: not proposed. The mission's 10/20/30-chapter runs are served by the existing sequential 5-chapter batches.

---

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
| P1-1 | **Usage instrumentation**: orchestrator appends `ops/usage.jsonl` per agent run (role, tier, range, provider-reported tokens if the host exposes them, wall time, outcome); `tools/usage_report.py` for cost per chapter / 1,000 words / arc, token share by role, retry count | F-08 | enables every claim; no direct saving | low | none | fixture run; first real batch with owner approval |
| P1-2 | Single parameterised rewrite prompt + style-change protocol (canary chapter, deterministic check, owner read, then bulk); retire two obsolete prompts; remove hard-coded paths and session URLs | F-07, F-15 | avoids a repeat of ~66 rewrites for 25 drafts; only measurable at the next style change | low | low | next style change: count of rewrite passes |
| P1-3 | Per-chapter pack as a delta: full bundle for the first chapter of a batch; later chapters get changes since the previous chapter and hashes for unchanged files | F-20 | ~10-13k tokens per 5-chapter batch (35-45% of repo-injected floor) | medium | medium (drift if the agent forgets unchanged state) | A/B on fixed chapters; critic-found canon errors per batch must not rise |
| P1-4 | Deterministic context selection from the outline line: names in the line pull matching `threads.md`, `timeline.md`, `twists-*.md`, `armor.md`, character entries; arc rolling summary replaces the unread archive; chapter provenance tags (`[ch 12]`) added to existing memory lines | F-05, F-22 | bounded context at 136-850 chapters; quality, not tokens, is the point | medium-high | medium | golden fixtures: expected facts retrieved for chapters 26-30; feature flag; blind comparison of two drafts of the same outline line (human read) |
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
