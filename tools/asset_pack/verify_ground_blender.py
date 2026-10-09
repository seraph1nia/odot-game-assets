"""Read saved detailed floors and real GLBs; exhaust rotation/seam/stack contracts.

Never rebuild/save a source. Evidence is scoped to this suite. Generic fidelity,
painted-channel audits and existing-asset regressions remain existing check routes.
"""
import hashlib
import itertools
import json
import math
import struct
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import numpy as np
from mathutils import Matrix

import art_style as style
import hex_ground as ground
from tools.asset_catalog.blender_selection import load_asset
from tools.asset_catalog.export_sources import plan_exports
from tools.asset_catalog.metadata import read_glb
from tools.asset_pack.verify_painted_blender import source_channels

EPS = 2e-5


def document(path):
    data = path.read_bytes()
    length, kind = struct.unpack_from('<II', data, 12)
    assert kind == 0x4E4F534A
    return json.loads(data[20:20+length])


def snapshot(objects):
    bpy.context.view_layer.update()
    roots = [obj for obj in objects if obj.name.endswith('_root') and obj.parent is None]
    assert len(roots) == 1
    root = roots[0]
    assert root.location.length < EPS
    assert root['ground_schema'] == 1 and isinstance(root['ground_schema'], int)
    assert root['ground_layer'] in ('base', 'overlay')
    points, uvs = [], []
    for obj in objects:
        if obj.type != 'MESH':
            continue
        assert obj.data.uv_layers and obj.data.materials
        points.extend(tuple(obj.matrix_world @ v.co) for v in obj.data.vertices)
        uvs.extend(tuple(loop.uv) for loop in obj.data.uv_layers.active.data)
        assert all(poly.normal.z >= -.001 for poly in obj.data.polygons) if root['ground_layer'] == 'overlay' else True
    points = np.array(points)
    assert np.isfinite(points).all() and np.isfinite(uvs).all()
    assert all(style.HEX.contains(x, y, EPS) for x, y, z in points)
    assert abs(points[:, 2].min()-root['ground_height_min']) < EPS
    assert abs(points[:, 2].max()-root['ground_height_max']) < EPS
    extras = {key: (root[key].to_list() if hasattr(root[key], 'to_list') else root[key])
              for key in root.keys() if key != '_RNA_UI'}
    return {'points': points, 'uvs': uvs, 'extras': extras}


def unique_rows(points):
    # Float32 reimport tolerances: compare nearest points, not rounded hash bins.
    return np.unique(np.round(points, 5), axis=0)


def assert_same(a, b):
    a, b = np.array(a), np.array(b)
    distances = np.linalg.norm(a[:, None, :] - b[None, :, :], axis=-1)
    assert distances.min(axis=1).max() < EPS and distances.min(axis=0).max() < EPS


def interface(points, edge, center=(0, 0)):
    points = points.copy()
    points[:, :2] -= center
    n = np.array(ground.normal(edge))
    projection = points[:, :2] @ n
    row = points[abs(projection-style.HEX.half_height) < EPS]
    assert len(row) >= 5
    return unique_rows(row)


def inspect_interfaces(points, family, edges):
    observed = {edge for edge in range(6) if sum(abs(points[:, :2] @ np.array(ground.normal(edge))
                                                - style.HEX.half_height) < EPS) >= 5}
    assert observed == set(edges), ('undeclared/missing mesh edge', observed, edges)
    if len(edges) == 1:
        n = np.array(ground.normal(edges[0]))
        # Dead end reaches the center with only a half-width terminal cap beyond.
        assert abs(float((points[:, :2] @ n).min())) <= style.GROUND.width(family)/2+EPS
    profile = style.GROUND.profile(family)
    width = style.GROUND.width(family)
    for edge in edges:
        n = ground.normal(edge)
        t = (-n[1], n[0])
        expected = [(style.HEX.half_height*n[0]+x*width*t[0],
                     style.HEX.half_height*n[1]+x*width*t[1], z) for x, z in profile]
        assert_same(interface(points, edge), expected)
        inward = points[(points[:, :2] @ n > style.HEX.half_height-style.GROUND.approach+EPS)]
        cross = inward[:, :2] @ t
        assert all(min(abs(value-x*width) for x, z in profile) < EPS for value in cross)
        for point, value in zip(inward, cross, strict=True):
            expected_z = min(profile, key=lambda pair: abs(value-pair[0]*width))[1]
            assert abs(point[2]-expected_z) < EPS


