#!/usr/bin/env python3
"""Risk level of a chapter for the self-review depth (0 tokens, no AI; standard library only).

Usage: risk.py N [--json]
HIGH   : a reveal CONFIRM (rung C in story/bible/reveal-ladder.md) falls in this chapter, the outline line or the chapter's
         summary names a death, a betrayal, a true identity or an arc climax, this is the last chapter of an arc, or an Unbind.
MEDIUM : a hint/doubt/evidence rung (H, D, E) falls here, a first-use ledger entry is planned here, an open debt is due here,
         or the outline line names a relationship turn or a new power.
LOW    : everything else.
Rules are plain keyword and table matches on the story files, never a judgement of the prose. It only chooses how deep the
self-review goes; it never changes the review frequency (critic per 10 chapters stays locked).
"""
import json
import re
import sys

from common import OPS, STORY, load_json, read
import context_pack

HIGH_WORDS = re.compile(r"\b(dies|died|death|killed|kills|murder\w*|betray\w*|true identity|identity|reveal\w*|climax|finale|unbind|execut\w*)\b", re.I)
MED_WORDS = re.compile(r"\b(kiss\w*|confess\w*|love|engage\w*|first use|new power|awaken\w*|armor-up|raiment|loan|lend\w*|promise\w*)\b", re.I)


def rungs_for(n):
    """{'C': [...], 'HDE': [...]} lines of the reveal ladder with a rung at chapter n."""
    out = {"C": [], "HDE": []}
    for ln in read(STORY / "bible" / "reveal-ladder.md").splitlines():
        for m in re.finditer(r"\b([HDEC])\s+(\d+)(?:-(\d+))?\b", ln):
            lo, hi = int(m.group(2)), int(m.group(3) or m.group(2))
            if lo <= n <= hi:
                out["C" if m.group(1) == "C" else "HDE"].append(ln.strip()[:90])
                break
    return out


def due_debts(n):
    out = []
    for ln in read(STORY / "bible" / "debts.md").splitlines():
        if "[open]" in ln:
            d = re.search(r"due:\s*ch\s*([\d,\s\-]+)", ln)
            if d and n in {int(x) for x in re.findall(r"\d+", d.group(1))}:
                out.append(ln.strip()[:90])
    return out


def arc_end(n):
    arcs = load_json(OPS / "engine.json", {}).get("arcs", {})
    return any(isinstance(a, dict) and a.get("end") == n for a in arcs.values())


def summary_for(n):
    m = re.search(r"(?ms)^#{1,3}\s*Ch\.?\s*%d\b.*?(?=^#{1,3}\s*Ch\.?\s*\d+|\Z)" % n, read(STORY / "bible" / "summaries.md"))
    return m.group(0) if m else ""


def assess(n):
    reasons, level = [], "LOW"
    ol = " ".join(context_pack.outline_lines(n, 1))
    text = ol + " " + summary_for(n)
    r = rungs_for(n)
    if r["C"]:
        level = "HIGH"; reasons.append("reveal CONFIRM: " + r["C"][0])
    if arc_end(n):
        level = "HIGH"; reasons.append("last chapter of an arc")
    m = HIGH_WORDS.search(text)
    if m:
        level = "HIGH"; reasons.append(f"keyword '{m.group(0)}' in outline/summary")
    if level != "HIGH":
        if r["HDE"]:
            level = "MEDIUM"; reasons.append("ladder rung: " + r["HDE"][0])
        dd = due_debts(n)
        if dd:
            level = "MEDIUM"; reasons.append("open debt due: " + dd[0])
        m = MED_WORDS.search(text)
        if m:
            level = "MEDIUM"; reasons.append(f"keyword '{m.group(0)}' in outline/summary")
        fu = [ln for ln in read(STORY / "bible" / "first-use.md").splitlines() if re.search(r"\bch %d\b" % n, ln) and "planned" in ln.lower()]
        if fu:
            level = "MEDIUM"; reasons.append("first use planned: " + fu[0][:70])
    return level, reasons


def main():
    if len(sys.argv) < 2 or not sys.argv[1].isdigit():
        sys.exit(__doc__)
    n = int(sys.argv[1])
    level, reasons = assess(n)
    if "--json" in sys.argv:
        print(json.dumps({"chapter": n, "risk": level, "reasons": reasons}, ensure_ascii=False))
    else:
        print(f"RISK ch {n}: {level}" + (" (" + "; ".join(reasons) + ")" if reasons else ""))


if __name__ == "__main__":
    main()
