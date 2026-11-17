# 01 — Device & Prerequisites

## Confirm your device matches

Connect over USB with **USB debugging** enabled, then:

```bash
adb shell getprop ro.build.fingerprint
# expect: Allwinner/virgo_perf1/virgo-perf1:8.1.0/OPM1.171019.026/20220520-132139:user/test-keys
adb shell getprop ro.build.tags        # expect: test-keys   <- required (public AOSP keys)
adb shell getprop ro.boot.hardware     # expect: sun8iw15p1
```

The **`test-keys`** build tag is what makes this whole approach possible. If your tag is
`release-keys`, the self-signed-OTA method will **not** work and nothing here applies.

Check the partition layout (you need the `boot` block device):

```bash
adb shell ls -l /dev/block/by-name
# boot -> /dev/block/mmcblk0p4   (this is what you patch)
```

## Host tools

| Tool | Why | Notes |
|---|---|---|
| **ADB + Fastboot** (platform-tools) | talk to the device | `adb devices` must show your reader |
| **JDK or JRE 8** | `signapk` reaches into `sun.security.pkcs`, removed in JDK 9+ | a plain **JRE 8** is enough |
| **Python 3** | build zips, patch images, render the sleep screen | |
| **aapt2** | build the RRO overlay (sleep screen) | from Google Maven: `com/android/tools/build/aapt2/<ver>/aapt2-<ver>-windows.jar` (the jar contains `aapt2.exe`) |
| **Magisk app APK** | the root engine | use **v28.1** (known-good here): `github.com/topjohnwu/Magisk/releases` |
| **git / curl / unzip** | fetch toolkits | |

Python package (for rendering the sleep-screen image):

```bash
pip install pillow
```

## The device-specific toolkit

Clone the reference repo — it has the `update-binary`, `signapk`, the **AOSP testkey**, and a
flashing-zip template that stock recovery accepts:

```bash
git clone --depth 1 https://github.com/delbertbeta/edp106.git
```

Key files you'll use:
- `root/toolkit/kernel_flashing_template.zip` — recovery-accepted OTA skeleton
- `root/toolkit/restore-updater-script` — writes `boot.img` to the boot partition
- `root/toolkit/signapk-1.0.jar`, `root/toolkit/testkey.{pk8,x509.pem}` — self-sign OTA zips
- `root/toolkit/dump_kernel_to_system_signed.zip` — dumps your boot to `/system/bimg.img`
- `navbar/keys/platform.{pk8,x509.pem}` — the **platform** key (needed for the sleep-screen overlay)

> **Windows / Git Bash note:** native tools (`python`, `java`, `adb`) need Windows-style paths.
> When a path is a device path (e.g. `/system/bimg.img`) wrap the command with `MSYS_NO_PATHCONV=1`
> and convert local paths with `cygpath -w`. Mixing these up silently corrupts paths.
