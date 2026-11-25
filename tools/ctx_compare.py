#!/usr/bin/env python3
"""A/B comparison of the current delta pack and the incremental delta pack on the frozen golden fixture (0 tokens).

Usage: ctx_compare.py [--fixture tests/fixtures/golden5] [--json]
For chapters 23-27 it installs the story-memory snapshot that existed before each chapter, builds
  (A) the current pack:      context_pack.py --part delta [--no-tail]
  (B) the incremental pack:  context_pack.py --part delta --incremental [--batch-start] [--no-tail]
  (C) B plus retrieval:      ... --retrieve
and reports injected characters (MEASURED) and tokens (ESTIMATE = chars/4; no provider data exists here).
Lossless check: State, Debts and Secrets rebuilt from pack B (previous text + diff/unchanged stub) must equal pack A's sections exactly.
Retrieval check: tools/memory_retrieve.py must return the sources listed in expected_retrieval.json.
Exit code 1 if any check fails.
"""
import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
FIRST = 23
CHAPTERS = [23, 24, 25, 26, 27]
SECTIONS = ("State", "Debts (open promises)", "Secrets")


def run(root, script, *args):
    env = dict(os.environ, ANOGEN_ROOT=str(root))
    r = subprocess.run([sys.executable, str(TOOLS / script), *args], capture_output=True, text=True, env=env, cwd=root)
    return r.returncode, r.stdout, r.stderr


TOP = r"(?:Engine state|Precheck:|Idea inbox|Epigraph|Outline for|Pacing|Retrieved memory|State|Debts|Secrets|Last summaries|End of previous chapter|Premise|Characters)"


def sections(pack):
    """Split at the pack's own top-level titles only (State and Last summaries contain their own '## ' sub-headings)."""
    out = {}
    for m in re.finditer(r"(?ms)^## (" + TOP + r".*?)\n(.*?)(?=^## " + TOP + r"|\Z)", pack):
        out[m.group(1)] = m.group(2).rstrip("\n")
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--fixture", default=str(TOOLS.parent / "tests/fixtures/golden5"))
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    fx = Path(a.fixture)
    tmp = Path(tempfile.mkdtemp(prefix="anogen-ctx-"))
    root = tmp / "root"
    shutil.copytree(fx / "root", root)
    sys.path.insert(0, str(TOOLS))
    os.environ["ANOGEN_ROOT"] = str(root)
    import context_pack  # noqa: E402  (needs ANOGEN_ROOT set first)
    rows, problems, rebuilt_prev = [], [], {}
    try:
        for n in CHAPTERS:
            for name in ("state", "debts", "secrets"):
                shutil.copy(fx / "memory" / f"pack{n}" / f"{name}.md", root / "story/bible" / f"{name}.md")
            flags = ["--part", "delta", "--chapter", str(n)] + ([] if n == FIRST else ["--no-tail"])
            inc_flags = flags + ["--incremental"] + (["--batch-start"] if n == FIRST else [])
            rc_b, pack_b, err_b = run(root, "context_pack.py", *inc_flags)       # logs the variety draw, writes the cache
            rc_a, pack_a, err_a = run(root, "context_pack.py", *flags, "--peek")  # same draw (logged), no cache change
            rc_c, pack_c, err_c = run(root, "context_pack.py", *flags, "--peek", "--retrieve")
            for label, rc, err in (("A", rc_a, err_a), ("B", rc_b, err_b), ("C", rc_c, err_c)):
                if rc != 0:
                    problems.append(f"ch {n}: pack {label} failed rc={rc}: {err.strip()[-120:]}")
            sa, sb = sections(pack_a), sections(pack_b)
            for title in SECTIONS:
                key_b = next((k for k in sb if k.startswith(title)), None)
                if key_b is None or title not in sa:
                    problems.append(f"ch {n}: section {title} missing")
                    continue
                body = sb[key_b]
                prev = rebuilt_prev.get(title)
                if body.startswith("[unchanged"):
                    cur = prev
                elif "CHANGED since" in key_b:
                    cur = context_pack.apply_diff(prev, body + "\n").rstrip("\n")
                else:
                    cur = re.sub(r"\n\[\.\.\.TRUNCATED.*$", "", body, flags=re.S)
                rebuilt_prev[title] = cur
                if cur is None or cur.strip() != sa[title].strip():
                    problems.append(f"ch {n}: {title} NOT rebuilt exactly from the incremental pack")
            rows.append({"chapter": n, "full_chars": len(pack_a), "incremental_chars": len(pack_b),
                         "incremental_plus_retrieval_chars": len(pack_c),
                         "mode": "FULL (batch start)" if n == FIRST else "diff",
                         "sections": {t: ("unchanged" if sb.get(next((k for k in sb if k.startswith(t)), ""), "").startswith("[unchanged")
                                           else "diff" if any(k.startswith(t) and "CHANGED" in k for k in sb) else "full") for t in SECTIONS}})
        exp = json.loads((fx / "expected_retrieval.json").read_text())
        retrieval = {}
        for ch, wanted in exp.items():
            rc, out, err = run(root, "memory_retrieve.py", "--chapter", ch)
            got = set(re.findall(r"\[([^\]\s]+:\d+)\]", out))
            retrieval[ch] = {"wanted": wanted, "found": [w for w in wanted if w in got], "missing": [w for w in wanted if w not in got]}
            if retrieval[ch]["missing"]:
                problems.append(f"ch {ch}: retrieval missed {retrieval[ch]['missing']}")
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    tot_a = sum(r["full_chars"] for r in rows)
    tot_b = sum(r["incremental_chars"] for r in rows)
    later = [r for r in rows if r["chapter"] != FIRST]
    res = {"rows": rows, "total_full_chars": tot_a, "total_incremental_chars": tot_b,
           "later_chapters_saved_chars": sum(r["full_chars"] - r["incremental_chars"] for r in later),
           "retrieval": retrieval, "problems": problems}
    if a.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"{'ch':>3} {'A current':>10} {'B incremental':>14} {'C B+retrieval':>14} {'saved B':>9}  sections (state/debts/secrets)")
        for r in rows:
            print(f"{r['chapter']:>3} {r['full_chars']:>10} {r['incremental_chars']:>14} {r['incremental_plus_retrieval_chars']:>14} "
                  f"{r['full_chars'] - r['incremental_chars']:>9}  {'/'.join(r['sections'][t] for t in SECTIONS)}")
        print(f"total chars A={tot_a} B={tot_b} (MEASURED); saved over chapters 24-27: {res['later_chapters_saved_chars']} chars "
              f"= about {res['later_chapters_saved_chars'] // 4} tokens (ESTIMATE, chars/4; no provider measurement)")
        for ch, r in retrieval.items():
            print(f"retrieval ch {ch}: found {len(r['found'])}/{len(r['wanted'])}" + (f", MISSING {r['missing']}" if r["missing"] else ""))
        print("lossless rebuild of State/Debts/Secrets:", "OK" if not any("rebuilt" in p for p in problems) else "FAILED")
        for p in problems:
            print("PROBLEM:", p)
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
