#!/usr/bin/env python3
"""Compact status report (0 tokens). Usage: status.py"""
import csv

from common import OPS, STORY, chapter_files, load_json, read, settings, word_count
import engine_state
import inbox
import schedule


def main():
    st = settings()
    cf = chapter_files()
    total = sum(word_count(read(p)) for _, p in cf)
    print(f"Title: {st['title']}")
    print(f"Chapters written: {len(cf)} (~{total} words)")
    print(f"Next chapter: {engine_state.compute_next()['next_chapter']}")
    arcs = load_json(OPS / "engine.json", {}).get("arcs", {})
    for k, v in sorted(arcs.items(), key=lambda kv: int(kv[0])):
        have = sum(1 for n, _ in cf if v["start"] <= n <= v["end"])
        print(f"Arc {k}: {v['start']}-{v['end']} [{v['status']}] {have}/{v['end'] - v['start'] + 1} written")
    b = engine_state.load()["batch"]
    print(f"Batch: {b['mode']} / {b['status']} {b.get('stop_reason', '')}".rstrip())
    nx = engine_state.compute_next()
    if nx.get("critic_pending"):
        print("Critic pass pending: chapters %d-%d" % tuple(nx["critic_pending"]))
    if nx.get("audit_due_at"):
        print("Managing-editor audit due (through chapter %d)" % nx["audit_due_at"])
    print(f"Inbox: {len(inbox.unprocessed_ideas())} unprocessed idea(s)")
    prop = read(STORY / "proposals-audit.md")
    if prop.strip():
        print(f"Proposals pending: {sum(1 for l in prop.splitlines() if l.lstrip().startswith(('-', '*')))} entries in story/proposals-audit.md (owner decides)")
    sc = schedule.load()
    print(f"Schedule: {'ON' if sc['enabled'] else 'OFF'} ({', '.join(sc['times'])} {sc['timezone']})")
    rows = list(csv.reader(read(OPS / "scores.csv").splitlines()))
    if len(rows) > 1:
        last = rows[-3:]
        print("Recent critic scores:")
        for r in last:
            print(f"  {r[0]}: " + ", ".join(r[1:]))


if __name__ == "__main__":
    main()
