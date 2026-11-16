#!/usr/bin/env python3
# Compare two Android boot partition dumps: parse header, find real image length,
# and report where/how much they differ.
import sys, struct, hashlib

def load(p): return open(p, "rb").read()

def parse(b):
    if b[:8] != b"ANDROID!":
        return None
    (kernel_sz, kernel_addr, ramdisk_sz, ramdisk_addr,
     second_sz, second_addr, tags_addr, page_sz) = struct.unpack("<8I", b[8:40])
    def pages(n): return (n + page_sz - 1)//page_sz
    total = page_sz  # header page
    for sz in (kernel_sz, ramdisk_sz, second_sz):
        total += pages(sz)*page_sz
    return dict(page_sz=page_sz, kernel_sz=kernel_sz, ramdisk_sz=ramdisk_sz,
                second_sz=second_sz, real_len=total)

a, b = load(sys.argv[1]), load(sys.argv[2])
print("file A:", sys.argv[1], len(a), "bytes")
print("file B:", sys.argv[2], len(b), "bytes")
for name, data in (("A", a), ("B", b)):
    h = parse(data)
    print(f"  {name} header: {h}")
ha, hb = parse(a), parse(b)
# first differing byte
first = next((i for i in range(min(len(a), len(b))) if a[i] != b[i]), -1)
print("first differing offset:", first)
if ha and hb:
    rl = max(ha["real_len"], hb["real_len"])
    ra, rb = a[:rl], b[:rl]
    print("real image len:", rl)
    print("real-image md5  A:", hashlib.md5(ra).hexdigest())
    print("real-image md5  B:", hashlib.md5(rb).hexdigest())
    print("real images identical:", ra == rb)
    # tail beyond real image
    print("tail(A) all-zero:", a[rl:].count(0) == len(a)-rl)
    print("tail(B) all-zero:", b[rl:].count(0) == len(b)-rl)
diffbytes = sum(1 for x, y in zip(a, b) if x != y)
print("total differing bytes:", diffbytes)
