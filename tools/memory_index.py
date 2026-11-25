#!/usr/bin/env python3
"""Story-memory index: SQLite + FTS5 built FROM the markdown files (0 tokens, standard library only).

The markdown stays the source of truth. The index (ops/memory.sqlite, gitignored, rebuildable any time) only helps retrieval.
Every row carries provenance (source = file:line) and the hash of its source file, so a changed file is re-indexed alone.

Usage:
  memory_index.py update                      index files whose hash changed (all on first run); prints counts
  memory_index.py rebuild                     drop and rebuild everything
  memory_index.py query [--text "..."] [--chars "Eden,Lysette"] [--chapter N] [--near K] [--arc K] [--type T] [--status S]
                        [--limit 12]          rows with provenance (type, chapter, arc, characters, status, source)
  memory_index.py stats                       rows per type
  memory_index.py arc-digest K [--write]      rolling digest of an arc: first sentence of each chapter summary (deterministic)
Row fields: id, type, chapter, arc, characters, summary, importance, status, source, last_updated, confidence,
related_events, supersedes. confidence is always 'derived' (a line parsed from markdown, never a judgement); importance is
'major' only when the line itself says big/major; supersedes is set only when the line says SUPERSEDED.
Types: chapter (summaries incl. archive), thread, twist, debt, secret, event (timeline), character, arc_outline.
"""
import argparse
import datetime
import hashlib
import json
import re
import sqlite3
import sys

from common import OPS, STORY, REPO, canon_names, chapter_files, load_json, read

DB = OPS / "memory.sqlite"
SOURCES = [("thread", "bible/threads.md"), ("debt", "bible/debts.md"), ("secret", "bible/secrets.md"),
           ("event", "bible/timeline.md"), ("character", "bible/characters.md")]
CH_RE = re.compile(r"\bch(?:apters?|\.)?\s*(\d+)", re.I)


def connect(path=None):
    path = path or DB
    try:
        con = sqlite3.connect(str(path))
        con.execute("PRAGMA journal_mode=WAL")
        if con.execute("PRAGMA quick_check").fetchone()[0] != "ok":
            raise sqlite3.DatabaseError("quick_check failed")
    except sqlite3.DatabaseError:
        # a damaged index is only a cache: set it aside and rebuild from the markdown (never lose the markdown)
        try:
            con.close()
        except Exception:
            pass
        import os
        os.replace(str(path), str(path) + ".corrupt")
        con = sqlite3.connect(str(path))
    con.executescript("""
    CREATE TABLE IF NOT EXISTS mem(id TEXT PRIMARY KEY, type TEXT, chapter INTEGER, arc INTEGER, characters TEXT, summary TEXT,
        importance TEXT, status TEXT, source TEXT, source_file TEXT, last_updated TEXT, confidence TEXT, related_events TEXT, supersedes TEXT);
    CREATE TABLE IF NOT EXISTS files(path TEXT PRIMARY KEY, hash TEXT, rows INTEGER);
    CREATE VIRTUAL TABLE IF NOT EXISTS mem_fts USING fts5(summary, characters, content='mem', content_rowid='rowid');
    """)
    return con


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]


def arc_of(n, arcs):
    if n is None:
        return None
    for k, a in arcs.items():
        if isinstance(a, dict) and a.get("start") is not None and a["start"] <= n <= (a.get("end") or 10**9):
            return int(k)
    return None


def names_in(text, names):
    low = text.lower()
    return sorted(n for n in names if len(n) >= 3 and re.search(r"\b" + re.escape(n.lower()) + r"\b", low))


def parse_file(rel, typ, names, arcs):
    """Yield dict rows for one markdown file."""
    path = STORY / rel
    text = read(path)
    if not text:
        return []
    rows = []
    for i, ln in enumerate(text.splitlines(), 1):
        s = ln.strip()
        if len(s) < 12 or s.startswith("#"):
            continue
        if not re.match(r"^([-*]|\d+\.|\|)", s):
            continue
        cm = [int(x) for x in CH_RE.findall(s)]
        ch = cm[0] if cm else None
        if typ == "thread" and s.count("|") >= 2 and re.match(r"^\d+\.", s):
            raised = re.findall(r"\d+", s.split("|")[1])  # ledger row: 'n. question | raised | feeds | payoff | check'
            ch = int(raised[0]) if raised else ch
        status = (re.match(r".*?\[(open|paid|done|closed)\]", s) or [None, ""])[1] or "unknown"
        rows.append(dict(type=typ, chapter=ch, text=s, source=f"story/{rel}:{i}", status=status))
    return rows


