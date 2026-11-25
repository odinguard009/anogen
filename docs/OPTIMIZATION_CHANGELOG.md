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

---

# Second pass (post-merge)

Test status after this pass: `python3 tools/test_tools.py` = 110 PASS, 0 FAIL (was 77); `python3 tools/ctx_compare.py` exits 0. Retrieval labels items planned for a later chapter as "background only, never plant or pay it early" and the writer prompt repeats it. `ops/rewrite-queue.md` now states that future rewrites require a critic re-review (cost impact).

Authorised by the owner ("full auto": push and merge). Locked settings untouched (tiers, critic frequency of once per 10, batch of 5, concurrency, schedule OFF). No live generation was run; no chapter was rewritten.

| ID | Change | Files | Evidence |
|---|---|---|---|
| A1 | `mark critic --rereview` removed. New `engine_state.py rereview C [C ...]` updates hashes only for the listed chapters; refuses missing files and chapters never reviewed; `mark` can no longer bless edited chapters | `engine_state.py`, `AGENTS.md` | test: review 1-10, edit 3 and 7, `rereview 3`, 3 cleared and 7 pending |
| A2 | Edited reviewed chapters are an explicit task: `rereview_pending`, and `writer_range` is `null` until they are re-reviewed; no forced 10-chapter pass; state is derived from hashes so it survives interruption | `engine_state.py`, `AGENTS.md` | tests incl. interruption/resume |
| A3 | `verify_batch.py` checks every subprocess: crashed checker, missing git, git errors, untracked chapter, and unexpected exceptions each fail with a stated cause; checker runs with `--strict` | `verify_batch.py` | 5 tests (no repo, untracked, git missing from PATH, checker stub exits 2, undecodable file) |
| A4 | `usage_log.py report` prints PROVIDER-REPORTED, MANUALLY OBSERVED and ESTIMATED separately and never adds them; cost line labelled per source; cache read/write columns; cache cost only if the owner put cache prices in `ops/prices.json`; no built-in prices | `usage_log.py` | 3 tests |
| B | Incremental delta pack: `context_pack.py --part delta --incremental [--batch-start]`. State, Debts and Secrets are sent as exact line diffs or an "unchanged" stub against the previous pack of the same batch. Falls back to the full text when: no cache, wrong chapter, `--batch-start`, static sources changed, cache older than 3 h, diff larger than 60%. Default (no flag) is unchanged. Cache `ops/ctx-cache.json` is local; `--peek` never writes it. Writer prompt updated | `context_pack.py`, `ops/batch-writer-prompt.md`, `.gitignore` | 9 tests; property test caught and fixed a real bug (a changed last line was glued to the next diff line) |
| C | `tools/memory_retrieve.py` and `context_pack.py --retrieve`: threads, twists, timeline lines and older/archived summaries matched by canon names found in the outline lines (rare names only; names in more than 20% of memory lines are ignored) and by planned feed/plant chapters (n-1..n+2). Each item shows `file:line`; items over the 3,000-char budget are listed by source, never dropped silently. No embeddings, no dependencies | `memory_retrieve.py`, `context_pack.py` | fixture: finds 2/2 expected sources for chapter 26 and 3/3 for chapter 28 |
| B/C | Frozen fixture `tests/fixtures/golden5` and `tools/ctx_compare.py` (A/B of current vs incremental vs incremental + retrieval, lossless rebuild, retrieval check) | `tests/fixtures/`, `ctx_compare.py` | below |
| D | README updated (usage logging, unverified schedule push, re-review rule); roadmap status and contradictions fixed; `docs/ARCHITECTURE.md` created; `.github/workflows/tests.yml` runs the tool tests and the fixture comparison on PRs (read-only token, no secrets) | docs, README, workflow | |
| fix | `save.py` now stages `tests/` too | `save.py` | |

## Context comparison on the golden fixture (MEASURED characters; tokens are ESTIMATES = chars/4)

