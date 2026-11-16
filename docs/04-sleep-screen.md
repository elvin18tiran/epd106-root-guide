# 04 — Custom Sleep Screen

The reader's standby images (the animals) are drawn by a **modified PowerManagerService**
(`showSuspendLogo` / `getLogoResource`), which picks one of `photo1`–`photo4` (plus `_charging`
variants) from **`framework-res.apk`** based on the `my_wallpaper_index` setting. There is **no
custom-file hook** — the image must come from those framework resources.

A great use for this is a **"lost & found" screen** with your contact info and reading list.
`scripts/render_sleep.py` renders one (758×1024, grayscale, Literata) — see the script for layout.

## ✅ The safe method: static RRO overlay (DO THIS)

Instead of replacing `framework-res.apk`, ship a separate **overlay** that only *supplies* new
`photoN` drawables. If anything is wrong, Android just ignores it — **it cannot brick the device** —
and it's removable with one command. Bonus: it lives in `/vendor`, so it **survives a factory
reset** (ideal for a lost-device screen).

**Prerequisite — the platform key must match the framework signer.** The overlay targets the
`android` package, so it must be signed with the same cert as `framework-res.apk`:

```bash
keytool -printcert -file <framework-res CERT.RSA>   # note the SHA256
keytool -printcert -file <navbar/keys/platform CERT.RSA>
# On this device both are identical (C8:A2:E9:BC...). If yours differ, this method won't work.
```

Build it:

```
# res/drawable-sw572dp-hdpi/photo1.png ... photo4.png, photo2_charging.png ... (all = your image)
# AndroidManifest.xml:
#   <overlay android:targetPackage="android" android:isStatic="true" android:priority="99" />
#   <application android:hasCode="false" />

aapt2 compile --dir res -o compiled.zip
aapt2 link -o overlay-unsigned.apk --manifest AndroidManifest.xml \
      -I framework-res.apk --min-sdk-version 27 compiled.zip
java -jar signapk-1.0.jar navbar/keys/platform.x509.pem navbar/keys/platform.pk8 \
      overlay-unsigned.apk sleepoverlay.apk
```

Install into `/vendor/overlay` (match the existing SELinux context) and reboot:

```bash
adb push sleepoverlay.apk /sdcard/
adb shell 'su -c "mount -o rw,remount /vendor;
  cp /sdcard/sleepoverlay.apk /vendor/overlay/sleepoverlay.apk;
  chown root:root /vendor/overlay/sleepoverlay.apk; chmod 644 /vendor/overlay/sleepoverlay.apk;
  chcon u:object_r:vendor_overlay_file:s0 /vendor/overlay/sleepoverlay.apk;
  sync; mount -o ro,remount /vendor"'
adb reboot
adb shell 'cmd overlay list | grep example'   # -> [x] com.example.sleepoverlay  (enabled)
```

**Note:** on Android 8.1, OverlayManager only honors **static** overlays preinstalled in a trusted
partition. A `pm install`ed dynamic overlay targeting the framework is silently ignored — don't
waste time on it.

**Remove it** (back to stock animals):

```bash
adb shell su -c "mount -o rw,remount /vendor; rm /vendor/overlay/sleepoverlay.apk; sync" && adb reboot
```

## ❌ The method that BRICKS this device (DON'T)

Replacing `framework-res.apk` via a **Magisk module** (`/data/adb/modules/.../system/framework/
framework-res.apk`) boot-loops the EPD106 — `framework-res` is loaded too early for Magisk's mount
to be safe, and `system_server` crashes. The patched APK itself was *valid* (verified: only the 7
STORED `photoN` images swapped in place with corrected CRCs, `resources.arsc` byte-identical — see
`scripts/patch_framework.py`); the **mount mechanism** is the problem, not the content. We tried it,
it bricked, and we recovered with the [boot-window race](03-backup-and-recovery.md#recovering-from-a-boot-loop).
The script is included for reference and for devices that *do* tolerate it — **not** the EPD106.
