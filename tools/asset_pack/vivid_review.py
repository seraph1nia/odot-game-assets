"""Bind full-catalog actual neutral GLB comparisons; historical ledgers stay read-only."""
import argparse
from concurrent.futures import ThreadPoolExecutor
import hashlib
import html
import json
import shutil
import subprocess
import struct
from pathlib import Path

from tools.asset_catalog.metadata import read_glb
from tools.asset_pack.worker import run_blender
from tools.asset_pack.woodland_report import resources, sha

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/vivid-palette'
FOCAL = ('buildings/woodcutter_hut', 'buildings/bakery', 'buildings/weaver',
         'buildings/magic_academy', 'characters/knight', 'characters/evil_mage_unit',
         'environment/hex_glowing_mushrooms', 'environment/hex_crystal_grove',
         'environment/hex_ground_leaf_litter', 'environment/hex_river_overlay_turn_60',
         'environment/components/forest_lantern_snail', 'props/staff')


def reason(aid):
    if aid.startswith('buildings/'):
        return 'Recover warm timber, distinct roof/cloth colors and amber craft accents; retain dense planted ivy/moss, working signatures and all second-round focal shapes/rest lanes.'
    if aid.startswith('characters/'):
        return 'Recover faction/role cloth, hair, warm skin and equipment hues; retain traveling layers, readable faces/grips, rig/sockets and all six clips. Low emission strengths retained.'
    if '/hex_ground_' in aid or '/hex_path_' in aid or '/hex_river_overlay_' in aid:
        return 'Recover living ground/ochre litter or teal water colors and related fine washes; preserve flat occupation planes, footprint, alpha and connector endpoints.'
    if aid.startswith('environment/'):
        return 'Recover green/teal foliage, blue/violet shaded magic and warm wood/fauna accents with fine related variation; preserve planted overgrowth, facets, shared prototypes and tile composition.'
    return 'Recover material-specific warm wood/leather, role colors and metal accents; retain functional silhouette, fine grip/joint detail, hierarchy and shared mesh ownership.'


