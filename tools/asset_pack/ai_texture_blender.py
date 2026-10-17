"""Scoped texture-only POC on saved sources; run through asset_pack.worker.

Never calls a builder. Baseline snapshots are mandatory before material edits.
"""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import numpy as np

from tools.asset_pack.hex_ground import IDS
from tools.asset_pack.vivid_refinement import structure, preserve_orphans
import art_style as style
import painted_finish
from tools.asset_pack.encoded_images import image_proof

ROOT = Path(__file__).resolve().parents[2]
CACHE = ROOT / '.cache/ai-textures'
ALL_IDS = (*IDS, 'buildings/archery_range')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def signature():
    """Whole-source geometry/UV/animation, slots, root metadata and physical state."""
    return {
        'structure': structure(),
        'slots': {o.name: [(s.link, s.material.name if s.material else None)
                           for s in o.material_slots] for o in bpy.data.objects},
        'extras': {o.name: json.loads(json.dumps(
            {k: o[k].to_list() if hasattr(o[k], 'to_list') else o[k] for k in o.keys()},
            default=str)) for o in bpy.data.objects},
        'materials': {m.name: {
            'diffuse': list(m.diffuse_color),
            'surface_render_method': m.surface_render_method,
            'backface_culling': m.use_backface_culling,
            'defaults': {s.name: list(s.default_value) if hasattr(s.default_value, '__len__')
                         else s.default_value for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'
                         for s in n.inputs if hasattr(s, 'default_value')},
        } for m in bpy.data.materials if m.use_nodes},
    }


