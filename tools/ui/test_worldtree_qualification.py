"""Serialized Worldtree qualification must bind current or explicit historical evidence."""
import hashlib
import json
import unittest
from pathlib import Path

from tools.asset_catalog.ui_assets import package_bytes, payload_files

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT/'docs/ui'


def load(name):
    return json.loads((DOCS/name).read_text())


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


class WorldtreeQualificationTests(unittest.TestCase):
    def test_current_payload_and_direct_package_receipts_agree(self):
        binding = load('worldtree-validation.json')
        payload = load('payload.json')
        package = load(binding['package_check'])
        self.assertEqual(binding['package_check_sha256'], digest(DOCS/binding['package_check']))
        self.assertEqual(binding['package_sha256'], package['package_sha256'])
        self.assertEqual(binding['package_sha256'], hashlib.sha256(package_bytes(ROOT, payload_files(ROOT))).hexdigest())
        direct = load(binding['directly_tested_package_receipt'])
        self.assertEqual(binding['directly_tested_package_sha256'], direct['package_sha256'])
        self.assertEqual(binding['package_sha256'], direct['package_sha256'])
        self.assertEqual(package['files'], {'UI/'+name: value for name, value in payload['files'].items()})
        self.assertEqual(binding['payload_audit']['files'], len(payload['files']))
        self.assertEqual(binding['payload_audit']['scenes'], sum(name.endswith('.tscn') for name in payload['files']))
        self.assertEqual(binding['payload_audit']['log'], payload['log'])
        self.assertEqual(binding['footprint']['total_payload_bytes'], payload['total_file_bytes'])
        self.assertEqual(payload['total_file_bytes'], sum((ROOT/'ui/preview/UI'/name).stat().st_size for name in payload['files']))
        for name, value in binding['runtime_files'].items():
            self.assertEqual(value, payload['files'][name])
        static = binding.get('static_package_copy')
        if static:
            path = ROOT/static['path']
            self.assertEqual(static['sha256'], digest(path))
            self.assertEqual(static['bytes'], path.stat().st_size)
            if static.get('entire_archive_byte_identical_to_current_generated_zip'):
                self.assertEqual(path.read_bytes(), (ROOT/binding['package_generated']).read_bytes())
            if static.get('entire_archive_byte_identical_to_directly_loaded_zip'):
                self.assertEqual(static['sha256'], direct['package_sha256'])

    def test_current_and_historical_visual_evidence_remain_separate(self):
        binding = load('worldtree-validation.json')
        result = load(binding['results'])
        captures = {item['path'] for item in result['captures']}
        self.assertEqual(captures, set(binding['capture_sha256']))
        self.assertEqual(binding['capture_count'], len(captures))
        self.assertEqual(binding['results_sha256'], digest(DOCS/binding['results']))
        review = binding['review']
        historical = load(review['historical_binding'])
        self.assertEqual(review['historical_binding_sha256'], digest(DOCS/review['historical_binding']))
        for item in historical['review']['images']:
            self.assertEqual(item['sha256'], historical['capture_sha256'][item['path']])
        for item in review['images']:
            self.assertEqual(item['sha256'], binding['capture_sha256'][item['path']])
        for name in review.get('byte_identical_to_historically_reviewed_images', []):
            self.assertEqual(binding['capture_sha256'][name], historical['capture_sha256'][name])
        for name, value in binding['capture_sha256'].items():
            self.assertEqual(value, digest((DOCS/binding['results']).parent/name))


if __name__ == '__main__':
    unittest.main()
