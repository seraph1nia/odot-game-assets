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

    def test_fine_color_detail_is_bounded_and_does_not_change_alpha(self):
        values = np.full((32, 32, 3), .5, dtype=np.float32)
        result = vivid.detail(values, 'leaf')
        self.assertGreater(float(np.ptp(result)), 0)
        self.assertLess(float(np.max(np.abs(result - values))), .025)


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(VividFixtures)
    if not unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful():
        raise SystemExit(1)
