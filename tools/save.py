#!/usr/bin/env python3
"""Commit everything and push.  Usage: save.py "message" [--no-push] [--trailer "text"]"""
import argparse
import subprocess
import sys

from common import ROOT


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("message")
    ap.add_argument("--no-push", action="store_true")
    ap.add_argument("--trailer", default="")
    a = ap.parse_args()

    git("add", "-A")
    if not git("status", "--porcelain").stdout.strip():
        print("Nothing to commit.")
        return
    msg = a.message + (("\n\n" + a.trailer) if a.trailer else "")
    r = git("commit", "-m", msg)
    if r.returncode != 0:
        print("COMMIT FAILED:", (r.stdout + r.stderr).strip())
        sys.exit(1)
    print("Committed:", a.message)
    if a.no_push:
        return
    if not git("remote").stdout.strip():
        print("No remote configured; not pushed.")
        return
    for attempt in (1, 2):
        r = git("push", "origin", "HEAD")
        if r.returncode == 0:
            print("Pushed.")
            return
        err = (r.stdout + r.stderr).strip()
    print("PUSH FAILED (work is committed locally):", err[-300:])
    sys.exit(3)


if __name__ == "__main__":
    main()
