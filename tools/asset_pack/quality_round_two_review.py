"""Bind second-round inventory and matched actual views using the canonical renderer.

Historical Whisperwood evidence is read-only. Renders selected changed GLBs via
woodland_render.py, retaining its exact renderer fingerprint and derivative paths.
"""
import argparse
import hashlib
import html
import json
import shutil
from pathlib import Path

from tools.asset_catalog.metadata import read_glb
from tools.asset_pack.worker import run_blender
from tools.asset_pack.woodland_report import resources, sha

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/quality-round-two'

REASONS = {
    'bakery': 'Layered shelter recovered from flat brown oval; warm ochre/cream separates bread canopy from timber while the window, wheat and bread stay focal.',
    'weaver': 'Folds and narrow selvedges now carry weaving craft; a quiet ridge lane reduces independent competing growth without changing embedded shingles or loom.',
    'magic_academy': 'Shaded orb now has volume rather than a lilac light disk; thin armillary bands identify scholarly magic. Purple crystal and narrow window glow remain intact.',
    'town_hall': 'Civic bell brought into its opening with a slight ringing lean; independent canopy growth thinned at the front, retaining antler-like branch and emblem identity.',
    'woodcutter_hut': 'Purposeful saw-tooth silhouette and hoist pulley distinguish the working wheel from a wagon wheel without adding another growth layer. Suspended log retained: changing its supports adds complexity without a reliable small-view gain.',
}


def retained_reason(aid):
    stem = aid.rsplit('/', 1)[-1]
    if aid == 'ui/menu-seal':
        return 'Original seal identity and relief already fit; original pixels/resources remain unchanged.'
    if aid.startswith('ui/'):
        return 'Native Ledger hierarchy, restrained woodland ornament and existing contrast already fit; no interface, interaction, layout, artwork or qualification change needed.'
    if aid.startswith('characters/'):
        return 'Clear ' + stem.replace('_', ' ') + ' face, weapon negative space and faction/role silhouette already survive the small neutral view; traveling detail fits. Retain rig, sockets, six clips and pose rather than invent motion evidence from stills.'
    if 'hex_ground_' in aid or 'hex_path_' in aid or 'hex_river_overlay_' in aid:
        return 'Flat painted ' + stem.replace('hex_', '').replace('_', ' ') + ' has legible rest area and must retain occupation/connector contracts; additional raised detail would obstruct composability.'
    if '/components/' in aid:
        return 'The ' + stem.removeprefix('forest_').replace('_', ' ') + ' prototype has readable facet/organic/structural silhouette and appropriate contact detail. Preserve canonical geometry/reuse; no speculative independent kit variation.'
    if aid.startswith('environment/'):
        return 'The ' + stem.removeprefix('hex_').replace('_', ' ') + ' composition keeps focal crystal/cap/tree, quiet ground and planted contacts; retain footprint, layered heights and water interfaces. No evidence of a beneficial additional layer.'
    if aid.startswith('props/'):
        return 'The ' + stem.removeprefix('kit_').replace('_', ' ') + ' functional silhouette, wrap/joint/facet detail and muted material separation fit. More dressing would blur grip/use or repeat growth.'
    return 'The ' + stem.replace('_', ' ') + ' working signature remains distinct at small size and its roof/entrance separation is sufficient; fitting source-preserved role structure needs no generic extra ornament.'


