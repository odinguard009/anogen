#!/usr/bin/env python3
"""Assemble the whole context for ONE chapter in a single call (0 tokens to build).

Usage: context_pack.py [--chapter N] [--extra world,armor] [--peek] [--part full|static|delta] [--no-tail]
                       [--incremental [--batch-start]] [--retrieve]
--part static: style, banned, series, premise, characters, extras (read ONCE per batch).
--part delta : state, precheck, inbox, outline, pacing, debts, secrets, summaries, previous tail (per chapter).
--incremental (delta only): for State, Debts and Secrets send only the exact line changes since the previous chapter's
  pack of the SAME batch (or a one-line "unchanged" stub). The first chapter of a batch MUST pass --batch-start (full text,
  starts the cache). Any doubt (no cache, wrong chapter, changed static sources, cache older than 3 h, diff larger than 60%
  of the file) falls back to the full text. Running without --incremental always gives the full pack.
--retrieve: add "Retrieved memory" (tools/memory_retrieve.py): threads, twists, timeline and older summaries that match the
  names and chapter numbers of the outline lines, each with file:line provenance.
Default full = both. "characters" is always in the pack; do not pass it in --extra.
Prints a compact pack; each section is capped and the total is capped by
the setting context_pack_max_chars.
"""
import argparse
import difflib
import hashlib
import re
import sys
import time

from common import OPS, STORY, body_text, chapter_path, load_json, read, save_json, setting_int
import engine_state
import precheck

OUTLINE_RE = re.compile(r"^\s*(?:[-*]\s*)?(?:\*\*)?Ch\.?\s*(\d+)\b")
PACING_RE = re.compile(r"^\s*(?:[-*]\s*)?Ch\.?\s*(\d+)\s*:")


TRUNCATED = []  # (section title, chars lost): any entry makes the tool exit 4 (never cut silently)


def cap(text, n, title="?"):
    text = text.strip()
    if len(text) <= n:
        return text
    TRUNCATED.append((title, len(text) - n))
    return text[:n].rstrip() + f"\n[...TRUNCATED: {len(text) - n} chars of '{title}' lost; raise the cap or shorten the source file]"


CACHE = OPS / "ctx-cache.json"   # local only (gitignored): what the previous chapter's pack contained
DIFFABLE = ("State", "Debts (open promises)", "Secrets")
CACHE_TTL_SECONDS = 3 * 3600
STATIC_SOURCES = [("style", "profile.md"), ("style", "banned.md"), ("outline", "series.md"),
                  ("bible", "characters.md"), ("bible", "premise.md")]


def sha(text):
    return hashlib.sha256(text.encode("utf-8")).hexdigest()[:12]


def static_hash():
    return sha("\x00".join(read(STORY / d / f) for d, f in STATIC_SOURCES))


def make_diff(old, new):
    # both sides end with a newline so a changed LAST line can never be glued to the next diff line
    return "".join(difflib.unified_diff((old.rstrip("\n") + "\n").splitlines(True), (new.rstrip("\n") + "\n").splitlines(True),
                                        "previous pack", "now", n=0))


def apply_diff(old, diff):
    """Rebuild `new` from `old` and a make_diff() result (used by the fixture test to prove nothing is lost)."""
    lines, out, i = (old.rstrip("\n") + "\n").splitlines(True), [], 0
    for h in re.finditer(r"(?m)^@@ -(\d+)(?:,(\d+))? \+(\d+)(?:,(\d+))? @@\n((?:[-+\\].*\n?)*)", diff):
        start = int(h.group(1)); cnt = int(h.group(2) if h.group(2) is not None else 1)
        pos = start - 1 if cnt else start
        out += lines[i:pos]
        i = pos + cnt
        out += [ln[1:] for ln in h.group(5).splitlines(True) if ln.startswith("+")]
    out += lines[i:]
    return "".join(out)


def outline_lines(n, count=3):
    files = []
    od = STORY / "outline"
    if od.is_dir():
        files = sorted(od.glob("arc-*.md")) + sorted(od.glob("volume*.md"))
    found = {}
    for f in files:
        for line in read(f).splitlines():
            m = OUTLINE_RE.match(line)
            if m:
                k = int(m.group(1))
                if n <= k < n + count and k not in found:
                    found[k] = line.strip()
    return [found[k] for k in sorted(found)]


