"""Audit actual optimized GLBs against unchanged evaluated sources and landed GLBs.

No rebuilds, .blend saves or texture float hashing. Source runtime bevel profile
is explicit; strict UV/normal/material comparisons remain independent of poses.
"""
import json
import sys
import tempfile
from collections import Counter, defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import numpy as np
from mathutils import Vector
from mathutils.kdtree import KDTree
from tools.asset_pack.export_normals_blender import canonical_array, condition_and_bound
from tools.asset_catalog.blender_selection import load_asset
from tools.asset_catalog.runtime_glb import read, accessor
from tools.asset_pack.ambient_contract import ASSETS, receipts, sha
from tools.asset_pack.encoded_images import png_proof
from tools.asset_pack.runtime_detail import export_detail
from tools.asset_pack.verify_ambient_blender import playback

DOCS = ROOT / 'docs/runtime-optimization'


def material_key(mat):
    return json.dumps({k: v for k, v in mat.items() if k != 'name'}, sort_keys=True)


def portable_contract(before, after):
    old, old_bin = read(before); new, new_bin = read(after)
    assert {material_key(m) for m in old['materials']} == {material_key(m) for m in new['materials']}, 'material/shader contract'
    assert old.get('textures') == new.get('textures') and old.get('samplers') == new.get('samplers'), 'texture/sampler bindings'
    images = []
    assert len(old.get('images', [])) == len(new.get('images', [])), 'image count'
    for a, b in zip(old.get('images', []), new.get('images', []), strict=True):
        def encoded(doc, binary, image):
            view = doc['bufferViews'][image['bufferView']]
            start = view.get('byteOffset', 0)
            return binary[start:start+view['byteLength']]
        assert {k:v for k,v in a.items() if k != 'bufferView'} == {k:v for k,v in b.items() if k != 'bufferView'}, 'image identity'
        source, target = encoded(old, old_bin, a), encoded(new, new_bin, b)
        assert source == target, ('encoded image bytes', a.get('name'))
        proof = png_proof(source)
        assert proof == png_proof(target), 'independent encoded samples/alpha'
        images.append({'name': a.get('name'), **proof})
    assert len(old['animations']) == len(new['animations']) == 1
    for a, b in zip(old['animations'], new['animations'], strict=True):
        assert a['name'] == b['name'] == 'ambient' and a['extras'] == b['extras'], 'clip name/loop extras'
        for x, y in zip(a['channels'], b['channels'], strict=True):
            assert x['target']['path'] == y['target']['path']
            assert old['nodes'][x['target']['node']]['name'] == new['nodes'][y['target']['node']]['name'], 'animated ownership'
        assert len(a['samplers']) == len(b['samplers'])
        for x, y in zip(a['samplers'], b['samplers'], strict=True):
            assert x.get('interpolation') == y.get('interpolation')
            for key in ('input', 'output'):
                assert accessor(old, old_bin, x[key]) == accessor(new, new_bin, y[key]), 'exact clip samples'
    return {'exact_material_contracts_and_texture_bindings': True,
            'exact_animation_targets_samples_and_loop_extras': True, 'encoded_image_proofs': images}


