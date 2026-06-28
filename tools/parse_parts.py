#!/usr/bin/env python3
# Parse the ESP32 partition table from a full flash dump and list partitions,
# plus scan for known filenames. Handy for inspecting a firmware backup.
#
# Usage:  python parse_parts.py firmware-full-8MB.bin
# To extract a FAT (ffat) partition afterwards, carve [off, off+size) to a
# .img and open it with 7-Zip:  7z x part.img -ofiles
import sys, struct

img = open(sys.argv[1], "rb").read()
TYPES = {0: "app", 1: "data"}
SUB = {0x82: "spiffs", 0x81: "fat", 0x80: "ota", 0x02: "nvs", 0x03: "coredump"}

base = 0x8000
print(f"image size: {len(img)} bytes")
print("--- partition table @0x8000 ---")
for i in range(0, 0xC00, 32):
    e = img[base + i: base + i + 32]
    if e[:2] != b"\xAA\x50":
        break
    ptype, subtype = e[2], e[3]
    offset, size = struct.unpack("<II", e[4:12])
    label = e[12:28].split(b"\x00")[0].decode("ascii", "replace")
    print(f"  {label:12s} type={TYPES.get(ptype,ptype)} sub=0x{subtype:02x}({SUB.get(subtype,'?')}) "
          f"off=0x{offset:06x} size=0x{size:06x} ({size//1024}KB)")

print("--- filename strings present ---")
for name in [b"hardcopy.bmp", b"eibi.txt", b"playlist.txt", b"etm.txt",
             b"logfile.txt", b"settings.txt", b"stations.txt", b"user.txt"]:
    n = img.count(name)
    if n:
        print(f"  {name.decode():14s} x{n}  first@0x{img.find(name):06x}")
