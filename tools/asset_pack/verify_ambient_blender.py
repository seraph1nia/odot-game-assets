"""Independent saved-source and actual GLB ambient playback/preservation audit."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from vivid_refinement import data_binding, sha_bytes, structure
from tools.asset_pack.encoded_images import image_proof, UnsupportedImage
import art_style as style
from tools.asset_catalog.export_sources import plan_exports
from tools.asset_catalog.blender_selection import asset_objects
from tools.asset_pack.ambient_contract import ASSETS, receipts, sha

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/ambient-motion'
SPEC = style.AMBIENT


def plain(value):
    if hasattr(value, 'to_dict'):
        return plain(value.to_dict())
    if hasattr(value, 'to_list'):
        return plain(value.to_list())
    if isinstance(value, dict):
        return {k: plain(v) for k, v in value.items()}
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    try:
        return [plain(v) for v in value]
    except TypeError:
        return repr(value)


def capture():
    bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    materials = {}
    for mat in bpy.data.materials:
        nodes = []
        if mat.use_nodes:
            for node in mat.node_tree.nodes:
                nodes.append((node.name, node.bl_idname,
                    [(i.name, plain(i.default_value)) for i in node.inputs if hasattr(i, 'default_value')],
                    data_binding(mat, node) if node.type == 'TEX_IMAGE' and node.image else None))
        links = sorted((l.from_node.name, l.from_socket.name, l.to_node.name, l.to_socket.name)
                       for l in mat.node_tree.links) if mat.use_nodes else []
        materials[mat.name] = sha_bytes(repr((plain(mat.diffuse_color), nodes, links, plain(dict(mat.items())))).encode())
    images = {}
    for im in bpy.data.images:
        if im.source == 'VIEWER' and im.type == 'COMPOSITING':
            # Blender's compositor Viewer is a nonpersistent presentation buffer,
            # not a texture. Prove it has no ID users before inventorying it as
            # such; any material/world/group/image-node binding fails closed.
            owners = bpy.data.user_map(subset={im}).get(im, set())
            if owners:
                raise UnsupportedImage(im.name + ': compositor buffer has image users; cannot exclude it from texture preservation')
            images[im.name] = {'unbound_nonpersistent_compositor_buffer': True, 'source': im.source,
                'type': im.type, 'dimensions': list(im.size), 'color_space': im.colorspace_settings.name,
                'alpha_mode': im.alpha_mode, 'use_view_as_render': im.use_view_as_render,
                'is_float': im.is_float, 'packed': bool(im.packed_file), 'image_user_count': 0}
        elif im.size[0]:
            images[im.name] = image_proof(im)
        elif im.type == 'RENDER_RESULT' and not im.packed_file:
            if bpy.data.user_map(subset={im}).get(im, set()):
                raise UnsupportedImage(im.name + ': empty render buffer has image users; cannot exclude it from texture preservation')
            images[im.name] = {'empty_render_result': True, 'type': im.type, 'dimensions': list(im.size),
                               'source': im.source, 'color_space': im.colorspace_settings.name, 'image_user_count': 0}
        else:
            raise UnsupportedImage(im.name + ': empty/unpacked image is not a verifiable saved map')
    return {'structure': structure(), 'materials': materials, 'images': images,
            'transforms': {o.name: (o.parent.name if o.parent else None, [list(row) for row in o.matrix_world]) for o in bpy.data.objects},
            'settings': {o.name: (plain(dict(o.items())), o.hide_render, o.hide_viewport,
                [list(row) for row in o.matrix_basis], [list(row) for row in o.matrix_parent_inverse],
                [(s.link, s.material.name if s.material else None) for s in o.material_slots]) for o in bpy.data.objects},
            'collections': {c.name: (sorted(o.name for o in c.objects), plain(dict(c.items()))) for c in bpy.data.collections},
            'ids': {kind: sorted(item.name for item in getattr(bpy.data, kind))
                    for kind in ('objects', 'meshes', 'materials', 'images', 'actions', 'armatures', 'curves', 'collections')}}


def compare(before, record):
    """Allow only declared pivot binds, new ambient channels and four tiny strips.

    All original objects/IDs, mesh data, UVs, material slots/overrides, full color
    and data images, shader values, existing actions, custom tags and collection
    membership survive. World matrices are independently checked before their
    tiny floating-point bind noise is normalized for the structural hash.
    """
    bpy.context.scene.frame_set(1); bpy.context.view_layer.update()
    parents, new_objects, new_meshes, new_materials, new_images = {}, [], [], [], []
    for feature in record['features']:
        if feature['pivot']:
            new_objects.append(feature['pivot'])
            parents.update({n: feature['pivot'] for n in feature['original_parents']})
        if added := feature['added_geometry']:
            new_objects.append(added['object']); new_meshes.append(added['mesh']); new_materials.append(added['material'])
            new_images.extend(added.get('images', []))
    actual = capture()
    additions = {'objects': new_objects, 'meshes': new_meshes, 'materials': new_materials, 'images': new_images, 'actions': [SPEC.clip]}
    for kind, names in before['ids'].items():
        assert set(actual['ids'][kind]) == set(names) | set(additions.get(kind, [])), ('unexpected ID change', kind)
    max_error = 0
    for name, (old_parent, matrix) in before['transforms'].items():
        obj = bpy.data.objects[name]
        assert (obj.parent.name if obj.parent else None) == parents.get(name, old_parent), ('unexpected parent', name)
        error = max(abs(matrix[i][j] - obj.matrix_world[i][j]) for i in range(4) for j in range(4))
        max_error = max(max_error, error)
        assert error < 2e-6, ('rest transform', name, error)
        old = before['settings'][name]; current = actual['settings'][name]
        assert old[:3] == current[:3] and old[5] == current[5], ('object settings/material overrides', name)
        # Existing bases are untouched; only explicit pivot children get a bind inverse.
        assert old[3] == current[3], ('authored local basis', name)
        if name not in parents:
            assert old[4] == current[4], ('unrelated parent inverse', name)
    normalized = structure(object_transforms=before['transforms'])
    for name, digest in before['structure'].items():
        assert normalized[name] == digest, ('mesh/UV/reuse/modifier/rig/action structure', name)
    for field in ('materials', 'images'):
        for name, value in before[field].items():
            assert actual[field][name] == value, ('original ' + field, name)
    for name, (members, tags) in before['collections'].items():
        observed, observed_tags = actual['collections'][name]
        assert [n for n in observed if n not in new_objects] == members and observed_tags == tags, ('collection ownership', name)
    action = bpy.data.actions[SPEC.clip]
    assert action.get('loop') is True
    assert tuple(round(f) for f in action.frame_range) == (SPEC.frames[0], SPEC.frames[-1])
    expected = {channel['object']: channel for f in record['features'] for channel in f['channels']}
    linked = {o.name for o in bpy.data.objects if o.animation_data and o.animation_data.action == action}
    assert linked == set(expected), ('unexpected animated targets', linked ^ set(expected))
    channels = 0
    for name, spec in expected.items():
        obj = bpy.data.objects[name]
        bag = action.layers[0].strips[0].channelbag(obj.animation_data.action_slot)
        for curve in bag.fcurves:
            assert curve.data_path == spec['path']
            assert spec['axis'] is None or curve.array_index == spec['axis']
            assert [round(k.co.x) for k in curve.keyframe_points] == list(SPEC.frames)
            assert len(curve.keyframe_points) == 5
            assert abs(curve.keyframe_points[0].co.y - curve.keyframe_points[-1].co.y) < 1e-7
            channels += 1
    return {'all_original_ids_retained': True, 'original_geometry_uv_reuse_rigs_actions_equal': True,
            'all_original_full_materials_and_images_equal': True, 'original_rest_matrix_max_error': max_error,
            'image_preservation_method': 'exact packed PNG bytes and independent encoded samples/alpha; no normalized float reads',
            'original_image_proofs': before['images'], 'unsupported_map_count': 0,
            'only_declared_pivot_parent_changes': True, 'original_collection_ownership_equal': True,
            'authored_keys_per_channel': 5, 'authored_channels': channels,
            'new_objects': new_objects, 'new_meshes': new_meshes, 'new_materials': new_materials}


def matrices(objects):
    bpy.context.view_layer.update()
    return {o.name: [list(row) for row in o.matrix_world] for o in objects}


def difference(a, b):
    return max((abs(x - y) for name in a for r, s in zip(a[name], b[name], strict=True)
                for x, y in zip(r, s, strict=True)), default=0)


def points(objects):
    bpy.context.view_layer.update(); depsgraph = bpy.context.evaluated_depsgraph_get()
    result = []
    for obj in sorted(objects, key=lambda o: o.name):
        if obj.type != 'MESH':
            continue
        evaluated = obj.evaluated_get(depsgraph); mesh = evaluated.to_mesh()
        result.extend(tuple(evaluated.matrix_world @ v.co) for v in mesh.vertices)
        evaluated.to_mesh_clear()
    return result


def playback(job, feature):
    """Evaluate real source and GLB-imported mesh points, not just clip names."""
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / job['source']))
    objects = asset_objects(job)
    moving_names = {c['object'] for c in feature['channels']}
    moving = [o for o in objects if o.name in moving_names or any(p.name in moving_names for p in ancestors(o))]
    assert moving and all(o.name != job['id'].split('/')[-1] + '_root' for o in moving)
    fixed = [o for o in objects if o not in moving]
    moving_objects = sorted(o.name for o in moving)
    source_samples, fixed_samples = [], []
    for frame in SPEC.frames:
        bpy.context.scene.frame_set(frame)
        source_samples.append(points(objects))
        fixed_samples.append(matrices(fixed))
    assert max(difference(fixed_samples[0], s) for s in fixed_samples) < 1e-7, (job['id'], 'static structure moved')
    assert source_samples[0] == source_samples[-1], (job['id'], 'source loop seam')
    assert any(source_samples[0] != sample for sample in source_samples[1:-1]), (job['id'], 'no actual source motion')
    # Keep the source in its own scene, then import the actual published GLB.
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.context.scene.render.fps = SPEC.fps
    bpy.ops.import_scene.gltf(filepath=str(ROOT / 'exports' / (job['id'] + '.glb')))
    imported = list(bpy.context.scene.objects)
    assert len(bpy.data.actions) == 1, (job['id'], 'expected one exported ambient clip')
    action = next(iter(bpy.data.actions))
    assert action.name.startswith(SPEC.clip), (job['id'], action.name)
    samples = []
    for frame in SPEC.frames:
        bpy.context.scene.frame_set(frame); samples.append(points(imported))
    assert samples[0] == samples[-1], (job['id'], 'export loop seam')
    assert any(samples[0] != sample for sample in samples[1:-1]), (job['id'], 'exported mesh does not move')
    # Export applies modifiers and splits/reorders vertices. A symmetric nearest
    # point distance avoids both order assumptions and rounding-bin boundaries.
    from mathutils.kdtree import KDTree
    def distance(a, b):
        tree = KDTree(len(b))
        for i, point in enumerate(b):
            tree.insert(point, i)
        tree.balance()
        return max(tree.find(point)[2] for point in a)
    errors = []
    for source, exported in zip(source_samples, samples, strict=True):
        error = max(distance(source, exported), distance(exported, source))
        errors.append(error)
        assert error < .0001, (job['id'], 'source/export pose differs by more than 0.1mm', error)
    return {'source_sha256': sha(ROOT / job['source']), 'glb_sha256': sha(ROOT / 'exports' / (job['id'] + '.glb')),
            'frames': list(SPEC.frames), 'seconds': (SPEC.frames[-1] - 1) / SPEC.fps,
            'source_and_export_meshes_move': True, 'source_and_export_endpoints_equal': True,
            'fixed_objects_world_matrices_equal_throughout': True, 'evaluated_pose_point_cloud_max_error_m': max(errors),
            'moving_objects': moving_objects, 'fixed_object_count': len(fixed)}


def ancestors(obj):
    while obj.parent:
        obj = obj.parent
        yield obj


def main():
    authored = receipts(ROOT); report = {'sources': {}, 'assets': {}}
    for path, record in authored.items():
        backup = ROOT / '.cache/ambient-motion/before' / path
        assert sha(backup) == record['sha256_before'] and sha(ROOT / path) == record['sha256_after'], path
        bpy.ops.wm.open_mainfile(filepath=str(backup)); before = capture()
        bpy.ops.wm.open_mainfile(filepath=str(ROOT / path)); result = compare(before, record)
        report['sources'][path] = {'sha256_before': sha(backup), 'sha256_after': sha(ROOT / path), **result}
        print('Strict motion preservation:', path, flush=True)
    jobs = {j['id']: j for j in plan_exports(ROOT, ASSETS)}
    features = {f['asset']: f for r in authored.values() for f in r['features']}
    assert set(features) == set(ASSETS)
    for aid, feature in features.items():
        report['assets'][aid] = playback(jobs[aid], feature)
        print('Actual exported motion:', aid, flush=True)
    (DOCS / 'validation.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Ambient validation passed:', len(report['sources']), 'sources;', len(report['assets']), 'actual GLB loops')


if __name__ == '__main__':
    main()
