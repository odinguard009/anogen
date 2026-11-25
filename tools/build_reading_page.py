#!/usr/bin/env python3
"""Build ONE self-contained HTML reading page from chapters/*.md (0 tokens; text never passes through a model).

Usage: build_reading_page.py [--range A-B] [--out out/reading-page.html]
Publish the output with any tool that can host an HTML page (for example Claude's Artifact tool: publish the file).
"""
import argparse
import html
import re

from common import ROOT, chapter_files, read, settings


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--range", default="")
    ap.add_argument("--out", default=str(ROOT / "out" / "reading-page.html"))
    a = ap.parse_args()
    lo, hi = 1, 10 ** 9
    m = re.match(r"^(\d+)-(\d+)$", a.range or "")
    if m:
        lo, hi = int(m.group(1)), int(m.group(2))
    parts, toc = [], []
    for n, f in chapter_files():
        if not lo <= n <= hi:
            continue
        out, title = [], ""
        for ln in read(f).splitlines():
            if ln.startswith("# "):
                title = ln[2:].strip()
                continue
            s = ln.strip()
            if not s:
                continue
            if s == "* * *":
                out.append('<p class="br">* * *</p>')
            elif s.startswith(">"):
                out.append("<blockquote>%s</blockquote>" % html.escape(s.lstrip("> ").strip()))
            else:
                t = html.escape(s)
                t = re.sub(r"\*\*(.+?)\*\*", r"<b>\1</b>", t)
                t = re.sub(r"\*(.+?)\*", r"<i>\1</i>", t)
                out.append("<p>%s</p>" % t)
        toc.append('<li><a href="#c%d">%s</a></li>' % (n, html.escape(title)))
        parts.append('<section id="c%d"><h2>%s</h2>%s</section>' % (n, html.escape(title), "".join(out)))
    title = html.escape(settings().get("title", "Reading page"))
    doc = ('<!DOCTYPE html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
           f"<title>{title} - Reading Page</title><style>body{{max-width:40rem;margin:0 auto;padding:1rem;font:18px/1.7 Georgia,serif;color:#222;background:#fbfaf6}}"
           "@media(prefers-color-scheme:dark){body{color:#ddd;background:#16161a}a{color:#9bc}}h2{margin-top:3rem;font-size:1.3rem}p{margin:.8em 0}"
           ".br{text-align:center;opacity:.6}blockquote{font-style:italic;opacity:.8;margin:1em 0;padding-left:1em;border-left:3px solid #8884}</style></head><body>"
           f"<h1>{title}</h1><ol style=\"list-style:none;padding:0\">" + "".join(toc) + "</ol>" + "".join(parts) + "</body></html>")
    ROOT.joinpath("out").mkdir(exist_ok=True)
    open(a.out, "w", encoding="utf-8").write(doc)
    print(f"Built {a.out} ({len(parts)} chapters, {len(doc)} bytes)")


if __name__ == "__main__":
    main()
