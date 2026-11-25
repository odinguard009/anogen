#!/usr/bin/env python3
"""Single-agent policy check (0 tokens, standard library only).

Usage: policy_check.py [--root PATH]
Exit 1 when the instructions or config say to start sub-agents or delegate.
Checks (ERROR):
  * engine/models.json: no role mode contains 'delegate'; no value mentions spawning.
  * the instruction files below: a line that tells the reader to spawn/start an agent, use delegation or the Agent tool,
    unless the same line forbids it (never / not / no sub-agents / forbidden / without / do not).
Historical records (docs/AUDIT_REPORT.md, PERFORMANCE_BASELINE.md, OPTIMIZATION_*.md, the single-agent audit docs,
novels/*/ops/decisions.md and ops/archive) are not scanned.
"""
import json
import re
import sys
from pathlib import Path

FILES = ["AGENTS.md", "CLAUDE.md", "README.md", "docs/ARCHITECTURE.md", "docs/SINGLE_AGENT_ARCHITECTURE.md"]
GLOBS = ["engine/*.md", "roles/*.md", "templates/**/*.md"]
BAD = re.compile(r"\b(spawn\w*|sub-?agents?|delegat\w*|agent tool|parallel agents?)\b", re.I)
OK = re.compile(r"\b(never|not|no sub-?agents?|forbidden|without|do not|don't|cannot|removed|disabled|zero|0|tidak|jangan|dilarang)\b", re.I)


def scan_text(name, text):
    out = []
    for i, line in enumerate(text.splitlines(), 1):
        if BAD.search(line) and not OK.search(line):
            out.append(f"ERROR {name}:{i}: {line.strip()[:140]}")
    return out


def scan_models(path):
    out = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as e:
        return [f"ERROR engine/models.json unreadable: {e}"]
    for role, cfg in data.get("roles", {}).items():
        if "delegate" in str(cfg.get("mode", "")).lower():
            out.append(f"ERROR engine/models.json: role {role} mode is delegate")

    def walk(v, where):
        if isinstance(v, dict):
            for k, x in v.items():
                walk(x, f"{where}.{k}")
        elif isinstance(v, str) and re.search(r"spawn", v, re.I) and not OK.search(v):
            out.append(f"ERROR engine/models.json {where}: mentions spawning")
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
