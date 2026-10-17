"""Executable archive safety and current texture successor/evidence contracts."""
import copy
import hashlib
from html.parser import HTMLParser
import json
import shutil
import stat
import tempfile
import unittest
import zipfile
from pathlib import Path
from unittest.mock import patch

from tools.asset_pack.ai_texture_contract import ASSETS, predecessor, source_predecessor, sha
from tools.asset_pack.runtime_contract import export_chain
from tools.asset_pack.ambient_contract import source_chain
from tools.asset_pack.encoded_images import _png
from tools.asset_catalog.runtime_glb import read
from tools.asset_pack.ai_texture_inputs import extract
from tools.asset_pack import ai_texture_report as texture_report
from tools.asset_pack.hex_ground import IDS

ROOT = Path(__file__).resolve().parents[2]


class InputSafety(unittest.TestCase):
    def test_extracts_bounded_files_and_records_exact_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            archive = root / 'pack.zip'
            with zipfile.ZipFile(archive, 'w') as stream:
                stream.writestr('pack/textures/moss.png', b'input map bytes')
            record = extract(archive, root / 'private')
            self.assertEqual(record['files'][0]['sha256'], sha(root / 'private/pack/textures/moss.png'))
            self.assertEqual(record['sha256'], sha(archive))
            with self.assertRaises(FileExistsError):
                extract(archive, root / 'private')

    def test_rejects_traversal_absolute_windows_symlink_duplicates_and_expansion(self):
        for kind in ('../escape', '/escape', 'C:/escape', 'a\\escape', 'symlink', 'duplicate', 'bomb'):
            with self.subTest(kind=kind), tempfile.TemporaryDirectory() as temp:
                root = Path(temp)
                archive = root / 'pack.zip'
                with zipfile.ZipFile(archive, 'w', compression=zipfile.ZIP_DEFLATED) as stream:
                    if kind == 'symlink':
                        info = zipfile.ZipInfo('link')
                        info.create_system = 3
                        info.external_attr = (stat.S_IFLNK | 0o777) << 16
                        stream.writestr(info, '../escape')
                    elif kind == 'duplicate':
                        stream.writestr('Map.PNG', b'a')
                        stream.writestr('map.png', b'b')
                    elif kind == 'bomb':
                        stream.writestr('large', b'0' * 100_000)
                    else:
                        stream.writestr(kind, b'a')
                with self.assertRaises(ValueError):
                    extract(archive, root / 'private')
                self.assertFalse((root / 'private').exists())


