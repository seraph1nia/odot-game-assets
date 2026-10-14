"""Executable Blender fixtures for scoped focal edits and shared growth ownership."""
import sys
from pathlib import Path
from unittest.mock import patch

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from mathutils import Matrix
import geometry as g
import painted_finish as paint
from tools.asset_pack import quality_round_two as q


def fixture():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    g.palette()
    col = g.collection('fixture')
    g.target(col)
    return col


def world_faces(objects):
    return sorted(tuple(sorted(tuple(round(v, 5) for v in obj.matrix_world @ obj.data.vertices[i].co)
                              for i in poly.vertices)) for obj in objects for poly in obj.data.polygons)


def follows_root(objects, root):
    bpy.context.view_layer.update()
    before = {obj: obj.matrix_world.copy() for obj in objects}
    original = root.matrix_world.copy()
    delta = Matrix.Translation((1.7, -.8, .6)) @ Matrix.Rotation(.7, 4, 'Z')
    root.matrix_world = delta @ original
    bpy.context.view_layer.update()
    for obj in objects:
        parent = obj.parent
        while parent and parent != root:
            parent = parent.parent
        assert parent == root, obj.name
        expected = delta @ before[obj]
        assert all(abs(obj.matrix_world[i][j] - expected[i][j]) < 1e-5
                   for i in range(4) for j in range(4)), obj.name
    root.matrix_world = original
    bpy.context.view_layer.update()


def main():
    for name in q.NAMES:
        col = fixture()
        root = g.empty(name + '_root')
        kit = g.empty('kit root')
        kit.parent = root
        kit['kit_asset'] = 'roof_tile'
        originals = []
        for part in ('Woodland shared curved ivy leaf', 'Woodland shared moss cushion'):
            prototype = g.mesh('growth', [(0, 0, 0), (.1, 0, 0), (0, .2, 0)], [(0, 1, 2)], 'wood')
            paint.project_uv(prototype)
            for i in range(5):
                obj = prototype if i == 0 else prototype.copy()
                if i:
                    col.objects.link(obj)
                obj['woodland_part'] = part
                obj.parent = kit if i == 3 else root
                obj.location = (i * 1.0, .5 if i == 4 else -.3, 4.8)
                obj.rotation_euler = (.1 * i, .2, -.15 * i)
                obj.scale = (1 + i * .1, .8, 1.2)
                originals.append(obj)
        bpy.context.view_layer.update()
        removed = [o.name for o in originals if q.quiet_lane(o, name)]
        survivors = [o for o in originals if o.name not in removed]
        before = world_faces(survivors)
        data = {o: o.data for o in survivors}
        uvs = {o: [tuple(loop.uv) for loop in o.data.uv_layers.active.data] for o in survivors}
        with patch.dict(q.EDITORS, {name: lambda collection: ['fixture focal edit']}):
            changes, actual_removed = q.refine(col, name, root)
        assert changes == ['fixture focal edit']
        assert set(actual_removed) == set(removed)
        assert set(o for o in col.objects if o.type == 'MESH') == set(survivors)
        assert world_faces(survivors) == before
        for obj in survivors:
            assert obj.data == data[obj]
            assert [tuple(loop.uv) for loop in obj.data.uv_layers.active.data] == uvs[obj]
            assert obj.data.materials[0] == g.M['wood']
        for part in ('Woodland shared curved ivy leaf', 'Woodland shared moss cushion'):
            assert len({o.data for o in survivors if o.get('woodland_part') == part}) == 1
        assert all(not q.quiet_lane(o, name) for o in survivors if q.kit_child(o))

    col = fixture()
    root = g.empty('weaver_root')
    parent = g.empty('cloth support')
    parent.parent = root
    cloth = g.mesh('Woodland long draped dyed cloth', [(-.2, 0, 1), (.2, 0, 1), (-.2, 0, .5), (.2, 0, .5), (-.2, 0, 0), (.2, 0, 0), (0, 0, -.05)], [(0, 1, 3, 2), (2, 3, 5, 6, 4)], 'blue')
    cloth.parent = parent
    original = [v.co.copy() for v in cloth.data.vertices]
    q.refine(col, 'weaver', root)
    assert cloth.data.vertices[0].co == original[0]
    assert cloth.data.vertices[2].co.y < original[2].y
    assert cloth.data.vertices[4].co.x > original[4].x
    edges = [o for o in col.objects if o.name.startswith('Quality woven selvedge')]
    assert len(edges) == 2 and all(o.parent == parent for o in edges)
    assert cloth.parent == parent
    follows_root(edges, root)

    col = fixture()
    root = g.empty('magic_academy_root', (2, -1, .4))
    root.rotation_euler = (.1, .2, .3)
    root.scale = (1.2, .9, 1.1)
    orb = g.ico('Academy glowing orb', (0, 0, 1), (.4,) * 3, 'magic', 1, 0)
    orb.parent = root
    crystal = g.ico('retained crystal', (0, 0, 3), (.2,) * 3, 'magic', 1, 0)
    crystal.parent = root
    emission = next(n for n in crystal.data.materials[0].node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Emission Strength'].default_value
    bpy.context.view_layer.update()
    created = {}
    torus = g.torus

    def capture(*args, **kwargs):
        obj = torus(*args, **kwargs)
        bpy.context.view_layer.update()
        created[obj] = [obj.matrix_world @ v.co for v in obj.data.vertices]
        return obj

    with patch.object(g, 'torus', capture):
        q.refine(col, 'magic_academy', root)
    bpy.context.view_layer.update()
    assert orb.data.materials[0] != crystal.data.materials[0]
    assert next(n for n in orb.data.materials[0].node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Emission Strength'].default_value < emission
    assert next(n for n in crystal.data.materials[0].node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Emission Strength'].default_value == emission
    assert len(created) == 2
    for obj, points in created.items():
        assert obj.parent == root and obj.get(q.TAG)
        assert all((obj.matrix_world @ v.co - p).length < 1e-5
                   for v, p in zip(obj.data.vertices, points, strict=True))
        assert obj.data.uv_layers.active
    follows_root(created, root)

    col = fixture()
    root = g.empty('woodcutter_hut_root')
    group = g.empty('Woodland role proportions')
    group.parent = root
    matrix = root.matrix_world.copy()
    q.refine(col, 'woodcutter_hut', root)
    teeth = bpy.data.objects['Quality single saw tooth ring']
    pulley = bpy.data.objects['Quality working hoist pulley']
    assert len(teeth.data.polygons) == 100
    assert teeth.parent == group and pulley.parent == group and root.matrix_world == matrix
    assert all(v.co.z > .27 for v in teeth.data.vertices)
    follows_root([teeth, pulley], root)
    print('Quality round two: shared leaf/moss instances across five paths, selective thinning, kit exclusion, planted folds, scoped orb emission, preserved world geometry and root motion passed')


if __name__ == '__main__':
    main()
