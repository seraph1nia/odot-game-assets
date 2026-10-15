"""Exact encoded-map protocol: PNG predictors, alpha, identity and mutations."""
import hashlib
from types import SimpleNamespace
import struct
import unittest
import zlib

from tools.asset_pack.encoded_images import UnsupportedImage, image_proof, png_proof


def chunk(kind, data):
    return struct.pack('>I', len(data)) + kind + data + struct.pack('>I', zlib.crc32(kind + data))


def png(rows, *, mode=0, color=6, depth=8):
    channels = {0: 1, 2: 3, 3: 1, 4: 2, 6: 4}[color]
    width = len(rows[0]) // channels; encoded = bytearray(); previous = bytes(len(rows[0]))
    for row in rows:
        encoded.append(mode)
        for i, value in enumerate(row):
            left = row[i - channels] if i >= channels else 0
            up = previous[i]; corner = previous[i - channels] if i >= channels else 0
            predictors = (0, left, up, (left + up) // 2)
            if mode == 4:
                p = left + up - corner
                candidates = (left, up, corner)
                predictor = min(enumerate(candidates), key=lambda item: (abs(p - item[1]), item[0]))[1]
            else:
                predictor = predictors[mode]
            encoded.append((value - predictor) & 255)
        previous = row
    return b'\x89PNG\r\n\x1a\n' + chunk(b'IHDR', struct.pack('>IIBBBBB', width, len(rows), depth, color, 0, 0, 0)) + chunk(b'IDAT', zlib.compress(encoded)) + chunk(b'IEND', b'')


def fake_image(data, **changes):
    settings = {'name': 'packed test map', 'source': 'FILE', 'is_float': False,
                'packed_file': SimpleNamespace(data=data), 'size': (3, 2),
                'colorspace_settings': SimpleNamespace(name='Non-Color'),
                'alpha_mode': 'STRAIGHT', 'use_view_as_render': False}
    settings.update(changes)
    return SimpleNamespace(**settings)


class EncodedImageContracts(unittest.TestCase):
    rows = [bytes((1, 33, 200, 0, 255, 127, 41, 125, 16, 80, 252, 255)),
            bytes((203, 7, 19, 1, 41, 249, 55, 127, 9, 111, 230, 254))]

    def test_all_five_png_filters_decode_exact_samples_and_alpha_without_floats(self):
        expected = b''.join(self.rows)
        for mode in range(5):
            proof = png_proof(png(self.rows, mode=mode))
            self.assertEqual(proof['samples_sha256'], hashlib.sha256(expected).hexdigest())
            self.assertEqual(proof['alpha_sha256'], hashlib.sha256(expected[3::4]).hexdigest())
            self.assertEqual(proof['dimensions'], [3, 2])
            self.assertEqual(proof['channels'], 4)
            self.assertEqual(proof['bit_depth'], 8)
            self.assertEqual(png_proof(png(self.rows, mode=mode), alpha_only=True)['alpha_sha256'], proof['alpha_sha256'])

    def test_repeated_identical_maps_match_and_one_encoded_sample_mutation_does_not(self):
        data = png(self.rows, mode=4); baseline = image_proof(fake_image(data))
        for _ in range(20):
            self.assertEqual(image_proof(fake_image(bytes(bytearray(data)))), baseline)
        changed = [bytearray(r) for r in self.rows]; changed[0][0] += 1
        observed = image_proof(fake_image(png(changed, mode=4)))
        self.assertNotEqual(observed['packed_sha256'], baseline['packed_sha256'])
        self.assertNotEqual(observed['samples_sha256'], baseline['samples_sha256'])
        self.assertEqual(observed['alpha_sha256'], baseline['alpha_sha256'])
        changed[0][3] = 1
        self.assertNotEqual(image_proof(fake_image(png(changed)))['alpha_sha256'], baseline['alpha_sha256'])

    def test_color_space_use_state_and_recompression_are_not_ignored(self):
        data = png(self.rows); baseline = image_proof(fake_image(data))
        self.assertNotEqual(image_proof(fake_image(data, colorspace_settings=SimpleNamespace(name='sRGB'))), baseline)
        self.assertNotEqual(image_proof(fake_image(data, alpha_mode='PREMUL')), baseline)
        self.assertNotEqual(image_proof(fake_image(data, use_view_as_render=True)), baseline)
        alternate = image_proof(fake_image(png(self.rows, mode=1)))
        self.assertEqual(alternate['samples_sha256'], baseline['samples_sha256'])
        self.assertNotEqual(alternate['packed_sha256'], baseline['packed_sha256'])

    def test_unsupported_or_malformed_representations_fail_closed(self):
        data = png(self.rows)
        for changes in ({'source': 'GENERATED'}, {'is_float': True}, {'packed_file': None}):
            with self.assertRaises(UnsupportedImage):
                image_proof(fake_image(data, **changes))
        with self.assertRaises(UnsupportedImage):
            png_proof(png(self.rows, depth=16))
        with self.assertRaises(ValueError):
            image_proof(fake_image(data, size=(4, 2)))
        with self.assertRaises(ValueError):
            png_proof(data[:-1] + b'!')


if __name__ == '__main__':
    unittest.main()
