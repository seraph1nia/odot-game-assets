"""Read-only current selected subpart inventory; no rebuild or source save."""
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from mathutils import Vector
from tools.asset_catalog.blender_selection import load_asset
from tools.asset_catalog.export_sources import plan_exports


def main():
    records = {}
    for job in plan_exports(ROOT):
        objects = load_asset(job, ROOT)
        meshes = [o for o in objects if o.type == 'MESH']
        details = [o for o in meshes if o.get('woodland_detail')]
        points = [o.matrix_world @ Vector(c) for o in meshes for c in o.bound_box]
        low = [min(p[i] for p in points) for i in range(3)]
        high = [max(p[i] for p in points) for i in range(3)]
        records[job['id']] = {
            'selected_mesh_objects': len(meshes),
            'added_detail_objects': len(details),
            'detail_parts': dict(sorted(Counter(o.get('woodland_part', o.name.split('.')[0]) for o in details).items())),
            'original_objects_retained': len(meshes)-len(details),
            'source_selected_bounds_saved_pose': {'low': low, 'high': high},
            'bone_names': [b.name for o in objects if o.type == 'ARMATURE' for b in o.data.bones],
        }
    (ROOT/'docs/whisperwood/subparts.json').write_text(json.dumps(records, indent=2)+'\n')
    print('Read-only selected subpart inventory:', len(records))


if __name__ == '__main__':
    main()
