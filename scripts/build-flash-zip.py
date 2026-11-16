#!/usr/bin/env python3
# Build an unsigned OTA zip that writes a given boot image to the boot partition.
# Usage: build-flash-zip.py <template.zip> <updater-script> <boot.img> <out-unsigned.zip>
import sys, zipfile

template, updater_path, boot_path, out = sys.argv[1:5]
updater = open(updater_path, "rb").read()
boot_img = open(boot_path, "rb").read()

with zipfile.ZipFile(template) as src, \
     zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as dst:
    for entry in src.infolist():
        data = updater if entry.filename.endswith("updater-script") else src.read(entry.filename)
        dst.writestr(entry, data)
    boot = zipfile.ZipInfo("boot.img")
    boot.compress_type = zipfile.ZIP_STORED
    dst.writestr(boot, boot_img)
print("  boot.img %d bytes (STORED), updater %d bytes" % (len(boot_img), len(updater)))