def audit(asset_id, *, baseline_cache=False):
    path = (CACHE / 'before/sources' if baseline_cache else ROOT / 'sources') / (asset_id + '.blend')
    expected = next(row for row in json.loads((ROOT / 'docs/ai-textures/baseline.json').read_text())['assets']
                    if row['id'] == asset_id)['sources']['sha256']
    assert sha(path) == expected, 'Refusing to overwrite the original audit with changed source bytes'
    bpy.ops.wm.open_mainfile(filepath=str(path))
    bpy.context.view_layer.update()
    objects = list(bpy.data.collections[asset_id.split('/')[-1]].all_objects)
    materials = {s.material for o in objects for s in o.material_slots if s.material}
    report = {'id': asset_id, 'source_sha256': sha(path), 'signature': signature(),
              'objects': [], 'materials': {}, 'images': {}}
    for o in objects:
        if o.type != 'MESH':
            continue
        report['objects'].append({'name': o.name, 'mesh': o.data.name,
            'vertices': len(o.data.vertices), 'dimensions': list(o.dimensions),
            'slots': [(s.link, s.material.name if s.material else None) for s in o.material_slots],
            'uvs': [{'name': uv.name, 'loops': len(uv.data),
                     'range': [np.min([tuple(x.uv) for x in uv.data], axis=0).tolist(),
                               np.max([tuple(x.uv) for x in uv.data], axis=0).tolist()]}
                    for uv in o.data.uv_layers]})
    for m in sorted(materials, key=lambda m: m.name):
        shader = next((n for n in m.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if m.use_nodes else None
        if not shader:
            continue
        report['materials'][m.name] = {s.name: [(l.from_node.name, l.from_node.type)
            for l in s.links] for s in shader.inputs if s.is_linked}
        for n in m.node_tree.nodes:
            if n.type == 'TEX_IMAGE' and n.image:
                im = n.image
                report['images'][im.name] = {'size': list(im.size),
                    'space': im.colorspace_settings.name, 'packed': bool(im.packed_file),
                    'proof': image_proof(im)}
    return report


def pixels(image):
    values = np.empty(image.size[0] * image.size[1] * 4, dtype=np.float32)
    image.pixels.foreach_get(values)
    return values.reshape(image.size[1], image.size[0], 4)


def decode(rgb):
    return np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)


def sample(image, size):
    values = pixels(image)[:, :, :3]
    y = np.linspace(0, values.shape[0] - 1, size).astype(int)
    x = np.linspace(0, values.shape[1] - 1, size).astype(int)
    return values[y[:, None], x[None, :]]


def managed_image(name, values, directory):
    """Content-keyed cache with ownership and packed/external coherence checks."""
    key = hashlib.sha256(values.astype(np.float32).tobytes()).hexdigest()
    existing = bpy.data.images.get(name)
    if existing:
        assert not existing.is_dirty, 'Unsaved edits in owned image buffer'
        assert existing.get('ai_texture_owner') == style.AI_TEXTURE.version
        assert existing.get('ai_texture_values_sha256') == key, 'Image-name collision'
        assert image_proof(existing)['packed_sha256'] == sha(directory / (name + '.png')), 'Stale packed/external map'
        return existing
    image = painted_finish.image_map(name, values, directory)
    image['ai_texture_owner'] = style.AI_TEXTURE.version
    image['ai_texture_values_sha256'] = key
    assert image_proof(image)['packed_sha256'] == sha(directory / (name + '.png'))
    return image


def ground_color(family, original, supplied):
    size = len(original)
    result = original * (1 - style.AI_TEXTURE.ground_blend) + supplied * style.AI_TEXTURE.ground_blend
    v, u = np.mgrid[0:size, 0:size].astype(np.float32) / (size - 1)
    if family in ('moss', 'grass', 'dirt', 'leaf_litter', 'pine_duff'):
        x, y = (u - .5) * 2 * style.HEX.radius, (v - .5) * 2 * style.HEX.radius
        distance = np.minimum.reduce([style.HEX.half_height + x * np.sin(e * np.pi / 3)
                                      - y * np.cos(e * np.pi / 3) for e in range(6)])
        keep = np.clip(distance / style.AI_TEXTURE.ground_edge_fade, 0, 1)
        keep = keep * keep * (3 - 2 * keep)
        edge = np.array(style.srgb_to_linear(style.AI_TEXTURE.ground_edge_color))
        result = edge * (1 - keep[:, :, None]) + result * keep[:, :, None]
    elif family in ('path', 'river'):
        # Exact symmetric cross-profile at BOTH endpoints. The supplied border
        # matching is not symmetric across U, so retain authored connector paint.
        keep = np.clip((np.minimum(v, 1-v) - .11) * 6, 0, 1)
        if family == 'river':
            # Supplied water/banks use the same transverse split; never planar UV.
            # Keep banks and lip authored: large AI foliage clumps stretch on turns.
            cross = abs(u - .5)
            water_edge = style.HEX.water_width / (2 * style.GROUND.width('river'))
            keep *= np.clip((water_edge - cross) / .035, 0, 1)
        result = original * (1 - keep[:, :, None]) + result * keep[:, :, None]
    return result


# Audited effective material users, not the archive's unverified candidate names.
ARCHERY = {
    'wood': ('wood_warm_planks', (.34, 0, .46, 1)),
    'wood.003': ('wood_warm_planks', (.34, 0, .46, 1)),
    'wood_light': ('wood_warm_planks', (.34, 0, .46, 1)),
    'wood_light.001': ('wood_warm_planks', (.34, 0, .46, 1)),
    'wood_edge': ('wood_horizontal_planks', (.05, .71, .48, .84)),
    'wood_dark': ('wood_dark_aged', (.35, 0, .49, 1)),
    'wood_dark.001': ('wood_dark_aged', (.35, 0, .49, 1)),
    'wood_dark.002': ('wood_dark_aged', (.35, 0, .49, 1)),
    'roof_blue': ('roof_blue_shingles', (.08, .77, .18, .91)),
    'roof_blue_light': ('roof_blue_shingles', (.08, .77, .18, .91)),
    'roof_blue_dark': ('roof_blue_shingles', (.08, .77, .18, .91)),
    'wall': ('plaster_warm', (0, 0, 1, 1)),
    'wall_light': ('stone_mossy_masonry', (.28, .29, .48, .47)),
    'wall_light.001': ('stone_mossy_masonry', (.28, .29, .48, .47)),
    'stone_light': ('stone_mossy_masonry', (.28, .29, .48, .47)),
    'blue': ('cloth_cobalt_weave', (0, 0, 1, 1)),
    **{name: ('ivy_moss_foliage', (0, 0, 1, 1)) for name in (
        'forest_leaf_woodland', 'forest_leaf_woodland.001',
        'forest_leaf_woodland_tip', 'forest_leaf_woodland_tip.001',
        'moss_woodland', 'moss_woodland.001', 'leaf.001', 'leaf_dark.001', 'leaf_light.001')},
}


def archery_color(family, original, supplied):
    if family == 'ivy_moss_foliage':
        # Existing individual leaves/cushions already have silhouette and root-tip
        # color. Borrow only restrained paint variation, never ivy-on-every-leaf.
        lum = supplied.mean(axis=-1)
        return np.clip(original * (1 + .20 * (lum / max(float(lum.mean()), .001) - 1))[:, :, None], 0, 1)
    # Retain authored shade relationships and role hue, adding related surface paint.
    supplied *= np.clip(original.mean(axis=(0, 1)) / np.maximum(supplied.mean(axis=(0, 1)), .001), .5, 2)
    return np.clip(original * (1 - style.AI_TEXTURE.building_blend) + supplied * style.AI_TEXTURE.building_blend, 0, 1)


def bind_archery(mat, source_path):
    family, crop = ARCHERY[mat.name]
    directory = ROOT / 'sources/buildings/textures/ai_archery/managed'
    supplied_path = directory.parent / 'input/textures' / (family + '_basecolor.png')
    shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    socket = shader.inputs['Base Color']
    if socket.is_linked and mat.get('ai_original_color_image') != '':
        node = socket.links[0].from_node
        assert node.type == 'TEX_IMAGE' and node.image
        old_name = mat.get('ai_original_color_image', node.image.name)
        original = bpy.data.images[old_name]
        original.use_fake_user = True
        mat['ai_original_color_image'] = old_name
        size = original.size[0]
        old_rgb = decode(sample(original, size))
    else:
        size = style.TEXTURES.size
        old_rgb = np.broadcast_to(np.array(socket.default_value[:3]), (size, size, 3)).copy()
        node = mat.node_tree.nodes.get('AI POC Base Color') or mat.node_tree.nodes.new('ShaderNodeTexImage')
        node.name = 'AI POC Base Color'
        mat.node_tree.links.new(node.outputs['Color'], socket)
        mat['ai_original_color_image'] = ''
    supplied = bpy.data.images.load(str(supplied_path), check_existing=False)
    supplied.colorspace_settings.name = style.TEXTURES.color_space
    raw = pixels(supplied)[:, :, :3]
    x0, y0, x1, y1 = crop
    rows = np.linspace(y0 * (raw.shape[0]-1), y1 * (raw.shape[0]-1), size).astype(int)
    cols = np.linspace(x0 * (raw.shape[1]-1), x1 * (raw.shape[1]-1), size).astype(int)
    rgb = raw[rows[:, None], cols[None, :]]
    if family == 'wood_horizontal_planks':
        rgb = rgb.transpose(1, 0, 2)  # Existing timber length is V, input grain U.
    values = archery_color(family, old_rgb, decode(rgb))
    bpy.data.images.remove(supplied)
    key = hashlib.sha256(values.astype(np.float32).tobytes()).hexdigest()[:24]
    name = style.AI_TEXTURE.version + '_' + family + '_' + key + '_base_color'
    image = managed_image(name, values, directory)
    image['input_sha256'] = sha(supplied_path)
    image.filepath = bpy.path.relpath(str(directory / (name + '.png')), start=str(source_path.parent))
    node.image = image
    mat['ai_texture_profile'] = style.AI_TEXTURE.version
    return {'material': mat.name, 'family': family, 'crop_uv': crop,
            'input_sha256': sha(supplied_path), 'image': image.name,
            'packed_sha256': image_proof(image)['packed_sha256'],
            'retained_channels': ['Roughness', 'Normal', 'Metallic', 'Emission', 'Alpha']}


def apply(asset_id):
    path = ROOT / 'sources' / (asset_id + '.blend')
    baseline = json.loads((CACHE / 'audit' / (asset_id.replace('/', '_') + '.json')).read_text())
    if sha(path) != baseline['source_sha256']:
        receipt = CACHE / 'applied' / (asset_id.replace('/', '_') + '.json')
        if receipt.is_file():
            applied = json.loads(receipt.read_text())
            assert applied['id'] == asset_id, 'Applied receipt asset mismatch'
            expected = applied['source_sha256']
        else:
            applied = json.loads((ROOT / 'docs/ai-textures/validation.json').read_text())['assets'][asset_id]
            expected = applied['source_after_sha256']
        assert sha(path) == expected, 'Source changed since audited baseline or last application; refusing to overwrite manual edits'
    bpy.ops.wm.open_mainfile(filepath=str(path))
    bpy.context.view_layer.update()
    assert json.loads(json.dumps(signature())) == baseline['signature'], 'Source geometry/UV/slots/physical state changed since audit'
    before = signature()
    objects = bpy.data.collections[asset_id.split('/')[-1]].all_objects
    materials = {s.material for o in objects for s in o.material_slots if s.material}
    changed = []
    for mat in sorted(materials, key=lambda m: m.name):
        if asset_id == 'buildings/archery_range':
            if mat.name in ARCHERY:
                changed.append(bind_archery(mat, path))
            continue
        if not mat.name.startswith('floor_'):
            continue
        family = mat.name.removeprefix('floor_')
        supplied_path = ROOT / 'sources/environment/textures/ai_ground/input/textures' / (family + '_basecolor.png')
        shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
        node = shader.inputs['Base Color'].links[0].from_node
        assert node.type == 'TEX_IMAGE' and node.image
        old_name = mat.get('ai_original_color_image', node.image.name)
        original = bpy.data.images[old_name]
        original.use_fake_user = True
        mat['ai_original_color_image'] = old_name
        supplied = bpy.data.images.load(str(supplied_path), check_existing=False)
        supplied.colorspace_settings.name = style.TEXTURES.color_space
        size = original.size[0]
        supplied_rgb = sample(supplied, size)
        if family == 'foundation':
            # One plausible shallow masonry course, not a square atlas squeezed
            # onto a 2.55m by .36m sidewall. UVs remain exactly authored.
            raw = pixels(supplied)[:, :, :3]
            rows = np.linspace(.43 * (len(raw)-1), .57 * (len(raw)-1), size).astype(int)
            cols = np.linspace(0, raw.shape[1]-1, size).astype(int)
            supplied_rgb = raw[rows[:, None], cols[None, :]]
        values = ground_color(family, decode(sample(original, size)), decode(supplied_rgb))
        bpy.data.images.remove(supplied)
        key = hashlib.sha256(values.astype(np.float32).tobytes()).hexdigest()[:24]
        name = style.AI_TEXTURE.version + '_' + family + '_' + key + '_base_color'
        directory = ROOT / 'sources/environment/textures/ai_ground/managed'
        image = managed_image(name, values, directory)
        image['input_sha256'] = sha(supplied_path)
        image.filepath = bpy.path.relpath(str(directory / (name + '.png')), start=str(path.parent))
        node.image = image
        mat['ai_texture_profile'] = style.AI_TEXTURE.version
        changed.append({'material': mat.name, 'input_sha256': sha(supplied_path),
                        'image': image.name, 'packed_sha256': image_proof(image)['packed_sha256'],
                        'retained_channels': ['Roughness', 'Normal']})
    assert changed, 'No scoped materials found'
    assert signature() == before
    preserve_orphans()
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    bpy.ops.wm.open_mainfile(filepath=str(path))
    bpy.context.view_layer.update()
    assert signature() == before, 'Round-trip source preservation failed'
    result = {'id': asset_id, 'source_sha256': sha(path), 'materials': changed,
              'preserved_geometry_uv_slots_animation_physical_state': True}
    out = CACHE / 'applied'
    out.mkdir(parents=True, exist_ok=True)
    (out / (asset_id.replace('/', '_') + '.json')).write_text(json.dumps(result, indent=2) + '\n')
    print('Texture-only saved:', asset_id, flush=True)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('operation', choices=['audit', 'audit-baseline', 'apply', 'idempotence'])
    parser.add_argument('ids', nargs='*', choices=ALL_IDS)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    out = CACHE / 'audit'
    out.mkdir(parents=True, exist_ok=True)
    for aid in args.ids or ALL_IDS:
        if args.operation in ('apply', 'idempotence'):
            if args.operation == 'idempotence':
                from tools.asset_pack.verify_ambient_blender import capture
                bpy.ops.wm.open_mainfile(filepath=str(ROOT / 'sources' / (aid + '.blend')))
                before = capture()
                apply(aid)
                assert capture() == before, 'Repeated application changed source semantics or grew datablocks'
                print('Idempotent:', aid, flush=True)
            else:
                apply(aid)
            continue
        result = audit(aid, baseline_cache=args.operation == 'audit-baseline')
        (out / (aid.replace('/', '_') + '.json')).write_text(json.dumps(result, indent=2) + '\n')
        print(aid, 'objects:', len(result['objects']), 'materials:', ', '.join(result['materials']), flush=True)


if __name__ == '__main__':
    main()
