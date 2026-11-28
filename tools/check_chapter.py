#!/usr/bin/env python3
"""Mechanical quality check for a chapter (0 tokens). Exits 0 unless --strict is given; read the SUMMARY line.

Usage: check_chapter.py chapters/chapter-012.md [--strict]   (--strict: exit 1 when any ISSUE remains)
"""
import difflib
import re
import sys
from pathlib import Path

from common import (STORY, TOOLS, body_text, canon_tokens, chapter_files, clean_body, heading_issue,
                     read, sentences, setting_int, settings, words)

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


ACTION_RE = re.compile(r"\b(struck|swung|cut|drove|caught|stepped|knocked|opened|shut|threw|fell|dropped|pushed|ran|lunged|blocked|parried|shot|slid|turned|hit|kicked|jumped|dodged|slashed|thrust|grabbed|pulled)\b")


def battle_check(num, body):
    """Battle clarity guard (locked setting 18). Returns (warnings, errors). Supporting guard only: it measures
    sentence length and crowding, not whether the fight is clear. The fight card in the outline is the real fix.
    For chapters 1-50 findings are warnings; from chapter 51 on they are errors."""
    if not num:
        return [], []
    outline = "\n".join(read(f) for f in sorted((STORY / "outline").glob("arc-*.md")))
    m = re.search(rf"^Ch {num} \|(.*)$", outline, re.M)
    if not m or "type: battle" not in m.group(1):
        return [], []
    found = []
    ap = [p for p in body.split("\n\n") if len(ACTION_RE.findall(p)) >= 2 and not p.lstrip().startswith(('"', "'"))]
    sl = [len(words(s)) for p in ap for s in sentences(p)]
    if sl:
        mean = sum(sl) / len(sl)
        if mean > 14:
            found.append(f"battle: action sentences average {mean:.1f} words (max 14): one action per short sentence")
        longs = sum(1 for x in sl if x >= 25)
        if longs > 2:
            found.append(f"battle: {longs} action sentences of 25+ words (max 2)")
    doors = len(re.findall(r"\bDoors?\b", body))
    if doors > 6:
        found.append(f"battle: 'Door' appears {doors} times (max 6): say what the reader sees, not the word")
    if "card:" not in m.group(1):
        found.append("battle: the outline line has no 'card:' (fight card: place=...; foe=...; stakes=...; clock=...; beats=bait>ahead>turn>finish>witness; new=one mechanic)")
    return (found, []) if num <= 50 else ([], found)


RIDDLES = ["that is not an answer", "it is the only one i have", "it is the only one", "that is not a reason", "that is not the same", "that is not the test", "that is not a good sum"]


def plain_check(num, body):
    """Plain Reading guard (locked setting 19). Supporting guard only: it finds riddle replies, unlinked surnames and
    long runs of bare dialogue; it cannot tell whether a scene makes sense. WARNING for ch 1-50, ERROR from ch 51."""
    if not num:
        return [], []
    found = []
    low = body.lower()
    rid = sum(low.count(r) for r in RIDDLES)
    if rid > 1:
        found.append(f"plain: {rid} riddle replies ('That is not an answer.' type; max 1): say the meaning in plain words")
    chars = read(STORY / "bible" / "characters.md")
    # Titles and role words are not surnames; a surname is fine once it has been linked
    # to a first name anywhere in the chapter, including inside a letter or a list.
    TITLE_WORDS = {"The", "A", "An", "Lord", "Dame", "Sir", "Lady", "Count", "Prince", "Princess", "King", "Queen", "Master", "Doctor"}
    for m in re.finditer(r"\*\*([A-Z][a-z]+)(?: [A-Z][a-z]+)* ([A-Z][a-z]+)\*\*", chars):
        first, last = m.group(1), m.group(2)
        if first in TITLE_WORDS or last in TITLE_WORDS or first == "Eden" or last == "Okoru":
            continue
        uses = [x.start() for x in re.finditer(rf"\b{last}\b", body)]
        if not uses:
            continue
        linked = re.search(rf"\b{first}(?: [A-Z][a-z]+)* {last}\b", body)
        if not linked:
            found.append(f"plain: surname '{last}' is never linked to '{first}' in this chapter: write '{first} {last}' once")
    # Readability grade (Flesch-Kincaid, approximate). For a low-level learner target, grade 6 is the ceiling.
    def _syllables(w):
        w = w.lower().strip(".,;:!?\"'()-")
        if not w:
            return 0
        groups = re.findall(r"[aeiouy]+", w)
        n = len(groups)
        if w.endswith("e") and n > 1:
            n -= 1
        return max(1, n)
    _words = words(body)
    _sents = sentences(body)
    if _words and _sents:
        _syll = sum(_syllables(w) for w in _words)
        _grade = 0.39 * (len(_words) / len(_sents)) + 11.8 * (_syll / len(_words)) - 15.59
        if _grade > 6:
            msg = f"plain: reading grade {_grade:.1f} is above 6 (low-level learner target): shorten sentences and use commoner words"
            found.append(msg)
    run = best = 0
    for para in body.split("\n\n"):
        if para.lstrip().startswith('"') and para.count('"') == 2 and len(para.split()) < 14:
            run += 1; best = max(best, run)
        else:
            run = 0
    if best >= 8:
        found.append(f"plain: a run of {best} bare short dialogue lines with no action or narration (max 7): show who speaks and what is meant")
    return (found, []) if num <= 50 else ([], found)



