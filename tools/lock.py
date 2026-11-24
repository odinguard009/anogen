#!/usr/bin/env python3
"""Single-runner lock: at most ONE bot (agent) may work on a job at a time.

Usage:
  lock.py acquire JOB [--owner NAME] [--ttl MINUTES]   exit 0 if acquired, 3 if another bot holds it
  lock.py release JOB
  lock.py status
A lock older than its TTL (default 120 min) is treated as stale (crashed run) and may be taken over.
The lock file is ops/lock.json (not committed).
"""
import argparse
import datetime
import sys

from common import OPS, load_json, save_json

PATH = OPS / "lock.json"


def now():
    return datetime.datetime.now(datetime.timezone.utc)


def parse(ts):
    return datetime.datetime.fromisoformat(ts)


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    a_ = sub.add_parser("acquire")
    a_.add_argument("job")
    a_.add_argument("--owner", default="unknown")
    a_.add_argument("--ttl", type=int, default=120)
    r_ = sub.add_parser("release")
    r_.add_argument("job")
    sub.add_parser("status")
    a = ap.parse_args()
    d = load_json(PATH, {})
    if a.cmd == "status":
        if not d:
            print("free")
        for job, v in d.items():
            age = (now() - parse(v["since"])).total_seconds() / 60
            stale = age > v["ttl"]
            print(f"{job}: held by {v['owner']} for {age:.0f} min{' (STALE)' if stale else ''}")
        return
    if a.cmd == "acquire":
        v = d.get(a.job)
        if v:
            age = (now() - parse(v["since"])).total_seconds() / 60
            if age <= v["ttl"]:
                print(f"BUSY: job '{a.job}' is held by {v['owner']} ({age:.0f} min). Do not start another bot.")
                sys.exit(3)
            print(f"Taking over stale lock from {v['owner']} ({age:.0f} min old).")
        d[a.job] = {"owner": a.owner, "since": now().isoformat(), "ttl": a.ttl}
        save_json(PATH, d)
        print(f"Lock acquired: {a.job} by {a.owner}")
    elif a.cmd == "release":
        d.pop(a.job, None)
        save_json(PATH, d)
        print("Lock released:", a.job)


if __name__ == "__main__":
    main()
