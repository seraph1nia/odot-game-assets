"""Execute the texture producer and decode its public PNG bytes."""
import hashlib
from pathlib import Path
import struct
import tempfile
import unittest
import zlib
from unittest.mock import patch
from dataclasses import replace

from . import art_style as style
from . import forest_decals as decals


def decode(data):
    if data[:8] != b'\x89PNG\r\n\x1a\n':
        raise ValueError('Not PNG')
    offset = 8
    compressed = b''
    width = height = None
    while offset < len(data):
        length = struct.unpack_from('>I', data, offset)[0]
        name = data[offset + 4:offset + 8]
        payload = data[offset + 8:offset + 8 + length]
        crc = struct.unpack_from('>I', data, offset + 8 + length)[0]
        if crc != zlib.crc32(name + payload):
            raise ValueError('PNG CRC mismatch')
        if name == b'IHDR':
            width, height, depth, color, *_ = struct.unpack('>IIBBBBB', payload)
            if (depth, color) != (8, 6):
                raise ValueError('Expected 8-bit RGBA')
        if name == b'IDAT':
            compressed += payload
        offset += 12 + length
    raw = zlib.decompress(compressed)
    stride = 1 + width * 4
    rows = [raw[row * stride:(row + 1) * stride] for row in range(height)]
    if not all(row[0] == 0 and len(row) == stride for row in rows):
        raise ValueError('Unexpected scanline/filter')
    return width, height, b''.join(row[1:] for row in rows)


class ForestDecalTests(unittest.TestCase):
    def test_public_pngs_have_straight_color_and_feathered_transparency(self):
        for name in decals.NAMES:
            with self.subTest(name=name):
                width, height, pixels = decode(decals.png(name, 96))
                self.assertEqual((width, height), (96, 96))
                alpha = pixels[3::4]
                self.assertEqual(max(alpha[:width]), 0)
                self.assertEqual(max(alpha[-width:]), 0)
                self.assertTrue(all(alpha[i * width] == alpha[i * width + width - 1] == 0 for i in range(height)))
                self.assertGreater(max(alpha), 45)
                self.assertLessEqual(max(alpha), round(255 * style.FOREST.decal_opacity))
                self.assertGreater(len(set(alpha)), 30)
                # Transparent RGB is deliberately colored, not premultiplied/black.
                self.assertGreater(sum(pixels[:3]), 0)
                self.assertEqual(pixels[:3], pixels[(width * height // 2) * 4: (width * height // 2) * 4 + 3])

    def test_build_writes_identical_source_export_pairs_and_bound_receipts(self):
        with tempfile.TemporaryDirectory() as tmp, patch.object(style, 'FOREST', replace(style.FOREST, decal_size=32)):
            first = decals.build(tmp)
            self.assertEqual(first, decals.build(tmp))
            self.assertEqual(len(first), 4)
            self.assertEqual(len({r['sha256'] for r in first}), 4)
            for record in first:
                source = (Path(tmp) / record['source']).read_bytes()
                self.assertEqual(source, (Path(tmp) / record['export']).read_bytes())
                self.assertEqual(hashlib.sha256(source).hexdigest(), record['sha256'])
                self.assertEqual(decode(source)[:2], (32, 32))

    def test_invalid_dimensions_and_names_fail(self):
        with self.assertRaises(ValueError):
            decals.png('rune_circle', 1)
        with self.assertRaises(ValueError):
            decals.coverage('unknown', 0, 0)


if __name__ == '__main__':
    unittest.main()