def render_one(job, args, baseline, old, second, renderer, previous):
    aid = job['id']
    model = ROOT / ('exports/' + aid + '.glb')
    source = ROOT / job['source']
    inherited = second.get(aid, old[aid])['after']
    assert inherited['export_sha256'] == baseline['files']['exports/' + aid + '.glb'], aid
    assert inherited['source_sha256'] == baseline['files'][job['source']], aid
    assert inherited['renderer_sha256'] == renderer, aid
    before = dict(inherited)
    before['derived_images'] = {}
    for size in (None, 192, 96):
        original = ROOT / inherited['image']
        if size:
            original = original.with_name(original.stem + f'-{size}.png')
            expected = inherited['derived_images'][original.relative_to(ROOT).as_posix()]
        else:
            expected = inherited['image_sha256']
        assert sha(original) == expected, original
        target = DOCS / 'evidence/before' / (aid + (f'-{size}' if size else '') + '.png')
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(original, target)
        if size:
            before['derived_images'][target.relative_to(ROOT).as_posix()] = expected
        else:
            before['image'] = target.relative_to(ROOT).as_posix()
    output = DOCS / 'evidence/after' / (aid + '.png')
    output.parent.mkdir(parents=True, exist_ok=True)
    prior = previous.get(aid, {}).get('after', {})
    derivatives = [output.with_name(output.stem + f'-{s}.png') for s in (192, 96)]
    fresh = (prior.get('export_sha256') == sha(model) and prior.get('renderer_sha256') == renderer
             and output.exists() and prior.get('image_sha256') == sha(output)
             and all(p.exists() and prior.get('derived_images', {}).get(p.relative_to(ROOT).as_posix()) == sha(p) for p in derivatives))
    if args.render and not fresh:
        run = run_blender('tools/asset_pack/woodland_render.py', (model, output), blender=args.blender,
                          root=ROOT, label='vivid-render-' + aid.replace('/', '-'))
    elif fresh:
        run = prior['job']
    else:
        raise ValueError('Missing/stale actual render; use --render: ' + aid)
    after = {'image': output.relative_to(ROOT).as_posix(), 'image_sha256': sha(output),
             'source_sha256': sha(source), 'export_sha256': sha(model), 'renderer_sha256': renderer,
             'derived_images': {p.relative_to(ROOT).as_posix(): sha(p) for p in derivatives}, 'job': run,
             'facts': read_glb(model)}
    rb, ra = resources(ROOT / '.cache/vivid-palette/before/exports' / (aid + '.glb')), resources(model)
    for key in ('meshes', 'triangles', 'materials', 'animations'):
        assert before['facts'][key] == after['facts'][key], (aid, key)
    for key in ('active_mesh_nodes', 'active_primitive_instances', 'active_triangle_instances', 'skin_joint_counts'):
        assert rb[key] == ra[key], (aid, key, rb[key], ra[key])
    # Canonical actual thumbnail, generated by the existing catalog renderer.
    thumb = ROOT / 'exports/thumbnails' / (aid + '.png')
    thumb.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(output, thumb)
    return aid, {'before': before, 'after': after, 'resources_before': rb, 'resources_after': ra}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render', action='store_true')
    parser.add_argument('--blender')
    args = parser.parse_args()
    baseline = json.loads((DOCS / 'baseline.json').read_text())
    authored = json.loads((DOCS / 'authored.json').read_text())
    old = json.loads((ROOT / 'docs/whisperwood/renders.json').read_text())['assets']
    second = json.loads((ROOT / 'docs/quality-round-two/renders.json').read_text())['assets']
    renderer = hashlib.sha256((sha(ROOT / 'tools/asset_catalog/render_blender.py') + sha(ROOT / 'tools/asset_pack/woodland_render.py')).encode()).hexdigest()
    records_path = DOCS / 'renders.json'
    records = json.loads(records_path.read_text()) if records_path.exists() else {'assets': {}}
    for path, item in authored.items():
        assert sha(ROOT / path) == item['sha256_after'], path
    with ThreadPoolExecutor(max_workers=2) as pool:
        for aid, record in pool.map(lambda j: render_one(j, args, baseline, old, second, renderer, records['assets']), baseline['jobs']):
            records['assets'][aid] = record
            records['scope'] = 'Actual neutral CPU GLBs and canonical 192/96 derivatives; identical renderer/auto-fit; no preview grading, game/GPU/artist acceptance'
            records_path.write_text(json.dumps(records, indent=2) + '\n')
    # A catalog-wide sheet for each family, with actual landed/current pairs.
    sheets = make_sheets(records['assets'])
    rows = []
    for job in baseline['jobs']:
        aid, path = job['id'], job['source']
        data = (ROOT / 'exports' / (aid + '.glb')).read_bytes()
        length = struct.unpack_from('<I', data, 12)[0]
        selected_materials = {m['name'] for m in json.loads(data[20:20 + length]).get('materials', [])}
        rows.append({'id': aid, 'status': 'refined', 'reason': reason(aid), 'source': path,
                     'source_sha256': sha(ROOT / path), 'evidence': records['assets'][aid],
                     'refined_subparts': [m['name'] for m in authored[path]['materials'] if m['status'] == 'refined' and m['name'] in selected_materials],
                     'retained_subparts': ['all original and added geometry/UVs/root hierarchy/reuse/rigs/actions',
                                          'all roughness/normal image pixels, alpha and emission strength',
                                          'unlinked authored prototypes/materials protected from serialization loss']})
    old_inventory = json.loads((ROOT / 'docs/quality-round-two/inventory.json').read_text())['assets']
    # Current catalog manifest binds the native captures; original seal is not rerendered.
    previews = json.loads((ROOT / 'docs/ui/catalog/previews.json').read_text())
    prior_ui = json.loads((DOCS / 'ui-before-previews.json').read_text())
    for row in old_inventory:
        aid = row['id']
        if not aid.startswith('ui/'):
            continue
        stem = aid.split('/')[-1]
        current = previews['entries'].get(stem)
        prior = prior_ui['entries'].get(stem)
        changed = bool(current and prior and current['sha256'] != prior['sha256'])
        for stage, view in (('before', prior), ('after', current)):
            if view:
                target = DOCS / 'evidence' / stage / (aid + '.png')
                target.parent.mkdir(parents=True, exist_ok=True)
                assert sha(ROOT / view['path']) == view['sha256']
                shutil.copy2(ROOT / view['path'], target)
        rows.append({'id': aid, 'status': 'refined' if changed else 'retained', 'source': row['source'],
                     'source_sha256': sha(ROOT / row['source']), 'before': prior, 'after': current,
                     'reason': 'Recover only affected six-SVG ornamental colors; native geometry/alpha/API/layout/states/fonts retained' if changed else 'No affected grey ornament in this view; preserve existing native presentation and original seal identity',
                     'retained_subparts': ['native code/layout/theme metrics/interfaces, original seal, SVG geometry and alpha'],
                     'evidence': 'ui-refined.json / ../ui/worldtree-validation.json'})
    assert len(rows) == 133 and len({r['id'] for r in rows}) == 133
    (DOCS / 'inventory.json').write_text(json.dumps({'baseline_revision': 'cfdb114', 'counts': {'assessed': 133, 'refined': sum(r['status'] == 'refined' for r in rows), 'retained': sum(r['status'] == 'retained' for r in rows)}, 'assets': rows}, indent=2) + '\n')
    sheets['paths'] = sorted(set(sheets['paths'] + make_ui_sheets([r for r in rows if r['id'].startswith('ui/')])))
    write_page(records['assets'], sheets)
    print('Bound 118 actual neutral pairs and all 133 catalog IDs')


