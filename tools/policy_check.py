#!/usr/bin/env python3
"""Single-agent policy check (0 tokens, standard library only).

Usage: policy_check.py [--root PATH]
Exit 1 when the instructions or config say to start sub-agents or delegate.
Checks (ERROR):
  * engine/models.json: no role mode contains 'delegate'; no value mentions spawning.
  * the instruction files below: a line that tells the reader to spawn/start an agent, use delegation or the Agent tool,
    unless the same line forbids it (never / not / no sub-agents / forbidden / without / do not).
Historical records (old audit docs, removed 2026-11-26; the single-agent architecture docs,
novels/*/ops/decisions.md and ops/archive) are not scanned.
"""
import json
import re
import sys
from pathlib import Path

FILES = ["AGENTS.md", "CLAUDE.md", "README.md", "docs/ARCHITECTURE.md", "docs/SINGLE_AGENT_ARCHITECTURE.md"]
GLOBS = ["engine/*.md", "roles/*.md", "templates/**/*.md"]
# Things an active instruction must not tell the reader to do.
BAD = re.compile(r"\b(spawn\w*|sub-?agents?|delegat\w*|agent tool|parallel agents?|"
                 r"independent (?:reviewer|critic|agent|review)s?|separate (?:ai|agent|model)s?|second (?:model|ai|agent)|"
                 r"(?:fresh|separate|new) (?:ai )?sessions? (?:for|per) (?:the |each )?(?:roles?|writer|critic|audit))\b", re.I)
# A clause is exempt only when it is a PURE prohibition: a prohibition word, then at most a few plain words, then the bad term.
# Words that turn a prohibition into an instruction ("forget to", "fail to", "lupa", "except", "kecuali") disqualify it.
NEG = r"(?:never|do not|is not|are not|isn't|aren't|not|don't|must not|mustn't|cannot|can't|no|tidak pernah|tidak boleh|tidak|jangan|dilarang|dilarang keras)"
NEG_BEFORE = re.compile(NEG + r"\b(?:\W+[\w'-]+){0,8}\W*$", re.I)
NEG_AFTER = re.compile(r"^\W+(?:(?:are|is|be|was|were|will be|shall be|should be|can be|may be|get|got)\W+)?(?:never|not|tidak pernah)\b", re.I)
DISQUAL = re.compile(r"\b(?:except|unless|kecuali|apart from|selain|but only|hanya untuk|only for|only when|hanya bila|forget|fail(?:ed)? to|hesitate|lupa|lalai|required|wajib|harus|must)\b", re.I)
SPLIT = re.compile(r"[;:]|\.(?=\s)|\b(?:but|however|although|though|then|whereas)\b|\b(?:tetapi|namun|walaupun|sedangkan|lalu|kemudian)\b|\s-\s|\u2014", re.I)


def clauses(line):
    """Split a line into clauses at sentence ends, ; : dashes and contrast words (the contrast word stays with the next clause)."""
    pieces, last = [], 0
    for m in SPLIT.finditer(line):
        if m.group(0).strip(".;:-\u2014 ") == "":
            pieces.append(line[last:m.start()])
            last = m.end()
        else:
            pieces.append(line[last:m.start()])
            last = m.start()
    pieces.append(line[last:])
    return [p for p in pieces if p.strip()]


def clause_ok(cl):
    """True when every bad term in this clause is under a prohibition: a prohibition word shortly before it, or 'is never/not'
    right after it. Any exception/obligation word in the clause (except, unless, forget to, must, kecuali, lupa...) fails it."""
    ms = list(BAD.finditer(cl))
    if not ms:
        return True
    if DISQUAL.search(cl):
        return False
    return all(NEG_BEFORE.search(cl[:m.start()]) or NEG_AFTER.search(cl[m.end():]) for m in ms)


def scan_text(name, text):
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if not BAD.search(line):
            continue
        bad = [c.strip() for c in clauses(line) if not clause_ok(c)]
        if bad:
            out.append(f"ERROR {name}:{i}: {bad[0][:140]}")
    return out


MODE_OK = re.compile(r"^(inline-stage|inside lead_writer batch|runs inside the critic run[^\n]*|inline[\w -]*)$", re.I)


def scan_models(path):
    out = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [f"ERROR engine/models.json unreadable: {e}"]
    conc = data.get("concurrency", {})
    if conc.get("max_agents_per_job") != 1:
        out.append(f"ERROR engine/models.json: concurrency.max_agents_per_job must stay 1 (is {conc.get('max_agents_per_job')!r})")
    for role, cfg in data.get("roles", {}).items():
        mode = str(cfg.get("mode", ""))
        if BAD.search(mode) or re.search(r"delegate|spawn|parallel|independent|separate", mode, re.I):
            out.append(f"ERROR engine/models.json: role {role} mode {mode!r} implies delegation")
        elif not MODE_OK.match(mode):
            out.append(f"ERROR engine/models.json: role {role} mode {mode!r} is not an inline stage")

    def walk(v, where):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, f"{where}.{k}")
        elif isinstance(v, str) and (BAD.search(v) or re.search(r"independent from|\bdelegate\b", v, re.I)):
            if not all(clause_ok(c) for c in clauses(v)) or re.search(r"independent from|\bdelegate\b", v, re.I) and not re.search(r"\b(not|never|no)\b", v, re.I):
                out.append(f"ERROR engine/models.json {where}: contradicts the single-agent policy: {v[:100]}")
    walk(data, "$")
    return out


def run(root):
    root = Path(root)
    problems = []
    p = root / "engine" / "models.json"
    if p.exists():
        problems += scan_models(p)
    files = [root / f for f in FILES]
    for g in GLOBS:
        files += sorted(root.glob(g))
    for f in files:
        if f.is_file():
            problems += scan_text(str(f.relative_to(root)), f.read_text(encoding="utf-8"))
    return problems


def main():
    root = Path(__file__).resolve().parent.parent
    if "--root" in sys.argv:
        root = Path(sys.argv[sys.argv.index("--root") + 1])
    problems = run(root)
    for p in problems:
        print(p)
    print("POLICY: OK (single agent, no delegation)" if not problems else f"POLICY: {len(problems)} problem(s)")
    sys.exit(1 if problems else 0)


if __name__ == "__main__":
    main()
