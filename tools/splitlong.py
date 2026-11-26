#!/usr/bin/env python3
"""Split overlong narration sentences at ', and X' / ', but X' where X starts a new clause.
Review the result by hand (it is a blunt tool: 'and' is dropped, 'but' becomes a sentence opener).
Usage: splitlong.py N [min_words]   (edits the chapter in place; skips dialogue)"""
import re, sys
sys.path.insert(0, __file__.rsplit('/', 1)[0])
from common import CHAPTERS
n = int(sys.argv[1]); mn = int(sys.argv[2]) if len(sys.argv) > 2 else 26
p = CHAPTERS / f"chapter-{n:03d}.md"
t = p.read_text(encoding='utf-8')
START = r"(?:He|She|It|They|The|His|Her|Its|Eden|Rowan|Clara|Felix|Lysette|Okoru|Vesk|Strent|Harrow|Valerius|Gorrath|Seraphine|Ysolde|There|Every|One|Two|Three|Nobody|Nothing|Somebody|Someone|Behind|Beyond|Then|That|This|A|An|No|Some|Each|When|Because|Until|Even)"
pat = re.compile(r", (and|but) (?=" + START + r" )", re.I)
out = []; cnt = 0
for line in t.split('\n'):
    if not line.strip() or line.startswith('#') or line.startswith('>') or line.startswith('*') and line.strip() == '* * *':
        out.append(line); continue
    sents = re.split(r'(?<=[.!?])\s+', line)
    new = []
    for s in sents:
        if len(s.split()) > mn:
            ms = list(pat.finditer(s))
            best = None
            ms = [m for m in ms if s[:m.start()].count('"') % 2 == 0]
            ms += [m for m in re.finditer(r"; (?=[A-Za-z])|, and then (?=[a-z])", s) if s[:m.start()].count('"') % 2 == 0]
            for m in ms:
                a = len(s[:m.start()].split()); b = len(s[m.end():].split())
                if a >= 8 and b >= 8:
                    sc = abs(a - b)
                    if best is None or sc < best[0]: best = (sc, m)
            if best:
                m = best[1]
                rest = s[m.end():]
                if m.group(0).startswith(', and then'):
                    s = s[:m.start()] + '. Then ' + rest
                elif m.group(0).lower().startswith(', but'):
                    s = s[:m.start()] + '. But ' + rest
                else:
                    s = s[:m.start()] + '. ' + rest[0].upper() + rest[1:]
                cnt += 1
        new.append(s)
    out.append(' '.join(new))
p.write_text('\n'.join(out), encoding='utf-8')
print(n, 'splits', cnt)
