#!/usr/bin/env python3
"""Python-first validation report for a chapter range (0 tokens, standard library only).

Usage: validate.py [A-B] [--json] [--write]
Default range: every written chapter. Levels: ERROR (certain technical problem), WARNING (possible inconsistency, a human
decides), INFO (facts for the audit). It never edits canon or chapters. Exit code 1 only when there is an ERROR.
Covers: file integrity (exists, not empty, complete ending, heading, word range, summary, outline, scores row), structure
(JSON files parse, chapter numbering has no gaps or duplicates, no duplicate summaries or score rows), story data (open debts
with no due chapter or overdue, capitalized names in the chapters that are not in canon_names.txt), git state, backup state,
and context-cache integrity. Not covered (needs structured story data, see docs/STORY_MEMORY_ENGINE.md): character status
changes without an event, timeline contradictions.
"""
import csv
import json
import re
import subprocess
import sys
from collections import Counter

from common import OPS, ROOT, REPO, STORY, canon_tokens, chapter_files, chapter_path, read, setting_int, word_count, load_json
import verify_batch

JSON_FILES = ["engine.json", "schedule.json", "variety_log.json", "ctx-cache.json"]
COMMON_CAPS = set("""Monday Tuesday Wednesday Thursday Friday Saturday Sunday January February March April May June July August
September October November December I I'm I'll I've I'd Mr Mrs Sir Lady Lord Duke Count Archduke Captain Master Mother Father
One Two Three Four Five Six Seven Eight Nine Ten Eleven Twelve Chapter Bell Bells Door Gate Raiment Aura Mana Tenet Unbind Unbound Hush Husk Veil Stalker Choir""".split())


def chapter_numbers():
    return [n for n, _ in chapter_files()]


