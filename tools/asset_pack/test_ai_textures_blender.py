"""Isolated cache/transition fixtures; creates only temporary maps and materials."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import numpy as np

from tools.asset_pack.ai_texture_blender import managed_image, ground_color


class TextureFixtures(unittest.TestCase):
    def test_owned_content_cache_is_idempotent_and_rejects_stale_external_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            directory = Path(temp)
            values = np.full((32, 32, 3), .24, dtype=np.float32)
            image = managed_image('ai_fixture_cache', values, directory)
            try:
                self.assertIs(managed_image('ai_fixture_cache', values, directory), image)
                with self.assertRaises(AssertionError):
                    managed_image('ai_fixture_cache', values * .5, directory)
                (directory / 'ai_fixture_cache.png').write_bytes(b'stale')
                with self.assertRaises(AssertionError):
                    managed_image('ai_fixture_cache', values, directory)
            finally:
                bpy.data.images.remove(image)

    def test_foreign_named_image_is_never_reused(self):
        image = bpy.data.images.new('foreign_fixture', width=32, height=32)
        try:
            with tempfile.TemporaryDirectory() as temp, self.assertRaises(AssertionError):
                managed_image('foreign_fixture', np.zeros((32, 32, 3)), Path(temp))
        finally:
            bpy.data.images.remove(image)

    def test_ribbon_endpoints_banks_and_floor_edge_fades(self):
        original = np.full((128, 128, 3), .1)
        supplied = np.full((128, 128, 3), .8)
        for family in ('river', 'path'):
            result = ground_color(family, original, supplied)
            np.testing.assert_array_equal(result[0], original[0])
            np.testing.assert_array_equal(result[-1], original[-1])
            self.assertGreater(result[64, 64, 0], original[64, 64, 0])
            if family == 'river':
                np.testing.assert_array_equal(result[:, 0], original[:, 0])
                np.testing.assert_array_equal(result[:, -1], original[:, -1])
        floor = ground_color('moss', original, supplied)
        self.assertLess(floor[0, 0, 0], floor[64, 64, 0])


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(TextureFixtures)
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
        raise SystemExit(1)