def pacing_lines(n):
    out = []
    for line in read(STORY / "outline" / "pacing.md").splitlines():
        m = PACING_RE.match(line)
        if m and n - 6 <= int(m.group(1)) <= n + 3:
            out.append(line.strip())
    return out


def epigraph_for(n):
    for line in read(STORY / "outline" / "epigraphs.md").splitlines():
        m = re.match(r"^\s*(?:[-*]\s*)?Ch\.?\s*(\d+)\s*\|\s*(.+)$", line)
        if m and int(m.group(1)) == n:
            return m.group(2).strip()
    return ""


def last_summaries(n, k=3):
    txt = read(STORY / "bible" / "summaries.md")
    items = re.split(r"(?m)^(?=#{1,3}\s*Ch\.?\s*\d+|\-\s*Ch\.?\s*\d+)", txt)
    keep = []
    for it in items:
        m = re.match(r"\W*Ch\.?\s*(\d+)", it)
        if m and int(m.group(1)) < n:
            keep.append((int(m.group(1)), it.strip()))
    keep.sort()
    return "\n".join(t for _, t in keep[-k:])


def prev_tail(n, nwords=300):
    p = chapter_path(n - 1)
    if not p.exists():
        return ""
    w = body_text(read(p)).split()
    return " ".join(w[-nwords:])


def load_cache(n, batch_start):
    """(cache, reason). cache is usable only for the chapter right after the one it recorded (same batch)."""
    if batch_start:
        return None, "FULL: batch start (baseline for the next chapters of this batch)"
    try:
        c = load_json(CACHE, None)
    except SystemExit:
        return None, "FULL: cache unreadable"
    if not c:
        return None, "FULL: no cache (first chapter of a batch needs --batch-start)"
    if c.get("base_chapter") != n - 1:
        return None, f"FULL: cache is for chapter {c.get('base_chapter')}, this is chapter {n}"
    if time.time() - c.get("ts", 0) > CACHE_TTL_SECONDS:
        return None, "FULL: cache older than 3 hours"
    if c.get("static_hash") != static_hash():
        return None, "FULL: static sources (style, banned, series, characters, premise) changed: re-run --part static"
    return c, f"DIFF vs the chapter {n - 1} pack"


