#!/usr/bin/env python3
"""START HERE for any AI: one command that says where the project stands and what to do next (0 tokens, read-only).

Usage: python3 tools/start.py
It runs: novel status, lock status, engine_state next, validate, debts. It writes nothing.
Then read AGENTS.md section "Start here" and follow the NEXT line printed at the end.
"""
import json
import re
import subprocess
import sys
from pathlib import Path

T = Path(__file__).resolve().parent
sys.path.insert(0, str(T))
REPO = T.parent


def run(*args):
    r = subprocess.run([sys.executable, str(T / args[0]), *args[1:]], capture_output=True, text=True, cwd=REPO)
    return r.returncode, (r.stdout + r.stderr).strip()


def main():
    print("== ANOGEN START ==")
    git = subprocess.run(["git", "status", "-sb"], capture_output=True, text=True, cwd=REPO).stdout.splitlines()
    print("git:", git[0] if git else "?", f"({len(git) - 1} changed files)" if len(git) > 1 else "(clean)")
    rc, out = run("novel.py", "status")
    print("novel:", out.splitlines()[0] if out else "(none)")
    rc, out = run("lock.py", "status")
    print("lock:", out.splitlines()[0] if out else "?")
    rc, out = run("engine_state.py", "next", "--no-apply")
    try:
        nx = json.loads(out[out.index("{"):])
    except Exception:
        nx = {}
        print("engine_state next FAILED:", out[-300:])
    hold = nx.get("hold")
    try:
        from common import OPS
        blocked = (OPS / "blocked.md").read_text(encoding="utf-8", errors="replace")
        first = next((ln for ln in blocked.splitlines() if ln.startswith("## ")), "")
        if re.match(r"##\s*HOLD\b", first) and "resolved" not in first.lower():
            hold = True
    except Exception:
        pass
    print("hold:", "YES - write nothing; only the owner clears it (see AGENTS.md)" if hold else "no")
    for k in ("next_chapter", "writer_range", "critic_pending", "critic_changed_after_review", "reason"):
        if k in nx:
            print(f"{k}: {nx[k]}")
    rc, out = run("validate.py", "1-%d" % max(1, (nx.get("next_chapter") or 2) - 1))
    last = [ln for ln in out.splitlines() if ln.startswith("VALIDATION")]
    print(last[-1] if last else "validate: no summary: " + out[-200:])
    errs = [ln for ln in out.splitlines() if ln.startswith("ERROR")]
    for ln in errs[:8]:
        print("  ", ln[:200])
    rc, out = run("debts.py")
    print(out.splitlines()[-1] if out else "debts: ?")
    try:
        from common import OPS
        rp = (OPS / "reading-page.txt").read_text(encoding="utf-8").strip()
        print("reading page URL:", rp or "NOT RECORDED (AGENTS.md step 5: build, publish, record in ops/reading-page.txt)")
    except Exception:
        print("reading page URL: NOT RECORDED (AGENTS.md step 5: build, publish, record in ops/reading-page.txt)")
    print()
    if hold:
        print("NEXT: HOLD is active. Write nothing. Tell the owner the hold reason in 3 lines.")
    elif errs:
        print("NEXT: fix the ERROR lines above first (they are rule breaks, not opinions), then run this again.")
    elif nx.get("critic_changed_after_review"):
        print("NEXT: re-review the changed chapters (AGENTS.md step 3), then `engine_state.py rereview ...`.")
    elif nx.get("critic_pending"):
        print("NEXT: run the critic stage on critic_pending before writing more.")
    elif nx.get("writer_range") and nx.get("continue"):
        print("NEXT: write chapters", nx["writer_range"], "(Production flow, AGENTS.md). Minimum 2000 words each.")
    else:
        print('NEXT: no batch is running. Do nothing until the owner gives a writing order ("kerjakan N bab", "tulis bab berikutnya", ...). Never start writing on your own.')


if __name__ == "__main__":
    import signal
    try:
        signal.signal(signal.SIGPIPE, signal.SIG_DFL)  # quiet exit when piped to head
    except (AttributeError, ValueError):
        pass
    main()
