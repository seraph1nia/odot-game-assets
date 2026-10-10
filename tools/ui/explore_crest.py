"""Two original, approval-only watch seals. Run with the existing Blender worker."""
import math
import sys
from pathlib import Path

import bpy
from mathutils import Vector

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / 'tools/asset_pack'))
import geometry as g


def build(direction):
    bpy.ops.object.select_all(action='SELECT')
    bpy.ops.object.delete(use_global=False)
    col = g.collection('UI exploration — not approved')
    g.target(col)
    rgb = (0.77, 0.53, 0.25) if direction == 'ledger' else (0.30, 0.43, 0.53)
    body = g.material('UI ' + direction + ' enamel', rgb, roughness=.78)
    relief = g.material('UI warm relief', (.89, .73, .43), roughness=.72)
    # Face-on six-sided seal; broad relief depicts a watch gate, not a copied crest.
    verts = [(math.cos(i * math.tau / 6), math.sin(i * math.tau / 6), z)
             for z in (-.09, .09) for i in range(6)]
    faces = [tuple(reversed(range(6))), tuple(range(6, 12))]
    faces += [(i, (i+1) % 6, (i+1) % 6+6, i+6) for i in range(6)]
    g.mesh('Hex seal', verts, faces, body, bevel=.05)
    for x in (-.37, .37):
        g.cube('Gate pier', (x, -.04, .16), (.20, .78, .11), relief, bevel=.025)
    g.cube('Lintel', (0, .33, .16), (.94, .18, .11), relief, bevel=.025)
    g.cube('Step', (0, -.47, .16), (.94, .12, .11), relief, bevel=.025)
    scene = bpy.context.scene
    scene.render.engine = 'CYCLES'
    scene.cycles.device = 'CPU'
    scene.cycles.samples = 32
    scene.cycles.use_denoising = True
    scene.render.resolution_x = scene.render.resolution_y = 192
    scene.render.resolution_percentage = 100
    scene.render.film_transparent = True
    scene.render.image_settings.file_format = 'PNG'
    scene.render.image_settings.color_mode = 'RGBA'
    scene.view_settings.view_transform = 'AgX'
    scene.view_settings.look = 'AgX - Medium High Contrast'
    scene.world.color = (.12, .12, .12)
    camera = bpy.data.objects.new('Orthographic camera', bpy.data.cameras.new('UI camera'))
    scene.collection.objects.link(camera)
    camera.location = (0, 0, 5)
    camera.data.type = 'ORTHO'
    camera.data.ortho_scale = 2.4
    scene.camera = camera
    lamp = bpy.data.objects.new('Large soft key', bpy.data.lights.new('UI key', 'AREA'))
    scene.collection.objects.link(lamp)
    lamp.location = (-2, 3, 4)
    lamp.rotation_euler = (Vector((0, 0, 0)) - lamp.location).to_track_quat('-Z', 'Y').to_euler()
    lamp.data.energy = 350
    lamp.data.shape = 'DISK'
    lamp.data.size = 4
    scene['ui_exploration'] = direction
    scene['intended_display_px'] = 48
    source = ROOT / ('sources/ui/menu_seal.blend' if direction == 'ledger'
                     else 'sources/ui/explorations/watch_seal.blend')
    output = ROOT / ('ui/preview/UI/art/menu_seal.png' if direction == 'ledger'
                     else 'ui/preview/art/explorations/watch_seal.png')
    source.parent.mkdir(parents=True, exist_ok=True)
    output.parent.mkdir(parents=True, exist_ok=True)
    scene.render.filepath = str(output)
    bpy.ops.wm.save_as_mainfile(filepath=str(source))
    bpy.ops.render.render(write_still=True)


for variant in ('ledger', 'watch'):
    build(variant)