def make_sheets(records):
    """Labeled contact sheets with installed ImageMagick; never recolor images."""
    folder = DOCS / 'evidence/sheets'
    folder.mkdir(parents=True, exist_ok=True)
    for family in ('buildings', 'characters', 'environment', 'props'):
        ids = sorted(aid for aid in records if aid.startswith(family + '/'))
        for start in range(0, len(ids), 16):
            command = ['magick', 'montage', '-background', '#262724', '-fill', '#eee7d7',
                       '-font', 'DejaVu-Sans', '-pointsize', '11']
            for aid in ids[start:start + 16]:
                for stage in ('before', 'after'):
                    command += ['-label', aid.rsplit('/', 1)[-1] + ' / ' + stage, str(ROOT / records[aid][stage]['image'])]
            command += ['-tile', '8x', '-geometry', '172x172+3+3', '-depth', '8', '-define', 'png:color-type=2', str(folder / f'{family}-{start // 16 + 1}.png')]
            subprocess.run(command, check=True, cwd=ROOT)
    return {'recipe': 'ImageMagick montage, actual 480px images fitted 172px, labels, 8 columns; no color grade',
            'paths': sorted(p.relative_to(DOCS).as_posix() for p in folder.glob('*.png'))}


def make_ui_sheets(rows):
    paths = []
    for start in range(0, len(rows), 8):
        command = ['magick', 'montage', '-background', '#262724', '-fill', '#eee7d7',
                   '-font', 'DejaVu-Sans', '-pointsize', '12']
        for row in rows[start:start + 8]:
            for stage in ('before', 'after'):
                view = row.get(stage)
                image = ROOT / view['path'] if view else ROOT / row['source']
                command += ['-label', row['id'] + ' / ' + stage, str(image)]
        path = DOCS / 'evidence/sheets' / f'ui-{start // 8 + 1}.png'
        command += ['-tile', '4x', '-geometry', '288x216+4+4', '-depth', '8', '-define', 'png:color-type=2', str(path)]
        subprocess.run(command, check=True, cwd=ROOT)
        paths.append(path.relative_to(DOCS).as_posix())
    return paths


