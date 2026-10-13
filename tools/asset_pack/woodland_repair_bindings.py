"""Correct only newly authored bow/crossbow wraps after actual image review."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import woodland_refinement as w


def main():
    receipt_path = w.g.ROOT/'docs/whisperwood/authored.json'
    receipt = json.loads(receipt_path.read_text())
    count = 0
    for source in ('sources/props/bow.blend', 'sources/props/crossbow.blend',
                   'sources/characters/archer.blend', 'sources/characters/evil_ranged_unit.blend'):
        file = w.g.ROOT/source
        record = receipt['sources'][source]
        assert w.digest(file) == record['sha256_after'], source
        bpy.ops.wm.open_mainfile(filepath=str(file))
        before = w.armature_contract()
        changed = []
        for root in list(bpy.data.objects):
            name = root.name.split('.')[0]
            if root.type != 'EMPTY' or name not in ('bow', 'crossbow') or root.get('woodland_binding_fit'):
                continue
            frame = w.binding_frame(root, name)
            wraps = [o for o in root.children_recursive if o.get('woodland_detail') and o.get('woodland_part') == w.PREFIX+'equipment worn binding']
            assert len(wraps) == 3, (source, name, len(wraps))
            root_matrix = root.matrix_world.copy()
            for obj in wraps:
                assert obj.parent == root and obj.matrix_basis == w.Matrix.Identity(4)
                obj.data = obj.data.copy()
                obj.data.transform(frame)
            assert root.matrix_world == root_matrix
            root['woodland_binding_fit'] = 1
            changed.append(name)
        assert w.armature_contract() == before, source
        if changed:
            bpy.context.preferences.filepaths.save_version = 0
            bpy.ops.wm.save_as_mainfile(filepath=str(file))
            record['sha256_after'] = w.digest(file)
            record['binding_fit_review'] = 'Extra wraps fitted to original geometric grip; original geometry/pivots/scale/rig retained'
            receipt_path.write_text(json.dumps(receipt, indent=2)+'\n')
            count += len(changed)
    print('Corrected newly added wraps, retaining authored attachment interfaces:', count)


if __name__ == '__main__':
    main()
