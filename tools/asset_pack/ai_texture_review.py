"""Matched portable GLB comparisons, reusing detailed-ground review/studio helpers."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from mathutils import Matrix, Vector

import art_style as style
import geometry as g
import ground_review as review
import hex_ground

ROOT = g.ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('revision', choices=['before', 'after'])
    parser.add_argument('ids', nargs='*')
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    exports = ROOT / ('.cache/ai-textures/before/exports' if args.revision == 'before' else 'exports')
    output = ROOT / 'docs/ai-textures/renders' / args.revision
    output.mkdir(parents=True, exist_ok=True)
    review.OUT = output

    def add(asset_id, pos=(0, 0, 0), turns=0):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(exports / (asset_id + '.glb')))
        objects = set(bpy.data.objects) - before
        for obj in objects:
            if obj.parent is None:
                obj.matrix_world = Matrix.Translation(Vector(pos)) @ Matrix.Rotation(turns * 3.141592653589793 / 3, 4, 'Z') @ obj.matrix_world
        bpy.context.scene.frame_set(1)
        bpy.context.view_layer.update()
        return objects

    review.add = add
    ids = args.ids or [*hex_ground.IDS, 'buildings/archery_range']
    for aid in ids:
        if aid == 'neighbors':
            for family, prefix in (('path', 'hex_path_'), ('river', 'hex_river_overlay_')):
                for piece, edges in hex_ground.PIECES.items():
                    fixtures = [('environment/hex_ground_moss', (0, 0, 0), 0),
                                ('environment/' + prefix + piece, (0, 0, 0), 0)]
                    for edge in edges:
                        n = hex_ground.normal(edge)
                        center = (2 * style.HEX.half_height * n[0], 2 * style.HEX.half_height * n[1], 0)
                        fixtures += [('environment/hex_ground_moss', center, 0),
                                     ('environment/' + prefix + 'end', center, (edge+3) % 6)]
                    review.render(f'neighbors_{family}_{piece}', fixtures, neighbors=True)
            continue
        if aid == 'mixed':
            a = style.HEX.half_height
            # Two connected chains on neighboring columns, all five floor families.
            fixtures = []
            for col in range(2):
                for row in range(-1, 2):
                    pos = (col * style.HEX.spacing_x, row * 2 * a + col * a, 0)
                    family = hex_ground.BASES[(row + 1 + col * 3) % 5]
                    prefix = 'hex_path_' if col else 'hex_river_overlay_'
                    piece = 'straight' if row == 0 else 'end'
                    turns = 0 if row == -1 else 3 if row == 1 else 0
                    fixtures.extend([('environment/hex_ground_' + family, pos, 0),
                                     ('environment/' + prefix + piece, pos, turns)])
            review.render('mixed', fixtures, neighbors=True)
            continue
        name = aid.replace('/', '_')
        fixtures = [(aid, (0, 0, 0), 0)]
        if 'hex_path_' in aid or 'hex_river_overlay_' in aid:
            fixtures.insert(0, ('environment/hex_ground_grass', (0, 0, 0), 0))
        review.render(name, fixtures, occupied=aid.startswith('buildings/'))
        review.render(name + '_close', fixtures, close=True, occupied=aid.startswith('buildings/'))
    # Correct baseline hashes: original helper records current root exports by default.
    for profile in review.PROFILES:
        profile['revision'] = args.revision
        for item in profile['assets']:
            item['glb_sha256'] = hashlib.sha256((exports / (item['id'] + '.glb')).read_bytes()).hexdigest()
        profile['baseline_revision'] = '133c7cdeb368cada408d1c95c9414e08488371a9'
        profile['render_worker_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        profile['shared_review_sha256'] = hashlib.sha256((ROOT / 'tools/asset_pack/ground_review.py').read_bytes()).hexdigest()
        profile['source_style_lights'] = [{'name': light.name, 'position': light.position,
                                         'energy': light.energy, 'size': light.size, 'color': light.color}
                                        for light in style.LIGHTS]
        profile['world'] = {'color': style.PREVIEW.world_color, 'strength': style.PREVIEW.world_strength}
        profile['renderer_device'] = 'CPU; portable evidence, not actual Godot/GPU acceptance'
    path = output / 'profiles.json'
    previous = json.loads(path.read_text()) if path.exists() else []
    updated = {p['name']: p for p in previous + review.PROFILES}
    path.write_text(json.dumps(list(updated.values()), indent=2) + '\n')


if __name__ == '__main__':
    main()
