# 03 — Backup & Recovery

## Back up BEFORE flashing

User data lives in `/data` and is **not touched** by any boot flashing — but back it up anyway.

```bash
# Internal storage (books, KOReader settings/progress, fonts, dictionaries)
adb pull /sdcard/.  backup/sdcard/
# Installed user apps
for p in $(adb shell pm list packages -3 | sed 's/package://' | tr -d '\r'); do
  adb pull "$(adb shell pm path $p | sed 's/package://' | tr -d '\r')" "backup/apks/$p.apk"; done
# State you can't recompute
adb shell pm list packages -u | sort > backup/packages-including-uninstalled.txt
for n in system secure global; do adb shell settings list $n > backup/settings-$n.txt; done
adb shell getprop > backup/getprop.txt
```

> **Windows filename gotcha:** a KOReader book name can contain a literal newline, which Windows
> can't write (the pull aborts mid-directory). Pull folder-by-folder; for the offending file,
> `cp` it to a temp name on-device first, then pull that.

## After root, back up partitions

With root you can image the small partitions (keep these — some have no other recovery path):

```bash
adb shell 'su -c "dd if=/dev/block/by-name/recovery of=/sdcard/recovery.img;
                  dd if=/dev/block/by-name/bootloader of=/sdcard/bootloader.img;
                  dd if=/dev/block/by-name/env of=/sdcard/env.img; chmod 644 /sdcard/*.img"'
# pull them, then delete from /sdcard
```

Your **`my-stock-boot.img`** (from [02](02-rooting.md)) is the most important file — it's the only
thing that restores *your* exact boot.

## The stock-boot restore zip

The `RESTORE-...zip` you built in [02 step 3](02-rooting.md#step-3--build--sign-the-flash-zips)
writes your stock boot back, removing Magisk:

```bash
adb reboot recovery            # "Apply update from ADB"
adb sideload RESTORE-my-stock-boot.zip
```

This un-roots but always boots (no Magisk → no modules → stock behavior).

## Recovering from a boot-loop

If a **Magisk module** breaks boot (see [04](04-sleep-screen.md) — the `framework-res` module
does), you don't have to lose root or data. During every boot *attempt*, `adbd` and `magiskd` come
up for a few seconds **before** the crash. Race them:

```bash
# Keep tapping "Try again" on the reader. Meanwhile, on the host:
for i in $(seq 1 240); do
  st=$(timeout 2 adb get-state 2>/dev/null)
  if [ -n "$st" ]; then
    adb shell 'su -c "rm -rf /data/adb/modules/<bad_module> && echo REMOVED"' && break
  fi
done
adb reboot
```

On the test unit this caught the window on the **first** attempt and removed the bad module with
root and all data intact. (If you can't catch it, sideload the stock-boot restore zip instead —
without Magisk the module never mounts, so the device boots; then remove the module and re-root.)

**Never tap "Factory reset"** on the "Can't load Android system" screen — the recovery above keeps
your data.
