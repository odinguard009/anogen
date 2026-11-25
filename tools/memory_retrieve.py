#!/usr/bin/env python3
"""Deterministic story-memory retrieval (0 tokens, standard library only, no embeddings).

Usage: memory_retrieve.py [--chapter N] [--budget 4000]
Question answered: "which older facts does the writer of chapter N need that the fixed pack does not already carry?"
Signals (all from files already in the repo):
  * names in the outline lines for chapters N..N+2 (only words that are in story/bible/canon_names.txt),
  * chapter numbers: a thread feed/plant or twist plant planned for chapters N-1..N+3 is always relevant,
  * older summaries (archive and live, before the last 3) that share 2+ of those names.
Sources: threads.md, twists-*.md, timeline.md, summaries (archive + live). Every item shows file:line (or the chapter
number for a summary), so the writer can open the source. The manuscript stays the source of truth; nothing is rewritten.
Entries that do not fit the budget are listed by file:line (never dropped silently).
"""
import argparse
import re

from common import ROOT, STORY, canon_names, next_chapter_number, read
import context_pack

LINE_MAX = 330
SUMMARY_MAX = 520


_NAMES = None


def names():
    """Canon names as phrases (so 'Black Order' is one term, not 'black' and 'order')."""
    global _NAMES
    if _NAMES is None:
        _NAMES = [(n, re.compile(r"(?<![\w])" + re.escape(n) + r"(?![\w])")) for n in sorted(canon_names(), key=len, reverse=True) if len(n) >= 3]
    return _NAMES


def line_terms(text, canon=None):
    return {n.lower() for n, rx in names() if rx.search(text)}


def terms_for(n, count=3):
    return line_terms("\n".join(context_pack.outline_lines(n, count)))


def chapters_in_fields(fields):
    nums = set()
    for f in fields:
        nums |= {int(x) for x in re.findall(r"(?<![\d.])(\d{1,3})(?![\d.]*\s*(?:chars|%|words))", f)}
    return nums


def short(text, limit):
    text = " ".join(text.split())
    return text if len(text) <= limit else text[:limit].rstrip() + " [cut: see source]"


def table_items(path, rel, n, terms, canon, field_slice):
    items = []
    window = range(n - 1, n + 3)
    for i, line in enumerate(read(path).splitlines(), 1):
        if not re.match(r"^\s*\d+\.\s", line):
            continue
        parts = [p.strip() for p in line.split(" | ")]
        nums = chapters_in_fields(parts[field_slice])
        in_window = sorted(x for x in nums if x in window)
        overlap = line_terms(line) & terms
        if in_window or len(overlap) >= 2:
            score = (6 if n in in_window else 3 if in_window else 0) + len(overlap)
            def tag(x):
                return ("planned for THIS chapter" if x == n else
                        f"planned for LATER ch {x}: background only, never plant or pay it early" if x > n else
                        f"was planned for ch {x}")
            why = ("; ".join(tag(x) for x in in_window) if in_window else "") + \
                  (("; " if in_window else "") + "names: " + ", ".join(sorted(overlap)) if overlap else "")
            items.append((score, f"{rel}:{i}", why, short(line, LINE_MAX)))
    return items


def timeline_items(n, terms, canon):
    items = []
    p = STORY / "bible" / "timeline.md"
    for i, line in enumerate(read(p).splitlines(), 1):
        if line.lstrip().startswith("-"):
            overlap = line_terms(line) & terms
            if len(overlap) >= 2:
                items.append((len(overlap), f"story/bible/timeline.md:{i}", "names: " + ", ".join(sorted(overlap)), short(line, LINE_MAX)))
    return items


def summary_items(n, terms, canon):
    texts = []
    arch = STORY / "bible" / "archive"
    if arch.is_dir():
        for f in sorted(arch.glob("summaries-*.md")):
            texts.append((f"story/bible/archive/{f.name}", read(f)))
    texts.append(("story/bible/summaries.md", read(STORY / "bible" / "summaries.md")))
    items = []
    for rel, txt in texts:
        for blk in re.split(r"(?m)^(?=##\s*Ch\.?\s*\d+)", txt):
            m = re.match(r"##\s*Ch\.?\s*(\d+)", blk)
            if not m or int(m.group(1)) >= n - 3:
                continue  # the last 3 summaries are already in the pack
            overlap = line_terms(blk) & terms
            if len(overlap) >= 2:
                items.append((len(overlap), f"{rel} (Ch {m.group(1)})", "names: " + ", ".join(sorted(overlap)), short(blk.strip(), SUMMARY_MAX)))
    return sorted(items, key=lambda x: -x[0])[:3]


def memory_lines():
    """Every line/block the retriever can return; used to measure how common each name is."""
    out = []
    for name in ["threads.md", "timeline.md"] + [f.name for f in sorted((STORY / "bible").glob("twists-*.md"))]:
        out += [ln for ln in read(STORY / "bible" / name).splitlines() if ln.strip()]
    arch = STORY / "bible" / "archive"
    for f in (sorted(arch.glob("summaries-*.md")) if arch.is_dir() else []):
        out += [b for b in re.split(r"(?m)^(?=##\s*Ch\.?\s*\d+)", read(f)) if b.strip()]
    out += [b for b in re.split(r"(?m)^(?=##\s*Ch\.?\s*\d+)", read(STORY / "bible" / "summaries.md")) if b.strip()]
    return out


def rare_terms(terms, canon):
    """Drop names that occur in more than 20% of memory lines (the hero, 'order', 'seal'...): they match everything."""
    lines = memory_lines()
    limit = max(3, int(0.2 * len(lines)))
    per_line = [line_terms(ln) for ln in lines]
    df = {t: sum(1 for s in per_line if t in s) for t in terms}
    return {t for t, c in df.items() if 0 < c <= limit}


def retrieve(n, budget=3000):
    canon = None
    all_terms = terms_for(n)
    terms = rare_terms(all_terms, canon)
    items = []
    items += table_items(STORY / "bible" / "threads.md", "story/bible/threads.md", n, terms, canon, slice(1, 4))
    for f in sorted((STORY / "bible").glob("twists-*.md")):
        items += table_items(f, f"story/bible/{f.name}", n, terms, canon, slice(1, None))
    items += timeline_items(n, terms, canon)
    items += summary_items(n, terms, canon)
    items.sort(key=lambda x: (-x[0], x[1]))
    head = (f"Outline names used for matching (rare ones only): {', '.join(sorted(terms)) or '(none)'}"
            + (f"; ignored as too common: {', '.join(sorted(all_terms - terms))}" if all_terms - terms else ""))
    out, used, skipped = [head], len(head), []
    for score, src, why, text in items:
        row = f"- [{src}] ({why}) {text}"
        if used + len(row) + 1 > budget:
            skipped.append(src)
            continue
        out.append(row)
        used += len(row) + 1
    if skipped:
        out.append(f"[not shown, over the {budget}-char budget: {', '.join(skipped)}]")
    if not items:
        out.append("(no older thread, twist, timeline or summary entry matched)")
    return "\n".join(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", type=int, default=None)
    ap.add_argument("--budget", type=int, default=3000)
    a = ap.parse_args()
    print(retrieve(a.chapter or next_chapter_number(), a.budget))


if __name__ == "__main__":
    main()
