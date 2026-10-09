"""Cheap intake contracts, not functional or artistic acceptance of production UI."""
import hashlib
import json
import re
import struct
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
        self.assertEqual(by_id['artistic-approval']['status'], 'blocked')
        self.assertEqual(by_id['D-foundation']['status'], 'blocked')
        for key in ('E-core', 'E-inspection', 'F-hud', 'F-menu', 'G-portability'):
            self.assertNotEqual(by_id[key]['status'], 'completed')

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
