"""Focused color-only authoring and orphan-preserving serialization fixtures."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import numpy as np
import vivid_refinement as vivid
import art_style as style
from tools.asset_pack.test_encoded_images import png


class VividFixtures(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)

    def test_orphan_prototypes_and_unused_material_maps_survive_save(self):
        mesh = bpy.data.meshes.new('shared leaf mesh')
        mesh.from_pydata([(0, 0, 0), (1, 0, 0), (0, 1, .1)], [], [(0, 1, 2)])
        prototype = bpy.data.objects.new('unlinked authored prototype', mesh)
        obj = bpy.data.objects.new('root-owned live instance', mesh)
        bpy.context.scene.collection.objects.link(obj)
        mat = bpy.data.materials.new('unused authored variant')
        mat.use_nodes = True
        image = bpy.data.images.new('original roughness', width=4, height=4)
        image.colorspace_settings.name = style.TEXTURES.data_space
        image.pixels.foreach_set(np.tile((.6, .6, .6, 1), 16).astype(np.float32))
        image.pack()
        node = mat.node_tree.nodes.new('ShaderNodeTexImage')
        node.image = image
        prototype_name, instance_name = prototype.name, obj.name
        before, channels = vivid.structure(), vivid.data_channels()
        protected = vivid.preserve_orphans()
        self.assertIn('objects/' + prototype.name, protected)
        self.assertIn('materials/' + mat.name, protected)
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'protected.blend'
            bpy.ops.wm.save_as_mainfile(filepath=str(path))
            bpy.ops.wm.open_mainfile(filepath=str(path))
            self.assertEqual(vivid.structure(), before)
            self.assertEqual(vivid.data_channels(), channels)
            self.assertIs(bpy.data.objects[prototype_name].data, bpy.data.objects[instance_name].data)

    def test_material_recovery_preserves_alpha_data_maps_and_low_emission(self):
        mat = bpy.data.materials.new('forest_leaf_woodland')
        mat.use_nodes = True
        shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        shader.inputs['Base Color'].default_value = (.08, .12, .08, 1)
        shader.inputs['Emission Strength'].default_value = .16
        color = bpy.data.images.new('current painted leaf', width=8, height=8, alpha=True)
        values = np.tile((.28, .35, .29, .4), (8, 8, 1)).astype(np.float32)
        color.pixels.foreach_set(values.ravel())
        node = mat.node_tree.nodes.new('ShaderNodeTexImage')
        node.image = color
        mat.node_tree.links.new(node.outputs['Color'], shader.inputs['Base Color'])
        with tempfile.TemporaryDirectory() as directory:
            row = vivid.apply_material(mat, {}, {}, Path(directory))
            result = vivid.pixels(node.image)
            self.assertTrue(np.allclose(result[:, :, 3], values[:, :, 3], atol=1 / 255))
            self.assertTrue(row['channels'][0]['map']['alpha_preserved'])
            self.assertTrue(node.image.packed_file)
            self.assertAlmostEqual(shader.inputs['Emission Strength'].default_value, .16)
            self.assertGreater(float(result[:, :, 1].mean() - result[:, :, 0].mean()), .1)

    def test_encoded_maps_reject_real_content_color_space_binding_mapping_and_use_changes(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / 'guard.png'
            rows = [bytes((31, 82, 170, 255) * 3), bytes((19, 99, 201, 125) * 3)]
            path.write_bytes(png(rows, mode=4))
            image = bpy.data.images.load(str(path), check_existing=False)
            image.colorspace_settings.name = style.TEXTURES.data_space; image.pack()
            mat = bpy.data.materials.new('guard material'); mat.use_nodes = True
            node = mat.node_tree.nodes.new('ShaderNodeTexImage'); node.image = image
            mapping = mat.node_tree.nodes.new('ShaderNodeMapping')
            mat.node_tree.links.new(mapping.outputs['Vector'], node.inputs['Vector'])
            shader = mat.node_tree.nodes.get('Principled BSDF')
            mat.node_tree.links.new(node.outputs['Color'], shader.inputs['Roughness'])
            key = mat.name + '/' + node.name
            baseline = vivid.data_channels()
            for _ in range(10):
                self.assertEqual(vivid.data_channels(), baseline)
            image.colorspace_settings.name = 'sRGB'
            self.assertNotEqual(vivid.data_channels(), baseline)
            image.colorspace_settings.name = style.TEXTURES.data_space
            alternate = bpy.data.images.load(str(path), check_existing=False)
            alternate.colorspace_settings.name = style.TEXTURES.data_space; alternate.pack()
            node.image = alternate
            changed = vivid.data_channels()
            self.assertEqual(changed[key]['encoded'], baseline[key]['encoded'])
            self.assertNotEqual(changed[key]['binding'], baseline[key]['binding'])
            node.image = image
            mapping.inputs['Scale'].default_value = (2, 1, 1)
            self.assertNotEqual(vivid.data_channels(), baseline)
            mapping.inputs['Scale'].default_value = (1, 1, 1)
            node.mute = True
            self.assertNotEqual(vivid.data_channels(), baseline)
            node.mute = False
            mat.node_tree.links.new(node.outputs['Color'], shader.inputs['Metallic'])
            self.assertNotEqual(vivid.data_channels(), baseline)
            mat.node_tree.links.remove(next(link for link in mat.node_tree.links if link.to_socket == shader.inputs['Metallic']))
            self.assertEqual(vivid.data_channels(), baseline)
            # Modify the actual persisted PNG with the same path/image/node identity.
            changed_rows = [bytearray(r) for r in rows]; changed_rows[0][0] += 1
            path.write_bytes(png(changed_rows, mode=4))
            image.unpack(method='REMOVE'); image.reload(); image.pack()
            observed = vivid.data_channels()
            self.assertEqual(observed[key]['binding'], baseline[key]['binding'])
            self.assertNotEqual(observed[key]['encoded']['packed_sha256'], baseline[key]['encoded']['packed_sha256'])
            self.assertNotEqual(observed[key]['encoded']['samples_sha256'], baseline[key]['encoded']['samples_sha256'])

    def test_fine_color_detail_is_bounded_and_does_not_change_alpha(self):
        values = np.full((32, 32, 3), .5, dtype=np.float32)
        result = vivid.detail(values, 'leaf')
        self.assertGreater(float(np.ptp(result)), 0)
        self.assertLess(float(np.max(np.abs(result - values))), .025)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(VividFixtures)
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
        raise SystemExit(1)
