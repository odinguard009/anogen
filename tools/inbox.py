#!/usr/bin/env python3
"""Manage the owner's idea inbox (story/inbox.md).

Usage:
  inbox.py list [--json]
  inbox.py add "idea text"
  inbox.py done <index|all> [--note "where it landed"]
"""
import argparse
import datetime
import json
import re

from common import STORY, read, write

INBOX = STORY / "inbox.md"
HEAD_U = "## Unprocessed"
HEAD_P = "## Processed"


def _items(lines):
    items, cur = [], None
    for ln in lines:
        if re.match(r"^\s*[-*]\s+", ln):
            if cur:
                items.append(cur)
            cur = re.sub(r"^\s*[-*]\s+", "", ln).rstrip()
        elif ln.strip():
            if cur is None:
                cur = ln.strip()
            else:
                cur += " " + ln.strip()
    if cur:
        items.append(cur)
    return items


def parse():
    txt = read(INBOX)
    lines = txt.splitlines()
    iu = next((i for i, ln in enumerate(lines) if ln.strip() == HEAD_U), None)
    ip = next((i for i, ln in enumerate(lines) if ln.strip() == HEAD_P), None)
    if iu is None:
        header = txt.rstrip() + "\n\n" if txt.strip() else "# Idea inbox\n\n"
        return header, [], []
    header = "\n".join(lines[:iu]).rstrip() + "\n\n"
    u_end = ip if (ip is not None and ip > iu) else len(lines)
    unprocessed = _items(lines[iu + 1:u_end])
    processed = _items(lines[ip + 1:]) if ip is not None and ip > iu else []
    return header, unprocessed, processed


def render(header, unprocessed, processed):
    out = [header.rstrip() + "\n", HEAD_U + "\n"]
    out += [f"- {i}" for i in unprocessed]
    out += ["", HEAD_P + "\n"]
    out += [f"- {i}" for i in processed]
    return "\n".join(out).rstrip() + "\n"


def unprocessed_ideas():
    return parse()[1]


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    pl = sub.add_parser("list")
    pl.add_argument("--json", action="store_true")
    pa = sub.add_parser("add")
    pa.add_argument("text")
    pd = sub.add_parser("done")
    pd.add_argument("which")
    pd.add_argument("--note", default="")
    a = ap.parse_args()

    header, un, pr = parse()
    if a.cmd == "list":
        if a.json:
            print(json.dumps(un, ensure_ascii=False))
        elif not un:
            print("No unprocessed ideas.")
        else:
            for i, t in enumerate(un, 1):
                print(f"{i}. {t}")
    elif a.cmd == "add":
        un.append(" ".join(a.text.split()))
        write(INBOX, render(header, un, pr))
        print(f"Added. Unprocessed: {len(un)}")
    elif a.cmd == "done":
        if a.which == "all":
            idx = list(range(len(un)))
        else:
            try:
                idx = [int(a.which) - 1]
            except ValueError:
                raise SystemExit("which must be a number or 'all'")
            if not (0 <= idx[0] < len(un)):
                raise SystemExit("no such idea")
        today = datetime.date.today().isoformat()
        for i in idx:
            note = f" -> {a.note}" if a.note else ""
            pr.append(f"({today}) {un[i]}{note}")
        un = [t for i, t in enumerate(un) if i not in idx]
        write(INBOX, render(header, un, pr))
        print(f"Marked {len(idx)} processed. Unprocessed left: {len(un)}")


if __name__ == "__main__":
    main()
