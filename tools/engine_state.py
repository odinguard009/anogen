#!/usr/bin/env python3
"""Track arcs and batch progress in ops/engine.json.

Usage:
  engine_state.py show
  engine_state.py arc-plan K --start S --end E [--name NAME] [--max M]
  engine_state.py arc-complete K          # release gate: all chapters of the arc must exist
  engine_state.py batch-start --mode n --target N
  engine_state.py batch-start --mode arc --arc K [--max M]
  engine_state.py mark critic|audit N     # critic/audit done through chapter N (validated; records chapter hashes)
  engine_state.py rereview C [C ...]      # critic re-reviewed exactly these chapters (already reviewed, now edited); nothing else is blessed
  engine_state.py baseline-reviewed       # owner-accepted: record current hashes for chapters 1..critic_through
  engine_state.py batch-resume            # continue a stopped batch (keeps start/target)
  engine_state.py batch-stop --reason TEXT [--status stopped|done]
  engine_state.py next [--no-apply]       # what to do next (updates batch status when a batch ends unless --no-apply)
"""
import argparse
import copy
import json
import sys

from common import OPS, chapter_files, chapter_path, file_hash, load_json, next_chapter_number, save_json, setting_int

PATH = OPS / "engine.json"
DEFAULT = {
    "arcs": {},
    "batch": {"mode": "none", "target": 0, "arc": None, "max": None,
              "start_chapter": None, "status": "idle", "stop_reason": ""},
    "critic_through": 0,
    "audit_through": 0,
    "reviewed": {},
}


def load():
    d = load_json(PATH, None)
    if not d:
        d = copy.deepcopy(DEFAULT)
    d.setdefault("arcs", {})
    d.setdefault("batch", copy.deepcopy(DEFAULT["batch"]))
    d.setdefault("critic_through", 0)
    d.setdefault("audit_through", 0)
    d.setdefault("reviewed", {})
    return d


def save(d):
    save_json(PATH, d, backup=True)  # atomic write; previous state kept as engine.json.bak


def missing_chapters(arc):
    return [n for n in range(arc["start"], arc["end"] + 1) if not chapter_path(n).exists()]


def hold_info(d):
    h = d.get("hold") or {}
    return h.get("reason", "") if h.get("active") else ""