def rotated(points, turns, center=(0, 0)):
    result = np.array([ground.rotate(p, turns) for p in points])
    result[:, :2] += center
    return result


def verify_coverage(records):
    pairs, ends = ground.coverage()
    assert set(pairs) == set(itertools.combinations(range(6), 2))
    assert set(ends) == {(edge,) for edge in range(6)}
    output = {}
    for family, prefix in (('path', 'hex_path_'), ('river', 'hex_river_overlay_')):
        orientations = []
        for key, (piece, turns) in {**pairs, **ends}.items():
            source = records['environment/'+prefix+piece]
            points = rotated(source['points'], turns)
            assert sorted((e+turns)%6 for e in source['extras']['connector_edges']) == list(key)
            inspect_interfaces(points, family, key)
            orientations.append((key, points))
        seams = 0
        for key, points in orientations:
            for edge in key:
                center = tuple(2*style.HEX.half_height*v for v in ground.normal(edge))
                opp = (edge+3)%6
                seam = interface(points, edge)
                for neighbor_key, neighbor_points in orientations:
                    if opp not in neighbor_key:
                        continue
                    neighbor_points = neighbor_points.copy()
                    neighbor_points[:, :2] += center
                    other = interface(neighbor_points, opp, center)
                    other[:, :2] += center
                    assert_same(seam, other)
                    seams += 1
        output[family] = {'through_pairs': {','.join(map(str, k)): {'piece': p, 'source_z_degrees': t*60}
                                           for k, (p, t) in pairs.items()},
                          'center_ends': [k[0] for k in ends], 'neighbor_seams_tested': seams}
    return output