Fixture: chapters 23-27. Memory for chapters 23-26 is REAL (taken from the repo's own chapter 23-25 commits); chapter 27 is SYNTHETIC (one state line, one debt flipped). Per chapter, `--part delta`, first chapter with tail, later ones with `--no-tail`, as the writer prompt does.

     ch  A current  B incremental  C B+retrieval   saved B  sections (state/debts/secrets)
     23      16653          16732          20118       -79  full/full/full
     24      15198           8949          18560      6249  diff/unchanged/unchanged
     25      15018           9434          18352      5584  diff/unchanged/unchanged
     26      14760           8964          18121      5796  diff/unchanged/unchanged
     27      14672           8101          18236      6571  diff/diff/unchanged
    total chars A=76301 B=52180 (MEASURED); saved over chapters 24-27: 24200 chars = about 6050 tokens (ESTIMATE, chars/4; no provider measurement)
    retrieval ch 26: found 2/2
    retrieval ch 28: found 3/3
    lossless rebuild of State/Debts/Secrets: OK
    

Reading the numbers:
- The incremental pack is smaller from the second chapter of a batch on (about 5.6-6.6k chars each in this fixture). Over the four later chapters of a batch that is 24,200 chars, about 6,050 tokens (ESTIMATE). The first chapter pays only a small mode note (+79 chars).
- State, Debts and Secrets were rebuilt exactly from the incremental packs (previous text + diff or stub) in every chapter: no information is lost relative to the current pack.
- Retrieval adds about 3.4-3.6k chars per chapter (column C minus B). That is a deliberate quality cost: it is more context, not less. Net of the two, a later chapter is still about 2.5k chars smaller than the current pack in this fixture, but treat retrieval as spending for better recall, not as a saving.
- Only three real transitions exist in the visible history, and in them Debts and Secrets never changed; a batch where the writer edits all three files heavily will save less (the 60% rule then sends full text).
- Not measured: provider token counts, writer quality with diffs versus full text, and whether the writer correctly applies diffs. Quality trade-off: the writer must hold its first pack in mind; the prompt tells it to re-run the full pack when unsure. Recommended before relying on it: one approved real batch compared against `ops/usage.jsonl`, and a critic check for state errors.

## Single-agent optimization, Stage 1 (2026-11-25)
- Backup sebelum mulai: branch `backup/pre-single-agent-opt-20261125` (commit 7815569).
- Audit Fase 0: `docs/SINGLE_AGENT_OPTIMIZATION_AUDIT.md`.
- `engine/models.json`: `mode` dari `delegate` menjadi `inline-stage` pada tiga peran; teks `concurrency.rule` dan `orchestrator.where` tidak lagi menyebut spawning. Nilai model, tier, dan `max_agents_per_job` tidak diubah.
- `AGENTS.md`, `docs/ARCHITECTURE.md`, `engine/PORTABILITY.md`, prompt writer dan critic: kata "spawn an agent" diganti "run the ... stage yourself".
- Baru: `tools/policy_check.py` (+8 tes di `test_tools.py`, +langkah CI). Diuji terhadap commit 7815569: mendeteksi 6 masalah (Verified); pada state sekarang 0.
- Belum diukur: penghematan token (tidak ada data provider).
- Stage 2: `context_pack.py` baru: fingerprint footer, `--log`, `--budget` (drop utuh bagian prioritas rendah), dedup baris identik, `--style auto|full`. Diukur: tidak ada pengurangan pada pack sekarang (lihat COST_BENCHMARK.md).
- Stage 3: `tools/validate.py` (ERROR/WARNING/INFO, `--json`, `--write`); `AGENTS.md` memakainya setelah `verify_batch.py`.
- Stage 4: `tools/risk.py`, `tools/review_pack.py`, `engine/self-review-checklist.md`; prompt writer mendapat langkah 3b (self-review sesi yang sama). Frekuensi critic (per 10 bab) tidak diubah.
- Stage 5: `tools/memory_index.py` (SQLite+FTS5 turunan markdown, provenance, dedup, pemulihan indeks rusak, arc digest); `save.py` memperbarui indeks best-effort. Dokumen: `docs/STORY_MEMORY_ENGINE.md`.
- Stage 6-7: `usage_log.py` diperluas (provider, novel, operation, context, fingerprint, revisi, actual_cost, per 100 bab, proyeksi berlabel, ringkasan context-log); `tools/bench_context.py`; `docs/COST_BENCHMARK.md`.
- Persetujuan owner (2026-11-25): perubahan `mode` di `engine/models.json` dan pemecahan style profile (tanpa menghapus aturan).
- Tes: semua lulus lokal; CI diverifikasi di PR.

