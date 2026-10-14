"""Restore only accidentally copied kit landmark data from preserved originals.

One-off corrective authoring for the first source pass, not a rebuilding path.
Restores original shared mesh/UV/slot datablocks for kit children touched by the
initial feature-scale routine; retains all additive detail and role proportions.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import woodland_refinement as w
from woodland_profiles import BUILDINGS


def embedded(obj):
    while obj.parent:
        obj = obj.parent
        if obj.get('kit_source'):
            return True
    return False


def main():
    receipt_path = w.g.ROOT/'docs/whisperwood/authored.json'
    receipt = json.loads(receipt_path.read_text())
    repaired = {}
    for name, profile in BUILDINGS.items():
        path = 'sources/buildings/'+name+'.blend'
        current = w.g.ROOT/path
        if w.digest(current) != receipt['sources'][path]['sha256_after']:
            raise ValueError('Unpreserved change: '+path)
        bpy.ops.wm.open_mainfile(filepath=str(w.g.ROOT/'.cache/whisperwood/before'/path))
        targets = {o.name: o.data.name for o in bpy.data.collections[name].all_objects
                   if o.type == 'MESH' and o.name.startswith(profile['feature']) and embedded(o)}
        if not targets:
            continue
        bpy.ops.wm.open_mainfile(filepath=str(current))
        if bpy.context.scene.get('woodland_reuse_repair'):
            continue
        names = tuple(sorted(set(targets.values())))
        with bpy.data.libraries.load(str(w.g.ROOT/'.cache/whisperwood/before'/path), link=False) as (_, dest):
            dest.meshes = list(names)
        meshes = dict(zip(names, dest.meshes, strict=True))
        for objname, meshname in targets.items():
            bpy.data.objects[objname].data = meshes[meshname]
        directory = w.g.ROOT/'sources/buildings/textures/whisperwood'
        for mesh in meshes.values():
            for mat in mesh.materials:
                if mat:
                    w.grade_material(mat, directory)
        bpy.context.scene['woodland_reuse_repair'] = True
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(current))
        receipt['sources'][path]['sha256_after'] = w.digest(current)
        receipt['sources'][path]['retained_shared_landmarks'] = sorted(targets)
        repaired[path] = sorted(targets)
        receipt_path.write_text(json.dumps(receipt, indent=2)+'\n')
    print('Restored original shared kit data without touching additive details:', {p: len(names) for p, names in repaired.items()})


if __name__ == '__main__':
    main()
