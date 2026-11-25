#!/usr/bin/env python3
"""Keep live files small for a 600-chapter run (0 tokens).

Usage: archive.py [--keep-summaries 10] [--keep-runlog 60]
- story/bible/summaries.md: chapters older than the last K move to story/bible/archive/summaries-chNNN-chMMM.md
  (context_pack only reads the last 3 summaries; audits read the last 10).
- ops/run-log.md: lines older than the last K move to ops/archive/run-log-<n>.md.
Nothing is deleted. Run at each audit.
"""
import argparse
import re

from common import ROOT, STORY, OPS, read, write


def archive_summaries(keep):
    p = STORY / "bible" / "summaries.md"
    txt = read(p)
    parts = re.split(r"(?m)^(?=##\s*Ch\.?\s*\d+)", txt)
    head, items = parts[0], parts[1:]
    nums = [int(re.match(r"##\s*Ch\.?\s*(\d+)", it).group(1)) for it in items]
    if len(items) <= keep:
        print("summaries: nothing to archive")
        return
    old, new = items[:-keep], items[-keep:]
    lo, hi = nums[0], nums[len(old) - 1]
    dest = STORY / "bible" / "archive" / f"summaries-ch{lo:03d}-ch{hi:03d}.md"
    write(dest, "".join(old))
    pointer = f"(Chapters {lo}-{hi}: see story/bible/archive/{dest.name})\n\n"
    head = re.sub(r"\(Chapters \d+-\d+: see story/bible/archive/[^)]*\)\n\n", "", head)
    write(p, head.rstrip("\n") + "\n\n" + pointer + "".join(new))
    print(f"summaries: archived chapters {lo}-{hi} -> {dest.relative_to(ROOT)}")


def archive_runlog(keep):
    p = OPS / "run-log.md"
    lines = read(p).splitlines(True)
    if len(lines) <= keep + 5:
        print("run-log: nothing to archive")
        return
    old, new = lines[:-keep], lines[-keep:]
    n = len(list((OPS / "archive").glob("run-log-*.md"))) + 1 if (OPS / "archive").exists() else 1
    write(OPS / "archive" / f"run-log-{n}.md", "".join(old))
    write(p, "# Run log (older entries in ops/archive/)\n" + "".join(new))
    print(f"run-log: archived {len(old)} lines")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep-summaries", type=int, default=10)
    ap.add_argument("--keep-runlog", type=int, default=60)
    a = ap.parse_args()
    archive_summaries(a.keep_summaries)
    archive_runlog(a.keep_runlog)
