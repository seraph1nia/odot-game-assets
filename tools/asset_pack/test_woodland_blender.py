"""Isolated fixtures for source-preserving woodland authoring boundaries."""
import hashlib
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import woodland_refinement as woodland


def graph(mat):
    return repr([(n.bl_idname, n.name, [(s.name, str(s.default_value)) for s in n.inputs
                                      if hasattr(s, 'default_value')]) for n in mat.node_tree.nodes]) + repr([(x.from_node.name, x.from_socket.name, x.to_node.name, x.to_socket.name) for x in mat.node_tree.links])


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


if __name__ == '__main__':
    main()