def write_page(records, sheets):
    cards = []
    for aid in FOCAL:
        rec = records[aid]
        pair = ''.join(f'<figure><img src="{rec[s]["image"].removeprefix("docs/vivid-palette/")}" alt="Actual {s} {html.escape(aid)}"><figcaption>{s.title()} · neutral actual GLB</figcaption></figure>' for s in ('before', 'after'))
        small = ''.join(f'<img width="96" height="96" src="evidence/{s}/{aid}-96.png" alt="96px canvas {s}">' for s in ('before', 'after'))
        rb, ra = rec['resources_before'], rec['resources_after']
        costs = '; '.join(f'{k}: {rb[k]:,} → {ra[k]:,}' for k in ('active_mesh_nodes', 'active_triangle_instances'))
        cards.append(f'<article><h2>{html.escape(aid)}</h2><p>{reason(aid)}</p><div class="pair">{pair}</div><p class="small">96px canvas {small}</p><p>{costs}. Geometry retained, not a tested GPU budget.</p></article>')
    for stem in ('hud', 'worldtree'):
        pair = ''.join(f'<figure><img src="evidence/{stage}/ui/{stem}.png" alt="Actual native {stage} {stem}"><figcaption>{stage.title()} · actual native Godot capture</figcaption></figure>' for stage in ('before', 'after'))
        cards.append(f'<article><h2>ui/{stem}</h2><p>Only affected ornamental palettes recovered. Native geometry, alpha, code/layout/state metrics, intent API and original seal unchanged; standalone mock data, not game evidence.</p><div class="pair">{pair}</div></article>')
    sheet_html = ''.join(f'<details><summary>{html.escape(Path(p).stem)}</summary><img class="sheet" src="{p}" alt="Full catalog actual pairs {Path(p).stem}"></details>' for p in sheets['paths'])
    page = '''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Vivid color, retained overgrowth</title><style>
:root{color-scheme:dark;--bg:#262724;--panel:#333530;--ink:#eee7d7;--muted:#c0b7a6;--line:#606353;--accent:#bdcb83}*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--ink);font:16px/1.6 system-ui}main{max-width:1180px;margin:auto;padding:32px 20px}h1,h2{font-family:Georgia,serif;font-weight:normal;line-height:1.2}h1{font-size:clamp(32px,5vw,60px)}h2{overflow-wrap:anywhere}a{color:var(--accent)}p,figcaption{color:var(--muted);overflow-wrap:anywhere}.pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:16px}figure{margin:0;min-width:0}figure img,.sheet{width:100%;height:auto}article{border-top:1px solid var(--line);padding:24px 0}.small img{vertical-align:middle}details{margin:18px 0;border:1px solid var(--line);padding:12px}summary{cursor:pointer}table{border-collapse:collapse;width:100%}td,th{padding:10px;border-bottom:1px solid var(--line);text-align:left;overflow-wrap:anywhere}@media(max-width:600px){main{padding:20px 12px}.pair{gap:8px}}
</style><main><p>ODOΤ · actual asset evidence</p><h1>Vivid color.<br>Still overgrown.</h1><p>Restore colorful material bodies, not the old bare geometry. Landed grey baseline versus current exported source colors under the unchanged neutral renderer. No post-render saturation or lighting trick. All 118 models and 15 native UI entries accounted for.</p><table><tr><th>Recovered</th><th>Retained</th><th>Not qualified</th></tr><tr><td>Blue/terracotta roofs, warm timber, faction cloth, living greens, cyan/violet bodies; restrained local painted variation.</td><td>Dense planted growth, distinct working signatures, second-round focal refinements, shared foliage, roots/rigs/clips and original seal.</td><td>Actual game consumption/camera, GPU budget, artist acceptance and animation appeal.</td></tr></table><p><a href="README.md">Direction, judgments and checks</a> · <a href="inventory.json">133-ID inventory</a> · <a href="renders.json">Exact evidence hashes and resource counts</a> · <a href="../../sources/reference/index.html">Original illustrative inspiration (not acceptance)</a></p>'''
    (DOCS / 'actual-review.html').write_text(page + ''.join(cards) + '<h2>Full-catalog actual contact sheets</h2>' + sheet_html + '</main></html>\n')


if __name__ == '__main__':
    main()
