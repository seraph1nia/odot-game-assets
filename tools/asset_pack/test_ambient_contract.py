"""Catalog-wide actual-clip, ownership, preservation and receipt freshness gates."""
from dataclasses import asdict
import hashlib
import json
import math
import struct
import unittest
from pathlib import Path

from tools.asset_pack import art_style as style
from tools.asset_pack.encoded_images import png_proof
from tools.asset_pack.runtime_contract import export_chain
from tools.asset_pack.ambient_contract import ASSETS, BUILDINGS, WATER, expected_resource_delta, receipts, sha, source_chain

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/ambient-motion'


def glb(path):
    data = path.read_bytes()
    length = struct.unpack_from('<I', data, 12)[0]
    return json.loads(data[20:20 + length])


class AmbientContracts(unittest.TestCase):
    def test_every_catalogued_building_and_all_water_roles_are_covered(self):
        associations = json.loads((ROOT / 'catalog/associations.json').read_text())['assets']
        buildings = {p.removeprefix('exports/buildings/').removesuffix('.glb') for p in associations if p.startswith('exports/buildings/')}
        self.assertEqual(buildings, set(BUILDINGS))
        self.assertEqual(len(BUILDINGS), 16)
        self.assertEqual(len(WATER), 9)
        for aid in ASSETS:
            self.assertEqual(associations['exports/' + aid + '.glb']['animation_policy'], {'ambient': True})

    def test_actual_exported_clips_are_small_finite_object_actions_not_root_motion(self):
        for aid in ASSETS:
            with self.subTest(asset=aid):
                doc = glb(ROOT / 'exports' / (aid + '.glb'))
                self.assertEqual([a['name'] for a in doc['animations']], [style.AMBIENT.clip])
                action = doc['animations'][0]
                self.assertTrue(action['extras']['loop'])
                self.assertTrue(action['channels'])
                for channel in action['channels']:
                    self.assertIn(channel['target']['path'], ('translation', 'rotation'))
                    self.assertNotEqual(doc['nodes'][channel['target']['node']]['name'], aid.split('/')[-1] + '_root')
                for sampler in action['samplers']:
                    accessor = doc['accessors'][sampler['input']]
                    self.assertLessEqual(accessor['count'], 97)  # existing official exporter samples 24 FPS
                    self.assertGreaterEqual(accessor['count'], 5)
                    self.assertTrue(all(math.isfinite(v) for v in accessor['min'] + accessor['max']))
                    self.assertAlmostEqual(accessor['max'][0] - accessor['min'][0], 4.0, places=6)

    def test_source_edit_and_independent_playback_receipts_bind_current_bytes(self):
        authored = receipts(ROOT)
        validation = json.loads((DOCS / 'validation.json').read_text())
        palette = json.loads((ROOT / 'docs/vivid-palette/authored.json').read_text())
        self.assertEqual(len(authored), 23)
        self.assertEqual(set(validation['sources']), set(authored))
        self.assertEqual(set(validation['assets']), set(ASSETS))
        features = {f['asset']: f for r in authored.values() for f in r['features']}
        self.assertEqual(set(features), set(ASSETS))
        for path, record in authored.items():
            source_chain(ROOT, path, palette[path]['sha256_after'])
            verified = validation['sources'][path]
            self.assertEqual(verified['sha256_before'], record['sha256_before'])
            self.assertEqual(verified['sha256_after'], sha(ROOT / path))
            self.assertTrue(verified['all_original_ids_retained'])
            self.assertTrue(verified['all_original_full_materials_and_images_equal'])
            self.assertTrue(verified['original_geometry_uv_reuse_rigs_actions_equal'])
            self.assertLess(verified['original_rest_matrix_max_error'], 2e-6)
            for feature in record['features']:
                if feature['asset'].startswith('buildings/'):
                    self.assertIsNotNone(feature['pivot'])
                    self.assertEqual(len(feature['channels']), 1)
                for channel in feature['channels']:
                    self.assertEqual(channel['keys_per_channel'], 5)
        for aid, result in validation['assets'].items():
            export_chain(ROOT, aid, result['glb_sha256'])
            self.assertTrue(result['source_and_export_meshes_move'])
            self.assertTrue(result['source_and_export_endpoints_equal'])
            self.assertTrue(result['fixed_objects_world_matrices_equal_throughout'])
            self.assertLess(result['evaluated_pose_point_cloud_max_error_m'], .0001)

    def test_actual_motion_render_derivatives_bind_current_exports_and_fixed_recipe(self):
        renders = json.loads((DOCS / 'renders.json').read_text())
        renderer = hashlib.sha256((''.join(sha(ROOT / p) for p in
            ('tools/asset_pack/render_ambient_blender.py', 'tools/asset_catalog/render_blender.py'))
            + json.dumps(asdict(style.AMBIENT), sort_keys=True)).encode()).hexdigest()
        self.assertEqual(set(renders), set(ASSETS))
        for aid, record in renders.items():
            # These are retained landed-detail renders, not relabeled runtime views.
            export_chain(ROOT, aid, record['export_sha256'])
            self.assertEqual(record['renderer_sha256'], renderer)
            self.assertEqual(len(record['files']), 8)
            for path, digest in record['files'].items():
                self.assertEqual(sha(ROOT / path), digest)
            prefix = 'docs/ambient-motion/evidence/' + aid + '/frame-'
            # PNG metadata and renderer sampling are not a clip-closure contract.
            # Exact source/export mesh endpoints are tested by the playback audit.
            for frame in ('001', '025', '049', '073', '097'):
                proof = png_proof((ROOT / (prefix + frame + '.png')).read_bytes())
                self.assertEqual(proof['dimensions'], [360, 360])
            self.assertNotEqual(record['files'][prefix + '025.png'], record['files'][prefix + '073.png'])

    def test_geometry_growth_is_explicitly_limited_to_four_small_water_glints(self):
        authored = receipts(ROOT)
        additions = [f['added_geometry'] for r in authored.values() for f in r['features'] if f['added_geometry']]
        self.assertEqual(len(additions), 4)
        self.assertEqual(sum(a['triangles'] for a in additions), 32)
        for aid in ASSETS:
            delta = expected_resource_delta(aid)
            self.assertEqual(delta['triangles'], 8 if aid.startswith('environment/hex_river_overlay_') else 0)
        renders = json.loads((ROOT / 'docs/vivid-palette/renders.json').read_text())['assets']
        for aid, record in renders.items():
            delta = expected_resource_delta(aid)
            for key in ('meshes', 'triangles', 'materials'):
                self.assertEqual(record['after']['facts'][key] - record['before']['facts'][key], delta[key], (aid, key))
            before, after = record['before']['facts']['animations'], record['after']['facts']['animations']
            self.assertEqual(len(after) - len(before), delta['animations'], aid)
            self.assertTrue(all(clip in after for clip in before), aid)


if __name__ == '__main__':
    unittest.main()
