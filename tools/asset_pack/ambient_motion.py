"""Explicit localized object actions on existing sources; never rebuild a library.

Run in an isolated Blender worker. Always author all 16 buildings and nine water
entries. Originals are checkpointed, then each complete source is scratch-saved,
reloaded and independently audited before atomic replacement. Completed sources
are retained on resume; partial asset selection is not supported.
"""
import argparse
import json
import math
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from mathutils import Matrix, Vector
import art_style as style
import geometry as g
import hex_ground
import painted_finish
from vivid_refinement import preserve_orphans
from tools.asset_catalog.export_sources import plan_exports
from tools.asset_catalog.blender_selection import asset_objects
from tools.asset_pack.ambient_contract import ASSETS, BUILDINGS, WATER, PALETTE_COMMIT, sha

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/ambient-motion'
SPEC = style.AMBIENT


def bounds(objects):
    points = [obj.matrix_world @ Vector(p) for obj in objects for p in obj.bound_box]
    return Vector([min(p[i] for p in points) for i in range(3)]), Vector([max(p[i] for p in points) for i in range(3)])


def animate(action, obj, path, vector, *, index=None):
    """Five authored keys, endpoint rest and zero-speed seam; one shared clip."""
    assert not obj.animation_data or not obj.animation_data.action, obj.name
    obj.animation_data_create()
    obj.animation_data.action = action
    obj.animation_data.action_slot = action.slots.new('OBJECT', obj.name)
    original = getattr(obj, path).copy()
    for frame, amount in zip(SPEC.frames, (0, 1, 0, -1, 0), strict=True):
        setattr(obj, path, Vector(original) + Vector(vector) * amount)
        obj.keyframe_insert(data_path=path, index=index if index is not None else -1, frame=frame, group='Localized ambient detail')
    setattr(obj, path, original)
    bag = action.layers[0].strips[0].channelbag(obj.animation_data.action_slot)
    for curve in bag.fcurves:
        for key in curve.keyframe_points:
            key.interpolation = 'BEZIER'
            key.handle_left_type = key.handle_right_type = 'AUTO_CLAMPED'
    return {'object': obj.name, 'path': path, 'axis': index, 'amplitude': list(vector), 'keys_per_channel': len(SPEC.frames)}


def building(job, action):
    name = job['id'].split('/')[-1]
    mode, prefixes, description = BUILDINGS[name]
    objects = [o for o in asset_objects(job) if o.type == 'MESH']
    if mode == 'lantern':
        glasses = [o for o in objects if o.name.startswith('Lantern amber glass')]
        assert glasses, name
        glass = min(glasses, key=lambda o: bounds([o])[0].y + bounds([o])[1].y)
        low, high = bounds([glass]); center = (low + high) / 2
        targets = []
        for obj in objects:
            if not obj.name.startswith(('Lantern amber glass', 'Lantern bottom', 'Lantern corner', 'Lantern roof', 'Lantern hanger')):
                continue
            a, b = bounds([obj]); c = (a + b) / 2
            if abs(c.x - center.x) < .13 and abs(c.y - center.y) < .13:
                targets.append(obj)
        assert len(targets) >= 8, (name, [o.name for o in targets])
    else:
        targets = [o for o in objects if o.name.startswith(prefixes)]
    assert targets and len({o.parent for o in targets}) == 1, (name, [o.name for o in targets])
    low, high = bounds(targets)
    center = (low + high) / 2
    if mode in ('banner', 'lantern', 'sign', 'hook', 'bell'):
        center.z = high.z
    if mode == 'flag':
        center.x, center.z = low.x, high.z
    pivot = bpy.data.objects.new('Ambient ' + name + ' detail pivot', None)
    pivot.empty_display_type = 'PLAIN_AXES'
    pivot.empty_display_size = .08
    pivot['ambient_detail'] = description
    collection = bpy.data.collections[job['collection']] if job.get('collection') else targets[0].users_collection[0]
    collection.objects.link(pivot)
    parent = targets[0].parent
    pivot.parent = parent
    pivot.matrix_world = Matrix.Translation(center)
    parents = {}
    for obj in targets:
        parents[obj.name] = obj.parent.name if obj.parent else None
        # Keep authored mesh transforms/data and complete ownership ancestry.
        obj.parent = pivot
        obj.matrix_parent_inverse = pivot.matrix_world.inverted() @ (parent.matrix_world if parent else Matrix.Identity(4)) @ obj.matrix_parent_inverse
    bpy.context.view_layer.update()
    if mode == 'shuttle':
        vector = Vector((SPEC.shuttle_travel, 0, 0))
        # Translation is authored in parent space, independent of scaled roles.
        vector = parent.matrix_world.to_3x3().inverted() @ vector if parent else vector
        channel = animate(action, pivot, 'location', vector)
    else:
        axis = 2 if mode in ('crystal', 'armillary') else 1 if mode == 'flag' else 0
        amplitude = math.radians(SPEC.crystal_degrees if mode == 'crystal' else SPEC.swing_degrees)
        vector = [0, 0, 0]; vector[axis] = amplitude
        channel = animate(action, pivot, 'rotation_euler', vector, index=axis)
    return {'asset': job['id'], 'description': description, 'targets': sorted(parents),
            'original_parents': parents, 'pivot': pivot.name, 'channels': [channel], 'added_geometry': None}


