#!/usr/bin/env python3
"""Labeled retrieval benchmark for tools/memory_index.py (0 tokens, standard library only).

Usage: bench_memory.py [--root DIR] [--k 3]
Runs tests/fixtures/retrieval_bench.json against a COPY of the frozen golden5 fixture (default) and compares ranking
variants on the same labeled queries: hit@1, hit@k, MRR over chapter-summary rows. Labels were written by the orchestrator
from the fixture text and are NOT owner-verified; the numbers measure ranking on this one fixture only.
Variants: 'production' (memory_index.query as shipped), 'chapter-order' (importance, then chapter; the PR #7 behaviour),
'bm25' (FTS5 bm25 rank, AND-less OR query). Exit 0 always; the test suite asserts on the numbers.
"""
import argparse
import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
FIX = TOOLS.parent / "tests" / "fixtures"


def run_variants(root, k):
    os.environ["ANOGEN_ROOT"] = str(root)
    sys.path.insert(0, str(TOOLS))
    import memory_index as mi
    mi.update(rebuild=True)
    queries = json.loads((FIX / "retrieval_bench.json").read_text())["queries"]
    con = mi.connect()

    def sql_variant(order, text):
        sql = ("SELECT m.type,m.chapter FROM mem m JOIN mem_fts f ON f.rowid=m.rowid WHERE mem_fts MATCH ? AND m.type='chapter' "
               "ORDER BY " + order + " LIMIT 50")
        return [r[1] for r in con.execute(sql, (mi.fts_query(text),)).fetchall()]

    def prod(text):
        return [r[1] for r in mi.query(text=text, typ="chapter", limit=50)]

    variants = {
        "production": prod,
        "chapter-order": lambda t: sql_variant("(m.importance='major') DESC, m.chapter", t),
        "bm25": lambda t: sql_variant("bm25(mem_fts)", t),
    }
    res = {}
    for name, fn in variants.items():
        h1 = hk = 0
        rr = 0.0
        for q in queries:
            got = fn(q["q"])
            rel = set(q["relevant"])
            rank = next((i for i, c in enumerate(got, 1) if c in rel), None)
            h1 += rank == 1
            hk += rank is not None and rank <= k
            rr += 1.0 / rank if rank else 0.0
        n = len(queries)
        res[name] = {"queries": n, "hit@1": round(h1 / n, 3), f"hit@{k}": round(hk / n, 3), "mrr": round(rr / n, 3)}
    con.close()
    return res


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--root")
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--inner", action="store_true")
    a = ap.parse_args()
    if a.inner:
        print(json.dumps(run_variants(Path(a.root), a.k)))
        return
    tmp = Path(tempfile.mkdtemp())
    try:
        root = tmp / "root"
        shutil.copytree(FIX / "golden5" / "root", root)
        out = subprocess.run([sys.executable, str(Path(__file__)), "--inner", "--root", str(root), "--k", str(a.k)],
                             capture_output=True, text=True, env={**os.environ, "ANOGEN_ROOT": str(root)})
        if out.returncode:
            print(out.stderr or out.stdout)
            sys.exit(1)
        res = json.loads(out.stdout.strip().splitlines()[-1])
    finally:
        shutil.rmtree(tmp, ignore_errors=True)
    print(f"Retrieval benchmark (golden5 fixture, labels by orchestrator, not owner-verified; k={a.k})")
    for name, r in res.items():
        print(f"- {name:14} hit@1 {r['hit@1']:.3f}  hit@{a.k} {r['hit@'+str(a.k)]:.3f}  MRR {r['mrr']:.3f}  (n={r['queries']})")


if __name__ == "__main__":
    main()
