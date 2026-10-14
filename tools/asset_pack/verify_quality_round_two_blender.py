"""Read-only baseline comparison of nonfocal meshes and every embedded kit child.

Requires exact baseline .blend bytes preserved in .cache/quality-round-two/before/.
Those files can also be recovered from revision 5cda624 without rebuilding models.
No source save/export/render; emits a source-bound preservation receipt.
"""
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import bpy

ALLOWED = {
    'bakery': ('Woodland layered bakery porch cap',),
    'weaver': ('Woodland long draped dyed cloth',),
    'magic_academy': ('Academy glowing orb',),
    'town_hall': ('Golden civic bell', 'Bell clapper'),
    'woodcutter_hut': (),
}


def snapshot(path, name):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    bpy.context.view_layer.update()
    rows, kit = {}, {}
    for obj in bpy.data.collections[name].all_objects:
        if obj.type != 'MESH':
            continue
        state = {
            'matrix': [[round(v, 6) for v in row] for row in obj.matrix_world],
            'positions': [[round(c, 6) for c in v.co] for v in obj.data.vertices],
            'faces': [list(p.vertices) for p in obj.data.polygons],
            'uvs': {uv.name: [[round(c, 6) for c in loop.uv] for loop in uv.data] for uv in obj.data.uv_layers},
            'materials': [s.material.name if s.material else None for s in obj.material_slots],
        }
        parent = obj.parent
        while parent:
            if parent.get('kit_asset'):
                kit[obj.name] = state
                break
            parent = parent.parent
        if not obj.get('woodland_detail') and not obj.name.startswith(ALLOWED[name]):
            rows[obj.name] = state
    return rows, kit


def main():
    docs = ROOT / 'docs/quality-round-two'
    baseline = json.loads((docs / 'baseline.json').read_text())
    reports = {}
    for name in ALLOWED:
        source = Path('sources/buildings/' + name + '.blend')
        original = ROOT / '.cache/quality-round-two/before' / source
        assert hashlib.sha256(original.read_bytes()).hexdigest() == baseline[source.as_posix()], source
        before, old_kit = snapshot(original, name)
        after, new_kit = snapshot(ROOT / source, name)
        for key in before:
            assert key in after, (name, 'missing original', key)
            assert before[key] == after[key], (name, 'unexpected original change', key)
        assert old_kit == new_kit, (name, 'embedded kit mutation')
        reports[name] = {
            'unchanged_original_meshes_verified': len(before),
            'unchanged_embedded_kit_children_verified': len(old_kit),
            'intended_focal_mesh_exceptions': ALLOWED[name],
            'source_sha256': hashlib.sha256((ROOT / source).read_bytes()).hexdigest(),
            'scope': 'World transforms, mesh positions/topology, all UV layers and material slot names; 1e-6 coordinate rounding, no shader/pixel/performance judgment',
        }
    (docs / 'preservation.json').write_text(json.dumps(reports, indent=2) + '\n')
    print('Verified preserved nonfocal originals and every embedded kit child for', len(reports), 'sources')


if __name__ == '__main__':
    main()
