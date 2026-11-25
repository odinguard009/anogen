# Post-PR7 cost correction (branch `claude/blissful-faraday-rqigdc`, base main d5813e8)

Status: NOT merged. Waiting for owner approval. Labels: **Measured** = counted by a script on a fixture; **Estimated** = chars/4, no provider data; **Not available** = no provider-reported token usage exists in this repo, so no real token or money saving is claimed anywhere.

Locked production settings (model, provider, tier values, batch size 5, critic per 10, concurrency, schedule OFF, chapter targets) are unchanged. No chapter, canon or bible file was touched. No sub-agent was used.

## 1. Files changed
- Instructions: `AGENTS.md`, `engine/PORTABILITY.md`, `engine/sop.md`, `engine/batch-critic-prompt.md`, `engine/batch-writer-prompt.md`, `engine/self-review-checklist.md`, `engine/models.json` (only the `_note` text and `copy_critic.when` text; no value changed), `docs/SINGLE_AGENT_ARCHITECTURE.md`.
- Tools: `tools/review_pack.py`, `tools/context_pack.py`, `tools/precheck.py`, `tools/memory_index.py`, `tools/policy_check.py`, `tools/bench_context.py`, `tools/test_tools.py`; new `tools/bench_memory.py`, `tests/fixtures/retrieval_bench.json`.

## 2. Instruction conflicts fixed (task 2)
- Critic prompt said "never copy existing works"; now matches the owner order (observe, imitate, modify allowed). Writer and critic agree.
- Critic is described everywhere as a sequential stage of the SAME session, NOT an independent reviewer (critic prompt, models.json notes, PORTABILITY, AGENTS.md, SOP). PORTABILITY no longer mentions separate fresh sessions or a cheaper separate model; mechanical work is done by `tools/`.
- Tier labels are described as informational (no per-role model selection). Values in `models.json` are unchanged.
- Cold-read procedure added to the critic prompt and the self-review checklist: judge the manuscript itself, consult outline and canon, do not assume the writer's reasoning, do not defend the draft, report concrete problems only.

## 3. Self-review pack (task 1), chapter 25, same files (Measured, characters)
| version | chars |
|---|---:|
| PR #7 (always full chapter) | 22,875 |
| now, risk LOW (no chapter text) | 7,205 (-68.5%) |
| now, risk MEDIUM (excerpts) | 8,636 (-62.2%) |
| now, risk HIGH (full chapter) | 18,748 (-18.0%) |
Python does the deterministic checks (check_chapter, names vs canon, bold labels, scene breaks, relevant canon via memory_retrieve, due debts/secrets only for names in the chapter). LOW keeps checklist items 1, 5, 7, 9 only. Tokens would be about chars/4 (Estimated). Limit: at LOW/MEDIUM the reviewer does not see the full prose, so prose-quality problems (style, human feel) are only caught on HIGH or by the per-10 critic. Critic frequency is unchanged.

## 4. Context engine (task 3)
Measured on real chapters 26/31/36/41/46 vs 7815569 (pre-optimization): static 32,195 -> 32,309 (+0.4%, footer line), delta -3.5% to -4.2%, total 255,385 -> 252,286 (**-1.2%**). On these real arc-1 outlines every chapter contains fight/power words, so the conditional style blocks save nothing.
Synthetic quiet fixture (plain outlines; a test fixture, NOT a real novel): static 32,195 -> 24,224 (-24.8%), total 240,367 -> 196,892 (**-18.1%**). Treat as the upper bound for non-combat chapters, not as a forecast.
Changes: writer prompt now uses `--extra "combat-style?"` (loaded only when the outline mentions fight/armor/power words) and `--static-seen <fingerprint>` guidance; precheck shows only name pools relevant to the chapter (rest on demand: `precheck.py --names all`, with a notice line). Name-pool hiding is the one place a writer could miss a name option: mitigated by the notice, not eliminated.
Measured repetition: identical lines across pack sections 0 chars; 6-gram overlap among static sections 9. Wording-level repeats are tiny, so no style rule was removed or shortened (locked setting 12).

## 5. Retrieval benchmark (task 4)
`tools/bench_memory.py` on the frozen golden5 fixture, 23 labeled queries (labels written by the orchestrator from fixture text, **not owner-verified**; one small fixture, so results show a ranking defect, not general quality). Before any change:
| ranking | hit@1 | hit@3 | MRR |
|---|---:|---:|---:|
| as shipped (importance, then chapter order; text only filters) | 0.087 | 0.174 | 0.215 |
| FTS5 bm25 | 1.000 | 1.000 | 1.000 |
Defect: a text query returned matches sorted by chapter, not relevance. Fix: with `--text`, `ORDER BY bm25(mem_fts)` then importance, then chapter. Without text the order is unchanged. After: production = 1.000 / 1.000 / 1.000. Other checks: 202 rows indexed, 0 duplicates, 0 bad provenance (every `file:line` exists), incremental update re-indexes only changed files (existing tests). Arc digest = first sentence per chapter: useful as an index, loses later events of each chapter; unchanged. No embeddings or vector DB. Scores of 1.000 on 23 paraphrase queries are optimistic; queries share vocabulary with the summaries.

## 6. Policy check (task 5)
`tools/policy_check.py` is now clause-level: a forbidden term counts as allowed only if every occurrence sits under a prohibition in its own clause, and exception/obligation words (except, unless, kecuali, required, must, forget, fail to...) disqualify it. `test_tools.py` adds adversarial tests: 19 lines that must be flagged (e.g. "Do not forget to spawn an agent.", "Never use sub-agents, except for the critic.", "No delegation is required; delegate the writer.", Indonesian and mixed variants), 10 that must pass, 5 `models.json` cases, and a contradictory line injected into AGENTS.md. Limit: regex heuristics, not language understanding; unusual phrasing can still slip through. The repo itself passes (`POLICY: OK`); three repo sentences that the stricter checker flagged were reworded.

## 7. Test results (Measured, local, real exit status)
- `python3 tools/test_tools.py`: ALL TESTS PASSED, exit 0, 0 FAIL lines (includes the new memory benchmark test).
- `python3 tools/ctx_compare.py`: exit 0 (retrieval ch 26 2/2, ch 28 3/3, lossless rebuild OK).
- `python3 tools/policy_check.py`: exit 0, "POLICY: OK (single agent, no delegation)".
- `python3 tools/bench_memory.py`: exit 0 (table above).
- CI: see section 8.

## 8. CI
(filled after the PR run)

## 9. Remaining risks
- No provider-reported usage exists, so real token or cost saving is unknown; all token figures are chars/4.
- Savings in section 4 depend on outlines; real fight-heavy chapters save about 1%.
- Review pack LOW/MEDIUM trades prose visibility for size; the per-10 critic and HIGH level remain the prose check. The critic is the same session as the writer.
- Retrieval labels are AI-written on one fixture.
- Policy checker is heuristic.
- `characters.md` / `state.md` "rank N" leftovers were not touched (canon).
