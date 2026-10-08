"""Render authored presentation scenes in a worker without saving sources."""
import sys
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
sys.path.insert(0,str(Path(__file__).resolve().parent))
import bpy
import geometry as g
import art_style as style
from tools.asset_catalog.export_sources import plan_exports


def selected_sources(names):
    """Resolve all inputs before rendering, using the catalog's source ownership."""
    if not names:
        return []
    jobs = plan_exports(g.ROOT)
    by_id = {job['id']: job for job in jobs}
    selected = []
    outputs = {}
    for name in names:
        matches = ([by_id[name]] if name in by_id else
                   [job for job in jobs if Path(job['id']).name == name])
        if not matches:
            raise ValueError(f'Unknown authored asset: {name}')
        if len(matches) != 1:
            ids = ', '.join(job['id'] for job in matches)
            raise ValueError(f'{name}: ambiguous asset name; use a canonical ID: {ids}')
        job = matches[0]
        stem = Path(job['id']).name
        if stem in outputs and outputs[stem] != job['id']:
            raise ValueError(f'{name}: preview filename collides with {outputs[stem]}')
        outputs[stem] = job['id']
        selected.append(job)
    return selected


def main(names):
    for job in selected_sources(names):
        name=Path(job['id']).name
        bpy.ops.wm.open_mainfile(filepath=str(g.ROOT/job['source']))
        scene=bpy.context.scene
        # Bound CPU use when several isolated review renders run concurrently.
        scene.render.threads_mode='FIXED';scene.render.threads=style.PREVIEW.threads
        if not scene.camera:raise ValueError(name+': no presentation camera')
        scene.render.filepath=str(g.ROOT/'exports/previews'/f'{name}.png')
        bpy.ops.render.render(write_still=True)
        print('Rendered preview:',name,flush=True)


if __name__=='__main__':
    main(sys.argv[sys.argv.index('--')+1:])
