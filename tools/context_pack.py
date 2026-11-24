#!/usr/bin/env python3
"""Assemble the whole context for ONE chapter in a single call (0 tokens to build).

Usage: context_pack.py [--chapter N] [--extra characters,world] [--peek]
Prints a compact pack; each section is capped and the total is capped by
the setting context_pack_max_chars.
"""
import argparse
import re

from common import STORY, CHAPTERS, body_text, chapter_files, chapter_path, read, setting_int
import engine_state
import precheck

OUTLINE_RE = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?Ch\.?\s*(\d+)\b")
PACING_RE = re.compile(r"^\s*(?:[-*]\s*)?Ch\.?\s*(\d+)\s*:")


def cap(text, n):
    text = text.strip()
    return text if len(text) <= n else text[:n].rstrip() + "\n[...truncated]"


def outline_lines(n, count=3):
    files = []
    od = STORY / "outline"
    if od.is_dir():
        files = sorted(od.glob("arc-*.md")) + sorted(od.glob("volume*.md"))
    found = {}
    for f in files:
        for line in read(f).splitlines():
            m = OUTLINE_RE.match(line)
            if m:
                k = int(m.group(1))
                if n <= k < n + count and k not in found:
                    found[k] = line.strip()
    return [found[k] for k in sorted(found)]


def pacing_lines(n):
    out = []
    for line in read(STORY / "outline" / "pacing.md").splitlines():
        m = PACING_RE.match(line)
        if m and n - 6 <= int(m.group(1)) <= n + 3:
            out.append(line.strip())
    return out


def last_summaries(n, k=3):
    txt = read(STORY / "bible" / "summaries.md")
    items = re.split(r"(?m)^(?=#{1,3}\s*Ch\.?\s*\d+|\-\s*Ch\.?\s*\d+)", txt)
    keep = []
    for it in items:
        m = re.match(r"\W*Ch\.?\s*(\d+)", it)
        if m and int(m.group(1)) < n:
            keep.append((int(m.group(1)), it.strip()))
    keep.sort()
    return "\n".join(t for _, t in keep[-k:])


def prev_tail(n, nwords=300):
    p = chapter_path(n - 1)
    if not p.exists():
        return ""
    w = body_text(read(p)).split()
    return " ".join(w[-nwords:])


def build(chapter=None, extra=(), peek=False):
    n = chapter or engine_state.compute_next()["next_chapter"]
    nxt = engine_state.compute_next()
    sections = []

    def add(title, body, limit):
        if body and body.strip():
            sections.append(f"## {title}\n{cap(body, limit)}")

    add("Engine state", f"next_chapter: {nxt['next_chapter']}\nbatch: {nxt['batch']}\ncontinue: {nxt['continue']} ({nxt['reason']})", 800)
    sections.append(precheck.build(n, peek=peek))
    add("Idea inbox", "\n".join(f"- {i}" for i in __import__('inbox').unprocessed_ideas()), 3000)
    add("Style profile", read(STORY / "style" / "profile.md"), 4500)
    add("Banned phrases", read(STORY / "style" / "banned.md"), 1500)
    add("Series arc", read(STORY / "outline" / "series.md"), 3000)
    ol = outline_lines(n)
    add("Outline for this and next chapters", "\n".join(ol) if ol else "NO OUTLINE for this chapter: Development Editor must plan the arc first.", 2500)
    add("Pacing (recent and upcoming)", "\n".join(pacing_lines(n)), 800)
    add("State", read(STORY / "bible" / "state.md"), 3500)
    debts = [ln for ln in read(STORY / "bible" / "debts.md").splitlines() if "[open]" in ln]
    add("Debts (open promises)", "\n".join(debts), 3000)
    sec = read(STORY / "bible" / "secrets.md").strip()
    add("Secrets", sec if len(sec) <= 2500 else "[older entries omitted]\n" + sec[-2500:], 2600)
    add("Characters", read(STORY / "bible" / "characters.md"), 3000)
    add("Last summaries", last_summaries(n), 3500)
    tail = prev_tail(n)
    add("End of previous chapter (continue from here, do not repeat it)", tail, 2200)
    add("Premise", read(STORY / "bible" / "premise.md"), 2500)
    for e in extra:
        add(f"Extra: {e}", read(STORY / "bible" / f"{e}.md"), 4000)

    out = "\n\n".join(sections)
    limit = setting_int("context_pack_max_chars")
    if len(out) > limit:
        out = out[:limit].rstrip() + "\n[...pack truncated at context_pack_max_chars]"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", type=int, default=None)
    ap.add_argument("--extra", default="")
    ap.add_argument("--peek", action="store_true")
    a = ap.parse_args()
    extra = [e.strip() for e in a.extra.split(",") if e.strip()]
    print(build(a.chapter, extra, a.peek))


if __name__ == "__main__":
    main()
