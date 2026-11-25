#!/usr/bin/env python3
"""Mechanical pre-pass for the critic (0 tokens). Prints an issue list per chapter.

Usage: prepass.py A-B     (e.g. 6-10)   or   prepass.py N
Checks: sentence length, long sentences, dialogue share, hard words/idioms (tools/hard_words.txt),
long words, phrases (5-word runs) repeated from the previous 10 chapters, tell-words.
The critic should fix what is listed and spend its own effort on story, canon and feeling.
"""
import re
import sys
from collections import Counter

from common import TOOLS, body_text, chapter_path, read, sentences, words

TELLS = ["ears went red", "ears turned red", "went pink", "stared at me as if", "for a long moment",
         "eaten today", "something went across", "let out a breath", "heart hammered", "heart pounded"]


def load_hard():
    plain, rx = [], []
    for ln in read(TOOLS / "hard_words.txt").splitlines():
        ln = ln.strip()
        if not ln or ln.startswith("#"):
            continue
        if ln.startswith("re:"):
            rx.append(re.compile(ln[3:], re.I))
        else:
            plain.append(ln.lower())
    return plain, rx


def grams(text, n=5):
    w = [x.lower() for x in words(text)]
    return Counter(" ".join(w[i:i + n]) for i in range(len(w) - n + 1))


def dialogue_share(text):
    q = re.findall(r"[\"“][^\"”]{1,400}[\"”]", text)
    total = max(len(text), 1)
    return sum(len(x) for x in q) / total


def check(n):
    p = chapter_path(n)
    if not p.exists():
        return [f"chapter {n}: missing"]
    text = body_text(read(p))
    out = []
    sents = [s for s in sentences(text) if s.strip()]
    lens = [len(words(s)) for s in sents]
    avg = sum(lens) / max(len(lens), 1)
    out.append(f"avg sentence {avg:.1f} words; dialogue {dialogue_share(text):.0%}; words {len(words(text))}")
    longs = [s.strip() for s, l in zip(sents, lens) if l > 25]
    if longs:
        out.append(f"{len(longs)} sentence(s) over 25 words, e.g.: {longs[0][:90]}...")
    plain, rx = load_hard()
    low = text.lower()
    hits = sorted({w for w in plain if re.search(r"\b" + re.escape(w) + r"\b", low)})
    hits += sorted({m.group(0) for r in rx for m in r.finditer(text)})
    if hits:
        out.append("hard words/idioms: " + ", ".join(hits[:20]))
    lw = Counter(w.lower() for w in words(text) if len(w) >= 11 and w.isalpha())
    if lw:
        out.append("long words (11+ letters, check they are plain): " + ", ".join(w for w, _ in lw.most_common(12)))
    tells = [t for t in TELLS if t in low]
    if tells:
        out.append("tells present: " + ", ".join(tells))
    cur = grams(text)
    prev = Counter()
    for k in range(max(1, n - 10), n):
        pp = chapter_path(k)
        if pp.exists():
            for g in set(grams(body_text(read(pp)))):
                prev[g] += 1
    rep = [g for g in cur if prev.get(g, 0) >= 2 and len(set(g.split())) >= 4]
    if rep:
        out.append("5-word runs also in 2+ of the last 10 chapters: " + " | ".join(rep[:6]))
    return out


def main():
    a = sys.argv[1] if len(sys.argv) > 1 else ""
    m = re.match(r"^(\d+)(?:-(\d+))?$", a)
    if not m:
        sys.exit("usage: prepass.py A-B | N")
    lo, hi = int(m.group(1)), int(m.group(2) or m.group(1))
    for n in range(lo, hi + 1):
        print(f"## chapter {n}")
        for line in check(n):
            print("- " + line)


if __name__ == "__main__":
    main()
