"""Matched original/delivered/corrected GLB grids; no source writes or builders."""
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
from hex_ground import BASES

ROOT = g.ROOT


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('stage', choices=('before', 'pr14', 'after'))
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:])
    paths = {'before': '.cache/ai-textures/before/exports',
             'pr14': '.cache/ai-textures-seams/pr14/exports', 'after': 'exports'}
    exports = ROOT / paths[args.stage]
    output = ROOT / 'docs/ai-textures/seams/grids' / args.stage
    output.mkdir(parents=True, exist_ok=True)
    review.OUT = output

    def add(aid, pos=(0, 0, 0), turns=0):
        before = set(bpy.data.objects)
        bpy.ops.import_scene.gltf(filepath=str(exports / (aid + '.glb')))
        for obj in set(bpy.data.objects) - before:
            if obj.parent is None:
                obj.matrix_world = (Matrix.Translation(Vector(pos)) @
                    Matrix.Rotation(turns * 3.141592653589793 / 3, 4, 'Z') @ obj.matrix_world)
        bpy.context.scene.frame_set(1)
        bpy.context.view_layer.update()

    review.add = add
    for family in (*BASES, 'mixed'):
        fixtures = []
        for col in range(3):
            for row in range(2):
                base = BASES[(row + col * 2) % len(BASES)] if family == 'mixed' else family
                pos = (col * style.HEX.spacing_x,
                       row * 2 * style.HEX.half_height + (col % 2) * style.HEX.half_height, 0)
                fixtures.append(('environment/hex_ground_' + base, pos, 0))
        review.render('same_' + family if family != 'mixed' else 'mixed', fixtures, neighbors=True)
    for profile in review.PROFILES:
        profile['revision'] = args.stage
        profile['render_worker_sha256'] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
        profile['shared_review_sha256'] = hashlib.sha256((ROOT / 'tools/asset_pack/ground_review.py').read_bytes()).hexdigest()
        profile['source_style_lights'] = [dict(name=l.name, position=l.position, energy=l.energy, size=l.size, color=l.color) for l in style.LIGHTS]
        profile['world'] = dict(color=style.PREVIEW.world_color, strength=style.PREVIEW.world_strength)
        for asset in profile['assets']:
            asset['glb_sha256'] = hashlib.sha256((exports / (asset['id'] + '.glb')).read_bytes()).hexdigest()
    (output / 'profiles.json').write_text(json.dumps(review.PROFILES, indent=2) + '\n')


if __name__ == '__main__':
    main()
