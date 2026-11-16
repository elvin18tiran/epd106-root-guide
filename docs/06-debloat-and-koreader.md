# 06 — Debloat & KOReader Setup

These need **no root** — just ADB. They're reversible.

## Debloat (reversible, per-user)

`pm uninstall -k --user 0 <pkg>` hides a package for user 0 but keeps it on the system image, so
it's fully reversible with `cmd package install-existing <pkg>` and survives a factory reset.

**Before removing the keyboard, install another one** (e.g. Simple Keyboard from F-Droid) and set
it default — otherwise you can't type:

```bash
adb install SimpleKeyboard.apk
adb shell ime enable rkr.simplekeyboard.inputmethod/.latin.LatinIME
adb shell ime set    rkr.simplekeyboard.inputmethod/.latin.LatinIME
adb shell pm uninstall -k --user 0 com.sohu.inputmethod.sogou.oem   # remove Sogou
```

Packages removed on the test unit (28), safe for a reading-only device with no cellular radio:

```
com.tencent.weread.eink  cn.wps.moffice_eng.lite  com.abupdate.fota_demo_iot
com.mgs.factorytest  com.softwinner.dragonaging  com.softwinner.dragonfire
com.android.phone  com.android.server.telecom  com.android.mms.service
com.android.providers.telephony  com.android.providers.blockednumber  com.android.nfc
com.android.musicfx  com.android.wallpapercropper  com.android.cts.ctsshim
com.android.cts.priv.ctsshim  com.duokan.einkreader  com.softwinner.explore
com.svox.pico  com.android.printspooler  com.android.printservice.recommendation
com.android.bips  com.android.bluetoothmidiservice  com.android.bluetooth
com.android.providers.contacts  com.android.wallpaperbackup
com.android.sharedstoragebackup  com.sohu.inputmethod.sogou.oem
```

Disabled (came back after reboot, so disabled instead):
`com.android.backupconfirm`, `com.android.companiondevicemanager`.

> **Keep:** `com.mgs.settings` and `com.softwinner.awmanager` (e-ink/power), the network login
> helpers (`captiveportallogin`, `pacprocessor`, `proxyhandler`, `vpndialogs`, `statementservice`),
> and all core `android` / `providers.*` / `systemui` / `settings` packages.
> **Restore everything:** loop `cmd package install-existing` over the removed list + `pm enable`
> the disabled ones.

### Faster e-ink + battery

```bash
adb shell "settings put global window_animation_scale 0; \
           settings put global transition_animation_scale 0; \
           settings put global animator_duration_scale 0"     # kill ghosting/lag
adb shell settings put system screen_off_timeout 120000       # 2-min sleep
adb shell cmd appops set <pkg> RUN_IN_BACKGROUND ignore       # curb background apps
```

## KOReader (Kindle-like)

- Install the latest **arm** build: `github.com/koreader/koreader/releases` (installs over the
  stock one, keeping settings).
- **Fonts:** drop `.ttf` into `/sdcard/koreader/fonts/` (e.g. **Literata**, close to Kindle's
  Bookerly).
- **Dictionary (tap-to-define):** Search → Dictionary settings → Download dictionaries → English
  (WordNet / GCIDE). Long-press any word to define. To preseed, drop a StarDict folder into
  `/sdcard/koreader/data/dict/` and set order in `settings.reader.lua` (`dicts_order`).
- **Kindle layout** (edit `/sdcard/koreader/settings.reader.lua`, force-stop KOReader first):
  `cre_font="Literata"`, `copt_font_size=22`, `copt_line_spacing=115`,
  `copt_h_page_margins={20,20}`, `copt_t_page_margin=20`, `copt_b_page_margin=15`.
  Minimal footer: set `footer` entries so only time-to-read + percentage show, `items_separator="none"`,
  `disable_progress_bar=true`.
  > Per-book `.sdr/metadata.epub.lua` sidecars override these defaults — strip the same keys from
  > them (keep highlights/positions) so the new look applies everywhere.
