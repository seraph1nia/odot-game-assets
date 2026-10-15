"""Real Blender runtime-detail fixtures, including restoration and a GLB round trip."""
from copy import deepcopy
import json
import sys
import tempfile
import unittest
from unittest import mock
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import geometry as g
from tools.asset_pack.runtime_detail import export_detail
from tools.asset_catalog.runtime_glb import optimize, read
from tools.asset_catalog.export_blender import _export_material_bindings
from tools.asset_pack.verify_runtime_blender import compare_samples, material_keys, samples, serialized_samples


class RuntimeFixtures(unittest.TestCase):
    def setUp(self):
        bpy.ops.wm.read_factory_settings(use_empty=True)
        self.col = bpy.data.collections.new('fixture'); bpy.context.scene.collection.children.link(self.col)
        g.target(self.col); g.material('fixture_green',(.2,.5,.1))
        self.moss = g.ico('Woodland shared moss cushion',(0,0,0),(.095,.075,.04),'fixture_green',2,0)
        self.other = self.moss.copy(); self.col.objects.link(self.other); self.other.location.x = .2
        self.hero = self.moss.copy(); self.hero.name = 'Signature crystal'; self.col.objects.link(self.hero); self.hero.location.y = .3
        self.fine = g.cube('Fine border',(0,0,0),(.2,.02,.02),'fixture_green',.003)
        self.large = g.cube('Broad structural bevel',(0,0,0),(.3,.3,.3),'fixture_green',.025)
        self.objects = list(self.col.objects)
        bpy.context.view_layer.update()

    def test_shared_moss_simplifies_only_in_export_and_every_binding_restores(self):
        original = self.moss.data
        self.assertEqual(len(original.polygons),80)
        for fail in (False,True):
            try:
                with export_detail(self.objects,'buildings/weaver') as report:
                    self.assertEqual(report,{'tiny_bevels':1,'moss_instances':2,'moss_mesh_variants':1})
                    self.assertIs(self.moss.data,self.other.data)
                    self.assertIsNot(self.moss.data,original)
                    self.assertEqual(len(self.moss.data.polygons),40)
                    self.assertIs(self.hero.data,original)
                    self.assertEqual(self.fine.modifiers[0].segments,1)
                    self.assertEqual(self.large.modifiers[0].segments,2)
                    if fail: raise RuntimeError('injected serializer failure')
            except RuntimeError:
                self.assertTrue(fail)
            self.assertIs(self.moss.data,original); self.assertIs(self.other.data,original)
            self.assertEqual(self.fine.modifiers[0].segments,2)
            self.assertEqual(len(bpy.data.meshes),3)

    def test_unapproved_asset_and_scaled_up_moss_stay_detailed(self):
        original = self.moss.data
        with export_detail(self.objects,'characters/knight') as report:
            self.assertEqual(report['moss_instances'],0); self.assertIs(self.moss.data,original)
        self.moss.scale = (5,5,5); self.other.scale = (5,5,5); bpy.context.view_layer.update()
        with export_detail(self.objects,'buildings/weaver') as report:
            self.assertEqual(report['moss_instances'],0); self.assertIs(self.moss.data,original)

    def test_actual_export_consolidates_and_source_bindings_survive(self):
        self.hero.scale.x *= -1
        root = bpy.data.objects.new('weaver_root',None); self.col.objects.link(root)
        for obj in self.objects: obj.parent=root
        original = self.moss.data
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'fixture.glb'
            bpy.ops.object.select_all(action='SELECT')
            with _export_material_bindings(self.objects),export_detail(self.objects,'buildings/weaver'):
                bpy.ops.export_scene.gltf(filepath=str(p),use_selection=True,export_apply=True)
                doc,_=read(p)
                source=samples(self.objects,material_keys(doc))
            raw=serialized_samples(p)
            self.assertTrue(compare_samples(source,raw)['one_to_one_source_triangle_connectivity_winding_equal'])
            optimize(p,'buildings/weaver')
            doc,_=read(p)
            self.assertEqual(len(doc['meshes']),1)
            self.assertTrue(compare_samples(source,serialized_samples(p))['one_to_one_source_triangle_connectivity_winding_equal'])
            self.assertIs(self.moss.data,original)
            bpy.ops.wm.read_factory_settings(use_empty=True)
            bpy.ops.import_scene.gltf(filepath=str(p))
            self.assertEqual(len([o for o in bpy.context.scene.objects if o.type=='MESH']),1)
            imported=samples(bpy.context.scene.objects,material_keys(doc),canonicalize=False)
            self.assertTrue(compare_samples(source,imported,normals=False)['one_to_one_source_triangle_connectivity_winding_equal'])

    def test_serialized_surface_check_rejects_real_triangle_attribute_and_binding_loss(self):
        from tools.asset_pack.runtime_surfaces_blender import compare
        key=('painted material',('NORMAL','POSITION','TEXCOORD_0'))
        triangle=(((0,0,1),(0,0,0),(.1,.2)),((0,0,1),(1,0,0),(.3,.2)),((0,0,1),(0,1,0),(.1,.4)))
        source={key:[triangle,triangle]}  # legitimate coincident faces retain multiplicity
        self.assertEqual(compare(source,source)['serialized_triangle_count'],2)
        with self.assertRaises(AssertionError):compare(source,{key:[triangle]})
        with self.assertRaises(AssertionError):compare(source,{('wrong material',key[1]):[triangle,triangle]})
        for ai,component in ((0,0),(1,0),(2,0)):
            altered=deepcopy(source)
            face=[list(v) for v in triangle]
            value=list(face[0][ai]);value[component]+=.05;face[0][ai]=tuple(value)
            altered[key][0]=tuple(tuple(v) for v in face)
            with self.assertRaises(AssertionError):compare(source,altered)
        # A genuinely nonzero tiny triangle must not be area-thresholded away.
        tiny=tuple((n,tuple(v*1e-8 for v in p),uv) for n,p,uv in triangle)
        proof=compare({key:[tiny]},{key:[tiny]})
        self.assertEqual(proof['serialized_triangle_count'],1)
        self.assertEqual(proof['exact_zero_area_before'],0)

    def test_actual_glb_normal_rounding_and_transform_counterfactual(self):
        from tools.asset_pack.diagnose_normal_quantization_blender import verify
        result=verify()
        self.assertTrue(result['perturbed_normal_control_rejected'])
        self.assertTrue(result['condition_1e6_control_rejected'])
        self.assertLess(max(r['canonical_max_component_error'] for r in result['unchanged_exporter_counterfactual']),.000001)
        self.assertGreater(max(r['unconverted_max_component_error'] for r in result['unchanged_exporter_counterfactual']),.001)

    def test_known_export_normal_rounding_has_a_bound_not_an_error_allowance(self):
        from mathutils import Matrix, Vector
        from tools.asset_pack.export_normals_blender import canonical, condition_and_bound
        local=Vector((.000049,.000049,1)).normalized()
        transform=Matrix.Diagonal((1,.03125,1,1))
        normal=transform.to_3x3().inverted().transposed()
        original=(normal@local).normalized();converted=(normal@canonical(local)).normalized()
        condition,chord,_=condition_and_bound(transform)
        self.assertAlmostEqual(condition,32)
        self.assertGreater((original-converted).length,.001)
        self.assertLess((original-converted).length,chord)
        self.assertEqual(tuple(canonical((0,0,0))),(0,0,1))
        with self.assertRaises(ValueError):condition_and_bound(Matrix.Diagonal((1,1,1e-6,1)))

    def test_fidelity_check_rejects_normal_uv_position_and_material_changes(self):
        key=('painted contract',True)
        triangle=(((0,0,0),(0,0,1),(.2,.3)),((1,0,0),(0,0,1),(.4,.3)),((0,1,0),(0,0,1),(.2,.5)))
        source=({key:[triangle]},{key:1})
        self.assertTrue(compare_samples(source,source)['all_triangle_corners_checked_bidirectionally'])
        for attribute, width in ((0,3),(1,3),(2,2)):
            for axis in range(width):
                face=deepcopy([list(c) for c in triangle])
                value=list(face[0][attribute]);value[axis]+=.01;face[0][attribute]=tuple(value)
                altered=({key:[tuple(tuple(c) for c in face)]},{key:1})
                with self.assertRaises(AssertionError): compare_samples(source,altered)
                if attribute == 1:
                    self.assertFalse(compare_samples(source,altered,normals=False)['normals_asserted'])
                else:
                    with self.assertRaises(AssertionError): compare_samples(source,altered,normals=False)
        with self.assertRaises(AssertionError): compare_samples(source,({'different material':source[0][key]},{'different material':1}))

    def test_source_triangles_reject_same_count_connectivity_winding_and_multiplicity_changes(self):
        key=('painted contract',True)
        a,b,c,d=tuple((p,(0,0,1),(.2,.3)) for p in ((0,0,0),(1,0,0),(1,1,.3),(0,1,0)))
        def records(faces): return ({key:faces},{key:len(faces)})
        source=records([(a,b,c),(a,c,d)])
        rotated=records([(c,d,a),(b,c,a)])
        self.assertEqual(compare_samples(source,rotated)['source_triangle_count'],2)
        for original, changed in (
                (source,records([(a,b,d),(b,c,d)])),
                (source,records([(a,c,b),(a,c,d)])),
                (records([(a,b,c),(a,b,c),(a,c,d)]),records([(a,b,c),(a,c,d),(a,c,d)])),
                (records([(a,a,b)]),records([(a,b,b)])),
                (source,records([(a,b,c)]))):
            for normals in (True,False):
                with self.assertRaises(AssertionError): compare_samples(original,changed,normals=normals)
        tiny=tuple((tuple(v*1e-8 for v in p),n,u) for p,n,u in (a,b,c))
        self.assertEqual(compare_samples(records([tiny,tiny,(a,a,b)]),records([tiny,tiny,(a,a,b)]))['source_triangle_count'],3)

    def test_runtime_playback_profiles_real_source_and_rejects_changed_pose(self):
        from tools.asset_pack import verify_ambient_blender as ambient
        from tools.asset_catalog.runtime_glb import accessor, write
        import struct
        from tools.asset_pack.art_style import AMBIENT
        for frame, x in zip(AMBIENT.frames,(0,.01,0,-.01,0),strict=True):
            self.moss.location.x=x
            self.moss.keyframe_insert(data_path='location',frame=frame)
        self.moss.animation_data.action.name='ambient'
        bpy.context.scene.frame_set(1)
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);path=root/'exports/buildings/weaver.glb';path.parent.mkdir(parents=True)
            bpy.ops.wm.save_as_mainfile(filepath=str(root/'fixture.blend'))
            bpy.ops.object.select_all(action='SELECT')
            with _export_material_bindings(self.objects),export_detail(self.objects,'buildings/weaver'):
                bpy.ops.export_scene.gltf(filepath=str(path),use_selection=True,export_apply=True,export_animations=True,export_animation_mode='ACTIONS')
            job={'id':'buildings/weaver','source':'fixture.blend','collection':'fixture','object':None}
            feature={'channels':[{'object':self.moss.name}]}
            with mock.patch.object(ambient,'ROOT',root):
                result=ambient.playback(job,feature)
                self.assertLess(result['evaluated_pose_point_cloud_max_error_m'],.0001)
                doc,binary=read(path);altered=bytearray(binary)
                channel=next(c for c in doc['animations'][0]['channels'] if c['target']['path']=='translation')
                output=doc['animations'][0]['samplers'][channel['sampler']]['output']
                acc=doc['accessors'][output];view=doc['bufferViews'][acc['bufferView']]
                start=view.get('byteOffset',0)+acc.get('byteOffset',0)
                for i,value in enumerate(accessor(doc,binary,output)):
                    struct.pack_into('<3f',altered,start+i*view.get('byteStride',12),value[0]+.01,*value[1:])
                write(path,doc,altered)
                with self.assertRaisesRegex(AssertionError,'0.1mm'): ambient.playback(job,feature)

    def test_standalone_ambient_entry_publishes_runtime_successor_without_losing_records(self):
        from tools.asset_pack import verify_ambient_blender as ambient, verify_runtime_blender as runtime
        old={'assets':{'selected':{'glb_sha256':'old'},'unselected':{'glb_sha256':'keep','source_sha256':'keep-source'}}}
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder);docs=root/'docs/runtime-optimization';docs.mkdir(parents=True)
            target=docs/'validation.json'
            (docs/'baseline.json').write_text('{}')
            target.write_text(json.dumps(old))
            historical=root/'docs/ambient-motion/validation.json';historical.parent.mkdir()
            historical.write_bytes(b'immutable historical receipt')
            with mock.patch.object(ambient,'ROOT',root),mock.patch.object(runtime,'ROOT',root),mock.patch.object(runtime,'DOCS',docs),mock.patch.object(runtime,'receipts',return_value={}),mock.patch.object(runtime,'audit_asset',return_value={'glb_sha256':'new'}) as audit,mock.patch.object(sys,'argv',['verify_ambient_blender.py','--','selected']):
                ambient.main()
            audit.assert_called_once_with('selected',{}, {})
            report=json.loads(target.read_text())
            self.assertEqual(report['assets'],{'selected':{'glb_sha256':'new'},'unselected':old['assets']['unselected']})
            self.assertEqual(historical.read_bytes(),b'immutable historical receipt')

    def test_failed_interrupted_and_unpublishable_audits_leave_ledger_unchanged(self):
        from tools.asset_pack import verify_runtime_blender as runtime
        original=b'{"assets":{"first":{"glb_sha256":"good"},"other":{"glb_sha256":"preserved"}}}\n'
        with tempfile.TemporaryDirectory() as folder:
            docs=Path(folder);target=docs/'validation.json';target.write_bytes(original)
            (docs/'baseline.json').write_text('{}')
            with mock.patch.object(runtime,'DOCS',docs),mock.patch.object(runtime,'receipts',return_value={}):
                for error in (AssertionError('bad second asset'),KeyboardInterrupt()):
                    for args in (['--','first','second'],[]):
                        with mock.patch.object(sys,'argv',['verify_runtime_blender.py',*args]),mock.patch.object(runtime,'ASSETS',('first','second')),mock.patch.object(runtime,'audit_asset',side_effect=[{'glb_sha256':'new'},error]):
                            with self.assertRaises(type(error)): runtime.main()
                        self.assertEqual(target.read_bytes(),original)
                with mock.patch.object(sys,'argv',['verify_runtime_blender.py','--','first']),mock.patch.object(runtime,'audit_asset',return_value={'glb_sha256':'new'}),mock.patch.object(Path,'replace',side_effect=OSError('cannot publish')):
                    with self.assertRaises(OSError): runtime.main()
                self.assertEqual(target.read_bytes(),original)
                self.assertEqual(sorted(p.name for p in docs.iterdir()),['baseline.json','validation.json'])


if __name__=='__main__': unittest.main(argv=[sys.argv[0]])
