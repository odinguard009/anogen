#!/usr/bin/env python3
"""Build an EPUB 3 with the standard library only.

Usage:
  build_epub.py --arc K [--force]
  build_epub.py --range A-B [--force]
  build_epub.py --all-complete
Gate: an arc is built only if its status is 'complete' in ops/engine.json (exit 2 otherwise).
"""
import argparse
import datetime
import re
import sys
import uuid
import zipfile
from xml.etree import ElementTree as ET
from xml.sax.saxutils import escape

from common import OUT, chapter_path, load_json, OPS, read, settings

CSS = """body{font-family:serif;line-height:1.5;margin:0 4%}
h1{text-align:center;margin:1.5em 0 1em;font-size:1.4em}
p{margin:0 0 .7em;text-indent:0}
p.brk{text-align:center;margin:1.2em 0}
h2{text-align:center;font-size:1.1em}
blockquote.epigraph{margin:0 12% 1.6em;font-style:italic;text-align:center}
blockquote.epigraph p{margin:0 0 .3em}
.title{text-align:center;margin-top:30%}
"""


def inline(s):
    s = escape(s)
    s = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"__(.+?)__", r"<strong>\1</strong>", s)
    s = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", s)
    s = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", r"<em>\1</em>", s)
    return s


BREAK = re.compile(r"^\s*(?:(?:\*\s*){3,}|-{3,}|_{3,})\s*$")


def md_to_xhtml(md, fallback_title):
    lines = md.splitlines()
    title, i = fallback_title, 0
    while i < len(lines) and not lines[i].strip():
        i += 1
    if i < len(lines) and lines[i].lstrip().startswith("#"):
        title = lines[i].lstrip("#").strip().replace("*", "").replace("_", " ").strip() or fallback_title
        i += 1
    body, buf = [], []

    def flush():
        if buf:
            txt = " ".join(x.strip() for x in buf)
            if txt.startswith("#"):
                body.append("<h2>" + escape(txt.lstrip("#").strip().replace("*", "")) + "</h2>")
            else:
                h = "<p>" + inline(txt) + "</p>"
                try:
                    ET.fromstring("<r>" + h + "</r>")
                except ET.ParseError:
                    h = "<p>" + escape(txt.replace("*", "")) + "</p>"
                body.append(h)
            buf.clear()

    quote = []
    for ln in lines[i:]:
        if ln.lstrip().startswith(">"):
            flush()
            quote.append(ln.lstrip()[1:].strip())
            continue
        if quote:
            body.append('<blockquote class="epigraph">' + "".join(
                "<p>" + inline(q) + "</p>" for q in quote if q) + "</blockquote>")
            quote = []
        if BREAK.match(ln):
            flush()
            body.append('<p class="brk">* * *</p>')
        elif not ln.strip():
            flush()
        else:
            buf.append(ln)
    if quote:
        body.append('<blockquote class="epigraph">' + "".join(
            "<p>" + inline(q) + "</p>" for q in quote if q) + "</blockquote>")
    flush()
    xhtml = ('<?xml version="1.0" encoding="utf-8"?>\n'
             '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops" lang="en">'
             f"<head><title>{escape(title)}</title>"
             '<link rel="stylesheet" type="text/css" href="style.css"/></head><body>'
             f"<h1>{escape(title)}</h1>\n" + "\n".join(body) + "</body></html>")
    return title, xhtml


