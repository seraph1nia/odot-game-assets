"""Explicit color-channel recovery on preserved landed sources; no geometry build.

Historical material/map bytes supply colors, not whole-source rollback. Current
roughness/normals, emission strengths, geometry, roots, rigging and reuse survive.
"""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import numpy as np
import art_style as style
from woodland_refinement import decode, encode

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/vivid-palette'
SPEC = style.VIVID


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def pixels(image):
    values = np.empty(image.size[0] * image.size[1] * 4, dtype=np.float32)
    image.pixels.foreach_get(values)
    return values.reshape(image.size[1], image.size[0], 4)


def structure():
    """Fingerprint geometry/UVs/reuse/hierarchy/rigs/animation, excluding colors."""
    result = {}
    for obj in bpy.data.objects:
        item = [obj.type, obj.parent.name if obj.parent else None, obj.parent_type,
                obj.parent_bone, list(map(list, obj.matrix_world)),
                sorted(c.name for c in obj.users_collection),
                [(m.name, m.type, getattr(m, 'object', None).name if getattr(m, 'object', None) else None)
                 for m in obj.modifiers]]
        if obj.type == 'MESH':
            mesh = obj.data
            item += [mesh.name, [(tuple(v.co), [(g.group, g.weight) for g in v.groups]) for v in mesh.vertices],
                     [(tuple(p.vertices), p.material_index, p.use_smooth) for p in mesh.polygons],
                     [(uv.name, [tuple(x.uv) for x in uv.data]) for uv in mesh.uv_layers]]
        elif obj.type == 'ARMATURE':
            item += [[(b.name, b.parent.name if b.parent else None, b.use_deform,
                       tuple(b.head_local), tuple(b.tail_local), list(map(list, b.matrix_local))) for b in obj.data.bones]]
        result[obj.name] = hashlib.sha256(repr(item).encode()).hexdigest()
    # Layered actions are serialized explicitly; their channels/keys must not move.
    for action in bpy.data.actions:
        curves = []
        for layer in action.layers:
            for strip in layer.strips:
                for bag in strip.channelbags:
                    curves.extend((f.data_path, f.array_index,
                                   [(tuple(k.co), tuple(k.handle_left), tuple(k.handle_right), k.interpolation) for k in f.keyframe_points])
                                  for f in bag.fcurves)
        result['ACTION:' + action.name] = hashlib.sha256(repr(curves).encode()).hexdigest()
    return result


def used_materials():
    return {slot.material for obj in bpy.data.objects for slot in obj.material_slots if slot.material}


def preserve_orphans():
    """Keep authored unlinked data that Blender otherwise drops on save.

    Unused is not disposable: orphan prototypes/material variants are editable
    source content. Fake users alter persistence only, never scene membership.
    """
    protected = []
    for kind in ('objects', 'meshes', 'materials', 'images', 'actions', 'armatures', 'curves', 'collections'):
        for item in getattr(bpy.data, kind):
            if item.users == 0 and not item.use_fake_user:
                item.use_fake_user = True
                protected.append(kind + '/' + item.name)
    return protected


def data_channels():
    return {m.name + '/' + n.name: sha_bytes(pixels(n.image).tobytes())
            for m in bpy.data.materials if m.use_nodes for n in m.node_tree.nodes
            if n.type == 'TEX_IMAGE' and n.image and n.image.colorspace_settings.name == style.TEXTURES.data_space}


def sha_bytes(data):
    return hashlib.sha256(data).hexdigest()


def originals(path):
    bpy.ops.wm.open_mainfile(filepath=str(path))
    materials, images = {}, {}
    for mat in bpy.data.materials:
        shader = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None) if mat.use_nodes else None
        if shader:
            row = {c: tuple(shader.inputs[c].default_value) for c in ('Base Color', 'Emission Color')}
            materials[mat.name] = row
            materials.setdefault(style.material_name(mat.name), row)
    for image in bpy.data.images:
        if image.colorspace_settings.name == style.TEXTURES.color_space and image.size[0]:
            values = pixels(image)
            images[image.name] = values
            images.setdefault(style.material_name(image.name), values)
    return materials, images


