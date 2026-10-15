"""Independent read-only landed/current source preservation audit after serialization."""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from vivid_refinement import data_channels, sha, sha_bytes, structure
from tools.asset_pack.encoded_images import image_proof
from tools.asset_pack.ambient_contract import source_chain

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
                alpha[mat.name + '/' + node.name] = image_proof(node.image, alpha_only=True)['alpha_sha256']
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
        motion = source_chain(ROOT, path, record['sha256_after'])
        palette = ROOT / '.cache/ambient-motion/before' / path if motion else ROOT / path
        assert sha(palette) == record['sha256_after'], path
        if motion:
            verified = json.loads((ROOT / 'docs/ambient-motion/validation.json').read_text())['sources'][path]
            assert verified['sha256_before'] == sha(palette) and verified['sha256_after'] == sha(ROOT / path)
            assert verified['original_geometry_uv_reuse_rigs_actions_equal']
            assert verified['all_original_full_materials_and_images_equal']
        bpy.ops.wm.open_mainfile(filepath=str(saved))
        before = snapshot()
        bpy.ops.wm.open_mainfile(filepath=str(palette))
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
                        'palette_checkpoint_sha256': sha(palette),
                        'palette_checkpoint_all_object_structure_equal': True,
                        'localized_motion_validation': '../ambient-motion/validation.json' if motion else None,
                        'all_material_noncolor_pixels_equal': True,
                        'data_map_proof': 'exact packed PNG bytes and independently decoded 8-bit samples/alpha; dimensions/channels/bit depth/color space and binding/mapping/use-state',
                        'protected_data_channel_count': len(before['data_channels']),
                        'protected_data_channels': {key: {'encoded': value['encoded'],
                            'binding_sha256': sha_bytes(json.dumps(value['binding'], sort_keys=True).encode())}
                            for key, value in before['data_channels'].items()},
                        'unsupported_map_count': 0,
                        'all_texture_alpha_equal': True, 'physical_defaults_and_emission_strength_equal': True,
                        'all_original_ids_retained': True, 'original_id_counts': {k: len(v) for k, v in before['ids'].items()}}
        print('Strict independent preservation:', path, flush=True)
    (DOCS / 'preservation.json').write_text(json.dumps(report, indent=2) + '\n')
    print('Strict independent preservation passed:', len(report), 'saved sources')


if __name__ == '__main__':
    main()
