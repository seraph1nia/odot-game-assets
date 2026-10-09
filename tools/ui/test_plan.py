"""Cheap metadata/provenance contracts, not input testing or an aesthetic verdict."""
import hashlib
import json
import re
import struct
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/ui'
PROJECT = ROOT / 'ui/preview'


def load(name):
    return json.loads((DOCS / name).read_text())


def png_header(path):
    data = path.read_bytes()
    if data[:8] != b'\x89PNG\r\n\x1a\n' or data[12:16] != b'IHDR':
        raise ValueError(f'Invalid PNG: {path}')
    return struct.unpack('>IIBB', data[16:26])  # width, height, depth, color type


class IntakeContracts(unittest.TestCase):
    def test_inventory_fields_and_dependencies(self):
        items = load('inventory.json')['items']
        ids = {item['id'] for item in items}
        self.assertEqual(len(ids), len(items))
        required = {'id', 'name', 'kind', 'purpose', 'use', 'existing', 'action',
                    'requirement', 'dependencies', 'states', 'blender', 'native_sufficient',
                    'reusable', 'priority', 'complexity', 'acceptance', 'migration'}
        for item in items:
            self.assertTrue(required <= item.keys(), item['id'])
            self.assertTrue(set(item['dependencies']) <= ids | {'artistic-approval'})
            self.assertTrue(item['acceptance'])

    def test_backlog_fields_and_acyclic_dependencies(self):
        tasks = load('tasks.json')['tasks']
        by_id = {task['id']: task for task in tasks}
        self.assertEqual(len(tasks), len(by_id))
        required = {'id', 'classification', 'status', 'objective', 'inputs', 'outputs',
                    'dependencies', 'approach', 'validation', 'completion', 'approval_required'}
        def visit(key, ancestors):
            self.assertNotIn(key, ancestors)
            for dependency in by_id[key]['dependencies']:
                visit(dependency, ancestors | {key})
        for task in tasks:
            self.assertTrue(required <= task.keys(), task['id'])
            self.assertTrue(set(task['dependencies']) <= by_id.keys())
            visit(task['id'], set())
        self.assertEqual(by_id['artistic-approval']['status'], 'completed')
        self.assertEqual(by_id['D-foundation']['status'], 'completed')
        self.assertTrue(load('tasks.json')['approved_decisions'])
        self.assertIsNone(load('tasks.json')['current_blocker'])

    def test_final_evidence_and_source_binding(self):
        result = load(load('tasks.json')['package_results'])
        self.assertEqual(result['failures'], [])
        self.assertEqual(result['checks'], 438)
        self.assertEqual(len(result['captures']), 35)
        self.assertIn('llvmpipe', result['renderer'])
        for name, digest in result['source_sha256'].items():
            self.assertEqual(hashlib.sha256((PROJECT / name).read_bytes()).hexdigest(), digest, name)
        binding = load('visual-review.json')
        review = binding['captures']
        self.assertEqual(len(review), 35)
        self.assertEqual({item['path'] for item in review}, {item['path'] for item in result['captures']})
        self.assertEqual(len({item['path'] for item in review}), len(review))
        for item in review:
            path = ROOT / binding['final_directory'] / item['path']
            self.assertEqual(png_header(path)[:2], (item['width'], item['height']))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item['sha256'])

    def test_historical_m1_is_preserved_not_rebound_to_changed_source(self):
        commit = load('tasks.json')['foundation_commit']
        self.assertEqual(commit, 'eb8ec20ca33ecc94ebcfd9ccb4ccf218562103cc')
        def original(path):
            return subprocess.check_output(['git', 'show', f'{commit}:{path}'], cwd=ROOT)
        name = 'docs/ui/production/m1-tab-scope/results.json'
        self.assertEqual((ROOT / name).read_bytes(), original(name))
        result = load('production/m1-tab-scope/results.json')
        self.assertEqual((result['checks'], result['failures']), (271, []))
        for path, digest in result['source_sha256'].items():
            self.assertEqual(hashlib.sha256(original('ui/preview/' + path)).hexdigest(), digest, path)
        binding = load('visual-review-m1.json')
        self.assertEqual((DOCS / 'visual-review-m1.json').read_bytes(), original('docs/ui/visual-review.json'))
        self.assertEqual(len(binding['captures']), 27)
        for item in binding['captures']:
            path = ROOT / item['path']
            self.assertEqual(png_header(path)[:2], (item['width'], item['height']))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item['sha256'])
            final = ROOT / binding['final_directory'] / path.name
            self.assertEqual(hashlib.sha256(final.read_bytes()).hexdigest(), item['sha256'])

    def test_runtime_payload_and_inventory_binding(self):
        manifest = load('payload.json')
        for name, digest in manifest['files'].items():
            self.assertEqual(hashlib.sha256((PROJECT / 'UI' / name).read_bytes()).hexdigest(), digest, name)
        inventory = load('inventory.json')
        self.assertEqual(set(inventory['implementation']), {item['id'] for item in inventory['items']})
        for item in inventory['implementation'].values():
            if 'resource' in item: self.assertTrue((PROJECT / item['resource']).is_file())
        self.assertEqual(manifest['seal_rgba_bytes'], 192 * 192 * 4)
        self.assertTrue((ROOT / 'docs/ui/api.md').is_file())

    def test_source_output_linkage(self):
        manifest = load('exploration-assets.json')
        self.assertTrue((ROOT / manifest['generator']).is_file())
        for item in manifest['assets']:
            for field in ('source', 'output'):
                path = ROOT / item[field]
                self.assertTrue(path.is_file())
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item[field + '_sha256'])
            self.assertEqual(png_header(ROOT / item['output']), (192, 192, 8, 6))
        mappings = load('migration.json')['mapping']
        ids = {item['id'] for item in load('inventory.json')['items']}
        for mapping in mappings:
            self.assertTrue(set(mapping['inventory']) <= ids)

    def test_captures_have_actual_dimensions(self):
        captures = load('previews/captures.json')['captures']
        self.assertEqual(len(captures), 8)
        self.assertEqual(len({c['path'] for c in captures}), 8)
        for capture in captures:
            header = png_header(ROOT / capture['path'])
            self.assertEqual(header[:2], (capture['width'], capture['height']))
            self.assertIn('llvmpipe', capture['renderer'])

    def test_portable_exploration_paths(self):
        for path in PROJECT.rglob('*'):
            if '.godot' in path.parts or path.suffix not in ('.gd', '.tscn', '.godot'):
                continue
            text = path.read_text()
            self.assertNotIn('/home/', text)
            self.assertNotIn('odot-game/', text)
            for resource in re.findall(r'res://[^"\n]+', text):
                # Dynamic direction texture path is checked by the asset manifest instead.
                if resource.endswith('/'):
                    continue
                self.assertTrue((PROJECT / resource.removeprefix('res://')).is_file(), resource)
        self.assertTrue((PROJECT / 'project.godot').is_file())


if __name__ == '__main__':
    unittest.main()
