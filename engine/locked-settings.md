# Locked settings
Single source: AGENTS.md section LOCKED SETTINGS and engine/models.json (updated 2026-11-25 by the owner's order: audit merged into the critic run at chapters 10/20/30..., forward-only style changes, two batches per chat session, vendor-neutral tiers). They change only when the owner explicitly orders it.
- 13. NO SUB-AGENTS (owner order 2026-11-25, permanent): see AGENTS.md locked setting 13.
- 14. ADVISOR CONSULT (owner order 2026-11-26, permanent): see AGENTS.md. One consult at a time, advice only; no sub-agents.
- 15. HOLD (owner order 2026-11-26): engine_state.py hold set/clear; nothing is written while it is set.
- 12 (extended 2026-11-26): POV AND VOICE (close third person, Eden flat), DIALOGUE MODEL, NAME LABELS **[Name]**, dates in story/bible/calendar.md.
16. CHAPTER LENGTH (owner order 2026-11-26): minimum 2000 words per chapter (brief.md chapter_words_min; hard range 2000-2500, aim 2150-2350). Never reached by padding.
17. GUARDS (owner order 2026-11-26): `python3 tools/start.py` first in every session; validate.py ERRORs (debts, outline labels, word range, style) block committing chapters; START HERE in AGENTS.md, tools/start.py and tools/debts.py are not to be weakened without the owner's order.
