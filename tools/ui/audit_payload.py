"""Copy only UI/ into a private independent project and check native resource loading."""
import argparse
import hashlib
import json
import os
import re
import shutil

from capture_explorations import ROOT, run_owned

PROBE = '''extends SceneTree
func _initialize() -> void: call_deferred("check")
func check() -> void:
	var body = Control.new()
	root.add_child(body)
	body.theme = load("res://UI/theme/ledger.tres")
	var components = ["resource_ledger", "upkeep_summary", "quoted_action", "city_navigation", "match_controls", "session_feedback", "unit_inspection", "army_roster", "modal", "skill_tree"]
	for name in components:
		var component = load("res://UI/components/" + name + ".tscn").instantiate()
		body.add_child(component)
		assert(component.is_node_ready(), "Independent scene ready: " + name)
	var skills = body.get_node("SkillTree")
	assert(skills.set_data({"root":{"id":"root", "cost":1}, "points":2, "branches":[{"nodes":[{"id":"a", "parent":"root", "cost":1}]}, {"nodes":[{"id":"b", "parent":"root", "cost":1}]}, {"nodes":[{"id":"c", "parent":"root", "cost":1}]}]}))
	assert(not skills.purchase("a"))
	assert(skills.purchase("root") and skills.points == 1)
	assert(skills.purchase("a") and not skills.purchase("a") and skills.points == 0)
	assert(load("res://UI/art/menu_seal.png") != null)
	print("UI_PAYLOAD 10 scenes, skill purchase guards, Theme and seal load without prototypes, game or tooling")
	quit()
'''


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', required=True)
    parser.add_argument('--dotnet-root')
    parser.add_argument('--label', default='m1')
    args = parser.parse_args()
    if not re.fullmatch(r'[A-Za-z0-9_-]+', args.label):
        parser.error('label must be a simple run name')
    cache = ROOT / '.cache/ui-payload' / args.label
    cache.mkdir(parents=True, exist_ok=False)  # Do not overwrite failed evidence.
    source = ROOT / 'ui/preview/UI'
    manifest = {}
    for path in sorted(source.rglob('*')):
        if not path.is_file():
            continue
        if path.is_symlink():
            raise ValueError(f'External/symlink resource: {path}')
        manifest[path.relative_to(source).as_posix()] = hashlib.sha256(path.read_bytes()).hexdigest()
    shutil.copytree(source, cache / 'UI')
    (cache / 'project.godot').write_text('[application]\nconfig/name="UI payload audit"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
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
    if 'ERROR:' in text or 'UI_PAYLOAD 10 scenes' not in text:
        raise RuntimeError('Payload load failed; see private full log')
    result = {'scope': 'Only UI/ copied; no prototypes/game/tooling runtime dependencies',
              'files': manifest, 'log': (cache / 'load.log').relative_to(ROOT).as_posix(),
              'seal_file_bytes': (source / 'art/menu_seal.png').stat().st_size,
              'seal_rgba_bytes': 192 * 192 * 4, 'nine_slice': 'not applicable: native StyleBoxFlat, fixed seal'}
    (ROOT / 'docs/ui/payload.json').write_text(json.dumps(result, indent=2) + '\n')
    print(f"UI payload passed: 10 scenes, Theme, fixed seal; {len(manifest)} files; log={result['log']}")


if __name__ == '__main__':
    main()
