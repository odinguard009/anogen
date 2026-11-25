#!/usr/bin/env python3
"""Before/after context-size benchmark (0 tokens). Characters only: MEASURED. Tokens are chars/4 ESTIMATES.

Usage: bench_context.py [--ref COMMIT] [--chapters 26,31,36,41,46] [--quiet] [--review N --review-ref COMMIT]
BEFORE = the tools of git commit REF (default 7815569, before PR #7) run on an export of that commit; AFTER = the current tools.
Both build the same packs for the same chapters: static (BEFORE: --extra combat-style, AFTER: --extra "combat-style?"),
delta (--retrieve), on the real files of the active novel.
--quiet     the same comparison on a COPY of the novel whose outline lines for the sampled chapters are replaced by plain
            non-fight lines (SYNTHETIC: it shows what the conditional parts save on quiet chapters, not a real chapter).
--review N  compares the self-review pack of written chapter N: REVIEW-REF's tool (default d5813e8, PR #7) vs now at each risk level.
It does NOT measure narrative quality, provider token usage, cost, or retrieval quality.
"""
import argparse
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent


def export(ref, d):
    arch = subprocess.run(["git", "archive", ref], capture_output=True, cwd=REPO)
    if arch.returncode:
        sys.exit(f"git archive {ref} failed: {arch.stderr.decode()[:200]}")
    subprocess.run(["tar", "-x", "-C", str(d)], input=arch.stdout, check=True)


def run(tools_dir, cwd, argv, env=None):
    e = dict(os.environ, **(env or {}))
    r = subprocess.run([sys.executable, str(tools_dir / argv[0]), *argv[1:]], capture_output=True, text=True, cwd=cwd, env=e)
    return r.stdout, r.returncode


def pack(tools_dir, cwd, chapter, part, extra, env=None):
    argv = ["context_pack.py", "--chapter", str(chapter), "--part", part, "--peek"]
    argv += ["--extra", extra] if part == "static" else ["--retrieve"]
    out, rc = run(tools_dir, cwd, argv, env)
    return len(out), rc


def table(old_tools, old_cwd, new_tools, new_cwd, chs, ref, env_old=None, env_new=None):
    print(f"| chapter | part | BEFORE chars ({ref}) | AFTER chars (now) | change |\n|---|---|---:|---:|---:|")
    tb = ta = 0
    for n in chs:
        for part in ("static", "delta"):
            b, rb = pack(old_tools, old_cwd, n, part, "combat-style", env_old)
            a, ra = pack(new_tools, new_cwd, n, part, "combat-style?", env_new)
            tb += b; ta += a
            note = "" if rb == 0 and ra == 0 else f" (exit {rb}/{ra})"
            print(f"| {n} | {part} | {b} | {a} | {a - b:+d} ({(a - b) / max(b, 1) * 100:+.1f}%){note} |")
    print(f"| total | | {tb} | {ta} | {ta - tb:+d} ({(ta - tb) / max(tb, 1) * 100:+.1f}%) |")
    print(f"\nAbout {tb // 4} -> {ta // 4} tokens over these packs (ESTIMATE chars/4; no provider data).")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ref", default="7815569")
    ap.add_argument("--chapters", default="26,31,36,41,46")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--review", type=int)
    ap.add_argument("--review-ref", default="d5813e8")
    a = ap.parse_args()
    chs = [int(x) for x in a.chapters.split(",")]
    with tempfile.TemporaryDirectory(prefix="anogen-bench-") as d:
        d = Path(d)
        if a.review:
            old = d / "old"; old.mkdir(); export(a.review_ref, old)
            b, _ = run(old / "tools", old, ["review_pack.py", str(a.review)])
            print(f"Self-review pack, chapter {a.review} (same files; BEFORE = {a.review_ref}):")
            print(f"| version | risk level | chars |\n|---|---|---:|\n| BEFORE (PR #7: always the full chapter) | any | {len(b)} |")
            for lv in ("LOW", "MEDIUM", "HIGH"):
                o, _ = run(REPO / "tools", REPO, ["review_pack.py", str(a.review), "--level", lv])
                print(f"| AFTER | {lv} | {len(o)} ({(len(o) - len(b)) / len(b) * 100:+.1f}%) |")
            return
        old = d / "old"; old.mkdir(); export(a.ref, old)
        if not a.quiet:
            table(old / "tools", old, REPO / "tools", REPO, chs, a.ref)
            return
        # SYNTHETIC quiet fixture: a flat-layout copy of the active novel with plain outline lines for the sampled chapters
        act = (REPO / "novels" / "ACTIVE").read_text().strip()
        src = REPO / "novels" / act
        root = d / "quiet"; root.mkdir()
        for sub in ("story", "chapters", "ops"):
            shutil.copytree(src / sub, root / sub, ignore=shutil.ignore_patterns("ctx-cache.json", "memory.sqlite*", "*.bak"))
        covered = {m for n in chs for m in range(n, n + 5)}
        for f in (root / "story" / "outline").glob("arc-*.md"):
            lines = f.read_text(encoding="utf-8").splitlines()
            for i, ln in enumerate(lines):
                m = re.match(r"^\s*(?:[-*]\s*)?(?:\*\*)?Ch\.?\s*(\d+)\b", ln)
                if m and int(m.group(1)) in covered:
                    lines[i] = f"- Ch {m.group(1)} | goal: the friends eat soup and talk about the garden | conflict: a small quarrel about chores | payoff: they laugh | hook: a letter arrives"
            f.write_text("\n".join(lines) + "\n", encoding="utf-8")
        env = {"ANOGEN_ROOT": str(root)}
        print("SYNTHETIC quiet fixture (outline lines replaced by non-fight lines):")
        table(old / "tools", root, REPO / "tools", root, chs, a.ref, env, env)


if __name__ == "__main__":
    main()
