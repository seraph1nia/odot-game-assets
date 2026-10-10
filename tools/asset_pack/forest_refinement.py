"""Explicit, source-preserving dreamlike forest authoring recipe.

Not a builder: requires a preserved baseline inventory and --apply. Only the
existing forest libraries and their actual material-dependent tile copies are
edited. Meshes, UVs, slots, normals, modifiers and interfaces are retained.
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
import art_style as style
import geometry as g
import painted_finish as paint

FOCALS = ('hex_glowing_mushrooms', 'hex_crystal_grove', 'hex_lantern_bridge')
# Existing peripheral ground plants regrouped at contacts, not new prototypes.
PLACEMENTS = {
    'hex_glowing_mushrooms': {'leaf_clump_instance.015': (.54, -.92, 0),
                              'leaf_clump_instance.020': (-.78, -.78, 0)},
    'hex_crystal_grove': {'leaf_clump_instance.023': (.72, -.86, 0),
                         'leaf_clump_instance.028': (-.43, -.67, 0)},
    'hex_lantern_bridge': {'leaf_clump_instance.014': (-1.44, -.88, 0),
                          'leaf_clump_instance.004': (1.47, -.55, 0)},
}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def mesh_contract():
    """Guard mesh/UV/smooth/slot identity, not custom normals or modifier settings."""
    meshes = {}
    for mesh in bpy.data.meshes:
        data = ([tuple(v.co) for v in mesh.vertices],
                [(tuple(p.vertices), p.material_index, p.use_smooth) for p in mesh.polygons],
                [[tuple(x.uv) for x in uv.data] for uv in mesh.uv_layers],
                [(a.name, a.domain, a.data_type) for a in mesh.color_attributes])
        meshes[mesh.name] = hashlib.sha256(repr(data).encode()).hexdigest()
    slots = {obj.name: (obj.data.name, [(s.link, s.material.name if s.material else None)
                                     for s in obj.material_slots],
                       [(m.name, m.type) for m in obj.modifiers])
             for obj in bpy.data.objects if obj.type == 'MESH'}
    return {'meshes': meshes, 'slots': slots}


def grade_receiver(mat, directory):
    if not (mat.get('receiving_ground') or mat.name.startswith('Painted receiving ground ')) or mat.get('forest_finish') == style.FOREST.version:
        return False
    shader = next(n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED')
    node = shader.inputs['Base Color'].links[0].from_node
    image = node.image
    if not image.name.startswith('painted_') or not image.packed_file:
        raise ValueError('Refusing unknown/manual ground channel: ' + mat.name)
    pixels = np.empty(image.size[0] * image.size[1] * 4, dtype=np.float32)
    image.pixels.foreach_get(pixels)
    rgb = pixels.reshape(image.size[1], image.size[0], 4)[:, :, :3]
    linear = np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)
    ratio = np.array(style.srgb_to_linear(style.FOREST.ground_to)) / style.srgb_to_linear(style.FOREST.ground_from)
    # Grade the preserved actual map, including hand-authored/contact variation;
    # never recompute placement shadows or bake the preview lights.
    node.image = paint.image_map(style.FOREST.version + '_' + image.name,
                                np.clip(linear * ratio, 0, 1), directory)
    mat['forest_finish'] = style.FOREST.version
    return True


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', required=True)
    parser.add_argument('--apply', action='store_true')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    baseline = json.loads((g.ROOT / args.baseline).read_text())
    sources = [p for p in baseline['files'] if p.endswith('.blend') and
               (Path(p).name in ('shared_forest_kit.blend', 'shared_enchanted_kit.blend') or
                Path(p).stem.startswith('hex_') and Path(p).stem not in
                ('hex_meadow_building', 'hex_meadow_character') and not
                Path(p).stem.startswith(('hex_ground_', 'hex_path_', 'hex_river_overlay_')))]
    # Validate the entire source closure before making the first change.
    for path in sources:
        if digest(g.ROOT / path) != baseline['files'][path]['sha256']:
            raise ValueError('Refusing non-baseline source: ' + path)
    from tools.asset_catalog.export_sources import plan_exports
    jobs = [j for j in plan_exports(g.ROOT) if j['source'] in sources]
    changes = {}
    affected = []
    directory = g.ROOT / 'sources/environment/textures'
    for path in sources:
        bpy.ops.wm.open_mainfile(filepath=str(g.ROOT / path))
        used = {s.material for obj in bpy.data.objects if obj.type == 'MESH'
                for s in obj.material_slots if s.material}
        targets = {m for m in used if style.material_name(m.name) in style.FOREST_MATERIALS}
        receivers = {m for m in used if m.get('receiving_ground') or
                     m.name.startswith('Painted receiving ground ')}
        if not targets and not receivers:
            continue
        for job in jobs:
            if job['source'] != path:
                continue
            col = bpy.data.collections.get(job['collection'] or Path(job['id']).name)
            objs = col.all_objects if col else []
            if any(s.material in targets | receivers for o in objs if o.type == 'MESH' for s in o.material_slots):
                affected.append(job['id'])
        if not args.apply:
            changes[path] = {'materials': sorted(m.name for m in targets | receivers)}
            continue
        before = mesh_contract()
        changed = [m.name for m in sorted(targets, key=lambda m: m.name) if paint.forest_material(m, directory)]
        changed += [m.name for m in sorted(receivers, key=lambda m: m.name) if grade_receiver(m, directory)]
        placements = {}
        for name, pos in PLACEMENTS.get(Path(path).stem, {}).items():
            obj = bpy.data.objects[name]
            if obj.get('kit_asset') != 'forest_leaf_clump':
                raise ValueError('Unexpected focal plant identity: ' + name)
            placements[name] = {'before': tuple(obj.location), 'after': pos,
                                'scale_before': tuple(obj.scale)}
            obj.location = pos
            obj.scale *= .72
            placements[name]['scale_after'] = tuple(obj.scale)
        assert mesh_contract() == before, 'Mesh/UV/slot/modifier contract altered: ' + path
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(g.ROOT / path))
        changes[path] = {'materials': changed, 'placements': placements,
                         'source_before': baseline['files'][path]['sha256'],
                         'source_after': digest(g.ROOT / path), 'mesh_contract': before}
    output = g.ROOT / 'docs/dreamlike-forest' / ('authored.json' if args.apply else 'scope.json')
    output.write_text(json.dumps({'profile': style.FOREST.version, 'ids': sorted(set(affected)),
                                  'sources': changes}, indent=2) + '\n')
    print('Named material closure:', len(changes), 'sources;', len(set(affected)), 'exports;', output)


if __name__ == '__main__':
    main()
