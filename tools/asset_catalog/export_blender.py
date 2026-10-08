"""Export selected existing sources without rebuilding, saving, or rendering.

blender -b --python-exit-code 1 --python tools/asset_catalog/export_blender.py -- props/sword
The asset collection or root object must match its ID stem; equipment is included.
"""
import argparse
from contextlib import contextmanager
import sys
import tempfile
from pathlib import Path

import bpy

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
from tools.asset_catalog.index import CatalogIndex, write_json
from tools.asset_catalog.metadata import read_glb
from tools.asset_catalog.export_sources import plan_exports
from tools.asset_catalog.blender_selection import load_asset


@contextmanager
def _export_material_bindings(objects):
    """Keep effective OBJECT slots when glTF applies modifiers to temporary meshes.

    Blender's evaluated to_mesh() retains DATA materials, not OBJECT overrides.
    Without modifiers glTF already uses object slots; leave those meshes alone.
    Normalize only divergent modified meshes, sharing each original/slot-tuple
    variant, and restore all bindings even if preparation or serialization fails.
    Collection-instance prototypes participate without making instances real.
    """
    pending = list(objects)
    seen, variants, restore = set(), {}, []
    try:
        while pending:
            obj = pending.pop()
            if obj in seen:
                continue
            seen.add(obj)
            if obj.instance_collection is not None:
                pending.extend(obj.instance_collection.all_objects)
            if obj.type != 'MESH' or not obj.modifiers:
                continue
            slots = tuple((slot.link, slot.material) for slot in obj.material_slots)
            effective = tuple(mat for _, mat in slots)
            if effective == tuple(obj.data.materials):
                continue
            original = obj.data
            key = (original, effective)
            if key not in variants:
                mesh = original.copy()
                variants[key] = mesh
                for i, mat in enumerate(effective):
                    mesh.materials[i] = mat
            restore.append((obj, original, slots))
            obj.data = variants[key]
            for slot in obj.material_slots:
                slot.link = 'DATA'
        bpy.context.view_layer.update()
        yield
    finally:
        for obj, original, slots in reversed(restore):
            obj.data = original
            for slot, (link, mat) in zip(obj.material_slots, slots, strict=True):
                slot.link = link
                if link == 'OBJECT':
                    slot.material = mat
        for mesh in variants.values():
            bpy.data.meshes.remove(mesh)
        bpy.context.view_layer.update()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('assets', nargs='*')
    parser.add_argument('--all', action='store_true')
    parser.add_argument('--root', type=Path, default=ROOT)
    args = parser.parse_args(sys.argv[sys.argv.index('--') + 1:] if '--' in sys.argv else [])
    if not args.assets and not args.all:
        parser.error('Supply asset IDs or --all')
    repo_root = args.root.resolve()
    jobs = plan_exports(repo_root, None if args.all else args.assets)
    index = CatalogIndex(repo_root)
    manifest = index.read_json('exports/asset_manifest.json', [])
    reports = {entry['file']: entry for entry in manifest.get('assets', [])}
    for job in jobs:
        asset_id = job['id']
        objects = load_asset(job, repo_root)
        bpy.ops.object.select_all(action='DESELECT')
        for obj in objects:
            obj.hide_set(False)
            obj.select_set(True)
        objects.sort(key=lambda obj: obj.name)
        bpy.context.view_layer.objects.active = next((obj for obj in objects if obj.type == 'ARMATURE'), objects[0])
        target = repo_root / 'exports' / (asset_id + '.glb')
        target.parent.mkdir(parents=True, exist_ok=True)
        staging = repo_root / '.cache'
        staging.mkdir(exist_ok=True)
        workspace = tempfile.TemporaryDirectory(dir=staging)
        temporary = Path(workspace.name) / target.name
        animated = any(obj.type == 'ARMATURE' or obj.animation_data for obj in objects)
        try:
            with _export_material_bindings(objects):
                result = bpy.ops.export_scene.gltf(
                    filepath=str(temporary), use_selection=True, export_animations=animated,
                    export_apply=True, export_extras=True, export_cameras=False,
                    export_lights=False, export_yup=True, export_skins=animated,
                    export_animation_mode='ACTIONS')
            if 'FINISHED' not in result:
                raise RuntimeError(f'Export failed: {asset_id}')
            facts = read_glb(temporary)
            temporary.replace(target)
        finally:
            workspace.cleanup()
        key = target.relative_to(repo_root).as_posix()
        reports[key] = reports.get(key, {}) | {'file': key, 'bytes': facts['bytes'],
                       'triangles': facts['triangles'], 'materials': facts['materials'],
                       'animations': [clip['name'] for clip in facts['animations']],
                       'source': job['source']}
        instances = [obj for obj in objects if obj.get('kit_asset')]
        if instances:
            usage = {}
            for obj in instances:
                kind = obj['kit_asset']
                usage[kind] = usage.get(kind, 0) + 1
            reports[key]['shared_kit_instances'] = usage
            reports[key]['shared_kits'] = sorted({obj['kit_source'] for obj in instances
                                                  if obj.get('kit_source')})
        manifest['assets'] = list(reports.values())
        write_json(repo_root / 'exports/asset_manifest.json', manifest)
        index.refresh()
        print(f'Exported {asset_id}; source unchanged')


if __name__ == '__main__':
    main()
