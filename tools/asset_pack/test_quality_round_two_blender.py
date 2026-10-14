"""Executable Blender fixtures for scoped focal edits and static growth ownership."""
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
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


def main():
    col = fixture()
    root = g.empty('kit root')
    root['kit_asset'] = 'roof_tile'
    originals = []
    for i in range(4):
        obj = g.mesh('leaf', [(0, 0, 0), (.1, 0, 0), (0, .2, 0)], [(0, 1, 2)], 'wood')
        obj['woodland_part'] = 'Woodland shared curved ivy leaf'
        obj.location = (i * .2, -.3, 2.8)
        paint.project_uv(obj)
        if i == 3:
            obj.parent = root
        originals.append(obj)
    bpy.context.view_layer.update()
    before = world_faces(originals)
    protected_data = originals[-1].data
    assert not q.quiet_lane(originals[-1], 'weaver')
    assert q.quiet_lane(originals[0], 'weaver')
    result = q.consolidate_growth(col)
    meshes = [o for o in col.objects if o.type == 'MESH']
    assert result == {'Woodland shared curved ivy leaf': 3}
    assert len(meshes) == 2
    assert originals[-1].data == protected_data
    assert world_faces(meshes) == before
    assert all(o.data.uv_layers.active and len(o.data.uv_layers.active.data) == len(o.data.loops) for o in meshes)
    assert all(o.data.materials[0] == g.M['wood'] for o in meshes)

    col = fixture()
    parent = g.empty('cloth support')
    cloth = g.mesh('Woodland long draped dyed cloth', [(-.2, 0, 1), (.2, 0, 1), (-.2, 0, .5), (.2, 0, .5), (-.2, 0, 0), (.2, 0, 0), (0, 0, -.05)], [(0, 1, 3, 2), (2, 3, 5, 6, 4)], 'blue')
    cloth.parent = parent
    original = [v.co.copy() for v in cloth.data.vertices]
    q.edit_weaver(col)
    assert cloth.data.vertices[0].co == original[0]  # suspension stays planted
    assert cloth.data.vertices[2].co.y < original[2].y
    assert cloth.data.vertices[4].co.x > original[4].x
    assert len([o for o in col.objects if o.name.startswith('Quality woven selvedge')]) == 2
    assert cloth.parent == parent

    col = fixture()
    orb = g.ico('Academy glowing orb', (0, 0, 1), (.4,) * 3, 'magic', 1, 0)
    crystal = g.ico('retained crystal', (0, 0, 3), (.2,) * 3, 'magic', 1, 0)
    emission = next(n for n in crystal.data.materials[0].node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Emission Strength'].default_value
    bpy.context.view_layer.update()
    q.edit_academy(col)
    assert orb.data.materials[0] != crystal.data.materials[0]
    assert next(n for n in orb.data.materials[0].node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Emission Strength'].default_value < emission
    assert next(n for n in crystal.data.materials[0].node_tree.nodes if n.type == 'BSDF_PRINCIPLED').inputs['Emission Strength'].default_value == emission
    assert len([o for o in col.objects if o.name.startswith('Quality scholarly armillary band')]) == 2

    col = fixture()
    root = g.empty('Woodland role proportions')
    matrix = root.matrix_world.copy()
    q.edit_lumber(col)
    teeth = bpy.data.objects['Quality single saw tooth ring']
    assert len(teeth.data.polygons) == 100
    assert teeth.parent == root and root.matrix_world == matrix
    assert all(v.co.z > .27 for v in teeth.data.vertices)
    print('Quality round two: geometry/UV/material preservation, kit ownership, planted folds, scoped orb emission and efficient saw fixtures passed')


if __name__ == '__main__':
    main()
