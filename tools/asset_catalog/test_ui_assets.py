"""Mixed catalog contracts through the real generator and static output."""
import functools
import hashlib
import io
import json
import shutil
import tempfile
import threading
import unittest
import urllib.request
import zipfile
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

from .build_site import build_site
from .index import CatalogIndex, ROOT, write_json
from .export_sources import plan_exports
from .thumbnails import RENDER_VERSION, render_thumbnails
from .test_catalog import glb
from .ui_assets import DOCUMENTS, PACKAGE, PROJECT, build_ui_assets, payload_files


class UIAssetsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        shutil.copytree(ROOT / 'catalog', self.root / 'catalog')
        glb(self.root / 'exports/props/example.glb', clips=('idle',))
        self.models = CatalogIndex(self.root).build()['assets']
        shutil.copytree(ROOT / 'ui/preview', self.root / PROJECT,
                        ignore=shutil.ignore_patterns('.godot'))
        for name in DOCUMENTS:
            target = self.root / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / name).read_bytes())
        previews = json.loads((ROOT / 'docs/ui/catalog/previews.json').read_text())
        for entry in previews['entries'].values():
            target = self.root / entry['path']
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes((ROOT / entry['path']).read_bytes())
        generator = 'tools/ui/capture_catalog.py'
        (self.root / generator).parent.mkdir(parents=True)
        (self.root / generator).write_bytes((ROOT / generator).read_bytes())
        source = 'sources/ui/menu_seal.blend'
        (self.root / source).parent.mkdir(parents=True)
        (self.root / source).write_bytes((ROOT / source).read_bytes())

    def test_generated_entries_are_shipped_resources_not_inventory_plans_or_aliases(self):
        data = CatalogIndex(self.root).build()
        models = [asset for asset in data['assets'] if not asset.get('kind')]
        self.assertEqual(models, self.models)  # Existing model contracts unchanged.
        self.assertEqual(data['schema_version'], 2)
        ui = {asset['id']: asset for asset in data['assets'] if asset.get('kind')}
        self.assertEqual(len(ui), 13)
        self.assertEqual({a['role'] for a in ui.values()}, {'component', 'theme', 'art', 'showcase'})
        self.assertEqual(len([a for a in ui.values() if a['role'] == 'component']), 9)
        self.assertEqual(ui['ui/menu-seal']['title'], 'Original menu seal')
        self.assertEqual(ui['ui/menu-seal']['kind'], 'image')
        self.assertEqual(ui['ui/theme']['kind'], 'godot-theme')
        self.assertIn('research-node', ui['ui/action-quote']['aliases'])
        self.assertIn('health-style', ui['ui/unit-inspection']['aliases'])
        for asset in ui.values():
            self.assertIsNone(asset['model'])
            self.assertEqual(asset['animations'], [])
            if asset['role'] == 'showcase':
                self.assertIsNone(asset['resource']); self.assertTrue(asset['resource_excluded'])
            else:
                self.assertEqual(asset['resource']['path'], asset['authored_resource'])
            self.assertTrue((self.root / asset['preview']['path']).is_file())
            if asset['role'] != 'art': self.assertIn('static image', asset['preview_label'])
        self.assertNotIn('ui/resource-icons', ui)
        self.assertNotIn('ui/research-node', ui)
        self.assertNotIn('ui/health-style', ui)

    def test_runtime_package_is_compact_deterministic_and_exactly_the_payload(self):
        assets = build_ui_assets(self.root)
        package = (self.root / PACKAGE).read_bytes()
        self.assertLess(len(package), 200_000)
        with zipfile.ZipFile(io.BytesIO(package)) as archive:
            manifest = json.loads(archive.read('manifest.json'))
            expected = {name.removeprefix(PROJECT): digest for name, digest in payload_files(self.root).items()}
            self.assertEqual(manifest['files'], expected)
            self.assertEqual(set(archive.namelist()), set(expected) | {'api.md', 'manifest.json', 'README.txt'})
            for name, digest in expected.items():
                self.assertEqual(hashlib.sha256(archive.read(name)).hexdigest(), digest)
            self.assertEqual(archive.read('api.md'), (ROOT / 'docs/ui/api.md').read_bytes())
        package_hash = hashlib.sha256(package).hexdigest()
        self.assertEqual({a['package']['version'] for a in assets}, {package_hash})
        native_evidence = json.loads((ROOT / 'docs/ui/catalog/package-check.json').read_text())
        self.assertEqual(native_evidence['package_sha256'], package_hash)
        self.assertEqual(native_evidence['files'], expected)
        build_ui_assets(self.root)
        self.assertEqual((self.root / PACKAGE).read_bytes(), package)

    def test_changed_dependency_or_source_cannot_silently_ship_stale_preview(self):
        for name in ('UI/ui_helpers.gd', 'prototypes/fixtures.gd', 'catalog/capture.gd'):
            path = self.root / PROJECT / name
            original = path.read_bytes()
            path.write_bytes(original + b'\n# changed input\n')
            with self.subTest(name=name), self.assertRaisesRegex(ValueError, 'binding changed'):
                build_ui_assets(self.root)
            path.write_bytes(original)
        path = self.root / PROJECT / 'UI/theme/ledger.tres'
        path.unlink()
        with self.assertRaisesRegex(ValueError, 'payload file set changed'):
            build_ui_assets(self.root)

    def test_preview_identity_and_image_hash_are_enforced(self):
        manifest = self.root / 'docs/ui/catalog/previews.json'
        original = manifest.read_text()
        data = json.loads(original)
        data['entries']['theme']['resource'] = PROJECT + 'prototypes/menu.tscn'
        manifest.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'identity mismatch'):
            build_ui_assets(self.root)
        manifest.write_text(original)
        path = self.root / data['entries']['theme']['path']
        path.write_bytes(path.read_bytes() + b'changed')
        with self.assertRaisesRegex(ValueError, 'image binding changed'):
            build_ui_assets(self.root)

    def test_preview_paths_are_portable_and_measured_dimensions_are_required(self):
        manifest = self.root / 'docs/ui/catalog/previews.json'
        original = manifest.read_text()
        for path in ('../outside.png', str(self.root / json.loads(original)['entries']['theme']['path'])):
            data = json.loads(original); data['entries']['theme']['path'] = path
            manifest.write_text(json.dumps(data))
            with self.subTest(path=path), self.assertRaisesRegex(ValueError, 'portable and repository-relative'):
                build_ui_assets(self.root)
        data = json.loads(original); data['entries']['theme']['width'] = 1
        manifest.write_text(json.dumps(data))
        with self.assertRaisesRegex(ValueError, 'dimensions invalid'):
            build_ui_assets(self.root)
        manifest.write_text(original)

    def test_static_output_has_runtime_dependencies_docs_and_one_package_not_history(self):
        data = build_site(root=self.root)
        output = self.root / 'dist/catalog'
        self.assertEqual(len(list(output.rglob('*.zip'))), 1)
        self.assertFalse(list(output.rglob('*.blend')))
        self.assertFalse((output / PROJECT / 'prototypes').exists())
        self.assertFalse((output / 'docs/ui/production').exists())
        self.assertFalse(list(output.rglob('.godot')))
        for name, digest in payload_files(self.root).items():
            self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), digest)
        for asset in data['assets']:
            if asset.get('role') == 'showcase':
                self.assertIsNone(asset['resource'])
                self.assertIsNone(asset['source'])
                self.assertTrue(asset['resource_excluded'])
            if asset.get('kind'):
                for key in ('package', 'api', 'provenance', 'inventory', 'preview', 'thumbnail'):
                    record = asset[key]
                    self.assertEqual(hashlib.sha256((output / record['path']).read_bytes()).hexdigest(), record['version'])
        self.assertEqual(data, build_site(root=self.root))

    def test_implicit_3d_thumbnail_and_export_consumers_ignore_ui(self):
        model = self.models[0]
        thumbnail = self.root / 'exports/thumbnails' / (model['id'] + '.png')
        thumbnail.parent.mkdir(parents=True, exist_ok=True)
        thumbnail.write_bytes(b'existing GLB thumbnail')
        write_json(self.root / 'exports/thumbnails/state.json', {'renderer_version': RENDER_VERSION,
            'assets': {model['id']: {'model': model['model']['version'],
                                   'image': hashlib.sha256(thumbnail.read_bytes()).hexdigest()}}})
        # A real nonexistent executable would fail if any native UI reached Blender.
        render_thumbnails([], blender='/not/an/installed/blender', root=self.root)
        self.assertEqual(list((self.root / 'exports/thumbnails').rglob('*.png')), [thumbnail])
        with self.assertRaisesRegex(SystemExit, 'Not GLB asset IDs'):
            render_thumbnails(['ui/theme'], blender='/not/an/installed/blender', root=self.root)
        normal = self.root / 'sources/props/example.blend'
        normal.parent.mkdir(parents=True, exist_ok=True); normal.touch()
        watch = self.root / 'sources/ui/explorations/watch_seal.blend'
        watch.parent.mkdir(parents=True); watch.touch()
        self.assertEqual([job['id'] for job in plan_exports(self.root)], ['props/example'])

    def test_repository_models_keep_every_existing_export_id_and_glb_record(self):
        models = {asset['id']: asset['model']['path'] for asset in CatalogIndex(ROOT).build()['assets'] if asset['model']}
        expected = {path.relative_to(ROOT / 'exports').with_suffix('').as_posix(): path.relative_to(ROOT).as_posix()
                    for path in (ROOT / 'exports').rglob('*.glb')}
        self.assertEqual(models, expected)
        jobs = plan_exports(ROOT)
        self.assertFalse({'sources/ui/menu_seal.blend', 'sources/ui/explorations/watch_seal.blend'} & {job['source'] for job in jobs})

    def test_recorded_browser_output_bindings_match_generated_output_and_frames(self):
        # Persisted provenance contract, not a substitute for executing the browser suites.
        evidence = json.loads((ROOT / 'docs/ui/catalog/browser-review.json').read_text())
        build_site(root=self.root)
        output = self.root / 'dist/catalog'
        for name, digest in evidence['alias_search_regression']['frontend_sha256'].items():
            self.assertEqual(hashlib.sha256((output / name).read_bytes()).hexdigest(), digest)
        for view in evidence['screenshots']:
            self.assertEqual(hashlib.sha256((ROOT / view['path']).read_bytes()).hexdigest(), view['sha256'])
        self.assertFalse((output / 'docs/ui/catalog/browser').exists())
        for result in evidence['ui_acceptance'].values():
            self.assertEqual(result['package_sha256'], hashlib.sha256((output / PACKAGE).read_bytes()).hexdigest())

    def test_published_file_links_fetch_under_local_and_pages_prefix(self):
        data = build_site(root=self.root)
        output = self.root / 'dist/catalog'
        # The same artifact is mounted at / and /odot-game-assets/, as on Pages.
        shutil.copytree(output, output / 'odot-game-assets')
        class QuietHandler(SimpleHTTPRequestHandler):
            def log_message(self, *_args): pass
        handler = functools.partial(QuietHandler, directory=str(output))
        server = ThreadingHTTPServer(('127.0.0.1', 0), handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        try:
            for prefix in ('/', '/odot-game-assets/'):
                base = f'http://127.0.0.1:{server.server_port}' + prefix
                for asset in data['assets']:
                    for key in ('model', 'resource', 'package', 'api', 'inventory', 'provenance', 'preview'):
                        record = asset.get(key)
                        if not record: continue
                        self.assertFalse(Path(record['path']).is_absolute())
                        self.assertNotIn('..', Path(record['path']).parts)
                        with urllib.request.urlopen(base + record['path']) as response:
                            self.assertEqual(hashlib.sha256(response.read()).hexdigest(), record['version'])
        finally:
            server.shutdown(); server.server_close(); thread.join()


if __name__ == '__main__':
    unittest.main()
