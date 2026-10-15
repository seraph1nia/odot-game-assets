"""Bounded runtime GLB consolidation, with no Blender/source mutations.

Bake stationary transforms into geometry under the nearest retained owner. Keep
all animation targets/ancestors and placement roots, and group only compatible
opaque/masked primitives by effective material and vertex layout. BLEND nodes
stay separate for transparency sorting. No skin/morph/extension guessing.
"""
from copy import deepcopy
import json
import math
import struct
from pathlib import Path

from tools.asset_pack.ambient_contract import ASSETS

VERSION = 'stationary_material_batches_v1'
COMPONENTS = {5120: ('b', 1), 5121: ('B', 1), 5122: ('h', 2),
              5123: ('H', 2), 5125: ('I', 4), 5126: ('f', 4)}
WIDTHS = {'SCALAR': 1, 'VEC2': 2, 'VEC3': 3, 'VEC4': 4}
IDENTITY = ((1, 0, 0, 0), (0, 1, 0, 0), (0, 0, 1, 0), (0, 0, 0, 1))


def read(path):
    data = Path(path).read_bytes()
    if len(data) < 20 or struct.unpack_from('<4sII', data) != (b'glTF', 2, len(data)):
        raise ValueError('Not a complete GLB 2')
    offset, doc, binary = 12, None, b''
    while offset < len(data):
        size, kind = struct.unpack_from('<I4s', data, offset)
        chunk = data[offset + 8:offset + 8 + size]
        if len(chunk) != size:
            raise ValueError('Truncated GLB chunk')
        if kind == b'JSON':
            doc = json.loads(chunk)
        elif kind == b'BIN\0':
            binary = chunk
        else:
            raise ValueError('Unsupported GLB chunk')
        offset += 8 + size
    if doc is None or len(doc.get('buffers', [])) != 1 or 'uri' in doc['buffers'][0]:
        raise ValueError('Expected one embedded GLB buffer')
    return doc, binary


def write(path, doc, binary):
    doc['buffers'] = [{'byteLength': len(binary)}]
    text = json.dumps(doc, separators=(',', ':'), ensure_ascii=False).encode()
    text += b' ' * (-len(text) % 4)
    binary = bytes(binary) + b'\0' * (-len(binary) % 4)
    Path(path).write_bytes(struct.pack('<4sII', b'glTF', 2, 28 + len(text) + len(binary))
                          + struct.pack('<I4s', len(text), b'JSON') + text
                          + struct.pack('<I4s', len(binary), b'BIN\0') + binary)


def accessor(doc, binary, index):
    a = doc['accessors'][index]
    if 'sparse' in a or 'bufferView' not in a:
        raise ValueError('Sparse/implicit accessors are not supported')
    view = doc['bufferViews'][a['bufferView']]
    code, size = COMPONENTS[a['componentType']]
    width = WIDTHS[a['type']]
    start = view.get('byteOffset', 0) + a.get('byteOffset', 0)
    stride = view.get('byteStride', width * size)
    return [struct.unpack_from('<' + code * width, binary, start + i * stride) for i in range(a['count'])]


def multiply(a, b):
    return tuple(tuple(sum(a[i][k] * b[k][j] for k in range(4)) for j in range(4)) for i in range(4))


def matrix(node):
    if 'matrix' in node:
        return tuple(tuple(node['matrix'][j * 4 + i] for j in range(4)) for i in range(4))
    x, y, z, w = node.get('rotation', (0, 0, 0, 1))
    s, t = node.get('scale', (1, 1, 1)), node.get('translation', (0, 0, 0))
    r = ((1-2*(y*y+z*z), 2*(x*y-z*w), 2*(x*z+y*w)),
         (2*(x*y+z*w), 1-2*(x*x+z*z), 2*(y*z-x*w)),
         (2*(x*z-y*w), 2*(y*z+x*w), 1-2*(x*x+y*y)))
    return tuple(tuple(r[i][j]*s[j] for j in range(3)) + (t[i],) for i in range(3)) + ((0, 0, 0, 1),)


