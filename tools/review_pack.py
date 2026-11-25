#!/usr/bin/env python3
"""Compact context for the per-chapter self-review (0 tokens to build). NOT the writer's context.

Usage: review_pack.py N [--text none|excerpts|full] [--level LOW|MEDIUM|HIGH]
The writer already has the chapter in its working context, so the default does NOT inject the whole chapter again:
  risk LOW    -> text none      (Python facts + the last lines, outline, relevant canon, 4 checklist lines)
  risk MEDIUM -> text excerpts  (+ the first and last 120 words)
  risk HIGH   -> text full      (the whole chapter is reloaded: a cold read of a reveal, death or arc end must not rely on memory,
                                  and context compaction may have dropped the text)
--text overrides the choice (use `full` after a context compaction or in a new chat); --level overrides the risk level
(for measuring). Canon is limited to what concerns the names that appear in THIS chapter. The style profile, premise and
characters of the writer's pack are never included; the mechanical style checks live in check_chapter.py and prepass.py.
"""
import re
import subprocess
import sys

from common import STORY, TOOLS, canon_names, chapter_path, read
import context_pack
import memory_retrieve
import risk

TEXT_FOR = {"LOW": "none", "MEDIUM": "excerpts", "HIGH": "full"}
COMMON = {"One", "Two", "Three", "Four", "Five", "Six", "Seven", "Eight", "Nine", "Ten", "Monday", "Tuesday", "Sunday", "Lance", "Chapter"}
LOW_ITEMS = {1, 5, 7, 9}   # checklist lines kept for LOW risk (outline, repetition, continuity, length/format)


def rows_mentioning(path, n, limit=4):
    pat = re.compile(r"(?<![\d-])%d(?![\d-])" % n)   # the number alone; a range like 1-25 is not a mention
    rows = [ln.strip() for ln in read(path).splitlines() if re.match(r"^\s*(?:[-*]|\d+\.)\s", ln) and pat.search(ln)]
    return [r[:240] for r in rows][:limit]


def facts(raw):
    body = raw.split("\n", 1)[-1]
    phrases = sorted(n for n in canon_names() if len(n) >= 3 and re.search(r"\b" + re.escape(n) + r"\b", body))
    known = {w.lower() for n in canon_names() for w in re.split(r"[\s,]+", n)}
    caps = {}
    for m in re.finditer(r"(?<=[a-z,;] )([A-Z][a-z]{2,})\b", body):
        caps[m.group(1)] = caps.get(m.group(1), 0) + 1
    unknown = sorted(w for w, c in caps.items() if w.lower() not in known and c >= 2 and w not in COMMON)
    labels = re.findall(r"\*\*\[[^\]]+\]\*\*", body)
    return phrases, unknown, labels, body.count("* * *")


def last_words(raw, k):
    w = raw.split()
    return " ".join(w[-k:])


def first_words(raw, k):
    body = raw.split("\n", 1)[-1].split()
    return " ".join(body[:k])


def check_summary(p):
    try:
        r = subprocess.run([sys.executable, str(TOOLS / "check_chapter.py"), str(p)], capture_output=True, text=True)
    except OSError as e:
        return f"check_chapter unavailable: {e}"
    for ln in r.stdout.splitlines():
        if ln.startswith("SUMMARY:"):
            return ln
    return "check_chapter printed no SUMMARY"


def checklist(level):
    txt = read(TOOLS.parent / "engine" / "self-review-checklist.md").strip()
    if level != "LOW":
        return txt
    keep = []
    for ln in txt.splitlines():
        m = re.match(r"^(\d+)\.\s", ln)
        if m and int(m.group(1)) not in LOW_ITEMS:
            continue
        keep.append(ln)
    return "\n".join(keep)


def build(n, text_mode=None, level=None):
    p = chapter_path(n)
    if not p.exists():
        return f"ERROR: chapter {n} does not exist"
    raw = read(p).strip()
    rl, reasons = risk.assess(n)
    level = level or rl
    mode = text_mode or TEXT_FOR[level]
    present, unknown, labels, scenes = facts(raw)
    parts = [f"## Self-review pack for chapter {n} (compact)\nRisk: {level}" + (" (" + "; ".join(reasons[:2]) + ")" if reasons else "")
             + f"\nChapter text in this pack: {mode}" + ("" if mode == "full" else " (the chapter is already in your session; after a context compaction or in a new chat rerun with --text full)")]
    parts.append("## Outline line\n" + "\n".join(context_pack.outline_lines(n, 1)))
    parts.append("## Facts from the text (Python)\n" + check_summary(p)
                 + f"\nscene breaks: {scenes}; labelled attacks: {', '.join(labels) or 'none'}"
                 + f"\ncanon names present: {', '.join(present) or 'none'}"
                 + (f"\nnames NOT in canon_names.txt (2+ uses): {', '.join(unknown)}" if unknown else ""))
    if mode == "excerpts":
        parts.append(f"## Opening (first 120 words)\n{first_words(raw, 120)}\n\n## Ending (last 120 words)\n{last_words(raw, 120)}")
    elif mode == "full":
        parts.append("## Chapter text\n" + raw)
    else:
        parts.append("## Ending (last 40 words)\n" + last_words(raw, 40))
    names = {w.lower() for w in present}
    parts.append("## Relevant canon (retrieved, with file:line)\n" + memory_retrieve.retrieve(n, budget=1200))
    lad = rows_mentioning(STORY / "bible" / "reveal-ladder.md", n)
    if lad:
        parts.append("## Reveal-ladder rows for this chapter\n" + "\n".join(lad))
    fu = rows_mentioning(STORY / "bible" / "first-use.md", n)
    if fu:
        parts.append("## First-use ledger rows for this chapter\n" + "\n".join(fu))

    def concerns(line):
        low = line.lower()
        return any(re.search(r"\b" + re.escape(x) + r"\b", low) for x in names)
    debts = [l.strip() for l in read(STORY / "bible" / "debts.md").splitlines() if "[open]" in l and (concerns(l) or re.search(r"due:[^|]*\b%d\b" % n, l))]
    if debts:
        parts.append("## Open debts that concern this chapter\n" + "\n".join(debts)[:1000])
    secrets = [l.strip() for l in read(STORY / "bible" / "secrets.md").splitlines() if l.strip().startswith("-") and concerns(l)]
    if secrets:
        parts.append("## Secrets that concern this chapter\n" + "\n".join(secrets)[:800])
    parts.append("## Checklist\n" + checklist(level))
    return "\n\n".join(parts)


def main():
    a = sys.argv[1:]
    if not a or not a[0].isdigit():
        sys.exit(__doc__)
    tm = a[a.index("--text") + 1] if "--text" in a else None
    lv = a[a.index("--level") + 1].upper() if "--level" in a else None
    if tm not in (None, "none", "excerpts", "full") or lv not in (None, "LOW", "MEDIUM", "HIGH"):
        sys.exit(__doc__)
    out = build(int(a[0]), tm, lv)
    print(out)
    print(f"[review pack: {len(out)} chars (about {len(out) // 4} tokens, ESTIMATE chars/4)]")


if __name__ == "__main__":
    main()