def check(lo, hi):
    R = []  # (level, where, message)

    def add(level, where, msg):
        R.append((level, where, msg))

    nums = chapter_numbers()
    if len(nums) != len(set(nums)):
        add("ERROR", "chapters", "duplicate chapter numbers")
    if nums:
        gaps = sorted(set(range(nums[0], nums[-1] + 1)) - set(nums))
        if gaps:
            add("ERROR", "chapters", f"gap in numbering: missing {gaps[:10]}")
    for name in JSON_FILES:
        p = OPS / name
        if p.exists():
            try:
                json.loads(p.read_text(encoding="utf-8"))
            except (ValueError, OSError) as e:
                add("ERROR", f"ops/{name}", f"invalid JSON: {e}")
    summ = read(STORY / "bible" / "summaries.md") + verify_batch._archived_summaries()
    ids = Counter(int(m.group(1)) for m in re.finditer(r"(?m)^#{1,3}\s*Ch\.?\s*(\d+)", summ))
    for k, v in ids.items():
        if v > 1:
            add("ERROR", "summaries", f"chapter {k} has {v} summaries")
    rows = [r[0] for r in csv.reader(read(OPS / "scores.csv").splitlines()) if r and r[0].isdigit()]
    for k, v in Counter(rows).items():
        if v > 1:
            add("ERROR", "scores.csv", f"chapter {k} has {v} score rows")

    git_ok = verify_batch.git_state()
    problems = 0
    checked = 0
    texts = {}
    for n in range(lo, hi + 1):
        p = chapter_path(n)
        if not p.exists():
            add("ERROR", f"ch {n}", "file missing")
            continue
        checked += 1
        raw = read(p)
        texts[n] = raw
        if not raw.strip():
            add("ERROR", f"ch {n}", "file is empty")
            continue
        end = raw.rstrip()[-1]
        if end not in ".!?\"'”’*)":
            add("ERROR", f"ch {n}", f"possibly truncated: last character is {end!r}")
        for pr in verify_batch.problems_for(n, git_ok):
            problems += 1
            add("ERROR", f"ch {n}", pr.split(": ", 1)[-1] if pr.startswith(f"ch {n}: ") else pr)

    # story data
    nxt = (nums[-1] + 1) if nums else 1
    # outline vs text: every **[Label]** the outline promises for chapter N must appear in chapter N
    # (write "not used yet" right after a label in the outline when the chapter must NOT use it)
    for om in re.finditer(r"^Ch (\d+) \|(.*)$", "\n".join(read(f) for f in sorted((STORY / "outline").glob("arc-*.md"))), re.M):
        cn = int(om.group(1))
        if cn not in texts:
            continue
        for lm in re.finditer(r"\*\*\[([^\]]+)\]\*\*", om.group(2)):
            if f"[{lm.group(1)}]" not in texts[cn] and "not used" not in om.group(2)[lm.end():lm.end() + 25]:
                add("ERROR", f"ch {cn}", f"outline promises **[{lm.group(1)}]** in this chapter but the text never uses it (fix the chapter or edit the outline)")
    import debts
    d_err, d_warn = debts.check(nxt)
    for i, msg in d_err:
        add("ERROR", f"debts.md:{i}", msg)
    for i, msg in d_warn:
        add("WARNING", f"debts.md:{i}", msg)
    known = canon_tokens()
    seen = Counter()
    for n, raw in texts.items():
        body = raw.split("\n", 1)[-1]
        for m in re.finditer(r"(?<=[a-z,;] )([A-Z][a-z]{2,})\b", body):
            w = m.group(1)
            if w.lower() not in known and w not in COMMON_CAPS:
                seen[w] += 1
    for w, c in seen.most_common(12):
        if c >= 3:
            add("WARNING", "names", f"'{w}' appears {c} times in ch {lo}-{hi} but is not in canon_names.txt")

    # git / backup / context integrity
    add("INFO", "git", "work tree OK" if git_ok[0] else f"git problem: {git_ok[1]}")
    try:
        r = subprocess.run(["git", "branch", "-r", "--list", "origin/backup/*"], capture_output=True, text=True, cwd=REPO)
        bk = [x.strip() for x in r.stdout.splitlines()]
        add("INFO", "backup", f"remote backup branches: {', '.join(bk)}" if bk else "no remote backup branch known locally (git fetch may be needed)")
    except OSError as e:
        add("WARNING", "backup", f"cannot check backups: {e}")
    cache = OPS / "ctx-cache.json"
    if cache.exists():
        try:
            c = json.loads(cache.read_text(encoding="utf-8"))
            import context_pack
            add("INFO" if c.get("static_hash") == context_pack.static_hash() else "WARNING", "context",
                "context cache matches static sources" if c.get("static_hash") == context_pack.static_hash()
                else "context cache is stale (static sources changed); the next pack falls back to FULL")
        except (ValueError, OSError):
            add("ERROR", "context", "ctx-cache.json unreadable")
    else:
        add("INFO", "context", "no context cache (normal outside a batch)")
    return R, checked


def main():
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    nums = chapter_numbers()
    lo, hi = (nums[0], nums[-1]) if nums else (1, 0)
    if args:
        m = re.match(r"^(\d+)(?:-(\d+))?$", args[0])
        if not m:
            sys.exit(__doc__)
        lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
    R, checked = check(lo, hi)
    cnt = Counter(l for l, _, _ in R)
    summary = {"range": f"{lo}-{hi}", "chapters_checked": checked, "errors": cnt["ERROR"], "warnings": cnt["WARNING"], "info": cnt["INFO"]}
    if "--json" in sys.argv:
        print(json.dumps({"summary": summary, "items": [{"level": l, "where": w, "message": m} for l, w, m in R]}, ensure_ascii=False, indent=1))
    else:
        for l, w, m in R:
            print(f"{l}: {w}: {m}")
        print(f"VALIDATION {summary['range']}: {checked} chapters, {cnt['ERROR']} error(s), {cnt['WARNING']} warning(s), {cnt['INFO']} info")
    if "--write" in sys.argv:
        (OPS / "validation-report.json").write_text(json.dumps({"summary": summary, "items": R}, ensure_ascii=False, indent=1), encoding="utf-8")
    sys.exit(1 if cnt["ERROR"] else 0)


if __name__ == "__main__":
    main()
