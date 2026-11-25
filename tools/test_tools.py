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
    shutil.copy(TOOLS.parent / "story/brief.md", root / "story/brief.md")
    shutil.copy(TOOLS.parent / "story/style/banned.md", root / "story/style/banned.md")
    shutil.copy(TOOLS.parent / "story/style/profile.md", root / "story/style/profile.md")
    write(root / "story/inbox.md", "# Idea inbox\n\n## Unprocessed\n\n## Processed\n")
    write(root / "story/bible/canon_names.txt", "Alvar\nBrenna\n")
    write(root / "story/bible/summaries.md", "# S\n")
    write(root / "ops/engine.json", json.dumps(engine or {"arcs": {}}))
    rng = random.Random(3)
    for n in chapters:
        write(root / f"chapters/chapter-{n:03d}.md", f"# Chapter {n}\n\n" + filler(rng, 2000, ["Alvar", "Brenna"]) + "\n")
    return root


ARC_RUNNING = {"arcs": {"1": {"start": 1, "end": 50, "name": "A", "max": 50, "status": "writing"}},
               "batch": {"mode": "arc", "target": 0, "arc": 1, "max": 50, "start_chapter": 1,
                         "status": "running", "stop_reason": ""}}


def phase_two_tests():
    # P0-1: context pack never cuts silently; the full style profile reaches the writer
    root = mkroot()
    try:
        c, o = run(root, "context_pack.py", "--part", "static", "--peek")
        check("pack keeps Human feel and Protagonist voice", c == 0 and "Human feel" in o and "Protagonist voice" in o and "TRUNCATED" not in o, o[-300:])
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
            write(root / f"chapters/chapter-{n:03d}.md", f"# Chapter {n}\n\n" + filler(random.Random(n), 2000, ["Alvar"]) + "\n")
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
        c, o = run(root, "engine_state.py", "mark", "critic", "10", "--rereview")
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
        c, o = run(root, "usage_log.py", "report")
        check("usage report totals and honest cost", c == 0 and "writer" in o and "critic" in o and "unknown" in o and "    1" in o, o)
        run(root, "log_run.py", "--chapter", "7", "--scores", "3,3,3,-,3,3")
        run(root, "log_run.py", "--chapter", "7", "--scores", "4,4,4,-,4,4")
        rows = [r for r in (root / "ops/scores.csv").read_text().splitlines() if r.startswith("7,")]
        check("log_run keeps one scores row per chapter", rows == ["7,4,4,4,-,4,4"], str(rows))
    finally:
        shutil.rmtree(root, ignore_errors=True)


def main():
    root = Path(tempfile.mkdtemp(prefix="anogen-test-"))
    try:
        for d in ("story/bible", "story/outline", "story/style", "chapters", "ops", "out"):
            (root / d).mkdir(parents=True)
        shutil.copy(TOOLS.parent / "story/brief.md", root / "story/brief.md")
        shutil.copy(TOOLS.parent / "story/inbox.md", root / "story/inbox.md")
        shutil.copy(TOOLS.parent / "story/style/banned.md", root / "story/style/banned.md")
        shutil.copy(TOOLS.parent / "story/style/profile.md", root / "story/style/profile.md")
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
        (root / "ops/schedule.json").write_text((TOOLS.parent / "ops/schedule.json").read_text())

        rng = random.Random(7)
        names = ["Alvar", "Brenna"]
        for n in range(1, 4):
            epi = "> \"A fine quote.\" - Somebody\n\n" if n == 1 else ""
            write(root / f"chapters/chapter-{n:03d}.md",
                  f"# Chapter {n} Title\n\n" + epi + filler(rng, 2000, names) + "\n")

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
        check("precheck lists unused names", "Corwin" in o and "Dasha" in o and "Alvar" not in o.split("Unused names")[1].split("Recent")[0], o)
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
        write(root / "chapters/chapter-004.md", "# Four\n\n" + filler(rng, 1450, names) + "\n\n" + talk + "\n")
        c, o = run(root, "check_chapter.py", "chapters/chapter-004.md")
        check("check_chapter clean", "SUMMARY: OK" in o, o)
        bad = "# Five\n\nA testament to patience. " + "word " * 100 + "\n"
        write(root / "chapters/chapter-005.md", bad)
        c, o = run(root, "check_chapter.py", "chapters/chapter-005.md")
        check("check_chapter flags banned and length", "banned phrase 'a testament to'" in o and "word count" in o, o)
        (root / "chapters/chapter-005.md").unlink()
        (root / "chapters/chapter-004.md").unlink()
        dup = (root / "chapters/chapter-003.md").read_text()
        write(root / "chapters/chapter-004.md", dup)
        c, o = run(root, "check_chapter.py", "chapters/chapter-004.md")
        check("check_chapter flags overlap with previous", "shared with chapter" in o and "too similar" in o, o)
        write(root / "chapters/chapter-004.md", "# Four\n\n" + filler(rng, 2100, names) + "\n")

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
            write(root / f"chapters/chapter-{n:03d}.md", f"# Chapter {n}\n\n" + filler(rng, 1900, names) + "\n")
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
    if FAILS:
        print("\nFAILED:", ", ".join(FAILS))
        sys.exit(1)
    print("\nALL TESTS PASSED")


if __name__ == "__main__":
    main()
