"""Supply only absent UVs to existing users of newly portable surface maps.

Preserves all existing authored UV layers, coordinates, topology, normals,
material slots, transforms and skeletons. No geometry regeneration.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import woodland_refinement as w


def geometry_contract():
    return {m.name: hashlib.sha256(repr(([(tuple(v.co)) for v in m.vertices],
                                        [(tuple(p.vertices), p.material_index, p.use_smooth) for p in m.polygons])).encode()).hexdigest()
            for m in bpy.data.meshes}


def main():
    path = w.g.ROOT/'docs/whisperwood/authored.json'
    receipt = json.loads(path.read_text())
    changed = {}
    for source, record in receipt['sources'].items():
        file = w.g.ROOT/source
        if w.digest(file) != record['sha256_after']:
            raise ValueError('Unpreserved source: '+source)
        bpy.ops.wm.open_mainfile(filepath=str(file))
        before = geometry_contract()
        original_uvs = {m.name: [[tuple(p.uv) for p in uv.data] for uv in m.uv_layers]
                        for m in bpy.data.meshes if m.uv_layers}
        missing = []
        for obj in bpy.data.objects:
            if obj.type != 'MESH' or obj.data.uv_layers:
                continue
            shaders = [next((n for n in s.material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
                       for s in obj.material_slots if s.material and s.material.use_nodes]
            if any(n and n.inputs['Base Color'].is_linked for n in shaders):
                w.paint.project_uv(obj)
                missing.append(obj.name)
        assert geometry_contract() == before, source+' geometry changed'
        for name, uvs in original_uvs.items():
            assert [[tuple(p.uv) for p in uv.data] for uv in bpy.data.meshes[name].uv_layers] == uvs, source+' manual UVs changed'
        if missing:
            bpy.context.preferences.filepaths.save_version = 0
            bpy.ops.wm.save_as_mainfile(filepath=str(file))
            record['sha256_after'] = w.digest(file)
            record['supplied_missing_uvs'] = missing
            changed[source] = len(missing)
            path.write_text(json.dumps(receipt, indent=2)+'\n')
    print('Added only missing portable UVs, preserving all previous UVs/geometry:', changed)


if __name__ == '__main__':
    main()
