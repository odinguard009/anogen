#!/usr/bin/env python3
"""Pre-writing facts for the next chapter (0 tokens): number, variety draw, unused names,
openings/closings to avoid, inbox status.

Usage: precheck.py [--chapter N] [--peek]
"""
import argparse
import re

from common import (STORY, body_text, canon_tokens, chapter_files,
                    next_chapter_number, read, sentences, setting_int)
import inbox
import variety


def unused_names(limit=6):
    """names.md: lines under '## culture' headers, then names (one per line or comma separated)."""
    txt = read(STORY / "names.md")
    used = canon_tokens()
    out, culture = {}, None
    for line in txt.splitlines():
        s = line.strip()
        if s.startswith("#"):
            culture = s.lstrip("#").strip() if s.startswith("##") else None
            continue
        if culture is None or not s or s.startswith("<!--") or len(s) > 200:
            continue
        for n in re.split(r"[,;]", s.lstrip("-* ")):
            n = n.strip()
            if n and not (set(re.split(r"\s+", n.lower())) & used):
                out.setdefault(culture, []).append(n)
    return {c: v[:limit] for c, v in out.items()}


def recent_edges(k):
    edges = []
    for n, p in chapter_files()[-k:]:
        t = read(p)
        ss = sentences(body_text(t))
        if ss:
            edges.append((n, ss[0][:140], ss[-1][:140]))
    return edges


def build(chapter=None, peek=False):
    n = chapter or next_chapter_number()
    lines = [f"## Precheck: chapter {n}"]
    lines.append("Variety constraints for this chapter (obey them):")
    lines.append(variety.format_picks(variety.draw(n, log_it=not peek)))
    names = unused_names()
    if names:
        lines.append("Unused names (use these for new characters/places; never reuse canon names):")
        for c, v in names.items():
            lines.append(f"- {c}: {', '.join(v)}")
    else:
        lines.append("Unused names: none available (story/names.md empty or fully used); invent distinctive ones and register them in canon_names.txt.")
    edges = recent_edges(setting_int("repeat_window"))
    if edges:
        lines.append("Recent openings and closings (do NOT echo their wording or shape):")
        for num, first, last in edges:
            lines.append(f"- ch {num} opens: {first}")
            lines.append(f"  ch {num} ends: {last}")
    cf = chapter_files()
    if cf:
        hi = cf[-1][0]
        summ = read(STORY / "bible" / "summaries.md")
        if not re.search(r"(?mi)^\W*Ch\.?\s*%d\b" % hi, summ):
            lines.append(f"WARNING: chapter {hi} has no summary in summaries.md: a previous run was interrupted. Finish its bookkeeping (Canon Keeper) and run save.py BEFORE writing chapter {n}.")
    un = inbox.unprocessed_ideas()
    lines.append(f"Inbox: {len(un)} unprocessed idea(s)" + (" -> develop them first (Development Editor)." if un else "."))
    return "\n".join(lines)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", type=int, default=None)
    ap.add_argument("--peek", action="store_true")
    a = ap.parse_args()
    print(build(a.chapter, a.peek))


if __name__ == "__main__":
    main()