def samples(objects, keys, *, canonicalize=True):
    """Independent Blender evaluation of every triangle corner, not optimizer data."""
    bpy.context.view_layer.update(); dg = bpy.context.evaluated_depsgraph_get()
    records, triangles, exact_zero = defaultdict(list), Counter(), Counter()
    conversion={'max_transform_condition':0,'max_analytic_angular_bound_degrees':0,
                'max_local_rounding_world_component_delta':0,'max_local_rounding_world_angle_degrees':0}
    for obj in objects:
        if obj.type != 'MESH':
            continue
        evaluated = obj.evaluated_get(dg); mesh = evaluated.to_mesh()
        mesh.calc_loop_triangles()
        transform = evaluated.matrix_world
        normal = transform.to_3x3().inverted().transposed()
        condition,_,angle_bound=condition_and_bound(transform)
        conversion['max_transform_condition']=max(conversion['max_transform_condition'],condition)
        conversion['max_analytic_angular_bound_degrees']=max(conversion['max_analytic_angular_bound_degrees'],angle_bound)
        local_normals=np.empty((len(mesh.loops),3),dtype=np.float32)
        mesh.corner_normals.foreach_get('vector',local_normals.reshape(-1))
        encoded_normals=canonical_array(local_normals) if canonicalize else local_normals.copy()
        nmatrix=np.asarray(normal,dtype=np.float64)
        original_world=local_normals.astype(np.float64)@nmatrix.T
        encoded_world=encoded_normals.astype(np.float64)@nmatrix.T
        original_lengths=np.linalg.norm(original_world,axis=1,keepdims=True)
        encoded_lengths=np.linalg.norm(encoded_world,axis=1,keepdims=True)
        np.divide(original_world,original_lengths,out=original_world,where=original_lengths!=0)
        np.divide(encoded_world,encoded_lengths,out=encoded_world,where=encoded_lengths!=0)
        defined=original_lengths[:,0]>0
        if canonicalize and defined.any():
            delta=float(np.max(np.abs(original_world[defined]-encoded_world[defined])))
            angles=np.degrees(np.arccos(np.clip(np.sum(original_world[defined]*encoded_world[defined],axis=1),-1,1)))
            observed_angle=float(np.max(angles))
            assert observed_angle<=angle_bound+1e-5,'normal conversion exceeds analytical bound'
            conversion['max_local_rounding_world_component_delta']=max(conversion['max_local_rounding_world_component_delta'],delta)
            conversion['max_local_rounding_world_angle_degrees']=max(conversion['max_local_rounding_world_angle_degrees'],observed_angle)
        uv = next((layer for layer in mesh.uv_layers if layer.active_render), None)
        for tri in mesh.loop_triangles:
            mat = obj.material_slots[tri.material_index].material
            assert mat and mat.name in keys, ('unknown material', mat.name if mat else None)
            key = keys[mat.name]
            positions = [tuple(transform @ mesh.vertices[i].co) for i in tri.vertices]
            a,b,c = positions
            ab = tuple(b[i]-a[i] for i in range(3)); ac = tuple(c[i]-a[i] for i in range(3))
            cross = (ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0])
            if cross == (0,0,0):
                # Area is diagnostic only. Keep every corner/triangle in the
                # strict source-to-buffer check, including degenerate faces.
                exact_zero[key] += 1
            triangles[key] += 1
            corners = []
            for li in tri.loops:
                pos = transform @ mesh.vertices[mesh.loops[li].vertex_index].co
                n = (normal @ Vector(encoded_normals[li])).normalized()
                coord = tuple(uv.data[li].uv) if uv and key[1] else None
                corners.append((tuple(pos), tuple(n), coord))
            if transform.to_3x3().determinant() < 0:
                corners[1], corners[2] = corners[2], corners[1]
            records[key].append(tuple(corners))
        evaluated.to_mesh_clear()
    return records, triangles, exact_zero, conversion


def compare_samples(before, after, *, normals=True):
    a, counts_a = before[:2]; b, counts_b = after[:2]
    assert counts_a == counts_b, ('per-material triangle multiplicity',
        {k: (counts_a.get(k,0), counts_b.get(k,0)) for k in counts_a.keys() | counts_b.keys() if counts_a.get(k,0) != counts_b.get(k,0)})
    assert set(a) == set(b) == set(counts_a), 'source material ownership differs'
    max_position, max_normal, max_uv = 0, 0, 0
    def center(triangle):
        return tuple(sum(c[0][axis] for c in triangle)/3 for axis in range(3))
    for key, left in a.items():
        right = b[key]
        assert len(left) == len(right) == counts_a[key], ('source triangle records', key)
        tree = KDTree(len(right))
        for i, triangle in enumerate(right): tree.insert(center(triangle), i)
        tree.balance()
        available = set(range(len(right)))
        for triangle in left:
            assert len(triangle) == 3, 'incomplete source triangle'
            found = None
            for _, i, _ in tree.find_range(center(triangle), 3e-5):
                if i not in available:
                    continue
                candidate = right[i]
                assert len(candidate) == 3, 'incomplete target triangle'
                for rotation in range(3):
                    errors = []
                    for corner, (pos, normal, uv) in enumerate(triangle):
                        p, n, u = candidate[(corner+rotation)%3]
                        pe = (Vector(pos)-Vector(p)).length
                        ne = max(abs(x-y) for x,y in zip(normal,n,strict=True))
                        ue = max((abs(x-y) for x,y in zip(uv,u,strict=True)),default=0) if uv is not None and u is not None else (0 if uv == u else 1)
                        if pe >= 2e-5 or (normals and ne >= .00002) or ue >= .00002:
                            break
                        errors.append((pe, ne, ue))
                    if len(errors) == 3:
                        found = (i, errors)
                        break
                if found is not None:
                    break
            assert found is not None, ('source triangle connectivity/winding/attribute mismatch', key, triangle)
            available.remove(found[0])
            for pe, ne, ue in found[1]:
                max_position = max(max_position,pe); max_normal = max(max_normal,ne); max_uv = max(max_uv,ue)
        assert not available, 'unexpected target triangles'
    return {'all_triangle_corners_checked_bidirectionally': True,
            'one_to_one_source_triangle_connectivity_winding_equal': True,
            'source_triangle_count': sum(counts_a.values()),
            'exact_zero_area_source_triangles': sum(before[2].values()) if len(before) >= 3 else 0,
            'exact_zero_area_imported_triangles': sum(after[2].values()) if len(after) >= 3 else 0,
            'per_material_triangle_multiplicity_equal': True,
            'normals_asserted': normals,
            'max_position_error_m': max_position,'max_normal_component_error': max_normal,'max_uv_error': max_uv}


