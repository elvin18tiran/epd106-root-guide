#!/usr/bin/env python3
# Annotate a Chinese EPUB with pinyin ruby above each hanzi (context-aware).
# Usage: pinyin_epub.py <in.epub> <out.epub>
import sys, zipfile, re, html
from bs4 import BeautifulSoup, NavigableString
from pypinyin import pinyin, Style

IN, OUT = sys.argv[1], sys.argv[2]
HANZI = re.compile(r'[㐀-䶿一-鿿豈-﫿]')
SKIP_PARENTS = {'script', 'style', 'rt', 'rp', 'ruby'}

RUBY_CSS = (
    "ruby{display:inline-ruby;}"
    "rt{font-size:50%;color:#444;line-height:1;}"
)

def ruby_for_run(run):
    # run = string of hanzi only; get per-char contextual pinyin
    reads = pinyin(run, style=Style.TONE, errors='default', heteronym=False)
    out = []
    for ch, r in zip(run, reads):
        py = r[0] if r else ''
        out.append(f"<ruby>{html.escape(ch)}<rt>{html.escape(py)}</rt></ruby>")
    return ''.join(out)

def annotate_text(s):
    # replace maximal hanzi runs with ruby, keep everything else verbatim
    res, i, n = [], 0, len(s)
    while i < n:
        if HANZI.match(s[i]):
            j = i
            while j < n and HANZI.match(s[j]):
                j += 1
            res.append(ruby_for_run(s[i:j]))
            i = j
        else:
            res.append(html.escape(s[i]))
            i += 1
    return ''.join(res)

def process_html(data):
    text = data.decode('utf-8', 'ignore')
    soup = BeautifulSoup(text, 'html.parser')
    changed = False
    for node in list(soup.find_all(string=True)):
        if not node or not HANZI.search(str(node)):
            continue
        p = node.parent
        bad = False
        while p is not None:
            if getattr(p, 'name', None) in SKIP_PARENTS:
                bad = True
                break
            p = p.parent
        if bad:
            continue
        frag = annotate_text(str(node))
        node.replace_with(BeautifulSoup(frag, 'html.parser'))
        changed = True
    if changed:
        head = soup.find('head')
        if head is not None:
            st = soup.new_tag('style')
            st.string = RUBY_CSS
            head.append(st)
    return str(soup).encode('utf-8'), changed

content_ext = ('.html', '.xhtml', '.htm')
zin = zipfile.ZipFile(IN, 'r')
names = zin.namelist()
n_changed = 0
with zipfile.ZipFile(OUT, 'w') as zout:
    # mimetype must be first and STORED
    if 'mimetype' in names:
        zout.writestr(zipfile.ZipInfo('mimetype'), zin.read('mimetype'), zipfile.ZIP_STORED)
    for name in names:
        if name == 'mimetype':
            continue
        data = zin.read(name)
        if name.lower().endswith(content_ext):
            try:
                data, ch = process_html(data)
                if ch:
                    n_changed += 1
            except Exception as e:
                sys.stderr.write(f"skip {name}: {e}\n")
        zout.writestr(name, data, zipfile.ZIP_DEFLATED)
zin.close()
print(f"annotated {n_changed} content file(s) -> {OUT}")
