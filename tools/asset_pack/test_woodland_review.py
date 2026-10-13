"""Render receipt cache behavior through the incremental review command."""
import hashlib
import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest.mock import patch

from tools.asset_pack import woodland_review as review


class RenderReceiptTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name)
        self.asset_id = 'characters/knight'
        self.source = self.root/'sources/characters/knight.blend'
        self.source.parent.mkdir(parents=True)
        self.source.write_bytes(b'current source')
        for name in ('tools/asset_catalog/render_blender.py', 'tools/asset_pack/woodland_render.py'):
            path = self.root/name
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_bytes(name.encode())
        self.inputs = (review.digest(self.root/'tools/asset_catalog/render_blender.py') +
                       review.digest(self.root/'tools/asset_pack/woodland_render.py'))
        self.renderer = hashlib.sha256(self.inputs.encode()).hexdigest()
        self.receipt = self.root/'docs/whisperwood/renders.json'
        self.receipt.parent.mkdir(parents=True)
        self.baseline = self.receipt.with_name('baseline.json')
        self.baseline.write_text(json.dumps({'jobs': [{'id': self.asset_id,
                                                     'source': self.source.relative_to(self.root).as_posix()}],
                                             'files': {'exports/'+self.asset_id+'.glb': {
                                                 'sha256': hashlib.sha256(b'model').hexdigest()}}}))

    def prepare(self, stage, fingerprint):
        self.model = self.root/('.cache/whisperwood/before/exports' if stage == 'before' else 'exports')/(self.asset_id+'.glb')
        self.model.parent.mkdir(parents=True, exist_ok=True)
        self.model.write_bytes(b'model')
        self.output = self.root/'docs/whisperwood/evidence'/stage/(self.asset_id+'.png')
        self.output.parent.mkdir(parents=True, exist_ok=True)
        self.output.write_bytes(b'cached image')
        self.tiers = [self.output.with_name(self.output.stem+f'-{size}.png') for size in (192, 96)]
        for path in self.tiers:
            path.write_bytes(b'cached tier')
        self.receipt.write_text(json.dumps({'assets': {self.asset_id: {stage: {
            'export_sha256': review.digest(self.model), 'renderer_sha256': fingerprint,
            'image_sha256': review.digest(self.output), 'source_sha256': 'old source'}}}}))

    def render(self, script, args, **options):
        self.assertEqual(script, 'tools/asset_pack/woodland_render.py')
        self.assertEqual(tuple(args), (self.model, self.output))
        self.assertEqual(options['root'], self.root)
        self.output.write_bytes(b'fresh image')
        for path in self.tiers:
            path.write_bytes(b'fresh tier')
        return {'job': 'fixture'}

    def invoke(self, stage):
        with patch.object(review, 'ROOT', self.root), patch('sys.argv', ['review', '--stage', stage]), \
                patch.object(review, 'run_blender', side_effect=self.render) as worker, \
                patch.object(review, 'read_glb', return_value={'fixture': True}), redirect_stdout(io.StringIO()):
            review.main()
        record = json.loads(self.receipt.read_text())['assets'][self.asset_id][stage]
        self.assertEqual(record['renderer_sha256'], self.renderer)
        self.assertEqual(record['export_sha256'], review.digest(self.model))
        self.assertEqual(record['image_sha256'], review.digest(self.output))
        self.assertEqual(record['derived_images'], {p.relative_to(self.root).as_posix(): review.digest(p) for p in self.tiers})
        if stage == 'after':
            self.assertEqual(record['source_sha256'], review.digest(self.source))
        return worker

    def test_exact_canonical_hash_reuses_both_stages(self):
        for stage in ('before', 'after'):
            with self.subTest(stage=stage):
                self.prepare(stage, self.renderer)
                self.invoke(stage).assert_not_called()
                self.assertEqual(self.output.read_bytes(), b'cached image')

    def test_obsolete_and_mismatched_hashes_rerender_both_stages(self):
        for stage in ('before', 'after'):
            for fingerprint in (self.inputs, '0'*64):
                with self.subTest(stage=stage, fingerprint=fingerprint):
                    self.prepare(stage, fingerprint)
                    self.invoke(stage).assert_called_once()
                    self.assertEqual(self.output.read_bytes(), b'fresh image')

    def test_changed_image_or_missing_tier_rerenders(self):
        for stage in ('before', 'after'):
            for changed in ('image', 'tier'):
                with self.subTest(stage=stage, changed=changed):
                    self.prepare(stage, self.renderer)
                    if changed == 'image':
                        self.output.write_bytes(b'changed image')
                    else:
                        self.tiers[0].unlink()
                    self.invoke(stage).assert_called_once()

    def test_obsolete_hash_cannot_bypass_preserved_baseline_guard(self):
        self.prepare('before', self.inputs)
        baseline = json.loads(self.baseline.read_text())
        baseline['files']['exports/'+self.asset_id+'.glb']['sha256'] = '0'*64
        self.baseline.write_text(json.dumps(baseline))
        before = self.receipt.read_bytes()
        with patch.object(review, 'ROOT', self.root), patch('sys.argv', ['review', '--stage', 'before']), \
                patch.object(review, 'run_blender') as worker, self.assertRaisesRegex(ValueError, 'Preserved baseline changed'):
            review.main()
        worker.assert_not_called()
        self.assertEqual(self.receipt.read_bytes(), before)


if __name__ == '__main__':
    unittest.main()
