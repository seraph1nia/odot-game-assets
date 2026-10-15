"""Execute the portable optimizer against generated binary scene contracts."""
from copy import deepcopy
import tempfile
import unittest
from pathlib import Path

from tools.asset_catalog.runtime_glb import (Buffer, IDENTITY, accessor, consolidate,
    matrix, multiply, optimize, read, transform, write)


def fixture():
    doc = {'asset': {'version': '2.0'}, 'buffers': [{'byteLength': 0}], 'bufferViews': [], 'accessors': [],
           'scenes': [{'nodes': [0]}], 'scene': 0,
           'materials': [{'name': 'paint', 'pbrMetallicRoughness': {'baseColorFactor': [1, .2, .1, 1]}},
                         {'name': 'paint.001', 'pbrMetallicRoughness': {'baseColorFactor': [1, .2, .1, 1]}}],
           'nodes': [{'name': 'fixture_root', 'children': [1, 2, 3]},
                     {'name': 'first', 'mesh': 0, 'translation': [2, 0, 0]},
                     {'name': 'mirrored', 'mesh': 1, 'scale': [-1, 2, 1]},
                     {'name': 'moving', 'translation': [0, 0, 1], 'children': [4]},
                     {'name': 'attached', 'mesh': 0, 'translation': [0, 3, 0]}]}
    b = Buffer(doc, b'')
    attrs = {k: b.add(v, {'componentType': 5126, 'type': t}, positions=k == 'POSITION') for k, v, t in
             [('POSITION', [(0, 0, 0), (1, 0, 0), (0, 1, 0)], 'VEC3'),
              ('NORMAL', [(0, 0, 1)]*3, 'VEC3'),
              ('TANGENT', [(1, 0, 0, 1)]*3, 'VEC4'),
              ('TEXCOORD_0', [(0, 0), (1, 0), (0, 1)], 'VEC2')]}
    indices = b.add([(0,), (1,), (2,)], {'componentType': 5123, 'type': 'SCALAR'})
    doc['meshes'] = [{'primitives': [{'attributes': attrs, 'indices': indices, 'material': i}]} for i in range(2)]
    doc['animations'] = [{'name': 'ambient', 'extras': {'loop': True},
        'samplers': [{'input': b.add([(0,), (1,), (2,)], {'componentType': 5126, 'type': 'SCALAR'}),
                      'output': b.add([(0, 0, 1), (0, 0, 2), (0, 0, 1)], {'componentType': 5126, 'type': 'VEC3'})}],
        'channels': [{'sampler': 0, 'target': {'node': 3, 'path': 'translation'}}]}]
    return doc, b.binary


