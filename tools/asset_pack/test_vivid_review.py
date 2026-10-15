"""Current palette receipt contracts and UI-only color restoration behavior."""
import hashlib
import json
import unittest
from pathlib import Path

from tools.asset_pack import art_style as style
from tools.ui.vivid_refinement import recover_colors

ROOT = Path(__file__).resolve().parents[2]


class VividContracts(unittest.TestCase):
    def test_role_palette_is_colorful_without_flat_primaries(self):
        for name in ('leaf_color', 'leaf_tip', 'cloth_color', 'porch_ochre', 'orb_color'):
            color = getattr(style.VIVID, name)
            self.assertGreater(max(color) - min(color), .2)
            self.assertTrue(all(.05 < channel < .95 for channel in color))

    def test_ui_recovery_changes_only_hex_colors_not_geometry_or_opacity(self):
        current = '<path d="M0 1L2 3" fill="#888888" opacity=".42"/>'
        original = '<path d="M0 1L2 3" fill="#aaff44" opacity=".60"/>'
        result = recover_colors(current, original)
        self.assertEqual(result, '<path d="M0 1L2 3" fill="#aaff44" opacity=".42"/>')
        with self.assertRaises(ValueError):
            recover_colors(current, original + '<path fill="#123456"/>')

    def test_actual_render_receipts_bind_current_exports_and_every_derivative(self):
        baseline = json.loads((ROOT / 'docs/vivid-palette/baseline.json').read_text())
        renders = json.loads((ROOT / 'docs/vivid-palette/renders.json').read_text())['assets']
        self.assertEqual(set(renders), {j['id'] for j in baseline['jobs']})
        renderer = hashlib.sha256((''.join(hashlib.sha256((ROOT / p).read_bytes()).hexdigest()
            for p in ('tools/asset_catalog/render_blender.py', 'tools/asset_pack/woodland_render.py'))).encode()).hexdigest()
        for aid, record in renders.items():
            with self.subTest(asset=aid):
                self.assertEqual(record['after']['export_sha256'], hashlib.sha256((ROOT / 'exports' / (aid + '.glb')).read_bytes()).hexdigest())
                for stage in ('before', 'after'):
                    view = record[stage]
                    self.assertEqual(view['renderer_sha256'], renderer)
                    self.assertEqual(view['image_sha256'], hashlib.sha256((ROOT / view['image']).read_bytes()).hexdigest())
                    self.assertEqual(len(view['derived_images']), 2)
                    for path, digest in view['derived_images'].items():
                        self.assertEqual(digest, hashlib.sha256((ROOT / path).read_bytes()).hexdigest())
                self.assertEqual(record['resources_before'], record['resources_after'])
        inventory = json.loads((ROOT / 'docs/vivid-palette/inventory.json').read_text())
        self.assertEqual(len(inventory['assets']), 133)
        self.assertEqual(len({r['id'] for r in inventory['assets']}), 133)

    def test_all_current_sources_bind_strict_preservation_receipts(self):
        baseline = json.loads((ROOT / 'docs/vivid-palette/baseline.json').read_text())
        authored = json.loads((ROOT / 'docs/vivid-palette/authored.json').read_text())
        self.assertEqual(len(baseline['jobs']), 118)
        self.assertEqual(set(authored), {j['source'] for j in baseline['jobs']})
        for path, record in authored.items():
            with self.subTest(source=path):
                self.assertEqual(record['sha256_before'], baseline['files'][path])
                self.assertEqual(record['sha256_after'], hashlib.sha256((ROOT / path).read_bytes()).hexdigest())
                self.assertTrue(record['geometry_uv_hierarchy_reuse_rigs_actions_preserved'])
                self.assertTrue(record['roughness_normal_pixels_preserved'])
                self.assertIn('protected_orphan_ids', record)
                for mat in record['materials']:
                    for channel in mat.get('channels', []):
                        if image := channel.get('map'):
                            self.assertTrue(image['alpha_preserved'])
                            self.assertTrue(image['packed'])


if __name__ == '__main__':
    unittest.main()
