#!/usr/bin/env python3
"""Mechanical quality check for a chapter (0 tokens). Always exits 0; read the SUMMARY line.

Usage: check_chapter.py chapters/chapter-012.md
"""
import difflib
import re
import sys
from pathlib import Path

from common import (STORY, TOOLS, body_text, canon_tokens, chapter_files, clean_body,
                    read, sentences, setting_int, words)

STOP = set("""a an the and or but if then so of to in on at by for with from as is are was were be been being
it its he she they them his her their i me my we us our you your this that these those there here not no
do did does had has have will would could should can may might shall just very too also than into out up
down over under again once only own same such what which who whom when where why how all any both each few
more most other some about after before above below between through during while until""".split())


def load_banned():
    txt = read(STORY / "style" / "banned.md")
    m = re.search(r"^##\s+Phrases\s*$(.*?)(?=^##\s|\Z)", txt, re.S | re.M)
    lines = m.group(1).splitlines() if m else read(TOOLS / "banned_default.txt").splitlines()
    out = []
    for ln in lines:
        s = ln.strip().lstrip("-* ").strip()
        if not s or s.startswith("#"):
            continue
        mx = 0
        if "|" in s:
            s, opt = s.split("|", 1)
            mm = re.search(r"max\s*=\s*(\d+)", opt)
            mx = int(mm.group(1)) if mm else 0
        out.append((s.strip().lower().replace("’", "'"), mx))
    return out


def content_words(text):
    return [w.lower() for w in words(text)]


def ngrams(seq, n):
    return [tuple(seq[i:i + n]) for i in range(len(seq) - n + 1)]


