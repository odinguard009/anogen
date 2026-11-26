# Blocked items (retry first on the next "lanjutkan")

## HOLD (owner order 2026-11-26): DO NOT WRITE OR REWRITE ANY CHAPTER
Chapters 1-10 are superseded drafts (ignore them). The plot, arcs and style are being replanned. Even on "lanjutkan": write nothing, run no writer or critic, add nothing to rewrite-queue.md. WHEN THE OWNER ORDERS THE REWRITE (procedure): 1) `python3 tools/engine_state.py hold clear`. 2) Delete chapters/chapter-001..010.md (copies are already in archive/superseded-2026-11-26/chapters/) and set critic_through 0, audit_through 0, reviewed {} in ops/engine.json (keep the file valid JSON). 3) Start `batch-start --mode arc --arc 1 --max 50` or the count the owner names, writing from chapter 1 with outline/arc-1.md, bible/calendar.md and profile.md. 4) Resume only when the owner explicitly orders the full rewrite (then rewrite from chapter 1 on the new plan). Do not run tools/rename.py on chapters/ meanwhile (use the skip option).

