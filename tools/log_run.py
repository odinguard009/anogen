#!/usr/bin/env python3
"""Append a run entry to ops/run-log.md and critic scores to ops/scores.csv.

Usage: log_run.py --chapter 12 --status ok --words 2310 --scores "4,3,4,-,4,3" --notes "..."
Scores order: tension,surprise,emotion,battle_clarity,voice,freshness ("-" = not applicable).
"""
import argparse
import datetime

from common import OPS, read, write

NAMES = ["tension", "surprise", "emotion", "battle_clarity", "voice", "freshness"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--command", default="tulis bab berikutnya")
    ap.add_argument("--chapter", type=int, default=None)
    ap.add_argument("--status", default="ok")
    ap.add_argument("--words", type=int, default=None)
    ap.add_argument("--scores", default="")
    ap.add_argument("--notes", default="")
    ap.add_argument("--quota-note", default="")
    a = ap.parse_args()

    now = datetime.datetime.now(datetime.timezone.utc)
    wib = now + datetime.timedelta(hours=7)
    head = f"### {now:%Y-%m-%d %H:%M} UTC ({wib:%H:%M} WIB) - {a.command}"
    if a.chapter is not None:
        head += f" - chapter {a.chapter}"
    head += f" - {a.status}"
    lines = [head]
    if a.words is not None:
        lines.append(f"- words: {a.words}")
    scores = [s.strip() for s in a.scores.split(",")] if a.scores else []
    if scores:
        lines.append("- scores: " + ", ".join(f"{n} {s}" for n, s in zip(NAMES, scores)))
    if a.notes:
        lines.append(f"- notes: {a.notes}")
    lines.append(f"- quota_note: {a.quota_note}")

    log = OPS / "run-log.md"
    cur = read(log) or "# Run log\n\nOne entry per run. The owner fills in quota_note after checking claude.ai/settings/usage.\n"
    write(log, cur.rstrip() + "\n\n" + "\n".join(lines) + "\n")

    if scores and a.chapter is not None:
        csvp = OPS / "scores.csv"
        cur = read(csvp) or "chapter," + ",".join(NAMES) + "\n"
        row = [str(a.chapter)] + (scores + ["-"] * 6)[:6]
        lines = cur.rstrip("\n").split("\n")
        # idempotent: one row per chapter (a retry or a critic fix replaces the row, never duplicates it)
        lines = [ln for i, ln in enumerate(lines) if i == 0 or ln.split(",")[0] != str(a.chapter)]
        lines.append(",".join(row))
        head_, body_ = lines[0], sorted(lines[1:], key=lambda s: int(s.split(",")[0]) if s.split(",")[0].isdigit() else 10 ** 9)
        write(csvp, "\n".join([head_] + body_) + "\n")
    print("Logged:", head)


if __name__ == "__main__":
    main()
