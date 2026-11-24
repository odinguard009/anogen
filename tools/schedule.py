#!/usr/bin/env python3
"""Schedule settings and the on/off switch (stored in ops/schedule.json).

The file only records the wish. Claude (in chat) creates or deletes the actual scheduled task
when the owner says "hidupkan jadwal" / "matikan jadwal".

Usage: schedule.py show | enable | disable | set KEY VALUE | set-task-id ID|none | cron
"""
import json
import sys

from common import OPS, load_json, save_json

PATH = OPS / "schedule.json"
DEFAULT = {
    "enabled": False,
    "timezone": "Asia/Jakarta",
    "runs_per_day": 2,
    "times": ["09:17", "21:43"],
    "command": "write next chapter",
    "chapters_per_run": 1,
    "arc_max_chapters": 50,
    "task_id": None,
}


def load():
    d = dict(DEFAULT)
    d.update(load_json(PATH, {}))
    return d


def convert(key, val):
    if key in ("runs_per_day", "chapters_per_run", "arc_max_chapters"):
        return int(val)
    if key == "times":
        ts = [t.strip() for t in val.split(",") if t.strip()]
        for t in ts:
            h, m = t.split(":")
            if not (0 <= int(h) < 24 and 0 <= int(m) < 60):
                raise ValueError(t)
        return ts
    if key == "enabled":
        return val.lower() in ("1", "true", "yes", "on")
    return val


def main():
    if len(sys.argv) < 2:
        sys.exit(__doc__)
    cmd, d = sys.argv[1], load()
    if cmd == "show":
        print(json.dumps(d, indent=2))
    elif cmd in ("enable", "disable"):
        d["enabled"] = cmd == "enable"
        save_json(PATH, d)
        print("schedule enabled =", d["enabled"], "(Claude must create/delete the scheduled task accordingly)")
    elif cmd == "set" and len(sys.argv) == 4:
        key = sys.argv[2]
        if key not in DEFAULT or key == "task_id":
            sys.exit(f"unknown key: {key}")
        try:
            d[key] = convert(key, sys.argv[3])
        except ValueError as e:
            sys.exit(f"bad value: {e}")
        save_json(PATH, d)
        print("set", key, "=", d[key])
    elif cmd == "set-task-id" and len(sys.argv) == 3:
        d["task_id"] = None if sys.argv[2].lower() == "none" else sys.argv[2]
        save_json(PATH, d)
        print("task_id =", d["task_id"])
    elif cmd == "cron":
        for t in d["times"]:
            h, m = t.split(":")
            print(f"CRON_TZ={d['timezone']} {int(m)} {int(h)} * * *")
    else:
        sys.exit(__doc__)


if __name__ == "__main__":
    main()