def normal_matrix(m):
    a, b, c = m[0][:3]; d, e, f = m[1][:3]; g, h, i = m[2][:3]
    cof = ((e*i-f*h, f*g-d*i, d*h-e*g), (c*h-b*i, a*i-c*g, b*g-a*h),
           (b*f-c*e, c*d-a*f, a*e-b*d))
    det = a*cof[0][0] + b*cof[0][1] + c*cof[0][2]
    if abs(det) < 1e-15:
        raise ValueError('Cannot bake singular transform')
    return tuple(tuple(v/det for v in row) for row in cof), det


def transform(m, v, point=False):
    return tuple(sum(m[i][j]*v[j] for j in range(3)) + (m[i][3] if point else 0) for i in range(3))


def unit(v):
    length = math.sqrt(sum(c*c for c in v))
    return tuple(c / length for c in v) if length else (0, 0, 0)


class Buffer:
    def __init__(self, doc, binary):
        self.doc, self.binary = doc, bytearray(binary)

    def add(self, values, schema, *, positions=False):
        code, _ = COMPONENTS[schema['componentType']]
        width = WIDTHS[schema['type']]
        self.binary += b'\0' * (-len(self.binary) % 4)
        start = len(self.binary)
        pack = struct.Struct('<' + code * width).pack
        for value in values:
            self.binary.extend(pack(*value))
        views = self.doc.setdefault('bufferViews', [])
        views.append({'buffer': 0, 'byteOffset': start, 'byteLength': len(self.binary) - start})
        a = dict(schema, bufferView=len(views)-1, count=len(values))
        if positions:
            a['min'] = [min(v[i] for v in values) for i in range(3)]
            a['max'] = [max(v[i] for v in values) for i in range(3)]
        self.doc.setdefault('accessors', []).append(a)
        return len(self.doc['accessors']) - 1


def compact(doc, binary):
    """Drop unreferenced original geometry; keep encoded image/animation bytes."""
    used = set()
    for mesh in doc['meshes']:
        for p in mesh['primitives']:
            used.update(p['attributes'].values()); used.add(p['indices'])
    for animation in doc.get('animations', []):
        for s in animation['samplers']:
            used.update((s['input'], s['output']))
    ids = {old: new for new, old in enumerate(sorted(used))}
    accessors = [doc['accessors'][i] for i in sorted(used)]
    for mesh in doc['meshes']:
        for p in mesh['primitives']:
            p['attributes'] = {k: ids[v] for k, v in p['attributes'].items()}
            p['indices'] = ids[p['indices']]
    for animation in doc.get('animations', []):
        for s in animation['samplers']:
            s['input'], s['output'] = ids[s['input']], ids[s['output']]
    doc['accessors'] = accessors
    used_views = {a['bufferView'] for a in accessors}
    used_views.update(im['bufferView'] for im in doc.get('images', []))
    view_ids, views, output = {}, [], bytearray()
    for old in sorted(used_views):
        view = deepcopy(doc['bufferViews'][old])
        start = view.get('byteOffset', 0)
        output += b'\0' * (-len(output) % 4)
        view['byteOffset'] = len(output)
        output.extend(binary[start:start + view['byteLength']])
        view_ids[old] = len(views); views.append(view)
    for a in accessors:
        a['bufferView'] = view_ids[a['bufferView']]
    for im in doc.get('images', []):
        im['bufferView'] = view_ids[im['bufferView']]
    doc['bufferViews'] = views
    return output


