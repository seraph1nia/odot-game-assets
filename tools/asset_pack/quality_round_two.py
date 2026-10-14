"""Explicit five-source focal edits from the preserved landed Whisperwood baseline.

No rebuilds, kit child changes, global defaults or GUI scene access. Baseline hashes
are checked for the complete selection before writing anything. Use --apply only
with authorized saved-source authoring; reruns refuse already changed sources.
"""
import argparse
import hashlib
import json
import math
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from mathutils import Matrix, Vector
import art_style as style
import geometry as g
import painted_finish as paint

NAMES = ('bakery', 'weaver', 'magic_academy', 'town_hall', 'woodcutter_hut')
TAG = 'whisperwood_quality_round_two'
DOCS = ROOT / 'docs/quality-round-two'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def kit_child(obj):
    while obj.parent:
        obj = obj.parent
        if obj.get('kit_asset'):
            return True
    return False


def quiet_lane(obj, name):
    """Only independent new growth; canonical embedded prototype users are exempt."""
    if kit_child(obj) or obj.get('woodland_part') not in (
            'Woodland shared curved ivy leaf', 'Woodland shared moss cushion'):
        return False
    p = obj.matrix_world.translation
    if name == 'town_hall':
        return p.z > 4 and p.y < .25
    if name in ('weaver', 'magic_academy'):
        return p.z > 2.1 and -.25 < p.x < .65 and p.y < .1
    return False


def edit_bakery(col):
    obj = next(o for o in col.all_objects if o.name.startswith('Woodland layered bakery porch cap'))
    obj.data = obj.data.copy()
    ochre = g.material('roof_quality_bakery_ochre', style.QUALITY_ROUND_TWO['porch_ochre'], .88)
    rim = g.material('roof_quality_bakery_rim', style.QUALITY_ROUND_TWO['porch_rim'], .9)
    obj.data.materials.clear()
    obj.data.materials.append(ochre)
    obj.data.materials.append(rim)
    low, high = min(v.co.z for v in obj.data.vertices), max(v.co.z for v in obj.data.vertices)
    for v in obj.data.vertices:
        t = (v.co.z - low) / (high - low)
        v.co.z += .23 * t
        # Asymmetric rising shelter, not a perfectly flat circular plate.
        v.co.z += .045 * math.sin(v.co.x * 2.8) * t
    obj.data.update()
    for p in obj.data.polygons:
        p.material_index = int(p.center.z < low + .08)
    for mat in (ochre, rim):
        paint.texture_material(mat, ROOT / 'sources/buildings/textures/quality_round_two')
    return ['curved ochre porch crown and cream underside']


def edit_weaver(col):
    cloth = [o for o in col.all_objects if o.name.startswith('Woodland long draped dyed cloth')]
    for index, obj in enumerate(cloth):
        obj.data = obj.data.copy()
        low, high = min(v.co.z for v in obj.data.vertices), max(v.co.z for v in obj.data.vertices)
        center = sum(v.co.x for v in obj.data.vertices) / len(obj.data.vertices)
        for v in obj.data.vertices:
            t = (high - v.co.z) / (high - low)
            v.co.x += (1 if index != 1 else -1) * .13 * t * t
            v.co.y -= .16 * math.sin(t * math.pi * .9)
            v.co.z += .045 * math.sin((v.co.x - center) * 12) * t
        obj.data.update()
        # Narrow side selvedges inherit the authored folded coordinates.
        for chain in ((0, 2, 4), (1, 3, 5)):
            points = [obj.data.vertices[i].co.copy() for i in chain]
            verts = []
            for p in points:
                verts += [tuple(p + Vector((0, -.006, 0))), tuple(p + Vector((.018, -.006, 0)))]
            edge = g.mesh('Quality woven selvedge', verts, [(0, 1, 3, 2), (2, 3, 5, 4)], 'wood_light')
            edge.parent = obj.parent
            edge.matrix_world = obj.matrix_world.copy()
    return ['alternating wind-curved drapes and narrow woven selvedges']


def edit_academy(col):
    orb = next(o for o in col.all_objects if o.name.startswith('Academy glowing orb'))
    # Dedicated body slot: do not change the crystal or any other magic user.
    mat = orb.material_slots[0].material.copy()
    mat.name = 'magic_quality_shaded_orb'
    shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    shader.inputs['Emission Strength'].default_value = style.QUALITY_ROUND_TWO['orb_body_emission']
    orb.data = orb.data.copy()
    orb.data.materials[0] = mat
    points = [orb.matrix_world @ Vector(c) for c in orb.bound_box]
    center = (Vector(tuple(min(p[i] for p in points) for i in range(3))) +
              Vector(tuple(max(p[i] for p in points) for i in range(3)))) / 2
    radius = (max(p.x for p in points) - min(p.x for p in points)) * .52
    for axis in ('Z', 'X'):
        g.torus('Quality scholarly armillary band', center, radius, .019, 'gold', axis, 24)
    return ['shaded purple orb body with narrow brass armillary bands']