def role_color(name):
    return {
        'forest_leaf_woodland': SPEC.leaf_color,
        'forest_leaf_woodland_tip': SPEC.leaf_tip,
        'moss_woodland': SPEC.moss_color,
        'bark_woodland': SPEC.root_color,
        'stone_woodland_lichen': SPEC.lichen_color,
        'woodland_cloth': SPEC.cloth_color,
        'roof_quality_bakery_ochre': SPEC.porch_ochre,
        'roof_quality_bakery_rim': SPEC.porch_rim,
        'magic_quality_shaded_orb': SPEC.orb_color,
    }.get(style.material_name(name))


def detail(rgb, family):
    """Small smooth material-local chromatic detail, never preview grading."""
    h, w = rgb.shape[:2]
    v, u = np.mgrid[0:h, 0:w].astype(np.float32) / max(h - 1, 1)
    wash = (np.sin(u * 17 + v * 9) + .45 * np.sin(u * 37 - v * 23)) / 1.45
    tint = np.array((.7, .25, -.5)) if family in ('wood', 'roof', 'plaster') else np.array((.5, .4, -.4))
    if family not in ('wood', 'roof', 'plaster', 'leaf', 'moss', 'mushroom', 'ground', 'stone'):
        return rgb
    result = rgb + SPEC.wash_strength * wash[:, :, None] * tint
    if family in ('leaf', 'moss'):
        vein = np.exp(-((u - .5) / .025) ** 2) * np.sin(v * np.pi)
        result += SPEC.leaf_vein_strength * vein[:, :, None] * np.array((.7, 1, -.2))
    elif family == 'wood':
        grain = np.sin(u * 131 + .5 * np.sin(v * 19))
        result += SPEC.grain_strength * grain[:, :, None] * np.array((1, .5, .2))
    return np.clip(result, 0, 1)


def image_map(values, directory):
    key = sha_bytes(values.astype(np.float32).tobytes())[:24]
    name = SPEC.version + '_' + key
    if existing := bpy.data.images.get(name):
        return existing
    h, w = values.shape[:2]
    image = bpy.data.images.new(name, width=w, height=h, alpha=True)
    image.colorspace_settings.name = style.TEXTURES.color_space
    image.pixels.foreach_set(values.astype(np.float32).ravel())
    directory.mkdir(parents=True, exist_ok=True)
    image.filepath_raw = str(directory / (name + '.png'))
    image.file_format = 'PNG'
    image.save()
    image.pack()
    image['vivid_finish'] = SPEC.version
    return image


