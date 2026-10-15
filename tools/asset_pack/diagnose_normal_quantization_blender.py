"""Minimal actual glTF export counterfactual for local normal rounding + scale.

Uses unrelated synthetic normals, transforms through condition 64 (and mirrored
winding), and controls below the worst-case analytical rounding envelope. No
source or production export is opened/saved/modified.
"""
import json
import math
import sys
import tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
import bpy
from mathutils import Vector
from tools.asset_catalog.runtime_glb import read, accessor
from tools.asset_pack.export_normals_blender import canonical, condition_and_bound, LOCAL_VECTOR_ERROR
from tools.asset_pack.runtime_surfaces_blender import triangles, compare


def verify():
    bpy.ops.wm.read_factory_settings(use_empty=True)
    mat=bpy.data.materials.new('Normal synthetic painted material');mat.use_nodes=True
    objects=[]
    for i,scale in enumerate(((1,1,1),(1,.25,2),(1,.1,3.2),(-1,.5,2),(1,.125,8),(1,.03125,1))):
        mesh=bpy.data.meshes.new('normal probe')
        # The last probe lies near a four-decimal quantizer cell boundary.
        # Geometric face normals avoid Blender custom-normal storage rounding
        # and independently expose local rounding before nonuniform scale.
        n=Vector((.000049,.000049,1) if i==5 else (.412345+i*.017,.678912-i*.031,.607219+i*.009)).normalized()
        mesh.from_pydata([(0,0,0),(1,0,-n.x/n.z),(0,1,-n.y/n.z)],[],[(0,1,2)])
        mesh.materials.append(mat);mesh.polygons[0].use_smooth=True
        mesh.update()
        obj=bpy.data.objects.new('Independent normal probe '+str(i),mesh)
        bpy.context.scene.collection.objects.link(obj);obj.location.x=i*5;obj.scale=scale
        obj.rotation_euler=(.31,.72,-.21);obj.select_set(True);objects.append(obj)
    bpy.context.view_layer.update()
    bpy.context.view_layer.objects.active=objects[0]
    with tempfile.TemporaryDirectory(dir=ROOT/'.cache') as folder:
        path=Path(folder)/'normal-probe.glb'
        bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_apply=True,export_animations=False)
        doc,binary=read(path)
        # Encoding is real float32, not normalized 8/16-bit accessors.
        accessors=[doc['accessors'][p['attributes']['NORMAL']] for m in doc['meshes'] for p in m['primitives']]
        assert all(a['componentType']==5126 and not a.get('normalized',False) for a in accessors)
        data=triangles(path);faces=[tri for values in data.values() for tri in values];report=[]
        for obj in objects:
            local=obj.data.corner_normals[0].vector.copy()
            normal=obj.matrix_world.to_3x3().inverted().transposed()
            plain=(normal@local).normalized();expected=(normal@canonical(local)).normalized()
            origin=tuple(obj.matrix_world@obj.data.vertices[0].co)
            candidates=[corner for tri in faces for corner in tri if (Vector(corner[1])-Vector(origin)).length<1e-5]
            # names from triangles() are ('NORMAL','POSITION') for this fixture.
            observed=min((Vector(c[0]) for c in candidates),key=lambda n:(n-expected).length)
            error=max(abs(a-b) for a,b in zip(observed,expected))
            assert error<2e-5,('canonical normal prediction',obj.name,error)
            condition,chord,angle=condition_and_bound(obj.matrix_world)
            actual_chord=(plain-expected).length
            assert actual_chord<=chord+1e-6
            actual_angle=math.degrees(math.atan2(plain.cross(observed).length,plain.dot(observed)))
            report.append({'object':obj.name,'scale':list(obj.scale),'condition':condition,
                'local_source_corner_normal':list(local),'predicted_export_world_normal':list(expected),
                'actual_export_world_normal':list(observed),'canonical_max_component_error':error,
                'unconverted_max_component_error':max(abs(a-b) for a,b in zip(plain,observed)),
                'rounding_chord':actual_chord,'rounding_angle_degrees':actual_angle,
                'analytic_chord_bound':chord,'analytic_angular_bound_degrees':angle})
        assert max(r['unconverted_max_component_error'] for r in report)>2e-5, 'probe must distinguish rounding from no rounding'
        # Control: change a real encoded normal by 0.001 -- below the conservative
        # high-condition original-rounding envelope, but rejected by fixed actual
        # accessor equivalence. UV/material/geometry controls live in fixtures.
        original=triangles(path)
        normal_index=doc['meshes'][0]['primitives'][0]['attributes']['NORMAL']
        values=accessor(doc,binary,normal_index);a=doc['accessors'][normal_index]
        view=doc['bufferViews'][a['bufferView']];offset=view.get('byteOffset',0)+a.get('byteOffset',0)
        import struct
        wrong=Vector(values[0]);wrong.x+=.001;wrong.normalize()
        altered=bytearray(binary);struct.pack_into('<3f',altered,offset,*wrong)
        from tools.asset_catalog.runtime_glb import write
        write(path,doc,altered)
        rejected=False
        try:compare(original,triangles(path))
        except AssertionError:rejected=True
        assert rejected,'materially changed encoded normal was accepted'
        try:condition_and_bound(__import__('mathutils').Matrix.Diagonal((1,1,1e-6,1)))
        except ValueError:pass
        else:raise AssertionError('ill-conditioned transform accepted')
        result={'local_rounding_digits':4,'local_vector_error_bound':LOCAL_VECTOR_ERROR,
            'normal_encoding':'FLOAT 5126, normalized false','unchanged_exporter_counterfactual':report,
            'perturbed_normal_control_rejected':rejected,'condition_1e6_control_rejected':True,
            'fixed_serialized_comparison_tolerance':.00002}
    return result


def main():
    result=verify()
    target=ROOT/'docs/runtime-optimization/diagnosis/normal-quantization.json'
    target.write_text(json.dumps(result,indent=2)+'\n')
    print('Independent normal rounding/transform counterfactual passed',flush=True)


if __name__=='__main__':main()
