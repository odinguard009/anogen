#!/usr/bin/env python3
"""Context for the per-chapter self-review (0 tokens to build). NOT the writer's context.

Usage: review_pack.py N [--next-reveals]
Holds: the chapter text, its outline line, the risk level and depth, the chapter-relevant canon (outline names matched in
threads, twists, timeline, older summaries via memory_retrieve; reveal-ladder and first-use rows that mention this chapter),
State/Debts/Secrets of the previous chapter, and the checklist. It leaves out the style profile, premise, characters and
extras the writer needed (the mechanical style checks are in check_chapter.py and prepass.py).
"""
import re
import sys

from common import REPO, STORY, chapter_path, read
import context_pack
import memory_retrieve
import risk


def rows_mentioning(path, n, limit=6):
    pat = re.compile(r"\b(?:ch\.?\s*)?%d\b" % n)
    out = [ln.strip()[:240] for ln in read(path).splitlines() if pat.search(ln) and len(ln.strip()) > 10]
    return out[:limit]


def build(n):
    p = chapter_path(n)
    if not p.exists():
        return f"ERROR: chapter {n} does not exist"
    level, reasons = risk.assess(n)
    parts = [f"## Self-review pack for chapter {n}\nRisk: {level}" + (" (" + "; ".join(reasons) + ")" if reasons else "")]
    parts.append("## Outline line\n" + "\n".join(context_pack.outline_lines(n, 1)))
    parts.append("## Chapter text\n" + read(p).strip())
    parts.append("## Relevant canon (retrieved, with file:line)\n" + memory_retrieve.retrieve(n, budget=2500))
    lad = rows_mentioning(STORY / "bible" / "reveal-ladder.md", n)
    if lad:
        parts.append("## Reveal-ladder rows for this chapter\n" + "\n".join(lad))
    fu = rows_mentioning(STORY / "bible" / "first-use.md", n)
    if fu:
        parts.append("## First-use ledger rows for this chapter\n" + "\n".join(fu))
    for title, f, keep in (("Debts (open)", "debts.md", lambda l: "[open]" in l), ("Secrets", "secrets.md", lambda l: bool(l.strip()))):
        lines = [l for l in read(STORY / "bible" / f).splitlines() if keep(l)]
        parts.append(f"## {title}\n" + "\n".join(lines)[-2500:])
    chk = read(REPO / "engine" / "self-review-checklist.md")
    parts.append("## Checklist\n" + chk.strip())
    return "\n\n".join(parts)


def main():
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        sys.exit(__doc__)
    out = build(int(sys.argv[1]))
    print(out)
    print(f"[review pack: {len(out)} chars (about {len(out) // 4} tokens, ESTIMATE chars/4)]")


if __name__ == "__main__":
    main()