def apply_material(mat, old_materials, old_images, directory):
    if not mat.use_nodes:
        return None
    shader = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not shader:
        return None  # Retained presentation-only atmosphere; no surface rewrite.
    name = style.material_name(mat.name)
    target = role_color(name)
    old = old_materials.get(mat.name, old_materials.get(name))
    if not target and not old:
        return {'name': mat.name, 'status': 'retained', 'reason': 'Later authored focal material; no historical grey channel to restore'}
    changes = []
    for channel in ('Base Color', 'Emission Color'):
        socket = shader.inputs[channel]
        before = np.array(socket.default_value[:3])
        after = np.array(style.srgb_to_linear(target)) if target else np.array(old[channel][:3])
        # Preserve second-round academy orb body emission strategy/strength.
        socket.default_value = (*after, socket.default_value[3])
        image_record = None
        if socket.is_linked:
            node = socket.links[0].from_node
            if node.type != 'TEX_IMAGE' or not node.image:
                raise ValueError('Unsupported linked color: ' + mat.name)
            image = node.image
            current = pixels(image)
            source_name = image.get('source_image', image.name)
            historical = old_images.get(source_name, old_images.get(style.material_name(source_name)))
            if historical is not None and not target:
                if historical.shape != current.shape:
                    raise ValueError('Historical map dimensions differ: ' + mat.name)
                result = historical.copy()
                method = 'original packed color map with restrained related wash'
            else:
                # Newly painted later maps retain grain/contact/UV variation;
                # replace the material role's RGB ratios, not their spatial field.
                result = current.copy()
                linear = decode(result[:, :, :3])
                result[:, :, :3] = encode(np.clip(linear * (after / np.maximum(before, .00001)), 0, 1))
                method = 'named role recolor retaining current painted spatial field'
            if channel == 'Base Color':
                result[:, :, :3] = detail(result[:, :, :3], style.material_family(name))
            # Current alpha ownership is authoritative, including later edits.
            result[:, :, 3] = current[:, :, 3]
            node.image = image_map(result, directory)
            image_record = {'before': image.name, 'historical': source_name if historical is not None else None,
                            'after': node.image.name, 'method': method,
                            'alpha_preserved': bool(np.array_equal(result[:, :, 3], current[:, :, 3])),
                            'packed': bool(node.image.packed_file)}
        changes.append({'channel': channel, 'linear_before': before.tolist(), 'linear_after': after.tolist(), 'map': image_record})
    mat.diffuse_color = shader.inputs['Base Color'].default_value
    mat['vivid_finish'] = SPEC.version
    return {'name': mat.name, 'status': 'refined', 'basis': 'explicit added role' if target else 'historical material color', 'channels': changes}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--sources', nargs='*')
    parser.add_argument('--repair-serialization', action='store_true',
                        help='Re-author preserved baseline to scratch; replace only exact recorded partial outputs after strict verification')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    if not args.apply:
        parser.error('Requires explicit --apply and preserved baseline bytes')
    baseline = json.loads((DOCS / 'baseline.json').read_text())
    original = json.loads((ROOT / 'docs/whisperwood/baseline.json').read_text())
    receipt = DOCS / 'authored.json'
    authored = json.loads(receipt.read_text()) if receipt.exists() else {}
    paths = sorted({j['source'] for j in baseline['jobs']})
    for path in args.sources or paths:
        if path not in paths:
            raise ValueError('Unknown source: ' + path)
        expected = authored.get(path, {}).get('sha256_after', baseline['files'][path])
        if args.repair_serialization and 'protected_orphan_ids' not in authored.get(path, {}):
            partial = json.loads((ROOT / '.cache/vivid-palette/diagnosis/partial-hashes.json').read_text())
            expected = partial.get(path, expected)
        if sha(ROOT / path) != expected:
            raise ValueError('Unpreserved subsequent source edit: ' + path)
        if path in authored and (not args.repair_serialization or 'protected_orphan_ids' in authored[path]):
            continue
        preserved = ROOT / '.cache/vivid-palette/before' / path
        if sha(preserved) != baseline['files'][path]:
            raise ValueError('Changed preserved baseline: ' + path)
        historical = ROOT / '.cache/whisperwood/before' / path
        if sha(historical) != original['files'][path]['sha256']:
            raise ValueError('Wrong historical color source: ' + path)
        old_materials, old_images = originals(historical)
        bpy.ops.wm.open_mainfile(filepath=str(preserved))
        before, data_before = structure(), data_channels()
        protected = preserve_orphans()
        rows = []
        for mat in sorted(used_materials(), key=lambda m: m.name):
            row = apply_material(mat, old_materials, old_images, ROOT / Path(path).parent / 'textures/vivid')
            if row:
                rows.append(row)
        if structure() != before or data_channels() != data_before:
            raise ValueError('Non-color mutation before save: ' + path)
        protected += preserve_orphans()
        scratch = ROOT / '.cache/vivid-palette/verified' / path
        scratch.parent.mkdir(parents=True, exist_ok=True)
        bpy.ops.wm.save_as_mainfile(filepath=str(scratch))
        bpy.ops.wm.open_mainfile(filepath=str(scratch))
        if structure() != before or data_channels() != data_before:
            raise ValueError('Saved source preservation failed (live source untouched): ' + path)
        os.replace(scratch, ROOT / path)
        authored[path] = {'sha256_before': baseline['files'][path], 'sha256_after': sha(ROOT / path),
                          'historical_sha256': sha(historical), 'materials': rows,
                          'protected_orphan_ids': protected,
                          'structure_sha256': sha_bytes(json.dumps(before, sort_keys=True).encode()),
                          'data_channels_sha256': sha_bytes(json.dumps(data_before, sort_keys=True).encode()),
                          'geometry_uv_hierarchy_reuse_rigs_actions_preserved': True,
                          'roughness_normal_pixels_preserved': True}
        receipt.write_text(json.dumps(authored, indent=2) + '\n')
        print('Recovered source colors, preserved structure:', path, flush=True)


if __name__ == '__main__':
    main()
