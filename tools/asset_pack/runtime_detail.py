"""Temporary export-only subpixel bevel/moss profile; restore on every exit.

Only the named repeated woodland moss prototype is simplified. It already has
portable painted color/roughness maps; keep those maps/UVs and every placement.
A single evaluated variant is shared by all qualifying instances, not one mesh
or Decimate modifier per instance. No hero geometry, leaves or rig is touched.
"""
from contextlib import contextmanager

from tools.asset_pack.art_style import RUNTIME
from tools.asset_pack.ambient_contract import ASSETS


@contextmanager
def export_detail(objects, asset_id):
    changed, seen, pending = [], set(), list(objects)
    restore, variants, probes = [], {}, []
    report = {'tiny_bevels': 0, 'moss_instances': 0, 'moss_mesh_variants': 0}
    try:
        if asset_id in ASSETS:
            import bpy
            while pending:
                obj = pending.pop()
                if obj in seen:
                    continue
                seen.add(obj)
                if obj.instance_collection:
                    pending.extend(obj.instance_collection.all_objects)
                for mod in obj.modifiers:
                    if (mod.type == 'BEVEL' and mod.segments == 2 and mod.show_viewport
                            and mod.width <= RUNTIME.tiny_bevel_width + 1e-8
                            and mod.offset_type == 'OFFSET'):
                        scale = max(abs(v) for v in obj.matrix_world.to_scale())
                        if mod.width * scale <= RUNTIME.tiny_bevel_width + 1e-8:
                            changed.append((mod, mod.segments))
                            mod.segments = 1
                if (obj.type != 'MESH' or not obj.name.startswith('Woodland shared moss cushion')
                        or obj.modifiers or max(obj.dimensions) > RUNTIME.moss_max_world_diameter):
                    continue
                original = obj.data
                # Include effective materials in the variant key; never swallow
                # object-level overrides as a side effect of mesh evaluation.
                slots = tuple((s.link, s.material) for s in obj.material_slots)
                key = (original, tuple(mat for _, mat in slots))
                if key not in variants:
                    probe = obj.copy(); probe.data = original
                    bpy.context.scene.collection.objects.link(probe); probes.append(probe)
                    mod = probe.modifiers.new('Runtime small moss topology', 'DECIMATE')
                    mod.ratio = RUNTIME.moss_triangle_ratio
                    mod.use_collapse_triangulate = True
                    bpy.context.view_layer.update()
                    dg = bpy.context.evaluated_depsgraph_get()
                    mesh = bpy.data.meshes.new_from_object(probe.evaluated_get(dg),
                        preserve_all_data_layers=True, depsgraph=dg)
                    variants[key] = mesh
                    for i, (_, mat) in enumerate(slots): mesh.materials[i] = mat
                    bpy.data.objects.remove(probe,do_unlink=True); probes.remove(probe)
                restore.append((obj, original, slots)); obj.data = variants[key]
                for slot in obj.material_slots: slot.link = 'DATA'
            bpy.context.view_layer.update()
        report.update(tiny_bevels=len(changed), moss_instances=len(restore), moss_mesh_variants=len(variants))
        yield report
    finally:
        for mod, segments in reversed(changed): mod.segments = segments
        for obj, original, slots in reversed(restore):
            obj.data = original
            for slot,(link,mat) in zip(obj.material_slots,slots,strict=True):
                slot.link = link
                if link == 'OBJECT': slot.material = mat
        if variants or probes:
            import bpy
            for obj in probes: bpy.data.objects.remove(obj,do_unlink=True)
            for mesh in variants.values(): bpy.data.meshes.remove(mesh)
            bpy.context.view_layer.update()
