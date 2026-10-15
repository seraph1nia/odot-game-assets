"""Bind actual exported key-pose crops, stepped GIFs and the complete motion review."""
import argparse
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
import hashlib
import html
import json
import subprocess
from pathlib import Path

from tools.asset_catalog.metadata import read_glb
from tools.asset_pack import art_style as style
from tools.asset_pack.ambient_contract import ASSETS, receipts, sha
from tools.asset_pack.worker import run_blender

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/ambient-motion'


def render(aid, previous, args, renderer):
    folder = DOCS / 'evidence' / aid
    model = ROOT / 'exports' / (aid + '.glb')
    files = [folder / f'frame-{f:03}.png' for f in style.AMBIENT.frames] + [folder / 'camera.json']
    prior = previous.get(aid, {})
    fresh = prior.get('export_sha256') == sha(model) and prior.get('renderer_sha256') == renderer and all(
        p.exists() and prior.get('files', {}).get(p.relative_to(ROOT).as_posix()) == sha(p) for p in files)
    if not fresh:
        if not args.render:
            raise ValueError('Missing/stale actual motion crops; use --render: ' + aid)
        job = run_blender('tools/asset_pack/render_ambient_blender.py', (aid, folder), blender=args.blender,
                          root=ROOT, label='ambient-render-' + aid.replace('/', '-'))
    else:
        job = prior['job']
    gif = folder / 'key-poses.gif'
    subprocess.run(['magick', '-delay', '100', *map(str, files[:4]), '-loop', '0', str(gif)], check=True)
    strip = folder / 'key-poses.png'
    subprocess.run(['magick', 'montage', '-background', '#262724', '-fill', '#eee7d7', '-font', 'DejaVu-Sans',
                    '-pointsize', '14', *[v for frame, path in zip(style.AMBIENT.frames, files, strict=False)
                    for v in ('-label', f'frame {frame}', str(path))], '-tile', '5x1', '-geometry', '192x192+3+3', str(strip)], check=True)
    return aid, {'export_sha256': sha(model), 'renderer_sha256': renderer, 'job': job,
                 'clip': read_glb(model)['animations'][0], 'files': {p.relative_to(ROOT).as_posix(): sha(p) for p in files + [gif, strip]}}


def page(records):
    features = {f['asset']: f for r in receipts(ROOT).values() for f in r['features']}
    cards = []
    for aid in ASSETS:
        feature = features[aid]
        folder = 'evidence/' + aid
        cards.append(f'<article><h2>{html.escape(aid)}</h2><p>{html.escape(feature["description"])}</p>'
                     f'<img class="gif" src="{folder}/key-poses.gif" alt="Four actual exported key poses, stepped once per second">'
                     f'<p>Five authored keys; actual exported <code>ambient</code> loop. GIF deliberately shows four sampled poses, not runtime smoothness. '
                     f'<a href="../../exports/{aid}.glb">Actual GLB</a> · <a href="{folder}/camera.json">Fixed crop camera</a></p>'
                     f'<details><summary>Matched rest / two extrema / middle / closed endpoint</summary>'
                     f'<img class="strip" src="{folder}/key-poses.png" alt="Five fixed-camera actual GLB poses">'
                     f'</details></article>')
    (DOCS / 'review.html').write_text('''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Small living details · actual exported motion</title><style>
:root{color-scheme:dark}*{box-sizing:border-box}body{margin:0;background:#262724;color:#eee7d7;font:16px/1.6 system-ui}main{max-width:1100px;margin:auto;padding:32px 20px}h1,h2{font-family:Georgia,serif;font-weight:normal;line-height:1.2;overflow-wrap:anywhere}h1{font-size:clamp(32px,5vw,56px)}p{max-width:850px;color:#c0b7a6;overflow-wrap:anywhere}a{color:#bdcb83}article{border-top:1px solid #606353;padding:24px 0}.gif{max-width:100%;width:360px;height:auto}.strip{max-width:100%;height:auto}summary{cursor:pointer}code{overflow-wrap:anywhere}@media(max-width:600px){main{padding:20px 12px}}
</style><main><p>ODOΤ · localized asset motion</p><h1>Small living details.<br>Still grounded.</h1><p>Every one of 16 buildings gets one connected animated spot. Nine water entries cover channels, waterfall streaks, pool foam, both bridge compositions and all four surface river shapes. Static roots, structure, plants and exact connector surfaces remain fixed.</p><p>These are fixed-camera CPU crops of actual published GLBs under unchanged neutral lights. Five authored keys over four seconds are sampled by the existing exporter at 24 FPS (97 samples; clip timestamps start at 1/24 second). Stepped GIFs are evidence of selected poses, not a claim of runtime frame rate, game integration, GPU performance or artist acceptance.</p><p><a href="README.md">Coverage, costs and playback contract</a> · <a href="validation.json">Independent preservation and real mesh playback audit</a> · <a href="renders.json">Exact export/render hashes</a> · <a href="../vivid-palette/actual-review.html">Matched vivid color / overgrowth comparisons</a></p>''' + ''.join(cards) + '</main></html>\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render', action='store_true'); parser.add_argument('--blender')
    args = parser.parse_args()
    path = DOCS / 'renders.json'
    records = json.loads(path.read_text()) if path.exists() else {}
    renderer = hashlib.sha256((''.join(sha(ROOT / p) for p in
        ('tools/asset_pack/render_ambient_blender.py', 'tools/asset_catalog/render_blender.py'))
        + json.dumps(asdict(style.AMBIENT), sort_keys=True)).encode()).hexdigest()
    with ThreadPoolExecutor(max_workers=2) as pool:
        for aid, result in pool.map(lambda a: render(a, records, args, renderer), ASSETS):
            records[aid] = result; path.write_text(json.dumps(records, indent=2) + '\n')
    page(records)
    print('Bound fixed-camera exported motion crops for', len(records), 'assets')


if __name__ == '__main__':
    main()