def cached_job(model, output, renderer, previous):
    """Fail closed on stale full-size or either canonical review derivative."""
    if (previous.get('export_sha256') != sha(model) or
            previous.get('renderer_sha256') != renderer or
            previous.get('image_sha256') != sha(output)):
        raise ValueError('Stale actual after view; explicitly rerender: ' + str(output))
    for size in (192, 96):
        path = output.with_name(output.stem + f'-{size}.png')
        expected = previous.get('derived_images', {}).get(path.relative_to(ROOT).as_posix())
        if not path.is_file() or expected != sha(path):
            raise ValueError('Missing/stale canonical derivative: ' + str(path))
    return previous['job']


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--render', action='store_true', help='Explicit authorized changed-export renders only')
    args = parser.parse_args()
    old = json.loads((ROOT / 'docs/whisperwood/completion.json').read_text())
    old_renders = json.loads((ROOT / 'docs/whisperwood/renders.json').read_text())['assets']
    baseline = json.loads((DOCS / 'baseline.json').read_text())
    authored = json.loads((DOCS / 'authored.json').read_text())
    names = [Path(p).stem for p in authored]
    renderer = hashlib.sha256((sha(ROOT / 'tools/asset_catalog/render_blender.py') + sha(ROOT / 'tools/asset_pack/woodland_render.py')).encode()).hexdigest()
    records = {'scope': 'Actual CPU neutral GLBs; same canonical renderer and auto-fit, not fixed projection/game/GPU/artist acceptance', 'assets': {}}
    for name in names:
        aid = 'buildings/' + name
        source = 'sources/' + aid + '.blend'
        model = 'exports/' + aid + '.glb'
        assert sha(ROOT / source) == authored[source]['sha256_after']
        before = dict(old_renders[aid]['after'])
        assert before['renderer_sha256'] == renderer
        assert before['export_sha256'] == baseline[model]
        assert before['source_sha256'] == baseline[source]
        before['derived_images'] = {}
        for suffix in ('', '-192', '-96'):
            src = ROOT / ('docs/whisperwood/evidence/after/' + aid + suffix + '.png')
            dst = DOCS / 'evidence/before' / (aid + suffix + '.png')
            expected = old_renders[aid]['after']['image_sha256'] if not suffix else old_renders[aid]['after']['derived_images'][src.relative_to(ROOT).as_posix()]
            assert sha(src) == expected
            dst.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(src, dst)
            if not suffix:
                before['image'] = dst.relative_to(ROOT).as_posix()
            else:
                before['derived_images'][dst.relative_to(ROOT).as_posix()] = expected
        before['provenance'] = 'Exact landed first-round after image bytes and canonical renderer/derivative binding; not re-rendered or reconstructed'
        output = DOCS / 'evidence/after' / (aid + '.png')
        output.parent.mkdir(parents=True, exist_ok=True)
        job = run_blender('tools/asset_pack/woodland_render.py', (ROOT / model, output), root=ROOT, label='quality-two-' + name) if args.render else None
        if not output.exists():
            raise ValueError('Missing actual after render; explicitly pass --render')
        if job is None:
            previous = json.loads((DOCS / 'renders.json').read_text())['assets'][aid]['after']
            job = cached_job(ROOT / model, output, renderer, previous)
        after = {'image': output.relative_to(ROOT).as_posix(), 'image_sha256': sha(output),
                 'export_sha256': sha(ROOT / model), 'source_sha256': sha(ROOT / source),
                 'renderer_sha256': renderer, 'inspection_tiers': [96, 192, 480],
                 'tier_scope': before['tier_scope'], 'job': job,
                 'derived_images': {output.with_name(name + f'-{s}.png').relative_to(ROOT).as_posix(): sha(output.with_name(name + f'-{s}.png')) for s in (192, 96)},
                 'facts': read_glb(ROOT / model)}
        records['assets'][aid] = {'before': before, 'after': after,
            'resources_before': resources(ROOT / '.cache/quality-round-two/before' / model),
            'resources_after': resources(ROOT / model)}
    (DOCS / 'renders.json').write_text(json.dumps(records, indent=2) + '\n')
    rows = []
    for row in old['assets']:
        aid = row['id']
        name = aid.rsplit('/', 1)[-1]
        selected = aid in records['assets']
        source = row['source']
        item = {'id': aid, 'status': 'refined' if selected else 'retained', 'source': source,
                'source_sha256': sha(ROOT / source), 'reason': REASONS[name] if selected else retained_reason(aid),
                'reviewer': 'implementation agent; actual image inspection, not commissioned artist acceptance',
                'baseline_image': row['after'], 'baseline_image_sha256': sha(ROOT / row['after'])}
        if not selected:
            assert item['source_sha256'] == row['source_sha256_after'], aid
            if row['kind'] == 'glb':
                item['export_sha256'] = sha(ROOT / ('exports/' + aid + '.glb'))
                assert item['export_sha256'] == row['export_sha256_after'], aid
            item['retained_subparts'] = row['retained_subparts'] + row['refined_subparts']
        else:
            item.update(evidence=records['assets'][aid], refined_subparts=authored[source]['focal_changes'],
                        retained_subparts=['root/export selector/identity', 'original UV/roughness/normal maps except named newly colored porch material', 'embedded kit children and shared mesh data', 'all other structural/trade features'],
                        rules=['D01', 'D03', 'D04', 'D05', 'D06', 'D08', 'D09'],
                        authored=authored[source])
        rows.append(item)
    assert len(rows) == 133 and len({r['id'] for r in rows}) == 133
    ledger = {'baseline_revision': '5cda624', 'baseline_evidence': 'docs/whisperwood/completion.json',
              'scope': 'Five selective focal building edits, all 133 existing IDs assessed; native UI retained; historical first-round ledgers read-only',
              'counts': {'assessed': 133, 'refined': 5, 'retained': 128}, 'assets': rows,
              'limits': 'Headless checks/CPU images only; game camera, native GPU timing/draw calls, artist acceptance and animation appeal untested'}
    (DOCS / 'inventory.json').write_text(json.dumps(ledger, indent=2) + '\n')
    cards = []
    for aid, rec in records['assets'].items():
        name = aid.split('/')[-1]
        images = ''
        for stage in ('before', 'after'):
            path = rec[stage]['image'].removeprefix('docs/quality-round-two/')
            images += f'<figure><img src="{path}" alt="Actual {stage} {name}"><figcaption>{stage.title()} · actual neutral GLB</figcaption></figure>'
        counts = rec['resources_before'], rec['resources_after']
        cost = '; '.join(f'{key}: {counts[0][key]:,} → {counts[1][key]:,}' for key in ('active_mesh_nodes', 'active_triangle_instances'))
        small = ''.join(f'<img class="tier" width="96" height="96" src="evidence/{stage}/{aid}-96.png" alt="96 canvas {stage}">' for stage in ('before', 'after'))
        cards.append(f'<article><h2>{html.escape(aid)}</h2><p>{html.escape(REASONS[name])}</p><div class="pair">{images}</div><p>96px canvas · {small}</p><p>{cost}. Counts, not tested game performance.</p></article>')
    page = '<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Whisperwood second quality round</title><style>body{margin:32px auto;max-width:1120px;padding:0 20px;background:#20251f;color:#eee7d7;font:16px/1.5 system-ui}h1,h2{font-family:Georgia;font-weight:normal}a{color:#bdcb83}.pair{display:grid;grid-template-columns:minmax(0,1fr) minmax(0,1fr);gap:16px}figure{margin:0;min-width:0}figure img{width:100%;max-height:480px;object-fit:contain}.tier{vertical-align:middle}article{border-top:1px solid #606353;padding:24px 0}p{color:#c0b7a6;overflow-wrap:anywhere}@media(max-width:600px){body{padding:0 12px}.pair{gap:8px}}</style><h1>Whisperwood · craft, rest planes, focal light</h1><p>133 assessed · five buildings refined · 128 IDs retained. Existing muted gloomy woodland direction, not a new theme. Before = exact landed first-round after bytes. Identical canonical neutral renderer and automatic fit; not a frozen camera projection or measured game occupied size. Actual after exports, not illustrations.</p><p><a href="README.md">Observations, check procedure and limits</a> · <a href="inventory.json">Full per-ID inventory</a> · <a href="renders.json">Exact renderer/image/export/derivative bindings</a> · <a href="../../sources/reference/whisperwood/direction.png">Original illustrative W0 board</a></p>' + ''.join(cards) + '<h2>Retained families and acceptance limits</h2><p>Units keep face/weapon/faction/rig identity; terrain keeps focal shapes and connectors; props keep working silhouette and grip; native UI keeps existing contrast, API, interactions and original seal. All rows have a retained/refined reason in the ledger. Surviving contact growth retains shared source instances; selective thinning is not a GPU batching or performance promise. CPU renders and headless export/style/texture fixtures are not actual-game, GPU, artist or motion acceptance.</p></html>'
    (DOCS / 'actual-review.html').write_text(page + '\n')
    print('Bound second quality round: 133 assessed, 5 refined, 128 retained; exact canonical renderer', renderer)


if __name__ == '__main__':
    main()
