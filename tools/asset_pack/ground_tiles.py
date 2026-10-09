"""Build only the new detailed floors and independent path/surface-stream overlays.

Explicit rebuilds replace these generated sources/maps: preserve manual edits first.
No existing kit or terrain is rebuilt. Export via the existing catalog selector.
"""
import json
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import numpy as np

import art_style as style
import geometry as g
import ground_paint
import hex_ground as topology
import painted_finish as paint

DIRECTORY = g.ROOT / 'sources/environment/textures/ground'


def painted_material(family, *, overlay=False):
    mat = g.material('floor_' + family, style.GROUND.colors(family)[0])
    size = style.TEXTURES.size if overlay or family == 'foundation' else style.TEXTURES.ground_size
    rgb, height, rough = (ground_paint.overlay_fields if overlay else ground_paint.floor_fields)(family, size)
    linear = np.where(rgb <= .04045, rgb/12.92, ((rgb+.055)/1.055)**2.4)
    dy, dx = np.gradient(height)
    n = np.stack((-dx*size*style.GROUND.normal_strength, -dy*size*style.GROUND.normal_strength,
                  np.ones_like(dx)), axis=-1)
    n /= np.linalg.norm(n, axis=-1, keepdims=True)
    shader = next(node for node in mat.node_tree.nodes if node.type == 'BSDF_PRINCIPLED')
    for field, values, data in (('Base Color', linear, False), ('Roughness', rough, True),
                                 ('Normal', n*.5+.5, True)):
        image = paint.image_map('ground_' + family + '_' + field.lower().replace(' ', '_'),
                                values, DIRECTORY, data=data)
        texture = mat.node_tree.nodes.new('ShaderNodeTexImage')
        texture.image = image
        texture.extension = 'EXTEND'
        if field == 'Normal':
            normal = mat.node_tree.nodes.new('ShaderNodeNormalMap')
            mat.node_tree.links.new(texture.outputs['Color'], normal.inputs['Color'])
            mat.node_tree.links.new(normal.outputs['Normal'], shader.inputs[field])
        else:
            mat.node_tree.links.new(texture.outputs['Color'], shader.inputs[field])
    mat['painted_finish'] = paint.VERSION
    mat['texture_family'] = 'ground'
    mat['receiving_ground'] = not overlay and family != 'foundation'
    mat['ground_map_owner'] = 'ground_paint.py; generated authored adaptation'
    return mat


def uv_from_vertices(obj, coordinates):
    uv = obj.data.uv_layers.new(name=style.TEXTURES.uv_name)
    for loop in obj.data.loops:
        uv.data[loop.index].uv = coordinates[loop.vertex_index]


def base(family):
    r = style.HEX.radius
    ring = [(r*math.cos(i*math.pi/3), r*math.sin(i*math.pi/3)) for i in range(6)]
    top = g.mesh('Painted occupation surface', [(0, 0, style.HEX.surface)] +
                 [(x, y, style.HEX.surface) for x, y in ring],
                 [(0, i+1, (i+1)%6+1) for i in range(6)], painted_material(family))
    uv_from_vertices(top, [(v.co.x/(2*r)+.5, v.co.y/(2*r)+.5) for v in top.data.vertices])
    verts, faces, uvs = [], [], []
    for i, a in enumerate(ring):
        b = ring[(i+1)%6]
        index = len(verts)
        verts.extend([(a[0], a[1], style.HEX.bottom), (b[0], b[1], style.HEX.bottom),
                      (b[0], b[1], style.HEX.surface), (a[0], a[1], style.HEX.surface)])
        uvs.extend([(0, 0), (1, 0), (1, 1), (0, 1)])
        faces.append((index, index+1, index+2, index+3))
    sides = g.mesh('Canonical hex foundation', verts, faces, painted_material('foundation'))
    uv_from_vertices(sides, uvs)
    g.mesh('Hex underside', [(x, y, style.HEX.bottom) for x, y in ring],
           [tuple(reversed(range(6)))], g.M['floor_foundation'])


