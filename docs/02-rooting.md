# 02 — Rooting (Magisk, no bootloader unlock)

**Principle:** the firmware is AOSP **test-key** signed, so a self-signed OTA zip is accepted by
stock recovery's *Apply update from ADB*. You flash a **Magisk-patched copy of your own boot
partition**. No unlock, no fastboot flash, no FEL, no PhoenixSuit.

> 🔑 **Golden rule:** patch **your own** boot image. On the test unit the real boot differed from
> the reference repo's (different kernel size!) despite an identical build fingerprint. Flashing a
> foreign patched boot is how you get a boot-loop.

## Step 0 — Prove the signing pipeline (no device risk)

Build and sign the **stock-restore** zip first (`scripts/build-flash-zip.py` +
`root/toolkit/restore-updater-script` + the repo's `zzboot.img`, signed with the testkey). If it
produces a valid zip whose inner `boot.img` md5 matches the repo's stock, your JRE-8 + signapk
toolchain works. Keep this zip — it's your safety net.

## Step 1 — Dump YOUR boot (read-only)

```bash
adb reboot recovery
# On the reader: select "Apply update from ADB"
adb sideload edp106/root/toolkit/dump_kernel_to_system_signed.zip
# Reboot to system, then:
adb pull /system/bimg.img my-stock-boot.img
md5sum my-stock-boot.img    # <-- THIS is your stock boot. Save it forever.
```

Compare against the repo's reference boot with `scripts/cmp-boot.py`. If they differ (they did for
us), you **must** patch your own — continue below. If identical, you *may* use the repo's
`magisk_patched.img`, but patching your own is always safe.

## Step 2 — Patch YOUR boot with Magisk (unprivileged, on-device)

Extract from `Magisk-v28.1.apk` (it's a zip) the `armeabi-v7a` libs and assets, rename, and push
to `/data/local/tmp/mboot/` along with your `my-stock-boot.img` (as `bimg.img`):

```
magiskboot  <- lib/armeabi-v7a/libmagiskboot.so
magiskinit  <- lib/armeabi-v7a/libmagiskinit.so
magisk      <- lib/armeabi-v7a/libmagisk.so
init-ld     <- lib/armeabi-v7a/libinit-ld.so
stub.apk    <- assets/stub.apk
boot_patch.sh, util_functions.sh  <- assets/
```

Then run Magisk's own patcher (no root needed — it only manipulates the file):

```bash
adb shell 'cd /data/local/tmp/mboot && chmod 755 magisk* init-ld boot_patch.sh && \
  KEEPVERITY=true KEEPFORCEENCRYPT=true PATCHVBMETAFLAG=false RECOVERYMODE=false LEGACYSAR=false \
  sh boot_patch.sh bimg.img'
adb pull /data/local/tmp/mboot/new-boot.img my-magisk-patched-boot.img
```

`KEEPVERITY=true KEEPFORCEENCRYPT=true` is the conservative choice here (no dm-verity/AVB to
remove, and it avoids touching the fstab). A correct patch keeps the **kernel byte-identical** and
only grows the **ramdisk**.

## Step 3 — Build + sign the flash zips

With `scripts/build-flash-zip.py` (template + `restore-updater-script` + your boot, **STORED**,
then sign with the testkey via `signapk` on JRE 8):

- **ROOT zip** — inner `boot.img` = `my-magisk-patched-boot.img`
- **RESTORE zip** — inner `boot.img` = `my-stock-boot.img` (escape hatch — build it *before* flashing)

Verify each zip's inner `boot.img` md5 matches what you intended.

## Step 4 — Flash root

```bash
adb reboot recovery            # select "Apply update from ADB" on the reader
adb sideload ROOT-install-magisk.zip
# On the reader: "Reboot system now"
```

If it boots to your launcher → rooted. If it boot-loops →
[recovery](03-backup-and-recovery.md#recovering-from-a-boot-loop).

## Step 5 — Finish Magisk setup

1. `adb install Magisk-v28.1.apk`
2. Open Magisk → it shows **"Requires Additional Setup"** → tap **OK** (it reflashes the working
   boot with preinit storage configured and reboots). Root is denied until this is done.
3. Grant ADB root: Magisk **Superuser access** is already *Apps and ADB*, but
   **Tapjacking Protection** (on by default) blocks *automated* taps on the grant prompt — so a
   finger tap is needed. Easiest: trigger `adb shell su -c id`, then in the Magisk app's
   **Superuser** tab toggle **Shell** on. Verify:

```bash
adb shell 'su -c "id"'   # uid=0(root) ... context=u:r:magisk:s0
```

Done. `magisk -V` → `28100`.
