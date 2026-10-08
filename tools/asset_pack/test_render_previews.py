"""Selected saved-source rendering behavior without launching Blender."""
import importlib.util
import io
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock, patch

from tools.asset_catalog.index import write_json


class PreviewSelectionTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        (self.root / 'exports/previews').mkdir(parents=True)
        self.ids = ['environment/hex_hollow_watchers', 'environment/hex_butterfly_glade',
                    'environment/hex_dream_menagerie', 'environment/hex_crystal_grove',
                    'buildings/archery_range', 'characters/knight']
        for asset in self.ids:
            self.source('sources/' + asset + '.blend')
        # The association, not a filename or supplied-reference list, owns this source.
        self.override = 'sources/authored/watcher_scene.blend'
        self.source(self.override)
        write_json(self.root / 'exports/asset_manifest.json', {'assets': [
            {'file': 'exports/' + asset + '.glb'} for asset in self.ids]})
        write_json(self.root / 'catalog/associations.json', {'schema_version': 1, 'assets': {
            'exports/environment/hex_hollow_watchers.glb': {
                'source': self.override, 'export_collection': 'hex_hollow_watchers'}}})
        self.scene = SimpleNamespace(camera=object(),
                                     render=SimpleNamespace(filepath='', threads_mode='', threads=0))
        self.bpy = SimpleNamespace(context=SimpleNamespace(scene=self.scene),
                                   ops=SimpleNamespace(wm=SimpleNamespace(open_mainfile=Mock()),
                                                       render=SimpleNamespace(render=Mock(side_effect=self.render))))
        self.geometry = SimpleNamespace(ROOT=self.root)
        spec = importlib.util.spec_from_file_location(
            '_preview_selection_fixture', Path(__file__).with_name('render_previews.py'))
        self.module = importlib.util.module_from_spec(spec)
        with patch.dict('sys.modules', {'bpy': self.bpy, 'geometry': self.geometry,
                                       'art_style': SimpleNamespace(PREVIEW=SimpleNamespace(threads=4))}):
            spec.loader.exec_module(self.module)

    def source(self, relative):
        path = self.root / relative
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_bytes(b'authored Blender source')

    def render(self, **options):
        self.assertEqual(options, {'write_still': True})
        Path(self.scene.render.filepath).write_bytes(b'rendered PNG fixture')

    def run_selection(self, names):
        with redirect_stdout(io.StringIO()):
            self.module.main(names)

    def test_dreaming_aliases_render_authoritative_sources_without_saving_them(self):
        before = {p: p.read_bytes() for p in (self.root / 'sources').rglob('*.blend')}
        self.run_selection(['hex_hollow_watchers', 'hex_butterfly_glade', 'hex_dream_menagerie'])
        expected = [self.override, 'sources/environment/hex_butterfly_glade.blend',
                    'sources/environment/hex_dream_menagerie.blend']
        self.assertEqual([c.kwargs['filepath'] for c in self.bpy.ops.wm.open_mainfile.call_args_list],
                         [str(self.root / path) for path in expected])
        self.assertEqual(self.bpy.ops.render.render.call_count, 3)
        self.assertEqual({p.name for p in (self.root / 'exports/previews').glob('*.png')},
                         {'hex_hollow_watchers.png', 'hex_butterfly_glade.png', 'hex_dream_menagerie.png'})
        self.assertEqual(before, {p: p.read_bytes() for p in before})
        self.assertEqual(self.scene.render.threads, 4)

    def test_normal_forest_and_building_aliases_preserve_existing_output_names(self):
        self.run_selection(['hex_crystal_grove', 'archery_range'])
        self.assertEqual([c.kwargs['filepath'] for c in self.bpy.ops.wm.open_mainfile.call_args_list],
                         [str(self.root / 'sources/environment/hex_crystal_grove.blend'),
                          str(self.root / 'sources/buildings/archery_range.blend')])
        self.assertEqual({p.name for p in (self.root / 'exports/previews').glob('*.png')},
                         {'hex_crystal_grove.png', 'archery_range.png'})

    def test_canonical_unit_id_renders_the_authored_source(self):
        self.run_selection(['characters/knight'])
        self.bpy.ops.wm.open_mainfile.assert_called_once_with(
            filepath=str(self.root / 'sources/characters/knight.blend'))
        self.assertTrue((self.root / 'exports/previews/knight.png').is_file())

    def test_unknown_selection_is_refused_before_opening_any_source(self):
        with self.assertRaises(ValueError):
            self.run_selection(['archery_range', 'not_an_asset'])
        self.bpy.ops.wm.open_mainfile.assert_not_called()
        self.bpy.ops.render.render.assert_not_called()

    def test_ambiguous_alias_is_refused_but_a_single_canonical_id_is_valid(self):
        self.source('sources/buildings/shared_name.blend')
        self.source('sources/environment/shared_name.blend')
        with self.assertRaisesRegex(ValueError, 'ambiguous'):
            self.run_selection(['shared_name'])
        self.bpy.ops.wm.open_mainfile.assert_not_called()
        self.run_selection(['buildings/shared_name'])
        self.bpy.ops.wm.open_mainfile.assert_called_once_with(
            filepath=str(self.root / 'sources/buildings/shared_name.blend'))

    def test_distinct_canonical_ids_cannot_overwrite_the_same_preview_filename(self):
        self.source('sources/buildings/shared_name.blend')
        self.source('sources/environment/shared_name.blend')
        with self.assertRaisesRegex(ValueError, 'preview filename'):
            self.run_selection(['buildings/shared_name', 'environment/shared_name'])
        self.bpy.ops.wm.open_mainfile.assert_not_called()

    def test_invalid_source_schema_is_refused_before_opening_blender(self):
        write_json(self.root / 'catalog/associations.json', {'schema_version': 1, 'assets': {
            'exports/environment/hex_hollow_watchers.glb': {
                'source': self.override, 'export_collection': 'tile', 'export_object': 'root'}}})
        with self.assertRaisesRegex(ValueError, 'not both'):
            self.run_selection(['hex_hollow_watchers'])
        self.bpy.ops.wm.open_mainfile.assert_not_called()


if __name__ == '__main__':
    unittest.main()
