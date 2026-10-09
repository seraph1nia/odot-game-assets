"""Bounded fresh-process Settings probes; XTest only on this command's owned Xvfb."""
import argparse
import ctypes
import json
import os
import subprocess
import sys
import time

from capture_explorations import ROOT, run_owned


def xtest_driver():
    if os.environ.get('UI_DIAGNOSTIC_OWNED_DISPLAY') != '1':
        raise RuntimeError('OS input is restricted to the owned diagnostic display')
    x11 = ctypes.CDLL('libX11.so.6')
    xtst = ctypes.CDLL('libXtst.so.6')
    x11.XOpenDisplay.argtypes = [ctypes.c_char_p]
    x11.XOpenDisplay.restype = ctypes.c_void_p
    display = x11.XOpenDisplay(None)
    if not display:
        raise RuntimeError('Owned display unavailable')
    x11.XStringToKeysym.argtypes = [ctypes.c_char_p]
    x11.XStringToKeysym.restype = ctypes.c_ulong
    x11.XKeysymToKeycode.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    x11.XKeysymToKeycode.restype = ctypes.c_uint
    x11.XSetInputFocus.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_ulong]
    x11.XDefaultRootWindow.argtypes = [ctypes.c_void_p]
    x11.XDefaultRootWindow.restype = ctypes.c_ulong
    x11.XCreateSimpleWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong, ctypes.c_int, ctypes.c_int,
                                       ctypes.c_uint, ctypes.c_uint, ctypes.c_uint, ctypes.c_ulong, ctypes.c_ulong]
    x11.XCreateSimpleWindow.restype = ctypes.c_ulong
    x11.XMapWindow.argtypes = [ctypes.c_void_p, ctypes.c_ulong]
    x11.XSync.argtypes = [ctypes.c_void_p, ctypes.c_int]
    x11.XCloseDisplay.argtypes = [ctypes.c_void_p]
    xtst.XTestFakeKeyEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
    xtst.XTestFakeButtonEvent.argtypes = [ctypes.c_void_p, ctypes.c_uint, ctypes.c_int, ctypes.c_ulong]
    xtst.XTestFakeMotionEvent.argtypes = [ctypes.c_void_p, ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_ulong]
    return x11, xtst, display


def inside(args, cache):
    ack = cache / 'ack.txt'
    command = [args.godot, '--path', str(ROOT / 'ui/preview'), 'res://tests/diagnose_settings.tscn',
               '--audio-driver', 'Dummy', '--resolution', '1100x820', '--max-fps', '30', '--',
               '--case=' + args.case, '--input=' + args.input, '--ack=' + str(ack), '--counterfactual=' + args.counterfactual]
    libraries = xtest_driver() if args.input == 'os' else None
    other_window = None
    window = None
    process = subprocess.Popen(command, cwd=ROOT, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
    try:
        for line in process.stdout:
            print(line, end='', flush=True)
            if libraries and line.startswith('NATIVE_WINDOW '):
                x11, xtst, display = libraries
                window = int(line.split()[1])
                x11.XSetInputFocus(display, window, 1, 0)
                x11.XSync(display, False)
            elif libraries and line.startswith('NATIVE_EVENT '):
                x11, xtst, display = libraries
                event = json.loads(line.removeprefix('NATIVE_EVENT '))
                if 'focus' in event:
                    if event['focus'] == 'away' and other_window is None:
                        other_window = x11.XCreateSimpleWindow(display, x11.XDefaultRootWindow(display),
                                                              1800, 0, 50, 50, 0, 0, 0)
                        x11.XMapWindow(display, other_window)
                    x11.XSetInputFocus(display, other_window if event['focus'] == 'away' else window, 1, 0)
                elif 'key' in event:
                    symbol = x11.XStringToKeysym(event['key'].encode())
                    code = x11.XKeysymToKeycode(display, symbol)
                    shift = x11.XKeysymToKeycode(display, x11.XStringToKeysym(b'Shift_L'))
                    if event.get('shift'):
                        xtst.XTestFakeKeyEvent(display, shift, True, 0)
                    xtst.XTestFakeKeyEvent(display, code, True, 0)
                    x11.XSync(display, False)
                    time.sleep(.05)
                    xtst.XTestFakeKeyEvent(display, code, False, 0)
                    if event.get('shift'):
                        xtst.XTestFakeKeyEvent(display, shift, False, 0)
                else:
                    xtst.XTestFakeMotionEvent(display, 0, *event['click'], 0)
                    xtst.XTestFakeButtonEvent(display, 1, True, 0)
                    x11.XSync(display, False)
                    time.sleep(.05)
                    xtst.XTestFakeButtonEvent(display, 1, False, 0)
                x11.XSync(display, False)
                ack.write_text(str(event['sequence']))
        if process.wait():
            raise RuntimeError('Diagnostic engine failed')
    finally:
        if process.poll() is None:
            process.terminate()
            process.wait(timeout=5)
        if libraries:
            libraries[0].XCloseDisplay(libraries[2])


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', required=True)
    parser.add_argument('--dotnet-root')
    parser.add_argument('--case', choices=['baseline', 'dropdown', 'fullscreen', 'slider-focus', 'slider', 'outside', 'full', 'modal'], required=True)
    parser.add_argument('--input', choices=['synthetic', 'os'], default='synthetic')
    parser.add_argument('--counterfactual', choices=['none', 'focus'], default='none')
    parser.add_argument('--label', default='')
    parser.add_argument('--inside-display', action='store_true')
    args = parser.parse_args()
    cache = ROOT / '.cache/ui-diagnosis' / (args.case + '-' + args.input + '-' + args.counterfactual + ('-' + args.label if args.label else ''))
    cache.mkdir(parents=True, exist_ok=True)
    if args.inside_display:
        inside(args, cache)
        return
    env = os.environ.copy()
    env.update(UI_DIAGNOSTIC_OWNED_DISPLAY='1', LIBGL_ALWAYS_SOFTWARE='1', GALLIUM_DRIVER='llvmpipe')
    for kind in ('DATA', 'CONFIG', 'CACHE'):
        path = cache / kind.lower()
        path.mkdir(exist_ok=True)
        env['XDG_' + kind + '_HOME'] = str(path)
    if args.dotnet_root:
        env['DOTNET_ROOT'] = args.dotnet_root
        env['PATH'] = args.dotnet_root + os.pathsep + env['PATH']
    run_owned([args.godot, '--path', str(ROOT / 'ui/preview'), '--headless', '--editor', '--import'],
              env, cache / 'import.log', timeout=60)
    command = ['xvfb-run', '-a', '--auth-file', str(cache / 'display.auth'),
               '-e', str(cache / 'xvfb.log'), '-s', '-screen 0 1920x1080x24 -nolisten tcp',
               sys.executable, str(ROOT / 'tools/ui/diagnose_settings.py'), '--inside-display',
               '--godot', args.godot, '--case', args.case, '--input', args.input,
               '--counterfactual', args.counterfactual, '--label', args.label]
    text = run_owned(command, env, cache / 'probe.log', timeout=60)
    result = next(line for line in text.splitlines() if line.startswith('DIAG_RESULT '))
    print(result)


if __name__ == '__main__':
    main()
