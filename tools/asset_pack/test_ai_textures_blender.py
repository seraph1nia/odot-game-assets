"""Isolated cache, transition and saved-source material preservation fixtures."""
from contextlib import contextmanager
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import numpy as np

from tools.asset_pack import ai_texture_blender as textures
from tools.asset_pack import verify_ai_textures_blender as verification
from tools.asset_pack.ai_texture_blender import managed_image, ground_color
from tools.asset_pack.verify_ambient_blender import capture
import geometry


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
        # A flat painted input must not acquire the old dark perimeter trench.
        floor = ground_color('moss', original, supplied)
        luma = np.array((.2126, .7152, .0722))
        np.testing.assert_allclose(floor @ luma, np.full((128, 128), floor[64, 64] @ luma), atol=1e-6)

    def test_preparation_excludes_atlas_frame_and_reduces_whole_tile_feature_scale(self):
        size = 128
        y, x = np.mgrid[0:size, 0:size] / (size - 1)
        supplied = np.full((size, size, 3), .1, dtype=np.float32)
        supplied[(x - .5)**2 + (y - .5)**2 < .16**2] = .8
        detail = textures.ground_detail(supplied)
        np.testing.assert_array_equal(detail, textures.ground_detail(supplied))
        damaged = supplied.copy()
        damaged[:10] = damaged[-10:] = 0
        damaged[:, :10] = damaged[:, -10:] = 0
        np.testing.assert_array_equal(detail, textures.ground_detail(damaged))
        # Along a row the former single broad mark becomes multiple smaller
        # painted marks. Test the emitted pixel field, not implementation text.
        row = detail[size // 2, :, 0] > .35
        runs = np.diff(np.r_[False, row, False].astype(int))
        starts, ends = np.flatnonzero(runs == 1), np.flatnonzero(runs == -1)
        self.assertGreater(len(starts), 1)
        self.assertLess(max(ends - starts), size * .20)
        self.assertGreater(float(detail.std()), .05)


class ApplyPreservation(unittest.TestCase):
    def write_input(self, directory, family, value):
        directory.mkdir(parents=True, exist_ok=True)
        image = textures.painted_finish.image_map(
            family + '_basecolor', np.full((32, 32, 3), value, dtype=np.float32), directory)
        bpy.data.images.remove(image)

    @contextmanager
    def source(self, asset_id, material_name, *, linked=True):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            cache = root / '.cache/ai-textures'
            with patch.multiple(textures, ROOT=root, CACHE=cache), patch.multiple(verification, ROOT=root, CACHE=cache):
                bpy.ops.wm.read_factory_settings(use_empty=True)
                collection = bpy.data.collections.new(asset_id.split('/')[-1])
                bpy.context.scene.collection.children.link(collection)
                mesh = bpy.data.meshes.new('authored_mesh')
                mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, 0)], [], [(0, 1, 2)])
                obj = bpy.data.objects.new('authored_object', mesh)
                collection.objects.link(obj)
                mat = geometry.material(material_name, (.2, .3, .4))
                mesh.materials.append(mat)
                original = textures.painted_finish.image_map(
                    'authored_color', np.full((32, 32, 3), .2, dtype=np.float32), root)
                original.use_fake_user = True
                if linked:
                    node = mat.node_tree.nodes.new('ShaderNodeTexImage')
                    node.image = original
                    shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
                    mat.node_tree.links.new(node.outputs['Color'], shader.inputs['Base Color'])
                building = asset_id == 'buildings/archery_range'
                folder = 'buildings/textures/ai_archery' if building else 'environment/textures/ai_ground'
                family = textures.ARCHERY[material_name][0] if building else material_name.removeprefix('floor_')
                inputs = root / 'sources' / folder / 'input/textures'
                self.write_input(inputs, family, .5)
                (inputs.parent.parent / 'managed').mkdir()
                path = root / 'sources' / (asset_id + '.blend')
                path.parent.mkdir(parents=True, exist_ok=True)
                bpy.ops.wm.save_as_mainfile(filepath=str(path))
                bpy.ops.wm.open_mainfile(filepath=str(path))
                bpy.context.view_layer.update()
                audit = cache / 'audit' / (asset_id.replace('/', '_') + '.json')
                audit.parent.mkdir(parents=True)
                audit.write_text(json.dumps({'id': asset_id, 'source_sha256': textures.sha(path),
                                             'signature': textures.signature()}))
                baseline = cache / 'before/sources' / (asset_id + '.blend')
                baseline.parent.mkdir(parents=True)
                baseline.write_bytes(path.read_bytes())
                try:
                    yield root, path, inputs, family
                finally:
                    bpy.ops.wm.read_factory_settings(use_empty=True)

    def verify(self, asset_id):
        receipt = textures.CACHE / 'applied' / (asset_id.replace('/', '_') + '.json')
        result = verification.source_preservation(asset_id, json.loads(receipt.read_text()))
        bpy.ops.wm.open_mainfile(filepath=str(textures.ROOT / 'sources' / (asset_id + '.blend')))
        return result

    def test_baseline_reapply_committed_receipt_and_texture_update(self):
        cases = [('environment/hex_ground_moss', 'floor_' + family, True)
                 for family in ('moss', 'grass', 'dirt', 'leaf_litter', 'pine_duff', 'foundation', 'path', 'river')]
        cases += [('buildings/archery_range', 'wood', True),
                  ('buildings/archery_range', 'blue', False)]
        for aid, material, linked in cases:
            with self.subTest(material=material), self.source(aid, material, linked=linked) as (root, path, inputs, family):
                textures.apply(aid)
                first = capture()
                first_report = self.verify(aid)
                self.assertEqual(first_report['retained_owned_image_proofs'], {})
                receipt = textures.CACHE / 'applied' / (aid.replace('/', '_') + '.json')
                self.assertEqual(json.loads(receipt.read_text())['source_sha256'], textures.sha(path))
                textures.apply(aid)
                self.assertEqual(capture(), first)
                validation = root / 'docs/ai-textures/validation.json'
                validation.parent.mkdir(parents=True)
                validation.write_text(json.dumps({'assets': {aid: {'source_after_sha256': textures.sha(path)}}}))
                receipt.unlink()
                textures.apply(aid)
                self.assertEqual(capture(), first)
                self.write_input(inputs, family, .8)
                textures.apply(aid)
                updated = capture()
                self.assertEqual(updated['structure'], first['structure'])
                self.assertEqual(updated['images']['authored_color'], first['images']['authored_color'])
                self.assertNotEqual(updated['materials'][material], first['materials'][material])
                textures.apply(aid)
                self.assertEqual(capture(), updated)
                report = self.verify(aid)
                self.assertEqual(report['new_image_count'], first_report['new_image_count'] + 1)
                predecessors = set(first['images']) - {'authored_color'}
                self.assertEqual(set(report['retained_owned_image_proofs']), predecessors)
                for name in predecessors:
                    self.assertEqual(report['retained_owned_image_proofs'][name], first['images'][name])
                self.assertEqual(capture(), updated)

    def test_verification_rejects_forged_predecessors_and_baseline_damage(self):
        for aid, material in (('environment/hex_ground_moss', 'floor_moss'),
                              ('buildings/archery_range', 'wood')):
            for damage in ('unowned', 'forged', 'wrong_path', 'predecessor_pixels', 'predecessor_channel',
                           'baseline_pixels', 'missing_baseline', 'active_pixels', 'unexplained_orphan', 'retained_has_users'):
                with self.subTest(material=material, damage=damage), self.source(aid, material) as (root, path, inputs, family):
                    textures.apply(aid)
                    receipt = textures.CACHE / 'applied' / (aid.replace('/', '_') + '.json')
                    predecessor = json.loads(receipt.read_text())['materials'][0]['image']
                    self.write_input(inputs, family, .8)
                    textures.apply(aid)
                    self.verify(aid)
                    applied = json.loads(receipt.read_text())
                    image = bpy.data.images[predecessor]
                    if damage == 'unowned':
                        del image['ai_texture_owner']
                    elif damage == 'forged':
                        image.copy().use_fake_user = True
                    elif damage == 'wrong_path':
                        image.filepath = str(root / 'authored_color.png')
                    elif damage in ('predecessor_pixels', 'baseline_pixels', 'active_pixels'):
                        if damage == 'baseline_pixels':
                            image = bpy.data.images['authored_color']
                        elif damage == 'active_pixels':
                            image = bpy.data.images[applied['materials'][0]['image']]
                        image.pixels[0] = .9
                        image.pack()
                    elif damage == 'predecessor_channel':
                        image.colorspace_settings.name = 'Non-Color'
                    elif damage == 'missing_baseline':
                        bpy.data.images.remove(bpy.data.images['authored_color'])
                    elif damage == 'unexplained_orphan':
                        orphan = textures.painted_finish.image_map(
                            'manual_orphan', np.full((32, 32, 3), .4, dtype=np.float32), root)
                        orphan.use_fake_user = True
                    else:
                        node = bpy.data.materials[material].node_tree.nodes.new('ShaderNodeTexImage')
                        node.image = image
                    bpy.ops.wm.save_as_mainfile(filepath=str(path))
                    saved = path.read_bytes()
                    with self.assertRaisesRegex(AssertionError, 'Source changed since application'):
                        verification.source_preservation(aid, applied)
                    applied['source_sha256'] = textures.sha(path)
                    with self.assertRaises(AssertionError):
                        verification.source_preservation(aid, applied)
                    self.assertEqual(path.read_bytes(), saved)

    def test_manual_bindings_metadata_and_packed_edits_are_rejected_before_writes(self):
        cases = [('environment/hex_ground_moss', 'floor_moss', True),
                 ('buildings/archery_range', 'wood', True),
                 ('buildings/archery_range', 'blue', False)]
        for aid, material, linked in cases:
            for edit in ('binding', 'original_metadata', 'original_pixels', 'managed_pixels'):
                with self.subTest(material=material, edit=edit), self.source(aid, material, linked=linked) as (root, path, _, _):
                    textures.apply(aid)
                    applied = capture()
                    edited_image = None
                    mat = bpy.data.materials[material]
                    shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
                    node = shader.inputs['Base Color'].links[0].from_node
                    if edit == 'binding':
                        manual = textures.painted_finish.image_map(
                            'manual_color', np.full((32, 32, 3), .7, dtype=np.float32), root)
                        node.image = manual
                    elif edit == 'original_metadata':
                        mat['ai_original_color_image'] = 'manual_original'
                    else:
                        image = bpy.data.images['authored_color'] if edit == 'original_pixels' else node.image
                        image.pixels[0] = .9
                        image.pack()
                        edited_image = image.name
                    bpy.ops.wm.save_as_mainfile(filepath=str(path))
                    bpy.ops.wm.open_mainfile(filepath=str(path))
                    authored = capture()
                    if edited_image:
                        self.assertNotEqual(authored['images'][edited_image], applied['images'][edited_image])
                    else:
                        self.assertNotEqual(authored['materials'][material], applied['materials'][material])
                    saved = path.read_bytes()
                    companions = {p: p.read_bytes() for p in root.rglob('*.png')}
                    receipt = textures.CACHE / 'applied' / (aid.replace('/', '_') + '.json')
                    last_applied = receipt.read_bytes()
                    for committed in (False, True):
                        if committed:
                            validation = root / 'docs/ai-textures/validation.json'
                            validation.parent.mkdir(parents=True)
                            validation.write_text(json.dumps({'assets': {aid: {
                                'source_after_sha256': json.loads(last_applied)['source_sha256']}}}))
                            receipt.unlink()
                        with self.assertRaisesRegex(AssertionError, 'refusing to overwrite manual edits'):
                            textures.apply(aid)
                        self.assertEqual(path.read_bytes(), saved)
                        self.assertEqual(capture(), authored)
                        self.assertEqual({p: p.read_bytes() for p in root.rglob('*.png')}, companions)
                        if not committed:
                            self.assertEqual(receipt.read_bytes(), last_applied)
                        else:
                            self.assertFalse(receipt.exists())


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
        raise SystemExit(1)