def build(asset_id):
    name = asset_id.rsplit('/', 1)[-1]
    g.clear_scene()
    # Own generated map/material users only; don't refresh unrelated painted maps.
    for mat in list(bpy.data.materials):
        if mat.name.startswith('floor_'):
            bpy.data.materials.remove(mat)
    for image in list(bpy.data.images):
        if image.name.startswith('ground_'):
            bpy.data.images.remove(image)
    col = g.collection(name)
    g.target(col)
    root = g.empty(name + '_root')
    root['ground_schema'] = 1
    root['ground_units'] = 'meters; source Z-up; GLB Y-up'
    root['ground_orientation'] = 'flat_top; edge0=+Y; CCW edge numbering'
    root['ground_origin'] = 'tile center; surface Z=0; no extra overlay translation'
    root['ground_reference_authority'] = 'authored adaptation; F3/F5 contextual only'
    root['footprint_radius'] = style.HEX.radius
    if name.startswith('hex_ground_'):
        family = name.removeprefix('hex_ground_')
        base(family)
        root['ground_layer'] = 'base'
        root['ground_family'] = family
        root['hex_radius'] = style.HEX.radius
        root['grid_spacing_x'] = style.HEX.spacing_x
        root['grid_spacing_y'] = style.HEX.spacing_y
        root['ground_height_min'] = style.HEX.bottom
        root['ground_height_max'] = style.HEX.surface
        root['occupation_surface'] = style.HEX.surface
    else:
        family = 'path' if name.startswith('hex_path_') else 'river'
        piece = name.removeprefix('hex_path_' if family == 'path' else 'hex_river_overlay_')
        verts, faces, uvs = topology.ribbon(family, piece)
        obj = g.mesh('Independent painted ' + family + ' ribbon', verts, faces,
                     painted_material(family, overlay=True))
        uv_from_vertices(obj, uvs)
        if piece == 'end':
            # Terminal banks follow radial distance, not projected X (which would
            # leave the tip unbanked). The endpoint paint is symmetric/quiet.
            row_faces = (len(topology.centerline(piece)[0])-1)*(len(style.GROUND.profile(family))-1)
            uv = obj.data.uv_layers.active
            for poly in list(obj.data.polygons)[row_faces:]:
                for index in poly.loop_indices:
                    p = obj.data.vertices[obj.data.loops[index].vertex_index].co
                    uv.data[index].uv = (.5 + math.hypot(p.x, p.y)/style.GROUND.width(family), 1)
        root['ground_layer'] = 'overlay'
        root['ground_family'] = family
        root['connector_edges'] = list(topology.PIECES[piece])
        root['connector_center_end'] = piece == 'end'
        root['connector_piece'] = piece
        root['connector_width'] = style.GROUND.width(family)
        root['connector_approach'] = style.GROUND.approach
        root['connector_profile'] = json.dumps(style.GROUND.profile(family))
        root['connector_interface'] = 'surface_path_v1' if family == 'path' else 'surface_stream_v1'
        root['ground_height_min'] = min(v[2] for v in verts)
        root['ground_height_max'] = max(v[2] for v in verts)
        root['occupation_surface'] = max(v[2] for v in verts)
    g.attach_all(col, root)
    paint.apply(col)
    col.asset_mark()
    col.asset_data.description = 'Authored detailed forest floor / independent surface overlay: ' + name
    g.studio(.18, 6.6)
    bpy.context.scene.name = name
    bpy.context.scene.render.filepath = str(g.ROOT/'exports/previews'/f'{name}.png')
    path = g.ROOT/'sources/environment'/f'{name}.blend'
    path.parent.mkdir(parents=True, exist_ok=True)
    bpy.ops.wm.save_as_mainfile(filepath=str(path))
    print('Authored', asset_id, flush=True)


if __name__ == '__main__':
    args = sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []
    selected = args or topology.IDS
    for asset_id in selected:
        if asset_id not in topology.IDS:
            raise ValueError('Choose canonical new ID: ' + asset_id)
        build(asset_id)