def audience_check(num, body):
    """Owner order 2026-11-28: plain language for a 15-year-old non-native reader.

    Returns (warnings, errors). While brief.md plain_language_strict is false the
    findings are WARNINGS, so the old chapters are not blocked before the rewrite.
    When the owner flips it to true the same findings become ERRORS.
    """
    conf = settings()
    strict = str(conf.get("plain_language_strict", "false")).strip().lower() in ("1", "true", "yes")
    low = body.lower()
    found = []

    asif = len(re.findall(r"\bas if\b", low))
    if asif:
        found.append(f"audience: 'as if' x{asif} (target 0): say what you see")
    likea = len(re.findall(r"\blike a\b", low))
    if likea > 1:
        found.append(f"audience: 'like a' x{likea} (max 1): use one plain comparison or none")

    caps = len(re.findall(r"\bDoors?\b", body))
    labels = len(re.findall(r"\*\*\[Door\]\*\*", body))
    if caps - labels > 0:
        found.append(f"audience: capital Door x{caps - labels} in narration: write 'a black opening' for the power")

    knock_magic = len(re.findall(r"\bknocked?\b[^.!?\n]{0,45}\bshadow|\bshadow[^.!?\n]{0,45}\bknocked?\b", low))
    if knock_magic:
        found.append(f"audience: 'knock' used for the power x{knock_magic}: write 'tap the shadow'")

    bare_dust = len(re.findall(r"(?<!grey )(?<!stone )\bdust\b", low))
    if bare_dust:
        found.append(f"audience: bare 'dust' x{bare_dust}: say grey dust, dirt or stone dust")
    ash_hits = len(re.findall(r"\bash\b", low))
    if ash_hits and re.search(r"\b(veil|husk|ember|enemy|body)\b[^.!?\n]{0,40}\bash\b", low):
        found.append("audience: 'ash' used for remains: write grey dust")

    for m in re.finditer(r"\bLance (Nine|One)\b", body):
        near = body[max(0, m.start() - 90): m.end() + 90].lower()
        if "group" not in near:
            found.append("audience: 'Lance Nine/One' without a plain 'group' gloss nearby: say 'a group of five students'")
            break

    mood = len(re.findall(r"\bwent quiet\b|\bwent still\b|\bthe air was thick\b|\bfrosted over\b|\bcold air\b|\bshadow moved\b", low))
    if mood > 2:
        found.append(f"audience: mood shortcuts x{mood}: say what people see, do or say")

    return ([], found) if strict else (found, [])


def main():
    strict = True  # LOCKED: always strict (owner order 2026-11-27)
    args = [x for x in sys.argv[1:] if x != "--strict"]
    if len(args) != 1:
        sys.exit(__doc__)
    path = Path(args[0])
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
    mm = re.match(r"chapter-(\d+)\.md$", path.name)
    hi_ = heading_issue(raw, int(mm.group(1)) if mm else None)
    if hi_:
        issues.append(hi_)

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
        notes.append(f"WARNING dialogue share {share:.0%} below the 25-40% guide (warning only, owner order 2026-11-26): do not pad; add a real exchange only if the scene needs it")
    names = set(re.findall(r"(?<=[a-z,;:] )[A-Z][a-z]+(?: [A-Z][a-z]+)*", body))
    if len(names) > 16:
        issues.append(f"{len(names)} distinct capitalized names/terms (max 16, target 12): cut background names, see CLARITY AND PICTURE")
    glued = re.findall(r"\b[a-z]{2,}[A-Z][a-z]+\b|\b[a-z]{3,}\d+\b", re.sub(r"\*\*\[[^\]]*\]\*\*", "", body))
    if glued:
        issues.append("glued words or typos (missing space?): " + ", ".join(sorted(set(glued))[:6]))
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

    bw, be = battle_check(int(mm.group(1)) if mm else None, body)
    pw, pe = plain_check(int(mm.group(1)) if mm else None, body)
    aw, ae = audience_check(int(mm.group(1)) if mm else None, body)
    notes += ["WARNING " + x for x in bw + pw + aw]
    issues += be + pe + ae
    print(f"Words: {wc} (target {lo}-{hi})")
    for n in notes:
        print("note:", n)
    for i in issues:
        print("ISSUE:", i)
    print("SUMMARY:", "OK" if not issues else f"{len(issues)} issue(s) to fix")
    if strict and issues:
        sys.exit(1)


if __name__ == "__main__":
    main()
