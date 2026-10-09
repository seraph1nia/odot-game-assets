"""Bounded CPU GLB review fixtures using the existing studio/worker routes.

Renders complete new suite, legacy floor comparator, neighbor chains, all ground
families with both layers and occupied tiles. No source rebuild/save or game use.
"""
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
from mathutils import Matrix, Vector
from bpy_extras.object_utils import world_to_camera_view

import art_style as style
import geometry as g
import hex_ground as ground

OUT = g.ROOT/'docs/detailed-ground/renders'
PROFILES = []


def add(asset_id, pos=(0, 0, 0), turns=0):
    before = set(bpy.data.objects)
    path = g.ROOT/'exports'/f'{asset_id}.glb'
    bpy.ops.import_scene.gltf(filepath=str(path))
    objects = set(bpy.data.objects)-before
    for obj in objects:
        if obj.parent is None:
            # Imported roots may use QUATERNION mode: editing rotation_euler
            # silently does nothing. Apply placement in world Z-up explicitly.
            obj.matrix_world = (Matrix.Translation(Vector(pos)) @
                                Matrix.Rotation(turns*3.141592653589793/3, 4, 'Z') @ obj.matrix_world)
    bpy.context.view_layer.update()
    return objects


def render(name, assets, *, close=False, neighbors=False, occupied=False):
    g.clear_scene()
    for asset_id, pos, turns in assets:
        add(asset_id, pos, turns)
    g.studio(.18, 6.6)
    scene = bpy.context.scene
    camera = scene.camera
    if neighbors:
        points = [obj.matrix_world @ vertex.co for obj in scene.objects if obj.type == 'MESH'
                  and not obj.name.startswith('Studio ground') for vertex in obj.data.vertices]
        lo = Vector(tuple(min(p[i] for p in points) for i in range(3)))
        hi = Vector(tuple(max(p[i] for p in points) for i in range(3)))
        target = (lo+hi)/2
        camera.location = target+Vector((0, -5, 12))
        camera.rotation_euler = (target-camera.location).to_track_quat('-Z', 'Y').to_euler()
        camera.data.ortho_scale = max(hi.x-lo.x, (hi.y-lo.y)*1.5)+1.1
        scene.render.resolution_x, scene.render.resolution_y = 640, 440
    else:
        target = Vector((0, 0, .18 if not occupied else 1.0))
        camera.location = target+Vector((6, -9, 10))
        camera.rotation_euler = (target-camera.location).to_track_quat('-Z', 'Y').to_euler()
        camera.data.ortho_scale = 2.8 if close else 6.6 if not occupied else 7.3
        scene.render.resolution_x = scene.render.resolution_y = 400
    scene.render.resolution_percentage = 100
    scene.cycles.samples = 24
    scene.render.threads_mode = 'FIXED'
    scene.render.threads = style.PREVIEW.threads
    scene.cycles.device = 'CPU'
    scene.render.filepath = str(OUT/(name+'.png'))
    bpy.context.view_layer.update()
    projected = [world_to_camera_view(scene, camera, obj.matrix_world @ vertex.co)
                 for obj in scene.objects if obj.type == 'MESH' and not obj.hide_render
                 and not obj.name.startswith('Studio ground')
                 and not all(col.hide_render for col in obj.users_collection) for vertex in obj.data.vertices]
    projected_box = [min(p.x for p in projected)*scene.render.resolution_x,
                     min(p.y for p in projected)*scene.render.resolution_y,
                     max(p.x for p in projected)*scene.render.resolution_x,
                     max(p.y for p in projected)*scene.render.resolution_y]
    bpy.ops.render.render(write_still=True)
    PROFILES.append({'name': name, 'assets': [{'id': a, 'source_z_degrees': t*60, 'position': p,
                                            'glb_sha256': hashlib.sha256((g.ROOT/'exports'/f'{a}.glb').read_bytes()).hexdigest()}
                                           for a, p, t in assets],
                     'camera_location': list(camera.location), 'camera_rotation': list(camera.rotation_euler),
                     'ortho_scale': camera.data.ortho_scale, 'resolution': [scene.render.resolution_x, scene.render.resolution_y],
                     'projected_geometry_box_pixels': projected_box,
                     'samples': scene.cycles.samples, 'threads': scene.render.threads,
                     'style_sha256': hashlib.sha256((g.ROOT/'tools/asset_pack/art_style.py').read_bytes()).hexdigest(),
                     'exposure': scene.view_settings.exposure, 'glow': scene.use_nodes,
                     'runtime': bpy.app.version_string, 'engine': scene.render.engine,
                     'transform': scene.view_settings.view_transform, 'look': scene.view_settings.look,
                     'png_sha256': hashlib.sha256((OUT/(name+'.png')).read_bytes()).hexdigest()})
    print('Rendered GLB fixture:', name, flush=True)


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    for base in ground.BASES:
        asset = 'environment/hex_ground_'+base
        render('floor_'+base, [(asset, (0, 0, 0), 0)])
        render('close_'+base, [(asset, (0, 0, 0), 0)], close=True)
    render('floor_legacy', [('environment/components/forest_hex_meadow', (0, 0, 0), 0)])
    render('close_legacy', [('environment/components/forest_hex_meadow', (0, 0, 0), 0)], close=True)
    for family, prefix in (('path', 'hex_path_'), ('river', 'hex_river_overlay_')):
        for piece, edges in ground.PIECES.items():
            render(f'{family}_{piece}', [('environment/hex_ground_grass', (0, 0, 0), 0),
                                         ('environment/'+prefix+piece, (0, 0, 0), 0)])
            assets = [('environment/hex_ground_moss', (0, 0, 0), 0), ('environment/'+prefix+piece, (0, 0, 0), 0)]
            for edge in edges:
                n = ground.normal(edge)
                center = (2*style.HEX.half_height*n[0], 2*style.HEX.half_height*n[1], 0)
                assets += [('environment/hex_ground_moss', center, 0),
                           ('environment/'+prefix+'end', center, (edge+3)%6)]
            render(f'neighbors_{family}_{piece}', assets, neighbors=True)
        for base in ground.BASES:
            render(f'stack_{base}_{family}', [('environment/hex_ground_'+base, (0, 0, 0), 0),
                                             ('environment/'+prefix+'turn_60', (0, 0, 0), 0)])
    for role, asset, base in (('tree', 'environment/components/forest_tree_snag', 'moss'),
                              ('building', 'buildings/archery_range', 'grass'),
                              ('unit', 'characters/knight', 'dirt')):
        render('occupied_'+role, [('environment/hex_ground_'+base, (0, 0, 0), 0),
                                 ('environment/hex_path_straight', (0, 0, 0), 0),
                                 (asset, (0, 0, .012), 0)], occupied=True)
    (OUT.parent/'review-profiles.json').write_text(json.dumps(PROFILES, indent=2)+'\n')


if __name__ == '__main__':
    main()
