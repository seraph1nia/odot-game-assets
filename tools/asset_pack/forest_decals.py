"""Four small transparent woodland decal source textures; no terrain projection.

Pure Python PNG authoring, no dependencies or schema changes. RGB is straight
sRGB and alpha is linear coverage, never premultiplied; color extends through
transparent pixels to avoid black fringes under linear/mip filtering.
"""
import argparse
import hashlib
import json
import math
from pathlib import Path
import struct
import zlib

from . import art_style as style

NAMES = ('rune_circle', 'moss_wash', 'fairy_ring', 'spore_growth')


def line_distance(x, y, a, b):
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = max(0, min(1, ((x - a[0]) * dx + (y - a[1]) * dy) / (dx * dx + dy * dy)))
    return math.hypot(x - a[0] - t * dx, y - a[1] - t * dy)


def coverage(kind, x, y):
    r, angle = math.hypot(x, y), math.atan2(y, x)
    if kind == 'rune_circle':
        ink = math.exp(-((r - .67) / .014) ** 2)
        ink *= .62 + .38 * math.sin(angle * 3 + .5) ** 2
        ink += .55 * math.exp(-((r - .46) / .010) ** 2)
        for i in range(6):
            a = i * math.tau / 6
            ca, sa = math.cos(a), math.sin(a)
            # Six modest glyph strokes; quiet center remains usable under a prop.
            points = [(.73 * ca, .73 * sa), (.81 * ca, .81 * sa)]
            ink = max(ink, math.exp(-(line_distance(x, y, *points) / .016) ** 2))
    elif kind == 'moss_wash':
        ink = 0
        for cx, cy, rx, ry in [(-.28, -.16, .28, .23), (.14, -.04, .36, .26),
                              (-.12, .29, .27, .17), (.35, .26, .16, .21)]:
            d = ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2
            ink = max(ink, math.exp(-d * d))
        ink *= .60 + .16 * math.sin(x * 19 + y * 8) + .12 * math.cos(y * 23 - x * 6)
    elif kind == 'fairy_ring':
        radius = .62 + .03 * math.sin(angle * 5) + .02 * math.cos(angle * 9)
        ink = .40 * math.exp(-((r - radius) / .044) ** 2)
        ink *= .28 + .72 * math.sin(angle * 7 + .4) ** 4
        for i in range(9):
            a = i * math.tau / 9 + .13 * math.sin(i)
            cx, cy = radius * math.cos(a), radius * math.sin(a)
            ink = max(ink, .72 * math.exp(-((x - cx) ** 2 + (y - cy) ** 2) / .0014))
    elif kind == 'spore_growth':
        ink = 0
        for i in range(7):
            a = i * 2.4
            end = (.51 * math.cos(a), .51 * math.sin(a))
            middle = (.28 * math.cos(a + .3), .28 * math.sin(a + .3))
            ink = max(ink, .65 * math.exp(-(line_distance(x, y, (0, 0), middle) / .013) ** 2),
                      .65 * math.exp(-(line_distance(x, y, middle, end) / .013) ** 2),
                      math.exp(-((x - end[0]) ** 2 + (y - end[1]) ** 2) / .0012))
        ink *= .82 + .18 * math.cos(x * 11 + y * 7)
    else:
        raise ValueError('Unknown forest decal: ' + kind)
    # Guard-band feathering: every image border is truly transparent.
    border = max(0, min(1, (1 - max(abs(x), abs(y))) / .16))
    return max(0, min(1, ink * border)) * style.FOREST.decal_opacity


def rgba(kind, size):
    color = (style.FOREST.leaf_tip if kind == 'moss_wash' else
             style.PAINTED_ACCENTS['rune_glow'][0] if kind == 'rune_circle' else
             style.FOREST.cap_purple_tip if kind == 'fairy_ring' else style.FOREST.gill_tip)
    rgb = bytes(round(c * 255) for c in color)
    pixels = bytearray()
    for row in range(size):
        y = 1 - 2 * row / (size - 1)
        for col in range(size):
            x = 2 * col / (size - 1) - 1
            pixels.extend(rgb)
            pixels.append(round(255 * coverage(kind, x, y)))
    return bytes(pixels)


def png(kind, size):
    if size < 2:
        raise ValueError('Decal dimensions must be at least two pixels')
    pixels = rgba(kind, size)
    def chunk(name, data):
        return struct.pack('>I', len(data)) + name + data + struct.pack('>I', zlib.crc32(name + data))
    scanlines = b''.join(b'\0' + pixels[i:i + size * 4] for i in range(0, len(pixels), size * 4))
    return (b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', size, size, 8, 6, 0, 0, 0)) +
            chunk(b'sRGB', b'\0') + chunk(b'IDAT', zlib.compress(scanlines, 9)) + chunk(b'IEND', b''))


def build(root):
    root = Path(root)
    records = []
    for name in NAMES:
        data = png(name, style.FOREST.decal_size)
        paths = [f'{folder}/environment/decals/forest_decal_{name}.png' for folder in ('sources', 'exports')]
        for path in paths:
            target = root / path
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(data)
        records.append({'name': name, 'source': paths[0], 'export': paths[1],
                        'sha256': hashlib.sha256(data).hexdigest(), 'bytes': len(data),
                        'size': [style.FOREST.decal_size] * 2, 'channels': 'straight sRGB RGB / linear coverage alpha'})
    return records


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--root', type=Path, default=Path(__file__).resolve().parents[2])
    args = parser.parse_args()
    records = build(args.root)
    output = args.root / 'docs/dreamlike-forest/decals.json'
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(records, indent=2) + '\n')
    print('Authored four transparent source/export PNGs:', sum(r['bytes'] for r in records), 'bytes per set')


if __name__ == '__main__':
    main()
