"""Small Blender fixtures for the narrow ambient edit/preservation boundary."""
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import geometry as g
import art_style as style
from tools.asset_pack.ambient_motion import building, shimmer
from tools.asset_pack.verify_ambient_blender import capture, compare
from tools.asset_pack.encoded_images import UnsupportedImage
from tools.asset_pack.ambient_contract import sha


class AmbientFixtures(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.directory = tempfile.TemporaryDirectory()
        self.addCleanup(self.directory.cleanup)
        self.col = bpy.data.collections.new('weaver')
        bpy.context.scene.collection.children.link(self.col)
        self.root = bpy.data.objects.new('weaver_root', None)
        self.col.objects.link(self.root)
        mat = g.material('fixture_wood', (.4, .2, .1))
        mesh = bpy.data.meshes.new('Shared authored fixture mesh')
        mesh.from_pydata([(0, 0, 0), (.1, 0, 0), (0, .1, 0)], [], [(0, 1, 2)])
        mesh.materials.append(mat)
        self.shuttle = bpy.data.objects.new('Loom shuttle', mesh)
        self.beam = bpy.data.objects.new('Fixed structural beam', mesh)
        for obj in (self.shuttle, self.beam):
            self.col.objects.link(obj); obj.parent = self.root
        bpy.context.view_layer.update()
        # Exact four-field job contract emitted by plan_exports(). Explicit nulls
        # matter: collection and object selection are mutually exclusive modes.
        self.job = {'id': 'buildings/weaver', 'source': 'sources/buildings/weaver.blend',
                    'collection': self.col.name, 'object': None}

    def author(self, job=None):
        before = capture()
        action = bpy.data.actions.new(style.AMBIENT.clip); action['loop'] = True
        feature = building(job or self.job, action)
        return before, {'features': [feature]}

    def test_explicit_object_selection_uses_the_same_preserved_ownership_contract(self):
        before, record = self.author(dict(self.job, collection=None, object=self.root.name))
        result = compare(before, record)
        self.assertTrue(result['original_collection_ownership_equal'])
        self.assertEqual(record['features'][0]['targets'], [self.shuttle.name])
        self.assertIs(self.shuttle.parent.parent, self.root)
        self.assertIs(self.beam.parent, self.root)

    def test_one_local_spot_moves_and_rests_without_unsharing_meshes(self):
        before, record = self.author()
        result = compare(before, record)
        self.assertTrue(result['all_original_full_materials_and_images_equal'])
        self.assertIs(self.shuttle.data, self.beam.data)
        rest = self.shuttle.matrix_world.copy()
        bpy.context.scene.frame_set(25); bpy.context.view_layer.update()
        self.assertAlmostEqual(self.shuttle.matrix_world.translation.x, style.AMBIENT.shuttle_travel, places=6)
        self.assertEqual(tuple(self.beam.matrix_world.translation), (0, 0, 0))
        bpy.context.scene.frame_set(97); bpy.context.view_layer.update()
        self.assertEqual(self.shuttle.matrix_world, rest)

    def test_motion_allowance_does_not_hide_geometry_color_or_parent_regressions(self):
        before, record = self.author()
        self.shuttle.data.vertices[0].co.z = .1
        with self.assertRaisesRegex(AssertionError, 'structure'):
            compare(before, record)
        self.shuttle.data.vertices[0].co.z = 0
        shader = self.shuttle.data.materials[0].node_tree.nodes.get('Principled BSDF')
        original = tuple(shader.inputs['Base Color'].default_value)
        shader.inputs['Base Color'].default_value = (1, 0, 0, 1)
        with self.assertRaisesRegex(AssertionError, 'materials'):
            compare(before, record)
        shader.inputs['Base Color'].default_value = original
        self.beam.parent = self.shuttle.parent
        with self.assertRaisesRegex(AssertionError, 'parent'):
            compare(before, record)

    def test_unbound_compositor_buffer_is_inventoried_but_cannot_hide_a_texture(self):
        path = Path(__file__).resolve().parents[2] / 'sources/buildings/arrow_tower.blend'
        original = sha(path)
        bpy.ops.wm.open_mainfile(filepath=str(path))
        viewer = bpy.data.images['Viewer Node']
        self.assertEqual(viewer.source, 'VIEWER')
        self.assertEqual(viewer.type, 'COMPOSITING')
        state = capture()['images'][viewer.name]
        self.assertTrue(state['unbound_nonpersistent_compositor_buffer'])
        self.assertEqual(state['image_user_count'], 0)
        mat = bpy.data.materials.new('negative Viewer texture binding'); mat.use_nodes = True
        node = mat.node_tree.nodes.new('ShaderNodeTexImage'); node.image = viewer
        with self.assertRaisesRegex(UnsupportedImage, 'has image users'):
            capture()
        node.image = bpy.data.images['Render Result']
        with self.assertRaisesRegex(UnsupportedImage, 'has image users'):
            capture()
        self.assertEqual(sha(path), original)

    def test_overlay_adds_only_one_tiny_uv_strip_and_keeps_ribbon_fixed(self):
        self.root.name = 'hex_river_overlay_straight_root'
        self.col.name = 'hex_river_overlay_straight'
        before = capture()
        action = bpy.data.actions.new(style.AMBIENT.clip); action['loop'] = True
        job = {'id': 'environment/hex_river_overlay_straight',
               'source': 'sources/environment/hex_river_overlay_straight.blend',
               'collection': self.col.name, 'object': None}
        feature = shimmer(job, action, directory=self.directory.name)
        result = compare(before, {'features': [feature]})
        self.assertEqual(len(result['new_meshes']), 1)
        mesh = bpy.data.meshes[feature['added_geometry']['mesh']]
        self.assertEqual(len(mesh.vertices), 10)
        self.assertEqual(sum(len(p.vertices) - 2 for p in mesh.polygons), 8)
        self.assertTrue(mesh.uv_layers)
        fixed = self.beam.matrix_world.copy()
        for frame in style.AMBIENT.frames:
            bpy.context.scene.frame_set(frame); bpy.context.view_layer.update()
            self.assertEqual(self.beam.matrix_world, fixed)


if __name__ == '__main__':
    unittest.main(argv=[sys.argv[0]])
