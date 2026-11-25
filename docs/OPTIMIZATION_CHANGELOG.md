# Optimization Changelog (Phase Two)

Authorised by the owner on 2026-11-25 (push and Phase Two; permanent project access, `ops/sop.md` section 0). Owner decisions applied: series length stays the 850-chapter plan; no re-run of the critic for chapters 1-20 (their current text is recorded as owner-accepted with `engine_state.py baseline-reviewed`); critic once per 10 chapters. Locked settings NOT changed: writer batches of 5, model tiers, one agent at a time, schedule OFF.

Test status: `python3 tools/test_tools.py` = 77 PASS, 0 FAIL after the changes (was 51 PASS; 26 new checks). The new tests were not all verified to fail on the old code: only the truncation test was seen failing against the old `context_pack.py`/`engine_state.py`/`save.py` (the old files crashed on the new CLI flags, so that run was not a clean mutation test). No live generation was run; nothing here is a token or cost measurement.

| ID | Change | Problem fixed | Files | Evidence |
|---|---|---|---|---|
| P0-1 | Style profile cap raised to 20,000; any truncation appends `PACK WARNING` naming the section and exits 4 (`cap()` records every cut, including the whole-pack cap) | F-01 | `context_pack.py` | Static pack 23,617 → 28,418 chars (+4,801, ESTIMATE ≈ +1.2k tokens per batch); contains "Human feel" and "Protagonist voice"; tests "pack keeps Human feel…" and "pack truncation exits 4…" |
| P0-2 | `writer_range` clamped before the next existing chapter, `gap_note` reported | F-03 | `engine_state.py` | test "gap: writer_range clamped…" |
| P0-3 | Per-chapter content hashes recorded at `mark critic`; `critic_changed_after_review`; `mark` validates (not beyond highest chapter, never backwards, audit never passes critic, no missing chapters); `arc-complete` refuses unreviewed edits; `baseline-reviewed` command; critic range = once per 10 chapters (`critic_span` setting, default 10), `critic_waiting`, `audit_with_critic`, audit catch-up | F-02, F-11 and owner order | `engine_state.py`, `common.py` | 6 tests incl. interrupted batch ending at 28 (critic range 29-30, audit rides along) |
| P0-4 | Atomic writes (temp + `os.replace`), `engine.json.bak` rolling backup, `flock` guard around lock read-modify-write, `lock.py release --owner` refuses non-holders | F-09, F-10 | `common.py`, `lock.py`, `.gitignore` | tests "atomic write…", "lock release by non-owner refused" |
| P0-5 | `save.py` stages only project paths (no `git add -A`; stray files reported, not added), on rejected push fetches and merges (never force/rebase), 4 attempts with backoff, aborts merge on conflict | F-04 (partial), F-19 | `save.py` | two-clone + bare-remote test: "save merges a rejected push", "save does not stage stray files" |
| P0-1b | `context_pack_max_chars` raised 40,000 → 48,000 in `story/brief.md` (the restored profile pushed `--part full --extra combat-style` to 40,660 chars and made it exit 4); static and delta calls stay far below the cap | regression found in review | `story/brief.md` | full pack exits 0 |
| P0-6 | `tools/verify_batch.py A-B` (file, title, words, summary incl. archive, outline line, scores row, checker issues, committed); `check_chapter.py --strict` | F-13 | new `verify_batch.py`, `check_chapter.py` | real chapters 21-25: `VERIFY: OK` |
| P1-1 | `tools/usage_log.py add/report` writing `ops/usage.jsonl`; no prices shipped, cost reported as unknown without `ops/prices.json`; `--source reported|manual|estimate` | F-08 | new `usage_log.py`, `AGENTS.md` | tests; first real data needs the owner's next run |
| P1-2 | Obsolete `readability-rewrite-prompt.md` and `simple-rewrite-prompt.md` moved to `ops/archive/` (git history kept); `rewrite-prompt.md` no longer hard-codes a path or session URL | F-07 (partial), F-15 | `ops/` | grep clean |
| P2-3 | `engine_state.py next --no-apply` is a pure read | F-12 (partial) | `engine_state.py` | tests use it |
| P2-4 | `log_run.py` keeps one `scores.csv` row per chapter (replace, sorted) | F-23 | `log_run.py` | test |
| P3-1 | Dead assignment, `ends`, unused imports, unused `last_chapters` removed | F-17 | `engine_state.py`, `check_chapter.py`, `precheck.py`, `build_epub.py`, `context_pack.py`, `common.py` | tests |

Prompt/doc changes under the owner's critic-per-10 order (`save.py` also retries an earlier failed push when there is nothing new to commit): `AGENTS.md` (locked setting 3, flow steps 0, 2, 3), `ops/batch-critic-prompt.md`, `ops/models.json` (`copy_critic.when`), `ops/sop.md`, `ops/decisions.md`.

## Not done, and why

- P1-3 (delta pack), P1-4/P1-5 (relevance-based memory, provenance, arc summary): quality-sensitive redesign; needs `usage.jsonl` data and a fixed A/B fixture first. Deliberately deferred; with 850 chapters planned this is the most important next step.
- P2-2 (deterministic continuity pre-check), P2-5 (conditional critic tier: owner order), CI workflow (F-18, not created: touches repo automation), F-12 `variety_log` write-on-read (unchanged; use `--peek`), F-14 single source of numeric targets.
- F-04 remaining: no cross-container lock (`ops/lock.json` stays local); the single-writer rule still applies if the schedule is turned on.