def content_ngrams(text, n):
    cw = [w for w in content_words(text) if w not in STOP]
    return set(ngrams(cw, n))


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    path = Path(sys.argv[1])
    raw = read(path)
    if not raw.strip():
        print("SUMMARY: FAIL file empty or missing")
        return
    body = clean_body(raw).replace("’", "'").replace("‘", "'")
    wc = len(words(body))
    lo, hi = setting_int("chapter_words_min"), setting_int("chapter_words_max")
    issues, notes = [], []

    if wc < lo or wc > hi:
        issues.append(f"word count {wc} outside {lo}-{hi}")
    if not raw.lstrip().startswith("#"):
        issues.append("missing '# Title' first line")

    low = body.lower()
    for phrase, mx in load_banned():
        c = len(re.findall(r"\b" + re.escape(phrase) + r"\b", low))
        if c > mx:
            issues.append(f"banned phrase '{phrase}' x{c}" + (f" (max {mx})" if mx else ""))

    cw = [w for w in content_words(body) if w not in STOP]
    seen = {}
    for g in ngrams(cw, 5):
        seen[g] = seen.get(g, 0) + 1
    reps = [" ".join(g) for g, c in seen.items() if c > 1]
    if len(reps) > 3:
        issues.append(f"{len(reps)} repeated 5-grams inside chapter, e.g. '{reps[0]}'")

    num = None
    m = re.search(r"chapter-(\d+)", path.name)
    if m:
        num = int(m.group(1))
    prevs = [c for c in chapter_files() if num is None or c[0] < num][-setting_int("repeat_window"):]
    mine6 = content_ngrams(body, 6)
    for pn, pp in prevs:
        ov = mine6 & content_ngrams(clean_body(read(pp)), 6)
        if len(ov) >= 3:
            issues.append(f"{len(ov)} 6-grams shared with chapter {pn}, e.g. '{' '.join(next(iter(ov)))}'")

    ss = sentences(body_text(raw))
    if ss and prevs:
        pss = sentences(body_text(read(prevs[-1][1])))
        if pss:
            for label, a, b in (("opening", ss[0], pss[0]), ("closing", ss[-1], pss[-1])):
                r = difflib.SequenceMatcher(None, a.lower(), b.lower()).ratio()
                if r > 0.6:
                    issues.append(f"{label} too similar to chapter {prevs[-1][0]} ({r:.2f})")

    canon = canon_tokens()
    if canon:
        unk = {}
        for s in sentences(body):
            toks = words(s)
            for w in toks[1:]:
                if w.endswith("'s"):
                    w = w[:-2]
                if w and w[0].isupper() and w.lower() not in canon and w.lower() not in STOP and w not in ("I",) \
                        and not w.lower().startswith("i'"):
                    unk[w] = unk.get(w, 0) + 1
        fresh = [w for w, c in unk.items() if c >= 2]
        if fresh:
            notes.append("capitalized words not in canon_names (new names must be registered): " + ", ".join(sorted(fresh)[:15]))

    paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
    dialog = sum(len(words(p)) for p in paras if p.lstrip().startswith(("\"", "“")))
    share = dialog / wc if wc else 0
    notes.append(f"dialogue share {share:.0%}; paragraphs {len(paras)}; avg {wc // max(len(paras), 1)} words/paragraph")
    if share > 0.65:
        issues.append(f"dialogue share {share:.0%} very high (talking heads)")
    if share < 0.1 and wc > 500:
        notes.append("very little dialogue")
    if share < 0.25 and wc > 500:
        issues.append(f"dialogue share {share:.0%} below 25% (target 25-40%, see CLARITY AND PICTURE)")
    names = set(re.findall(r"(?<=[a-z,;:] )[A-Z][a-z]+(?: [A-Z][a-z]+)*", body))
    if len(names) > 16:
        issues.append(f"{len(names)} distinct capitalized names/terms (max 16, target 12): cut background names, see CLARITY AND PICTURE")
    dash = (raw.count("—") + raw.count("--")) * 1000 / max(wc, 1)
    notes.append(f"em-dashes per 1000 words: {dash:.1f}")
    if dash > 12:
        issues.append(f"em-dash overuse ({dash:.1f}/1000 words)")

    # AI-tell heuristics
    sl = [len(words(x)) for x in sentences(body)]
    if len(sl) > 20:
        mean = sum(sl) / len(sl)
        sd = (sum((x - mean) ** 2 for x in sl) / len(sl)) ** 0.5
        notes.append(f"sentence length mean {mean:.1f}, variation {sd / mean:.2f} (human prose usually > 0.45)")
        if mean < 8.5:
            issues.append(f"sentence length mean {mean:.1f} below 8.5 (target 9-12): join short sentences with and/but/because/when")
        if mean > 13.5:
            issues.append(f"sentence length mean {mean:.1f} above 13.5 (target 9-12): split long sentences")
        short = sum(1 for x in sl if x <= 5) / len(sl)
        if sd / mean < 0.3 and short < 0.05:
            notes.append("rhythm is too even: add fragments and very short sentences")
    contrast = len(re.findall(r"\b(?:wasn't|weren't|isn't|aren't|not)\b[^.!?\n]{0,50}\b(?:but|just)\b", body, re.I)) \
        + len(re.findall(r"(?:wasn't|weren't|isn't|didn't)[^.!?\n]{0,40}[.!?]\s+It (?:was|is)\b", body, re.I))
    if contrast > 3:
        issues.append(f"'not X but Y' contrast pattern x{contrast} (AI tell)")
    starts = {}
    for x in sentences(body):
        w = words(x)
        if w:
            starts[w[0].lower()] = starts.get(w[0].lower(), 0) + 1
    if sl and starts:
        top, c = max(starts.items(), key=lambda kv: kv[1])
        if c / len(sl) > 0.22 and c > 6:
            issues.append(f"{c} sentences start with '{top}' ({c / len(sl):.0%}): vary openers")
    triples = len(re.findall(r"\b\w+, \w+(?: \w+)?, and \w+", body))
    if triples > 6:
        issues.append(f"rule-of-three lists x{triples}: cut most of them")
    ends = [para.strip().split("\n")[-1] for para in re.split(r"\n\s*\n", body) if para.strip()]

    print(f"Words: {wc} (target {lo}-{hi})")
    for n in notes:
        print("note:", n)
    for i in issues:
        print("ISSUE:", i)
    print("SUMMARY:", "OK" if not issues else f"{len(issues)} issue(s) to fix")


if __name__ == "__main__":
    main()
