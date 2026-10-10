"""Fresh standalone Godot import plus owned software native-input/visual checks."""
import argparse
import hashlib
import json
import os

from capture_explorations import ROOT, run_owned


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', required=True)
    parser.add_argument('--dotnet-root')
    parser.add_argument('--label', default='production')
    parser.add_argument('--only', choices=['all', 'production'], default='all')
    args = parser.parse_args()
    cache = ROOT / '.cache/ui' / args.label
    cache.mkdir(parents=True, exist_ok=True)
    output = ROOT / 'docs/ui/production' / args.label
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(LIBGL_ALWAYS_SOFTWARE='1', GALLIUM_DRIVER='llvmpipe')
    for kind in ('DATA', 'CONFIG', 'CACHE'):
        path = cache / kind.lower()
        path.mkdir(exist_ok=True)
        env['XDG_' + kind + '_HOME'] = str(path)
    if args.dotnet_root:
        env['DOTNET_ROOT'] = args.dotnet_root
        env['PATH'] = args.dotnet_root + os.pathsep + env['PATH']
    engine = [args.godot, '--path', str(ROOT / 'ui/preview'), '--audio-driver', 'Dummy']
    run_owned([*engine, '--headless', '--editor', '--import'], env, cache / 'import.log')
    command = ['xvfb-run', '-a', '--auth-file', str(cache / 'display.auth'),
               '-e', str(cache / 'xvfb.log'), '-s', '-screen 0 1920x1080x24 -nolisten tcp',
               *engine, 'res://tests/runner.tscn', '--resolution', '1100x820',
               '--rendering-method', 'gl_compatibility', '--rendering-driver', 'opengl3',
               '--max-fps', '30', '--', '--output=' + str(output), '--only=' + args.only]
    source = ROOT / 'ui/preview'
    manifest = {path.relative_to(source).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest()
                for path in sorted(source.rglob('*')) if path.is_file()
                and '.godot' not in path.parts and path.suffix not in ('.uid', '.import')}
    text = run_owned(command, env, cache / 'tests.log', timeout=180)
    if any(hashlib.sha256((source / name).read_bytes()).hexdigest() != digest for name, digest in manifest.items()):
        raise RuntimeError('Source changed during validation; fresh process required')
    result_path = output / 'results.json'
    result = json.loads(result_path.read_text())
    result['renderer'] = next(line for line in text.splitlines() if 'OpenGL API' in line)
    result['log'] = (cache / 'tests.log').relative_to(ROOT).as_posix()
    result['source_sha256'] = manifest
    result_path.write_text(json.dumps(result, indent=2) + '\n')
    if result['failures']:
        raise RuntimeError('UI assertions failed')
    print(f"UI passed: {result['checks']} checks, {len(result['captures'])} actual captures; log={result['log']}")


if __name__ == '__main__':
    main()
