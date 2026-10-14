"""Isolated fixtures for source-preserving woodland authoring boundaries."""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import woodland_refinement as woodland


def graph(mat):
    return repr([(n.bl_idname, n.name, [(s.name, str(s.default_value)) for s in n.inputs
                                      if hasattr(s, 'default_value')]) for n in mat.node_tree.nodes]) + repr([(x.from_node.name, x.from_socket.name, x.to_node.name, x.to_socket.name) for x in mat.node_tree.links])


def ownership_contract():
    from tools.asset_catalog.blender_selection import load_asset

    receipts = json.loads((woodland.g.ROOT/'docs/whisperwood/authored.json').read_text())['sources']
    expected = {'knight': 12, 'archer': 9, 'berserker': 16, 'evil_berserker_unit': 16,
                'evil_mage_unit': 13, 'evil_melee_unit': 14, 'evil_ranged_unit': 10, 'mage': 13}
    for name, count in expected.items():
        path = 'sources/characters/'+name+'.blend'
        source = woodland.g.ROOT/path
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        job = {'id': 'characters/'+name, 'source': path, 'collection': None, 'object': None}
        selected = set(load_asset(job, woodland.g.ROOT))
        assert set(woodland.asset_objects(job)) == selected
        existing = {o for o in bpy.data.objects if not o.get('woodland_detail')}
        added = [o for o in selected if o not in existing and o.type == 'MESH']
        assert len(added) == receipts[path]['added_mesh_objects'] == count, name
        assert hashlib.sha256(source.read_bytes()).hexdigest() == before == receipts[path]['sha256_after']

    bpy.ops.wm.read_factory_settings(use_empty=True)
    unit = bpy.data.collections.new('unit')
    plain = bpy.data.collections.new('plain')
    equipment = bpy.data.collections.new('EQUIPMENT')
    nested = bpy.data.collections.new('nested')
    equipment.children.link(nested)
    rig = bpy.data.objects.new('rig', bpy.data.armatures.new('rig'))
    unit.objects.link(rig)
    body = bpy.data.objects.new('body', bpy.data.meshes.new('body'))
    unit.objects.link(body)
    existing = set(bpy.data.objects)
    gear = bpy.data.objects.new('gear', bpy.data.meshes.new('gear'))
    nested.objects.link(gear)
    unit.objects.link(gear)
    extra = bpy.data.objects.new('extra gear', bpy.data.meshes.new('extra gear'))
    nested.objects.link(extra)
    plain.objects.link(body)
    root = bpy.data.objects.new('root', None)
    body.parent = root
    job = {'id': 'unit', 'source': 'fixture.blend', 'collection': 'unit', 'object': None}
    owned = set(woodland.asset_objects(job))
    assert owned == {rig, body, gear, extra}
    assert len([o for o in owned if o not in existing and o.type == 'MESH']) == 2
    assert woodland.asset_objects(dict(job, collection='plain')) == [body]
    assert set(woodland.asset_objects(dict(job, collection=None, object='root'))) == {root, body}
    print('Woodland ownership: eight saved character receipts include equipment; nested/shared equipment counted once; plain collections and root assets exclude unrelated equipment; source bytes unchanged')


def library_ownership_contract():
    receipts = json.loads((woodland.g.ROOT/'docs/whisperwood/authored.json').read_text())['sources']
    subparts = json.loads((woodland.g.ROOT/'docs/whisperwood/subparts.json').read_text())
    jobs = woodland.plan_exports(woodland.g.ROOT)
    expected = {'sources/props/shared_village_kit.blend': 242,
                'sources/environment/shared_forest_kit.blend': 360,
                'sources/environment/shared_enchanted_kit.blend': 58}
    for path, count in expected.items():
        source = woodland.g.ROOT/path
        before = hashlib.sha256(source.read_bytes()).hexdigest()
        bpy.ops.wm.open_mainfile(filepath=str(source))
        selected_jobs = [job for job in jobs if job['source'] == path]
        assert {job['id'] for job in selected_jobs} == set(receipts[path]['ids'])
        selected = set()
        for job in selected_jobs:
            objects = woodland.asset_objects(job)
            details = [o for o in objects if o.type == 'MESH' and o.get('woodland_detail')]
            assert len(details) == subparts[job['id']]['added_detail_objects'], job['id']
            selected.update(objects)
        added = [o for o in selected if o.type == 'MESH' and o.get('woodland_detail')]
        assert len(added) == receipts[path]['added_mesh_objects'] == count, path
        assert hashlib.sha256(source.read_bytes()).hexdigest() == before == receipts[path]['sha256_after']
    print('Woodland library ownership: village 242, forest 360, enchanted 58 distinct canonical added meshes; subpart and authoring receipts agree; source bytes unchanged')


def main():
    source = woodland.g.ROOT/'sources/buildings/bakery.blend'
    before = hashlib.sha256(source.read_bytes()).hexdigest()
    bpy.ops.wm.open_mainfile(filepath=str(source))
    mat = bpy.data.materials['Chimney smoke volume']
    original = graph(mat)
    assert woodland.retained_presentation_volume(mat)
    assert not woodland.grade_material(mat, woodland.g.ROOT/'.cache/whisperwood/fixtures')
    assert graph(mat) == original
    # A matching material name and valid volume node are insufficient: an
    # unsupported surface connection must fail closed rather than be waived.
    unknown = mat.copy()
    diffuse = unknown.node_tree.nodes.new('ShaderNodeBsdfDiffuse')
    output = next(n for n in unknown.node_tree.nodes if n.type == 'OUTPUT_MATERIAL')
    unknown.node_tree.links.new(diffuse.outputs['BSDF'], output.inputs['Surface'])
    assert not woodland.retained_presentation_volume(unknown)
    try:
        woodland.grade_material(unknown, woodland.g.ROOT/'.cache/whisperwood/fixtures')
    except ValueError as error:
        assert 'Unsupported surface' in str(error)
    else:
        raise AssertionError('Unknown surface graph was silently retained')
    # A disconnected Principled node cannot disguise an unsupported active graph.
    unknown.node_tree.nodes.new('ShaderNodeBsdfPrincipled')
    try:
        woodland.grade_material(unknown, woodland.g.ROOT/'.cache/whisperwood/fixtures')
    except ValueError as error:
        assert 'Unsupported surface output' in str(error)
    else:
        raise AssertionError('Inactive Principled node bypassed the guard')
    # A volume assigned to an export collection is not presentation-only.
    export_user = bpy.data.objects.new('volume export fixture', bpy.data.meshes.new('volume fixture'))
    bpy.data.collections['bakery'].objects.link(export_user)
    export_user.data.materials.append(mat)
    assert not woodland.retained_presentation_volume(mat)
    assert hashlib.sha256(source.read_bytes()).hexdigest() == before
    print('Woodland guard: real PRINCIPLED_VOLUME/Volume output retained unchanged; unknown surface, inactive Principled and exported volume rejected; source bytes unchanged')
    ownership_contract()
    library_ownership_contract()


if __name__ == '__main__':
    main()
