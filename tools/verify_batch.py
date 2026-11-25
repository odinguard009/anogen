#!/usr/bin/env python3
"""Deterministic go/no-go for a chapter range (0 tokens). Run after a writer batch, before the critic.

Usage: verify_batch.py A-B [--strict-exit]
Per chapter: file exists, '# Title' first line, word count in range, summary present, an outline line exists,
scores row present, check_chapter has no ISSUE, and the chapter file is committed (clean in git).
Prints one line per problem and 'VERIFY: OK' or 'VERIFY: n problem(s)'. Exit code 1 on problems.
"""
import csv
import re
import subprocess
import sys

from common import OPS, ROOT, STORY, chapter_path, read, setting_int, word_count
import context_pack


def problems_for(n):
    out = []
    p = chapter_path(n)
    if not p.exists():
        return [f"ch {n}: file missing"]
    raw = read(p)
    if not raw.lstrip().startswith("#"):
        out.append(f"ch {n}: no '# Title' first line")
    wc = word_count(raw)
    lo, hi = setting_int("chapter_words_min"), setting_int("chapter_words_max")
    if not lo <= wc <= hi:
        out.append(f"ch {n}: {wc} words outside {lo}-{hi}")
    if not re.search(r"(?mi)^\W*Ch\.?\s*%d\b" % n, read(STORY / "bible" / "summaries.md") + _archived_summaries()):
        out.append(f"ch {n}: no summary in summaries.md (canon keeper step missing)")
    if not context_pack.outline_lines(n, 1):
        out.append(f"ch {n}: no outline line")
    rows = {r[0] for r in csv.reader(read(OPS / "scores.csv").splitlines()) if r}
    if str(n) not in rows:
        out.append(f"ch {n}: no row in ops/scores.csv")
    c = subprocess.run([sys.executable, str(__import__("common").TOOLS / "check_chapter.py"), str(p)],
                       capture_output=True, text=True, cwd=ROOT)
    out += [f"ch {n}: {ln}" for ln in c.stdout.splitlines() if ln.startswith("ISSUE:")]
    st = subprocess.run(["git", "status", "--porcelain", "--", str(p)], capture_output=True, text=True, cwd=ROOT)
    if st.returncode == 0 and st.stdout.strip():
        out.append(f"ch {n}: not committed ({st.stdout.strip()[:2]})")
    return out


def _archived_summaries():
    d = STORY / "bible" / "archive"
    return "".join(read(f) for f in sorted(d.glob("summaries-*.md"))) if d.is_dir() else ""


def main():
    a = sys.argv[1] if len(sys.argv) > 1 else ""
    m = re.match(r"^(\d+)(?:-(\d+))?$", a)
    if not m:
        sys.exit(__doc__)
    lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
    probs = [x for n in range(lo, hi + 1) for x in problems_for(n)]
    for x in probs:
        print("PROBLEM:", x)
    print("VERIFY: OK" if not probs else f"VERIFY: {len(probs)} problem(s)")
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
