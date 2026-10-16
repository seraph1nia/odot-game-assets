"""Package actual matched POC views and an immutable content-hash game handoff.

No Blender/source writes. Run only after export validation and final render refresh.
"""
import hashlib
import html
import json
import struct
import subprocess
from pathlib import Path

from tools.asset_pack.ai_texture_contract import ASSETS, predecessor, sha
from tools.asset_catalog.runtime_glb import read

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/ai-textures'


def encoded_images(path):
    doc, binary = read(path)
    result = []
    for image in doc.get('images', []):
        view = doc['bufferViews'][image['bufferView']]
        start = view.get('byteOffset', 0)
        data = binary[start:start + view['byteLength']]
        assert data[:8] == b'\x89PNG\r\n\x1a\n'
        w, h = struct.unpack_from('>II', data, 16)
        result.append({'name': image.get('name'), 'sha256': hashlib.sha256(data).hexdigest(),
                       'bytes': len(data), 'dimensions': [w, h], 'decoded_rgba8_bytes': w*h*4})
    return result


def main():
    validation = json.loads((DOCS / 'validation.json').read_text())
    profiles = {stage: {p['name']: p for p in json.loads((DOCS / 'renders' / stage / 'profiles.json').read_text())}
                for stage in ('before', 'after')}
    assert profiles['before'].keys() == profiles['after'].keys()
    resources, handoff = [], []
    for aid in ASSETS:
        predecessor(ROOT, aid, 'exports')
        row = validation['assets'][aid]
        cost = row['export_preservation']
        images = encoded_images(ROOT / 'exports' / (aid + '.glb'))
        before_images = encoded_images(ROOT / '.cache/ai-textures/before/exports' / (aid + '.glb'))
        resources.append({'id': aid, 'before': cost['before'], 'after': cost['after'],
            'before_decoded_rgba8_bytes_no_mips': sum(im['decoded_rgba8_bytes'] for im in before_images),
            'after_decoded_rgba8_bytes_no_mips': sum(im['decoded_rgba8_bytes'] for im in images),
            'source_bytes_before': (ROOT / '.cache/ai-textures/before/sources' / (aid + '.blend')).stat().st_size,
            'source_bytes_after': (ROOT / 'sources' / (aid + '.blend')).stat().st_size,
            'retained_original_source_image_count': row['source_preservation']['original_image_count'],
            'added_source_color_images': row['source_preservation']['new_image_count']})
        handoff.append({'id': aid, 'sourcePath': 'exports/' + aid + '.glb', 'sha256': cost['after']['version'],
            'bytes': cost['after']['bytes'], 'materials': cost['after']['materials'],
            'animationNames': [a['name'] for a in cost['after']['animations']], 'embeddedImages': images,
            'source_blend_sha256': row['source_after_sha256']})
    inputs = []
    for folder in ('environment/textures/ai_ground/input', 'buildings/textures/ai_archery/input'):
        for path in sorted((ROOT / 'sources' / folder).rglob('*.png')):
            data = path.read_bytes()
            valid = len(data) >= 24 and data[:8] == b'\x89PNG\r\n\x1a\n'
            w, h = struct.unpack_from('>II', data, 16) if valid else (0, 0)
            inputs.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': sha(path),
                           'bytes': path.stat().st_size, 'dimensions': [w, h], 'decoded_rgba8_bytes': w*h*4,
                           'valid_png_header': valid,
                           'issue': None if valid else 'Invalid/empty supplied map; retained as original input only, never loaded or embedded.'})
    (DOCS / 'resources.json').write_text(json.dumps({'assets': resources, 'input_maps': inputs,
        'limitations': ['RGBA8 estimates exclude mipmaps, compression, renderer deduplication and allocation overhead.',
                        'No GPU timing, frame-rate or actual-game acceptance is inferred from CPU renders.']}, indent=2) + '\n')
    identity = hashlib.sha256(json.dumps(handoff, sort_keys=True).encode()).hexdigest()
    (DOCS / 'handoff.json').write_text(json.dumps({'schemaVersion': 1,
        'source': 'https://github.com/seraph1nia/odot-game-assets.git',
        'contentIdentity': identity, 'baselineRevision': validation['baseline_revision'],
        'revisionRule': 'Import only the immutable assets-main commit containing this exact manifest after the asset PR merges. Resolve that full commit SHA, verify it is an ancestor of origin/main, and pin it explicitly in the game manifest. This content manifest is not permission to import a private branch.',
        'gameAcceptance': 'Partial assets-first milestone. After this asset PR lands on assets main, dependent game ship odot-ai-textures-game must update the explicit immutable pin and hash/derived manifest metadata, then complete actual-GPU acceptance in settlement, forest, river and path views, including placement, tile connections, water motion and asset loading; include Archery Range settlement acceptance if its material stage is visually acceptable. Do not declare the overall request complete until that game work lands with acceptance evidence. No actual-game improvement claim yet.',
        'files': handoff}, indent=2) + '\n')
    comparisons = DOCS / 'comparisons'
    comparisons.mkdir(exist_ok=True)
    cards, render_manifest = [], []
    for name in profiles['before']:
        before, after = profiles['before'][name], profiles['after'][name]
        for key in ('camera_location', 'camera_rotation', 'ortho_scale', 'resolution', 'samples', 'threads',
                    'exposure', 'glow', 'engine', 'transform', 'look', 'source_style_lights', 'world'):
            assert before[key] == after[key], (name, key, 'unmatched comparison')
        for stage, profile in (('before', before), ('after', after)):
            image = DOCS / 'renders' / stage / (name + '.png')
            assert sha(image) == profile['png_sha256']
            assert profile['render_worker_sha256'] == sha(ROOT / 'tools/asset_pack/ai_texture_review.py')
            for asset in profile['assets']:
                path = ROOT / ('.cache/ai-textures/before/exports' if stage == 'before' else 'exports') / (asset['id'] + '.glb')
                assert sha(path) == asset['glb_sha256'], 'stale render export'
        first_before = before['assets'][-1]['glb_sha256'][:12]
        first_after = after['assets'][-1]['glb_sha256'][:12]
        output = comparisons / (name + '.png')
        subprocess.run(['magick', 'montage', '-label', 'BEFORE 133c7cde / ' + first_before,
            str(DOCS / 'renders/before' / (name + '.png')), '-label', 'AI POC / ' + first_after,
            str(DOCS / 'renders/after' / (name + '.png')), '-tile', '2x1', '-geometry', '+4+4', '-depth', '8', str(output)], check=True)
        render_manifest.append({'name': name, 'comparison_sha256': sha(output),
                                'before': before, 'after': after})
        hashes = '<details><summary>Exact assets, hashes &amp; render settings</summary><pre>' + html.escape(json.dumps({'before': before, 'after': after}, indent=2)) + '</pre></details>'
        cards.append('<article><h2>' + html.escape(name.replace('_', ' ')) + '</h2><a href="comparisons/' + name + '.png"><img class="pair" loading="lazy" src="comparisons/' + name + '.png" alt="Matched original and textured GLB: ' + name + '"></a>'
            + '<div class="small"><figure><figcaption>Before · 96 px diagnostic</figcaption><img width="96" height="96" src="renders/before/' + name + '.png" alt="Before small view"></figure>'
            + '<figure><figcaption>After · 96 px diagnostic</figcaption><img width="96" height="96" src="renders/after/' + name + '.png" alt="After small view"></figure></div>' + hashes + '</article>')
    # A matched pixel crop of the visible sidewall, not a fabricated new camera.
    foundation_images = []
    for stage in ('before', 'after'):
        source = DOCS / 'renders' / stage / 'environment_hex_ground_moss.png'
        target = DOCS / 'renders' / stage / 'foundation_side.png'
        subprocess.run(['magick', str(source), '-crop', '320x80+40+235', '+repage', '-depth', '8', str(target)], check=True)
        foundation_images.append({'stage': stage, 'path': target.relative_to(DOCS).as_posix(),
                                  'sha256': sha(target), 'source_profile': 'environment_hex_ground_moss',
                                  'source_sha256': sha(source), 'pixel_crop_xywh': [40, 235, 320, 80]})
    subprocess.run(['magick', 'montage', '-label', 'Before foundation / 133c7cde',
        str(DOCS / 'renders/before/foundation_side.png'), '-label', 'AI foundation / final GLB',
        str(DOCS / 'renders/after/foundation_side.png'), '-tile', '2x1', '-geometry', '+4+4',
        '-depth', '8', str(comparisons / 'foundation_side.png')], check=True)
    cards.insert(0, '<article><h2>Shared foundation · sidewall detail</h2><img class="pair" src="comparisons/foundation_side.png" alt="Before and after sidewall pixel crop"><p>Same moss GLBs, same camera. A shallow course cropped from the supplied foundation atlas avoids squeezing several square block rows into the .36m sidewall. Unchanged UVs and base depth; the underside shares this material.</p></article>')
    (DOCS / 'renders.json').write_text(json.dumps({'contentIdentity': identity, 'comparisons': render_manifest,
        'foundation_crops': foundation_images, 'foundation_comparison_sha256': sha(comparisons / 'foundation_side.png')}, indent=2) + '\n')
    (DOCS / 'review.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>Odot · AI texture POC</title><style>
:root{color-scheme:dark;--bg:#262724;--panel:#333530;--ink:#eee7d7;--muted:#c0b7a6;--line:#606353;--accent:#bdcb83}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui,sans-serif}main{max-width:1200px;margin:auto;padding:32px 20px}h1,h2{font-family:Georgia,serif;font-weight:normal;line-height:1.2}h1{font-size:clamp(30px,5vw,56px)}h2{font-size:24px;overflow-wrap:anywhere}p{max-width:80ch;color:var(--muted)}a{color:var(--accent)}article{min-width:0;border:1px solid var(--line);background:var(--panel);padding:16px;margin:24px 0;border-radius:8px}.pair{display:block;width:100%;height:auto}.small{display:flex;flex-wrap:wrap;gap:20px}figure{margin:12px 0;min-width:0}figcaption{font-size:12px;color:var(--muted)}.small img{object-fit:contain}details,pre{min-width:0;overflow-wrap:anywhere}pre{white-space:pre-wrap;font:11px/1.4 monospace;max-height:420px;overflow:auto}code{overflow-wrap:anywhere}.status{border-left:4px solid var(--accent);padding:12px 18px;background:var(--panel)}a:focus-visible,summary:focus-visible{outline:3px solid var(--accent);outline-offset:3px}</style><main><p>ODOТ / TEXTURE-ONLY TRIAL</p><h1>More painted surfaces.<br>The same authored assets.</h1>
<div class="status"><strong>Partial assets-first milestone, not end-to-end completion.</strong> Matched original/new GLBs rendered through the existing Cycles studio on CPU. After this asset PR lands on assets main, dependent game ship <code>odot-ai-textures-game</code> must update the explicit immutable pin and hash/derived manifest metadata, then complete actual-GPU acceptance in settlement, forest, river and path views, including placement, tile connections, water motion and asset loading. Include Archery Range settlement acceptance if its material stage is visually acceptable. Do not declare the overall request complete until that game work lands with acceptance evidence.</div>
<p>Reference-library palette and serif hierarchy, reused for this offline review. All images are actual GLB renders; no concept art is substituted. Click any pair for full resolution. The 96px views are representative diagnostics, not calibrated game captures.</p>
<p><a href="README.md">Decisions, defects, reproduction &amp; rollback</a> · <a href="resources.json">Resource deltas</a> · <a href="validation.json">Independent preservation</a> · <a href="ground-verification.json">Connector / stack checks</a> · <a href="handoff.json">Assets-main-only handoff</a></p>
<p><strong>Observed:</strong> floors gain recognizable painted leaves, pebbles and grass; wood, stone and cloth gain restrained surface variation. <strong>Limits:</strong> the small enlarged ground swatches blur close-up, pine duff resembles leaf litter, repeated stamps remain visible, and connector endcaps stay quieter. The building change is mainly a close-view improvement; its preserved growth dominates small views. See the written review for per-family judgments.</p>''' + ''.join(cards) + '<footer>Baseline 133c7cdeb368cada408d1c95c9414e08488371a9 · POC content identity <code>' + identity + '</code></footer></main></html>')
    print('Review:', DOCS / 'review.html')
    print('Main-only handoff content identity:', identity)


if __name__ == '__main__':
    main()
