#!/usr/bin/env python3
"""Deterministic go/no-go for a chapter range (0 tokens). Run after a writer batch, before the critic.

Usage: verify_batch.py A-B [--strict-exit]
Every subprocess result is checked: a crashed checker, a missing git, or a git error is a PROBLEM with its cause.
Per chapter: file exists, '# Title' first line, word count in range, summary present, an outline line exists,
scores row present, check_chapter has no ISSUE, and the chapter file is committed (clean in git).
Prints one line per problem and 'VERIFY: OK' or 'VERIFY: n problem(s)'. Exit code 1 on problems.
"""
import csv
import re
import subprocess
import sys

from common import OPS, ROOT, STORY, TOOLS, chapter_path, read, setting_int, word_count
import context_pack


def run_cmd(argv):
    """Run a command; returns (returncode, stdout, stderr). A missing executable is returncode 127, never a pass."""
    try:
        r = subprocess.run(argv, capture_output=True, text=True, cwd=ROOT)
        return r.returncode, r.stdout, r.stderr
    except OSError as e:
        return 127, "", f"cannot run {argv[0]}: {e}"


def git_state():
    """(ok, reason). ok only if git runs and ROOT is a work tree."""
    rc, out, err = run_cmd(["git", "rev-parse", "--is-inside-work-tree"])
    if rc != 0 or out.strip() != "true":
        return False, f"git unavailable or not a git work tree (rc={rc}): {(err or out).strip()[:120]}"
    return True, ""


def problems_for(n, git_ok=None):
    p = chapter_path(n)
    if not p.exists():
        return [f"ch {n}: file missing"]
    try:
        return _problems_for(n, p, git_ok)
    except Exception as e:  # a crash inside verification is a failed verification, never a pass
        return [f"ch {n}: verification crashed: {type(e).__name__}: {str(e)[:150]}"]


def _problems_for(n, p, git_ok):
    out = []
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
    rc, so, se = run_cmd([sys.executable, str(TOOLS / "check_chapter.py"), str(p), "--strict"])
    if "SUMMARY:" not in so:
        out.append(f"ch {n}: checker crashed or printed no SUMMARY (rc={rc}): {(se or so).strip()[-150:]}")
    else:
        out += [f"ch {n}: {ln}" for ln in so.splitlines() if ln.startswith("ISSUE:")]
        if rc != 0 and not any(ln.startswith("ISSUE:") for ln in so.splitlines()):
            out.append(f"ch {n}: checker exited {rc} without a listed ISSUE: {se.strip()[-150:]}")
    if git_ok is None:
        git_ok = git_state()
    if not git_ok[0]:
        out.append(f"ch {n}: cannot verify commit state: {git_ok[1]}")
    else:
        rc, so, se = run_cmd(["git", "status", "--porcelain", "--", str(p)])
        if rc != 0:
            out.append(f"ch {n}: git status failed (rc={rc}): {se.strip()[:120]}")
        elif so.strip():
            out.append(f"ch {n}: not committed ({so.strip()[:2].strip() or 'changed'})")
        else:
            rc, so, se = run_cmd(["git", "ls-files", "--error-unmatch", "--", str(p)])
            if rc != 0:
                out.append(f"ch {n}: file is not tracked by git")
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
    g = git_state()
    probs = [x for n in range(lo, hi + 1) for x in problems_for(n, g)]
    for x in probs:
        print("PROBLEM:", x)
    print("VERIFY: OK" if not probs else f"VERIFY: {len(probs)} problem(s)")
    sys.exit(1 if probs else 0)


if __name__ == "__main__":
    main()
