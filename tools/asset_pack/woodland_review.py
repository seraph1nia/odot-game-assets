"""Inventory-backed before/after actual GLB renders through existing worker/setup.

Before means the preserved original exported bytes, not a simulated reconstruction.
Current exported bytes are rendered for after. Runs incrementally by actual bound
hashes; every render remains a separate isolated Blender process. Not game tests.
"""
import argparse
import hashlib
import json
from pathlib import Path

from tools.asset_pack.worker import run_blender
from tools.asset_catalog.metadata import read_glb

ROOT = Path(__file__).resolve().parents[2]


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--stage', choices=('before', 'after'), required=True)
    parser.add_argument('--blender')
    parser.add_argument('ids', nargs='*')
    args = parser.parse_args()
    baseline = json.loads((ROOT/'docs/whisperwood/baseline.json').read_text())
    ids = {j['id'] for j in baseline['jobs']}
    requested = set(args.ids) if args.ids else ids
    if requested-ids:
        parser.error('Unknown 3D IDs: '+', '.join(sorted(requested-ids)))
    record_path = ROOT/'docs/whisperwood/renders.json'
    records = json.loads(record_path.read_text()) if record_path.exists() else {'scope': 'Actual CPU neutral GLB renders, not native GPU/game-camera or artist acceptance', 'assets': {}}
    renderer_inputs = digest(ROOT/'tools/asset_catalog/render_blender.py') + digest(ROOT/'tools/asset_pack/woodland_render.py')
    renderer = hashlib.sha256(renderer_inputs.encode()).hexdigest()
    for asset_id in sorted(requested):
        model = ROOT/('.cache/whisperwood/before/exports' if args.stage == 'before' else 'exports')/(asset_id+'.glb')
        output = ROOT/'docs/whisperwood/evidence'/args.stage/(asset_id+'.png')
        model_hash = digest(model)
        previous = records['assets'].get(asset_id, {}).get(args.stage, {})
        # Migrate the original concatenated input fingerprint without claiming
        # a new render: the underlying renderer/derivation bytes are identical.
        if previous.get('renderer_sha256') == renderer_inputs:
            previous['renderer_sha256'] = renderer
        tiers = [output.with_name(output.stem+f'-{size}.png') for size in (192, 96)]
        if (previous.get('export_sha256') == model_hash and previous.get('renderer_sha256') == renderer and
                output.exists() and previous.get('image_sha256') == digest(output) and all(p.exists() for p in tiers)):
            # The image binds exported bytes. A verified unchanged export can
            # legitimately survive unrelated edits in its shared source owner.
            previous['derived_images'] = {p.relative_to(ROOT).as_posix(): digest(p) for p in tiers}
            previous['tier_scope'] = 'Canvas sizes; occupied geometry pixels and game views not certified'
            if args.stage == 'after':
                source = ROOT/next(j['source'] for j in baseline['jobs'] if j['id'] == asset_id)
                previous['source_sha256'] = digest(source)
            record_path.write_text(json.dumps(records, indent=2)+'\n')
            continue
        if args.stage == 'before' and model_hash != baseline['files']['exports/'+asset_id+'.glb']['sha256']:
            raise ValueError('Preserved baseline changed: '+asset_id)
        output.parent.mkdir(parents=True, exist_ok=True)
        job = run_blender('tools/asset_pack/woodland_render.py', (model, output), blender=args.blender,
                          root=ROOT, label='whisperwood-'+args.stage+'-'+asset_id.replace('/', '-'))
        facts = read_glb(model)
        data = {'export_sha256': model_hash, 'renderer_sha256': renderer, 'image': output.relative_to(ROOT).as_posix(),
                'image_sha256': digest(output), 'inspection_tiers': [96, 192, 480],
                'tier_scope': 'Canvas sizes; occupied geometry pixels and game views not certified',
                'derived_images': {p.relative_to(ROOT).as_posix(): digest(p) for p in tiers}, 'export_bytes': model.stat().st_size,
                'facts': facts, 'job': job}
        if args.stage == 'after':
            source = ROOT/next(j['source'] for j in baseline['jobs'] if j['id'] == asset_id)
            data['source_sha256'] = digest(source)
        records['assets'].setdefault(asset_id, {})[args.stage] = data
        record_path.write_text(json.dumps(records, indent=2)+'\n')
    print('Bound '+args.stage+' renders:', sum(args.stage in d for d in records['assets'].values()))


if __name__ == '__main__':
    main()
