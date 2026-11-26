#!/usr/bin/env python3
"""End-to-end test of every tool using a temporary root and synthetic filler text.
Run: python3 tools/test_tools.py   (prints ALL TESTS PASSED on success)
Does not touch the real story or chapters.
"""
import json
import os
import random
import shutil
import subprocess
import sys
import tempfile
import zipfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent


def _src():
    """Folder holding the real story files the tests copy (the active novel, or the repo itself in the flat layout)."""
    act = TOOLS.parent / "novels" / "ACTIVE"
    return TOOLS.parent / "novels" / act.read_text().strip() if act.exists() else TOOLS.parent


SRC = _src()
PY = sys.executable
FAILS = []


def run(root, script, *args, stdin=None):
    env = dict(os.environ, ANOGEN_ROOT=str(root))
    r = subprocess.run([PY, str(TOOLS / script), *args], capture_output=True, text=True,
                       env=env, input=stdin, cwd=root)
    return r.returncode, r.stdout + r.stderr


def check(name, cond, detail=""):
    print(("PASS " if cond else "FAIL ") + name + ("" if cond else f"  -> {detail[:300]}"))
    if not cond:
        FAILS.append(name)


VOCAB = ("river stone lantern copper winter orchard harbor ledger falcon marsh timber glass ember ridge "
         "thunder candle mirror anchor saddle canyon whisper cinder meadow bridge compass hammer velvet "
         "lantern forge tide bramble quarry signal weaver shadow granite harvest pilgrim furnace").split()
VERBS = "carried broke followed measured crossed lifted buried painted counted traded opened".split()


def filler(rng, words, names):
    out, count = [], 0
    while count < words:
        n = rng.randint(8, 16)
        s = [rng.choice(VOCAB) for _ in range(n)]
        s[1] = rng.choice(VERBS)
        if rng.random() < 0.3:
            s[2] = rng.choice(names)
        sent = " ".join(s).capitalize() + "."
        out.append(sent)
        count += n
    paras = []
    i = 0
    while i < len(out):
        k = rng.randint(2, 5)
        paras.append(" ".join(out[i:i + k]))
        i += k
    mid = len(paras) // 2
    paras.insert(mid, "* * *")
    return "\n\n".join(paras)


def write(p, t):
    p = Path(p)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(t, encoding="utf-8")


def git(root, *args):
    return subprocess.run(["git", *args], cwd=root, capture_output=True, text=True)


def mkroot(chapters=(), engine=None):
    root = Path(tempfile.mkdtemp(prefix="anogen-test2-"))
    for d in ("story/bible", "story/outline", "story/style", "chapters", "ops", "out"):
        (root / d).mkdir(parents=True)
    shutil.copy(SRC / "story/brief.md", root / "story/brief.md")
    shutil.copy(SRC / "story/style/banned.md", root / "story/style/banned.md")
    shutil.copy(SRC / "story/style/profile.md", root / "story/style/profile.md")
    write(root / "story/inbox.md", "# Idea inbox\n\n## Unprocessed\n\n## Processed\n")
    write(root / "story/bible/canon_names.txt", "Alvar\nBrenna\n")
    write(root / "story/bible/summaries.md", "# S\n")
    write(root / "ops/engine.json", json.dumps(engine or {"arcs": {}}))
    rng = random.Random(3)
    for n in chapters:
        write(root / f"chapters/chapter-{n:03d}.md", f"# Chapter {n}: Test Title\n\n" + filler(rng, 2000, ["Alvar", "Brenna"]) + "\n")
    return root


ARC_RUNNING = {"arcs": {"1": {"start": 1, "end": 50, "name": "A", "max": 50, "status": "writing"}},
               "batch": {"mode": "arc", "target": 0, "arc": 1, "max": 50, "start_chapter": 1,
                         "status": "running", "stop_reason": ""}}