class TextureSuccessors(unittest.TestCase):
    def test_all14_current_sources_exports_and_preservation_receipts_bind_baseline(self):
        baseline = json.loads((ROOT / 'docs/ai-textures/baseline.json').read_text())
        report = json.loads((ROOT / 'docs/ai-textures/validation.json').read_text())
        self.assertEqual(set(report['assets']), set(ASSETS))
        for item in baseline['assets']:
            for kind in ('sources', 'exports'):
                with self.subTest(asset=item['id'], kind=kind):
                    self.assertEqual(predecessor(ROOT, item['id'], kind), item[kind]['sha256'])
            geometry = report['assets'][item['id']]['export_preservation']
            for check in geometry['newly_exported_existing_source_uvs'].values():
                self.assertTrue(check['all_triangle_corners_checked_bidirectionally'])
                self.assertLess(check['max_uv_error'], .00002)

    def test_shared_component_chain_uses_actual_library_and_rejects_changed_owner(self):
        aid = 'environment/components/forest_foam'
        baseline = json.loads((ROOT / 'docs/runtime-optimization/baseline.json').read_text())
        job = baseline['assets'][aid]['job']
        self.assertNotEqual(job['source'], 'sources/' + aid + '.blend')
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ('docs/runtime-optimization/baseline.json',
                         'docs/runtime-optimization/validation.json',
                         'docs/ambient-motion/authored.json', job['source'],
                         'exports/' + aid + '.glb'):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            export_chain(root, aid, baseline['assets'][aid]['facts']['version'])
            self.assertEqual(source_predecessor(root, job['source']), baseline['sources'][job['source']])
            palette = json.loads((ROOT / 'docs/vivid-palette/authored.json').read_text())
            source_chain(root, job['source'], palette[job['source']]['sha256_after'])
            with (root / job['source']).open('ab') as stream:
                stream.write(b'changed library')
            with self.assertRaises(AssertionError):
                source_chain(root, job['source'], palette[job['source']]['sha256_after'])

    def test_broken_predecessor_identity_is_rejected_even_with_current_bytes(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            aid = 'environment/hex_ground_moss'
            for name in ('docs/ai-textures/baseline.json', 'docs/ai-textures/validation.json',
                         'docs/ai-textures/seams/baseline.json',
                         'tools/asset_pack/verify_ai_textures_blender.py',
                         'sources/' + aid + '.blend', 'exports/' + aid + '.glb'):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            path = root / 'docs/ai-textures/validation.json'
            report = json.loads(path.read_text())
            report['assets'][aid]['source_before_sha256'] = '0' * 64
            path.write_text(json.dumps(report))
            with self.assertRaises(AssertionError):
                predecessor(root, aid, 'sources')

    def test_changed_export_bytes_are_rejected_instead_of_reusing_old_receipt(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            aid = 'environment/hex_ground_moss'
            for name in ('docs/ai-textures/baseline.json', 'docs/ai-textures/validation.json',
                         'docs/ai-textures/seams/baseline.json',
                         'tools/asset_pack/verify_ai_textures_blender.py',
                         'sources/' + aid + '.blend', 'exports/' + aid + '.glb'):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            self.assertEqual(predecessor(root, aid, 'exports'), predecessor(ROOT, aid, 'exports'))
            path = root / 'exports' / (aid + '.glb')
            with path.open('ab') as stream:
                stream.write(b'corrupt')
            with self.assertRaises(AssertionError):
                predecessor(root, aid, 'exports')


class GalleryDOM(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links, self.images, self.article_count = [], [], 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])
        if tag == 'img':
            self.images.append(attrs)
        if tag == 'article':
            self.article_count += 1


class ReviewOutputs(unittest.TestCase):
    def test_ground_receipt_matches_current_sources_exports_validation_and_handoff(self):
        docs = ROOT / 'docs/ai-textures'
        receipt = json.loads((docs / 'ground-verification.json').read_text())
        texture_report.validate_ground_receipt(ROOT, receipt)
        validation = json.loads((docs / 'validation.json').read_text())['assets']
        handoff = {row['id']: row for row in json.loads((docs / 'handoff.json').read_text())['files']}
        for row in receipt['resources']:
            aid = row['asset_id']
            self.assertEqual(row['source_sha256'], validation[aid]['source_after_sha256'])
            self.assertEqual(row['version'], validation[aid]['export_preservation']['after']['version'])
            self.assertEqual(row['source_sha256'], handoff[aid]['source_blend_sha256'])
            self.assertEqual(row['version'], handoff[aid]['sha256'])

    def test_report_rejects_stale_or_incomplete_ground_evidence_before_writing(self):
        docs = ROOT / 'docs/ai-textures'
        receipt = json.loads((docs / 'ground-verification.json').read_text())
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            output = root / 'docs/ai-textures'
            output.mkdir(parents=True)
            shutil.copyfile(docs / 'validation.json', output / 'validation.json')
            for aid in IDS:
                for kind, suffix in (('sources', '.blend'), ('exports', '.glb')):
                    relative = Path(kind) / (aid + suffix)
                    target = root / relative
                    target.parent.mkdir(parents=True, exist_ok=True)
                    shutil.copyfile(ROOT / relative, target)
            texture_report.validate_ground_receipt(root, receipt)
            mutations = [(aid, field) for aid in IDS for field in ('source_sha256', 'version')]
            mutations += [(None, kind) for kind in ('missing', 'duplicate', 'extra')]
            for aid, field in mutations:
                with self.subTest(asset=aid, field=field):
                    stale = copy.deepcopy(receipt)
                    rows = stale['resources']
                    if aid:
                        next(row for row in rows if row['asset_id'] == aid)[field] = '0' * 64
                        error = 'stale ground source' if field == 'source_sha256' else 'stale ground export'
                    else:
                        if field == 'missing':
                            rows.pop()
                        elif field == 'duplicate':
                            rows[-1] = copy.deepcopy(rows[0])
                        else:
                            rows.append({**rows[0], 'asset_id': 'environment/not_in_ground_suite'})
                        error = 'Incomplete ground receipt coverage'
                    (output / 'ground-verification.json').write_text(json.dumps(stale))
                    before = {p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}
                    with patch.multiple(texture_report, ROOT=root, DOCS=output), self.assertRaisesRegex(AssertionError, error):
                        texture_report.main()
                    self.assertEqual({p.relative_to(output): p.read_bytes() for p in output.rglob('*') if p.is_file()}, before)

    def test_static_gallery_local_links_images_and_png_metadata_are_complete(self):
        docs = ROOT / 'docs/ai-textures'
        dom = GalleryDOM()
        dom.feed((docs / 'review.html').read_text())
        report = json.loads((docs / 'renders.json').read_text())
        self.assertEqual(dom.article_count, len(report['comparisons']) + 1)
        self.assertEqual(len(dom.images), len(report['comparisons']) * 3 + 1)
        for link in dom.links + [im['src'] for im in dom.images]:
            path = (docs / link).resolve()
            self.assertTrue(path.is_relative_to(docs))
            self.assertTrue(path.is_file(), link)
        for image in dom.images:
            self.assertTrue(image.get('alt'))
        for source in {im['src'] for im in dom.images}:
            (w, h, color, channels), _, _ = _png((docs / source).read_bytes())
            self.assertGreater(w, 0)
            self.assertGreater(h, 0)

    def test_render_hashes_profiles_and_labels_bind_final_original_and_current_glbs(self):
        docs = ROOT / 'docs/ai-textures'
        report = json.loads((docs / 'renders.json').read_text())
        self.assertEqual(len(report['comparisons']), 37)
        for pair in report['comparisons']:
            self.assertEqual(pair['before']['revision'], 'before')
            self.assertEqual(pair['after']['revision'], 'after')
            self.assertEqual(sha(docs / 'comparisons' / (pair['name'] + '.png')), pair['comparison_sha256'])
            for field in ('camera_location', 'camera_rotation', 'ortho_scale', 'resolution', 'samples',
                          'threads', 'exposure', 'glow', 'engine', 'transform', 'look', 'source_style_lights', 'world'):
                self.assertEqual(pair['before'][field], pair['after'][field])
            for stage in ('before', 'after'):
                profile = pair[stage]
                self.assertEqual(sha(docs / 'renders' / stage / (pair['name'] + '.png')), profile['png_sha256'])
                self.assertEqual(sha(ROOT / 'tools/asset_pack/ai_texture_review.py'), profile['render_worker_sha256'])
                self.assertEqual(sha(ROOT / 'tools/asset_pack/ground_review.py'), profile['shared_review_sha256'])
                for asset in profile['assets']:
                    aid = asset['id']
                    expected = predecessor(ROOT, aid, 'exports') if stage == 'before' else sha(ROOT / 'exports' / (aid + '.glb'))
                    self.assertEqual(asset['glb_sha256'], expected)
        for crop in report['foundation_crops']:
            self.assertEqual(sha(docs / crop['path']), crop['sha256'])
            self.assertEqual(sha(docs / 'renders' / crop['stage'] / (crop['source_profile'] + '.png')), crop['source_sha256'])
        self.assertEqual(sha(docs / 'comparisons/foundation_side.png'), report['foundation_comparison_sha256'])

    def test_handoff_content_set_and_each_embedded_image_match_current_exports(self):
        docs = ROOT / 'docs/ai-textures'
        handoff = json.loads((docs / 'handoff.json').read_text())
        self.assertEqual({f['id'] for f in handoff['files']}, set(ASSETS))
        self.assertEqual(hashlib.sha256(json.dumps(handoff['files'], sort_keys=True).encode()).hexdigest(), handoff['contentIdentity'])
        for file in handoff['files']:
            path = ROOT / file['sourcePath']
            self.assertEqual(sha(path), file['sha256'])
            self.assertEqual(path.stat().st_size, file['bytes'])
            self.assertEqual(sha(ROOT / 'sources' / (file['id'] + '.blend')), file['source_blend_sha256'])
            doc, binary = read(path)
            actual = []
            for image in doc['images']:
                self.assertNotIn('uri', image)
                view = doc['bufferViews'][image['bufferView']]
                start = view.get('byteOffset', 0)
                actual.append(hashlib.sha256(binary[start:start+view['byteLength']]).hexdigest())
            self.assertEqual(actual, [im['sha256'] for im in file['embeddedImages']])
            self.assertEqual(file['animationNames'], [a['name'] for a in doc.get('animations', [])])
        resources = json.loads((docs / 'resources.json').read_text())
        invalid = [im for im in resources['input_maps'] if not im['valid_png_header']]
        self.assertEqual(len(invalid), 1)
        self.assertEqual(invalid[0]['bytes'], 0)
        self.assertEqual(invalid[0]['decoded_rgba8_bytes'], 0)


class SeamCorrectionOutputs(unittest.TestCase):
    def test_delivered_predecessor_cannot_be_removed_or_rebound(self):
        aid = 'environment/hex_ground_moss'
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            for name in ('docs/ai-textures/baseline.json', 'docs/ai-textures/validation.json',
                         'docs/ai-textures/seams/baseline.json', 'tools/asset_pack/verify_ai_textures_blender.py',
                         'sources/' + aid + '.blend', 'exports/' + aid + '.glb'):
                target = root / name
                target.parent.mkdir(parents=True, exist_ok=True)
                shutil.copyfile(ROOT / name, target)
            path = root / 'docs/ai-textures/validation.json'
            report = json.loads(path.read_text())
            predecessor(root, aid, 'sources')
            for damage in ('missing', 'source_sha256', 'source_signature_before', 'all_predecessor_images_exact'):
                broken = copy.deepcopy(report)
                row = broken['assets'][aid]
                if damage == 'missing':
                    del row['immediate_predecessor']
                else:
                    row['immediate_predecessor'][damage] = False if damage == 'all_predecessor_images_exact' else '0' * 64
                path.write_text(json.dumps(broken))
                with self.subTest(damage=damage), self.assertRaises(AssertionError):
                    predecessor(root, aid, 'sources')

    def test_three_revision_evidence_binds_pixels_profiles_and_export_sets(self):
        from tools.asset_pack.ai_texture_seams_report import comparison
        docs = ROOT / 'docs/ai-textures'
        report = json.loads((docs / 'seams/comparisons.json').read_text())
        self.assertEqual(len(report['comparisons']), 41)
        delivered = json.loads((docs / 'seams/baseline.json').read_text())
        original = json.loads((docs / 'baseline.json').read_text())
        manifests = {
            'before': {a['id']: a['exports']['sha256'] for a in original['assets']},
            'pr14': {a['id']: a['exports']['sha256'] for a in delivered['assets']},
            'after': {aid: sha(ROOT / 'exports' / (aid + '.glb')) for aid in IDS}}
        for row in report['comparisons']:
            paths = {s: (docs / 'seams' / p).parent for s, p in row['images'].items()}
            worker = ('tools/asset_pack/ai_texture_seams_review.py' if row['kind'] == 'neighbors'
                      else 'tools/asset_pack/ai_texture_review.py')
            comparison(ROOT, paths, row['name'], row['profiles'], manifests, worker)
        self.assertEqual(report['correction_content_identity'], json.loads((docs / 'handoff.json').read_text())['contentIdentity'])
        dom = GalleryDOM()
        dom.feed((docs / 'seams/review.html').read_text())
        self.assertEqual(dom.article_count, 41)
        self.assertEqual(len(dom.images), 123)
        for link in dom.links + [im['src'] for im in dom.images]:
            path = (docs / 'seams' / link).resolve()
            self.assertTrue(path.is_relative_to(docs))
            self.assertTrue(path.is_file(), link)
        for row in report['resources']:
            self.assertEqual(row['image_count_delta'], 0)
            self.assertEqual(row['decoded_rgba8_delta_no_mips'], 0)
            self.assertEqual(row['delivered']['materials'], row['correction']['materials'])
            self.assertEqual(row['delivered']['triangles'], row['correction']['triangles'])

    def test_three_revision_packaging_refuses_stale_pixels_glbs_and_settings(self):
        from tools.asset_pack.ai_texture_seams_report import comparison
        docs = ROOT / 'docs/ai-textures'
        row = json.loads((docs / 'seams/comparisons.json').read_text())['comparisons'][0]
        paths = {s: (docs / 'seams' / p).parent for s, p in row['images'].items()}
        manifests = {s: {a['id']: a['glb_sha256'] for a in p['assets']} for s, p in row['profiles'].items()}
        worker = 'tools/asset_pack/ai_texture_review.py'
        comparison(ROOT, paths, row['name'], row['profiles'], manifests, worker)
        for field in ('png_sha256', 'render_worker_sha256', 'shared_review_sha256', 'ortho_scale'):
            profiles = copy.deepcopy(row['profiles'])
            profiles['after'][field] = 'stale'
            with self.subTest(field=field), self.assertRaises(AssertionError):
                comparison(ROOT, paths, row['name'], profiles, manifests, worker)
        bad = copy.deepcopy(manifests)
        bad['after'][next(iter(bad['after']))] = '0' * 64
        with self.assertRaises(AssertionError):
            comparison(ROOT, paths, row['name'], row['profiles'], bad, worker)


if __name__ == '__main__':
    unittest.main()