def parse_summaries(names):
    """Chapter summaries from the live file and the archive files."""
    files = [STORY / "bible" / "summaries.md"] + sorted((STORY / "bible" / "archive").glob("summaries-*.md"))
    rows = []
    for f in files:
        rel = f.relative_to(STORY).as_posix()
        text = read(f)
        for m in re.finditer(r"(?ms)^#{1,3}\s*Ch\.?\s*(\d+)[^\n]*\n(.*?)(?=^#{1,3}\s*Ch\.?\s*\d+|\Z)", text):
            line = text[:m.start()].count("\n") + 1
            rows.append(dict(type="chapter", chapter=int(m.group(1)), text=m.group(2).strip(), source=f"story/{rel}:{line}", status="written"))
    return rows


def parse_outline():
    rows = []
    od = STORY / "outline"
    for f in sorted(od.glob("arc-*.md")) if od.is_dir() else []:
        rel = f.relative_to(STORY).as_posix()
        for i, ln in enumerate(read(f).splitlines(), 1):
            m = re.match(r"^\s*(?:[-*]\s*)?(?:\*\*)?Ch\.?\s*(\d+)\b(.*)", ln)
            if m and len(ln.strip()) > 12:
                rows.append(dict(type="arc_outline", chapter=int(m.group(1)), text=ln.strip(), source=f"story/{rel}:{i}", status="planned"))
    return rows


def twist_rows():
    rows = []
    for f in sorted((STORY / "bible").glob("twists-*.md")):
        rel = f.relative_to(STORY).as_posix()
        for i, ln in enumerate(read(f).splitlines(), 1):
            s = ln.strip()
            if re.match(r"^\d+\.", s) and len(s) > 12:
                pl = re.search(r"plants?:\s*([\d,\s\-]+)", s)
                ch = int(re.findall(r"\d+", pl.group(1))[0]) if pl and re.findall(r"\d+", pl.group(1)) else None
                rows.append(dict(type="twist", chapter=ch, text=s, source=f"story/{rel}:{i}", status="planned"))
    return rows


def file_groups():
    """[(source_key, files_for_hash, rows_fn)] so one changed file re-indexes alone."""
    names = canon_names()
    arcs = load_json(OPS / "engine.json", {}).get("arcs", {})
    groups = [(rel, [STORY / rel], (lambda rel=rel, typ=typ: parse_file(rel, typ, names, arcs))) for typ, rel in SOURCES]
    groups.append(("summaries", [STORY / "bible" / "summaries.md"] + sorted((STORY / "bible" / "archive").glob("summaries-*.md")), lambda: parse_summaries(names)))
    groups.append(("outline", sorted((STORY / "outline").glob("arc-*.md")), parse_outline))
    groups.append(("twists", sorted((STORY / "bible").glob("twists-*.md")), twist_rows))
    return groups, names, arcs


def finish(row, names, arcs, stamp):
    t = row["text"]
    ch = row["chapter"]
    row["characters"] = ", ".join(names_in(t, names))
    row["arc"] = arc_of(ch, arcs)
    row["importance"] = "major" if re.search(r"\((?:big|major)\b|\bbig\)|\bmajor\b", t, re.I) else "normal"
    row["supersedes"] = "yes" if "SUPERSEDED" in t else ""
    if "SUPERSEDED" in t:
        row["status"] = "superseded"
    row["related_events"] = ",".join(str(x) for x in sorted({int(x) for x in CH_RE.findall(t)} - {ch})[:12])
    row["id"] = sha(row["type"] + "|" + re.sub(r"\s+", " ", t.lower()))
    row["last_updated"] = stamp
    row["confidence"] = "derived"
    return row


def update(rebuild=False):
    con = connect()
    if rebuild:
        con.executescript("DELETE FROM mem; DELETE FROM files; INSERT INTO mem_fts(mem_fts) VALUES('delete-all');")
    groups, names, arcs = file_groups()
    stamp = datetime.date.today().isoformat()
    changed, dups = [], 0
    for key, files, fn in groups:
        h = sha("".join(f.name + read(f) for f in files))
        old = con.execute("SELECT hash FROM files WHERE path=?", (key,)).fetchone()
        if old and old[0] == h:
            continue
        con.execute("DELETE FROM mem WHERE source_file=?", (key,))
        n = 0
        for row in fn():
            row = finish(row, names, arcs, stamp)
            try:
                con.execute("INSERT INTO mem(id,type,chapter,arc,characters,summary,importance,status,source,source_file,last_updated,confidence,related_events,supersedes) "
                            "VALUES(?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (row["id"], row["type"], row["chapter"], row["arc"], row["characters"], row["text"],
                                                                     row["importance"], row["status"], row["source"], key, stamp, row["confidence"],
                                                                     row["related_events"], row["supersedes"]))
                n += 1
            except sqlite3.IntegrityError:
                dups += 1  # same type and text already indexed: memory deduplication
        con.execute("INSERT OR REPLACE INTO files(path,hash,rows) VALUES(?,?,?)", (key, h, n))
        changed.append(f"{key}:{n}")
    con.execute("INSERT INTO mem_fts(mem_fts) VALUES('rebuild')")
    con.commit()
    total = con.execute("SELECT COUNT(*) FROM mem").fetchone()[0]
    con.close()
    return changed, dups, total


