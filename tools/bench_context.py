#!/usr/bin/env python3
"""Before/after context-size benchmark (0 tokens). Characters only: MEASURED. Tokens are chars/4 ESTIMATES.

Usage: bench_context.py [--ref COMMIT] [--chapters 26,31,36,41,46]
BEFORE = the tools of git commit REF (default: the backup commit 7815569) run on a temporary export of that commit.
AFTER  = the current tools on the current files. Both build the same packs for the same chapters:
  static (--extra combat-style), delta (--retrieve), and the follow-up delta (--incremental) is covered by ctx_compare.py.
It does NOT measure narrative quality, provider token usage, cost, or retrieval precision/recall (no labelled data).
"""
import argparse
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def pack(tools_dir, cwd, chapter, part):
    argv = [sys.executable, str(tools_dir / "context_pack.py"), "--chapter", str(chapter), "--part", part, "--peek"]
    if part == "static":
        argv += ["--extra", "combat-style"]
    else:
        argv += ["--retrieve"]
    r = subprocess.run(argv, capture_output=True, text=True, cwd=cwd)
    return len(r.stdout), r.returncode


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="7815569")
    ap.add_argument("--chapters", default="26,31,36,41,46")
    a = ap.parse_args()
    chs = [int(x) for x in a.chapters.split(",")]
    with tempfile.TemporaryDirectory(prefix="anogen-bench-") as d:
        arch = subprocess.run(["git", "archive", a.ref], capture_output=True, cwd=REPO)
        if arch.returncode:
            sys.exit(f"git archive failed: {arch.stderr.decode()[:200]}")
        subprocess.run(["tar", "-x", "-C", d], input=arch.stdout, check=True)
        old = Path(d)
        print(f"| chapter | part | BEFORE chars ({a.ref}) | AFTER chars (now) | change |\n|---|---|---:|---:|---:|")
        tot_b = tot_a = 0
        for n in chs:
            for part in ("static", "delta"):
                b, rb = pack(old / "tools", old, n, part)
                af, ra = pack(REPO / "tools", REPO, n, part)
                tot_b += b; tot_a += af
                note = "" if rb == 0 and ra == 0 else f" (exit {rb}/{ra})"
                print(f"| {n} | {part} | {b} | {af} | {af - b:+d} ({(af - b) / max(b, 1) * 100:+.1f}%){note} |")
        print(f"| total | | {tot_b} | {tot_a} | {tot_a - tot_b:+d} ({(tot_a - tot_b) / max(tot_b, 1) * 100:+.1f}%) |")
        print(f"\nAbout {tot_b // 4} -> {tot_a // 4} tokens over these packs (ESTIMATE chars/4; no provider data).")


if __name__ == "__main__":
    main()
