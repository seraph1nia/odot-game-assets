"""Cheap metadata/provenance contracts, not input testing or an aesthetic verdict."""
import hashlib
import json
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
        self.assertEqual(by_id['artistic-approval']['status'], 'completed')
        self.assertEqual(by_id['D-foundation']['status'], 'completed')
        for key in ('E-core', 'E-inspection', 'F-hud', 'F-menu', 'G-portability'):
            self.assertEqual(by_id[key]['status'], 'completed')
        self.assertEqual(load('tasks.json')['overall_status'], 'standalone-completed-awaiting-delivery-handoff')
        self.assertTrue(load('tasks.json')['approved_decisions'])
        self.assertIsNone(load('tasks.json')['current_blocker'])

    def test_historical_final_evidence_is_preserved(self):
        result = load(load('tasks.json')['package_results'])
        self.assertEqual(result['failures'], [])
        self.assertEqual(result['checks'], load('tasks.json')['package_checks'])
        self.assertEqual(len(result['captures']), 79)
        self.assertIn('llvmpipe', result['renderer'])
        # This accepted package predates the additional skill tree. Its immutable
        # artifact bindings remain below; current source binding has its own test.
        binding = load(load('tasks.json')['package_visual_review'])
        self.assertEqual(binding['capture_count'], 79)
        prior = load(binding['prior_review'])
        prior_result = load(prior['capture_manifest'])
        prior_hashes = {item['path']: hashlib.sha256((ROOT / prior['final_directory'] / item['path']).read_bytes()).hexdigest()
                        for item in prior_result['captures']}
        prior_rows = [f"{item['path']} {item['width']} {item['height']} {prior_hashes[item['path']]}\n"
                      for item in prior_result['captures']]
        self.assertEqual(hashlib.sha256(''.join(prior_rows).encode()).hexdigest(), prior['image_set_sha256'])
        inspected = set(binding['newly_inspected'])
        names = set(); rows = []; inherited = 0
        for item in result['captures']:
            name = item['path']; names.add(name)
            path = ROOT / binding['final_directory'] / name
            self.assertEqual(png_header(path)[:2], (item['width'], item['height']))
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            rows.append(f"{name} {item['width']} {item['height']} {digest}\n")
            if name not in inspected:
                self.assertEqual(digest, prior_hashes.get(name), name)
                inherited += 1
        self.assertEqual(len(names), 79)
        self.assertTrue(inspected <= names)
        self.assertEqual(inherited + len(inspected), len(names))
        self.assertEqual(hashlib.sha256(''.join(rows).encode()).hexdigest(), binding['image_set_sha256'])

    def test_current_skill_tree_evidence_and_source_binding(self):
        binding = load('skill-tree-validation.json')
        result = load(binding['results'])
        self.assertEqual(hashlib.sha256((DOCS / binding['results']).read_bytes()).hexdigest(), binding['results_sha256'])
        self.assertEqual(result['failures'], [])
        self.assertEqual(result['checks'], 706)
        self.assertEqual(len(result['captures']), 85)
        self.assertIn('llvmpipe', result['renderer'])
        for name, digest in result['source_sha256'].items():
            self.assertEqual(hashlib.sha256((PROJECT / name).read_bytes()).hexdigest(), digest, name)
        for name, digest in binding['tools_sha256'].items():
            self.assertEqual(hashlib.sha256((ROOT / name).read_bytes()).hexdigest(), digest, name)
        captures = {c['path']: c for c in result['captures']}
        for name, digest in binding['reviewed_captures'].items():
            path = DOCS / binding['results']
            path = path.parent / name
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest, name)
            self.assertEqual(png_header(path)[:2], (captures[name]['width'], captures[name]['height']))
        catalog = binding['reviewed_catalog']
        self.assertEqual(hashlib.sha256((ROOT / catalog['path']).read_bytes()).hexdigest(), catalog['sha256'])
        self.assertEqual(load('catalog/previews.json')['entries']['skill-tree']['sha256'], catalog['sha256'])

    def test_historical_representative_package_is_preserved(self):
        self.preserved_milestone('representative')
        result = load('production/production-package-reviewed/results.json')
        self.assertEqual((result['checks'], result['failures']), (438, []))
        binding = load('visual-review-components.json')
        self.assertEqual(len(binding['captures']), 35)
        for item in binding['captures']:
            path = ROOT / binding['final_directory'] / item['path']
            self.assertEqual(png_header(path)[:2], (item['width'], item['height']))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item['sha256'])

    def test_historical_m1_is_preserved_not_rebound_to_changed_source(self):
        self.preserved_milestone('foundation')
        result = load('production/m1-tab-scope/results.json')
        self.assertEqual((result['checks'], result['failures']), (271, []))
        binding = load('visual-review-m1.json')
        self.assertEqual(len(binding['captures']), 27)
        for item in binding['captures']:
            path = ROOT / item['path']
            self.assertEqual(png_header(path)[:2], (item['width'], item['height']))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), item['sha256'])
            final = ROOT / binding['final_directory'] / path.name
            self.assertEqual(hashlib.sha256(final.read_bytes()).hexdigest(), item['sha256'])

    def preserved_milestone(self, name):
        milestone = load('preservation.json')['milestones'][name]
        self.assertEqual(milestone['commit'], load('tasks.json')[name + '_commit'])
        for path, digest in milestone['files'].items():
            self.assertEqual(hashlib.sha256((DOCS / path).read_bytes()).hexdigest(), digest, path)

    def test_submitted_acceptance_is_preserved(self):
        for name in ('submitted', 'review_fixes'):
            milestone = load('preservation.json')['milestones'][name]
            for path, digest in milestone['files'].items():
                self.assertEqual(hashlib.sha256((DOCS / path).read_bytes()).hexdigest(), digest, path)

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


if __name__ == '__main__':
    unittest.main()
