"""Sync selected muted ornament palettes, retaining native structure/behavior/seal.

Explicit authoring for Whisperwood. Four manually edited woodland SVGs are
source-owned; two existing Worldtree foliage SVGs receive only specified palette
replacements. Nothing regenerates controls, topology, icons, geometry or fonts.
"""
import hashlib
import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
WORLD_COLORS = {'#9baf56': '#84916e', '#d0bf68': '#b3b48c',
                '#879d50': '#70815d', '#bdba6d': '#a0a780'}


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    baseline = json.loads((ROOT/'docs/whisperwood/ui-baseline.json').read_text())
    for relative, expected in baseline['runtime'].items():
        path = ROOT/'ui/preview/UI'/relative
        if path.suffix in ('.gd', '.tscn', '.tres', '.png', '.ttf') and digest(path) != expected:
            raise ValueError('Unintended native behavior/structure/identity edit: '+relative)
    changes = {}
    for family, names in [('woodland', ('branch_frame', 'woodland_corners', 'parchment_button', 'resource_icons')),
                          ('worldtree', ('foliage_alive', 'roots_alive'))]:
        for name in names:
            relative = 'art/'+family+'/'+name+'.svg'
            source = ROOT/'sources/ui'/family/(name+'.svg')
            output = ROOT/'ui/preview/UI'/relative
            if digest(output) != baseline['runtime'][relative] and output.read_bytes() != source.read_bytes():
                raise ValueError('Unpreserved runtime ornament: '+relative)
            text = source.read_text()
            if family == 'worldtree':
                for original, replacement in WORLD_COLORS.items():
                    text = text.replace(original, replacement)
                source.write_text(text)
            shutil.copy2(source, output)
            changes[relative] = {'before': baseline['runtime'][relative], 'after': digest(output),
                                 'refined': 'saturated ornament body palette only',
                                 'retained': 'SVG path geometry, dimensions, alpha ownership, native state/text/behavior'}
    for filename in ('woodland-art.json', 'worldtree-art.json'):
        path = ROOT/'docs/ui'/filename
        provenance = json.loads(path.read_text())
        for art in provenance['artwork']:
            source, output = ROOT/art['source'], ROOT/art['output']
            if source.read_bytes() != output.read_bytes():
                raise ValueError('Source/runtime artwork mismatch: '+art['source'])
            art['sha256'] = digest(source)
            if 'bytes' in art:
                art['bytes'] = source.stat().st_size
        if 'generator' in provenance:
            provenance['generator_sha256'] = digest(ROOT/provenance['generator'])
        provenance['whisperwood_refinement'] = 'Muted selected ornament bodies; existing structure, native contrast/states, topology and original seal retained. docs/whisperwood/ui-refined.json binds before/after.'
        path.write_text(json.dumps(provenance, indent=2)+'\n')
    result = {'scope': 'Six selected SVG ornamental palettes; no UI redesign, runtime code, native layout or original seal change',
              'changes': changes, 'seal_sha256': digest(ROOT/'ui/preview/UI/art/menu_seal.png'),
              'retained_native_files': {p: h for p, h in baseline['runtime'].items() if p.endswith(('.gd', '.tscn', '.tres', '.png', '.ttf'))}}
    (ROOT/'docs/whisperwood/ui-refined.json').write_text(json.dumps(result, indent=2)+'\n')
    print('Synced six selected SVG ornament refinements; all native code/layout/theme bindings, icons/topology, font and original seal retained')


if __name__ == '__main__':
    main()
