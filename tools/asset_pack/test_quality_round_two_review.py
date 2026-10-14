"""Behavioral freshness tests for the second-round actual-image receipt consumer."""
import json
import struct
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from tools.asset_pack import quality_round_two_review as review


class CachedViewTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.model = self.root / 'asset.glb'
        self.output = self.root / 'asset.png'
        self.model.write_bytes(b'exported model')
        self.output.write_bytes(b'actual image')
        self.derivatives = [self.output.with_name(f'asset-{size}.png') for size in (192, 96)]
        for path in self.derivatives:
            path.write_bytes(b'actual derivative')
        self.previous = {
            'export_sha256': review.sha(self.model),
            'image_sha256': review.sha(self.output),
            'renderer_sha256': 'canonical fingerprint',
            'derived_images': {p.name: review.sha(p) for p in self.derivatives},
            'job': {'job': 'real fixture'},
        }
        self.addCleanup(patch.stopall)
        patch.object(review, 'ROOT', self.root).start()

    def consume(self):
        return review.cached_job(self.model, self.output, 'canonical fingerprint', self.previous)

    def test_exact_binding_reuses_job(self):
        self.assertEqual(self.consume(), {'job': 'real fixture'})

    def test_changed_export_or_full_image_fails_closed(self):
        for path in (self.model, self.output):
            original = path.read_bytes()
            path.write_bytes(b'changed')
            with self.assertRaisesRegex(ValueError, 'Stale actual after view'):
                self.consume()
            path.write_bytes(original)

    def test_changed_renderer_fails_closed(self):
        self.previous['renderer_sha256'] = 'obsolete or concatenated fingerprint'
        with self.assertRaisesRegex(ValueError, 'Stale actual after view'):
            self.consume()

    def test_both_derivatives_require_current_files_and_bindings(self):
        for path in self.derivatives:
            for change in ('bytes', 'file', 'binding', 'all bindings'):
                with self.subTest(path=path.name, change=change):
                    original = path.read_bytes()
                    bindings = dict(self.previous['derived_images'])
                    if change == 'bytes':
                        path.write_bytes(b'changed')
                    elif change == 'file':
                        path.unlink()
                    elif change == 'binding':
                        del self.previous['derived_images'][path.name]
                    else:
                        del self.previous['derived_images']
                    with self.assertRaisesRegex(ValueError, 'Missing/stale canonical derivative'):
                        self.consume()
                    path.write_bytes(original)
                    self.previous['derived_images'] = bindings
                    self.assertEqual(self.consume(), {'job': 'real fixture'})


class ExportOwnershipTests(unittest.TestCase):
    def test_authored_glb_geometry_belongs_to_building_root(self):
        for name in ('bakery', 'weaver', 'magic_academy', 'town_hall', 'woodcutter_hut'):
            with self.subTest(asset=name):
                data = (review.ROOT / 'exports/buildings' / (name + '.glb')).read_bytes()
                length, kind = struct.unpack_from('<II', data, 12)
                self.assertEqual(kind, 0x4E4F534A)
                document = json.loads(data[20:20 + length])
                nodes = document['nodes']
                root = next(i for i, node in enumerate(nodes) if node['name'] == name + '_root')
                descendants = set()
                pending = [root]
                while pending:
                    index = pending.pop()
                    if index not in descendants:
                        descendants.add(index)
                        pending.extend(nodes[index].get('children', []))
                authored = {i for i, node in enumerate(nodes)
                            if node.get('extras', {}).get('whisperwood_quality_round_two') and 'mesh' in node}
                self.assertLessEqual(authored, descendants)
                if name == 'magic_academy':
                    self.assertEqual(len(authored), 2)
                    self.assertEqual(document['scenes'][document.get('scene', 0)]['nodes'], [root])


if __name__ == '__main__':
    unittest.main()
