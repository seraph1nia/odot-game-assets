"""Independent texture-only successor audit of saved sources and serialized GLBs.

Normalizes ONLY declared Base Color replacements. All other source content and
portable triangle corners, normals, UVs, data maps and animation samples must match.
"""
import hashlib
import json
import sys
from collections import Counter, defaultdict
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy

from tools.asset_catalog.metadata import read_glb
from tools.asset_catalog.runtime_glb import read, accessor
from tools.asset_pack.ambient_contract import sha
from tools.asset_pack.encoded_images import image_proof, png_proof
from tools.asset_pack.hex_ground import IDS
from tools.asset_pack.verify_ambient_blender import capture
from tools.asset_pack.verify_runtime_blender import serialized_samples, compare_samples, material_key, samples

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / '.cache/ai-textures'


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True).encode()).hexdigest()


def capture_source():
    result = capture()
    result['material_render_properties'] = {m.name: [m.surface_render_method, m.use_backface_culling,
        m.use_backface_culling_shadow] for m in bpy.data.materials}
    result['animation_bindings'] = {o.name: {
        'action': o.animation_data.action.name if o.animation_data.action else None,
        'slot': o.animation_data.action_slot.identifier if o.animation_data.action_slot else None,
        'nla': [(track.name, [(s.name, s.action.name if s.action else None,
                              s.frame_start, s.frame_end, s.blend_type, s.extrapolation)
                             for s in track.strips]) for track in o.animation_data.nla_tracks],
    } for o in bpy.data.objects if o.animation_data}
    return result


def source_preservation(aid, applied):
    before_path = CACHE / 'before/sources' / (aid + '.blend')
    bpy.ops.wm.open_mainfile(filepath=str(before_path))
    before = capture_source()
    bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'sources' / (aid + '.blend')))
    # Prove the live owned Base Color image before normalizing it for comparison.
    new_images = set()
    for change in applied['materials']:
        mat = bpy.data.materials[change['material']]
        shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        node = shader.inputs['Base Color'].links[0].from_node
        assert node.type == 'TEX_IMAGE' and node.image.name == change['image']
        image = node.image
        assert image.colorspace_settings.name == 'sRGB' and image.packed_file
        assert image_proof(image)['packed_sha256'] == change['packed_sha256']
        assert sha(Path(bpy.path.abspath(image.filepath))) == change['packed_sha256']
        new_images.add(image.name)
        old_name = mat['ai_original_color_image']
        if old_name:
            node.image = bpy.data.images[old_name]
        else:
            assert node.name == 'AI POC Base Color'
            mat.node_tree.nodes.remove(node)
        assert set(k for k in mat.keys() if k.startswith('ai_')) == {'ai_original_color_image', 'ai_texture_profile'}
        del mat['ai_original_color_image']
        del mat['ai_texture_profile']
    actual = capture_source()
    protected = ('structure', 'transforms', 'settings', 'collections', 'materials',
                 'material_render_properties', 'animation_bindings')
    for field in protected:
        assert before[field] == actual[field], (aid, 'protected source field', field)
    for kind in before['ids']:
        assert set(actual['ids'][kind]) == set(before['ids'][kind]) | (new_images if kind == 'images' else set()), (aid, kind)
    for name, proof in before['images'].items():
        assert actual['images'][name] == proof, (aid, 'original packed image changed', name)
    return {'geometry_uv_slots_hierarchy_actions_equal': True,
            'all_other_nodes_defaults_render_settings_equal': True,
            'all_original_packed_images_exact': True,
            'signature_before': digest({k: before[k] for k in protected}),
            'signature_after_normalized': digest({k: actual[k] for k in protected}),
            'original_image_proofs': before['images'],
            'original_image_count': len(before['images']), 'new_image_count': len(new_images)}


def encoded(doc, binary, image):
    assert 'uri' not in image and image.get('mimeType') == 'image/png'
    view = doc['bufferViews'][image['bufferView']]
    start = view.get('byteOffset', 0)
    return binary[start:start + view['byteLength']]


def normalized_materials(doc, binary):
    def walk(value):
        if isinstance(value, dict):
            result = {}
            for k, v in value.items():
                if k in ('baseColorTexture', 'baseColorFactor', 'name') or k.startswith('ai_'):
                    continue
                if k.endswith('Texture') and isinstance(v, dict) and 'index' in v:
                    texture = doc['textures'][v['index']]
                    raw = encoded(doc, binary, doc['images'][texture['source']])
                    result[k] = {**{x: y for x, y in v.items() if x != 'index'},
                                 'encoded_image_sha256': hashlib.sha256(raw).hexdigest(),
                                 'sampler': doc.get('samplers', [])[texture['sampler']] if 'sampler' in texture else None}
                else:
                    result[k] = walk(v)
            return result
        return value
    return {material_key(m): digest(walk(m)) for m in doc['materials']}


