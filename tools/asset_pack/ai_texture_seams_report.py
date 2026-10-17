"""Validate and package three-revision terrain evidence, without Blender writes."""
import html
import json
import os
from pathlib import Path

from tools.asset_pack.ai_texture_contract import sha
from tools.asset_pack.ai_texture_report import encoded_images, validate_ground_receipt
from tools.asset_pack.hex_ground import IDS

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/ai-textures'
MATCHED = ('camera_location', 'camera_rotation', 'ortho_scale', 'resolution', 'samples',
           'threads', 'exposure', 'glow', 'engine', 'transform', 'look', 'source_style_lights', 'world')


def comparison(root, paths, name, profiles, manifests, worker):
    """Fail closed on stale pixels, exports, renderer or unmatched settings."""
    first = profiles['before']
    for stage, profile in profiles.items():
        for field in MATCHED:
            assert profile[field] == first[field], (name, stage, field)
        assert profile['render_worker_sha256'] == sha(root / worker), (name, 'stale worker')
        assert profile['shared_review_sha256'] == sha(root / 'tools/asset_pack/ground_review.py')
        assert sha(paths[stage] / (name + '.png')) == profile['png_sha256'], (name, stage, 'stale pixels')
        for asset in profile['assets']:
            assert asset['glb_sha256'] == manifests[stage][asset['id']], (name, stage, asset['id'], 'stale GLB')
    return {'name': name, 'profiles': profiles,
            'images': {s: os.path.relpath(paths[s] / (name + '.png'), root / 'docs/ai-textures/seams')
                       for s in profiles}}


