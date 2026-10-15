"""Repeatable isolated headless Godot before/after import/instantiation benchmark."""
import argparse
import json
import os
import platform
import shutil
import subprocess
import time
from pathlib import Path

from tools.asset_pack.ambient_contract import ASSETS, sha

ROOT = Path(__file__).resolve().parents[2]


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--godot', required=True, help='Verified installed executable; never installs')
    parser.add_argument('--project', type=Path, default=ROOT/'.cache/runtime-optimization/godot')
    args = parser.parse_args()
    project = args.project.resolve()
    if not project.is_relative_to(ROOT/'.cache/runtime-optimization'):
        parser.error('Use a task-local project under .cache/runtime-optimization')
    cache_was_present=(project/'.godot/imported').exists()
    project.mkdir(parents=True, exist_ok=True)
    (project/'project.godot').write_text('[application]\nconfig/name="Odot isolated asset benchmark"\n[rendering]\nrenderer/rendering_method="gl_compatibility"\n')
    shutil.copy2(ROOT/'tools/asset_pack/runtime_benchmark.gd',project/'benchmark.gd')
    selected, bindings = [], {}
    # Interleave pairs to avoid putting all before or after scenes in one phase.
    for aid in ASSETS:
        for stage in ('before','after'):
            source = (ROOT/'.cache/runtime-optimization/before/exports' if stage == 'before' else ROOT/'exports')/(aid+'.glb')
            target = project/stage/(aid+'.glb')
            target.parent.mkdir(parents=True,exist_ok=True); shutil.copy2(source,target)
            resource = 'res://'+target.relative_to(project).as_posix()
            selected.append(resource)
            bindings[resource] = sha(source)
    (project/'selection.json').write_text(json.dumps(selected))
    logs = ROOT/'.cache/asset-check/logs'
    environment=os.environ | {'XDG_DATA_HOME':str(project/'.user-data'),
        'XDG_CONFIG_HOME':str(project/'.user-config'),'XDG_CACHE_HOME':str(project/'.user-cache'),
        'DOTNET_CLI_HOME':str(project/'.dotnet-cli'),'DOTNET_CLI_TELEMETRY_OPTOUT':'1'}
    started = time.monotonic()
    with (logs/'runtime-godot-import.log').open('w') as log:
        subprocess.run([args.godot,'--headless','--path',str(project),'--editor','--import'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600,env=environment)
    import_seconds = time.monotonic()-started
    (project/'results.json').unlink(missing_ok=True)
    with (logs/'runtime-godot-benchmark.log').open('w') as log:
        subprocess.run([args.godot,'--headless','--path',str(project),'--script','res://benchmark.gd'],stdout=log,stderr=subprocess.STDOUT,check=True,timeout=600,env=environment)
    errors=[p for p in (logs/'runtime-godot-import.log',logs/'runtime-godot-benchmark.log')
            if 'ERROR:' in p.read_text(errors='replace')]
    if errors:
        raise RuntimeError('Godot emitted errors: '+', '.join(str(p) for p in errors))
    report = json.loads((project/'results.json').read_text())
    if (len(report['samples'])!=len(selected)
            or any(not isinstance(s,dict) or not s.get('loop_endpoints_equal')
                   or not s.get('all_track_targets_resolve') or s.get('moving_meshes',0)<=0
                   for s in report['samples'])):
        raise RuntimeError('Incomplete/failed native scene or loop measurement')
    report['editor_import_wall_seconds'] = import_seconds
    report['source_glb_sha256'] = bindings
    report['benchmark_script_sha256'] = sha(ROOT/'tools/asset_pack/runtime_benchmark.gd')
    report['host']={'platform':platform.platform(),'logical_cpus':os.cpu_count()}
    report['driver_sha256']=sha(Path(__file__))
    report['godot_import_cache_at_start']='existing' if cache_was_present else 'empty'
    report['import_setup'] = ('Existing' if cache_was_present else 'Fresh')+' task-local Godot import cache; copied landed and optimized GLBs. OS page cache not flushed, no game repository. Repeat using a new --project subdirectory for empty Godot resource/import caches; this is not cold OS-cache timing.'
    (ROOT/'docs/runtime-optimization/godot.json').write_text(json.dumps(report,indent=2)+'\n')
    print('Headless Godot benchmark:',len(report['samples']),'actual imported scenes; import seconds',round(import_seconds,2))


if __name__ == '__main__': main()