def geometry_samples(path, keys, *, new_uv_materials=()):
    data, counts, zeros = serialized_samples(path)
    result, totals, empty = defaultdict(list), Counter(), Counter()
    for (material, textured), faces in data.items():
        key = (keys[material], True)
        if material in new_uv_materials:
            # Only newly exported UVs already checked against the saved source
            # below may be absent from the historical untextured GLB.
            faces = [tuple((pos, normal, None) for pos, normal, uv in face) for face in faces]
        result[key].extend(faces)
        totals[key] += counts[(material, textured)]
        empty[key] += zeros[(material, textured)]
    return result, totals, empty


def export_preservation(aid):
    old_path = CACHE / 'before/exports' / (aid + '.glb')
    new_path = ROOT / 'exports' / (aid + '.glb')
    old, old_bin = read(old_path)
    new, new_bin = read(new_path)
    old_keys, new_keys = normalized_materials(old, old_bin), normalized_materials(new, new_bin)
    assert set(old_keys.values()) == set(new_keys.values()), (aid, 'non-color shader/channel contract')
    newly_textured = []
    added_uv_checks = {}
    if aid == 'buildings/archery_range':
        # The old blue pennant/banner used a scalar color, so glTF omitted its
        # already-authored source UVs. New cloth must export precisely those UVs.
        mat = next(m for m in new['materials'] if m['name'] == 'blue')
        raw_key = material_key(mat)
        assert 'baseColorTexture' in mat['pbrMetallicRoughness']
        assert 'baseColorTexture' not in next(m for m in old['materials'] if m['name'] == 'blue')['pbrMetallicRoughness']
        bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'sources' / (aid + '.blend')))
        objects = [o for o in bpy.data.collections['archery_range'].all_objects
                   if o.type == 'MESH' and any(s.material and s.material.name == 'blue' for s in o.material_slots)]
        assert {s.material.name for o in objects for s in o.material_slots} == {'blue'}
        source = samples(objects, {'blue': (raw_key, True)})
        target = serialized_samples(new_path)
        key = (raw_key, True)
        target = ({key: target[0][key]}, Counter({key: target[1][key]}), Counter({key: target[2][key]}))
        added_uv_checks['blue'] = compare_samples(source, target)
        newly_textured.append(raw_key)
    geometry = compare_samples(geometry_samples(old_path, old_keys),
                               geometry_samples(new_path, new_keys, new_uv_materials=newly_textured))
    assert len(old.get('animations', [])) == len(new.get('animations', []))
    for a, b in zip(old.get('animations', []), new.get('animations', []), strict=True):
        assert a['name'] == b['name'] and a.get('extras') == b.get('extras')
        assert len(a['channels']) == len(b['channels']) and len(a['samplers']) == len(b['samplers'])
        for x, y in zip(a['channels'], b['channels'], strict=True):
            assert x['target']['path'] == y['target']['path']
            assert old['nodes'][x['target']['node']]['name'] == new['nodes'][y['target']['node']]['name']
        for x, y in zip(a['samplers'], b['samplers'], strict=True):
            assert x.get('interpolation') == y.get('interpolation')
            for key in ('input', 'output'):
                assert accessor(old, old_bin, x[key]) == accessor(new, new_bin, y[key])
    images = [png_proof(encoded(new, new_bin, image)) for image in new.get('images', [])]
    return {'all_serialized_triangle_corners_normals_uvs_equal': geometry,
            'newly_exported_existing_source_uvs': added_uv_checks,
            'non_color_materials_and_embedded_data_maps_equal': True,
            'exact_animation_targets_samples_loop_extras': True,
            'before': read_glb(old_path), 'after': read_glb(new_path),
            'embedded_images': len(images),
            'decoded_rgba8_bytes_no_mips': sum(p['dimensions'][0] * p['dimensions'][1] * 4 for p in images)}


def main():
    report = {'baseline_revision': '133c7cdeb368cada408d1c95c9414e08488371a9',
              'runtime': bpy.app.version_string, 'assets': {}}
    for aid in (*IDS, 'buildings/archery_range'):
        applied = json.loads((CACHE / 'applied' / (aid.replace('/', '_') + '.json')).read_text())
        assert applied['source_sha256'] == sha(ROOT / 'sources' / (aid + '.blend'))
        report['assets'][aid] = {'source_before_sha256': sha(CACHE / 'before/sources' / (aid + '.blend')),
            'source_after_sha256': applied['source_sha256'],
            'source_preservation': source_preservation(aid, applied),
            'export_preservation': export_preservation(aid), 'materials': applied['materials']}
        print('Exact texture-only source/export successor verified:', aid, flush=True)
    report['verifier_sha256'] = sha(__file__)
    out = ROOT / 'docs/ai-textures/validation.json'
    out.write_text(json.dumps(report, indent=2) + '\n')


if __name__ == '__main__':
    main()
