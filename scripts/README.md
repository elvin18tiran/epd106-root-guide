# Scripts

| Script | Purpose | Guide |
|---|---|---|
| `build-flash-zip.py` | assemble an unsigned OTA zip (template + updater-script + boot.img STORED); sign with signapk afterwards | [02](../docs/02-rooting.md) |
| `cmp-boot.py` | parse two Android boot images, compare real (non-padding) content | [02](../docs/02-rooting.md) |
| `patch_framework.py` | in-place swap of STORED PNGs in an APK with CRC fix-up (⚠ Magisk-module use bricks the EPD106) | [04](../docs/04-sleep-screen.md) |
| `render_sleep.py` | render the 758×1024 grayscale "lost & found" sleep image (Literata) | [04](../docs/04-sleep-screen.md) |
| `pinyin_epub.py` | add context-aware pinyin ruby above every hanzi in an EPUB | [05](../docs/05-pinyin-books.md) |

These are reference implementations from a real session; read before running and adapt paths.
