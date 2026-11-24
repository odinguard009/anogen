#!/usr/bin/env python3
"""Track arcs and batch progress in ops/engine.json.

Usage:
  engine_state.py show
  engine_state.py arc-plan K --start S --end E [--name NAME] [--max M]
  engine_state.py arc-complete K          # release gate: all chapters of the arc must exist
  engine_state.py batch-start --mode n --target N
  engine_state.py batch-start --mode arc --arc K [--max M]
  engine_state.py batch-resume            # continue a stopped batch (keeps start/target)
  engine_state.py batch-stop --reason TEXT [--status stopped|done]
  engine_state.py next                    # what to do next (updates state when a batch ends)
"""
import argparse
import copy
import json
import sys

from common import OPS, chapter_path, load_json, next_chapter_number, save_json, setting_int

PATH = OPS / "engine.json"
DEFAULT = {
    "arcs": {},
    "batch": {"mode": "none", "target": 0, "arc": None, "max": None,
              "start_chapter": None, "status": "idle", "stop_reason": ""},
}


def load():
    d = load_json(PATH, None)
    if not d:
        d = copy.deepcopy(DEFAULT)
    d.setdefault("arcs", {})
    d.setdefault("batch", copy.deepcopy(DEFAULT["batch"]))
    return d


def save(d):
    save_json(PATH, d)


def missing_chapters(arc):
    return [n for n in range(arc["start"], arc["end"] + 1) if not chapter_path(n).exists()]


def compute_next(apply=False):
    d = load()
    n = next_chapter_number()
    b = d["batch"]
    arc = None
    cont = False
    reason = "no running batch (single chapter)"
    if b["status"] == "running":
        if b["mode"] == "n":
            done = n - b["start_chapter"]
            if done >= b["target"]:
                reason = f"batch complete ({done}/{b['target']})"
                if apply:
                    b["status"], b["stop_reason"] = "done", reason
            else:
                cont, reason = True, f"{done}/{b['target']} written"
        elif b["mode"] == "arc":
            arc = d["arcs"].get(str(b["arc"]))
            if not arc:
                reason = "arc not planned: plan it first (Development Editor)"
            elif n < arc["start"]:
                reason = f"next chapter {n} is before arc {b['arc']} starts ({arc['start']}); finish earlier chapters first"
            elif n > arc["end"]:
                reason = f"arc {b['arc']} fully written"
                if apply:
                    b["status"], b["stop_reason"] = "done", reason
                    if not missing_chapters(arc):
                        arc["status"] = "complete"
            elif b.get("max") and (n - b["start_chapter"]) >= b["max"]:
                reason = "max chapters for this batch reached before the arc ended"
                if apply:
                    b["status"], b["stop_reason"] = "stopped", reason
            else:
                cont = True
                reason = f"arc {b['arc']}: chapter {n} of {arc['start']}-{arc['end']}"
    if apply:
        save(d)
    return {"next_chapter": n, "continue": cont, "reason": reason, "batch": b, "arc": arc}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    sub.add_parser("next")
    p = sub.add_parser("arc-plan")
    p.add_argument("arc", type=int)
    p.add_argument("--start", type=int, required=True)
    p.add_argument("--end", type=int, required=True)
    p.add_argument("--name", default="")
    p.add_argument("--max", type=int, default=None)
    p = sub.add_parser("arc-complete")
    p.add_argument("arc", type=int)
    p = sub.add_parser("batch-start")
    p.add_argument("--mode", choices=["n", "arc"], required=True)
    p.add_argument("--target", type=int, default=0)
    p.add_argument("--arc", type=int, default=None)
    p.add_argument("--max", type=int, default=None)
    sub.add_parser("batch-resume")
    p = sub.add_parser("batch-stop")
    p.add_argument("--reason", required=True)
    p.add_argument("--status", choices=["stopped", "done"], default="stopped")
    a = ap.parse_args()

    d = load()
    if a.cmd == "show":
        if not d["arcs"]:
            print("Arcs: none planned")
        for k, v in sorted(d["arcs"].items(), key=lambda kv: int(kv[0])):
            print(f"Arc {k}: chapters {v['start']}-{v['end']} [{v['status']}] {v.get('name', '')}")
        print("Batch:", json.dumps(d["batch"], ensure_ascii=False))
        print("Next chapter:", next_chapter_number())
    elif a.cmd == "next":
        print(json.dumps(compute_next(apply=True), indent=2, ensure_ascii=False))
    elif a.cmd == "arc-plan":
        if a.start < 1 or a.end < a.start:
            sys.exit("invalid range")
        size = a.end - a.start + 1
        if a.max and size > a.max:
            sys.exit(f"arc has {size} chapters, above max {a.max}")
        for k, v in d["arcs"].items():
            if int(k) != a.arc and not (a.end < v["start"] or a.start > v["end"]):
                sys.exit(f"overlaps arc {k} ({v['start']}-{v['end']})")
        if a.max is None:
            a.max = setting_int("arc_default_max")
            if size > a.max:
                sys.exit(f"arc has {size} chapters, above default max {a.max}")
        old = d["arcs"].get(str(a.arc))
        status = old["status"] if old and (old["start"], old["end"]) == (a.start, a.end) else "planned"
        d["arcs"][str(a.arc)] = {"start": a.start, "end": a.end, "name": a.name or (old or {}).get("name", ""),
                                 "max": a.max, "status": status}
        save(d)
        print(f"Arc {a.arc} planned: chapters {a.start}-{a.end} ({size} chapters)")
    elif a.cmd == "arc-complete":
        arc = d["arcs"].get(str(a.arc))
        if not arc:
            sys.exit(f"arc {a.arc} is not planned")
        miss = missing_chapters(arc)
        if miss:
            print(f"Arc {a.arc} is NOT complete. Missing chapters: {miss[:20]}")
            sys.exit(2)
        arc["status"] = "complete"
        save(d)
        print(f"Arc {a.arc} marked complete (release gate open).")
    elif a.cmd == "batch-start":
        n = next_chapter_number()
        if a.mode == "n":
            if a.target < 1:
                sys.exit("--target must be >= 1")
            d["batch"] = {"mode": "n", "target": a.target, "arc": None, "max": None,
                          "start_chapter": n, "status": "running", "stop_reason": ""}
        else:
            if a.arc is None or str(a.arc) not in d["arcs"]:
                sys.exit("arc not planned: run arc-plan first")
            arc = d["arcs"][str(a.arc)]
            if n < arc["start"] or n > arc["end"]:
                sys.exit(f"next chapter {n} is outside arc {a.arc} ({arc['start']}-{arc['end']}): finish the other chapters/arcs first")
            if arc["status"] != "complete":
                arc["status"] = "writing"
            d["batch"] = {"mode": "arc", "target": 0, "arc": a.arc, "max": a.max,
                          "start_chapter": n, "status": "running", "stop_reason": ""}
        save(d)
        print("Batch started at chapter", n)
    elif a.cmd == "batch-resume":
        b = d["batch"]
        if b["mode"] == "none" or b["status"] not in ("stopped", "running"):
            sys.exit("no stopped batch to resume (status: %s)" % b["status"])
        b["status"], b["stop_reason"] = "running", ""
        save(d)
        print("Batch resumed; next chapter", next_chapter_number())
    elif a.cmd == "batch-stop":
        d["batch"]["status"], d["batch"]["stop_reason"] = a.status, a.reason
        save(d)
        print("Batch", a.status + ":", a.reason)


if __name__ == "__main__":
    main()