def textured(value):
    return isinstance(value,dict) and any((k.endswith('Texture') and isinstance(v,dict) and 'index' in v) or textured(v) for k,v in value.items())


def material_keys(doc):
    return {m['name']:(material_key(m),textured(m)) for m in doc['materials']}


def serialized_samples(path):
    from tools.asset_pack.runtime_surfaces_blender import triangles
    records,counts,exact_zero=defaultdict(list),Counter(),Counter()
    for (material,names),faces in triangles(path).items():
        key=(material,textured(json.loads(material)))
        pi,ni=names.index('POSITION'),names.index('NORMAL')
        ui=names.index('TEXCOORD_0') if 'TEXCOORD_0' in names else None
        for face in faces:
            a,b,c=(corner[pi] for corner in face)
            ab=tuple(b[i]-a[i] for i in range(3));ac=tuple(c[i]-a[i] for i in range(3))
            cross=(ab[1]*ac[2]-ab[2]*ac[1],ab[2]*ac[0]-ab[0]*ac[2],ab[0]*ac[1]-ab[1]*ac[0])
            if cross==(0,0,0):exact_zero[key]+=1
            counts[key]+=1
            corners=[]
            for corner in face:
                uv=(corner[ui][0],1-corner[ui][1]) if ui is not None and key[1] else None
                corners.append((corner[pi],corner[ni],uv))
            records[key].append(tuple(corners))
    return records,counts,exact_zero


def fidelity(job, baseline, exported, raw):
    old,_=read(baseline);new,_=read(exported)
    objects=load_asset(job,ROOT)
    with export_detail(objects,job['id']) as count:
        bpy.context.view_layer.update()
        source=samples(objects,material_keys(old))
    raw_check=compare_samples(source,serialized_samples(raw))
    exported_check=compare_samples(source,serialized_samples(exported))
    bpy.ops.wm.read_factory_settings(use_empty=True)
    bpy.ops.import_scene.gltf(filepath=str(exported))
    imported=samples(bpy.context.scene.objects,material_keys(new),canonicalize=False)
    # Blender stores imported split normals in its own quantized corner-normal
    # representation. The unmodified baseline counterfactual already differs by
    # up to 0.01135 in a component; do not weaken actual GLB normal assertions to
    # accommodate that representation. Check real serialized floats strictly
    # above, and use reimport only for geometry/UVs plus a normal diagnostic.
    return {'runtime_detail':count,'source_normal_conversion':source[3],
            'source_to_raw_buffers':raw_check,
            'source_to_exported_buffers':exported_check,
            'reimport':compare_samples(source,imported,normals=False)}


def audit_asset(aid, baseline, features):
    item = baseline['assets'][aid]; job = item['job']
    assert sha(ROOT/job['source']) == baseline['sources'][job['source']], 'editable source bytes changed'
    before = ROOT/'.cache/runtime-optimization/before/exports'/(aid+'.glb')
    assert sha(before) == item['facts']['version'], 'stale baseline export'
    after = ROOT/'exports'/(aid+'.glb')
    from tools.asset_pack.runtime_surfaces_blender import triangles, compare as compare_serialized
    raw = ROOT/'.cache/runtime-optimization/unbatched'/(aid+'.glb')
    serialized = compare_serialized(triangles(raw),triangles(after))
    result = {'source_sha256':sha(ROOT/job['source']),'glb_sha256':sha(after),
              'unbatched_runtime_profile_sha256':sha(raw), 'serialized_surfaces':serialized,
              **portable_contract(before,after), **fidelity(job,before,after,raw)}
    result['playback'] = playback(job,features[aid])
    return result


def main():
    baseline = json.loads((DOCS/'baseline.json').read_text())
    features = {f['asset']:f for r in receipts(ROOT).values() for f in r['features']}
    target = DOCS/'validation.json'
    report = json.loads(target.read_text()) if target.exists() else {'assets':{}}
    report['scope'] = 'Every source and serialized transformed triangle matched one-to-one with connectivity, winding, multiplicity and corner attributes (including exact zero-area faces); strict source-to-GLB position/UV/normal floats without area filtering; Blender reimport geometry/UVs and diagnostic normals; all25 source/export loops; exact landed materials/images/clip samples. No game-renderer/FPS qualification.'
    selected = (sys.argv[sys.argv.index('--')+1:] if '--' in sys.argv else []) or ASSETS
    for aid in selected:
        report['assets'][aid] = audit_asset(aid, baseline, features)
        print('Runtime fidelity and loop verified:',aid,flush=True)
    with tempfile.NamedTemporaryFile(mode='w', dir=DOCS, prefix='.validation-', suffix='.json', delete=False) as stream:
        temporary = Path(stream.name)
        try:
            stream.write(json.dumps(report,indent=2)+'\n')
            stream.close()
            temporary.replace(target)
        finally:
            temporary.unlink(missing_ok=True)


if __name__ == '__main__': main()
