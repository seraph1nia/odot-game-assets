"""Real Blender runtime-detail fixtures, including restoration and a GLB round trip."""
from copy import deepcopy
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT)); sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import geometry as g
from tools.asset_pack.runtime_detail import export_detail
from tools.asset_catalog.runtime_glb import optimize, read
from tools.asset_catalog.export_blender import _export_material_bindings
from tools.asset_pack.verify_runtime_blender import compare_samples


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
        root = bpy.data.objects.new('weaver_root',None); self.col.objects.link(root)
        for obj in self.objects: obj.parent=root
        original = self.moss.data
        with tempfile.TemporaryDirectory() as folder:
            p=Path(folder)/'fixture.glb'
            bpy.ops.object.select_all(action='SELECT')
            with _export_material_bindings(self.objects),export_detail(self.objects,'buildings/weaver'):
                bpy.ops.export_scene.gltf(filepath=str(p),use_selection=True,export_apply=True)
            optimize(p,'buildings/weaver')
            doc,_=read(p)
            self.assertEqual(len(doc['meshes']),1)
            self.assertIs(self.moss.data,original)
            bpy.ops.wm.read_factory_settings(use_empty=True)
            bpy.ops.import_scene.gltf(filepath=str(p))
            self.assertEqual(len([o for o in bpy.context.scene.objects if o.type=='MESH']),1)

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
        source=({key:{((0,0,0),(0,0,1),(.2,.3))}},{key:1})
        self.assertTrue(compare_samples(source,source)['all_triangle_corners_checked_bidirectionally'])
        for value in (((.01,0,0),(0,0,1),(.2,.3)),((0,0,0),(0,1,0),(.2,.3)),((0,0,0),(0,0,1),(.4,.3))):
            with self.assertRaises(AssertionError): compare_samples(source,({key:{value}},{key:1}))
        with self.assertRaises(AssertionError): compare_samples(source,({'different material':source[0][key]},{'different material':1}))


if __name__=='__main__': unittest.main(argv=[sys.argv[0]])