def phase_two_tests():
    # P0-1: context pack never cuts silently; the full style profile reaches the writer
    root = mkroot()
    try:
        c, o = run(root, "context_pack.py", "--part", "static", "--peek")
        check("pack keeps Human feel, Eden flat and the dialogue model", c == 0 and "HUMAN FEEL" in o and "EDEN IS FLAT" in o and "DIALOGUE MODEL" in o and "TRUNCATED" not in o, o[-300:])
        write(root / "story/style/profile.md", "# P\n\n## A\n" + "word " * 5000)
        c, o = run(root, "context_pack.py", "--part", "static", "--peek")
        check("pack truncation exits 4 and names the section", c == 4 and "PACK WARNING" in o and "Style profile" in o, o[-300:])
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # P0-2: gap fill never plans over existing chapters
    root = mkroot([1, 2, 3, 4, 6, 7, 8, 9], ARC_RUNNING)
    try:
        c, o = run(root, "engine_state.py", "next", "--no-apply")
        d = json.loads(o)
        check("gap: writer_range clamped before existing chapter", d["next_chapter"] == 5 and d["writer_range"] == [5, 5] and "gap" in d["gap_note"], o)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # P0-3: critic once per 10, reviewed hashes, validated marks, audit alignment
    root = mkroot(range(1, 6), ARC_RUNNING)
    try:
        d = json.loads(run(root, "engine_state.py", "next", "--no-apply")[1])
        check("critic waits until 10 chapters are ready", d["critic_pending"] is None and d["critic_waiting"] == [1, 5], str(d))
        for n in range(6, 11):
            write(root / f"chapters/chapter-{n:03d}.md", f"# Chapter {n}: Test Title\n\n" + filler(random.Random(n), 2000, ["Alvar"]) + "\n")
        d = json.loads(run(root, "engine_state.py", "next", "--no-apply")[1])
        check("critic due at 10 with audit", d["critic_pending"] == [1, 10] and d["audit_with_critic"] is True, str(d))
        c, o = run(root, "engine_state.py", "mark", "critic", "11")
        check("mark refuses beyond highest chapter", c != 0 and "highest chapter" in o, o)
        c, o = run(root, "engine_state.py", "mark", "critic", "10")
        check("mark critic 10", c == 0, o)
        c, o = run(root, "engine_state.py", "mark", "critic", "4")
        check("mark never goes backwards", c != 0, o)
        c, o = run(root, "engine_state.py", "mark", "audit", "10")
        check("mark audit 10", c == 0, o)
        pf = root / "chapters/chapter-003.md"
        pf.write_text(pf.read_text() + "\nA late edit after review.\n")
        d = json.loads(run(root, "engine_state.py", "next", "--no-apply")[1])
        check("edited chapter returns after review", d["critic_changed_after_review"] == [3], str(d))
        c, o = run(root, "engine_state.py", "rereview", "3")
        d = json.loads(run(root, "engine_state.py", "next", "--no-apply")[1])
        check("rereview clears the change", c == 0 and d["critic_changed_after_review"] == [], str(d))
        check("engine.json backup kept", (root / "ops/engine.json.bak").exists())
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # interrupted batch (chapters stop at 28): critic still ends on 30, so the audit rides along
    root = mkroot(range(1, 39), dict(ARC_RUNNING, critic_through=28, audit_through=20))
    try:
        d = json.loads(run(root, "engine_state.py", "next", "--no-apply")[1])
        check("after interruption critic range ends on a multiple of 10 and audit rides along",
              d["critic_pending"] == [29, 30] and d["audit_with_critic"] is True, str(d))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # A1/A2: explicit per-chapter re-review; changed chapters block writing and are scheduled
    root = mkroot(range(1, 11), dict(ARC_RUNNING))
    try:
        run(root, "engine_state.py", "mark", "critic", "10")
        for k in (3, 7):
            pf = root / f"chapters/chapter-{k:03d}.md"
            pf.write_text(pf.read_text() + "\nEdited after review.\n")
        d = json.loads(run(root, "engine_state.py", "next", "--no-apply")[1])
        check("changed chapters 3 and 7 detected, writing blocked, no full critic job",
              d["critic_changed_after_review"] == [3, 7] and d["rereview_pending"] == [3, 7]
              and d["writer_range"] is None and d["critic_pending"] is None, str(d))
        c, o = run(root, "engine_state.py", "rereview", "3")
        d = json.loads(run(root, "engine_state.py", "next", "--no-apply")[1])
        check("re-review of chapter 3 only clears 3, chapter 7 stays pending",
              c == 0 and d["critic_changed_after_review"] == [7] and d["writer_range"] is None, str(d))
        c, o = run(root, "engine_state.py", "rereview", "99")
        check("rereview refuses a missing chapter file", c != 0 and "missing" in o, o)
        c, o = run(root, "engine_state.py", "rereview", "7")
        d = json.loads(run(root, "engine_state.py", "next", "--no-apply")[1])
        check("after all re-reviews writing resumes", c == 0 and d["rereview_pending"] == [] and d["writer_range"] == [11, 15], str(d))
        c, o = run(root, "engine_state.py", "mark", "critic", "10", "--rereview")
        check("old --rereview flag is gone", c != 0, o)
        # interruption and resume: state is derived from hashes, so a fresh process sees the same pending list
        pf = root / "chapters/chapter-005.md"
        pf.write_text(pf.read_text() + "\nEdit again.\n")
        d1 = json.loads(run(root, "engine_state.py", "next", "--no-apply")[1])
        d2 = json.loads(run(root, "engine_state.py", "next")[1])
        d3 = json.loads(run(root, "engine_state.py", "next", "--no-apply")[1])
        check("re-review pending survives interruption and resume", d1["rereview_pending"] == d2["rereview_pending"] == d3["rereview_pending"] == [5], str(d3))
        # HOLD (owner order): nothing may be planned, started or resumed while it is set
        c, o = run(root, "engine_state.py", "hold", "set", "--reason", "owner wait")
        check("hold set", c == 0, o)
        d = json.loads(run(root, "engine_state.py", "next", "--no-apply")[1])
        check("hold: next returns no writer range, no critic, continue false", d["writer_range"] is None and d["critic_pending"] is None and d["continue"] is False and d.get("hold") is True, str(d))
        c, o = run(root, "engine_state.py", "batch-resume")
        check("hold: batch-resume refused", c != 0 and "HOLD" in o, o)
        c, o = run(root, "engine_state.py", "batch-start", "--mode", "n", "--target", "3")
        check("hold: batch-start refused", c != 0 and "HOLD" in o, o)
        c, o = run(root, "engine_state.py", "hold", "clear")
        d = json.loads(run(root, "engine_state.py", "next", "--no-apply")[1])
        check("hold cleared: planning works again", c == 0 and d.get("hold") is None, str(d))
        # reset-draft: one deterministic step when the owner orders a full rewrite
        run(root, "engine_state.py", "hold", "set", "--reason", "wait")
        c, o = run(root, "engine_state.py", "reset-draft", "--confirm")
        check("reset-draft refused while HOLD is set", c != 0 and "HOLD" in o, o)
        run(root, "engine_state.py", "hold", "clear")
        c, o = run(root, "engine_state.py", "reset-draft")
        check("reset-draft needs --confirm", c != 0 and "--confirm" in o, o)
        c, o = run(root, "engine_state.py", "reset-draft", "--confirm", "--date", "2000-01-01")
        d = json.loads(run(root, "engine_state.py", "next", "--no-apply")[1])
        check("reset-draft archives chapters and resets review state", c == 0 and not list((root / "chapters").glob("chapter-*.md")) and (root / "archive/superseded-2000-01-01/chapters/chapter-001.md").exists() and d["next_chapter"] == 1 and d["critic_pending"] is None, o + str(d))
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # A3: verify_batch never passes on subprocess or git failures
    root = mkroot([1])
    try:
        write(root / "story/outline/arc-1.md", "Ch 1 | goal: a | conflict: b | payoff: c | hook: d | pov: first | type: quiet\n")
        write(root / "story/bible/summaries.md", "# S\n\n## Ch 1 - One\nx\n")
        write(root / "ops/scores.csv", "chapter,t,s,e,b,v,f\n1,3,3,3,-,3,3\n")
        c, o = run(root, "verify_batch.py", "1")
        check("verify_batch without a git repo fails and names the cause", c == 1 and "not a git work tree" in o, o)
        subprocess.run(["git", "init", "-q"], cwd=root)
        git(root, "config", "user.email", "t@t"); git(root, "config", "user.name", "t")
        c, o = run(root, "verify_batch.py", "1")
        check("verify_batch flags an untracked chapter", c == 1 and ("not committed" in o or "not tracked" in o), o)
        git(root, "add", "-A"); git(root, "commit", "-q", "-m", "x")
        c, o = run(root, "verify_batch.py", "1")
        issues = [ln for ln in o.splitlines() if "ISSUE" in ln or "words outside" in ln]
        check("verify_batch sees committed chapter (only checker findings remain)", "not committed" not in o and "not a git" not in o, o)
        # git missing from PATH
        env = dict(os.environ, ANOGEN_ROOT=str(root), PATH="/nonexistent")
        r = subprocess.run([PY, str(TOOLS / "verify_batch.py"), "1"], capture_output=True, text=True, env=env, cwd=root)
        check("verify_batch with git missing fails", r.returncode == 1 and ("cannot run git" in r.stdout + r.stderr or "git unavailable" in r.stdout), r.stdout + r.stderr)
        # checker crash: replace check_chapter by a crashing stub in a copy of the tools
        stub = Path(tempfile.mkdtemp(prefix="anogen-stub-"))
        try:
            shutil.copytree(TOOLS, stub / "tools", ignore=shutil.ignore_patterns("__pycache__"))
            (stub / "tools/check_chapter.py").write_text("import sys\nsys.exit(2)\n")
            env = dict(os.environ, ANOGEN_ROOT=str(root))
            r = subprocess.run([PY, str(stub / "tools/verify_batch.py"), "1"], capture_output=True, text=True, env=env, cwd=root)
            check("verify_batch fails when the checker crashes", r.returncode == 1 and "checker crashed" in r.stdout, r.stdout + r.stderr)
        finally:
            shutil.rmtree(stub, ignore_errors=True)
        # undecodable chapter file: verification fails with a cause instead of a traceback
        (root / "chapters/chapter-001.md").write_bytes(b"# T\n\xff\xfe bad bytes\n")
        c, o = run(root, "verify_batch.py", "1")
        check("verify_batch reports a crash as a problem", c == 1 and "PROBLEM" in o and "Traceback" not in o, o)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # P0-4: atomic write and lock owner check
    root = mkroot()
    try:
        code = ("import common; common.write(common.OPS/'x.txt','one'); common.write(common.OPS/'x.txt','two',backup=True);"
                "import os; print(sorted(os.listdir(common.OPS)))")
        r = subprocess.run([PY, "-c", code], capture_output=True, text=True, cwd=TOOLS, env=dict(os.environ, ANOGEN_ROOT=str(root)))
        check("atomic write leaves no temp file and keeps .bak", "x.txt.bak" in r.stdout and ".tmp" not in r.stdout and (root / "ops/x.txt").read_text() == "two", r.stdout + r.stderr)
        run(root, "lock.py", "acquire", "w", "--owner", "a")
        c, o = run(root, "lock.py", "release", "w", "--owner", "b")
        check("lock release by non-owner refused", c == 3 and "REFUSED" in o, o)
        c, o = run(root, "lock.py", "release", "w", "--owner", "a")
        check("lock release by owner", c == 0, o)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # P0-5: save merges on a rejected push and never stages stray files
    base = Path(tempfile.mkdtemp(prefix="anogen-remote-"))
    try:
        subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(base / "remote.git")])
        a, b = base / "a", base / "b"
        for d in (a, b):
            d.mkdir()
            git(d, "init", "-q", "-b", "main")
            git(d, "config", "user.email", "t@t")
            git(d, "config", "user.name", "t")
            git(d, "remote", "add", "origin", str(base / "remote.git"))
            (d / "story").mkdir()
        (a / "story/a.md").write_text("a")
        c, o = run(a, "save.py", "first")
        check("save pushes to remote", c == 0 and "Pushed" in o, o)
        git(b, "pull", "-q", "origin", "main")
        (b / "story/b.md").write_text("b")
        c, o = run(b, "save.py", "from b")
        (a / "story/a2.md").write_text("a2")
        (a / "stray.txt").write_text("must not be committed")
        c, o = run(a, "save.py", "second from a (remote is ahead)")
        check("save merges a rejected push", c == 0 and "Pushed" in o, o)
        git(a, "remote", "set-url", "origin", str(base / "missing.git"))
        (a / "story/a3.md").write_text("a3")
        c, o = run(a, "save.py", "push will fail")
        check("failed push reported, work committed locally", c == 3 and "PUSH FAILED" in o, o)
        git(a, "remote", "set-url", "origin", str(base / "remote.git"))
        c, o = run(a, "save.py", "no new changes")
        check("save retries an earlier failed push", c == 0 and "Pushed" in o and "not pushed yet" in o, o)
        tracked = git(a, "ls-files").stdout
        check("save does not stage stray files", "stray.txt" not in tracked and "story/b.md" in tracked, tracked + o)
    finally:
        shutil.rmtree(base, ignore_errors=True)

    # P0-6: verify_batch go/no-go, check_chapter --strict
    root = mkroot([1])
    try:
        write(root / "story/outline/arc-1.md", "Ch 1 | goal: a | conflict: b | payoff: c | hook: d | pov: first | type: quiet\n")
        c, o = run(root, "verify_batch.py", "1-2")
        check("verify_batch flags missing chapter, summary, scores", c == 1 and "ch 2: file missing" in o and "no summary" in o and "scores.csv" in o, o)
        c, o = run(root, "check_chapter.py", "chapters/chapter-001.md", "--strict")
        check("dialogue below 25% is a warning only, not an issue", "WARNING dialogue share" in o and "below 25%" not in o.split("ISSUE")[-1] if "ISSUE" in o else "WARNING dialogue share" in o, o)
        (root / "chapters/chapter-001.md").write_text("# Chapter 1: T\n\nShort.\n", encoding="utf-8")
        c, o = run(root, "check_chapter.py", "chapters/chapter-001.md", "--strict")
        check("check_chapter --strict exits 1 on issues", c == 1 and "ISSUE" in o, o)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # P1-1 usage log and idempotent log_run
    root = mkroot([1, 2])
    try:
        c, o = run(root, "usage_log.py", "report")
        check("usage report with no data says UNMEASURED", "UNMEASURED" in o, o)
        run(root, "usage_log.py", "add", "--role", "writer", "--model", "m", "--range", "1-2", "--input", "1000", "--output", "500", "--seconds", "60", "--source", "reported")
        run(root, "usage_log.py", "add", "--role", "critic", "--model", "m", "--range", "1-2", "--input", "800", "--output", "100", "--outcome", "retry")
        run(root, "usage_log.py", "add", "--role", "writer", "--model", "m", "--range", "3", "--input", "999", "--output", "1", "--source", "estimate")
        run(root, "usage_log.py", "add", "--role", "writer", "--model", "m", "--range", "4", "--input", "50", "--output", "5", "--cache-read", "700", "--source", "manual")
        c, o = run(root, "usage_log.py", "report")
        check("usage report separates sources and never merges them",
              c == 0 and "PROVIDER-REPORTED" in o and "MANUALLY OBSERVED" in o and "ESTIMATED" in o and "never added across sources" in o
              and "unknown" in o, o)
        check("usage report shows cache tokens and no invented price", "cache_rd" in o and "700" in o and "USD" not in o.split("Prices come")[0], o)
        write(root / "ops/prices.json", json.dumps({"m": {"input": 3.0, "output": 15.0}}))
        c, o = run(root, "usage_log.py", "report")
        check("cost is labelled with its source and flags unpriced cache", "reported-based" in o and "manual-based" in o and "cache tokens not priced" in o, o)
        run(root, "log_run.py", "--chapter", "7", "--scores", "3,3,3,-,3,3")
        run(root, "log_run.py", "--chapter", "7", "--scores", "4,4,4,-,4,4")
        rows = [r for r in (root / "ops/scores.csv").read_text().splitlines() if r.startswith("7,")]
        check("log_run keeps one scores row per chapter", rows == ["7,4,4,4,-,4,4"], str(rows))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def phase_b_tests():
    fx = TOOLS.parent / "tests/fixtures/golden5"

    def pack(root, *args):
        return run(root, "context_pack.py", "--part", "delta", *args)

    def fresh():
        root = Path(tempfile.mkdtemp(prefix="anogen-fx-"))
        shutil.rmtree(root)
        shutil.copytree(fx / "root", root)
        for name in ("state", "debts", "secrets"):
            shutil.copy(fx / "memory/pack23" / f"{name}.md", root / "story/bible" / f"{name}.md")
        return root

    def install(root, k):
        for name in ("state", "debts", "secrets"):
            shutil.copy(fx / "memory" / f"pack{k}" / f"{name}.md", root / "story/bible" / f"{name}.md")

    # diff round trip (property test over random edits)
    code = ("import random, context_pack as c\nrng = random.Random(5); ok = True\n"
            "for _ in range(300):\n"
            "    old = [f'line {i} ' + 'x' * rng.randint(0, 20) for i in range(rng.randint(0, 30))]\n"
            "    new = list(old)\n"
            "    for _ in range(rng.randint(0, 6)):\n"
            "        op = rng.choice('dia'); k = rng.randint(0, max(len(new) - 1, 0))\n"
            "        if op == 'd' and new: new.pop(k)\n"
            "        elif op == 'i': new.insert(k, 'new ' + str(rng.random()))\n"
            "        elif new: new[k] = 'changed ' + str(rng.random())\n"
            "    a, b = '\\n'.join(old).strip(), '\\n'.join(new).strip()\n"
            "    ok &= c.apply_diff(a, c.make_diff(a, b)).strip() == b\n"
            "print(ok)\n")
    r = subprocess.run([PY, "-c", code], capture_output=True, text=True, cwd=TOOLS,
                       env=dict(os.environ, ANOGEN_ROOT=str(fx / "root")))
    check("make_diff/apply_diff rebuild text exactly (300 random edits)", r.stdout.strip() == "True", r.stdout + r.stderr[-300:])

    root = fresh()
    try:
        c, o = pack(root, "--chapter", "24", "--no-tail", "--incremental")
        check("incremental without a cache falls back to FULL and says why", c == 0 and "context mode: FULL: no cache" in o and "[CHANGED" not in o and "## State\n#" in o, o[:300])
        c, o = pack(root, "--chapter", "23", "--incremental", "--batch-start")
        check("batch start gives full text and writes the cache", c == 0 and "FULL: batch start" in o and (root / "ops/ctx-cache.json").exists(), o[:200])
        full23 = o
        c, o = pack(root, "--chapter", "23", "--no-tail")
        check("default pack is unchanged (no mode line, full State)", c == 0 and "context mode" not in o and "## State\n#" in o)
        install(root, 24)
        c, o = pack(root, "--chapter", "24", "--no-tail", "--incremental", "--peek")
        check("next chapter sends a diff for State and stubs for Debts/Secrets",
              c == 0 and "DIFF vs the chapter 23 pack" in o and "## State [CHANGED since the chapter 23 pack" in o and "[unchanged since the chapter 23 pack" in o, o[:400])
        cache_before = (root / "ops/ctx-cache.json").read_text()
        check("--peek never writes the cache", '"base_chapter": 23' in cache_before)
        c, o = pack(root, "--chapter", "25", "--no-tail", "--incremental", "--peek")
        check("a skipped chapter (cache is for 23, asking for 25) falls back to FULL", "FULL: cache is for chapter 23" in o and "## State\n#" in o, o[:300])
        c, o = pack(root, "--chapter", "24", "--no-tail", "--incremental")
        check("chapter 24 incremental ok and cache moves to 24", c == 0 and '"base_chapter": 24' in (root / "ops/ctx-cache.json").read_text())
        # invalidation: static source change
        (root / "story/style/banned.md").write_text((root / "story/style/banned.md").read_text() + "\n- extra\n")
        c, o = pack(root, "--chapter", "25", "--no-tail", "--incremental", "--peek")
        check("changed static source invalidates the cache", "FULL: static sources" in o, o[:300])
        (root / "story/style/banned.md").write_text((root / "story/style/banned.md").read_text().replace("\n- extra\n", ""))
        # invalidation: old cache
        d = json.loads((root / "ops/ctx-cache.json").read_text()); d["ts"] -= 4 * 3600
        (root / "ops/ctx-cache.json").write_text(json.dumps(d))
        c, o = pack(root, "--chapter", "25", "--no-tail", "--incremental", "--peek")
        check("cache older than 3 hours is ignored", "FULL: cache older than 3 hours" in o, o[:300])
        # large change: diff bigger than 60% falls back to full text
        d["ts"] += 4 * 3600
        (root / "ops/ctx-cache.json").write_text(json.dumps(d))
        (root / "story/bible/state.md").write_text("# Totally new state\n" + "\n".join(f"- brand new line {i} about something else entirely" for i in range(40)))
        c, o = pack(root, "--chapter", "25", "--no-tail", "--incremental", "--peek")
        check("a change larger than 60% sends the full text, not a diff", "## State\n# Totally new state" in o and "[CHANGED" not in o.split("## Debts")[0], o[:300])
    finally:
        shutil.rmtree(root, ignore_errors=True)

    # golden A/B: lossless, smaller from the second chapter, retrieval finds the planted facts
    r = subprocess.run([PY, str(TOOLS / "ctx_compare.py"), "--json"], capture_output=True, text=True)
    try:
        res = json.loads(r.stdout)
    except ValueError:
        res = {"problems": ["unparsable output"], "rows": []}
    check("golden fixture: State/Debts/Secrets rebuilt exactly from incremental packs", r.returncode == 0 and not res["problems"], r.stdout[-400:] + r.stderr[-300:])
    later = [x for x in res["rows"] if x["chapter"] != 23]
    check("golden fixture: incremental pack is smaller for every later chapter", bool(later) and all(x["incremental_chars"] < x["full_chars"] for x in later), str(res.get("rows")))
    check("golden fixture: first chapter pays only the small mode note", res["rows"] and res["rows"][0]["incremental_chars"] - res["rows"][0]["full_chars"] < 300, str(res.get("rows")))
    check("golden fixture: retrieval finds the expected thread/twist lines", all(not v["missing"] for v in res.get("retrieval", {"x": {"missing": ["?"]}}).values()), str(res.get("retrieval")))

    # retrieval behaviour
    root = fresh()
    try:
        c, o = run(root, "memory_retrieve.py", "--chapter", "26")
        check("retrieval shows provenance for every item", c == 0 and "story/bible/twists-1.md:16" in o and "ignored as too common" in o, o[:400])
        c, o = run(root, "memory_retrieve.py", "--chapter", "26", "--budget", "500")
        check("retrieval over budget names what it left out", "not shown, over the 500-char budget" in o, o[-300:])
        c, o = run(root, "context_pack.py", "--part", "delta", "--chapter", "26", "--no-tail", "--retrieve", "--peek")
        check("--retrieve adds the Retrieved memory section", c == 0 and "## Retrieved memory" in o)
        c, o = run(root, "context_pack.py", "--part", "delta", "--chapter", "26", "--no-tail", "--peek")
        check("without --retrieve there is no retrieval section", "Retrieved memory" not in o)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def novel_tests():
    """novels/<slug>/ layout: creation, selection, isolation, one global lock."""
    import hashlib
    repo = Path(tempfile.mkdtemp(prefix="anogen-novels-"))
    shutil.copytree(TOOLS, repo / "tools", ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copytree(TOOLS.parent / "templates", repo / "templates")

    def nrun(script, *args, novel=None):
        env = {k: v for k, v in os.environ.items() if k not in ("ANOGEN_ROOT", "ANOGEN_NOVEL")}
        if novel:
            env["ANOGEN_NOVEL"] = novel
        r = subprocess.run([PY, str(repo / "tools" / script), *args], capture_output=True, text=True, env=env, cwd=repo)
        return r.returncode, r.stdout + r.stderr

    def snap(slug):
        out = {}
        for f in sorted((repo / "novels" / slug).rglob("*")):
            if f.is_file():
                out[str(f.relative_to(repo / "novels" / slug))] = hashlib.sha256(f.read_bytes()).hexdigest()
        return out

    (repo / "novels").mkdir()
    rc, o = nrun("novel.py", "list")
    check("novel: list with no novels is not an error", rc == 0, o)
    rc, o = nrun("status.py")
    check("novel: tools refuse to run with no active novel (clear message)", rc != 0 and "no active novel" in o, o)
    rc, o = nrun("novel.py", "new", "alpha-saga", "--title", "Alpha Saga")
    check("novel: new creates folder from template and activates it", rc == 0 and (repo / "novels/alpha-saga/story/brief.md").exists()
          and (repo / "novels/ACTIVE").read_text().strip() == "alpha-saga", o)
    check("novel: title written into brief", "title: Alpha Saga" in (repo / "novels/alpha-saga/story/brief.md").read_text())
    rc, o = nrun("novel.py", "new", "alpha-saga", "--title", "again")
    check("novel: new refuses an existing slug", rc != 0, o)
    rc, o = nrun("novel.py", "new", "Bad Slug", "--title", "x")
    check("novel: new refuses an invalid slug", rc != 0, o)
    rc, o = nrun("novel.py", "new", "beta-tale", "--title", "Beta Tale")
    check("novel: second novel created", rc == 0 and (repo / "novels/beta-tale/ops/scores.csv").exists(), o)
    a_before = snap("alpha-saga")
    rc, o = nrun("inbox.py", "add", "idea for beta")
    check("novel: commands act on the active novel only", rc == 0 and "idea for beta" in (repo / "novels/beta-tale/story/inbox.md").read_text(), o)
    check("novel: other novel is byte-identical after the command", snap("alpha-saga") == a_before)
    rc, o = nrun("inbox.py", "add", "idea for alpha", novel="alpha-saga")
    check("novel: ANOGEN_NOVEL overrides ACTIVE", rc == 0 and "idea for alpha" in (repo / "novels/alpha-saga/story/inbox.md").read_text()
          and "idea for alpha" not in (repo / "novels/beta-tale/story/inbox.md").read_text(), o)
    rc, o = nrun("novel.py", "use", "nope")
    check("novel: use refuses an unknown novel", rc != 0, o)
    rc, o = nrun("novel.py", "use", "alpha-saga")
    check("novel: use switches the active novel", rc == 0 and (repo / "novels/ACTIVE").read_text().strip() == "alpha-saga", o)
    rc, o = nrun("novel.py", "new", "gamma", "--title", "Gamma", "--style-from", "missing")
    check("novel: --style-from an unknown novel is refused and creates nothing", rc != 0 and not (repo / "novels/gamma").exists(), o)
    (repo / "novels/alpha-saga/story/style/profile.md").write_text("# custom style\n")
    rc, o = nrun("novel.py", "new", "delta", "--title", "Delta", "--style-from", "alpha-saga")
    check("novel: --style-from copies the profile", rc == 0 and (repo / "novels/delta/story/style/profile.md").read_text() == "# custom style\n", o)
    rc, o = nrun("lock.py", "acquire", "write", "--owner", "w", novel="alpha-saga")
    rc2, o2 = nrun("lock.py", "acquire", "write", "--owner", "w2", novel="beta-tale")
    check("novel: ONE global lock (second novel cannot start while the first is locked)", rc == 0 and rc2 == 3, o + o2)
    rc, o = nrun("lock.py", "release", "write", "--owner", "w", novel="alpha-saga")
    check("novel: lock released", rc == 0, o)
    (repo / "novels/ACTIVE").write_text("ghost\n")
    rc, o = nrun("status.py")
    check("novel: ACTIVE pointing at a missing novel fails clearly", rc != 0 and "not found" in o, o)
    # chapter heading format (owner order 2026-11-25): "# Chapter N: Title"
    hroot = mkroot(chapters=(1, 2))
    rc, o = run(hroot, "check_chapter.py", "chapters/chapter-001.md", "--strict")
    check("heading: '# Chapter 1: Title' is accepted", "must be '# Chapter N: Title'" not in o and "heading says" not in o, o)
    body = (hroot / "chapters/chapter-001.md").read_text().split("\n", 1)[1]
    for label, head in (("old '# Title'", "# Forty Minutes of Grass"), ("no colon", "# Chapter 1 Forty"), ("wrong number", "# Chapter 7: Forty")):
        (hroot / "chapters/chapter-001.md").write_text(head + "\n" + body)
        rc, o = run(hroot, "check_chapter.py", "chapters/chapter-001.md", "--strict")
        check(f"heading: {label} is an ISSUE (strict exit 1)", rc == 1 and ("ISSUE" in o), o)
    rc, o = run(hroot, "verify_batch.py", "1-1")
    check("heading: verify_batch reports a bad heading", "ch 1:" in o and ("Chapter" in o), o)
    shutil.rmtree(hroot, ignore_errors=True)
    # rename.py: whole words, longest first, dry run, de-dupe of canon names, skip list
    rroot = mkroot(chapters=(1,))
    (rroot / "chapters/chapter-001.md").write_text("# Chapter 1: T\n\nI let the Mantle come. The Faceless Mantle's hood. Mantlepiece and Patience as a virtue? No: Patience and Kingsrest.\n")
    write(rroot / "story/bible/canon_names.txt", "# x\nFaceless Mantle\nMantle\nAlvar\n")
    write(rroot / "story/bible/armor.md", "Faceless Mantle plate; the Mantle.\n")
    write(rroot / "story/skipme.md", "Mantle stays here\n")
    write(rroot / "story/rename-map.json", json.dumps({"_skip": ["story/skipme.md"], "The Faceless Mantle": "Umra", "Faceless Mantle": "Umra", "the Mantle": "Umra", "Mantle": "Umra", "Patience and Kingsrest": "Tamu and Oru"}))
    before = (rroot / "chapters/chapter-001.md").read_text()
    rc, o = run(rroot, "rename.py")
    check("rename: dry run writes nothing", rc == 0 and "DRY RUN" in o and (rroot / "chapters/chapter-001.md").read_text() == before, o)
    rc, o = run(rroot, "rename.py", "--apply")
    ch = (rroot / "chapters/chapter-001.md").read_text()
    check("rename: whole words, possessive and longest-first", "I let Umra come. Umra's hood." in ch and "Mantlepiece" in ch and "Tamu and Oru" in ch, ch)
    check("rename: a name that is a common word elsewhere is left alone (only mapped phrases change)", "Patience as a virtue" in ch, ch)
    check("rename: skip list is untouched", (rroot / "story/skipme.md").read_text() == "Mantle stays here\n")
    check("rename: canon_names de-duplicated", (rroot / "story/bible/canon_names.txt").read_text() == "# x\nUmra\nAlvar\n", (rroot / "story/bible/canon_names.txt").read_text())
    rc, o = run(rroot, "rename.py")
    check("rename: second run finds nothing", rc == 0 and "0 replacement" in o, o)
    write(rroot / "story/rename-map.json", json.dumps({"A": "A"}))
    rc, o = run(rroot, "rename.py")
    check("rename: a self-mapping is refused", rc != 0, o)
    shutil.rmtree(rroot, ignore_errors=True)
    shutil.rmtree(repo, ignore_errors=True)


def policy_tests():
    """Single-agent policy (tools/policy_check.py)."""
    import json as _j
    import policy_check as pc
    repo = Path(__file__).resolve().parent.parent
    check("policy: repo passes the single-agent check", pc.run(repo) == [], "; ".join(pc.run(repo)))
    check("policy: spawn instruction is flagged", len(pc.scan_text("x.md", "Then spawn ONE agent for the writer.")) == 1)
    check("policy: sub-agent instruction is flagged", len(pc.scan_text("x.md", "Use a sub-agent per chapter.")) == 1)
    check("policy: delegation is flagged", len(pc.scan_text("x.md", "Delegate the critic to a second model.")) == 1)
    check("policy: a forbidding line passes", pc.scan_text("x.md", "NEVER spawn sub-agents.") == [])
    check("policy: Indonesian forbidding line passes", pc.scan_text("x.md", "Tidak pernah memakai subagent.") == [])
    d = Path(tempfile.mkdtemp())
    try:
        (d / "engine").mkdir()
        (d / "engine" / "models.json").write_text(_j.dumps({"roles": {"w": {"mode": "delegate"}}}), encoding="utf-8")
        r = pc.run(d)
        check("policy: delegate mode in models.json is an ERROR", any("delegate" in x for x in r), str(r))
        (d / "engine" / "models.json").write_text("{bad", encoding="utf-8")
        check("policy: unreadable models.json is an ERROR", any("unreadable" in x for x in pc.run(d)))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def stage2_tests():
    """Context engine: style split, dedup, budget, fingerprint (tools/context_pack.py)."""
    import context_pack as cp
    prof = ("## 1. LEVEL\nalways\n\n## 9. SCENE FEEL AND ARMOR (x)\n- mood\n"
            "- ARMOR (story/bible/armor.md; invent nothing): whenever\n- armor rule\n\n## 10. BATTLES AND AURA\n- battle rule\n\n## 11. NATURAL\n- human\nvoice\n")
    quiet, loud = "Ch 5: they cook soup and talk.", "Ch 5: a duel in the yard."
    s, om = cp.style_for(prof, quiet)
    check("ctx style: quiet outline stubs the situational blocks", len(om) == 2 and "armor rule" not in s and "battle rule" not in s, str(om))
    check("ctx style: always-on rules stay", all(k in s for k in ("always", "- mood", "- human", "voice")))
    check("ctx style: stub names what was omitted", "STYLE NOTE" in s and "--style full" in s)
    check("ctx style: fight outline keeps everything", cp.style_for(prof, loud) == (prof, []))
    check("ctx style: no outline keeps everything", cp.style_for(prof, "") == (prof, []))
    check("ctx style: --style full keeps everything", cp.style_for(prof, quiet, "full") == (prof, []))
    long = "x" * 90
    secs, rem = cp.dedup_sections(["## A\n" + long, "## B\n" + long + "\nshort", "## C\nshort"])
    check("ctx dedup: identical long line kept once", sum(long in s for s in secs) == 1 and rem == 91, str(rem))
    check("ctx dedup: short lines never removed", secs[1].endswith("short") and secs[2].endswith("short"))
    d = "## S [CHANGED since the chapter 4 pack: x]\n" + long
    check("ctx dedup: diff sections untouched", cp.dedup_sections(["## A\n" + long, d])[0][1] == d)
    check("ctx: fingerprint is stable and content-sensitive", cp.sha("a") == cp.sha("a") and cp.sha("a") != cp.sha("b"))
    base = [sys.executable, str(TOOLS / "context_pack.py"), "--part", "delta", "--retrieve", "--peek"]
    full = subprocess.run(base + ["--budget", "10000000"], capture_output=True, text=True)
    n = len(full.stdout.split("\n[context fingerprint")[0])
    check("ctx: footer carries fingerprint and estimate label", "[context fingerprint" in full.stdout and "ESTIMATE" in full.stdout)
    if "## Retrieved memory" in full.stdout:
        lim = n - 500  # the precheck name picks vary by ~150 chars between runs, so the margin must be larger than that
        small = subprocess.run(base + ["--budget", str(lim)], capture_output=True, text=True)
        check("ctx budget: low-priority section dropped whole with a note", small.returncode == 0 and "PACK NOTE" in small.stdout and "## Retrieved memory" not in small.stdout, small.stderr)
    root = mkroot([1, 2])
    try:
        write(root / "story/bible/combat-style.md", "# Combat\n## Stance\nlow and calm\n")
        write(root / "story/bible/series.md", "x")
        write(root / "story/outline/arc-1.md", "# A\n- Ch 3: they cook soup and talk.\n- Ch 4: a walk in the rain.\n- Ch 5: tea.\n")
        c, q = run(root, "context_pack.py", "--part", "static", "--chapter", "3", "--peek", "--extra", "combat-style?")
        check("ctx extra?: conditional extra is replaced by a stub when the outline has no fight", c == 0 and "## Extra: combat-style\n[omitted" in q and "low and calm" not in q, q[-400:])
        write(root / "story/outline/arc-1.md", "# A\n- Ch 3: they cook soup.\n- Ch 4: a duel in the yard.\n- Ch 5: tea.\n")
        c, q2 = run(root, "context_pack.py", "--part", "static", "--chapter", "3", "--peek", "--extra", "combat-style?")
        check("ctx extra?: loaded when the outline shows a fight", "low and calm" in q2 and "[omitted" not in q2.split("Extra: combat-style")[1][:40], q2[-300:])
        c, q3 = run(root, "context_pack.py", "--part", "static", "--chapter", "3", "--peek", "--extra", "combat-style")
        check("ctx extra: a name without '?' is always loaded", "low and calm" in q3)
        fp = q2.strip().splitlines()[-1].split("fingerprint ")[1].split(";")[0]
        c, q4 = run(root, "context_pack.py", "--part", "static", "--chapter", "3", "--peek", "--extra", "combat-style?", "--static-seen", fp)
        check("ctx static-seen: an identical static pack becomes one line", "static context unchanged" in q4 and len(q4) < 500 and "Style profile" not in q4, q4[:300])
        c, q5 = run(root, "context_pack.py", "--part", "static", "--chapter", "3", "--peek", "--extra", "combat-style?", "--static-seen", "000000000000")
        check("ctx static-seen: a different fingerprint still gives the full pack", "Style profile" in q5 and "unchanged" not in q5.split("## Style")[0][-200:])
    finally:
        shutil.rmtree(root, ignore_errors=True)
    tiny = subprocess.run(base + ["--budget", "3000"], capture_output=True, text=True)
    check("ctx budget: protected sections over budget exit 4, never silent", tiny.returncode == 4 and "TRUNCATED" in tiny.stdout, str(tiny.returncode))


def stage3_tests():
    """Python-first validation report (tools/validate.py)."""
    root = mkroot([1, 2, 4], ARC_RUNNING)
    try:
        write(root / "chapters/chapter-002.md", "# Chapter 2: Test Title\n\nAlvar walked to the gate and")
        write(root / "story/bible/summaries.md", "# S\n## Ch 1 - A\nx\n## Ch 1 - A again\ny\n")
        write(root / "story/bible/debts.md", "# D\n- [open] old promise | planted: ch 1 | due: ch 2\n- [open] no due here | planted: ch 1\n- [paid] done | planted: ch 1 | due: ch 3\n")
        write(root / "ops/schedule.json", "{bad")
        c, o = run(root, "validate.py", "1-4")
        check("validate: exit 1 and ERROR lines when something is wrong", c == 1 and "ERROR" in o, o[-300:])
        check("validate: numbering gap is an ERROR", "gap in numbering: missing [3]" in o, o)
        check("validate: truncated ending is an ERROR", "ch 2: possibly truncated" in o, o)
        check("validate: missing chapter file is an ERROR", "ch 3: file missing" in o, o)
        check("validate: invalid JSON is an ERROR", "ops/schedule.json: invalid JSON" in o, o)
        check("validate: duplicate summary is an ERROR", "chapter 1 has 2 summaries" in o, o)
        check("validate: overdue open debt is a WARNING", "WARNING: debts.md:2: open debt is overdue" in o, o)
        check("validate: debt without due is a WARNING", "WARNING: debts.md:3: open debt has no" in o, o)
        check("validate: paid debt is not flagged", "debts.md:4" not in o, o)
        check("validate: summary line present", "VALIDATION 1-4:" in o and "error(s)" in o and "warning(s)" in o, o)
        c, o = run(root, "validate.py", "1-1", "--json")
        j = json.loads(o)
        check("validate: --json is parseable with counts", "summary" in j and j["summary"]["chapters_checked"] == 1 and isinstance(j["items"], list), o[:200])
        c, o = run(root, "validate.py", "bad")
        check("validate: bad range prints usage", c != 0, o[:100])
    finally:
        shutil.rmtree(root, ignore_errors=True)


def stage4_tests():
    """Risk-based self-review (tools/risk.py, tools/review_pack.py, engine/self-review-checklist.md)."""
    eng = {"arcs": {"1": {"start": 1, "end": 9, "name": "A", "max": 9, "status": "writing"}}}
    root = mkroot([1, 2, 3, 4, 5, 6, 7, 8, 9], eng)
    try:
        write(root / "story/outline/arc-1.md", "# A\n- Ch 1: Alvar cooks soup.\n- Ch 2: Alvar talks to Brenna about hats.\n- Ch 3: Brenna kisses Alvar.\n"
              "- Ch 4: The captain dies in the yard.\n- Ch 5: Walk to town.\n- Ch 6: Walk home.\n- Ch 7: Sleep.\n- Ch 8: Wake.\n- Ch 9: Finale of the arc.\n")
        write(root / "story/bible/reveal-ladder.md", "# L\n- R1 plot (big): H 2 | D 5 | C 6\n")
        write(root / "story/bible/debts.md", "# D\n- [open] hat debt | planted: ch 1 | due: ch 7\n")
        write(root / "story/bible/first-use.md", "# F\n")
        def lvl(n):
            c, o = run(root, "risk.py", str(n), "--json")
            return json.loads(o)["risk"], o
        check("risk: plain chapter is LOW", lvl(1)[0] == "LOW", lvl(1)[1])
        check("risk: ladder hint is MEDIUM", lvl(2)[0] == "MEDIUM", lvl(2)[1])
        check("risk: relationship keyword is MEDIUM", lvl(3)[0] == "MEDIUM", lvl(3)[1])
        check("risk: death keyword is HIGH", lvl(4)[0] == "HIGH", lvl(4)[1])
        check("risk: reveal CONFIRM is HIGH", lvl(6)[0] == "HIGH", lvl(6)[1])
        check("risk: open debt due is MEDIUM", lvl(7)[0] == "MEDIUM", lvl(7)[1])
        check("risk: arc end is HIGH", lvl(9)[0] == "HIGH", lvl(9)[1])
        c, o = run(root, "review_pack.py", "4")
        check("review pack: has chapter, outline, canon, checklist and risk", c == 0 and "## Chapter text" in o and "## Outline line" in o and "## Relevant canon" in o and "## Checklist" in o and "Risk: HIGH" in o, o[:200])
        check("review pack: leaves out the writer's style profile, premise and characters", "## Style profile" not in o and "## Premise" not in o and "## Characters" not in o)
        c, lo = run(root, "review_pack.py", "1")
        c, me = run(root, "review_pack.py", "2")
        c, hi = run(root, "review_pack.py", "4")
        check("review pack: LOW risk does not reload the chapter text", "Chapter text in this pack: none" in lo and "## Chapter text" not in lo and "## Opening" not in lo and "## Ending (last 40 words)" in lo, lo[:300])
        check("review pack: MEDIUM risk carries opening and ending excerpts only", "Chapter text in this pack: excerpts" in me and "## Opening" in me and "## Chapter text" not in me, me[:300])
        check("review pack: HIGH risk reloads the whole chapter", "Chapter text in this pack: full" in hi and "## Chapter text" in hi, hi[:300])
        check("review pack: compact modes are smaller than full", len(lo) < len(me) < len(hi), f"{len(lo)} {len(me)} {len(hi)}")
        c, fo = run(root, "review_pack.py", "1", "--text", "full")
        check("review pack: --text full overrides the risk choice", "## Chapter text" in fo and c == 0)
        check("review pack: LOW checklist keeps only items 1, 5, 7, 9", all(f"\n{i}. " in lo for i in (1, 5, 7, 9)) and "\n2. " not in lo and "\n3. " not in lo, lo[-700:])
        check("review pack: cold-read rule is in the checklist", "COLD READ" in lo and "do not defend" in lo)
        c, o = run(root, "review_pack.py", "1", "--text", "bogus")
        check("review pack: bad --text value prints usage", c != 0)
        c, o = run(root, "review_pack.py", "40")
        check("review pack: missing chapter is an ERROR line", "ERROR" in o, o[:100])
    finally:
        shutil.rmtree(root, ignore_errors=True)


def stage5_tests():
    """Story memory index (tools/memory_index.py): SQLite + FTS5 derived from markdown."""
    eng = {"arcs": {"1": {"start": 1, "end": 3, "name": "A", "max": 3, "status": "writing"}, "2": {"start": 4, "end": 6, "name": "B", "max": 3, "status": "planned"}}}
    root = mkroot([], eng)
    try:
        write(root / "story/bible/canon_names.txt", "Alvar\nBrenna\nCorentin\n")
        write(root / "story/bible/summaries.md", "# S\n## Ch 1 - A\nAlvar finds a silver locket. He hides it.\n## Ch 2 - B\nBrenna sees the locket and says nothing.\n## Ch 4 - C\nCorentin returns.\n")
        write(root / "story/bible/threads.md", "# T\n1. Whose locket is it | 1 | 2 feeds | 5 | ok\n")
        write(root / "story/bible/debts.md", "# D\n- [open] Locket (Corentin) | planted: ch 1 | due: ch 5\n- [paid] Soup debt | planted: ch 2 | due: ch 3\n- [open] Locket (Corentin) | planted: ch 1 | due: ch 5\n")
        write(root / "story/bible/secrets.md", "# S\n- Corentin was a Veil (big) | known by: Alvar | reveal planned: ch 5\n")
        write(root / "story/bible/timeline.md", "# T\n- Ch 1 the locket is found in the well\n- Old text SUPERSEDED by the new timeline\n")
        write(root / "story/bible/characters.md", "# C\n- **Alvar Stone**, 18, finds things\n")
        write(root / "story/outline/arc-1.md", "# A\n- Ch 1: Alvar finds the locket.\n- Ch 2: Brenna asks about it.\n")
        c, o = run(root, "memory_index.py", "update")
        check("memory: first update indexes all sources", c == 0 and "rows in index" in o and "summaries:3" in o, o)
        check("memory: identical lines are deduplicated", "duplicates skipped: 1" in o, o)
        c, o = run(root, "memory_index.py", "update")
        check("memory: unchanged files are not re-indexed", "nothing changed" in o, o)
        c, o = run(root, "memory_index.py", "query", "--text", "silver locket")
        check("memory: FTS finds the summary with provenance", "story/bible/summaries.md:" in o and "silver locket" in o, o)
        c, o = run(root, "memory_index.py", "query", "--chars", "Corentin", "--type", "debt", "--status", "open")
        check("memory: filter by character, type and status", c == 0 and "debts.md:2" in o and "paid" not in o, o)
        c, o = run(root, "memory_index.py", "query", "--chapter", "1", "--near", "1", "--type", "chapter")
        check("memory: filter by chapter window", "ch 1" in o and "ch 2" in o and "ch 4" not in o, o)
        c, o = run(root, "memory_index.py", "query", "--arc", "2", "--type", "chapter")
        check("memory: filter by arc", "ch 4" in o and "ch 1 " not in o, o)
        c, o = run(root, "memory_index.py", "query", "--type", "thread")
        check("memory: thread ledger row gets its raised chapter", "thread ch 1" in o, o)
        c, o = run(root, "memory_index.py", "query", "--type", "secret")
        check("memory: major importance is read from the line itself", "MAJOR" in o, o)
        c, o = run(root, "memory_index.py", "query", "--type", "event", "--status", "superseded")
        check("memory: SUPERSEDED line gets that status", "SUPERSEDED" in o, o)
        write(root / "story/bible/debts.md", "# D\n- [open] New debt about a hat | planted: ch 2 | due: ch 6\n")
        c, o = run(root, "memory_index.py", "update")
        check("memory: only the changed file is re-indexed", "bible/debts.md:1" in o and "threads" not in o, o)
        c, o = run(root, "memory_index.py", "arc-digest", "1")
        check("memory: arc digest uses first sentences and provenance", "Ch 1: Alvar finds a silver locket." in o and "He hides it" not in o and "Ch 4" not in o, o)
        db = root / "ops" / "memory.sqlite"
        db.write_bytes(b"this is not a database at all, just damaged bytes" * 50)
        c, o = run(root, "memory_index.py", "update")
        check("memory: damaged index is set aside and rebuilt", c == 0 and "rows in index" in o and (root / "ops" / "memory.sqlite.corrupt").exists(), o)
        check("memory: markdown sources untouched by indexing", "SUPERSEDED" in read_text(root / "story/bible/timeline.md"))
    finally:
        shutil.rmtree(root, ignore_errors=True)
    # labeled retrieval benchmark (tools/bench_memory.py; labels by the orchestrator, not owner-verified)
    b = subprocess.run([sys.executable, str(TOOLS / "bench_memory.py")], capture_output=True, text=True)
    prod = [l for l in b.stdout.splitlines() if l.startswith("- production")]
    old = [l for l in b.stdout.splitlines() if l.startswith("- chapter-order")]
    check("memory benchmark: production ranking finds the labeled chapter at rank 1 for >= 90% of queries and beats chapter order",
          b.returncode == 0 and bool(prod) and bool(old) and float(prod[0].split("hit@1")[1].split()[0]) >= 0.9
          and float(old[0].split("hit@1")[1].split()[0]) < 0.5, b.stdout + b.stderr)


def read_text(p):
    return Path(p).read_text(encoding="utf-8")


def stage6_tests():
    """Usage and cost measurement (tools/usage_log.py): actual vs estimate, per chapter, projection, context log."""
    root = mkroot([1, 2], ARC_RUNNING)
    try:
        c, o = run(root, "usage_log.py", "report")
        check("cost: no data says UNMEASURED, no projection", "UNMEASURED" in o and "850" not in o, o)
        run(root, "usage_log.py", "add", "--role", "writer", "--model", "m", "--provider", "p", "--range", "1-2", "--input", "1000", "--output", "500",
            "--source", "reported", "--actual-cost", "0.30", "--context-chars", "30000", "--context-fingerprint", "abc123", "--revision-count", "1")
        row = json.loads((root / "ops/usage.jsonl").read_text().splitlines()[0])
        check("usage row carries novel, provider, operation, total tokens, context size, fingerprint, revisions, actual cost",
              row["provider"] == "p" and row["operation"] == "writer" and row["total_tokens"] == 1500 and row["context_characters"] == 30000
              and row["context_fingerprint"] == "abc123" and row["revision_count"] == 1 and row["actual_cost"] == 0.30 and row["novel"], str(row))
        run(root, "usage_log.py", "add", "--role", "writer", "--range", "1-2", "--source", "estimate", "--input", "9999999", "--output", "9999999")
        c, o = run(root, "usage_log.py", "report")
        reported = o.split("== ESTIMATED")[0]
        check("cost: per-chapter and per-100 from provider actual_cost", "0.1500 USD" in reported and "15.00 USD" in reported, o)
        check("cost: 850-chapter figure is labelled a projection, not a measurement", "PROJECTION" in reported and "NOT a measurement" in reported and "128 USD" in reported, o)
        check("cost: estimate source never feeds the actual figures", "not available" in o.split("== ESTIMATED")[1].split("Prices come")[0], o)
        check("cost: stages and revisions per chapter shown", "role stages per chapter: 0.50" in reported and "revisions/retries per chapter: 0.50" in reported, o)
        write(root / "ops/context-log.jsonl", json.dumps({"chars": 100, "fingerprint": "a", "omitted": []}) + "\n" + json.dumps({"chars": 300, "fingerprint": "b", "omitted": [["x", 1]]}) + "\n")
        c, o = run(root, "usage_log.py", "report")
        check("context log summary is in characters, not tokens", "CONTEXT SIZE LOG (2 pack(s), characters, NOT tokens): avg 200, max 300" in o and "dropped sections: 1" in o, o)
    finally:
        shutil.rmtree(root, ignore_errors=True)


def policy_adversarial_tests():
    """Contradictory active instructions must be rejected; pure prohibitions must pass."""
    import json as _j
    import policy_check as pc
    must_flag = ["Do not forget to spawn an agent.", "Never use sub-agents, except for the critic.", "No delegation is required; delegate the writer.",
                 "Jangan lupa spawn agent untuk critic.", "Tidak pernah memakai subagent, kecuali untuk critic.", "Jangan spawn agent, tetapi gunakan sub-agent untuk critic.",
                 "The critic is an independent reviewer of the writer.", "Open a separate fresh session for the writer and critic roles.",
                 "Do not spawn agents. Spawn one agent for the critic.", "You must spawn the writer.", "Please delegate the audit.",
                 "Run sub-agent for the critic, never for the writer.", "Never use sub-agents unless the critic needs one.",
                 "Tidak boleh spawn agent, namun critic wajib memakai sub-agent.", "Never spawn agents - delegate the critic instead.",
                 "Spawn an agent, not a sub-agent.", "Tidak ada delegasi; delegate the writer.", "Gunakan sub-agent hanya untuk critic.",
                 "Do not spawn; instead delegate to a second model."]
    must_pass = ["Never spawn sub-agents.", "NEVER use sub-agents, delegation or parallel agents.", "Tidak pernah memakai subagent.", "Jangan pernah mendelegasikan.",
                 "Agents are never spawned; the orchestrator performs each role.", "Sub-agents are NEVER used in this repo; perform each role inline instead.",
                 "It is not allowed to delegate.", "No sub-agents.", "The critic is NOT an independent reviewer.", "Never start sub-agents (do not use the Agent tool)."]
    missed = [s for s in must_flag if not pc.scan_text("x.md", s)]
    wrong = [s for s in must_pass if pc.scan_text("x.md", s)]
    check(f"policy adversarial: all {len(must_flag)} contradictory lines rejected", not missed, "; ".join(missed))
    check(f"policy adversarial: all {len(must_pass)} pure prohibitions accepted", not wrong, "; ".join(wrong))
    d = Path(tempfile.mkdtemp())
    try:
        (d / "engine").mkdir()
        base = {"concurrency": {"max_agents_per_job": 1}, "roles": {"w": {"mode": "inline-stage"}}}
        def models(x):
            (d / "engine" / "models.json").write_text(_j.dumps(x), encoding="utf-8")
            return pc.run(d)
        check("policy models: clean config passes", models(base) == [])
        bad = _j.loads(_j.dumps(base)); bad["roles"]["w"]["when"] = "strict scoring (independent from the writer)"
        check("policy models: 'independent from the writer' is rejected", any("independent" in x for x in models(bad)), str(models(bad)))
        bad = _j.loads(_j.dumps(base)); bad["roles"]["w"]["mode"] = "parallel"
        check("policy models: a non-inline mode is rejected", len(models(bad)) >= 1)
        bad = _j.loads(_j.dumps(base)); bad["concurrency"]["max_agents_per_job"] = 2
        check("policy models: more than one agent per job is rejected", any("max_agents_per_job" in x for x in models(bad)))
        bad = _j.loads(_j.dumps(base)); bad["orchestrator"] = {"where": "spawns ONE agent at a time"}
        check("policy models: spawn text in any field is rejected", any("spawn" in x.lower() for x in models(bad)), str(models(bad)))
        (d / "AGENTS.md").write_text("Never spawn sub-agents.\nUse a second model for the critic.\n", encoding="utf-8")
        (d / "engine" / "models.json").write_text(_j.dumps(base), encoding="utf-8")
        check("policy files: a contradictory active line in AGENTS.md is rejected", any("AGENTS.md:2" in x for x in pc.run(d)), str(pc.run(d)))
    finally:
        shutil.rmtree(d, ignore_errors=True)


def main():
    root = Path(tempfile.mkdtemp(prefix="anogen-test-"))
    try:
        for d in ("story/bible", "story/outline", "story/style", "chapters", "ops", "out"):
            (root / d).mkdir(parents=True)
        shutil.copy(SRC / "story/brief.md", root / "story/brief.md")
        shutil.copy(SRC / "story/inbox.md", root / "story/inbox.md")
        shutil.copy(SRC / "story/style/banned.md", root / "story/style/banned.md")
        shutil.copy(SRC / "story/style/profile.md", root / "story/style/profile.md")
        write(root / "story/names.md", "# Names\nIntro prose that must be ignored.\n## Culture A\nAlvar, Brenna, Corwin\n## Culture B\nDasha, Emrys\n")
        write(root / "story/bible/canon_names.txt", "Alvar\nBrenna\n")
        write(root / "story/bible/premise.md", "A test world.")
        write(root / "story/bible/state.md", "Alvar is at the harbor.")
        write(root / "story/bible/summaries.md",
              "## Ch 1 - One\nSummary one.\n\n## Ch 2 - Two\nSummary two.\n\n## Ch 3 - Three\nSummary three.\n")
        write(root / "story/outline/series.md", "Series arc text.")
        write(root / "story/outline/arc-1.md",
              "Ch 4 | goal: a | conflict: b | payoff: c | hook: d | pov: first | type: battle\n"
              "Ch 5 | goal: a | conflict: b | payoff: c | hook: d | pov: first | type: quiet\n")
        write(root / "story/outline/pacing.md", "Ch 3: tense\nCh 4: calm\n")
        write(root / "ops/engine.json", json.dumps({"arcs": {}, "batch": {
            "mode": "none", "target": 0, "arc": None, "max": None, "start_chapter": None,
            "status": "idle", "stop_reason": ""}}))
        (root / "ops/schedule.json").write_text((SRC / "ops/schedule.json").read_text())

        rng = random.Random(7)
        names = ["Alvar", "Brenna"]
        for n in range(1, 4):
            epi = "> \"A fine quote.\" - Somebody\n\n" if n == 1 else ""
            write(root / f"chapters/chapter-{n:03d}.md",
                  f"# Chapter {n}: Test Title\n\n" + epi + filler(rng, 2000, names) + "\n")

        # variety
        c, o1 = run(root, "variety.py", "draw", "--chapter", "4")
        c, o2 = run(root, "variety.py", "draw", "--chapter", "4")
        check("variety stable per chapter", c == 0 and o1 == o2 and "opening_type" in o1, o1 + o2)
        run(root, "variety.py", "draw", "--chapter", "5")
        log = json.loads((root / "story/variety_log.json").read_text())
        check("variety avoids last pick", log[1]["picks"]["opening_type"] != log[0]["picks"]["opening_type"])

        # inbox
        run(root, "inbox.py", "add", "a mentor who lies")
        run(root, "inbox.py", "add", "the sea remembers")
        c, o = run(root, "inbox.py", "list")
        check("inbox add/list", "1. a mentor who lies" in o and "2. the sea remembers" in o, o)
        run(root, "inbox.py", "done", "1", "--note", "arc 1 ch 20")
        c, o = run(root, "inbox.py", "list", "--json")
        check("inbox done", json.loads(o) == ["the sea remembers"], o)
        txt = (root / "story/inbox.md").read_text()
        check("inbox processed section", "a mentor who lies -> arc 1 ch 20" in txt, txt)

        # precheck
        c, o = run(root, "precheck.py", "--peek")
        c, oa = run(root, "precheck.py", "--peek", "--names", "all")
        check("precheck lists unused names", "Corwin" in oa and "Dasha" in oa and "Alvar" not in oa.split("Unused names")[1].split("Recent")[0], oa)
        check("precheck hides name pools of nations absent from the outline, and says how to get them", ("Other name pools not shown" in o and "--names all" in o) or ("Corwin" in o and "Dasha" in o), o)
        check("precheck shows inbox", "1 unprocessed" in o, o)

        # context pack
        c, o = run(root, "context_pack.py", "--peek")
        for sec in ("Style profile", "Outline for this and next chapters", "Last summaries",
                    "End of previous chapter", "Debts", "Premise"):
            if sec == "Debts":
                continue
            check(f"context_pack has '{sec}'", sec in o, o[:300])
        check("context_pack outline lines for ch 4", "Ch 4 |" in o and "Ch 5 |" in o)
        check("context_pack summaries before chapter", "Summary three" in o)

        # check_chapter
        talk = "\n\n".join('"' + filler(rng, 110, names).replace("\n", " ") + '"' for _ in range(7))
        write(root / "chapters/chapter-004.md", "# Chapter 4: Four\n\n" + filler(rng, 1450, names) + "\n\n" + talk + "\n")
        c, o = run(root, "check_chapter.py", "chapters/chapter-004.md")
        check("check_chapter clean", "SUMMARY: OK" in o, o)
        bad = "# Chapter 5: Five\n\nA testament to patience. " + "word " * 100 + "\n"
        write(root / "chapters/chapter-005.md", bad)
        c, o = run(root, "check_chapter.py", "chapters/chapter-005.md")
        check("check_chapter flags banned and length", "banned phrase 'a testament to'" in o and "word count" in o, o)
        (root / "chapters/chapter-005.md").unlink()
        (root / "chapters/chapter-004.md").unlink()
        dup = (root / "chapters/chapter-003.md").read_text()
        write(root / "chapters/chapter-004.md", dup)
        c, o = run(root, "check_chapter.py", "chapters/chapter-004.md")
        check("check_chapter flags overlap with previous", "shared with chapter" in o and "too similar" in o, o)
        write(root / "chapters/chapter-004.md", "# Chapter 4: Four\n\n" + filler(rng, 2100, names) + "\n")

        # engine_state
        c, o = run(root, "engine_state.py", "arc-plan", "1", "--start", "1", "--end", "6", "--name", "First", "--max", "10")
        check("arc-plan", c == 0, o)
        c, o = run(root, "engine_state.py", "arc-plan", "2", "--start", "5", "--end", "9")
        check("arc-plan rejects overlap", c != 0, o)
        c, o = run(root, "engine_state.py", "arc-plan", "3", "--start", "7", "--end", "30", "--max", "10")
        check("arc-plan rejects over max", c != 0, o)
        c, o = run(root, "engine_state.py", "arc-complete", "1")
        check("arc-complete refuses with missing chapters", c == 2 and "Missing" in o, o)
        c, o = run(root, "build_epub.py", "--arc", "1")
        check("epub gate refuses incomplete arc", c == 2 and "GATE" in o, o)
        c, o = run(root, "engine_state.py", "batch-start", "--mode", "arc", "--arc", "1", "--max", "10")
        c, o = run(root, "engine_state.py", "next")
        d = json.loads(o)
        check("batch continues mid arc", d["continue"] is True and d["next_chapter"] == 5, o)
        for n in (5, 6):
            write(root / f"chapters/chapter-{n:03d}.md", f"# Chapter {n}: Test Title\n\n" + filler(rng, 1900, names) + "\n")
        c, o = run(root, "engine_state.py", "next")
        d = json.loads(o)
        check("batch ends when arc written", d["continue"] is False and d["batch"]["status"] == "done", o)
        c, o = run(root, "engine_state.py", "arc-complete", "1")
        check("arc-complete refuses without critic pass", c == 2 and "critic" in o, o)
        ed = json.loads((root / "ops" / "engine.json").read_text())
        run(root, "engine_state.py", "mark", "critic", str(ed["arcs"]["1"]["end"]))
        c, o = run(root, "engine_state.py", "arc-complete", "1")
        check("arc-complete ok", c == 0, o)

        # epub
        c, o = run(root, "build_epub.py", "--arc", "1")
        ep = root / "out/arc-1.epub"
        check("epub built", c == 0 and ep.exists(), o)
        if ep.exists():
            with zipfile.ZipFile(ep) as z:
                nm = z.namelist()
                check("epub mimetype first and stored", nm[0] == "mimetype" and z.getinfo("mimetype").compress_type == 0)
                check("epub has 6 chapters", sum(1 for n in nm if n.startswith("OEBPS/c") and n.endswith(".xhtml")) == 6, str(nm))
                check("epub epigraph", b'class="epigraph"' in z.read("OEBPS/c001.xhtml") and b"A fine quote" in z.read("OEBPS/c001.xhtml"))
                check("epub scene break", b'class="brk"' in z.read("OEBPS/c001.xhtml"))
        # gap handling and resume
        os_unlink = (root / "chapters/chapter-003.md")
        keep = os_unlink.read_text()
        os_unlink.unlink()
        c, o = run(root, "engine_state.py", "next")
        check("next fills the lowest gap", json.loads(o)["next_chapter"] == 3, o)
        os_unlink.write_text(keep)
        run(root, "engine_state.py", "batch-start", "--mode", "n", "--target", "3")
        run(root, "engine_state.py", "batch-stop", "--reason", "quota")
        c, o = run(root, "engine_state.py", "batch-resume")
        check("batch-resume", c == 0 and "resumed" in o, o)
        c, o = run(root, "engine_state.py", "arc-plan", "9", "--start", "50", "--end", "60")
        c, o = run(root, "engine_state.py", "batch-start", "--mode", "arc", "--arc", "9")
        check("arc batch refuses when next chapter outside arc", c != 0, o)
        # corrupt json is not overwritten
        (root / "ops/engine.json").write_text("{bad")
        c, o = run(root, "engine_state.py", "show")
        check("corrupt engine.json is an error", c != 0 and (root / "ops/engine.json").read_text() == "{bad", o)
        (root / "ops/engine.json").write_text(json.dumps({"arcs": {"1": {"start": 1, "end": 6, "name": "", "max": 10, "status": "complete"}}, "batch": {"mode": "none", "target": 0, "arc": None, "max": None, "start_chapter": None, "status": "idle", "stop_reason": ""}}))
        # critic/audit tracking
        c, o = run(root, "engine_state.py", "next")
        d2 = json.loads(o)
        check("critic pending reported", d2["critic_pending"] == [1, 6], o)
        run(root, "engine_state.py", "mark", "critic", "6")
        c, o = run(root, "engine_state.py", "next")
        check("critic pending cleared", json.loads(o)["critic_pending"] is None, o)
        # batch n
        c, o = run(root, "engine_state.py", "batch-start", "--mode", "n", "--target", "2")
        c, o = run(root, "engine_state.py", "next")
        check("batch n continues", json.loads(o)["continue"] is True, o)

        # patch
        pf = root / "chapters/chapter-007.md"
        write(pf, "# Seven\n\nThe cat sat. The dog ran. The dog ran.\n")
        c, o = run(root, "patch.py", str(pf), stdin=json.dumps([{"find": "The cat sat.", "replace": "The cat leapt."}]))
        check("patch ok", c == 0 and "leapt" in pf.read_text(), o)
        c, o = run(root, "patch.py", str(pf), stdin=json.dumps([{"find": "The dog ran.", "replace": "x"}]))
        check("patch ambiguous refused", c == 1 and "The dog ran. The dog ran." in pf.read_text(), o)
        pf.unlink()

        # log_run
        c, o = run(root, "log_run.py", "--chapter", "4", "--words", "2100", "--scores", "4,3,4,-,4,3", "--notes", "test")
        check("log_run writes log and scores", c == 0 and "chapter 4" in (root / "ops/run-log.md").read_text()
              and "4,4,3,4,-,4,3" in (root / "ops/scores.csv").read_text(), o)

        # schedule
        c, o = run(root, "schedule.py", "show")
        check("schedule default off", json.loads(o)["enabled"] is False, o)
        run(root, "schedule.py", "enable")
        c, o = run(root, "schedule.py", "show")
        check("schedule enable", json.loads(o)["enabled"] is True, o)
        run(root, "schedule.py", "disable")
        run(root, "schedule.py", "set", "times", "08:05,20:30")
        c, o = run(root, "schedule.py", "cron")
        check("schedule cron", "CRON_TZ=Asia/Jakarta 5 8 * * *" in o and "30 20 * * *" in o, o)
        c, o = run(root, "schedule.py", "set", "times", "25:00")
        check("schedule rejects bad time", c != 0, o)

        # lock
        c, o = run(root, "lock.py", "acquire", "arc1", "--owner", "writer-a")
        check("lock acquire", c == 0, o)
        c, o = run(root, "lock.py", "acquire", "arc1", "--owner", "writer-b")
        check("lock refuses second bot", c == 3 and "BUSY" in o, o)
        run(root, "lock.py", "release", "arc1")
        c, o = run(root, "lock.py", "acquire", "arc1", "--owner", "writer-b")
        check("lock reacquire after release", c == 0, o)
        run(root, "lock.py", "release", "arc1")

        # status
        c, o = run(root, "status.py")
        check("status runs", c == 0 and "Chapters written: 6" in o and "Schedule: OFF" in o, o)

        # save
        subprocess.run(["git", "init", "-q"], cwd=root)
        subprocess.run(["git", "config", "user.email", "t@t"], cwd=root)
        subprocess.run(["git", "config", "user.name", "t"], cwd=root)
        c, o = run(root, "save.py", "test commit", "--no-push")
        log = subprocess.run(["git", "log", "--oneline"], cwd=root, capture_output=True, text=True).stdout
        check("save commits", c == 0 and "test commit" in log, o + log)
        c, o = run(root, "save.py", "again")
        check("save nothing to commit", "Nothing to commit" in o, o)
    finally:
        shutil.rmtree(root, ignore_errors=True)

    phase_two_tests()
    phase_b_tests()
    novel_tests()
    policy_tests()
    policy_adversarial_tests()
    stage2_tests()
    stage3_tests()
    stage4_tests()
    stage5_tests()
    stage6_tests()
    if FAILS:
        print("\nFAILED:", ", ".join(FAILS))
        sys.exit(1)
    print("\nALL TESTS PASSED")


if __name__ == "__main__":
    main()
