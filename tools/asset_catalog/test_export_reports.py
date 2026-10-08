"""Selected-export report behavior with serialized GLBs and stubbed Blender calls."""
import importlib.util
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from .index import CatalogIndex, write_json
from .metadata import read_glb

ROOT = Path(__file__).resolve().parents[2]
CASES = [('characters/evil_ranged_unit', 90, 92), ('props/crossbow', 10, 12)]


class ExportReportTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        obj = Mock(name='selected mesh', type='MESH', modifiers=[],
                   instance_collection=None, animation_data=None)
        obj.name = 'fixture'
        obj.get.return_value = None
        self.bpy = Mock()
        self.selection = SimpleNamespace(load_asset=Mock(return_value=[obj]))
        spec = importlib.util.spec_from_file_location(
            '_export_report_fixture', Path(__file__).with_name('export_blender.py'))
        self.exporter = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules', {'bpy': self.bpy,
                                       'tools.asset_catalog.blender_selection': self.selection}):
            spec.loader.exec_module(self.exporter)

    def test_selected_export_refreshes_existing_and_new_reports_from_serialized_glbs(self):
        for asset_id, stale, expected in CASES:
            for existing in (True, False):
                with self.subTest(asset_id=asset_id, existing=existing):
                    key = 'exports/' + asset_id + '.glb'
                    source = 'sources/' + asset_id + '.blend'
                    source_path = self.root / source
                    source_path.parent.mkdir(parents=True, exist_ok=True)
                    source_path.write_bytes(b'authored source fixture')
                    payload = (ROOT / key).read_bytes()
                    previous = {'file': key, 'meshes': stale, 'source': source,
                                'title': 'Authored title', 'animation_policy': {'idle': True}}
                    untouched = {'file': 'exports/props/unselected.glb', 'meshes': 37}
                    write_json(self.root / 'exports/asset_manifest.json', {
                        'fps': 24, 'assets': [previous, untouched] if existing else [untouched]})

                    def serialize(**options):
                        Path(options['filepath']).write_bytes(payload)
                        return {'FINISHED'}

                    self.bpy.ops.export_scene.gltf.side_effect = serialize
                    with patch.object(self.exporter.sys, 'argv', [
                            'blender', '--', '--root', str(self.root), asset_id]), \
                            redirect_stdout(io.StringIO()):
                        self.exporter.main()
                    manifest = json.loads((self.root / 'exports/asset_manifest.json').read_text())
                    reports = {entry['file']: entry for entry in manifest['assets']}
                    facts = read_glb(self.root / key)
                    self.assertEqual(facts['meshes'], expected)
                    self.assertEqual(reports[key], (previous if existing else {}) | {
                        'file': key, 'bytes': facts['bytes'], 'meshes': expected,
                        'triangles': facts['triangles'], 'materials': facts['materials'],
                        'animations': [clip['name'] for clip in facts['animations']],
                        'source': source})
                    self.assertEqual(reports[untouched['file']], untouched)
                    self.assertEqual(manifest['fps'], 24)
                    self.assertEqual((self.root / key).read_bytes(), payload)
                    self.assertEqual(source_path.read_bytes(), b'authored source fixture')
                    catalog = CatalogIndex(self.root).build()
                    asset = next(entry for entry in catalog['assets'] if entry['id'] == asset_id)
                    self.assertEqual(asset['meshes'], expected)
                    self.assertEqual(list((self.root / '.cache').iterdir()), [])

    def test_published_mesh_counts_match_serialized_glbs(self):
        manifest = json.loads((ROOT / 'exports/asset_manifest.json').read_text())
        reports = {entry['file']: entry for entry in manifest['assets']}
        for asset_id, _, expected in CASES:
            with self.subTest(asset_id=asset_id):
                key = 'exports/' + asset_id + '.glb'
                self.assertEqual(read_glb(ROOT / key)['meshes'], expected)
                self.assertEqual(reports[key]['meshes'], expected)


if __name__ == '__main__':
    unittest.main()
