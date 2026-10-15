"""Matched fixed-camera crops of actual GLB motion; no .blend saves or shading edits."""
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import bpy
from mathutils import Vector
from tools.asset_catalog import render_blender
from tools.asset_pack import art_style as style
from tools.asset_pack.ambient_contract import receipts


def main():
    aid, folder = sys.argv[sys.argv.index('--') + 1:]
    folder = Path(folder); folder.mkdir(parents=True, exist_ok=True)
    setup = ROOT / '.cache/ambient-motion/setup' / (aid + '.png')
    setup.parent.mkdir(parents=True, exist_ok=True)
    args = sys.argv[:]
    sys.argv = [args[0], '--', str(ROOT / 'exports' / (aid + '.glb')), str(setup)]
    render_blender.main()
    sys.argv = args
    feature = next(f for r in receipts(ROOT).values() for f in r['features'] if f['asset'] == aid)
    target_names = {c['object'] for c in feature['channels']}
    def moves(obj):
        while obj:
            if obj.name in target_names:
                return True
            obj = obj.parent
        return False
    scene = bpy.context.scene
    scene.render.fps = style.AMBIENT.fps
    scene.frame_set(1); bpy.context.view_layer.update()
    meshes = [o for o in scene.objects if o.type == 'MESH' and moves(o)]
    assert meshes, aid
    points = [o.matrix_world @ Vector(p) for o in meshes for p in o.bound_box]
    low = Vector([min(p[i] for p in points) for i in range(3)])
    high = Vector([max(p[i] for p in points) for i in range(3)])
    center = (low + high) / 2
    radius = max((p - center).length for p in points)
    camera = scene.camera
    direction = (style.AMBIENT.low_detail_camera_direction if aid in style.AMBIENT.low_detail_camera_assets
                 else style.AMBIENT.detail_camera_direction)
    camera.location = center + Vector(direction).normalized() * max(radius * 4, 3)
    camera.rotation_euler = (center - camera.location).to_track_quat('-Z', 'Y').to_euler()
    camera.data.ortho_scale = max(.65, radius * 2.8)
    scene.render.resolution_x = scene.render.resolution_y = 360
    camera_config = {'position': list(camera.location), 'rotation': list(camera.rotation_euler),
                     'ortho_scale': camera.data.ortho_scale, 'resolution': [360, 360],
                     'scope': 'One fixed crop of actual exported detail; unchanged neutral lights/materials; not game or artist acceptance'}
    for frame in style.AMBIENT.frames:
        scene.frame_set(frame); bpy.context.view_layer.update()
        scene.render.filepath = str(folder / f'frame-{frame:03}.png')
        bpy.ops.render.render(write_still=True)
    (folder / 'camera.json').write_text(json.dumps(camera_config, indent=2) + '\n')
    print('Matched actual exported ambient poses:', aid, flush=True)


if __name__ == '__main__':
    main()