def main():
    output = DOCS / 'seams'
    baseline = json.loads((DOCS / 'baseline.json').read_text())
    delivered = json.loads((output / 'baseline.json').read_text())
    validation = json.loads((DOCS / 'validation.json').read_text())
    validate_ground_receipt(ROOT, json.loads((DOCS / 'ground-verification.json').read_text()))
    manifests = {
        'before': {a['id']: a['exports']['sha256'] for a in baseline['assets']},
        'pr14': {a['id']: a['exports']['sha256'] for a in delivered['assets']},
        'after': {aid: sha(ROOT / 'exports' / (aid + '.glb')) for aid in IDS}}
    manifests['after']['buildings/archery_range'] = sha(ROOT / 'exports/buildings/archery_range.glb')
    sets = []
    for grid in (False, True):
        paths = ({s: output / 'grids' / s for s in manifests} if grid else
                 {'before': DOCS / 'renders/before', 'pr14': output / 'pr14', 'after': DOCS / 'renders/after'})
        profiles = {s: {p['name']: p for p in json.loads((p / 'profiles.json').read_text())}
                    for s, p in paths.items()}
        assert profiles['before'].keys() == profiles['pr14'].keys() == profiles['after'].keys()
        for name in profiles['before']:
            if name.startswith('buildings_'):
                continue
            row = comparison(ROOT, paths, name, {s: profiles[s][name] for s in profiles}, manifests,
                             'tools/asset_pack/ai_texture_seams_review.py' if grid else
                             'tools/asset_pack/ai_texture_review.py')
            row['kind'] = 'neighbors' if grid else 'original-review'
            sets.append(row)
    resources = []
    for aid in IDS:
        row = validation['assets'][aid]
        old = row['immediate_predecessor']['export']['before']
        new = row['export_preservation']['after']
        assert old['version'] == manifests['pr14'][aid] and new['version'] == manifests['after'][aid]
        assert old['triangles'] == new['triangles'] and old['materials'] == new['materials']
        old_images = encoded_images(ROOT / '.cache/ai-textures-seams/pr14/exports' / (aid + '.glb'))
        new_images = encoded_images(ROOT / 'exports' / (aid + '.glb'))
        resources.append({'id': aid, 'delivered': old, 'correction': new,
                          'bytes_delta': new['bytes'] - old['bytes'],
                          'image_count_delta': len(new_images) - len(old_images),
                          'decoded_rgba8_delta_no_mips': sum(im['decoded_rgba8_bytes'] for im in new_images) -
                              sum(im['decoded_rgba8_bytes'] for im in old_images)})
    report = {'original_revision': baseline['revision'], 'delivered_revision': delivered['revision'],
              'correction_content_identity': json.loads((DOCS / 'handoff.json').read_text())['contentIdentity'],
              'comparisons': sets, 'resources': resources,
              'actual_game_acceptance': 'Pending separate GPU game task after immutable successor lands on asset main.'}
    (output / 'comparisons.json').write_text(json.dumps(report, indent=2) + '\n')
    titles = {'before': 'Original · 133c7cde', 'pr14': 'Delivered · 2d88d355', 'after': 'Correction · content hash'}
    cards = []
    # Lead with repetition/mixed grids; isolated material close-ups follow.
    for row in sorted(sets, key=lambda r: (r['kind'] != 'neighbors', r['name'])):
        figures = []
        for stage, path in row['images'].items():
            p = row['profiles'][stage]
            hashes = ', '.join(sorted({a['glb_sha256'][:12] for a in p['assets']}))
            figures.append('<figure><figcaption>' + titles[stage] + '<br><code>' + hashes + '</code></figcaption>'
                           '<a href="' + path + '"><img src="' + path + '" alt="' + stage + ' ' + html.escape(row['name']) + '"></a></figure>')
        cards.append('<article><h2>' + html.escape(row['name'].replace('_', ' ')) + '</h2><div class="triple">' +
                     ''.join(figures) + '</div><details><summary>Exact revisions, files, camera, light and color settings</summary><pre>' +
                     html.escape(json.dumps(row, indent=2)) + '</pre></details></article>')
    (output / 'review.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Odot · bounded ground correction</title><style>
:root{color-scheme:dark}body{background:#262724;color:#eee7d7;font:16px/1.5 system-ui;margin:24px auto;padding:0 20px;max-width:1320px}h1,h2{font-family:Georgia,serif;font-weight:normal}a{color:#bdcb83}article{background:#333530;border:1px solid #606353;padding:16px;margin:24px 0}.triple{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:10px}figure{margin:0;min-width:0}img{width:100%;height:auto}figcaption{font-size:13px;color:#c0b7a6}pre{white-space:pre-wrap;max-height:360px;overflow:auto;font-size:11px}code{overflow-wrap:anywhere}p{max-width:90ch}@media(max-width:700px){.triple{grid-template-columns:1fr}}</style><h1>Painted ground, without the dark outline.</h1>
<p>Three immutable content sets, actual GLBs, identical studio settings. Original → initially delivered paint → bounded pixel-only correction. <strong>Not actual-game acceptance.</strong> RX6800 findings motivate this change; the successor must land before the separate game task re-pins and judges it.</p>
<p><a href="README.md">Diagnosis, judgments, costs and reproduction</a> · <a href="comparisons.json">All image/profile/hash evidence</a> · <a href="../handoff.json">Main-only successor handoff</a> · <a href="../review.html">Original/correction pairs, foundation and unchanged overlays/Archery</a></p>
<p>The first six grids deliberately repeat identical orientations: smaller motifs and no dark uniform edge ring, not a promise that one immutable image can become non-repeating. Cards display single-tile views at roughly 260px occupied width and six-cell views at roughly 100px per tile on a wide desktop, spanning the retained game close/overview sizes. Click for native pixels. These are scale diagnostics, not calibrated Godot camera screenshots. Settings and every GLB/image hash are below each card.</p>
''' + ''.join(cards) + '<footer>Correction content set: <code>' + report['correction_content_identity'] + '</code></footer></html>')
    print('Three-revision gallery:', output / 'review.html')
    print('Export-byte delta from delivered terrain:', sum(r['bytes_delta'] for r in resources))


if __name__ == '__main__':
    main()
