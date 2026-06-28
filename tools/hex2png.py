#!/usr/bin/env python3
# Convert an ats-mini serial screenshot (HEX BMP dump from the 'C' command)
# into a PNG. Stdlib only (zlib). Pixels are RGB565, byte-swapped (htons),
# rows emitted bottom-up.
#
# Usage:  python hex2png.py screenshot.hex screenshot.png
import sys, zlib, struct, re

WIDTH, HEIGHT = 320, 170

def main(hexpath, pngpath):
    raw = open(hexpath, "r", errors="ignore").read()
    lines = [l.strip() for l in raw.splitlines() if l.strip()]
    rows = [l for l in lines if len(l) == WIDTH * 4 and re.fullmatch(r"[0-9a-fA-F]+", l)]
    if len(rows) < HEIGHT:
        print(f"WARN: only {len(rows)} pixel rows (expected {HEIGHT})", file=sys.stderr)
    rows = rows[:HEIGHT][::-1]  # take first frame, flip bottom-up -> top-down

    out = bytearray()
    for row in rows:
        b = bytes.fromhex(row)
        for i in range(0, len(b), 2):
            v = (b[i + 1] << 8) | b[i]        # undo htons byte-swap
            r = ((v >> 11) & 0x1F) << 3
            g = ((v >> 5) & 0x3F) << 2
            bl = (v & 0x1F) << 3
            out += bytes((r | (r >> 5), g | (g >> 6), bl | (bl >> 5)))
    rowbytes = WIDTH * 3
    while len(out) < rowbytes * HEIGHT:
        out += b"\x00" * rowbytes

    def chunk(typ, data):
        c = typ + data
        return struct.pack(">I", len(data)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)

    sig = b"\x89PNG\r\n\x1a\n"
    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    scan = bytearray()
    for y in range(HEIGHT):
        scan += b"\x00" + out[y * rowbytes:(y + 1) * rowbytes]
    idat = zlib.compress(bytes(scan), 9)
    png = sig + chunk(b"IHDR", ihdr) + chunk(b"IDAT", idat) + chunk(b"IEND", b"")
    open(pngpath, "wb").write(png)
    print(f"OK -> {pngpath} ({WIDTH}x{HEIGHT}, {len(rows)} rows)")

if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
