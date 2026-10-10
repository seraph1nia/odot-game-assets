"""Load the actual generated ZIP in an independent, owned Godot project."""
import argparse
import hashlib
import json
import os
import zipfile
from pathlib import Path

from audit_payload import PROBE
from capture_explorations import ROOT, run_owned


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--package', default='dist/catalog/exports/ui/ledger-ui.zip')
    parser.add_argument('--godot', required=True)
    parser.add_argument('--dotnet-root')
    parser.add_argument('--label', required=True)
    args = parser.parse_args()
    if not args.label.replace('-', '').replace('_', '').isalnum():
        parser.error('label must be a simple run name')
    cache = ROOT / '.cache/ui-catalog-package' / args.label
    cache.mkdir(parents=True, exist_ok=False)
    package = (ROOT / args.package).resolve()
    with zipfile.ZipFile(package) as archive:
        for name in archive.namelist():
            path = Path(name)
            if path.is_absolute() or '..' in path.parts:
                raise ValueError('Unsafe package member')
        archive.extractall(cache)
    manifest = json.loads((cache / 'manifest.json').read_text())
    for name, expected in manifest['files'].items():
        if hashlib.sha256((cache / name).read_bytes()).hexdigest() != expected:
            raise ValueError('Package dependency hash mismatch: ' + name)
    (cache / 'project.godot').write_text('[application]\nconfig/name="Generated catalog payload check"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
    (cache / 'probe.gd').write_text(PROBE)
    env = os.environ.copy()
    for kind in ('DATA', 'CONFIG', 'CACHE'):
        path = cache / kind.lower()
        path.mkdir()
        env['XDG_' + kind + '_HOME'] = str(path)
    if args.dotnet_root:
        env['DOTNET_ROOT'] = args.dotnet_root
        env['PATH'] = args.dotnet_root + os.pathsep + env['PATH']
    engine = [args.godot, '--headless', '--path', str(cache), '--audio-driver', 'Dummy']
    run_owned([*engine, '--editor', '--import'], env, cache / 'import.log')
    text = run_owned([*engine, '--script', 'res://probe.gd'], env, cache / 'load.log')
    if 'UI_PAYLOAD 9 scenes' not in text:
        raise RuntimeError('Native payload probe did not finish')
    result = {'package_sha256': hashlib.sha256(package.read_bytes()).hexdigest(),
              'files': manifest['files'], 'checks': 'All nine scenes instantiated/ready, Theme and seal loaded in independent project; no prototypes/game/tools/cache history copied',
              'engine': run_owned([args.godot, '--version'], env, cache / 'version.log').strip(),
              'logs': [p.relative_to(ROOT).as_posix() for p in sorted(cache.glob('*.log'))]}
    (cache / 'result.json').write_text(json.dumps(result, indent=2) + '\n')
    (ROOT / 'docs/ui/catalog/package-check.json').write_text(json.dumps(result, indent=2) + '\n')
    print('Native generated UI package passed: ' + result['package_sha256'])


if __name__ == '__main__':
    main()
