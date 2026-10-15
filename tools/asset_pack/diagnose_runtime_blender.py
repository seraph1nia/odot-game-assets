"""Independent source/raw-buffer/reimport counterfactual for the academy pilot.

Only writes task-local diagnosis evidence. No source saves or runtime overwrite.
"""
import json
import math
import struct
import sys
from collections import defaultdict
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
from mathutils import Matrix, Quaternion, Vector
from tools.asset_catalog.blender_selection import load_asset
from tools.asset_catalog.export_sources import plan_exports
from tools.asset_catalog.export_blender import _export_material_bindings
from tools.asset_pack.runtime_detail import export_detail
from tools.asset_pack.ambient_contract import sha

OUT=ROOT/'.cache/runtime-optimization/diagnosis'


def area(points):
    a,b,c=points
    ab=[b[i]-a[i] for i in range(3)]; ac=[c[i]-a[i] for i in range(3)]
    cross=(ab[1]*ac[2]-ab[2]*ac[1], ab[2]*ac[0]-ab[0]*ac[2], ab[0]*ac[1]-ab[1]*ac[0])
    return math.sqrt(sum(v*v for v in cross))/2


def collect(records, name, identity, indices, local, world):
    row=records[name]
    row['triangles']+=1
    ar=area(world)
    repeated_indices=len(set(indices))<3
    repeated_positions=len(set(tuple(p) for p in world))<3
    if ar == 0:
        row['exact_zero_area']+=1
        row['zero_triangles'].append({'identity':identity,'indices':list(indices),
            'repeated_indices':repeated_indices,'repeated_world_positions':repeated_positions,
            'local_positions':local,'transformed_positions':world,'transformed_area':ar})
    else:
        row['nonzero_triangles']+=1
        row['min_nonzero_area']=min(row['min_nonzero_area'],ar)


def records():
    return defaultdict(lambda:{'triangles':0,'exact_zero_area':0,'nonzero_triangles':0,'min_nonzero_area':float('inf'),'zero_triangles':[]})


def from_source(objects):
    result=records(); dg=bpy.context.evaluated_depsgraph_get()
    for obj in objects:
        if obj.type!='MESH': continue
        evaluated=obj.evaluated_get(dg);mesh=evaluated.to_mesh();mesh.calc_loop_triangles()
        for ti,tri in enumerate(mesh.loop_triangles):
            local=[list(mesh.vertices[i].co) for i in tri.vertices]
            world=[list(evaluated.matrix_world@Vector(p)) for p in local]
            mat=obj.material_slots[tri.material_index].material
            collect(result,mat.name,{'object':obj.name,'triangle':ti},list(tri.vertices),local,world)
        evaluated.to_mesh_clear()
    return dict(result)


def raw_glb(path):
    # Independent glTF accessor/transform reader: no runtime optimizer imports.
    data=path.read_bytes(); size=struct.unpack_from('<I',data,12)[0]
    doc=json.loads(data[20:20+size]);start=20+size
    length,kind=struct.unpack_from('<I4s',data,start);assert kind==b'BIN\0'
    binary=data[start+8:start+8+length]
    def values(index):
        a=doc['accessors'][index];v=doc['bufferViews'][a['bufferView']]
        width={'SCALAR':1,'VEC2':2,'VEC3':3,'VEC4':4}[a['type']]
        code,nbytes={5121:('B',1),5123:('H',2),5125:('I',4),5126:('f',4)}[a['componentType']]
        offset=v.get('byteOffset',0)+a.get('byteOffset',0);stride=v.get('byteStride',width*nbytes)
        return [struct.unpack_from('<'+code*width,binary,offset+i*stride) for i in range(a['count'])]
    result=records()
    def visit(index,parent):
        n=doc['nodes'][index]
        if 'matrix' in n:
            local=Matrix([n['matrix'][i:i+4] for i in range(0,16,4)]).transposed()
        else:
            x,y,z,w=n.get('rotation',(0,0,0,1))
            local=Matrix.LocRotScale(Vector(n.get('translation',(0,0,0))),Quaternion((w,x,y,z)),Vector(n.get('scale',(1,1,1))))
        transform=parent@local
        if 'mesh' in n:
            for pi,p in enumerate(doc['meshes'][n['mesh']]['primitives']):
                pos=values(p['attributes']['POSITION']);idx=[v[0] for v in values(p['indices'])]
                for i in range(0,len(idx),3):
                    indices=idx[i:i+3];points=[pos[j] for j in indices]
                    world=[list(transform@Vector(p)) for p in points]
                    collect(result,doc['materials'][p['material']]['name'],{'node':index,'name':n.get('name'),'primitive':pi,'triangle':i//3},indices,points,world)
        for child in n.get('children',[]):visit(child,transform)
    for root in doc['scenes'][doc.get('scene',0)]['nodes']:visit(root,Matrix.Identity(4))
    return dict(result)


def main():
    OUT.mkdir(parents=True,exist_ok=True)
    job=plan_exports(ROOT,['buildings/magic_academy'])[0]
    source_sha=sha(ROOT/job['source']);objects=load_asset(job,ROOT)
    detailed=from_source(objects)
    bpy.ops.object.select_all(action='DESELECT')
    for obj in objects:obj.select_set(True)
    bpy.context.view_layer.objects.active=objects[0]
    raw=OUT/'magic_academy-unmodified-export.glb'
    with _export_material_bindings(objects):
        bpy.ops.export_scene.gltf(filepath=str(raw),use_selection=True,export_animations=True,export_apply=True,
            export_extras=True,export_cameras=False,export_lights=False,export_yup=True,export_skins=True,export_animation_mode='ACTIONS')
    with export_detail(objects,job['id']) as profile:
        bpy.context.view_layer.update();simplified=from_source(objects)
        raw_runtime=OUT/'magic_academy-runtime-profile-unbatched.glb'
        with _export_material_bindings(objects):
            bpy.ops.export_scene.gltf(filepath=str(raw_runtime),use_selection=True,export_animations=True,export_apply=True,
                export_extras=True,export_cameras=False,export_lights=False,export_yup=True,export_skins=True,export_animation_mode='ACTIONS')
    report={'source_sha256':source_sha,'runtime_detail':profile,'stages':{'detailed_source':detailed,'runtime_profile_source':simplified}}
    paths={'baseline_landed':ROOT/'.cache/runtime-optimization/before/exports/buildings/magic_academy.glb',
           'optimized':OUT/'magic_academy-optimized.glb','unmodified_counterfactual':raw,'runtime_profile_unbatched':raw_runtime}
    for stage,path in paths.items():
        report['stages'][stage+'_buffers']=raw_glb(path)
        bpy.ops.wm.read_factory_settings(use_empty=True);bpy.ops.import_scene.gltf(filepath=str(path))
        report['stages'][stage+'_reimport']=from_source(bpy.context.scene.objects)
    assert sha(ROOT/job['source'])==source_sha
    # JSON infinity is not portable. Null denotes no nonzero triangles.
    for stage in report['stages'].values():
        for row in stage.values():
            if not math.isfinite(row['min_nonzero_area']):row['min_nonzero_area']=None
    (OUT/'triangle-diagnosis.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Independent raw-buffer and unmodified source counterfactual recorded',flush=True)


if __name__=='__main__':main()
