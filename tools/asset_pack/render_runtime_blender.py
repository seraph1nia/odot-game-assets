"""Matched neutral CPU exported-asset pairs; one unchanged camera/light setup."""
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
import bpy
from tools.asset_catalog import render_blender
from tools.asset_pack.ambient_contract import sha


def main():
    aid = sys.argv[sys.argv.index('--')+1]
    folder = ROOT/'docs/runtime-optimization/evidence'/aid
    folder.mkdir(parents=True,exist_ok=True)
    before = ROOT/'.cache/runtime-optimization/before/exports'/(aid+'.glb')
    after = ROOT/'exports'/(aid+'.glb')
    sys.argv = [sys.argv[0],'--',str(before),str(folder/'before.png')]
    render_blender.main()
    scene = bpy.context.scene
    config = {'position':list(scene.camera.location),'rotation':list(scene.camera.rotation_euler),
        'ortho_scale':scene.camera.data.ortho_scale, 'resolution':[480,480], 'frame':1,
        'engine':scene.render.engine,'samples':scene.cycles.samples,
        'view_transform':scene.view_settings.view_transform,'look':scene.view_settings.look,
        'exposure':scene.view_settings.exposure,'glow':False,
        'lights':'Same three neutral SUN lights and world, untouched between imports',
        'scope':'Standalone neutral CPU GLBs at identical projection; 192/96 canvas diagnostics, not measured game occupied pixels/FPS'}
    # Preserve exactly the original camera, lights, world and color management.
    for obj in list(scene.objects):
        if obj.type not in ('CAMERA','LIGHT'):
            bpy.data.objects.remove(obj,do_unlink=True)
    bpy.ops.import_scene.gltf(filepath=str(after))
    scene.frame_set(1); scene.render.filepath = str(folder/'after.png')
    bpy.ops.render.render(write_still=True)
    record = {'asset':aid,'before_glb_sha256':sha(before),'after_glb_sha256':sha(after),
              'blender':bpy.app.version_string,'blender_build':bpy.app.build_hash.decode(),
              'renderer_sha256':sha(Path(__file__)),
              'neutral_setup_sha256':sha(ROOT/'tools/asset_catalog/render_blender.py'),
              'camera':config, 'images':{}}
    for stage in ('before','after'):
        for size in (192,96):
            subprocess.run(['magick',str(folder/(stage+'.png')),'-resize',f'{size}x{size}',
                            str(folder/(stage+f'-{size}.png'))],check=True)
        for suffix in ('','-192','-96'):
            image = folder/(stage+suffix+'.png')
            record['images'][image.relative_to(ROOT).as_posix()] = sha(image)
    (folder/'render.json').write_text(json.dumps(record,indent=2)+'\n')
    print('Matched fixed-camera actual GLB pair:',aid,flush=True)


if __name__ == '__main__': main()
