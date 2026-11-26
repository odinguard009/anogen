#!/usr/bin/env python3
"""Commit everything and push.  Usage: save.py "message" [--no-push] [--trailer "text"]"""
import argparse
import subprocess
import sys
import time

from common import REPO, ROOT

# Stage only the project's own folders and files (never `git add -A`: a stray file would be pushed to a public repo).
_COMMON = ["docs", "tools", "tests", "roles", "AGENTS.md", "CLAUDE.md", "README.md", ".gitignore"]
if ROOT == REPO:  # flat layout (tests, scratch copies)
    TRACKED = ["chapters", "story", "ops", "out", "archive"] + _COMMON
else:  # novels/<slug>/ layout: engine files, templates, and ONLY the active novel
    TRACKED = ["engine", "templates", "novels/ACTIVE", str(ROOT.relative_to(REPO))] + _COMMON


def git(*args):
    return subprocess.run(["git", *args], cwd=REPO, capture_output=True, text=True)


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
    if ROOT != REPO:  # fix mixed encodings (cp1252 lines from other tools) before anything reads or commits them
        from common import normalize_utf8
        for folder in (ROOT / "story", ROOT / "ops", ROOT / "chapters"):
            for f in sorted(folder.rglob("*")) if folder.exists() else []:
                if f.suffix in (".md", ".txt", ".json", ".csv", ".jsonl") and f.is_file():
                    n = normalize_utf8(f)
                    if n:
                        print(f"note: {f.relative_to(REPO)}: {n} lines converted to UTF-8")
    if ROOT != REPO:  # novels layout: keep the derived story-memory index fresh (hash-based, best effort, never blocks a save)
        try:
            import memory_index
            memory_index.update()
        except Exception as e:
            print(f"note: memory index not updated ({type(e).__name__})")
    paths = [p for p in TRACKED if (REPO / p).exists()]
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
