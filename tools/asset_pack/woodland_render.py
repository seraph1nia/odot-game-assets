"""Render a real GLB using the existing neutral catalog setup; derive review sizes."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))
import bpy
from tools.asset_catalog import render_blender


def main():
    render_blender.main()
    _, output = sys.argv[sys.argv.index('--')+1:]
    image = bpy.data.images.load(output, check_existing=False)
    for size in (192, 96):
        image.scale(size, size)
        image.filepath_raw = str(Path(output).with_name(Path(output).stem+f'-{size}.png'))
        image.file_format = 'PNG'
        image.save()
    print('Actual neutral CPU GLB render + derived 192/96 review images:', output)


if __name__ == '__main__':
    main()