def shimmer(job, action, *, directory=None):
    """Only the four otherwise single-mesh overlays need a small movable glint."""
    piece = job['id'].removeprefix('environment/hex_river_overlay_')
    points, tangents = hex_ground.centerline(piece)
    middle = len(points) // 2
    x, y = points[middle]; tx, ty = tangents[middle]
    z = dict(style.GROUND.profile('river'))[0] + SPEC.shimmer_clearance
    vertices = []
    for i in range(5):
        u = (i / 4 - .5) * SPEC.shimmer_length
        v = math.sin(i * math.pi / 4) * .012
        width = SPEC.shimmer_width * (.4 + .6 * math.sin(i * math.pi / 4))
        vertices.extend(((u, v - width / 2, 0), (u, v + width / 2, 0)))
    faces = [(2*i, 2*i+2, 2*i+3, 2*i+1) for i in range(4)]
    previous_images = set(im.name for im in bpy.data.images)
    mat = g.material('water_ambient_shimmer', SPEC.shimmer_color, roughness=.84)
    painted_finish.texture_material(mat, Path(directory) if directory else ROOT / 'sources/environment/textures/ambient-motion')
    new_images = sorted(set(im.name for im in bpy.data.images) - previous_images)
    mesh = bpy.data.meshes.new('Shared ambient water shimmer strip')
    mesh.from_pydata(vertices, [], faces); mesh.materials.append(mat); mesh.update()
    uv = mesh.uv_layers.new(name='UVMap')
    for loop in mesh.loops:
        vi = loop.vertex_index
        uv.data[loop.index].uv = (vi // 2 / 4, vi % 2)
    obj = bpy.data.objects.new('Ambient interior water shimmer', mesh)
    col = bpy.data.collections[job['collection']]; col.objects.link(obj)
    obj.parent = bpy.data.objects[job['id'].split('/')[-1] + '_root']
    obj.location = (x, y, z)
    # Local X spans the channel; local Y follows its tangent.
    obj.rotation_euler.z = math.atan2(-tx, ty)
    channel = animate(action, obj, 'location', (tx * SPEC.current_travel, ty * SPEC.current_travel, 0))
    return {'asset': job['id'], 'description': WATER[job['id']], 'targets': [], 'original_parents': {},
            'pivot': None, 'channels': [channel], 'added_geometry': {'object': obj.name, 'mesh': mesh.name,
            'material': mat.name, 'images': new_images, 'vertices': len(vertices), 'triangles': 8}}


def water(job, action):
    if '/hex_river_overlay_' in job['id']:
        return shimmer(job, action)
    channels = []
    for obj in asset_objects(job):
        if obj.type != 'MESH':
            continue
        if obj.name.startswith('River reflected current'):
            vector = (0, SPEC.current_travel, 0)
        elif obj.name.startswith(('River foam ripple', 'Foam bead')):
            vector = (SPEC.foam_travel, 0, 0)
        elif obj.name.startswith(('Waterfall foam streak', 'Waterfall fine streak')):
            vector = (SPEC.waterfall_travel, 0, 0)
        else:
            continue
        channels.append(animate(action, obj, 'location', vector))
    assert channels, job['id']
    return {'asset': job['id'], 'description': WATER[job['id']], 'targets': [], 'original_parents': {},
            'pivot': None, 'channels': channels, 'added_geometry': None}


def main():
    from tools.asset_pack.verify_ambient_blender import capture, compare
    DOCS.mkdir(parents=True, exist_ok=True)
    path = DOCS / 'authored.json'
    receipts = json.loads(path.read_text()) if path.exists() else {}
    groups = {}
    for job in plan_exports(ROOT, ASSETS):
        groups.setdefault(job['source'], []).append(job)
    for source, jobs in groups.items():
        live = ROOT / source
        backup = ROOT / '.cache/ambient-motion/before' / source
        if source in receipts:
            assert sha(live) == receipts[source]['sha256_after'], source + ': preserve subsequent manual edits before revising'
            print('Retained verified ambient source:', source, flush=True)
            continue
        backup.parent.mkdir(parents=True, exist_ok=True)
        if not backup.exists():
            shutil.copy2(live, backup)
        assert sha(live) == sha(backup), source + ': checkpoint differs'
        bpy.ops.wm.open_mainfile(filepath=str(live))
        bpy.context.scene.frame_set(1)
        before = capture()
        assert not bpy.data.actions.get(SPEC.clip), source
        action = bpy.data.actions.new(SPEC.clip)
        action.use_fake_user = True
        action['loop'] = True
        action['description'] = 'Small localized authored detail; building/tile roots and structural meshes remain static'
        features = [building(job, action) if job['id'].startswith('buildings/') else water(job, action) for job in jobs]
        scene = bpy.context.scene; scene.render.fps = SPEC.fps; scene.render.fps_base = 1
        scene.frame_start, scene.frame_end = SPEC.frames[0], SPEC.frames[-1]
        scene.frame_set(1); bpy.context.view_layer.update()
        protected = preserve_orphans()
        record = {'palette_checkpoint_commit': PALETTE_COMMIT, 'sha256_before': sha(backup), 'clip': SPEC.clip,
                  'loop': True, 'fps': SPEC.fps, 'frames': list(SPEC.frames), 'features': features,
                  'protected_orphan_ids': protected}
        scratch = ROOT / '.cache/ambient-motion/saved' / source
        scratch.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(scratch))
        bpy.ops.wm.open_mainfile(filepath=str(scratch)); scene = bpy.context.scene; scene.frame_set(1)
        compare(before, record)
        record['preservation_verified_after_reload'] = True
        record['sha256_after'] = sha(scratch)
        os.replace(scratch, live)
        receipts[source] = record
        path.write_text(json.dumps(receipts, indent=2) + '\n')
        print('Verified saved ambient source:', source, flush=True)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    main()
