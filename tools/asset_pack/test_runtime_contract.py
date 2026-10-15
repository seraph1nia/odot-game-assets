"""Current generated runtime scene/evidence contracts, not implementation text."""
import json
import unittest
from pathlib import Path

from tools.asset_pack.ambient_contract import ASSETS, sha
from tools.asset_pack.runtime_contract import export_chain
from tools.asset_pack.runtime_review import metrics, FOCAL

ROOT=Path(__file__).resolve().parents[2]
DOCS=ROOT/'docs/runtime-optimization'


class RuntimeContracts(unittest.TestCase):
    def test_all25_actual_exports_bind_strict_current_fidelity_and_localized_loops(self):
        baseline=json.loads((DOCS/'baseline.json').read_text())
        report=json.loads((DOCS/'validation.json').read_text())
        self.assertEqual(set(report['assets']),set(ASSETS))
        for aid in ASSETS:
            with self.subTest(asset=aid):
                original=baseline['assets'][aid];record=report['assets'][aid]
                export_chain(ROOT,aid,original['facts']['version'])
                self.assertEqual(record['glb_sha256'],sha(ROOT/'exports'/(aid+'.glb')))
                self.assertEqual(record['source_sha256'],sha(ROOT/original['job']['source']))
                for key in ('source_to_raw_buffers','source_to_exported_buffers','reimport'):
                    check=record[key]
                    self.assertEqual(check['normals_asserted'],key != 'reimport')
                    self.assertTrue(check['one_to_one_source_triangle_connectivity_winding_equal'])
                    self.assertEqual(check['source_triangle_count'],record['serialized_surfaces']['serialized_triangle_count'])
                    self.assertTrue(check['all_triangle_corners_checked_bidirectionally'])
                    self.assertTrue(check['per_material_triangle_multiplicity_equal'])
                    self.assertLess(check['max_position_error_m'],.00002)
                    self.assertLess(check['max_uv_error'],.00002)
                    if check['normals_asserted']:
                        self.assertLess(check['max_normal_component_error'],.00002)
                self.assertTrue(record['serialized_surfaces']['one_to_one_transformed_triangle_attributes_equal'])
                self.assertTrue(record['serialized_surfaces']['zero_area_triangles_not_filtered'])
                self.assertTrue(record['playback']['fixed_objects_world_matrices_equal_throughout'])
                self.assertTrue(record['playback']['source_and_export_endpoints_equal'])
                self.assertLess(record['playback']['evaluated_pose_point_cloud_max_error_m'],.0001)
                after=metrics(ROOT/'exports'/(aid+'.glb'))
                before_nodes=original['resources']['active_mesh_nodes']
                if aid.startswith('buildings/'):
                    self.assertLess(after['mesh_nodes'],before_nodes*.15)
                self.assertLessEqual(after['triangle_instances'],original['resources']['active_triangle_instances'])

    def test_all50_real_godot_import_measurements_and_clips_bind_exact_glbs(self):
        report=json.loads((DOCS/'godot.json').read_text())
        samples={s['path']:s for s in report['samples']}
        self.assertEqual(len(samples),50)
        baseline=json.loads((DOCS/'baseline.json').read_text())
        for aid in ASSETS:
            for stage in ('before','after'):
                path='res://'+stage+'/'+aid+'.glb';sample=samples[path]
                expected=baseline['assets'][aid]['facts']['version'] if stage=='before' else sha(ROOT/'exports'/(aid+'.glb'))
                self.assertEqual(report['source_glb_sha256'][path],expected)
                self.assertEqual(len(sample['instantiate_us']),11)
                self.assertEqual(sample['median_instantiate_us'],sorted(sample['instantiate_us'])[5])
                self.assertTrue(sample['loop_endpoints_equal'])
                self.assertTrue(sample['all_track_targets_resolve'])
                self.assertGreater(sample['moving_meshes'],0)

    def test_eight_matched_actual_render_pairs_bind_current_bytes_and_derivatives(self):
        for aid in FOCAL:
            record=json.loads((DOCS/'evidence'/aid/'render.json').read_text())
            self.assertEqual(record['after_glb_sha256'],sha(ROOT/'exports'/(aid+'.glb')))
            self.assertEqual(record['renderer_sha256'],sha(ROOT/'tools/asset_pack/render_runtime_blender.py'))
            self.assertEqual(record['neutral_setup_sha256'],sha(ROOT/'tools/asset_catalog/render_blender.py'))
            self.assertEqual(len(record['images']),6)
            for image,digest in record['images'].items():self.assertEqual(sha(ROOT/image),digest)


if __name__=='__main__':unittest.main()
