"""Execute complete-inventory authoring and resume with a doubled Blender boundary."""
import contextlib
import importlib.util
import io
import json
import runpy
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

from tools.asset_catalog import export_sources
from tools.asset_pack import art_style
from tools.asset_pack.ambient_contract import ASSETS, sha

ROOT = Path(__file__).resolve().parents[2]
SCRIPT = ROOT / 'tools/asset_pack/ambient_motion.py'
SHARED = 'sources/environment/shared_forest_kit.blend'
SHARED_WATER = {
    'environment/components/forest_foam',
    'environment/components/forest_hex_stream',
    'environment/components/forest_waterfall',
}


class AmbientAuthoring(unittest.TestCase):
    def setUp(self):
        directory = tempfile.TemporaryDirectory(dir=ROOT)
        self.addCleanup(directory.cleanup)
        self.root = Path(directory.name)
        catalog = self.root / 'catalog/associations.json'
        catalog.parent.mkdir(parents=True)
        catalog.write_bytes((ROOT / 'catalog/associations.json').read_bytes())
        self.jobs = export_sources.plan_exports(ROOT, ASSETS)
        for source in {job['source'] for job in self.jobs}:
            path = self.root / source
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text('palette checkpoint: ' + source)
        self.docs = self.root / 'docs/ambient-motion'
        self.receipt = self.docs / 'authored.json'
        self.pending = []
        self.actions = types.SimpleNamespace(get=Mock(return_value=None), new=Mock(return_value=MagicMock()))
        self.wm = types.SimpleNamespace(
            open_mainfile=Mock(side_effect=self.open_source),
            save_as_mainfile=Mock(side_effect=self.save_source),
        )
        self.audit = types.ModuleType('tools.asset_pack.verify_ambient_blender')
        self.audit.capture = Mock(return_value={})
        self.audit.compare = Mock()
        self.modules = {
            'bpy': types.SimpleNamespace(
                data=types.SimpleNamespace(actions=self.actions),
                context=types.SimpleNamespace(scene=Mock(), view_layer=Mock()),
                ops=types.SimpleNamespace(wm=self.wm),
            ),
            'mathutils': types.SimpleNamespace(Matrix=Mock(), Vector=Mock()),
            'art_style': art_style,
            'geometry': types.ModuleType('geometry'),
            'hex_ground': types.ModuleType('hex_ground'),
            'painted_finish': types.ModuleType('painted_finish'),
            'vivid_refinement': types.SimpleNamespace(preserve_orphans=Mock(return_value=[])),
            'tools.asset_catalog.blender_selection': types.SimpleNamespace(asset_objects=Mock()),
            'tools.asset_pack.verify_ambient_blender': self.audit,
        }
        self.enterContext(patch.dict(sys.modules, self.modules))
        original_path = sys.path[:]
        self.addCleanup(lambda: sys.path.__setitem__(slice(None), original_path))
        spec = importlib.util.spec_from_file_location('ambient_authoring_under_test', SCRIPT)
        self.authoring = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(self.authoring)
        self.authoring.ROOT = self.root
        self.authoring.DOCS = self.docs
        self.authoring.building = Mock(side_effect=self.feature)
        self.authoring.water = Mock(side_effect=self.feature)

    def open_source(self, *, filepath):
        self.pending = json.loads(Path(filepath).read_text()) if Path(filepath).is_relative_to(
            self.root / '.cache/ambient-motion/saved') else []

    def save_source(self, *, filepath):
        Path(filepath).write_text(json.dumps(self.pending))

    def feature(self, job, action):
        self.pending.append(job['id'])
        return {'asset': job['id']}

    def run_authoring(self):
        with contextlib.redirect_stdout(io.StringIO()):
            self.authoring.main()

    def reset_calls(self):
        for mock in (self.wm.open_mainfile, self.wm.save_as_mainfile,
                     self.actions.new, self.audit.capture, self.audit.compare,
                     self.authoring.building, self.authoring.water):
            mock.reset_mock()

    def test_complete_inventory_including_all_shared_water_precedes_source_completion(self):
        self.run_authoring()
        receipts = json.loads(self.receipt.read_text())
        self.assertEqual(len(receipts), 23)
        self.assertEqual(self.authoring.building.call_count, 16)
        self.assertEqual(self.authoring.water.call_count, 9)
        self.assertEqual(self.wm.save_as_mainfile.call_count, 23)
        self.assertEqual(self.audit.compare.call_count, 23)
        self.assertEqual({f['asset'] for r in receipts.values() for f in r['features']}, set(ASSETS))
        self.assertEqual({f['asset'] for f in receipts[SHARED]['features']}, SHARED_WATER)
        self.assertEqual(set(json.loads((self.root / SHARED).read_text())), SHARED_WATER)
        for source, record in receipts.items():
            self.assertEqual(record['sha256_after'], sha(self.root / source))
            self.assertEqual(record['sha256_before'], sha(self.root / '.cache/ambient-motion/before' / source))
            self.assertTrue(record['preservation_verified_after_reload'])
            self.assertEqual(
                {f['asset'] for f in record['features']},
                {job['id'] for job in self.jobs if job['source'] == source},
            )

    def test_complete_run_resume_keeps_receipts_sources_and_checkpoints_unchanged(self):
        self.run_authoring()
        files = {p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}
        self.reset_calls()
        self.run_authoring()
        self.assertEqual({p: p.read_bytes() for p in self.root.rglob('*') if p.is_file()}, files)
        for mock in (self.wm.open_mainfile, self.wm.save_as_mainfile,
                     self.actions.new, self.audit.capture, self.audit.compare,
                     self.authoring.building, self.authoring.water):
            mock.assert_not_called()

    def test_interrupted_shared_source_is_not_receipted_and_resumes_all_water_features(self):
        def interrupt(job, action):
            if job['id'] == 'environment/components/forest_waterfall':
                raise RuntimeError('interrupted waterfall authoring')
            return self.feature(job, action)

        self.authoring.water.side_effect = interrupt
        with self.assertRaisesRegex(RuntimeError, 'interrupted waterfall'):
            self.run_authoring()
        completed = json.loads(self.receipt.read_text())
        self.assertNotIn(SHARED, completed)
        originals = {source: (self.root / source).read_bytes() for source in completed}
        self.authoring.water.side_effect = self.feature
        self.reset_calls()
        self.run_authoring()
        receipts = json.loads(self.receipt.read_text())
        self.assertEqual({f['asset'] for f in receipts[SHARED]['features']}, SHARED_WATER)
        self.assertEqual(set(json.loads((self.root / SHARED).read_text())), SHARED_WATER)
        self.assertEqual({f['asset'] for r in receipts.values() for f in r['features']}, set(ASSETS))
        for source, record in completed.items():
            self.assertEqual(receipts[source], record)
            self.assertEqual((self.root / source).read_bytes(), originals[source])
        reopened = {Path(c.kwargs['filepath']).relative_to(self.root).as_posix()
                    for c in self.wm.open_mainfile.call_args_list}
        self.assertTrue(set(completed).isdisjoint(reopened))

    def test_resume_refuses_subsequent_manual_source_edits(self):
        self.run_authoring()
        receipt = self.receipt.read_bytes()
        live = self.root / SHARED
        live.write_bytes(live.read_bytes() + b' manual edit')
        edited = live.read_bytes()
        self.reset_calls()
        with self.assertRaisesRegex(AssertionError, 'preserve subsequent manual edits'):
            self.run_authoring()
        self.assertEqual(self.receipt.read_bytes(), receipt)
        self.assertEqual(live.read_bytes(), edited)
        self.wm.open_mainfile.assert_not_called()
        self.wm.save_as_mainfile.assert_not_called()

    def test_python_entry_point_rejects_partial_inventory(self):
        with self.assertRaises(TypeError):
            self.authoring.main(['environment/components/forest_foam'])
        self.assertFalse(self.receipt.exists())

    def test_cli_help_and_selector_rejection_do_not_start_authoring(self):
        with patch.object(export_sources, 'plan_exports') as planner:
            for arguments, status in ((['--help'], 0),
                                      (['environment/components/forest_foam'], 2)):
                with self.subTest(arguments=arguments), patch.object(
                    sys, 'argv', [str(SCRIPT), '--', *arguments]
                ), contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
                    with self.assertRaises(SystemExit) as exit_status:
                        runpy.run_path(str(SCRIPT), run_name='__main__')
                    self.assertEqual(exit_status.exception.code, status)
            planner.assert_not_called()

    def test_cli_without_selector_plans_the_complete_inventory(self):
        with patch.object(export_sources, 'plan_exports', return_value=[]) as planner, patch.object(
            sys, 'argv', [str(SCRIPT), '--']
        ):
            runpy.run_path(str(SCRIPT), run_name='__main__')
        planner.assert_called_once_with(ROOT, ASSETS)
        self.wm.open_mainfile.assert_not_called()


if __name__ == '__main__':
    unittest.main()
