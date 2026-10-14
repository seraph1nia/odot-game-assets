"""Read-only fixture against actual corrected standalone/equipped grip wraps."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import bpy
import woodland_refinement as w


def main():
    for source in ('sources/props/bow.blend', 'sources/props/crossbow.blend',
                   'sources/characters/archer.blend', 'sources/characters/evil_ranged_unit.blend'):
        path = w.g.ROOT/source
        original = w.digest(path)
        bpy.ops.wm.open_mainfile(filepath=str(path))
        roots = [o for o in bpy.data.objects if o.type == 'EMPTY' and o.name.split('.')[0] in ('bow', 'crossbow')]
        assert len(roots) == 1, source
        root = roots[0]
        frame = w.binding_frame(root, root.name.split('.')[0])
        wraps = [o for o in root.children_recursive if o.get('woodland_part') == w.PREFIX+'equipment worn binding']
        assert len(wraps) == 3 and root.get('woodland_binding_fit') == 1
        offsets = []
        for obj in wraps:
            local = root.matrix_world.inverted() @ obj.matrix_world
            center = sum((local @ v.co for v in obj.data.vertices), w.Vector())/len(obj.data.vertices)
            fitted = frame.inverted() @ center
            assert abs(fitted.x) < 1e-5 and abs(fitted.y) < 1e-5, (source, tuple(fitted))
            offsets.append(fitted.z)
        assert all(abs(a-b) < 1e-5 for a,b in zip(sorted(offsets), [-.065,.005,.075], strict=True))
        assert w.digest(path) == original, source+' source changed'
    print('Actual bow/crossbow grip-fit fixtures passed; standalone/equipped sources unchanged')


if __name__ == '__main__':
    main()
