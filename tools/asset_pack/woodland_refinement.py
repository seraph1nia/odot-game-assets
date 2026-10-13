"""Explicit source-preserving Whisperwood authoring, not a procedural rebuild.

Requires preserved baseline hashes and --apply. Existing manual geometry, maps,
UVs, armatures, actions, roots and socket transforms remain owned by saved sources.
Additive library details propagate into embedded copies without rebuilding them.
"""
import argparse
import hashlib
import json
import math
import random
import sys
from collections import Counter
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import numpy as np
from mathutils import Matrix, Vector
from mathutils.bvhtree import BVHTree
import art_style as style
import geometry as g
import painted_finish as paint
from woodland_profiles import BUILDINGS, UNITS
from tools.asset_catalog.export_sources import plan_exports

SPEC = style.WHISPERWOOD
TAG = SPEC.version
PREFIX = 'Woodland '
TEMPLATES = {}


def digest(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def decode(rgb):
    return np.where(rgb <= .04045, rgb / 12.92, ((rgb + .055) / 1.055) ** 2.4)


def encode(rgb):
    return np.where(rgb <= .0031308, rgb * 12.92, 1.055 * np.maximum(rgb, 0) ** (1 / 2.4) - .055)


def grade(rgb, *, accent=False, skin=False):
    saturation = SPEC.skin_saturation if skin else SPEC.accent_saturation if accent else SPEC.saturation
    value = SPEC.skin_value if skin else SPEC.accent_value if accent else SPEC.value
    luminance = np.sum(rgb * np.array((.2126, .7152, .0722)), axis=-1, keepdims=True)
    return np.clip((luminance + (rgb - luminance) * saturation) * value, 0, 1)


def retained_presentation_volume(mat):
    """Recognize the inspected volume output, never a name-based exemption."""
    outputs = [n for n in mat.node_tree.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output]
    if len(outputs) != 1:
        return False
    output = outputs[0]
    if output.inputs['Surface'].is_linked or output.inputs['Displacement'].is_linked:
        return False
    volume = output.inputs['Volume']
    if len(volume.links) != 1:
        return False
    link = volume.links[0]
    if (link.from_node.bl_idname != 'ShaderNodeVolumePrincipled' or
            link.from_node.type != 'PRINCIPLED_VOLUME' or link.from_socket.name != 'Volume'):
        return False
    users = [o for o in bpy.data.objects if o.type == 'MESH' and
             any(s.material == mat for s in o.material_slots)]
    return bool(users) and all(o.users_collection and
                              all(c.name == 'DISPLAY_ATMOSPHERE' for c in o.users_collection)
                              for o in users)


def grade_material(mat, directory):
    if mat.get('woodland_finish') == TAG or not mat.use_nodes:
        return False
    shader = next((n for n in mat.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
    if not shader:
        if retained_presentation_volume(mat):
            return False
        raise ValueError('Unsupported surface: ' + mat.name)
    outputs = [n for n in mat.node_tree.nodes if n.type == 'OUTPUT_MATERIAL' and n.is_active_output]
    if (len(outputs) != 1 or len(outputs[0].inputs['Surface'].links) != 1 or
            outputs[0].inputs['Surface'].links[0].from_node != shader):
        raise ValueError('Unsupported surface output: ' + mat.name)
    name = style.material_name(mat.name)
    skin = name.startswith(('skin', 'cream', 'fur_cream'))
    luminous = float(shader.inputs['Emission Strength'].default_value) > 0
    accent = name.startswith(('gold', 'window', 'rune', 'magic_core')) or luminous
    for channel in ('Base Color', 'Emission Color'):
        socket = shader.inputs[channel]
        socket.default_value = (*decode(grade(encode(np.array(socket.default_value[:3])), accent=accent, skin=skin)), socket.default_value[3])
        if not socket.is_linked:
            continue
        node = socket.links[0].from_node
        if node.type != 'TEX_IMAGE' or node.image is None:
            raise ValueError('Refusing nonportable/manual shader graph: ' + mat.name + '/' + channel)
        original = node.image
        if original.get('woodland_finish') == TAG:
            continue
        if original.colorspace_settings.name != style.TEXTURES.color_space:
            raise ValueError('Color channel must be sRGB: ' + original.name)
        values = np.empty(original.size[0] * original.size[1] * 4, dtype=np.float32)
        original.pixels.foreach_get(values)
        rgb = values.reshape(original.size[1], original.size[0], 4)[:, :, :3]
        # Byte-image pixels are encoded; preserved contact/manual variation is
        # graded, never regenerated from the old builders or studio illumination.
        key = hashlib.sha256(values.tobytes() + repr((accent, skin, channel)).encode()).hexdigest()[:20]
        replacement = paint.image_map(TAG + '_' + key, decode(grade(rgb, accent=accent, skin=skin)), directory)
        replacement['woodland_finish'] = TAG
        replacement['source_image'] = original.name
        node.image = replacement
    emission = shader.inputs['Emission Strength']
    if emission.is_linked:
        raise ValueError('Refusing linked emission strength: ' + mat.name)
    emission.default_value *= SPEC.window_emission_factor if name.startswith('window') else SPEC.emission_factor
    if not shader.inputs['Roughness'].is_linked:
        shader.inputs['Roughness'].default_value = max(float(shader.inputs['Roughness'].default_value), .76 if not name.startswith(('silver', 'gold', 'crystal')) else .38)
    mat.diffuse_color = shader.inputs['Base Color'].default_value
    mat['woodland_finish'] = TAG
    return True


def palette():
    g.M = {style.material_name(m.name): m for m in bpy.data.materials if m.use_nodes}
    for name, color in [('moss_woodland', SPEC.moss_color), ('forest_leaf_woodland', SPEC.leaf_color),
                        ('forest_leaf_woodland_tip', SPEC.leaf_tip), ('bark_woodland', SPEC.root_color),
                        ('stone_woodland_lichen', SPEC.lichen_color), ('woodland_cloth', SPEC.cloth_color)]:
        mat = g.material(name, color, .90)
        mat['woodland_finish'] = TAG
    # Material names remain compatible with existing geometry helpers.
    for name in ('wood', 'wood_dark', 'wood_light', 'leather', 'silver_dark', 'silver', 'gold', 'cream', 'stone', 'stone_dark', 'blue', 'red'):
        if name not in g.M:
            spec = style.BASE_MATERIALS[name]
            mat = g.material(name, style.woodland_color(spec.color), spec.roughness, spec.metallic)
            mat['woodland_finish'] = TAG


def finish_new(objects, category):
    directory = g.ROOT / 'sources' / category / 'textures/whisperwood'
    seen = set()
    for obj in objects:
        obj['woodland_detail'] = TAG
        obj['woodland_part'] = obj.name.split('.')[0]
        if obj.type != 'MESH':
            continue
        if obj.data not in seen:
            paint.project_uv(obj)
            seen.add(obj.data)
        for slot in obj.material_slots:
            if slot.material:
                paint.texture_material(slot.material, directory)


def templates():
    if TEMPLATES:
        return
    col = bpy.data.collections.new('WHISPERWOOD_PROTOTYPES — excluded')
    previous = g.CURRENT
    g.target(col)
    length = SPEC.leaf_length
    leaf = g.mesh(PREFIX + 'shared curved ivy leaf', [(0, 0, 0), (-length*.45, length*.36, .02),
                  (0, length*.48, .035), (length*.45, length*.36, .02), (0, length, .055)],
                  [(0, 1, 2), (0, 2, 3), (1, 4, 2), (2, 4, 3)], 'forest_leaf_woodland')
    leaf.data.materials.append(g.M['forest_leaf_woodland_tip'])
    for face in leaf.data.polygons:
        face.material_index = int(face.center.y > length*.45)
    moss = g.ico(PREFIX + 'shared moss cushion', (0, 0, .015), (SPEC.moss_radius, SPEC.moss_radius*.78, SPEC.moss_radius*.42), 'moss_woodland', 2, .08)
    TEMPLATES.update(leaf=leaf, moss=moss)
    finish_new([leaf, moss], 'environment')
    g.target(previous)


def instance(kind, pos, scale=1, rotation=None):
    templates()
    obj = TEMPLATES[kind].copy()
    g.CURRENT.objects.link(obj)
    obj.location = pos
    obj.scale = (scale,)*3 if isinstance(scale, (int, float)) else scale
    if rotation:
        obj.rotation_euler = rotation
    return obj


def cluster(pos, rng, radius=.22, count=10, *, normal=(0, 0, 1)):
    n = Vector(normal).normalized()
    basis = n.to_track_quat('Z', 'Y').to_matrix()
    for i in range(count):
        angle = rng.uniform(0, math.tau)
        r = radius * math.sqrt(rng.random())
        p = Vector(pos) + basis @ Vector((math.cos(angle)*r, math.sin(angle)*r, .01))
        obj = instance('moss' if i % 3 == 0 else 'leaf', p, rng.uniform(.65, 1.45))
        obj.rotation_euler = (basis.to_4x4() @ Matrix.Rotation(angle, 4, 'Z')).to_euler()


def vine(points, rng, radius=SPEC.vine_radius, *, leaves=True):
    obj = g.tube(PREFIX + 'joint-following vine', points, [radius*(1-i/(len(points)+1)*.8) for i in range(len(points))], 'bark_woodland', 7)
    if leaves:
        for i, point in enumerate(points[1:]):
            side = -1 if i % 2 else 1
            instance('leaf', point, rng.uniform(.8, 1.3), (math.pi*.36, side*.3, side*.8))
    return obj


def bounds(objects):
    points = [o.matrix_world @ Vector(c) for o in objects if o.type == 'MESH' for c in o.bound_box]
    return (Vector(tuple(min(p[i] for p in points) for i in range(3))),
            Vector(tuple(max(p[i] for p in points) for i in range(3))))


def surface_tree(objects):
    vertices, faces = [], []
    for obj in objects:
        if obj.type != 'MESH' or obj.get('woodland_detail'):
            continue
        if not any(style.material_family(s.material.name) in ('wood', 'stone', 'roof', 'plaster') for s in obj.material_slots if s.material):
            continue
        if obj.name.startswith(('Fine', 'Dark inset', 'Carved timber grain', 'Round iron', 'Window', 'Warm arched')):
            continue
        start = len(vertices)
        vertices.extend(obj.matrix_world @ v.co for v in obj.data.vertices)
        faces.extend(tuple(i+start for i in p.vertices) for p in obj.data.polygons)
    return BVHTree.FromPolygons(vertices, faces) if vertices else None


def planted_building(col, rng, *, roots=True):
    original = list(col.all_objects)
    tree = surface_tree(original)
    if not tree:
        raise ValueError('Building has no structural surfaces: ' + col.name)
    low, high = bounds(original)
    # Irregular roof shelves attach to real upward surfaces, not floating disks.
    for i in range(90):
        x, y = rng.uniform(max(low.x, -1.5), min(high.x, 1.5)), rng.uniform(-.75, .85)
        hit, normal, _, _ = tree.ray_cast(Vector((x, y, high.z+1)), Vector((0, 0, -1)))
        if hit and abs(normal.z) > .2 and hit.z > 1.4 and (i % 3 or x < -.35):
            # Existing saved two-sided cuboids can have inward face winding.
            # Orient placement normals against the cast without rewriting them.
            if normal.z < 0:
                normal = -normal
            cluster(hit, rng, .16, 6, normal=normal)
    # Two climbing routes keep the central entrance/role sign free.
    for x in (-.92, .92):
        points = []
        for i in range(18):
            z = .09 + i*.145
            px = x + .11*math.sin(i*.64) + .035*math.sin(i*1.7)
            hit, normal, _, _ = tree.ray_cast(Vector((px, low.y-1, z)), Vector((0, 1, 0)))
            if hit and abs(normal.y) > .2:
                if normal.y > 0:
                    normal = -normal
                points.append(hit + normal*.018)
        if len(points) > 3:
            vine(points, rng, SPEC.vine_radius*1.5)
            cluster(points[0], rng, .20, 16)
    for x, y in ([(-.94, -.72), (.94, -.72), (-.82, .72), (.86, .74)] if roots else []):
        vine([(x, y, .46), (x*1.06, y*1.08, .16), (x*1.2, y*1.18, .025), (x*1.35, y*1.23, .01)], rng, SPEC.root_radius)
        cluster((x*1.15, y*1.16, .025), rng, .19, 15)


def feature_scale(objects, prefixes, factor):
    def embedded(obj):
        while obj.parent:
            obj = obj.parent
            if obj.get('kit_source'):
                return True
        return False
    selected = [o for o in objects if o.type == 'MESH' and o.name.startswith(prefixes) and not embedded(o)]
    if not selected:
        return []
    # Local mesh edits preserve skeleton weights/object parent transforms. Copy
    # only the changed data; unmodified repeated prototypes retain shared meshes.
    low, high = bounds(selected)
    pivot = (low+high)/2
    pivot.z = low.z
    world = Matrix.Translation(pivot) @ Matrix.Diagonal((*factor, 1)) @ Matrix.Translation(-pivot)
    for obj in selected:
        obj.data = obj.data.copy()
        obj.data.transform(obj.matrix_world.inverted() @ world @ obj.matrix_world)
    return [o.name for o in selected]


def banner(name, x, y, z, width, height, color='woodland_cloth'):
    verts = [(x-width/2, y, z), (x+width/2, y, z), (x-width*.49, y-.06, z-height*.48),
             (x+width*.49, y-.08, z-height*.48), (x-width*.44, y+.025, z-height),
             (x+width*.4, y+.02, z-height*.93), (x, y-.09, z-height*1.06)]
    obj = g.mesh(PREFIX + name, verts, [(0, 1, 3, 2), (2, 3, 5, 6, 4)], color)
    mod = obj.modifiers.new('Woven cloth edge thickness', 'SOLIDIFY')
    mod.thickness = .018
    return obj


def branches(x, y, z, size, rng, *, lanterns=False):
    for sign in (-1, 1):
        points = [(x+sign*.15*size, y, z), (x+sign*.40*size, y+.07, z+.42*size),
                  (x+sign*.81*size, y+.10, z+.68*size), (x+sign*.94*size, y+.15, z+size)]
        vine(points, rng, .095*size)
        for i in (1, 2):
            p = points[i]
            vine([p, (p[0]+sign*.15*size, p[1]-.08, p[2]+.31*size)], rng, .047*size)
            cluster(p, rng, .11*size, 5)
        if lanterns:
            p = points[2]
            g.beam(PREFIX + 'lantern suspension', p, (p[0], p[1], p[2]-.26), .025, .025, 'silver_dark', 0)
            g.lantern((p[0], p[1], p[2]-.38), .72)


def building_detail(kind, rng):
    if kind == 'saw_wheel':
        center = (1.34, -.93, 1.04)
        g.torus(PREFIX + 'great lumber saw wheel', center, .69, .09, 'wood_dark', 'Y', 28)
        g.torus(PREFIX + 'saw iron rim', (1.34, -1.015, 1.04), .68, .028, 'silver_dark', 'Y', 28)
        for i in range(10):
            a = i*math.tau/10
            end = (center[0]+math.sin(a)*.63, center[1], center[2]+math.cos(a)*.63)
            g.beam(PREFIX + 'saw wheel spoke', center, end, .075, .08, 'wood_light')
        g.tube(PREFIX + 'saw axle', [(1.34, -1.17, 1.04), (1.34, -.62, 1.04)], .13, 'silver_dark', 12)
        branches(0, .20, 2.9, 1, rng)
        g.beam(PREFIX + 'log hoist branch', (.40, .40, 3.42), (1.92, .2, 3.42), .14, .16, 'bark_woodland')
        for x in (1.37, 1.8):
            g.tube(PREFIX + 'log hoist rope', [(x, .2, 3.42), (x, .2, 2.6)], .023, 'leather', 6)
        g.log((1.15, .2, 2.53), .88, .145, 'X')
    elif kind == 'bread_cap':
        cap = g.lathe(PREFIX + 'layered bakery porch cap', [(0, .98), (.12, 1.02), (.32, .83), (.47, .58), (.56, .14)], 'wood_light', 20, (0, -1.23, 1.65))
        for v in cap.data.vertices:
            v.co.y = -1.23+(v.co.y+1.23)*.53
        for sign in (-1, 1):
            for i in range(6):
                x, y = sign*1.18+math.sin(i)*.06, -1.05+i*.075
                g.beam(PREFIX + 'wheat stalk', (x, y, .03), (x+.07, y, .75+i*.025), .019, .019, 'wood_light', 0)
                for k in range(4):
                    g.ico(PREFIX + 'wheat ear', (x+.07, y, .58+k*.057+i*.025), (.041, .03, .07), 'gold', 1, .01)
    elif kind in ('standing_blocks', 'ore_stack'):
        for i in range(3):
            x, y = (1.27+i*.23, .35+i*.32) if kind == 'standing_blocks' else (-1.62+i*.30, .6+i*.19)
            height = (1.25, 1.9, 1.45)[i] if kind == 'standing_blocks' else (.8, 1.25, .9)[i]
            g.cube(PREFIX + 'standing dressed block' if kind == 'standing_blocks' else PREFIX + 'railside ore stack', (x, y, height/2), (.38, .45, height), 'stone' if kind == 'standing_blocks' else 'silver_dark', style.GEOMETRY.stone_bevel_width, (0, -.05+i*.05, .12*i))
            cluster((x, y, height+.01), rng, .15, 7)
    elif kind in ('civic_crown', 'arcane_crown'):
        branches(0, .34, 3.65 if kind == 'civic_crown' else 3.25, 1.13 if kind == 'civic_crown' else .84, rng, lanterns=True)
        if kind == 'arcane_crown':
            for i in range(3):
                g.cube(PREFIX + 'academy shelf folio', (.9+i*.12, -.98, .42+i*.13), (.36, .24, .09), 'blue', .01, (0, 0, .15*i))
    elif kind == 'flowing_cloth':
        for i in range(3):
            banner('long draped dyed cloth', .62+i*.24, -1.89-.03*i, 2.65-i*.20, .29, 1.04-i*.12, 'blue' if i != 1 else 'cream')
        g.beam(PREFIX + 'drapery branch lintel', (.3, -1.89, 2.65), (1.44, -1.89, 2.40), .1, .1, 'bark_woodland')
        for i in range(3):
            g.lathe(PREFIX + 'large working bobbin', [(0, .085), (.04, .085), (.04, .055), (.22, .055), (.22, .085), (.25, .085)], 'wood_light', 10, (-1.55+i*.18, -1.08, .76))
    elif kind == 'market_tents':
        for sign in (-1, 1):
            x = sign*1.25
            g.beam(PREFIX + 'high tent mast', (x, -.22, 0), (x, -.22, 2.8), .09, .09, 'wood_dark')
            g.mesh(PREFIX + 'peaked merchant canvas', [(x-.64, -.72, 2.05), (x+.64, -.72, 2.05), (x+.64, .30, 2.14), (x-.64, .30, 2.14), (x, -.22, 2.78)], [(0, 1, 4), (1, 2, 4), (2, 3, 4), (3, 0, 4)], 'woodland_cloth' if sign < 0 else 'cream')
            for i in range(2):
                g.cube(PREFIX + 'tied merchant parcel', (x+i*.16, -.57, .2), (.28, .27, .32), 'leather', .018)
                g.torus(PREFIX + 'parcel twine', (x+i*.16, -.57, .2), .16, .014, 'wood_light', 'X', 8)
    elif kind == 'portal_roots':
        vine([(-.95, -.86, .08), (-1.05, -.9, .8), (-.83, -.96, 1.65), (-.22, -.97, 1.9), (.40, -.98, 1.74), (.97, -.93, .87)], rng, .13)
    elif kind == 'brewing_casks':
        for i in range(2):
            g.barrel((1.43, -.22+i*.58, 0), .9)
            g.torus(PREFIX + 'brew tap seal', (1.43, -.52+i*.58, .31), .09, .022, 'gold', 'Y', 12)
    elif kind in ('watch_basket', 'tree_baskets'):
        for i in range(1 if kind == 'watch_basket' else 2):
            x, y, z = (.92, -.70, 2.05) if kind == 'watch_basket' else (-1.05+i*2.04, -.45, 2.33+i*.4)
            g.lathe(PREFIX + 'suspended supply basket', [(0, .13), (.20, .22), (.3, .22)], 'wood_light', 12, (x, y, z))
            for sign in (-1, 1):
                g.beam(PREFIX + 'basket braided suspension', (x+sign*.18, y, z+.3), (x, y, z+.72), .02, .02, 'leather', 0)
            cluster((x, y, z+.26), rng, .10, 7)
    elif kind == 'star_chart':
        banner('hanging observatory star chart', -.82, -1.06, 2.22, .56, .77, 'blue')
        for i in range(5):
            g.ico(PREFIX + 'chart brass star marker', (-1.02+i*.095, -1.13, 1.72+.18*math.sin(i*1.8)), (.022, .012, .022), 'gold', 1, 0)
    elif kind == 'ammo_cradle':
        for i in range(3):
            g.ico(PREFIX + 'stacked ammunition', (1.22, -.55+i*.27, .18), (.17,)*3, 'silver_dark', 2, .01)
        for sign in (-1, 1):
            g.beam(PREFIX + 'ammunition cradle rail', (1.22+sign*.2, -.73, .04), (1.22+sign*.2, .20, .04), .09, .1, 'wood_dark')
    elif kind in ('bow_rack', 'spear_standard'):
        for i in range(3):
            x = -1.48+i*.14
            g.tube(PREFIX + 'bundled field spear' if kind == 'spear_standard' else PREFIX + 'spare curved field bow', [(x, -.68, .12), (x-.08, -.67, .8), (x-.05, -.65, 1.64)], .029, 'wood_light', 6)
            if kind == 'spear_standard':
                g.ico(PREFIX + 'spear leaf blade', (x-.05, -.65, 1.76), (.075, .025, .18), 'silver', 1, 0)
        g.beam(PREFIX + 'rack leather binding', (-1.58, -.715, .78), (-1.08, -.715, .78), .048, .035, 'leather')
    else:
        raise ValueError('Unknown building detail ' + kind)


def attach_rest(objects, rig, bone):
    # Armature deformation uses rest-world vertices and the unchanged anatomical
    # bone. No bone-parent inverse guessing, no new skeleton or applied modifier.
    for obj in objects:
        if obj.type != 'MESH':
            continue
        world = obj.matrix_world.copy()
        obj.parent = rig
        obj.matrix_world = world
        group = obj.vertex_groups.new(name=bone)
        group.add(list(range(len(obj.data.vertices))), 1, 'REPLACE')
        mod = obj.modifiers.new('Shared skeleton — woodland attachment', 'ARMATURE')
        mod.object = rig


def unit_detail(kind, rig):
    before = set(g.CURRENT.objects)
    if kind in ('bedroll', 'war_mantle'):
        if kind == 'bedroll':
            g.tube(PREFIX + 'pilgrim bedroll', [(-.37, .37, 1.34), (.37, .37, 1.34)], .16, 'woodland_cloth', 12)
            for x in (-.22, .22):
                g.torus(PREFIX + 'bedroll leather strap', (x, .37, 1.34), .16, .023, 'leather', 'X', 12)
        else:
            for i in range(5):
                banner('battered sentry mantle', -.34+i*.17, .32, 1.56, .19, .57+i%2*.1, 'leather')
        attach_rest(set(g.CURRENT.objects)-before, rig, 'spine')
    elif kind in ('scrolls', 'forager', 'talismans', 'ambusher'):
        for i in range(3):
            x = -.38+i*.13 if kind == 'scrolls' else .34+i*.07
            z = .95+i%2*.12
            if kind == 'scrolls':
                g.lathe(PREFIX + 'travel scroll', [(0, .055), (.29, .055)], 'cream', 10, (x, -.34, z))
                g.torus(PREFIX + 'scroll tie', (x, -.34, z+.14), .055, .012, 'leather', 'Z', 10)
            elif kind == 'ambusher':
                g.cube(PREFIX + 'ambusher bolt case', (x, .20, 1.12), (.11, .14, .46), 'wood_dark', .018)
                g.beam(PREFIX + 'case wire binding', (x-.055, .11, 1.03), (x+.055, .11, 1.03), .023, .023, 'silver_dark', 0)
            elif kind == 'talismans':
                g.lathe(PREFIX + 'occult field vial', [(0, .04), (.12, .055), (.17, .02)], 'stone_dark', 8, (x, -.32, z-.15))
                g.ico(PREFIX + 'vial bone stopper', (x, -.32, z+.035), (.035,)*3, 'cream', 1, 0)
            else:
                g.ico(PREFIX + 'forager seed pouch', (x, -.24, z-.1), (.065, .09, .1), 'leather', 2, .02)
                g.torus(PREFIX + 'pouch cord', (x, -.24, z-.02), .055, .012, 'wood_light', 'Z', 10)
        attach_rest(set(g.CURRENT.objects)-before, rig, 'pelvis')
        before = set(g.CURRENT.objects)
        if kind in ('talismans', 'scrolls'):
            g.torus(PREFIX + 'scholar talisman chain', (0, -.27, 1.36), .13, .014, 'gold', 'Y', 16)
            g.ico(PREFIX + 'carved talisman', (0, -.30, 1.2), (.06, .026, .09), 'stone', 1, 0)
        elif kind == 'ambusher':
            banner('long torn ambusher scarf', .36, .25, 1.66, .28, .9, 'red')
        attach_rest(set(g.CURRENT.objects)-before, rig, 'spine')
    elif kind in ('trophies', 'jaw_trophies'):
        for i in range(5):
            x, z = -.25+i*.125, 1.32-.07*math.sin(i*math.pi/4)
            g.tube(PREFIX + 'bone trophy tooth', [(x, -.31, z+.03), (x+.012, -.36, z-.13)], [.047, .012], 'cream', 7)
        attach_rest(set(g.CURRENT.objects)-before, rig, 'spine')
        before = set(g.CURRENT.objects)
        for i in range(5):
            g.ico(PREFIX + 'shaggy traveler belt tuft', (-.30+i*.15, .09, .95), (.12, .13, .17), 'leather' if kind == 'jaw_trophies' else 'cream', 1, .02)
        attach_rest(set(g.CURRENT.objects)-before, rig, 'pelvis')
    else:
        raise ValueError('Unknown unit detail ' + kind)


def binding_frame(root, name):
    """Fit extra wraps to authored grip geometry, not the attachment pivot."""
    grip_name = {'bow': 'Bow grip', 'crossbow': 'Crossbow pistol grip'}.get(name)
    if grip_name is None:
        return Matrix.Identity(4)
    grips = [o for o in root.children_recursive if o.type == 'MESH' and o.name.split('.')[0] == grip_name]
    if len(grips) != 1:
        raise ValueError('Expected one authored grip for ' + name)
    obj = grips[0]
    local = root.matrix_world.inverted() @ obj.matrix_world
    center = sum((local @ v.co for v in obj.data.vertices), Vector()) / len(obj.data.vertices)
    normals = [local.to_3x3().inverted().transposed() @ p.normal for p in obj.data.polygons]
    axis = max(normals, key=lambda n: abs(n.z)).normalized()
    if axis.z < 0:
        axis = -axis
    return Matrix.Translation(center) @ axis.to_track_quat('Z', 'Y').to_matrix().to_4x4()


def gear_detail(root, name, category):
    if root.get('woodland_gear') == TAG:
        return
    previous = g.CURRENT
    col = next(iter(root.users_collection))
    g.target(col)
    before = set(col.objects)
    if 'shield' in name:
        # Wider shield field/edge but unchanged hand grip and attachment scale.
        meshes = [o for o in root.children_recursive if o.type == 'MESH' and 'grip' not in o.name.lower()]
        for obj in meshes:
            obj.data = obj.data.copy()
            obj.data.transform(Matrix.Diagonal((1.12, 1, 1.08, 1)))
        for x in (-.34, .34):
            for z in (-.22, .18, .45):
                g.ico(PREFIX + 'shield worn iron rivet', (x, -.14, z), (.024, .013, .024), 'silver_dark', 1, 0)
    elif name in ('staff', 'evil_staff', 'bow', 'crossbow', 'axe', 'axe_offhand', 'evil_axe', 'evil_axe_offhand', 'sword', 'evil_sword'):
        frame = binding_frame(root, name)
        for i in range(3):
            # Attachment pivots are not necessarily geometric grip centers.
            obj = g.torus(PREFIX + 'equipment worn binding', (0, 0, -.065+i*.07), .058 if 'axe' not in name else .068, .011, 'leather', 'Z', 10)
            obj.data.transform(frame)
        if 'staff' in name:
            g.tube(PREFIX + 'staff hanging charm cord', [(.11, 0, 1.01), (.18, -.04, .74)], .012, 'leather', 6)
            g.ico(PREFIX + 'staff carved seed charm', (.18, -.04, .70), (.05, .04, .08), 'stone', 1, 0)
    added = list(set(col.objects)-before)
    for obj in added:
        obj.parent = root
        obj.matrix_parent_inverse = Matrix.Identity(4)
    finish_new(added, category)
    root['woodland_gear'] = TAG
    g.target(previous)


def prototype_detail(col, rng, *, inverted_surfaces_only=False):
    """Category-appropriate additions; no common wreath for every kit object."""
    g.target(col)
    kind = col.name.removeprefix('forest_').removeprefix('kit_')
    original = [o for o in col.objects if o.type == 'MESH']
    if not original:
        return
    # Prototypes are placement-local; their overview display collection instances
    # must not contribute the display offsets to the authored geometry.
    low, high = bounds(original)
    center = (low+high)/2
    tree = surface_tree(original)
    if kind in ('boulder', 'stone_block', 'stone_arch_block', 'shrine_plinth', 'rune_monolith', 'bridge_plank', 'bridge_post', 'bridge_rail', 'root', 'tree_snag', 'hollow_tree', 'spiral_tree', 'lantern_post', 'roof_tile', 'bench', 'barrel', 'open_barrel', 'crate', 'open_crate', 'target'):
        if tree:
            for i in range(12):
                x, y = rng.uniform(low.x, high.x), rng.uniform(low.y, high.y)
                hit, normal, _, _ = tree.ray_cast(Vector((x, y, high.z+1)), Vector((0, 0, -1)))
                if hit and abs(normal.z) > .2 and (not inverted_surfaces_only or normal.z < 0):
                    if normal.z < 0:
                        normal = -normal
                    cluster(hit, rng, min(.09, (high-low).length*.07), 3, normal=normal)
        if inverted_surfaces_only:
            return
        if kind in ('tree_snag', 'hollow_tree', 'spiral_tree'):
            vine([(center.x-.20, center.y, low.z+.08), (center.x-.14, center.y-.22, .45), (center.x+.13, center.y-.24, .95), (center.x+.15, center.y-.14, 1.4)], rng)
    elif inverted_surfaces_only:
        return
    elif kind in ('leaf_clump', 'fern', 'spiral_fern', 'moss', 'shrub', 'pine'):
        for i in range(14 if kind != 'pine' else 8):
            angle = i*2.399
            r = min(.27, (high-low).length*.15)*math.sqrt((i+1)/14)
            instance('leaf', (center.x+math.cos(angle)*r, center.y+math.sin(angle)*r, low.z+.015+(i%3)*.025), rng.uniform(1, 1.7), (.3+i%2*.3, 0, angle))
    elif kind.startswith('mushroom'):
        cluster((center.x-.12, center.y, low.z+.025), rng, min(.12, (high-low).length*.09), 10)
    elif kind.startswith('crystal'):
        cluster((center.x-.13, center.y+.03, low.z+.015), rng, .11, 7)
    elif kind in ('jackalope', 'lantern_snail'):
        if kind == 'jackalope':
            for sign in (-1, 1):
                g.tube(PREFIX + 'delicate whisker', [(sign*.045, -.26, .24), (sign*.17, -.30, .25)], .004, 'cream', 4)
        else:
            g.torus(PREFIX + 'snail weathered shell rim', (0, 0, .20), .13, .014, 'wood_light', 'Y', 14)
    elif kind in ('butterfly_cyan', 'butterfly_sunset', 'moon_moth'):
        for sign in (-1, 1):
            g.tube(PREFIX + 'delicate antenna fork', [(sign*.025, -.08, .015), (sign*.06, -.14, .03), (sign*.10, -.16, .015)], .005, 'wood_dark', 5)
    elif kind == 'lantern_flower':
        for i in range(3):
            instance('leaf', (0, 0, low.z+.06*i), 1.2, (.35, .15, i*2.1))
    elif kind in ('book', 'parcel', 'mug', 'lantern'):
        # Groundless objects keep functional silhouettes: small seam/strap details.
        g.beam(PREFIX + 'worn prop binding', (low.x, low.y-.007, center.z), (high.x, low.y-.007, center.z), .017, .012, 'leather', 0)
    # Arrow, spear, skull, spike, cannonball, foam, water, runes and hex-base
    # prototypes deliberately use material wear/muted emission, not obstructive
    # extra geometry. Their category treatment is recorded as material-only.


def sync_libraries():
    additions = []
    roots = [o for o in bpy.data.objects if o.get('kit_source') and o.get('kit_asset')]
    for path in sorted({o['kit_source'] for o in roots}):
        group = [o for o in roots if o['kit_source'] == path]
        names = tuple(sorted({o['kit_asset'] if o['kit_asset'].startswith('forest_') else 'kit_'+o['kit_asset'] for o in group}))
        with bpy.data.libraries.load(str(g.ROOT/path), link=False) as (_, dest):
            # Blender replaces the requested-name list with datablocks in place.
            # Keep immutable keys separate from that mutable RNA return list.
            dest.collections = list(names)
        prototypes = dict(zip(names, dest.collections, strict=True))
        for root in group:
            key = root['kit_asset'] if root['kit_asset'].startswith('forest_') else 'kit_'+root['kit_asset']
            prototype = prototypes[key]
            if prototype is None:
                raise ValueError('Missing prototype: ' + path + '/' + key)
            existing = Counter(o.get('woodland_part') for o in root.children if o.get('woodland_detail'))
            encountered = Counter()
            col = next(iter(root.users_collection))
            for original in prototype.objects:
                if not original.get('woodland_detail'):
                    continue
                part = original.get('woodland_part')
                encountered[part] += 1
                if encountered[part] <= existing[part]:
                    continue
                obj = original.copy()
                col.objects.link(obj)
                obj.parent = root
                obj.matrix_parent_inverse = Matrix.Identity(4)
                obj.matrix_basis = original.matrix_basis.copy()
                additions.append(obj)
            root['woodland_library'] = TAG
        # Remove unlinked appended prototype objects/collections, retaining their
        # shared meshes in copies; never link the library's display scene.
        for prototype in prototypes.values():
            for obj in list(prototype.objects):
                bpy.data.objects.remove(obj, do_unlink=True)
            bpy.data.collections.remove(prototype)
    return additions


def armature_contract():
    return {o.name: {'bones': [(b.name, b.parent.name if b.parent else None, tuple(b.head_local), tuple(b.tail_local), b.use_deform) for b in o.data.bones],
                     'actions': [(t.name, [(s.action.name, s.frame_start, s.frame_end) for s in t.strips]) for t in o.animation_data.nla_tracks] if o.animation_data else [],
                     'matrix': [list(row) for row in o.matrix_world]}
            for o in bpy.data.objects if o.type == 'ARMATURE'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--baseline', default='docs/whisperwood/baseline.json')
    parser.add_argument('--apply', action='store_true')
    parser.add_argument('--growth-revision', action='store_true', help='Add corrected surface growth to already-authored sources only')
    parser.add_argument('sources', nargs='*', help='Source paths; defaults to complete 3D closure')
    args = parser.parse_args(sys.argv[sys.argv.index('--')+1:])
    baseline = json.loads((g.ROOT/args.baseline).read_text())
    jobs = plan_exports(g.ROOT)
    sources = sorted(set(args.sources or [j['source'] for j in jobs]))
    libraries = ['sources/props/shared_village_kit.blend', 'sources/environment/shared_forest_kit.blend', 'sources/environment/shared_enchanted_kit.blend']
    sources.sort(key=lambda p: (p not in libraries, libraries.index(p) if p in libraries else p))
    if not args.apply:
        print(json.dumps({'profile': TAG, 'sources': sources, 'ids': [j['id'] for j in jobs if j['source'] in sources]}, indent=2))
        return
    # Fail closed before the first write. Repeated passes are explicit; each
    # source already bearing the applied scene tag is skipped, not double-graded.
    authored_path = g.ROOT/'docs/whisperwood/authored.json'
    authored = json.loads(authored_path.read_text()) if authored_path.exists() else {'profile': TAG, 'sources': {}}
    for path in sources:
        expected = authored['sources'].get(path, {}).get('sha256_after', baseline['files'][path]['sha256'])
        if digest(g.ROOT/path) != expected:
            raise ValueError('Refusing changed/unpreserved source: ' + path)
    for path in sources:
        already = path in authored['sources']
        if already and not args.growth_revision:
            continue
        bpy.ops.wm.open_mainfile(filepath=str(g.ROOT/path))
        TEMPLATES.clear()
        bpy.context.scene.frame_set(1)
        if args.growth_revision and bpy.context.scene.get('woodland_growth_revision') == 1:
            continue
        bpy.context.view_layer.update()
        before_rig = armature_contract()
        palette()
        category = Path(path).parts[1]
        existing = set(bpy.data.objects)
        modified = []
        name = Path(path).stem
        rng = random.Random(int(hashlib.sha256(name.encode()).hexdigest()[:8], 16))
        if path in libraries:
            for col in list(bpy.data.collections):
                if col.name.startswith(('kit_', 'forest_')) and (not col.get('woodland_finish') or args.growth_revision):
                    previous = set(col.objects)
                    prototype_detail(col, rng, inverted_surfaces_only=args.growth_revision)
                    finish_new(set(col.objects)-previous, category)
                    col['woodland_finish'] = TAG
        else:
            sync_libraries()
            if name in BUILDINGS:
                col = bpy.data.collections[name]
                g.target(col)
                profile = BUILDINGS[name]
                if not args.growth_revision:
                    modified = feature_scale(list(col.all_objects), profile['feature'], (1.12, 1.08, 1.1))
                planted_building(col, rng, roots=not args.growth_revision)
                if not args.growth_revision:
                    building_detail(profile['detail'], rng)
                elif name == 'weaver':
                    for obj in col.objects:
                        if obj.get('woodland_part') in ('Woodland long draped dyed cloth', 'Woodland drapery branch lintel'):
                            obj.data = obj.data.copy()
                            obj.data.transform(Matrix.Translation((0, -.75, 0)))
                new = [o for o in col.all_objects if o not in existing]
                finish_new(new, category)
                root = bpy.data.objects.get(name+'_root') or next(o for o in col.objects if o.parent is None and o.type == 'EMPTY')
                # New group proportions change each massing, keeping canonical
                # ground root transform/pivot unchanged and preserving mesh reuse.
                group = bpy.data.objects.get(PREFIX+'role proportions') if args.growth_revision else None
                if group is None:
                    group = g.empty(PREFIX + 'role proportions')
                    group.parent = root
                bpy.context.view_layer.update()
                for obj in list(col.objects):
                    if obj not in (root, group) and obj.parent == root:
                        world = obj.matrix_world.copy()
                        obj.parent = group
                        obj.matrix_world = world
                    elif obj not in (root, group) and obj.parent is None:
                        world = obj.matrix_world.copy()
                        obj.parent = group
                        obj.matrix_world = world
                group.scale = profile['scale']
                col['woodland_signature'] = profile['signature']
            elif name in UNITS and not args.growth_revision:
                col = bpy.data.collections[name]
                g.target(col)
                profile = UNITS[name]
                modified = feature_scale(list(col.all_objects), profile['feature'], profile['factor'])
                rig = next(o for o in col.all_objects if o.type == 'ARMATURE')
                unit_detail(profile['detail'], rig)
                finish_new([o for o in col.all_objects if o not in existing], category)
                col['woodland_signature'] = profile['signature']
            # Explicit standalone weapon roots and character-equipped copies use
            # the same local recipe, retaining grips and attachment transforms.
            for obj in list(bpy.data.objects):
                if obj.type == 'EMPTY' and obj.name.split('.')[0] in ('shield', 'evil_shield', 'sword', 'evil_sword', 'staff', 'evil_staff', 'bow', 'crossbow', 'axe', 'axe_offhand', 'evil_axe', 'evil_axe_offhand', 'arrow', 'evil_hand_flame'):
                    gear_detail(obj, obj.name.split('.')[0], category)
        owned = {o for j in jobs if j['source'] == path
                 for col in [bpy.data.collections.get(j['collection'] or Path(j['id']).name)]
                 if col for o in col.all_objects}
        if not owned:
            owned = {o for j in jobs if j['source'] == path
                     for root in [bpy.data.objects.get(j['object'] or Path(j['id']).name)]
                     if root for o in root.children_recursive}
        added = [o for o in owned if o not in existing and o.type == 'MESH']
        directory = g.ROOT/'sources'/category/'textures/whisperwood'
        used = {s.material for o in bpy.data.objects if o.type == 'MESH' for s in o.material_slots if s.material}
        changed_materials = [m.name for m in sorted(used, key=lambda m: m.name) if grade_material(m, directory)]
        for obj in bpy.data.objects:
            if obj.type == 'MESH' and not obj.data.uv_layers:
                shaders = [next((n for n in s.material.node_tree.nodes if n.type == 'BSDF_PRINCIPLED'), None)
                           for s in obj.material_slots if s.material and s.material.use_nodes]
                if any(n and n.inputs['Base Color'].is_linked for n in shaders):
                    paint.project_uv(obj)
        assert armature_contract() == before_rig, 'Skeleton/clip interface changed: ' + path
        scene = bpy.context.scene
        scene['woodland_finish'] = TAG
        if args.growth_revision:
            scene['woodland_growth_revision'] = 1
        bpy.context.preferences.filepaths.save_version = 0
        bpy.ops.wm.save_as_mainfile(filepath=str(g.ROOT/path))
        authored['sources'][path] = {'sha256_before': baseline['files'][path]['sha256'], 'sha256_after': digest(g.ROOT/path),
                                    'ids': [j['id'] for j in jobs if j['source'] == path], 'graded_materials': changed_materials,
                                    'changed_landmarks': authored['sources'].get(path, {}).get('changed_landmarks', modified) if args.growth_revision else modified,
                                    'added_mesh_objects': authored['sources'].get(path, {}).get('added_mesh_objects', 0)+len(added),
                                    'rig_contract_preserved': True, 'growth_revision': int(args.growth_revision)}
        authored_path.write_text(json.dumps(authored, indent=2)+'\n')
        print('Authored', path, 'materials', len(changed_materials), 'added meshes', len(added), flush=True)


if __name__ == '__main__':
    main()
