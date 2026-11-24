#!/usr/bin/env python3
"""Apply targeted find/replace patches to a file in ONE call.

Usage:
  python3 tools/patch.py chapters/chapter-012.md <<'EOF'
  [{"find": "exact old text", "replace": "new text"}, ...]
  EOF
Each "find" must occur exactly once, otherwise that patch is skipped and reported.
"""
import json
import sys
from pathlib import Path


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    target = Path(sys.argv[1])
    patches = json.load(sys.stdin)
    text = target.read_text(encoding="utf-8")
    applied, bad = 0, []
    for i, p in enumerate(patches):
        find, repl = p["find"], p["replace"]
        c = text.count(find)
        if c != 1:
            bad.append(f"patch {i}: found {c} times: {find[:50]!r}")
            continue
        text = text.replace(find, repl, 1)
        applied += 1
    if applied:
        target.write_text(text, encoding="utf-8")
    print(f"Applied {applied}/{len(patches)} patches to {target}")
    for b in bad:
        print("SKIPPED", b)
    sys.exit(1 if bad else 0)


if __name__ == "__main__":
    main()
