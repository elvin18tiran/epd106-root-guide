#!/usr/bin/env python3
# Surgically replace STORED png entries in an apk/zip IN PLACE:
#   same byte length (new png zero-padded to the original entry size),
#   local-header + central-directory CRC-32 updated, every offset unchanged.
# Usage: patch_framework.py <in.apk> <out.apk> <new.png> name1 name2 ...
import sys, zlib, struct, zipfile

in_apk, out_apk, new_png = sys.argv[1:4]
names = sys.argv[4:]
png = open(new_png, "rb").read()

buf = bytearray(open(in_apk, "rb").read())

# map name -> (header_offset, stored_size, compress_type) via zipfile
info = {}
with zipfile.ZipFile(in_apk) as z:
    for zi in z.infolist():
        if zi.filename in names:
            info[zi.filename] = (zi.header_offset, zi.compress_type, zi.file_size, zi.compress_size)

for n in names:
    if n not in info:
        sys.exit(f"ERROR: entry not found: {n}")
    ho, comp, usize, csize = info[n]
    if comp != 0:
        sys.exit(f"ERROR: {n} is not STORED (compress_type={comp})")
    if len(png) > csize:
        sys.exit(f"ERROR: new png {len(png)} > target {csize} for {n}")
    # local header: PK\x03\x04 ; fname len @26(2), extra len @28(2); data after
    assert buf[ho:ho+4] == b"PK\x03\x04", f"bad local header at {ho}"
    fnlen = struct.unpack_from("<H", buf, ho + 26)[0]
    exlen = struct.unpack_from("<H", buf, ho + 28)[0]
    data_start = ho + 30 + fnlen + exlen
    padded = png + b"\x00" * (csize - len(png))
    buf[data_start:data_start + csize] = padded
    crc = zlib.crc32(padded) & 0xffffffff
    struct.pack_into("<I", buf, ho + 14, crc)   # local header CRC
    print(f"  {n}: wrote {len(png)} + pad {csize-len(png)} = {csize}, crc {crc:08x}")

# update central directory CRCs. Find EOCD (PK\x05\x06) scanning from end.
eocd = buf.rfind(b"PK\x05\x06")
assert eocd != -1, "no EOCD"
cd_size, cd_off = struct.unpack_from("<II", buf, eocd + 12)
p = cd_off
updated = 0
while p < cd_off + cd_size and buf[p:p+4] == b"PK\x01\x02":
    fnlen = struct.unpack_from("<H", buf, p + 28)[0]
    exlen = struct.unpack_from("<H", buf, p + 30)[0]
    cmlen = struct.unpack_from("<H", buf, p + 32)[0]
    name = buf[p + 46:p + 46 + fnlen].decode("utf-8", "replace")
    if name in names:
        padded_len = info[name][3]
        ho = info[name][0]
        # recompute crc from the data we just wrote
        fnl2 = struct.unpack_from("<H", buf, ho + 26)[0]
        exl2 = struct.unpack_from("<H", buf, ho + 28)[0]
        ds = ho + 30 + fnl2 + exl2
        crc = zlib.crc32(bytes(buf[ds:ds + padded_len])) & 0xffffffff
        struct.pack_into("<I", buf, p + 16, crc)  # central dir CRC
        updated += 1
    p += 46 + fnlen + exlen + cmlen

print(f"central-dir CRCs updated: {updated}/{len(names)}")
open(out_apk, "wb").write(buf)
print("wrote", out_apk, len(buf), "bytes (same size as input:", len(buf) == len(open(in_apk,'rb').read()), ")")
