# Blocked items (retry first on the next "lanjutkan")

## HOLD resolved 2026-11-26
The old HOLD from the full replan was cleared by the owner's explicit order to write chapters 1-5 and build an EPUB. Procedure followed: `engine_state.py hold clear`, `reset-draft --confirm`, `batch-start --mode n --target 5`. The HOLD section is removed so a later "lanjutkan" is not read as a hold. If the owner wants writing to stop again, set a new HOLD.

## Push status 2026-11-26
Push was expected to be unavailable, but `save.py` pushed successfully during the critic commit. `main` and `origin/main` were in sync after "critic pass chapters 1-5". Later bookkeeping commits may be local only.

## EPUB delivery 2026-11-26
Arc EPUB is still gated on arc completion. The owner explicitly asked for chapters 1-5, so a partial EPUB was built with `build_epub.py --range 1-5`: `out/chapters-1-5.epub`, also copied to the workspace root as `the-thirteenth-knight-chapters-1-5.epub`. Zip verified: 12 entries, five chapter XHTML files, no bad members.
