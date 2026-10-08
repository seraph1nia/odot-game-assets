"""Real selected-export material fixtures; temporary sources only, never rebuild assets."""
import hashlib
import json
import struct
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / 'tools/asset_pack'))
import bpy
import geometry as g
from tools.asset_catalog import export_blender as exporter


def document(path):
    data = path.read_bytes()
    length = struct.unpack_from('<I', data, 12)[0]
    return json.loads(data[20:20 + length])


def bindings():
    return {o.name: {'data': o.data.name,
                     'slots': [(s.link, s.material.name if s.material else None) for s in o.material_slots],
                     'vertices': [list(v.co) for v in o.data.vertices],
                     'faces': [(list(p.vertices), p.material_index, p.use_smooth) for p in o.data.polygons],
                     'uv': [[list(v.uv) for v in layer.data] for layer in o.data.uv_layers],
                     'parent': o.parent.name if o.parent else None,
                     'matrix': [list(row) for row in o.matrix_basis],
                     'modifiers': [(m.name, m.type, m.show_viewport) for m in o.modifiers]}
            for o in bpy.data.objects if o.type == 'MESH'}


class SelectedMaterialTests(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        g.M.clear()
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'sources/props').mkdir(parents=True)
        (self.root / 'exports').mkdir()
        (self.root / 'exports/asset_manifest.json').write_text('{"assets": []}')
        self.col = g.collection('fixture')
        g.target(self.col)
        self.red = g.material('fixture_red', (.8, .04, .04))
        self.blue = g.material('fixture_blue', (.04, .04, .8))
        self.green = g.material('fixture_green', (.04, .8, .04))
        self.base = g.cube('Default red', (0, 0, 0), (1, 1, 1), self.red, bevel=.008)
        self.base.data.uv_layers.new(name='Authored UV')
        for i, corner in enumerate(self.base.data.uv_layers.active.data):
            corner.uv = (i / 24, i % 4 / 4)
        self.source = self.root / 'sources/props/fixture.blend'
        self.target = self.root / 'exports/props/fixture.glb'

    def override(self, name, materials, modified=True):
        obj = self.base.copy()
        obj.name = name
        self.col.objects.link(obj)
        if not modified:
            obj.modifiers.clear()
        for i, material in enumerate(materials):
            obj.material_slots[i].link = 'OBJECT'
            obj.material_slots[i].material = material
        return obj

    def export(self, during=None, fail=False, **options):
        bpy.ops.wm.save_as_mainfile(filepath=str(self.source))
        digest = hashlib.sha256(self.source.read_bytes()).hexdigest()
        before = bindings()
        mesh_count = len(bpy.data.meshes)
        real = bpy.ops.export_scene.gltf

        calls = []

        def invoke(**kwargs):
            calls.append(kwargs)
            kwargs.update(options)
            if during:
                during()
            if fail:
                raise RuntimeError('fixture injected serializer failure')
            return real(**kwargs)

        with patch.object(sys, 'argv', ['blender', '--', '--root', str(self.root), 'props/fixture']), \
                patch.object(bpy.ops, 'export_scene', SimpleNamespace(gltf=invoke)):
            if fail:
                with self.assertRaisesRegex(RuntimeError, 'injected serializer failure'):
                    exporter.main()
            else:
                exporter.main()
        self.assertEqual(len(calls), 1, 'Actual selected exporter must invoke the fixture serializer')
        self.assertEqual(hashlib.sha256(self.source.read_bytes()).hexdigest(), digest)
        self.assertEqual(bindings(), before, 'Source scene bindings changed in memory')
        self.assertEqual(len(bpy.data.meshes), mesh_count, 'Transient mesh leaked')
        self.assertEqual(list((self.root / '.cache').glob('tmp*')), [])
        return document(self.target) if not fail else None

    def assert_materials(self, doc, name, expected):
        node = next(n for n in doc['nodes'] if n.get('name') == name)
        primitives = doc['meshes'][node['mesh']]['primitives']
        actual = {doc['materials'][p['material']]['name'] if 'material' in p else None for p in primitives}
        self.assertEqual(actual, set(expected), (name, actual, expected))
        for p in primitives:
            if 'material' not in p:
                continue
            mat = doc['materials'][p['material']]
            source = bpy.data.materials[mat['name']]
            shader = next(n for n in source.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
            for actual, value in zip(mat['pbrMetallicRoughness']['baseColorFactor'], shader.inputs['Base Color'].default_value, strict=True):
                self.assertAlmostEqual(actual, value, places=6)

    def test_shared_red_data_blue_object_override(self):
        self.override('Blue override', [self.blue])
        doc = self.export()
        self.assert_materials(doc, 'Blue override', ['fixture_blue'])
        self.assert_materials(doc, 'Default red', ['fixture_red'])

    def test_multiple_slots_default_object_and_null_precedence(self):
        self.base.data.materials.append(self.green)
        self.base.data.materials.append(None)
        self.base.data.materials.append(self.red)
        for i, poly in enumerate(self.base.data.polygons):
            poly.material_index = i % 4
        obj = self.override('Mixed slots', [self.blue, self.green, None, None])
        obj.material_slots[1].link = 'DATA'
        doc = self.export()
        self.assert_materials(doc, 'Mixed slots', ['fixture_blue', 'fixture_green', None])
        self.assert_materials(doc, 'Default red', ['fixture_red', 'fixture_green', None])

    def test_equal_tuples_reuse_and_differing_tuples_do_not(self):
        self.override('Blue one', [self.blue])
        self.override('Blue two', [self.blue])
        self.override('Green', [self.green])

        def during():
            self.assertIs(bpy.data.objects['Blue one'].data, bpy.data.objects['Blue two'].data)
            self.assertIsNot(bpy.data.objects['Blue one'].data, bpy.data.objects['Green'].data)
            self.assertIsNot(bpy.data.objects['Blue one'].data, bpy.data.objects['Default red'].data)
        doc = self.export(during)
        for name, mat in [('Blue one', 'fixture_blue'), ('Blue two', 'fixture_blue'), ('Green', 'fixture_green')]:
            self.assert_materials(doc, name, [mat])

    def test_no_modifier_override_needs_no_normalization(self):
        self.override('Direct blue', [self.blue], modified=False)
        doc = self.export(lambda: self.assertIs(bpy.data.objects['Direct blue'].data, bpy.data.objects['Default red'].data))
        self.assert_materials(doc, 'Direct blue', ['fixture_blue'])

    def test_range_style_red_over_blue_data(self):
        self.base.data.materials[0] = self.blue
        self.override('Red collar', [self.red])
        doc = self.export()
        self.assert_materials(doc, 'Red collar', ['fixture_red'])
        self.assert_materials(doc, 'Default red', ['fixture_blue'])

    def test_collection_instance_prototype_override(self):
        prototype = self.override('Instanced blue', [self.blue])
        self.col.objects.unlink(prototype)
        library = bpy.data.collections.new('Library')
        library.objects.link(prototype)
        instance = bpy.data.objects.new('Collection instance', None)
        instance.instance_type = 'COLLECTION'
        instance.instance_collection = library
        self.col.objects.link(instance)
        doc = self.export()
        self.assert_materials(doc, 'Instanced blue', ['fixture_blue'])

    def test_serializer_failure_restores_source_and_target(self):
        self.override('Blue override', [self.blue])
        self.target.parent.mkdir()
        self.target.write_bytes(b'previous output')
        self.export(fail=True)
        self.assertEqual(self.target.read_bytes(), b'previous output')


if __name__ == '__main__':
    suite = unittest.defaultTestLoader.loadTestsFromTestCase(SelectedMaterialTests)
    # A focused reproduction can run before any production change.
    if '--' in sys.argv and sys.argv[sys.argv.index('--') + 1:]:
        suite = unittest.defaultTestLoader.loadTestsFromNames(sys.argv[sys.argv.index('--') + 1:], SelectedMaterialTests)
    result = unittest.TextTestRunner(verbosity=2).run(suite)
    if not result.wasSuccessful():
        raise RuntimeError('Selected-export material regression failed')