def consolidate(doc, binary):
    """Return a new document/buffer; input is never mutated. Fail closed on rigs."""
    doc = deepcopy(doc)
    if doc.get('skins') or doc.get('extensionsRequired'):
        raise ValueError('Runtime consolidation does not support skins/required extensions')
    nodes = doc['nodes']
    parents = {}
    for i, node in enumerate(nodes):
        if node.get('extensions') or 'skin' in node or 'weights' in node:
            raise ValueError('Unsupported node deformation/extension')
        for c in node.get('children', []):
            if c in parents:
                raise ValueError('Multiple node parents')
            parents[c] = i
    keep = {i for i, n in enumerate(nodes) if n.get('name', '').endswith('_root')}
    for animation in doc.get('animations', []):
        for channel in animation['channels']:
            if channel['target']['path'] not in ('translation', 'rotation', 'scale'):
                raise ValueError('Only object transform animation is supported')
            keep.add(channel['target']['node'])
    # Ancestors retain their exact local TRS: animation values are never rebaked.
    for i in tuple(keep):
        while i in parents:
            i = parents[i]; keep.add(i)
    for i, node in enumerate(nodes):
        if 'mesh' in node:
            for p in doc['meshes'][node['mesh']]['primitives']:
                mat = doc.get('materials', [])[p['material']] if 'material' in p else {}
                if mat.get('alphaMode') == 'BLEND':
                    keep.add(i)
                    j = i
                    while j in parents:
                        j = parents[j]; keep.add(j)
    # Share only exactly equivalent material contracts, never palette averages.
    materials, mat_ids, keys = [], {}, {}
    for i, m in enumerate(doc.get('materials', [])):
        key = json.dumps({k: v for k, v in m.items() if k != 'name'}, sort_keys=True)
        if key not in keys:
            keys[key] = len(materials); materials.append(m)
        mat_ids[i] = keys[key]
    doc['materials'] = materials
    remap = {i: j for j, i in enumerate(sorted(keep))}
    result_nodes = []
    for i in sorted(keep):
        n = {k: v for k, v in nodes[i].items() if k not in ('children', 'mesh')}
        n['children'] = []
        result_nodes.append(n)
    # Multiple mesh-root component selections get a ground-zero static owner.
    synthetic = len(result_nodes)
    result_nodes.append({'name': 'runtime_static_root', 'children': []})
    groups, cached = {}, {}
    visited = set()

    def visit(i, owner, relative):
        if i in visited:
            raise ValueError('Node repeated across scenes or cyclic hierarchy')
        visited.add(i)
        node = nodes[i]
        relative = multiply(relative, matrix(node))
        if i in keep:
            current = remap[i]
            if owner != synthetic:
                result_nodes[owner]['children'].append(current)
            owner, relative = current, IDENTITY
        if 'mesh' in node:
            mesh = doc['meshes'][node['mesh']]
            if mesh.get('weights') or mesh.get('extensions'):
                raise ValueError('Unsupported mesh deformation/extension')
            normals, det = normal_matrix(relative)
            for p in mesh['primitives']:
                if p.get('mode', 4) != 4 or p.get('targets') or p.get('extensions'):
                    raise ValueError('Only plain triangle primitives are supported')
                if any(k.startswith(('JOINTS_', 'WEIGHTS_')) for k in p['attributes']):
                    raise ValueError('Cannot consolidate skinned geometry')
                schemas = {k: {s: doc['accessors'][v][s] for s in ('componentType', 'type', 'normalized')
                               if s in doc['accessors'][v]} for k, v in p['attributes'].items()}
                material = mat_ids.get(p.get('material'))
                key = (owner, material, json.dumps(schemas, sort_keys=True))
                attrs, indices = groups.setdefault(key, ({k: [] for k in schemas}, []))
                base = len(attrs['POSITION'])
                for name, index in p['attributes'].items():
                    if index not in cached:
                        cached[index] = accessor(doc, binary, index)
                    values = cached[index]
                    if name == 'POSITION':
                        values = [transform(relative, v, True) for v in values]
                    elif name == 'NORMAL':
                        values = [unit(transform(normals, v)) for v in values]
                    elif name == 'TANGENT':
                        values = [(*unit(transform(relative, v)), v[3] * (-1 if det < 0 else 1)) for v in values]
                    attrs[name].extend(values)
                if 'indices' in p:
                    idx = p['indices']
                    if idx not in cached:
                        cached[idx] = accessor(doc, binary, idx)
                    values = [v[0] for v in cached[idx]]
                else:
                    values = list(range(len(values)))
                if len(values) % 3:
                    raise ValueError('Incomplete triangle list')
                for start in range(0, len(values), 3):
                    a, b, c = values[start:start+3]
                    indices.extend(((base+a,), (base+c,), (base+b,)) if det < 0 else ((base+a,), (base+b,), (base+c,)))
        for child in node.get('children', []):
            visit(child, owner, relative)

    if len(doc.get('scenes', [])) != 1:
        raise ValueError('Expected one asset scene')
    roots = doc['scenes'][0]['nodes']
    for root in roots:
        visit(root, synthetic, IDENTITY)
    for animation in doc.get('animations', []):
        for channel in animation['channels']:
            channel['target']['node'] = remap[channel['target']['node']]
    builder = Buffer(doc, binary)
    meshes = []
    for (owner, material, schema_json), (attrs, indices) in groups.items():
        schemas = json.loads(schema_json)
        # Exact full-attribute weld reduces vertex bandwidth without UV/normal seams.
        names = sorted(attrs)
        vertex_keys = [tuple(attrs[n][i] for n in names) for i in range(len(attrs['POSITION']))]
        protected = set()
        for i in range(0, len(indices), 3):
            original = [v[0] for v in indices[i:i+3]]
            # Preserve distinct coincident corners in authored zero-area faces.
            # Blender's importer retains those, but drops repeated-index faces.
            # Never silently change that topology or filter a small real face.
            if len({vertex_keys[v] for v in original}) < len(set(original)):
                protected.update(original)
        unique, welded, table = {n: [] for n in names}, [], {}
        for i in range(len(attrs['POSITION'])):
            key = (vertex_keys[i], i if i in protected else None)
            if key not in table:
                table[key] = len(table)
                for n in names:
                    unique[n].append(attrs[n][i])
            welded.append(table[key])
        p = {'attributes': {n: builder.add(unique[n], schemas[n], positions=n == 'POSITION') for n in names},
             'indices': builder.add([(welded[v[0]],) for v in indices], {'componentType': 5125, 'type': 'SCALAR'})}
        if material is not None:
            p['material'] = material
        name = f'Runtime surface {len(meshes):03}'
        result_nodes[owner]['children'].append(len(result_nodes))
        result_nodes.append({'name': name, 'mesh': len(meshes)})
        meshes.append({'name': name, 'primitives': [p]})
    # The synthetic node is intentionally kept only if it owns component meshes.
    used_synthetic = bool(result_nodes[synthetic]['children'])
    scene_roots = [remap[r] for r in roots if r in keep]
    if used_synthetic:
        scene_roots.append(synthetic)
    if not used_synthetic:
        # Remove the one unused node and shift later batch indices.
        result_nodes.pop(synthetic)
        for n in result_nodes:
            if 'children' in n:
                n['children'] = [i - int(i > synthetic) for i in n['children']]
    for n in result_nodes:
        if n.get('children') == []:
            del n['children']
    doc['nodes'], doc['meshes'] = result_nodes, meshes
    doc['scenes'][0]['nodes'] = scene_roots
    doc.setdefault('asset', {}).setdefault('extras', {})['runtime_optimization'] = VERSION
    return doc, compact(doc, builder.binary)


def optimize(path, asset_id):
    """Official selected-export hook; units and unapproved assets remain untouched."""
    if asset_id not in ASSETS:
        return False
    doc, binary = read(path)
    candidate, payload = consolidate(doc, binary)
    # The tiny water components/overlays are already cheap transform targets.
    # Do not turn eight animated mesh nodes into eight empties plus eight meshes.
    # Only publish batching when it actually lowers total scene-node overhead.
    if len(candidate['nodes']) >= len(doc['nodes']):
        return False
    write(path, candidate, payload)
    return True
