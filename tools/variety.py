#!/usr/bin/env python3
"""Draw random variety constraints for a chapter, avoiding the recent chapters' picks.

Usage: variety.py draw --chapter N [--peek] [--seed S]
The menu lives in tools/variety_menu.json (the owner can extend it).
The draw for a chapter is logged in story/variety_log.json and is stable on re-run.
"""
import argparse
import random

from common import STORY, TOOLS, load_json, save_json, setting_int

LOG = STORY / "variety_log.json"


def load_menu():
    return load_json(TOOLS / "variety_menu.json", {})


def draw(chapter, log_it=True, seed=None):
    log = load_json(LOG, [])
    for e in log:
        if e.get("chapter") == chapter:
            return e["picks"]
    window = setting_int("repeat_window")
    recent = [e["picks"] for e in log if e.get("chapter", 0) < chapter][-window:]
    rng = random.Random(seed)
    picks = {}
    for cat, opts in load_menu().items():
        used = {r.get(cat) for r in recent}
        pool = [o for o in opts if o not in used] or list(opts)
        picks[cat] = rng.choice(pool)
    if log_it:
        log.append({"chapter": chapter, "picks": picks})
        save_json(LOG, log)
    return picks


def format_picks(picks):
    return "\n".join(f"- {k}: {v}" for k, v in picks.items())


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["draw"])
    ap.add_argument("--chapter", type=int, required=True)
    ap.add_argument("--peek", action="store_true", help="do not record the draw")
    ap.add_argument("--seed", type=int, default=None)
    a = ap.parse_args()
    print(format_picks(draw(a.chapter, log_it=not a.peek, seed=a.seed)))


if __name__ == "__main__":
    main()
