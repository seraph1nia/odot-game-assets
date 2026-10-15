"""Compile actual runtime costs and fixed-camera comparison evidence; never model."""
import html
import json
import shutil
from pathlib import Path

from tools.asset_catalog.metadata import read_glb
from tools.asset_catalog.runtime_glb import read
from tools.asset_pack.ambient_contract import ASSETS, sha

ROOT=Path(__file__).resolve().parents[2]
DOCS=ROOT/'docs/runtime-optimization'
FOCAL=('buildings/magic_academy','buildings/barracks','buildings/town_hall','buildings/arrow_tower',
       'buildings/bakery','buildings/weaver','environment/hex_lantern_bridge','environment/hex_river_overlay_turn_60')


def metrics(path):
    doc,_=read(path);facts=read_glb(path);active=set()
    def visit(i):
        assert i not in active,'repeated node in scene'
        active.add(i)
        for child in doc['nodes'][i].get('children',[]):visit(child)
    for i in doc['scenes'][doc.get('scene',0)]['nodes']:visit(i)
    primitives=[p for i in active if 'mesh' in doc['nodes'][i] for p in doc['meshes'][doc['nodes'][i]['mesh']]['primitives']]
    return {'sha256':facts['version'],'bytes':facts['bytes'],'nodes':len(active),
        'mesh_nodes':sum('mesh' in doc['nodes'][i] for i in active),'mesh_definitions':facts['meshes'],
        'material_definitions':facts['materials'],'surface_instances':len(primitives),
        'triangle_instances':sum(doc['accessors'][p['indices']]['count']//3 for p in primitives),
        'vertex_instances':sum(doc['accessors'][p['attributes']['POSITION']]['count'] for p in primitives),
        'unique_primitive_triangles':facts['triangles'],'animations':facts['animations']}


def main():
    baseline=json.loads((DOCS/'baseline.json').read_text());validation=json.loads((DOCS/'validation.json').read_text())
    godot=json.loads((DOCS/'godot.json').read_text());native={r['path']:r for r in godot['samples']}
    records={}
    for aid in ASSETS:
        before=ROOT/'.cache/runtime-optimization/before/exports'/(aid+'.glb');after=ROOT/'exports'/(aid+'.glb')
        assert sha(before)==baseline['assets'][aid]['facts']['version']
        assert sha(after)==validation['assets'][aid]['glb_sha256']
        records[aid]={'before':metrics(before),'after':metrics(after),
            'godot_before':native['res://before/'+aid+'.glb'],'godot_after':native['res://after/'+aid+'.glb']}
    renders={}
    for aid in FOCAL:
        path=DOCS/'evidence'/aid/'render.json';record=json.loads(path.read_text())
        assert record['before_glb_sha256']==records[aid]['before']['sha256']
        assert record['after_glb_sha256']==records[aid]['after']['sha256']
        for image,digest in record['images'].items():assert sha(ROOT/image)==digest
        renders[aid]=record
    result={'scope':'Actual scene-reachable GLB nodes/surfaces/triangles, including zero-area triangles; unique definitions reported separately. Headless PackedScene measurements are not FPS/GPU qualification.',
        'assets':records,'renders':renders}
    (DOCS/'metrics.json').write_text(json.dumps(result,indent=2)+'\n')
    rows=[]
    def delta(row,key):return f'{row["before"][key]:,} → {row["after"][key]:,}'
    for aid,row in records.items():
        speed=f'{row["godot_before"]["median_instantiate_us"]/1000:.3f} → {row["godot_after"]["median_instantiate_us"]/1000:.3f}'
        rows.append(f'<tr><th>{html.escape(aid)}</th><td>{delta(row,"nodes")}</td><td>{delta(row,"mesh_nodes")}</td><td>{delta(row,"material_definitions")}</td><td>{delta(row,"surface_instances")}</td><td>{delta(row,"triangle_instances")}</td><td>{row["before"]["bytes"]/1e6:.2f} → {row["after"]["bytes"]/1e6:.2f}</td><td>{speed}</td></tr>')
    cards=[]
    for aid in FOCAL:
        pair=''.join(f'<figure><img loading="lazy" src="evidence/{aid}/{stage}-192.png" alt="Actual {stage} {html.escape(aid)}"><figcaption>{stage.title()} · identical camera/lights</figcaption></figure>' for stage in ('before','after'))
        tiny=''.join(f'<img loading="lazy" src="evidence/{aid}/{stage}-96.png" width="96" height="96" alt="Actual {stage} at 96px canvas">' for stage in ('before','after'))
        cards.append(f'<article><h3>{html.escape(aid)}</h3><div class="pair">{pair}</div><div class="tiny">{tiny}</div><p>Mesh nodes {delta(records[aid],"mesh_nodes")} · scene triangle instances {delta(records[aid],"triangle_instances")}</p><details><summary>480px diagnostic originals and camera receipt</summary><a href="evidence/{aid}/before.png">Before</a> · <a href="evidence/{aid}/after.png">After</a> · <a href="evidence/{aid}/render.json">Projection/hash receipt</a></details></article>')
    page='''<!doctype html><html lang="en"><meta charset="utf-8"><meta name="viewport" content="width=device-width"><title>Odot · runtime export review</title><style>
body{margin:32px auto;max-width:1380px;padding:0 22px;background:#20251f;color:#eee7d7;font:16px/1.5 system-ui}h1,h2,h3{font-family:Georgia;font-weight:normal}h1{font-size:42px}a{color:#bdcb83}p{max-width:95ch;color:#d0c6b3}.notice{padding:16px;border-left:4px solid #c99c63;background:#30362b}.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(min(100%,440px),1fr));gap:24px}article{min-width:0;border-top:1px solid #606353;padding:12px 0}h3{overflow-wrap:anywhere}.pair{display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px}figure{margin:0;min-width:0}figure img{width:192px;max-width:100%;height:auto}figcaption{font-size:13px}.tiny{display:flex;gap:16px;margin-top:14px}.table{overflow:auto}table{border-collapse:collapse;font-size:13px;white-space:nowrap}td,th{padding:9px;border-bottom:1px solid #454e3b;text-align:right}th:first-child{text-align:left}code{overflow-wrap:anywhere}details{font-size:14px}.kicker{letter-spacing:.14em;text-transform:uppercase;color:#bdcb83}</style>
<p class="kicker">Actual exports · bounded asset-side optimization</p><h1>Keep the woodland. Lose the node tax.</h1>
<p>Editable detailed Blender sources are byte-identical. Stationary compatible surfaces are consolidated by material and animation owner; small animated targets and placement roots survive. Existing painted textures and every localized loop remain.</p>
<div class="notice"><strong>Read the tradeoff, not just the node reduction.</strong> Consolidation expands shared prototype geometry into shared per-asset buffers, increasing GLB bytes/unique topology while reducing runtime nodes and surfaces. Small moss topology and subpixel bevels are simplified only at export. No game-side framework, shader rewrite or blanket LOD system was added.</div>
<h2>Matched standalone views</h2><p>Actual CPU GLBs rendered at 480px with one unchanged neutral camera/light setup per pair; canonical 192/96px derivatives shown at native canvas sizes. These are gameplay-like diagnostic tiers, not measured game occupied pixels, artist approval or rendered game performance. Retain vivid roof/magic colors, planted overgrowth and each role signature.</p><section class="cards">'''+''.join(cards)+'''</section><h2>All 25 selections · measured before → after</h2><p>Scene-reachable counts, not Blender object prose or guessed draw calls. Triangle instances include all serialized zero-area faces; unique definition totals are separate in the JSON. Instantiation is the median of 11 warm headless Godot trials after one warmup; import, resource loading, add_child, physics and rendering are excluded. First process resource-load and editor import timing are recorded separately; OS cache was not flushed.</p><div class="table"><table><thead><tr><th>Selection</th><th>All nodes</th><th>Mesh nodes</th><th>Materials</th><th>Surfaces</th><th>Triangles</th><th>GLB MB</th><th>Instantiate ms</th></tr></thead><tbody>'''+''.join(rows)+'''</tbody></table></div><h2>Acceptance boundaries</h2><p>Every serialized transformed triangle and attribute is checked one-to-one, including exact zero-area faces, against the unbatched runtime profile. Source-to-GLB position/UV/normal checks use actual float accessors on every corner and explicitly model the pinned exporter’s local four-decimal normal conversion before inverse-transpose. Normal comparisons are fixed at 0.00002, not widened to fit the earlier failure. Encoded PNG bytes, independently decoded samples/alpha, material texture bindings and all clip targets/samples are strict. Blender reimport normal perturbation is independently counterfactually documented, not mistaken for a changed GLB normal.</p><p>All 25 source/export loops are evaluated at five poses; root/static structure remains fixed and endpoints close. Isolated Godot imports also resolve all tracks and exercise the loops. Headless timings do not qualify GPU cost, rendered FPS or actual game-camera acceptance. Use game-side batching only if later real renderer measurements demonstrate a remaining need.</p><p><a href="README.md">Procedure, tactic assessment and downstream handoff</a> · <a href="metrics.json">Full costs and render hashes</a> · <a href="validation.json">Fidelity / loops</a> · <a href="godot.json">Headless measurements</a> · <a href="diagnosis/README.md">Independent fidelity counterfactuals</a></p></html>'''
    (DOCS/'actual-review.html').write_text(page+'\n')
    lavish=ROOT/'.lavish/runtime-optimization';lavish.mkdir(parents=True,exist_ok=True)
    shutil.copytree(DOCS,lavish,dirs_exist_ok=True)
    print('Bound actual runtime comparison:',len(records),'exports;',len(renders),'fixed-camera pairs')


if __name__=='__main__':main()