def fts_query(text):
    toks = re.findall(r"[A-Za-z0-9']{2,}", text)
    return " OR ".join('"' + t.replace('"', '') + '"' for t in toks)


def query(text="", chars="", chapter=None, near=0, arc=None, typ=None, status=None, limit=12):
    con = connect()
    sql, args = "SELECT m.type,m.chapter,m.arc,m.characters,m.status,m.importance,m.source,m.summary FROM mem m", []
    where = []
    if text.strip():
        sql += " JOIN mem_fts f ON f.rowid=m.rowid"
        where.append("mem_fts MATCH ?"); args.append(fts_query(text))
    for c in [c.strip() for c in chars.split(",") if c.strip()]:
        where.append("m.characters LIKE ?"); args.append(f"%{c}%")
    if chapter is not None:
        where.append("m.chapter BETWEEN ? AND ?"); args += [chapter - near, chapter + near]
    if arc is not None:
        where.append("m.arc=?"); args.append(arc)
    if typ:
        where.append("m.type=?"); args.append(typ)
    if status:
        where.append("m.status=?"); args.append(status)
    if where:
        sql += " WHERE " + " AND ".join(where)
    if text.strip():
        # relevance first (FTS5 bm25); importance and chapter only break ties. tools/bench_memory.py: chapter-order ranking
        # found the labeled chapter at rank 1 for 9% of queries, bm25 for 100% (golden5 fixture, 23 queries).
        sql += " ORDER BY bm25(mem_fts), (m.importance='major') DESC, m.chapter LIMIT ?"
    else:
        sql += " ORDER BY (m.importance='major') DESC, m.chapter LIMIT ?"
    args.append(limit)
    rows = con.execute(sql, args).fetchall()
    con.close()
    return rows


def first_sentence(t, n=170):
    s = re.split(r"(?<=[.!?])\s", t.strip(), maxsplit=1)[0]
    return s if len(s) <= n else s[:n].rsplit(" ", 1)[0] + "..."


def arc_digest(k):
    arcs = load_json(OPS / "engine.json", {}).get("arcs", {})
    a = arcs.get(str(k))
    if not a:
        return None
    con = connect()
    rows = con.execute("SELECT chapter,summary,source FROM mem WHERE type='chapter' AND chapter BETWEEN ? AND ? ORDER BY chapter",
                       (a["start"], a.get("end") or 10**9)).fetchall()
    con.close()
    out = [f"# Arc {k} digest (DERIVED from chapter summaries; first sentence each; rebuild with memory_index.py arc-digest {k} --write)"]
    out += [f"- Ch {c}: {first_sentence(s)} [{src}]" for c, s, src in rows]
    return "\n".join(out) + "\n"


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("update"); sub.add_parser("rebuild"); sub.add_parser("stats")
    q = sub.add_parser("query")
    q.add_argument("--text", default=""); q.add_argument("--chars", default=""); q.add_argument("--chapter", type=int)
    q.add_argument("--near", type=int, default=0); q.add_argument("--arc", type=int); q.add_argument("--type"); q.add_argument("--status")
    q.add_argument("--limit", type=int, default=12)
    d = sub.add_parser("arc-digest"); d.add_argument("arc", type=int); d.add_argument("--write", action="store_true")
    a = ap.parse_args()
    if a.cmd in ("update", "rebuild"):
        changed, dups, total = update(rebuild=(a.cmd == "rebuild"))
        print(f"indexed: {', '.join(changed) or 'nothing changed'}; duplicates skipped: {dups}; rows in index: {total}")
    elif a.cmd == "stats":
        con = connect()
        for t, c in con.execute("SELECT type,COUNT(*) FROM mem GROUP BY type ORDER BY 2 DESC"):
            print(f"{t}: {c}")
    elif a.cmd == "query":
        update()
        rows = query(a.text, a.chars, a.chapter, a.near, a.arc, a.type, a.status, a.limit)
        for t, ch, arc, chars, st, imp, src, s in rows:
            print(f"- [{src}] {t} ch {ch} arc {arc} {st}{' MAJOR' if imp == 'major' else ''} ({chars}): {s[:220]}")
        if not rows:
            print("(no match)")
    elif a.cmd == "arc-digest":
        update()
        out = arc_digest(a.arc)
        if out is None:
            sys.exit(f"unknown arc {a.arc}")
        if a.write:
            p = STORY / "bible" / f"arc-digest-{a.arc}.md"
            p.write_text(out, encoding="utf-8")
            print(f"wrote {p}")
        else:
            print(out)


if __name__ == "__main__":
    main()
