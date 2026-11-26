"""Shared helpers for the Anogen tools. Standard library only. No AI calls."""
import hashlib
import json
import os
import sys
import re
import shutil
from pathlib import Path

TOOLS = Path(__file__).resolve().parent
SLUG_RE = re.compile(r"^[a-z0-9][a-z0-9-]{0,63}$")


def _resolve():
    """Return (REPO, ROOT, ENGINE, LOCK_DIR, error).

    REPO     git work tree (holds tools/, engine/, templates/, novels/)
    ROOT     the active novel folder (story/, chapters/, ops/, out/ live here)
    ENGINE   engine-level shared files (prices.json)
    LOCK_DIR where the single global lock lives (one agent at a time across ALL novels)
    ANOGEN_ROOT (tests, scratch copies) wins and keeps the old flat layout: everything under that folder.
    Otherwise: ANOGEN_NOVEL, then novels/ACTIVE; a repo with no novels/ folder keeps the old flat layout.
    """
    env = os.environ.get("ANOGEN_ROOT")
    if env:
        r = Path(env)
        return r, r, r / "ops", r / "ops", ""
    repo = TOOLS.parent
    novels = repo / "novels"
    engine = repo / "engine"
    if not novels.is_dir():
        return repo, repo, repo / "ops", repo / "ops", ""
    slug = (os.environ.get("ANOGEN_NOVEL") or read(novels / "ACTIVE")).strip()
    if not slug:
        return repo, novels / "_none", engine, novels, "no active novel: run `python3 tools/novel.py use <slug>` (see `novel.py list`)"
    if not SLUG_RE.match(slug) or not (novels / slug).is_dir():
        return repo, novels / "_none", engine, novels, f"novel '{slug}' not found in novels/ (see `novel.py list`)"
    return repo, novels / slug, engine, novels, ""


DEFAULTS = {
    "title": "Untitled Serial",
    "author": "Anogen",
    "chapter_words_min": "2000",
    "chapter_words_max": "2500",
    "context_pack_max_chars": "40000",
    "repeat_window": "5",
    "arc_default_max": "50",
    "critic_span": "10",
}

_CH_RE = re.compile(r"^chapter-(\d+)\.md$")
WORD_RE = re.compile(r"[A-Za-z0-9À-ɏ]+(?:['’\-][A-Za-z0-9À-ɏ]+)*")
SENT_RE = re.compile(r"(?<=[.!?…])[\"”’')\]]*\s+")
_BREAK_RE = re.compile(r"^\s*(?:(?:\*\s*){3,}|-{3,}|_{3,})\s*$")


def decode_mixed(raw):
    """Decode bytes as UTF-8; any line that is not valid UTF-8 is read as Windows-1252 (a PowerShell Add-Content leftover)."""
    try:
        return raw.decode("utf-8"), 0
    except UnicodeDecodeError:
        out, bad = [], 0
        for ln in raw.split(b"\n"):
            try:
                out.append(ln.decode("utf-8"))
            except UnicodeDecodeError:
                bad += 1
                out.append(ln.decode("cp1252", errors="replace"))
        return "\n".join(out), bad


def normalize_utf8(path):
    """Rewrite a text file as clean UTF-8 if it holds mixed encodings. Returns the number of lines fixed."""
    p = Path(path)
    text, bad = decode_mixed(p.read_bytes())
    if bad:
        p.write_bytes(text.encode("utf-8"))
    return bad


def read(path, default=""):
    try:
        text, bad = decode_mixed(Path(path).read_bytes())
    except (FileNotFoundError, IsADirectoryError):
        return default
    if bad:
        print(f"WARNING: {path} is not valid UTF-8 ({bad} lines read as Windows-1252); run python3 tools/save.py to normalize it", file=sys.stderr)
    return text




REPO, ROOT, ENGINE, LOCK_DIR, NOVEL_ERROR = _resolve()
if NOVEL_ERROR and not os.environ.get("ANOGEN_NO_NOVEL_OK"):
    raise SystemExit("ERROR: " + NOVEL_ERROR)
STORY = ROOT / "story"
CHAPTERS = ROOT / "chapters"
OPS = ROOT / "ops"
OUT = ROOT / "out"


def write(path, text, backup=False):
    """Atomic write: temp file in the same folder, then os.replace (a crash never leaves a half file).
    backup=True keeps the previous version as <name>.bak."""
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    if backup and p.exists():
        shutil.copyfile(p, p.with_name(p.name + ".bak"))
    tmp = p.with_name(f".{p.name}.tmp{os.getpid()}")
    try:
        tmp.write_text(text, encoding="utf-8")
        os.replace(tmp, p)
    finally:
        if tmp.exists():
            tmp.unlink()


def load_json(path, default):
    try:
        return json.loads(Path(path).read_text(encoding="utf-8"))
    except FileNotFoundError:
        return default
    except ValueError as e:
        raise SystemExit(f"ERROR: {path} is not valid JSON ({e}). Fix it; nothing was overwritten.")


def save_json(path, data, backup=False):
    write(path, json.dumps(data, indent=2, ensure_ascii=False) + "\n", backup=backup)


def file_hash(path):
    """Short content hash of a file ('' if missing). Used to know whether a reviewed chapter changed."""
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()[:16]
    except FileNotFoundError:
        return ""


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
    """Lowest chapter number that does not exist yet (fills gaps first)."""
    n = 1
    while chapter_path(n).exists():
        n += 1
    return n


HEADING_RE = re.compile(r"^#\s+Chapter\s+(\d+):\s+\S.*$")


def heading_issue(text, n=None):
    """'' if the first non-empty line is `# Chapter N: Title` (N = n when given), else the reason (owner order 2026-11-25)."""
    first = next((ln.strip() for ln in text.splitlines() if ln.strip()), "")
    m = HEADING_RE.match(first)
    if not m:
        return "first line must be '# Chapter N: Title' (example: # Chapter 1: Forty Minutes of Grass)"
    if n is not None and int(m.group(1)) != n:
        return f"heading says Chapter {m.group(1)} but the file is chapter {n}"
    return ""


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
    kept = [ln for ln in body_text(text).splitlines()
            if not _BREAK_RE.match(ln) and not ln.lstrip().startswith(">")]
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


WORDS_MIN_FLOOR = 2000  # owner order 2026-11-26, locked setting 16: never lower, whatever a brief says


def setting_int(key):
    s = settings()
    try:
        v = int(s[key])
        if key == "chapter_words_min":
            v = max(v, WORDS_MIN_FLOOR)
        return v
    except (ValueError, KeyError):
        return int(DEFAULTS[key])


def canon_names():
    names = set()
    for line in read(STORY / "bible" / "canon_names.txt").splitlines():
        s = line.strip()
        if s and not s.startswith("#"):
            names.add(s)
    return names


_NAME_STOP = {"of", "the", "a", "an", "and", "de", "von", "van", "la", "le", "el", "al", "bin", "ibn"}


def canon_tokens():
    toks = set()
    for n in canon_names():
        for t in re.split(r"[\s,]+", n.lower().replace("’", "'")):
            if t and t not in _NAME_STOP:
                toks.add(t)
    return toks