class RuntimeGLBTests(unittest.TestCase):
    def test_material_batches_retain_moving_owner_and_bake_mirrored_winding(self):
        source, binary = fixture(); original = deepcopy(source)
        result, data = consolidate(source, binary)
        self.assertEqual(source, original)
        self.assertEqual(len(result['materials']), 1)
        self.assertEqual(len(result['meshes']), 2)
        nodes = result['nodes']
        target = result['animations'][0]['channels'][0]['target']['node']
        self.assertEqual(nodes[target]['name'], 'moving')
        self.assertEqual(nodes[target]['translation'], [0, 0, 1])
        mesh = result['meshes'][nodes[nodes[0]['children'][-1]]['mesh']]['primitives'][0]
        positions = accessor(result, data, mesh['attributes']['POSITION'])
        idx = [v[0] for v in accessor(result, data, mesh['indices'])]
        self.assertEqual([positions[i] for i in idx], [(2, 0, 0), (3, 0, 0), (2, 1, 0),
                                                     (0, 0, 0), (0, 2, 0), (-1, 0, 0)])
        tangents = accessor(result, data, mesh['attributes']['TANGENT'])
        self.assertIn((-1, 0, 0, -1), tangents)
        self.assertEqual(result['animations'][0]['extras'], {'loop': True})
        for old, new in zip(source['animations'][0]['samplers'], result['animations'][0]['samplers'], strict=True):
            for key in ('input', 'output'):
                self.assertEqual(accessor(source, binary, old[key]), accessor(result, data, new[key]))

    def test_blend_remains_separate_and_distinct_materials_are_not_averaged(self):
        doc, binary = fixture()
        doc['materials'][1]['alphaMode'] = 'BLEND'
        doc['nodes'].append({'name': 'second transparent instance', 'mesh': 1})
        doc['nodes'][0]['children'].append(5)
        result, _ = consolidate(doc, binary)
        self.assertEqual(len(result['materials']), 2)
        self.assertEqual(len(result['meshes']), 4)
        self.assertIn('mirrored', [n['name'] for n in result['nodes']])

    def test_embedded_image_bytes_and_bindings_survive_compaction(self):
        doc, binary = fixture()
        doc['bufferViews'].append({'buffer': 0, 'byteOffset': len(binary), 'byteLength': 8})
        doc['images'] = [{'name': 'strict data map', 'mimeType': 'image/png', 'bufferView': len(doc['bufferViews'])-1}]
        binary += b'DATA\x00\xff\x01\x80'
        doc['textures'] = [{'source': 0}]
        doc['materials'][0]['normalTexture'] = {'index': 0, 'scale': .12}
        result, data = consolidate(doc, binary)
        view = result['bufferViews'][result['images'][0]['bufferView']]
        self.assertEqual(data[view['byteOffset']:view['byteOffset']+view['byteLength']], b'DATA\x00\xff\x01\x80')
        self.assertEqual(result['materials'][0]['normalTexture'], {'index': 0, 'scale': .12})
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'fixture.glb'; write(p, result, data)
            loaded, payload = read(p)
            self.assertEqual(loaded['images'], result['images'])
            self.assertEqual(payload[:len(data)], data)

    def test_coincident_authored_corners_do_not_become_repeated_indices(self):
        doc, binary = fixture()
        builder = Buffer(doc, binary)
        attrs = doc['meshes'][0]['primitives'][0]['attributes']
        for name, index in list(attrs.items()):
            values = accessor(doc, binary, index)
            values[1] = values[0]
            schema = {k: doc['accessors'][index][k] for k in ('componentType', 'type')}
            attrs[name] = builder.add(values, schema, positions=name == 'POSITION')
        result, payload = consolidate(doc, builder.binary)
        # Exact zero-area triangles survive with distinct corner indices. No
        # epsilon-area filtering and no source-visible triangle loss is allowed.
        for mesh in result['meshes']:
            p = mesh['primitives'][0]
            indices = [v[0] for v in accessor(result, payload, p['indices'])]
            for i in range(0, len(indices), 3):
                self.assertEqual(len(set(indices[i:i+3])), 3)
        self.assertEqual(sum(result['accessors'][m['primitives'][0]['indices']]['count'] for m in result['meshes']), 9)

    def test_already_small_animated_selection_is_not_inflated(self):
        doc, binary = fixture()
        doc['nodes'] = [{'name': 'shimmer', 'mesh': 0}]
        doc['scenes'][0]['nodes'] = [0]
        doc['animations'][0]['channels'][0]['target']['node'] = 0
        with tempfile.TemporaryDirectory() as folder:
            p = Path(folder) / 'water.glb'; write(p, doc, binary)
            before = p.read_bytes()
            self.assertFalse(optimize(p, 'environment/hex_river_overlay_straight'))
            self.assertEqual(p.read_bytes(), before)

    def test_nested_nonuniform_transform_normal_is_inverse_transpose(self):
        from tools.asset_catalog.runtime_glb import normal_matrix, unit
        m = multiply(matrix({'translation': [1, 2, 3]}), matrix({'scale': [2, 3, 4]}))
        self.assertEqual(transform(m, (1, 1, 1), True), (3, 5, 7))
        normal, det = normal_matrix(m)
        n = unit(transform(normal, (1, 1, 0)))
        self.assertAlmostEqual(n[0]/n[1], 1.5)
        self.assertEqual(det, 24)
        self.assertEqual(multiply(IDENTITY, m), m)

    def test_unsupported_deformation_fails_without_modifying_input(self):
        for change in ('skins', 'targets', 'required', 'extension'):
            doc, binary = fixture()
            if change == 'skins': doc['skins'] = [{'joints': [0]}]
            if change == 'targets': doc['meshes'][0]['primitives'][0]['targets'] = [{'POSITION': 0}]
            if change == 'required': doc['extensionsRequired'] = ['EXT_mesh_gpu_instancing']
            if change == 'extension': doc['nodes'][1]['extensions'] = {'EXT_mesh_gpu_instancing': {}}
            original = deepcopy(doc)
            with self.assertRaises(ValueError): consolidate(doc, binary)
            self.assertEqual(doc, original)


if __name__ == '__main__':
    unittest.main()
