"""Shared helpers for the Anogen tools. Standard library only. No AI calls."""
import json
import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("ANOGEN_ROOT") or Path(__file__).resolve().parent.parent)
STORY = ROOT / "story"
CHAPTERS = ROOT / "chapters"
OPS = ROOT / "ops"
OUT = ROOT / "out"
TOOLS = Path(__file__).resolve().parent

DEFAULTS = {
    "title": "Untitled Serial",
    "author": "Anogen",
    "chapter_words_min": "1800",
    "chapter_words_max": "2500",
    "context_pack_max_chars": "40000",
    "repeat_window": "5",
    "arc_default_max": "50",
}

_CH_RE = re.compile(r"^chapter-(\d+)\.md$")
WORD_RE = re.compile(r"[A-Za-z0-9À-ɏ]+(?:['’\-][A-Za-z0-9À-ɏ]+)*")
SENT_RE = re.compile(r"(?<=[.!?…])[\"”’')\]]*\s+")
_BREAK_RE = re.compile(r"^\s*(?:(?:\*\s*){3,}|-{3,}|_{3,})\s*$")


def read(path, default=""):
    try:
        return Path(path).read_text(encoding="utf-8")
    except (FileNotFoundError, IsADirectoryError):
        return default


def write(path, text):
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


def load_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except (FileNotFoundError, ValueError):
        return default


def save_json(path, data):
    write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n")


def chapter_files():
    out = []
    if CHAPTERS.is_dir():
        for p in CHAPTERS.iterdir():
            m = _CH_RE.match(p.name)
            if m:
                out.append((int(m.group(1)), p))
    return sorted(out)


def chapter_path(n):
    return CHAPTERS / f"chapter-{n:03d}.md"


def next_chapter_number():
    cf = chapter_files()
    return cf[-1][0] + 1 if cf else 1


def chapter_title(text, fallback=""):
    for line in text.splitlines():
        s = line.strip()
        if s.startswith("#"):
            return s.lstrip("#").strip()
        if s:
            break
    return fallback


def body_text(text):
    """Chapter text without the leading title line."""
    lines = text.splitlines()
    i = 0
    while i < len(lines) and (not lines[i].strip() or lines[i].lstrip().startswith("#")):
        i += 1
    return "\n".join(lines[i:])


def clean_body(text):
    """Body without scene-break lines and emphasis marks (for counting and analysis)."""
    kept = [ln for ln in body_text(text).splitlines() if not _BREAK_RE.match(ln)]
    return "\n".join(kept).replace("*", "")


def words(text):
    return WORD_RE.findall(text)


def word_count(text):
    return len(words(clean_body(text)))


def sentences(text):
    parts = SENT_RE.split(text.strip())
    return [p.strip() for p in parts if p.strip()]


def settings():
    d = dict(DEFAULTS)
    txt = read(STORY / "brief.md")
    m = re.search(r"^##\s+Machine settings\s*$(.*?)(?=^##\s|\Z)", txt, re.S | re.M)
    if m:
        for line in m.group(1).splitlines():
            mm = re.match(r"^\s*([a-z_]+)\s*[:=]\s*(.+?)\s*$", line)
            if mm:
                d[mm.group(1)] = mm.group(2)
    return d


def setting_int(key):
    s = settings()
    try:
        return int(s[key])
    except (ValueError, KeyError):
        return int(DEFAULTS[key])


def canon_names():
    names = set()
    for line in read(STORY / "bible" / "canon_names.txt").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            names.add(s)
    return names


def canon_tokens():
    toks = set()
    for n in canon_names():
        for t in re.split(r"[\s,]+", n.lower().replace("’", "'")):
            if t:
                toks.add(t)
    return toks


def last_chapters(k, before=None):
    cf = chapter_files()
    if before is not None:
        cf = [c for c in cf if c[0] < before]
    return cf[-k:] if k > 0 else []
