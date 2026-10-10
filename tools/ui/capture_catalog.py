"""Small focused native UI catalog exports; preserves all historical evidence."""
import argparse
import json
import os
import sys

from capture_explorations import ROOT, run_owned

sys.path.insert(0, str(ROOT))
from tools.asset_catalog.ui_assets import (PREVIEWS, PROJECT, digest, preview_sources,
                                           published_items)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', required=True)
    parser.add_argument('--dotnet-root')
    parser.add_argument('--label', required=True, help='New evidence directory; never overwritten')
    args = parser.parse_args()
    if not args.label.replace('-', '').replace('_', '').isalnum():
        parser.error('label must be a simple run name')
    cache = ROOT / '.cache/ui-catalog' / args.label
    output = ROOT / 'docs/ui/catalog' / args.label
    cache.mkdir(parents=True, exist_ok=False)
    output.mkdir(parents=True, exist_ok=False)
    env = os.environ.copy()
    env.update(LIBGL_ALWAYS_SOFTWARE='1', GALLIUM_DRIVER='llvmpipe')
    for kind in ('DATA', 'CONFIG', 'CACHE'):
        path = cache / kind.lower()
        path.mkdir()
        env['XDG_' + kind + '_HOME'] = str(path)
    if args.dotnet_root:
        env['DOTNET_ROOT'] = args.dotnet_root
        env['PATH'] = args.dotnet_root + os.pathsep + env['PATH']
    engine = [args.godot, '--path', str(ROOT / PROJECT), '--audio-driver', 'Dummy']
    run_owned([*engine, '--headless', '--editor', '--import'], env, cache / 'import.log')
    sources = preview_sources(ROOT)
    display = ['xvfb-run', '-a', '--auth-file', str(cache / 'display.auth'),
               '-e', str(cache / 'xvfb.log'), '-s', '-screen 0 1280x720x24 -nolisten tcp']
    rendering = ['--rendering-method', 'gl_compatibility', '--rendering-driver', 'opengl3', '--max-fps', '30']
    text = run_owned([*display, *engine, '--script', 'res://catalog/capture.gd',
                      '--resolution', '640x480', *rendering, '--', '--output=' + str(output)],
                     env, cache / 'focused.log', timeout=90)
    observed = {line.split()[1]: line.split()[2] for line in text.splitlines()
                if line.startswith('UI_CATALOG_CAPTURE ')}
    for identity, screen in (('hud', 'hud'), ('start-menu', 'menu')):
        text += run_owned([*display, *engine, 'res://prototypes/showcase.tscn',
                           '--resolution', '1280x720', *rendering, '--', '--screen=' + screen,
                           '--capture=' + str(output / (identity + '.png'))],
                          env, cache / (identity + '.log'))
    if preview_sources(ROOT) != sources:
        raise RuntimeError('Source changed during capture')
    inventory = json.loads((ROOT / 'docs/ui/inventory.json').read_text())
    entries = {}
    for item, resource in published_items(inventory):
        if item['id'] == 'watch-seal':
            continue
        path = output / (item['id'] + '.png')
        composition = item['kind'] == 'composition'
        if not composition and observed.get(item['id']) != 'res://' + resource:
            raise RuntimeError('Native loaded resource identity mismatch: ' + item['id'])
        entries[item['id']] = {'resource': PROJECT + resource,
            'path': path.relative_to(ROOT).as_posix(), 'sha256': digest(path),
            'width': 1280 if composition else 1100 if item['id'] == 'skill-tree' else 640,
            'height': 720 if composition else 820 if item['id'] == 'skill-tree' else 480,
            'native_loaded_resource': observed.get(item['id']),
            'capture_host': PROJECT + ('prototypes/showcase.tscn' if composition else 'catalog/capture.gd'),
            'composition_screen': ('hud' if item['id'] == 'hud' else 'menu') if composition else None,
            'label': 'Native Godot · mock-data showcase · static image; no game/services' if composition else
                     'Native Godot · Theme control sample · static image, not a runtime component' if item['id'] == 'theme' else
                     'Native Godot · ' + item['name'] + ' · mock data / host content · static image'}
    result = {'schema_version': 1, 'scope': 'Focused resource views and two authoring-only compositions; not an interaction campaign or game certification',
              'engine': run_owned([args.godot, '--version'], env, cache / 'version.log').strip(),
              'renderer': next(line for line in text.splitlines() if 'OpenGL API' in line),
              'host': PROJECT + 'catalog/capture.gd', 'generator': 'tools/ui/capture_catalog.py',
              'generator_sha256': digest(ROOT / 'tools/ui/capture_catalog.py'),
              'logs': [str(p.relative_to(ROOT)) for p in sorted(cache.glob('*.log'))],
              'source_sha256': sources, 'entries': entries}
    # A source-bound record is retained in each immutable run directory too.
    (output / 'previews.json').write_text(json.dumps(result, indent=2) + '\n')
    (ROOT / PREVIEWS).write_text(json.dumps(result, indent=2) + '\n')
    print(f'UI catalog: {len(entries)} native static previews; manifest={PREVIEWS}')


if __name__ == '__main__':
    main()
