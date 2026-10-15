"""Recover only the six greyed SVG palettes, preserving geometry/alpha/native APIs."""
import argparse
import hashlib
import json
import re
import shutil
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DOCS = ROOT / 'docs/vivid-palette'
ART = ('woodland/branch_frame.svg', 'woodland/woodland_corners.svg',
       'woodland/parchment_button.svg', 'woodland/resource_icons.svg',
       'worldtree/foliage_alive.svg', 'worldtree/roots_alive.svg')
COLOR = re.compile(r'#[0-9a-fA-F]{6}\b')


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def recover_colors(current, original):
    colors = COLOR.findall(original)
    if len(colors) != len(COLOR.findall(current)):
        raise ValueError('SVG palette structure differs; manual selection needed')
    iterator = iter(colors)
    result = COLOR.sub(lambda _: next(iterator), current)
    if COLOR.sub('#COLOR', result) != COLOR.sub('#COLOR', current):
        raise ValueError('Nonpalette mutation')
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--apply', action='store_true')
    if not parser.parse_args().apply:
        parser.error('Requires explicit --apply')
    baseline_path = DOCS / 'ui-baseline.json'
    runtime = ROOT / 'ui/preview/UI'
    if not baseline_path.exists():
        before = {p.relative_to(runtime).as_posix(): sha(p) for p in runtime.rglob('*')
                  if p.is_file() and p.suffix not in ('.import', '.uid')}
        baseline_path.write_text(json.dumps(before, indent=2) + '\n')
        shutil.copy2(ROOT / 'docs/ui/worldtree-validation.json', DOCS / 'ui-before-validation.json')
        shutil.copy2(ROOT / 'docs/ui/catalog/previews.json', DOCS / 'ui-before-previews.json')
    baseline = json.loads(baseline_path.read_text())
    rows = []
    for relative in ART:
        source, output = ROOT / 'sources/ui' / relative, runtime / 'art' / relative
        if sha(output) != baseline['art/' + relative]:
            raise ValueError('Changed native palette baseline: ' + relative)
        text = source.read_text()
        original = subprocess.check_output(['git', 'show', 'cadf037:sources/ui/' + relative], cwd=ROOT, text=True)
        source.write_text(recover_colors(text, original))
        shutil.copy2(source, output)
        rows.append({'path': 'art/' + relative, 'before': baseline['art/' + relative], 'after': sha(output),
                     'geometry_and_alpha_unchanged': COLOR.sub('#COLOR', text) == COLOR.sub('#COLOR', source.read_text())})
    for name, expected in baseline.items():
        if name not in {'art/' + p for p in ART} and sha(runtime / name) != expected:
            raise ValueError('Nonpalette native change: ' + name)
    for filename in ('woodland-art.json', 'worldtree-art.json'):
        path = ROOT / 'docs/ui' / filename
        provenance = json.loads(path.read_text())
        for item in provenance['artwork']:
            source, output = ROOT / item['source'], ROOT / item['output']
            if source.read_bytes() != output.read_bytes():
                raise ValueError('Source/runtime mismatch: ' + str(source))
            item['sha256'] = sha(source)
            if 'bytes' in item:
                item['bytes'] = source.stat().st_size
        if 'generator' in provenance:
            provenance['generator_sha256'] = sha(ROOT / provenance['generator'])
        provenance['vivid_refinement'] = 'Restored six original colorful ornamental palettes only; all SVG geometry/alpha/native controls and original seal retained. docs/vivid-palette/ui-refined.json'
        path.write_text(json.dumps(provenance, indent=2) + '\n')
    (DOCS / 'ui-refined.json').write_text(json.dumps({'artwork': rows, 'seal_sha256': sha(runtime / 'art/menu_seal.png'),
        'retained': 'All other native files, interfaces, styles, interactions, SVG geometry/opacity and original seal'}, indent=2) + '\n')
    print('Recovered six SVG palettes; all non-color native bytes unchanged')


if __name__ == '__main__':
    main()
