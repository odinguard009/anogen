#!/usr/bin/env python3
"""Rename names across the active novel (story/ and chapters/) from a map. Whole words only, case-sensitive.

Usage: rename.py [--map story/rename-map.json] [--apply]
  The map is a JSON object {"Old": "New", ...}. Longer names are replaced first ("Faceless Mantle" before "Mantle").
  Default is a DRY RUN (nothing is written). --apply writes the files (atomic) and removes duplicate lines
  that the rename creates in story/bible/canon_names.txt.
Never touched: the map itself, files listed in the map's "_skip" list, ops/ (history), out/ (built files), archive/.
Chapters that change get a new hash: afterwards record them with `engine_state.py baseline-reviewed`
ONLY if the change is a pure rename (read the dry-run report first) and log it in ops/decisions.md.
"""
import argparse
import re
import sys

from common import ROOT, STORY, CHAPTERS, load_json, read, write


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--map", default=str(STORY / "rename-map.json"))
    ap.add_argument("--apply", action="store_true")
    a = ap.parse_args()
    data = load_json(a.map, None)
    if not isinstance(data, dict) or not data:
        sys.exit(f"ERROR: {a.map} must be a non-empty JSON object {{\"Old\": \"New\"}}")
    skip = set(data.get("_skip", []))
    pairs = {k: v for k, v in data.items() if not k.startswith("_")}
    for k, v in pairs.items():
        if not isinstance(v, str) or not k or not v:
            sys.exit(f"ERROR: bad map entry {k!r} -> {v!r}")
        if k == v:
            sys.exit(f"ERROR: map entry maps {k!r} to itself")
    olds = sorted(pairs, key=len, reverse=True)
    rx = re.compile(r"(?<![\w])(" + "|".join(re.escape(o) for o in olds) + r")(?![\w])")
    from pathlib import Path
    map_path = Path(a.map).resolve()
    files = []
    for base in (STORY, CHAPTERS):
        if base.is_dir():
            files += [p for p in sorted(base.rglob("*")) if p.is_file() and p.suffix in (".md", ".txt", ".json")]
    total, changed, counts = 0, [], {}
    for p in files:
        if p.resolve() == map_path or str(p.relative_to(ROOT)) in skip:
            continue
        txt = read(p)
        n = 0

        def sub(m):
            nonlocal n
            n += 1
            counts[m.group(1)] = counts.get(m.group(1), 0) + 1
            return pairs[m.group(1)]
        new = rx.sub(sub, txt)
        if n:
            changed.append((p, n, new))
            total += n
    for p, n, _ in changed:
        print(f"{n:4d}  {p.relative_to(ROOT)}")
    print("per name:", ", ".join(f"{k}->{pairs[k]} x{counts[k]}" for k in sorted(counts, key=counts.get, reverse=True)))
    print(f"{total} replacement(s) in {len(changed)} file(s). " + ("APPLIED." if a.apply else "DRY RUN: nothing written (add --apply)."))
    if not a.apply:
        return
    for p, _, new in changed:
        write(p, new)
    cn = STORY / "bible" / "canon_names.txt"
    if cn.exists():
        seen, out = set(), []
        for ln in read(cn).splitlines():
            if ln.startswith("#") or not ln.strip() or ln not in seen:
                out.append(ln)
                seen.add(ln)
        write(cn, "\n".join(out) + "\n")
    print("canon_names.txt de-duplicated.")


if __name__ == "__main__":
    main()
