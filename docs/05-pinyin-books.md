# 05 — Pinyin over Chinese Text (learn Mandarin)

**There is no font or OS toggle for this.** A hanzi's reading depends on the *word* (行 = háng in
银行 but xíng in 行走), so pinyin must be computed from context. The thing people remember as a
"system-wide" setting was **Duokan's built-in pinyin mode** — and Duokan is a cloud app that does
not survive a serious debloat (it crashes on bookshelf init and drags `com.mgs.settings` into a
crash loop). Don't chase it.

## The working method: ruby annotation + KOReader

KOReader (crengine) renders HTML **`<ruby>`** annotations natively — pinyin appears above each
character, no setting needed. So you pre-process each Chinese EPUB to wrap every hanzi as
`<ruby>字<rt>zì</rt></ruby>`, using `pypinyin` for **context-aware** readings.

`scripts/pinyin_epub.py` does exactly this:

```bash
pip install pypinyin beautifulsoup4 lxml      # (opencc-python-reimplemented for 繁→简)
python3 pinyin_epub.py  input-chinese.epub  output-pinyin.epub
adb push output-pinyin.epub "/sdcard/General Books/"
# open in KOReader — pinyin shows automatically
```

Verified on-device: 银行 → **yín háng** (correct), 静夜思 poem fully annotated, tone marks (hàn).

### Options / notes

- **Tone marks vs numbers:** the script uses `Style.TONE` (hàn). For `han4`, change to `Style.TONE3`.
- **Traditional → Simplified:** if your source is traditional, convert first with OpenCC
  (`OpenCC('t2s').convert(text)`) before annotating — simplified is standard for Mandarin learners.
- **Only hanzi are wrapped** — punctuation, English, and all HTML structure are untouched.
- Ruby roughly **doubles line height** (expected — it makes room for the pinyin).
- `pypinyin` is excellent but not perfect on rare literary/classical characters; an occasional
  reading may need a manual fix.
- **Where to get public-domain Chinese books:** Project Gutenberg (`gutenberg.org`, often
  traditional/classical — it may rate-limit automated downloads), Wikisource (`zh.wikisource.org`),
  or any EPUB you own. Famous beginner-friendly public-domain picks: Tang poems (唐诗), Lu Xun
  short stories (鲁迅, e.g. 孔乙己), Zhu Ziqing essays (朱自清, 《背影》).
