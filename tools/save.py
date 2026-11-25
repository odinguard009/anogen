#!/usr/bin/env python3
"""Commit everything and push.  Usage: save.py "message" [--no-push] [--trailer "text"]"""
import argparse
import subprocess
import sys
import time

from common import ROOT

# Stage only the project's own folders and files (never `git add -A`: a stray file would be pushed to a public repo).
TRACKED = ["chapters", "story", "ops", "out", "docs", "tools", "roles", "archive",
           "AGENTS.md", "CLAUDE.md", "README.md", ".gitignore"]


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def push_loop():
    if not git("remote").stdout.strip():
        print("No remote configured; not pushed.")
        return
    err = ""
    for attempt in (1, 2, 3, 4):
        r = git("push", "origin", "HEAD")
        if r.returncode == 0:
            print("Pushed.")
            return
        err = (r.stdout + r.stderr).strip()
        branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        # rejected because the remote has newer commits: fetch and MERGE (never force, never rebase)
        if branch and branch != "HEAD" and git("fetch", "origin", branch).returncode == 0:
            m = git("merge", "--no-edit", "FETCH_HEAD")
            if m.returncode != 0:
                git("merge", "--abort")
                print("MERGE CONFLICT with the remote branch (work is committed locally; merge aborted):", (m.stdout + m.stderr).strip()[-300:])
                sys.exit(3)
        time.sleep(2 * attempt)
    print("PUSH FAILED (work is committed locally):", err[-300:])
    sys.exit(3)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("message")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--trailer", default="")
    a = ap.parse_args()

    if git("rev-parse", "--is-inside-work-tree").returncode != 0:
        print("ERROR: not a git repository; nothing saved.")
        sys.exit(1)
    paths = [p for p in TRACKED if (ROOT / p).exists()]
    r = git("add", "-A", "--", *paths)
    if r.returncode != 0:
        print("ERROR: git add failed:", (r.stdout + r.stderr).strip())
        sys.exit(1)
    leftovers = [ln for ln in git("status", "--porcelain").stdout.splitlines() if ln.startswith("??")]
    if leftovers:
        print("note: untracked files outside the project folders were NOT added:", "; ".join(leftovers)[:200])
    if not git("diff", "--cached", "--quiet").returncode:
        # nothing new to commit; still finish an earlier push that failed (branch ahead of its upstream)
        branch = git("rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
        ahead = git("rev-list", "--count", f"origin/{branch}..HEAD")
        if a.no_push or ahead.returncode != 0 or ahead.stdout.strip() in ("", "0"):
            print("Nothing to commit.")
            return
        print(f"Nothing new to commit; {ahead.stdout.strip()} earlier commit(s) not pushed yet: retrying push.")
        return push_loop()
    msg = a.message + (("\n\n" + a.trailer) if a.trailer else "")
    r = git("commit", "-m", msg)
    if r.returncode != 0:
        print("COMMIT FAILED:", (r.stdout + r.stderr).strip())
        sys.exit(1)
    print("Committed:", a.message)
    if a.no_push:
        return
    push_loop()


if __name__ == "__main__":
    main()
