#!/usr/bin/env python3
"""Insert a text block after an exact anchor line/sentence in a chapter. Usage: addbeat.py N  (JSON list of [anchor, new_text] on stdin). Exits 1 if an anchor is missing or not unique."""
import json, sys
from common import CHAPTERS
n = int(sys.argv[1])
p = CHAPTERS / f"chapter-{n:03d}.md"
t = p.read_text(encoding="utf-8")
for anchor, new in json.load(sys.stdin):
    if t.count(anchor) != 1:
        sys.exit(f"anchor not unique/missing ({t.count(anchor)}): {anchor[:60]}")
    t = t.replace(anchor, anchor + new, 1)
p.write_text(t, encoding="utf-8")
