#!/usr/bin/env python3
"""Manage novels. Each novel lives in its own folder novels/<slug>/ (story, chapters, ops, out, archive).

  novel.py list                         all novels, marking the active one
  novel.py new <slug> --title "..."     create novels/<slug>/ from templates/novel/ (and make it active)
                                        [--style-from <slug>] copies another novel's style profile (optional)
  novel.py use <slug>                   make a novel the active one (written to novels/ACTIVE)
  novel.py status                       the active novel and its progress

The scheduler/agents always work on the active novel only. Standard library only.
"""
import argparse
import os
import re
import shutil
import sys

os.environ["ANOGEN_NO_NOVEL_OK"] = "1"  # allowed to run with no active novel
from common import NOVEL_ERROR, REPO, ROOT, SLUG_RE, chapter_files, read, write  # noqa: E402

NOVELS = REPO / "novels"
TEMPLATE = REPO / "templates" / "novel"


def slugs():
    return sorted(p.name for p in NOVELS.iterdir() if p.is_dir() and SLUG_RE.match(p.name)) if NOVELS.is_dir() else []


def active():
    return "" if NOVEL_ERROR else ROOT.name


def title_of(slug):
    m = re.search(r"(?m)^title:\s*(.+)$", read(NOVELS / slug / "story" / "brief.md"))
    return m.group(1).strip() if m else "(no title)"


def cmd_list(_):
    if not slugs():
        print("No novels yet. Create one: novel.py new <slug> --title \"...\"")
    for s in slugs():
        n = sum(1 for _ in (NOVELS / s / "chapters").glob("chapter-*.md")) if (NOVELS / s / "chapters").is_dir() else 0
        print(f"{'*' if s == active() else ' '} {s}  |  {title_of(s)}  |  {n} chapters")


def cmd_use(a):
    if not SLUG_RE.match(a.slug) or not (NOVELS / a.slug).is_dir():
        sys.exit(f"ERROR: no novel '{a.slug}'. Existing: {', '.join(slugs()) or '(none)'}")
    write(NOVELS / "ACTIVE", a.slug + "\n")
    print(f"Active novel: {a.slug}  ({title_of(a.slug)})")


def cmd_new(a):
    if not SLUG_RE.match(a.slug):
        sys.exit("ERROR: slug must be lowercase letters, digits and hyphens (example: the-thirteenth-knight)")
    dest = NOVELS / a.slug
    if dest.exists():
        sys.exit(f"ERROR: novels/{a.slug} already exists; nothing changed.")
    if not TEMPLATE.is_dir():
        sys.exit("ERROR: templates/novel/ is missing.")
    if a.style_from and not (NOVELS / a.style_from / "story" / "style" / "profile.md").exists():
        sys.exit(f"ERROR: novel '{a.style_from}' has no style profile to copy.")
    NOVELS.mkdir(exist_ok=True)
    shutil.copytree(TEMPLATE, dest)
    brief = dest / "story" / "brief.md"
    write(brief, read(brief).replace("{{TITLE}}", a.title))
    if a.style_from:
        shutil.copyfile(NOVELS / a.style_from / "story" / "style" / "profile.md", dest / "story" / "style" / "profile.md")
    write(NOVELS / "ACTIVE", a.slug + "\n")
    print(f"Created novels/{a.slug} (title: {a.title}); it is now the active novel.")


def cmd_status(_):
    if NOVEL_ERROR:
        sys.exit(NOVEL_ERROR)
    print(f"Active novel: {ROOT.name}  ({title_of(ROOT.name)}); chapters: {len(chapter_files())}")


def main():
    ap = argparse.ArgumentParser()
    sub = ap.add_subparsers(dest="cmd", required=True)
    sub.add_parser("list").set_defaults(f=cmd_list)
    p = sub.add_parser("new"); p.add_argument("slug"); p.add_argument("--title", required=True)
    p.add_argument("--style-from", default=""); p.set_defaults(f=cmd_new)
    p = sub.add_parser("use"); p.add_argument("slug"); p.set_defaults(f=cmd_use)
    sub.add_parser("status").set_defaults(f=cmd_status)
    a = ap.parse_args()
    a.f(a)


if __name__ == "__main__":
    main()
