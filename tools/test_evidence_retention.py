"""Fast discovered retention checks and dependency-free negative fixtures."""
import copy
import json
from pathlib import Path
import tempfile
import unittest

from tools.evidence_retention import POLICY, ROOT, validate


class EvidenceRetentionTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.name = 'docs/campaign/evidence'
        self.image = self.root / self.name / 'before/frame.png'
        self.image.parent.mkdir(parents=True)
        self.image.write_bytes(b'fixture')
        self.policy = {'version': 1, 'aggregate_cap_bytes': 7, 'groups': [
            {'root': self.name, 'purpose': 'Retained comparison',
             'provenance': 'docs/campaign/receipt.json', 'files': {'before/frame.png': 7}}]}

    def errors(self):
        return '\n'.join(validate(self.root, self.policy))

    def test_repository_retention(self):
        self.assertEqual(validate(ROOT), [])

    def test_allowed_retention(self):
        self.assertEqual(self.errors(), '')

    def test_new_capture_and_new_campaign(self):
        for name in (self.name + '/next-run/new.PNG', 'docs/new/evidence/new.png'):
            path = self.root / name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(b'new')
            self.assertIn(name, self.errors())
        self.assertIn('unlisted evidence root', self.errors())

    def test_missing_retained_file(self):
        self.image.unlink()
        self.assertIn('before/frame.png: retained PNG missing', self.errors())

    def test_per_path_growth_even_with_aggregate_headroom(self):
        self.policy['aggregate_cap_bytes'] = 100
        self.image.write_bytes(b'fixture!')
        self.assertIn('before/frame.png: 8 bytes exceeds cap 7', self.errors())

    def test_aggregate_growth(self):
        self.policy['aggregate_cap_bytes'] = 6
        self.assertIn('aggregate PNG bytes 7 exceeds cap 6', self.errors())

    def test_traversal_absolute_and_nonportable_paths(self):
        group = self.policy['groups'][0]
        for name in ('../escape.png', '/escape.png', 'before/../escape.png',
                     'before//frame.png', 'before/./frame.png', 'before\\frame.png', 'not.png/'):
            group['files'] = {name: 7}
            with self.subTest(name=name):
                self.assertIn('invalid PNG path', self.errors())
        group['root'] = '../outside/evidence'
        self.assertIn('invalid monitored root', self.errors())

    def test_duplicate_roots_and_paths(self):
        self.policy['groups'].append(copy.deepcopy(self.policy['groups'][0]))
        self.assertIn('duplicate monitored root', self.errors())
        self.assertIn('duplicate retained path', self.errors())

    def test_duplicate_json_keys_are_not_silently_overwritten(self):
        path = self.root / POLICY
        path.write_text(json.dumps(self.policy).replace('"before/frame.png": 7',
                                                      '"before/frame.png": 7, "before/frame.png": 8'))
        self.assertIn('duplicate JSON entry: before/frame.png', '\n'.join(validate(self.root)))

    def test_invalid_bounds(self):
        for cap in (0, -1, True, 1.5, '7', None):
            with self.subTest(cap=cap):
                self.policy['groups'][0]['files']['before/frame.png'] = cap
                self.assertIn('positive integer', self.errors())
                self.policy['aggregate_cap_bytes'] = cap
                self.assertIn('positive integer', self.errors())
                self.policy['aggregate_cap_bytes'] = 7

    def test_invalid_schema_and_monitored_root(self):
        self.assertIn('expected version 1', '\n'.join(validate(self.root, [])))
        for version in (True, '1', 2):
            self.policy['version'] = version
            self.assertIn('expected version 1', self.errors())
        self.policy['version'] = 1
        self.policy['groups'][0]['root'] = 'sources/evidence'
        self.assertIn('invalid monitored root', self.errors())

    def test_promotion_requires_purpose_and_provenance(self):
        for field in ('purpose', 'provenance'):
            original = self.policy['groups'][0][field]
            self.policy['groups'][0][field] = ' '
            self.assertIn(f'nonblank {field}', self.errors())
            self.policy['groups'][0][field] = original

    def test_explicit_reviewed_promotion(self):
        path = self.image.with_name('new.png')
        path.write_bytes(b'new')
        self.policy['groups'][0]['files']['before/new.png'] = 3
        self.policy['aggregate_cap_bytes'] += 3
        self.assertEqual(self.errors(), '')

    def test_reference_originals_outside_monitored_roots_are_not_budgeted(self):
        path = self.root / 'docs/ui/references/evidence/original.png'
        path.parent.mkdir(parents=True)
        path.write_bytes(b'reference')
        self.assertEqual(self.errors(), '')

    def test_symlink_cannot_supply_retained_png(self):
        self.image.unlink()
        self.image.symlink_to('/dev/null')
        self.assertIn('expected regular PNG inside repository', self.errors())


if __name__ == '__main__':
    unittest.main()