def build(chapter=None, extra=(), peek=False, part="full", no_tail=False, incremental=False, batch_start=False, retrieve=False):
    n = chapter or engine_state.compute_next()["next_chapter"]
    nxt = engine_state.compute_next()
    sections = []
    delivered = {}
    cache, mode = (load_cache(n, batch_start) if incremental and part in ("full", "delta") else (None, ""))
    prev_ch = (cache or {}).get("base_chapter")

    def add(title, body, limit, diffable=False):
        if not (body and body.strip()):
            return
        if diffable and incremental:
            cur = body.strip()
            delivered[title] = cur
            prev = (cache or {}).get("sections", {}).get(title)
            if prev is not None:
                if prev == cur:
                    sections.append(f"## {title}\n[unchanged since the chapter {prev_ch} pack; sha {sha(prev)}]")
                    return
                d = make_diff(prev, cur)
                if len(d) < 0.6 * len(cur):
                    sections.append(f"## {title} [CHANGED since the chapter {prev_ch} pack: exact line changes ('-' removed, '+' added); all other lines are as in that pack]\n{d.rstrip()}")
                    return
        sections.append(f"## {title}\n{cap(body, limit, title)}")

    want_s = part in ("full", "static")
    want_d = part in ("full", "delta")
    if want_d:
        add("Engine state", f"next_chapter: {nxt['next_chapter']}\nbatch: {nxt['batch']}\ncontinue: {nxt['continue']} ({nxt['reason']})"
            + (f"\ncontext mode: {mode}. For State, Debts and Secrets a DIFF or 'unchanged' line means: the full text is in the earlier pack in your conversation plus these changes. If you are unsure, run context_pack.py --part delta (no --incremental) for the full text." if mode.startswith("DIFF") else (f"\ncontext mode: {mode}" if mode else "")), 1200)
        sections.append(precheck.build(n, peek=peek))
        add("Idea inbox", "\n".join(f"- {i}" for i in __import__('inbox').unprocessed_ideas()), 3000)
    if want_s:
        add("Style profile", read(STORY / "style" / "profile.md"), 20000)
        add("Banned phrases", read(STORY / "style" / "banned.md"), 2500)
    if want_d:
        ep = epigraph_for(n)
        if ep:
            add("Epigraph for this chapter (put it right under the title as a '> ' blockquote, one or two lines)", ep, 500)
    if want_s:
        add("Series arc", read(STORY / "outline" / "series.md"), 3000)
    if want_d:
        ol = outline_lines(n)
        add("Outline for this and next chapters", "\n".join(ol) if ol else "NO OUTLINE for this chapter: Development Editor must plan the arc first.", 2500)
        add("Pacing (recent and upcoming)", "\n".join(pacing_lines(n)), 800)
        if retrieve:
            import memory_retrieve
            add("Retrieved memory (deterministic: matches the outline names and chapter numbers; source file:line shown; the chapters are the source of truth)", memory_retrieve.retrieve(n), 4200)
        add("State", read(STORY / "bible" / "state.md"), 3500, diffable=True)
        debts = [ln for ln in read(STORY / "bible" / "debts.md").splitlines() if "[open]" in ln]
        add("Debts (open promises)", "\n".join(debts), 3000, diffable=True)
        sec = read(STORY / "bible" / "secrets.md").strip()
        add("Secrets", sec if len(sec) <= 2500 else "[older entries omitted]\n" + sec[-2500:], 2600, diffable=True)
    if want_s:
        add("Characters", read(STORY / "bible" / "characters.md"), 3000)
    if want_d:
        add("Last summaries", last_summaries(n), 3500)
        if not no_tail:
            add("End of previous chapter (continue from here, do not repeat it)", prev_tail(n), 2200)
    if want_s:
        add("Premise", read(STORY / "bible" / "premise.md"), 2500)
        seen = {"characters", "premise"}
        for e in extra:
            if e in seen:
                continue
            seen.add(e)
            add(f"Extra: {e}", read(STORY / "bible" / f"{e}.md"), 9500)

    out = "\n\n".join(sections)
    limit = setting_int("context_pack_max_chars")
    if len(out) > limit:
        # never cut silently: cut only the tail and name what was lost
        cut = out[limit:]
        lost = [ln[3:].strip() for ln in cut.splitlines() if ln.startswith("## ")]
        TRUNCATED.append(("whole pack (" + (", ".join(lost) or "tail of the last section") + ")", len(cut)))
        out = out[:limit].rstrip() + "\n[...PACK TRUNCATED at context_pack_max_chars; lost sections: " + (", ".join(lost) or "tail of the last section") + "]"
    if incremental and not peek and part in ("full", "delta") and not TRUNCATED:
        save_json(CACHE, {"base_chapter": n, "ts": time.time(), "static_hash": static_hash(), "sections": delivered})
    if TRUNCATED:
        out += "\n[PACK WARNING: truncated sections: " + ", ".join(f"{s} (-{k} chars)" for s, k in TRUNCATED) + "]"
    return out


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--chapter", type=int, default=None)
    ap.add_argument("--extra", default="")
    ap.add_argument("--peek", action="store_true")
    ap.add_argument("--part", choices=["full", "static", "delta"], default="full")
    ap.add_argument("--no-tail", action="store_true")
    ap.add_argument("--incremental", action="store_true")
    ap.add_argument("--batch-start", action="store_true")
    ap.add_argument("--retrieve", action="store_true")
    a = ap.parse_args()
    extra = [e.strip() for e in a.extra.split(",") if e.strip()]
    print(build(a.chapter, extra, a.peek, a.part, a.no_tail, a.incremental, a.batch_start, a.retrieve))
    if TRUNCATED:
        print("ERROR: context pack was truncated (see PACK WARNING); fix the caps before writing.", file=sys.stderr)
        sys.exit(4)


if __name__ == "__main__":
    main()
