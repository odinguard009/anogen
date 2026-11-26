#!/usr/bin/env python3
"""One parser for story/bible/debts.md (used by validate.py and context_pack.py).

Canonical line:  - [open] what was planted | planted: ch A, B | due: ch N, M-K
Status words: [open], [paid ch N], [dropped] (a dropped debt needs a reason after the text).
Due numbers: every integer after 'due:' ('ch' is optional). A range 'A-B' counts as A and B.

Usage: debts.py [list|overdue]   (reads the active novel; 0 tokens)
"""
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from common import STORY, read, CHAPTERS  # noqa: E402

LINE = re.compile(r"^\s*-\s*\[(\w+)([^\]]*)\]\s*(.*)$")


def due_numbers(text):
    m = re.search(r"due:\s*([^|]*)", text)
    return [int(x) for x in re.findall(r"\d+", m.group(1))] if m else []


def parse(path=None):
    """Return a list of dicts: line (1-based), status, text, due (list of ints)."""
    p = path or (STORY / "bible" / "debts.md")
    out = []
    for i, ln in enumerate(read(p).split("\n"), 1):
        m = LINE.match(ln)
        if m:
            out.append({"line": i, "status": m.group(1), "text": m.group(3), "due": due_numbers(ln), "raw": ln})
    return out


def check(next_chapter):
    """Return (errors, warnings) as lists of (line, message) for open debts."""
    errs, warns = [], []
    for d in parse():
        if d["status"] != "open":
            continue
        if not d["due"]:
            errs.append((d["line"], "open debt has no 'due:' chapter number"))
        elif max(d["due"]) < next_chapter:
            errs.append((d["line"], f"open debt is overdue: last due chapter {max(d['due'])}, next chapter is {next_chapter}; mark it [paid ch N], [dropped] with a reason, or give it a new due"))
        elif min(d["due"]) < next_chapter:
            warns.append((d["line"], f"open debt passed its first due chapter {min(d['due'])} (later due {max(d['due'])} remains)"))
    return errs, warns


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "overdue"
    nums = sorted(int(m.group(1)) for f in CHAPTERS.glob("chapter-*.md") if (m := re.match(r"chapter-(\d+)\.md", f.name)))
    nxt = (nums[-1] + 1) if nums else 1
    if cmd == "list":
        for d in parse():
            print(d["line"], d["status"], d["due"], d["text"][:100])
        return 0
    errs, warns = check(nxt)
    for ln, msg in errs:
        print(f"ERROR debts.md:{ln}: {msg}")
    for ln, msg in warns:
        print(f"WARNING debts.md:{ln}: {msg}")
    print(f"debts: {len(errs)} error(s), {len(warns)} warning(s), next chapter {nxt}")
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main())