def compute_next(apply=False):
    d = load()
    hold = hold_info(d)
    if hold:
        # HOLD (owner order): nothing may be written or reviewed until the owner clears it
        return {"next_chapter": next_chapter_number(), "continue": False, "reason": "HOLD: " + hold,
                "hold": True, "batch": d["batch"], "arc": None, "writer_range": None, "gap_note": "",
                "critic_pending": None, "critic_waiting": None, "critic_changed_after_review": [],
                "rereview_pending": [], "rereview_blocks_writing": False,
                "audit_with_critic": False, "audit_due_at": None}
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
            elif b.get("max") and (n - b["start_chapter"]) >= b["max"]:
                reason = "max chapters for this batch reached before the arc ended"
                if apply:
                    b["status"], b["stop_reason"] = "stopped", reason
            else:
                cont = True
                reason = f"arc {b['arc']}: chapter {n} of {arc['start']}-{arc['end']}"
    if apply:
        save(d)
    cf = chapter_files()
    hi = cf[-1][0] if cf else 0
    existing = {k for k, _ in cf}
    limit = None
    if b["status"] in ("running",) and b["mode"] == "n":
        limit = b["start_chapter"] + b["target"] - 1
    elif b["status"] in ("running",) and b["mode"] == "arc" and arc:
        limit = arc["end"]
        if b.get("max"):
            limit = min(limit, b["start_chapter"] + b["max"] - 1)
    # never plan over chapters that already exist (gap fill): stop before the next existing chapter
    later = [k for k in existing if k > n]
    stop_at = (min(later) - 1) if later else None
    writer_range, gap_note = None, ""
    if cont and limit and n <= limit:
        end_ = min(n + 4, limit)
        if stop_at is not None and stop_at < end_:
            end_ = stop_at
            gap_note = f"gap: chapter {n} is missing but chapter {min(later)} exists; range clamped to {n}-{end_} (never overwrite)"
        writer_range = [n, end_]
    elif not cont and b["status"] not in ("running",) and reason.startswith("no running batch"):
        writer_range = [n, n]  # single-chapter mode
    ct = d.get("critic_through", 0)
    span = setting_int("critic_span")
    boundary = (ct // span + 1) * span
    end_c = min(hi, boundary)
    running = b["status"] == "running" and cont
    arc_done = bool(arc) and hi >= arc["end"]
    critic_due = hi > ct and (hi >= boundary or not running or arc_done)
    critic_pending = [ct + 1, end_c] if critic_due else None
    critic_waiting = [ct + 1, hi] if (hi > ct and not critic_due) else None
    reviewed = d.get("reviewed", {})
    changed = [k for k in sorted(existing) if k <= ct and str(k) in reviewed and reviewed[str(k)] != file_hash(chapter_path(k))]
    if changed:
        writer_range = None  # changed chapters are an editorial task that must run before more writing
    at = d.get("audit_through", 0)
    audit_missed = (ct // 10) * 10 if (ct // 10) * 10 > at else None
    audit_with_critic = bool(critic_pending) and critic_pending[1] % 10 == 0 and critic_pending[1] > at
    return {"next_chapter": n, "continue": cont, "reason": reason, "batch": b, "arc": arc,
            "writer_range": writer_range, "gap_note": gap_note,
            "critic_pending": critic_pending, "critic_waiting": critic_waiting,
            "critic_changed_after_review": changed,
            "rereview_pending": changed,
            "rereview_blocks_writing": bool(changed),
            "audit_with_critic": audit_with_critic, "audit_due_at": audit_missed}


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("show")
    p = sub.add_parser("next")
    p.add_argument("--no-apply", action="store_true", help="pure read: do not update batch status")
    sub.add_parser("baseline-reviewed")
    p = sub.add_parser("rereview")
    p.add_argument("chapters", type=int, nargs="+")
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
    p = sub.add_parser("hold")
    p.add_argument("action", choices=["set", "clear", "show"])
    p.add_argument("--reason", default="")
    p = sub.add_parser("mark")
    p.add_argument("what", choices=["critic", "audit"])
    p.add_argument("chapter", type=int)
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
        print(json.dumps(compute_next(apply=not a.no_apply), indent=2, ensure_ascii=False))
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
        if d.get("critic_through", 0) < arc["end"]:
            print(f"Arc {a.arc} NOT released: critic pass done only through chapter {d.get('critic_through', 0)} (need {arc['end']}).")
            sys.exit(2)
        stale = [k for k in range(arc["start"], arc["end"] + 1)
                 if str(k) in d.get("reviewed", {}) and d["reviewed"][str(k)] != file_hash(chapter_path(k))]
        if stale:
            print(f"Arc {a.arc} NOT released: chapters changed after their critic review: {stale[:20]}")
            sys.exit(2)
        arc["status"] = "complete"
        save(d)
        print(f"Arc {a.arc} marked complete (release gate open).")
    elif a.cmd == "hold":
        if a.action == "set":
            if not a.reason:
                sys.exit("--reason is required")
            d["hold"] = {"active": True, "reason": a.reason}
            save(d)
            print("HOLD set:", a.reason)
        elif a.action == "clear":
            d["hold"] = {"active": False, "reason": ""}
            save(d)
            print("HOLD cleared (only the owner may do this).")
        else:
            print(json.dumps(d.get("hold") or {"active": False}))
    elif a.cmd in ("batch-start", "batch-resume", "arc-plan") and hold_info(d):
        sys.exit("HOLD is set: " + hold_info(d) + ". Write nothing. Only the owner can clear it (engine_state.py hold clear).")
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
    elif a.cmd == "mark":
        key = a.what + "_through"
        cur = d.get(key, 0)
        hi = (chapter_files() or [(0, None)])[-1][0]
        if a.chapter > hi:
            sys.exit(f"cannot mark {a.what} through {a.chapter}: highest chapter is {hi}")
        if a.chapter < cur:
            sys.exit(f"{key} is already {cur}; marks never go backwards (use 'rereview C ...' for edited chapters)")
        if a.what == "audit" and a.chapter > d.get("critic_through", 0):
            sys.exit(f"audit cannot pass the critic: critic_through is {d.get('critic_through', 0)}")
        if a.what == "critic":
            miss = [k for k in range(cur + 1, a.chapter + 1) if not chapter_path(k).exists()]
            if miss:
                sys.exit(f"cannot mark critic: missing chapters {miss[:10]}")
            rev = d.setdefault("reviewed", {})
            for k in range(cur + 1, a.chapter + 1):
                rev[str(k)] = file_hash(chapter_path(k))
        d[key] = max(cur, a.chapter)
        save(d)
        print(f"{a.what} done through chapter {d[key]}")
    elif a.cmd == "rereview":
        rev = d.setdefault("reviewed", {})
        ct = d.get("critic_through", 0)
        bad = sorted({k for k in a.chapters if not chapter_path(k).exists()})
        if bad:
            sys.exit(f"cannot re-review: missing chapter files {bad[:10]}")
        bad = sorted({k for k in a.chapters if k > ct})
        if bad:
            sys.exit(f"cannot re-review chapters {bad[:10]}: not reviewed yet (critic_through is {ct}); use 'mark critic'")
        for k in sorted(set(a.chapters)):
            rev[str(k)] = file_hash(chapter_path(k))
        save(d)
        print("re-reviewed (hashes updated) only:", sorted(set(a.chapters)))
    elif a.cmd == "baseline-reviewed":
        rev = d.setdefault("reviewed", {})
        for k in range(1, d.get("critic_through", 0) + 1):
            if chapter_path(k).exists():
                rev[str(k)] = file_hash(chapter_path(k))
        save(d)
        print(f"recorded current text of chapters 1-{d.get('critic_through', 0)} as reviewed (owner-accepted baseline)")
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
