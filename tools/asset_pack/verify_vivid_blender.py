"""Independent read-only landed/current source preservation audit after serialization."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from vivid_refinement import data_channels, pixels, sha, sha_bytes, structure

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/vivid-palette'


def snapshot():
    alpha, physical = {}, {}
    for mat in bpy.data.materials:
        if not mat.use_nodes:
            continue
        for node in mat.node_tree.nodes:
            if node.type == 'BSDF_PRINCIPLED':
                for name in ('Roughness', 'Metallic', 'Emission Strength', 'Alpha'):
                    physical[mat.name + '/' + node.name + '/' + name] = float(node.inputs[name].default_value)
            elif node.type == 'TEX_IMAGE' and node.image and node.image.size[0]:
                alpha[mat.name + '/' + node.name] = sha_bytes(pixels(node.image)[:, :, 3].tobytes())
    return {'structure': structure(), 'data_channels': data_channels(), 'texture_alpha': alpha,
            'physical_defaults': physical,
            'ids': {kind: sorted(item.name for item in getattr(bpy.data, kind))
                    for kind in ('objects', 'meshes', 'materials', 'images', 'actions', 'armatures', 'curves', 'collections')}}


def main():
    baseline = json.loads((DOCS / 'baseline.json').read_text())
    authored = json.loads((DOCS / 'authored.json').read_text())
    report = {}
    for path, record in authored.items():
        saved = ROOT / '.cache/vivid-palette/before' / path
        assert sha(saved) == baseline['files'][path]
        assert sha(ROOT / path) == record['sha256_after']
        bpy.ops.wm.open_mainfile(filepath=str(saved))
        before = snapshot()
        bpy.ops.wm.open_mainfile(filepath=str(ROOT / path))
        after = snapshot()
        for field in ('structure', 'data_channels', 'texture_alpha', 'physical_defaults'):
            if before[field] != after[field]:
                diff = {k: {'expected': before[field].get(k), 'observed': after[field].get(k)}
                        for k in before[field].keys() | after[field].keys() if before[field].get(k) != after[field].get(k)}
                raise ValueError(path + '/' + field + ': ' + json.dumps(diff))
        for kind, names in before['ids'].items():
            missing = sorted(set(names) - set(after['ids'][kind]))
            if missing:
                raise ValueError(path + '/missing/' + kind + ': ' + ', '.join(missing))
        report[path] = {'source_sha256': sha(ROOT / path), 'baseline_sha256': sha(saved),
                        'all_object_structure_equal': True, 'all_material_noncolor_pixels_equal': True,
                        'all_texture_alpha_equal': True, 'physical_defaults_and_emission_strength_equal': True,
                        'all_original_ids_retained': True, 'original_id_counts': {k: len(v) for k, v in before['ids'].items()}}
        print('Strict independent preservation:', path, flush=True)
    (DOCS / 'preservation.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Strict independent preservation passed:', len(report), 'saved sources')


if __name__ == '__main__':
    main()
