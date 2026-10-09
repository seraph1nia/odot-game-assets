"""Capture only the standalone approval scene on an owned software display."""
import argparse
import json
import os
import signal
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', required=True, help='Existing local Godot 4 executable; never installed here')
    parser.add_argument('--dotnet-root', help='Existing SDK root, needed by a .NET Godot build even for GDScript')
    args = parser.parse_args()
    cache = ROOT / '.cache/ui-explorations'
    output = ROOT / 'docs/ui/previews'
    cache.mkdir(parents=True, exist_ok=True)
    output.mkdir(parents=True, exist_ok=True)
    env = os.environ.copy()
    env.update(LIBGL_ALWAYS_SOFTWARE='1', GALLIUM_DRIVER='llvmpipe',
               GODOT_SILENCE_ROOT_WARNING='1')
    for kind in ('DATA', 'CONFIG', 'CACHE'):
        path = cache / kind.lower()
        path.mkdir(exist_ok=True)
        env['XDG_' + kind + '_HOME'] = str(path)
    if args.dotnet_root:
        env['DOTNET_ROOT'] = args.dotnet_root
        env['PATH'] = args.dotnet_root + os.pathsep + env['PATH']
    engine = [args.godot, '--path', str(ROOT / 'ui/preview'), '--audio-driver', 'Dummy']
    records = []
    for width, height in ((1100, 820), (1280, 720)):
        for direction in ('ledger', 'watch'):
            for composition in ('hud', 'menu'):
                name = f'{direction}-{composition}-{width}x{height}'
                log = cache / (name + '.log')
                command = ['xvfb-run', '-a', '--auth-file', str(cache / (name + '.auth')),
                           '-e', str(cache / (name + '-xvfb.log')),
                           '-s', '-screen 0 1920x1080x24 -nolisten tcp', *engine,
                           '--rendering-method', 'gl_compatibility', '--rendering-driver', 'opengl3',
                           '--resolution', f'{width}x{height}', '--',
                           '--direction=' + direction, '--composition=' + composition,
                           '--capture=' + str(output / (name + '.png'))]
                with log.open('w') as stream:
                    process = subprocess.Popen(command, env=env, cwd=ROOT, stdout=stream,
                                               stderr=subprocess.STDOUT, start_new_session=True)
                    try:
                        code = process.wait(timeout=60)
                        if code:
                            raise RuntimeError(f'Capture exit {code}; see {log.relative_to(ROOT)}')
                    finally:
                        # xvfb-run owns its display, but a timeout must also reap engine children.
                        try:
                            os.killpg(process.pid, signal.SIGTERM)
                        except ProcessLookupError:
                            pass
                        try:
                            process.wait(timeout=5)
                        except subprocess.TimeoutExpired:
                            os.killpg(process.pid, signal.SIGKILL)
                            process.wait()
                text = log.read_text()
                if 'SCRIPT ERROR' in text or 'ERROR:' in text or 'CAPTURE ' not in text:
                    raise RuntimeError(f'Invalid capture; see {log.relative_to(ROOT)}')
                renderer = next((line for line in text.splitlines() if 'OpenGL' in line), 'not logged')
                records.append(dict(path=(output / (name + '.png')).relative_to(ROOT).as_posix(),
                                    width=width, height=height, renderer=renderer,
                                    log=log.relative_to(ROOT).as_posix()))
                print(name + ': captured', flush=True)
    (output / 'captures.json').write_text(json.dumps(dict(scope='Approval explorations; not production acceptance',
                                                        captures=records), indent=2) + '\n')


if __name__ == '__main__':
    main()
