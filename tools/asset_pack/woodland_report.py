"""Bind the complete catalog to actual refinement/review artifacts.

Run only after saved-source export/style/painted checks and actual renders.
This compiles evidence, never generates an asset or grants artist/game acceptance.
"""
import hashlib
import html
import json
import struct
from pathlib import Path

from .woodland_profiles import BUILDINGS, UNITS

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT/'docs/whisperwood'


def load(name):
    return json.loads((DOCS/name).read_text())


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def resources(path):
    data = path.read_bytes()
    size = struct.unpack_from('<I', data, 12)[0]
    d = json.loads(data[20:20+size])
    nodes = d.get('nodes', [])
    active = set()
    def visit(index):
        if index in active:
            return
        active.add(index)
        for child in nodes[index].get('children', []):
            visit(child)
    for index in d['scenes'][d.get('scene', 0)]['nodes']:
        visit(index)
    primitives = [p for i in active if 'mesh' in nodes[i]
                  for p in d['meshes'][nodes[i]['mesh']]['primitives']]
    return {'active_mesh_nodes': sum('mesh' in nodes[i] for i in active),
            'active_primitive_instances': len(primitives),
            'active_triangle_instances': sum(d['accessors'][p['indices']]['count']//3 for p in primitives),
            'skin_joint_counts': [len(s['joints']) for s in d.get('skins', [])],
            'scope': 'Exported scene instances at mesh-definition topology; not GPU draw calls, animated bounds or performance qualification'}


def main():
    baseline, authored, renders = load('baseline.json'), load('authored.json'), load('renders.json')['assets']
    subparts, ui = load('subparts.json'), load('ui-baseline.json')
    matrix = load('completion.json')
    jobs = {j['id']: j for j in baseline['jobs']}
    rows = []
    for old in matrix['assets']:
        row = dict(old)
        aid = row['id']
        row['source'] = row['source'] or ui['assets'][aid]['source']
        source = ROOT/row['source']
        row['source_sha256_after'] = sha(source)
        row['artist_acceptance'] = 'Not claimed; supplied direction is illustrative, agent review is not artist approval'
        if aid in jobs:
            job, views = jobs[aid], renders[aid]
            assert sha(source) == authored['sources'][job['source']]['sha256_after'] == views['after']['source_sha256'], aid
            assert sha(ROOT/('exports/'+aid+'.glb')) == views['after']['export_sha256'], aid
            for stage, view in views.items():
                assert sha(ROOT/view['image']) == view['image_sha256'], aid
                for image, digest in view['derived_images'].items():
                    assert sha(ROOT/image) == digest, image
            row.update(status='refined', before=views['before']['image'], after=views['after']['image'],
                       export_sha256_after=views['after']['export_sha256'], subparts=subparts[aid],
                       resources_before=views['before']['facts'], resources_after=views['after']['facts'],
                       resource_instances_after=resources(ROOT/('exports/'+aid+'.glb')),
                       resource_instances_before=resources(ROOT/('.cache/whisperwood/before/exports/'+aid+'.glb')),
                       evidence='renders.json / subparts.json / checks.json')
            stem = aid.split('/')[-1]
            if stem in BUILDINGS:
                p = BUILDINGS[stem]
                row['refined_subparts'] = ['muted weathered surface bodies, quiet luminous accents', 'contact-planted roof/facade/root growth', p['signature'], 'purposeful '+p['detail'].replace('_', ' ')+' details']
                row['retained_subparts'] = ['existing role plan, recessed entrance, timber/masonry joints and shingle topology', 'manual UV layers/paint patterns and roughness/normal maps; root/orientation/export selector; embedded shared-kit data']
                row['reason'] = 'Bright tidy dressing needed woodland density and a more exaggerated individual trade cue; fitting architecture retained.'
            elif stem in UNITS:
                row['refined_subparts'] = ['muted faction surfaces and localized glow', UNITS[stem]['signature'], 'weighted traveling equipment and removable gear bindings']
                row['retained_subparts'] = ['readable face/hands, sharp armor facets and original weapons', '19-bone skeleton/weights, socket/grip transforms, 24FPS six clips and armature modifiers']
                row['reason'] = 'Faction/role already read; exaggerate selected cues and add purposeful travel detail, not a common costume.'
            else:
                parts = list(subparts[aid]['detail_parts'])
                row['refined_subparts'] = ['muted related surface shades; restrained luminous accents'] + parts
                row['retained_subparts'] = ['original useful silhouette, topology/UVs, painted variation and roughness/normal data maps', 'origin/attachment scale; hex footprint, flat floor or water interfaces where applicable']
                row['reason'] = ('Flat/detailed receiving floor already has useful paint and must retain its shape; palette-only refinement.' if 'ground_detailed' in row['source'] else
                                 'Add category-appropriate contact/detail layers while retaining the readable base.' if parts else
                                 'Narrow functional/overlay shape already fits; material-only refinement avoids obstructive foliage or a generic wreath.')
        else:
            before = ui['assets'][aid]
            after = 'docs/whisperwood/evidence/after/'+aid+'.png'
            assert (ROOT/after).exists(), aid
            assert sha(ROOT/before['image']) == before['image_sha256'], aid
            retained = sha(ROOT/after) == before['image_sha256']
            row.update(status='retained' if retained else 'refined', before=before['image'], after=after,
                       image_sha256_after=sha(ROOT/after), evidence='ui-refined.json / ../ui/worldtree-validation.json')
            row['refined_subparts'] = [] if retained else ['referenced woodland leaf/violet ornament bodies; alive Worldtree foliage/roots where used']
            row['retained_subparts'] = ['byte-identical native scripts/scenes/Theme resource, fonts, seal identity, layout/hit geometry, API and interactions', 'small amber/cyan functional accents and readable Ledger hierarchy']
            row['reason'] = ('Original seal already fits and identity must remain intact.' if aid=='ui/menu-seal' else
                             'Already quiet readable native control; no visual subpart needed refinement. Original resource and captured pixels are unchanged.' if retained else
                             'Existing woodland Ledger structure fits; refine only ornamental saturation, not UI design.')
        rows.append(row)
    non_catalog = []
    for path, original in baseline['files'].items():
        if path.startswith('sources/') and path.endswith('.blend') and path not in authored['sources']:
            assert sha(ROOT/path) == original['sha256'], path
            non_catalog.append({'source': path, 'status': 'retained', 'sha256': original['sha256'],
                                'reason': 'Original seal authoring source preserved with the unchanged seal.' if '/ui/' in path else
                                'Historical overview assembly preserved to avoid discarding manual assembly edits; not a synchronized Whisperwood output. Canonical per-ID sources/exports/previews are current.'})
    originals = [p for p in baseline['files'] if p.startswith('sources/') and p.endswith('.png') and '/decals/' not in p and '/reference/' not in p and not p.startswith('sources/ui/')]
    for path in originals:
        assert sha(ROOT/path) == baseline['files'][path]['sha256'], path
    matrix.update(assets=rows, non_catalog=non_catalog, decals=load('decals-refined.json'),
                  texture_companions={'original_png_files_retained': len(originals), 'refinement': 'Packed graded color copies/new supported finish maps; existing UVs, original source PNGs and roughness/normal channels retained'},
                  qualification='Mechanical/actual-render evidence only; no actual-game, native-GPU or artist acceptance')
    (DOCS/'completion.json').write_text(json.dumps(matrix, indent=2)+'\n')
    cards=[]
    for r in rows:
        cards.append('<article><h2>'+html.escape(r['id'])+' · '+r['status']+'</h2><div class="pair"><figure><img loading="lazy" src="'+r['before'].removeprefix('docs/whisperwood/')+'"><figcaption>Actual before</figcaption></figure><figure><img loading="lazy" src="'+r['after'].removeprefix('docs/whisperwood/')+'"><figcaption>Actual after</figcaption></figure></div><p>'+html.escape(r['reason'])+'</p><p>Refined: '+html.escape('; '.join(r['refined_subparts']) or 'none')+'</p><p>Retained: '+html.escape('; '.join(r['retained_subparts']))+'</p></article>')
    page='<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Whisperwood actual asset review</title><style>body{margin:32px auto;max-width:1180px;padding:0 20px;background:#20251f;color:#eee7d7;font:16px/1.5 system-ui}h1,h2{font-family:Georgia;font-weight:normal}a{color:#bdcb83}.pair{display:grid;grid-template-columns:1fr 1fr;gap:16px}figure{margin:0}img{width:100%;height:380px;object-fit:contain}article{border-top:1px solid #606353;padding:24px 0}p{color:#c0b7a6}@media(max-width:600px){img{height:210px}}</style><h1>Whisperwood · actual selective refinement</h1><p>All 133 catalog IDs. These are actual exported GLB renders/native captures, not generated mockups. Neutral GLBs use identical renderer/auto-fit procedure, not a fixed camera projection; 96/192/480 are canvas sizes, not certified occupied/game pixels. Mechanical checks and agent inspection do not grant artist/native-GPU/game acceptance.</p><p><a href="README.md">Direction, checks, limitations</a> · <a href="completion.json">Complete retained/refined ledger and resource deltas</a> · <a href="../../sources/reference/whisperwood/direction.png">Supplied illustrative direction</a></p>'+''.join(cards)+'</html>'
    (DOCS/'actual-review.html').write_text(page+'\n')
    print('Bound complete selective ledger:', len(rows), 'catalog IDs;', len(non_catalog), 'preserved noncatalog source owners')


if __name__ == '__main__':
    main()
