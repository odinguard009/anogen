#!/usr/bin/env python3
"""Record and report what each agent run cost (0 tokens). Standard library only.

The repo never calls a model itself, so the orchestrator reports usage after every agent:
  usage_log.py add --role writer --tier standard --model sonnet --range 26-30 \\
       --input 61000 --output 14000 [--cache-read N] [--cache-write N] --seconds 540 \\
       --outcome ok|failed|retry --source reported|manual|estimate
Use --source reported ONLY for numbers the host/provider gave you; owner-read usage page deltas are 'manual'.
  usage_log.py report            totals by role, per chapter, per 1,000 words, retries
Optional ops/prices.json {"<model>": {"input": usd_per_million, "output": usd_per_million}} enables cost lines;
without it cost is reported as unknown (nothing is invented).
"""
import argparse
import datetime
import json
import re
import sys

from common import OPS, chapter_path, load_json, read, word_count

LOG = OPS / "usage.jsonl"


def rows():
    out = []
    for ln in read(LOG).splitlines():
        if ln.strip():
            try:
                out.append(json.loads(ln))
            except ValueError:
                print("skipping unreadable line in usage.jsonl", file=sys.stderr)
    return out


def chapter_span(rng):
    m = re.fullmatch(r"(\d+)(?:-(\d+))?", rng or "")
    if not m:
        return []
    lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
    return list(range(lo, hi + 1))


def cmd_add(a):
    row = {"ts": datetime.datetime.now(datetime.timezone.utc).isoformat(timespec="seconds"),
           "role": a.role, "tier": a.tier, "model": a.model, "range": a.range,
           "input": a.input, "output": a.output, "cache_read": a.cache_read, "cache_write": a.cache_write,
           "seconds": a.seconds, "outcome": a.outcome, "source": a.source, "note": a.note}
    OPS.mkdir(parents=True, exist_ok=True)
    with open(LOG, "a", encoding="utf-8") as fh:
        fh.write(json.dumps(row, ensure_ascii=False) + "\n")
    print("logged usage:", a.role, a.range, a.outcome)


def cmd_report(_a):
    rs = rows()
    if not rs:
        print("No usage recorded yet (ops/usage.jsonl is empty). Token and cost figures are UNMEASURED.")
        return
    prices = load_json(OPS / "prices.json", {})
    by = {}
    for r in rs:
        b = by.setdefault(r["role"], {"runs": 0, "in": 0, "out": 0, "sec": 0, "retries": 0, "failed": 0, "cost": 0.0, "costed": 0, "unreported": 0})
        b["runs"] += 1
        b["retries"] += r["outcome"] == "retry"
        b["failed"] += r["outcome"] == "failed"
        b["sec"] += r.get("seconds") or 0
        if r.get("input") is None and r.get("output") is None:
            b["unreported"] += 1
        b["in"] += r.get("input") or 0
        b["out"] += r.get("output") or 0
        p = prices.get(r.get("model") or "")
        if p and r.get("input") is not None and r.get("output") is not None:
            b["cost"] += (r["input"] * p["input"] + r["output"] * p["output"]) / 1e6
            b["costed"] += 1
    tot_in = sum(b["in"] for b in by.values())
    tot_out = sum(b["out"] for b in by.values())
    print(f"{'role':18}{'runs':>5}{'input':>10}{'output':>9}{'sec':>7}{'retry':>6}{'fail':>5}  cost")
    for role, b in sorted(by.items()):
        cost = f"{b['cost']:.2f} USD" if b["costed"] == b["runs"] and b["runs"] else ("unknown" if not b["costed"] else f"partial {b['cost']:.2f} USD")
        print(f"{role:18}{b['runs']:>5}{b['in']:>10}{b['out']:>9}{b['sec']:>7.0f}{b['retries']:>6}{b['failed']:>5}  {cost}")
    drafted = set()
    for r in rs:
        if r["role"] == "writer" and r["outcome"] == "ok":
            drafted.update(chapter_span(r["range"]))
    words = sum(word_count(read(chapter_path(n))) for n in drafted if chapter_path(n).exists())
    print(f"writer chapters with usage logged: {len(drafted)} ({words} words)")
    if drafted and (tot_in or tot_out):
        print(f"all roles: {(tot_in + tot_out) / len(drafted):.0f} tokens per logged chapter; "
              f"{(tot_in + tot_out) / max(words, 1) * 1000:.0f} tokens per 1,000 words")
    srcs = sorted({r.get("source", "?") for r in rs})
    print("sources:", ", ".join(srcs), "(only 'reported' is provider data)")
    if any(b["unreported"] for b in by.values()):
        print("note: some runs have no token counts; totals are lower bounds.")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    p = sub.add_parser("add")
    p.add_argument("--role", required=True, choices=["orchestrator", "development_editor", "writer", "critic", "audit", "rewrite", "other"])
    p.add_argument("--tier", default="")
    p.add_argument("--model", default="")
    p.add_argument("--range", default="")
    p.add_argument("--input", type=int, default=None)
    p.add_argument("--output", type=int, default=None)
    p.add_argument("--cache-read", dest="cache_read", type=int, default=None)
    p.add_argument("--cache-write", dest="cache_write", type=int, default=None)
    p.add_argument("--seconds", type=float, default=None)
    p.add_argument("--outcome", choices=["ok", "failed", "retry"], default="ok")
    p.add_argument("--source", choices=["reported", "manual", "estimate"], default="manual")
    p.add_argument("--note", default="")
    sub.add_parser("report")
    a = ap.parse_args()
    {"add": cmd_add, "report": cmd_report}[a.cmd](a)


if __name__ == "__main__":
    main()