def edit_hall(col):
    bell = next(o for o in col.all_objects if o.name.startswith('Golden civic bell'))
    clapper = next(o for o in col.all_objects if o.name.startswith('Bell clapper'))
    for obj in (bell, clapper):
        obj.data = obj.data.copy()
        # Tilt suspended bell very slightly and move forward into open tower bay.
        points = [v.co for v in obj.data.vertices]
        pivot = sum(points, Vector()) / len(points)
        transform = Matrix.Translation((0, -.14, 0)) @ Matrix.Translation(pivot) @ Matrix.Rotation(.09, 4, 'Y') @ Matrix.Translation(-pivot)
        obj.data.transform(transform)
    return ['forward civic bell and lightly tilted ringing silhouette']


def edit_lumber(col):
    # Authored wheel coordinates live under the original role-proportions group.
    group = bpy.data.objects['Woodland role proportions']
    verts, faces = [], []
    for i in range(20):
        angle = i * math.tau / 20
        start = len(verts)
        for y in (-1.045, -1.075):
            for a, r in ((angle - .055, .67), (angle + .07, .67), (angle + .055, .76)):
                verts.append((1.34 + math.sin(a) * r, y, 1.04 + math.cos(a) * r))
        faces.extend(tuple(start + j for j in face) for face in ((0, 2, 1), (3, 4, 5), (0, 1, 4, 3), (1, 2, 5, 4), (2, 0, 3, 5)))
    teeth = g.mesh('Quality single saw tooth ring', verts, faces, 'silver')
    teeth.parent = group
    pulley = g.torus('Quality working hoist pulley', (1.59, .2, 3.36), .12, .029, 'silver_dark', 'Y', 16)
    pulley.parent = group
    return ['single-mesh saw tooth ring and functional hoist pulley']


EDITORS = dict(zip(NAMES, (edit_bakery, edit_weaver, edit_academy, edit_hall, edit_lumber), strict=True))


def refine(col, name, root):
    existing = set(col.all_objects)
    removed = [o.name for o in col.all_objects if quiet_lane(o, name)]
    for obj in list(col.all_objects):
        if obj.name in removed:
            bpy.data.objects.remove(obj, do_unlink=True)
    changes = EDITORS[name](col)
    bpy.context.view_layer.update()
    for obj in set(col.all_objects) - existing:
        if obj.type == 'MESH':
            if obj.parent is None:
                world = obj.matrix_world.copy()
                obj.parent = root
                obj.matrix_parent_inverse = root.matrix_world.inverted()
                obj.matrix_world = world
            paint.project_uv(obj)
            obj[TAG] = True
    return changes, removed


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    baseline = json.loads((DOCS / 'baseline.json').read_text())
    if not args.apply:
        print('Selected focal edits:', ', '.join(NAMES))
        return
    for name in NAMES:
        path = f'sources/buildings/{name}.blend'
        if sha(ROOT / path) != baseline[path]:
            raise ValueError('Changed/unpreserved source: ' + path)
    records = {}
    for name in NAMES:
        path = f'sources/buildings/{name}.blend'
        bpy.ops.wm.open_mainfile(filepath=str(ROOT / path))
        bpy.context.scene.frame_set(1)
        bpy.context.view_layer.update()
        col = bpy.data.collections[name]
        g.target(col)
        g.M = {style.material_name(m.name): m for m in bpy.data.materials}
        root = bpy.data.objects[name + '_root']
        root_matrix = root.matrix_world.copy()
        changes, removed = refine(col, name, root)
        assert root.matrix_world == root_matrix
        bpy.context.scene[TAG] = True
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(ROOT / path))
        records[path] = {'sha256_before': baseline[path], 'sha256_after': sha(ROOT / path),
                         'focal_changes': changes, 'removed_independent_growth': removed,
                         'root_preserved': True, 'kit_children_untouched': True}
        (DOCS / 'authored.json').write_text(json.dumps(records, indent=2) + '\n')
        print('Refined', name, changes, 'removed', len(removed), flush=True)


if __name__ == '__main__':
    main()