def main():
    records = {'source': {}, 'glb': {}}
    resources = []
    for job in plan_exports(ROOT, ground.IDS):
        objects = load_asset(job, ROOT)
        source = snapshot(objects)
        materials = {slot.material for obj in objects if obj.type == 'MESH'
                     for slot in obj.material_slots if slot.material}
        source_pixels = {}
        for mat in materials:
            assert set(source_channels(mat)) == {'baseColorTexture', 'metallicRoughnessTexture', 'normalTexture'}
            for node in mat.node_tree.nodes:
                if node.type != 'TEX_IMAGE':
                    continue
                expected_space = 'sRGB' if node.image.name.endswith('base_color') else 'Non-Color'
                assert node.image.colorspace_settings.name == expected_space
                field = 'color' if node.image.name.endswith('base_color') else 'normal' if node.image.name.endswith('normal') else 'roughness'
                source_pixels[(mat.name, field)] = np.array(node.image.pixels[:]).reshape(-1, 4)[:, :3]
                # No variation at either endpoint, and symmetric cross-profile.
                if source['extras']['ground_layer'] == 'overlay':
                    pixels = np.array(node.image.pixels[:]).reshape(node.image.size[1], node.image.size[0], 4)
                    assert np.max(abs(pixels[0]-pixels[-1])) < .009, (job['id'], node.image.name, 'endpoint texture seam')
                    assert np.max(abs(pixels[0]-pixels[0, ::-1])) < .009
        path = ROOT/'exports'/f"{job['id']}.glb"
        doc = document(path)
        assert all(mat['pbrMetallicRoughness'].get('baseColorFactor', [1, 1, 1, 1]) == [1, 1, 1, 1]
                   for mat in doc['materials']), 'effective textured albedo multiplied in export'
        for obj in list(bpy.data.objects):
            bpy.data.objects.remove(obj, do_unlink=True)
        bpy.ops.import_scene.gltf(filepath=str(path))
        imported = snapshot(list(bpy.context.scene.objects))
        imported_materials = {slot.material for obj in bpy.context.scene.objects if obj.type == 'MESH'
                              for slot in obj.material_slots if slot.material}
        for mat in imported_materials:
            shader = next(node for node in mat.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
            source_name = next(name for name, field in source_pixels if mat.name == name or mat.name.startswith(name+'.'))
            for socket, field in (('Base Color', 'color'), ('Normal', 'normal'), ('Roughness', 'roughness')):
                node = shader.inputs[socket].links[0].from_node
                while node.type != 'TEX_IMAGE':
                    linked = next(inp for inp in node.inputs if inp.links)
                    node = linked.links[0].from_node
                pixels = np.array(node.image.pixels[:]).reshape(-1, 4)[:, :3]
                expected = source_pixels[(source_name, field)]
                actual = pixels[:, 1] if field == 'roughness' else pixels
                expected = expected[:, 0] if field == 'roughness' else expected
                assert np.max(abs(actual-expected)) < .009, (job['id'], field, 'portable pixels differ')
        assert_same(unique_rows(source['points']), unique_rows(imported['points']))
        assert_same(unique_rows(source['uvs']), unique_rows(imported['uvs']))
        for key in ('ground_schema', 'ground_layer', 'ground_family', 'ground_height_min', 'ground_height_max'):
            assert source['extras'][key] == imported['extras'][key]
        if source['extras']['ground_layer'] == 'overlay':
            for key in ('connector_piece', 'connector_edges', 'connector_center_end', 'connector_interface',
                        'connector_width', 'connector_approach', 'connector_profile'):
                a, b = source['extras'][key], imported['extras'][key]
                assert a == b, (job['id'], key, a, b)
            edges = list(imported['extras']['connector_edges'])
            assert all(isinstance(e, int) and 0 <= e < 6 for e in edges)
            inspect_interfaces(imported['points'], imported['extras']['ground_family'], edges)
        else:
            assert abs(source['points'][:, 2].max()-style.HEX.surface) < EPS
            assert abs(source['points'][:, 2].min()-style.HEX.bottom) < EPS
        if source['extras']['ground_layer'] == 'overlay':
            # Exercise real imported root placement, not only array arithmetic.
            # glTF roots use quaternion rotation mode in this runtime.
            imported_root = next(obj for obj in bpy.context.scene.objects
                                 if obj.name.endswith('_root') and obj.parent is None)
            original_matrix = imported_root.matrix_world.copy()
            for turns in range(6):
                imported_root.matrix_world = Matrix.Rotation(turns*math.pi/3, 4, 'Z') @ original_matrix
                placed = snapshot(list(bpy.context.scene.objects))
                assert_same(placed['points'], rotated(imported['points'], turns))
                inspect_interfaces(placed['points'], imported['extras']['ground_family'],
                                   [(edge+turns)%6 for edge in imported['extras']['connector_edges']])
            imported_root.matrix_world = original_matrix
            bpy.context.view_layer.update()
        records['source'][job['id']] = source
        records['glb'][job['id']] = imported
        facts = read_glb(path)
        images = {node.image for mat in materials for node in mat.node_tree.nodes if node.type == 'TEX_IMAGE'}
        # Images above belong to source datablocks retained by import; record actual dimensions.
        resources.append({'asset_id': job['id'], **facts, 'images': len(doc['images']),
                          'decoded_rgba8_image_bytes': sum(im.size[0]*im.size[1]*4 for im in images),
                          'source_sha256': hashlib.sha256((ROOT/job['source']).read_bytes()).hexdigest()})
        print('Verified source/GLB ground semantics:', job['id'], flush=True)
    coverage = {mode: verify_coverage(items) for mode, items in records.items()}
    stacks = []
    for base in ground.IDS[:5]:
        for overlay in ground.IDS[5:]:
            clearance = records['glb'][overlay]['points'][:, 2].min()-records['glb'][base]['points'][:, 2].max()
            assert clearance >= .006-EPS
            stacks.append({'base': base, 'overlay': overlay, 'minimum_geometric_clearance': round(float(clearance), 6)})
    result = {'runtime': bpy.app.version_string, 'real_imported_root_rotations_tested': 48,
              'source_and_glb_rotation_coverage': coverage,
              'base_overlay_stacks': stacks, 'resources': resources,
              'height_envelope': {'base_surface': 0, 'base_bottom': style.HEX.bottom,
                                  'path': [.006, .012], 'surface_river': [.006, .016]},
              'limitations': ['Surface-stream overlays do not match old recessed river elevation.',
                              'Normal depth tests and occupant contact placement required.',
                              'Counts are not native GPU performance; RGBA8 excludes mips.']}
    path = ROOT/'docs/detailed-ground/verification.json'
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(result, indent=2)+'\n')
    print('All 15 pairs + six ends per family, source/GLB seams and 40 stacks passed')


if __name__ == '__main__':
    main()