def build(numbers, out_path, book_title, author):
    chapters = []
    for n in numbers:
        p = chapter_path(n)
        if not p.exists():
            sys.exit(f"missing chapter file: {p.name}")
        t, x = md_to_xhtml(read(p), f"Chapter {n}")
        chapters.append((n, t, x))

    uid = "urn:uuid:" + str(uuid.uuid5(uuid.NAMESPACE_URL, f"anogen/{book_title}/{numbers[0]}-{numbers[-1]}"))
    now = datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    manifest = ['<item id="nav" href="nav.xhtml" media-type="application/xhtml+xml" properties="nav"/>',
                '<item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>',
                '<item id="css" href="style.css" media-type="text/css"/>',
                '<item id="titlepage" href="title.xhtml" media-type="application/xhtml+xml"/>']
    spine = ['<itemref idref="titlepage"/>']
    nav_li, ncx_pts = [], []
    for k, (n, t, _) in enumerate(chapters, 1):
        manifest.append(f'<item id="c{n}" href="c{n:03d}.xhtml" media-type="application/xhtml+xml"/>')
        spine.append(f'<itemref idref="c{n}"/>')
        nav_li.append(f'<li><a href="c{n:03d}.xhtml">{escape(t)}</a></li>')
        ncx_pts.append(f'<navPoint id="np{n}" playOrder="{k}"><navLabel><text>{escape(t)}</text></navLabel>'
                       f'<content src="c{n:03d}.xhtml"/></navPoint>')

    opf = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<package xmlns="http://www.idpf.org/2007/opf" version="3.0" unique-identifier="bookid">'
           '<metadata xmlns:dc="http://purl.org/dc/elements/1.1/">'
           f'<dc:identifier id="bookid">{uid}</dc:identifier><dc:title>{escape(book_title)}</dc:title>'
           f'<dc:creator>{escape(author)}</dc:creator><dc:language>en</dc:language>'
           f'<meta property="dcterms:modified">{now}</meta></metadata>'
           f'<manifest>{"".join(manifest)}</manifest><spine toc="ncx">{"".join(spine)}</spine></package>')
    nav = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<html xmlns="http://www.w3.org/1999/xhtml" xmlns:epub="http://www.idpf.org/2007/ops"><head><title>Contents</title></head>'
           f'<body><nav epub:type="toc"><h1>Contents</h1><ol>{"".join(nav_li)}</ol></nav></body></html>')
    ncx = ('<?xml version="1.0" encoding="utf-8"?>\n'
           '<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">'
           f'<head><meta name="dtb:uid" content="{uid}"/></head><docTitle><text>{escape(book_title)}</text></docTitle>'
           f'<navMap>{"".join(ncx_pts)}</navMap></ncx>')
    titlepage = ('<?xml version="1.0" encoding="utf-8"?>\n'
                 '<html xmlns="http://www.w3.org/1999/xhtml"><head><title>Title</title>'
                 '<link rel="stylesheet" type="text/css" href="style.css"/></head><body>'
                 f'<div class="title"><h1>{escape(book_title)}</h1><p>{escape(author)}</p></div></body></html>')
    container = ('<?xml version="1.0"?>\n<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">'
                 '<rootfiles><rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/></rootfiles></container>')

    out_path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out_path, "w") as z:
        z.writestr(zipfile.ZipInfo("mimetype"), "application/epub+zip", compress_type=zipfile.ZIP_STORED)
        z.writestr("META-INF/container.xml", container, compress_type=zipfile.ZIP_DEFLATED)
        for name, data in (("content.opf", opf), ("nav.xhtml", nav), ("toc.ncx", ncx),
                           ("style.css", CSS), ("title.xhtml", titlepage)):
            z.writestr("OEBPS/" + name, data, compress_type=zipfile.ZIP_DEFLATED)
        for n, _, x in chapters:
            z.writestr(f"OEBPS/c{n:03d}.xhtml", x, compress_type=zipfile.ZIP_DEFLATED)
    validate(out_path)
    return out_path


def validate(path):
    with zipfile.ZipFile(path) as z:
        names = z.namelist()
        if names[0] != "mimetype" or z.getinfo("mimetype").compress_type != zipfile.ZIP_STORED:
            sys.exit("INVALID EPUB: mimetype must be first and stored")
        for n in names:
            if n.endswith((".xhtml", ".opf", ".ncx", ".xml")):
                try:
                    ET.fromstring(z.read(n))
                except ET.ParseError as e:
                    sys.exit(f"INVALID EPUB: {n} not well-formed: {e}")
        opf = ET.fromstring(z.read("OEBPS/content.opf"))
        ns = {"o": "http://www.idpf.org/2007/opf"}
        ids = set()
        for it in opf.findall(".//o:manifest/o:item", ns):
            ids.add(it.get("id"))
            if "OEBPS/" + it.get("href") not in names:
                sys.exit(f"INVALID EPUB: manifest file missing: {it.get('href')}")
        for ir in opf.findall(".//o:spine/o:itemref", ns):
            if ir.get("idref") not in ids:
                sys.exit(f"INVALID EPUB: spine idref unknown: {ir.get('idref')}")


def main():
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--arc", type=int)
    g.add_argument("--range")
    g.add_argument("--all-complete", action="store_true")
    ap.add_argument("--force", action="store_true")
    a = ap.parse_args()
    st = settings()
    title, author = st["title"], st["author"]
    arcs = load_json(OPS / "engine.json", {}).get("arcs", {})

    def do_arc(k):
        arc = arcs.get(str(k))
        if not arc:
            sys.exit(f"arc {k} is not planned")
        if arc["status"] != "complete" and not a.force:
            print(f"GATE: arc {k} is '{arc['status']}', not complete. EPUB not built.")
            sys.exit(2)
        name = arc.get("name") or f"Arc {k}"
        p = build(list(range(arc["start"], arc["end"] + 1)), OUT / f"arc-{k}.epub", f"{title} - {name}", author)
        print("Built", p)

    if a.arc is not None:
        do_arc(a.arc)
    elif a.range:
        m = re.fullmatch(r"(\d+)-(\d+)", a.range)
        if not m:
            sys.exit("--range must look like 1-50")
        s, e = int(m.group(1)), int(m.group(2))
        print("Built", build(list(range(s, e + 1)), OUT / f"chapters-{s}-{e}.epub", title, author))
    else:
        done = [k for k, v in arcs.items() if v["status"] == "complete"]
        if not done:
            print("No completed arcs.")
        for k in sorted(done, key=int):
            do_arc(int(k))


if __name__ == "__main__":
    main()
