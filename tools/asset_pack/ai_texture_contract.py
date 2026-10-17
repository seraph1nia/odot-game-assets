"""Hash-bound texture-only successors for immutable earlier art/cost evidence.

Never relabel an old render or Godot measurement as a view of new textures.
"""
import hashlib
import json
from pathlib import Path

from tools.asset_pack.hex_ground import IDS

ASSETS = (*IDS, 'buildings/archery_range')


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def source_predecessor(root, source):
    """Resolve the job's actual source owner, including shared component libraries."""
    relative = Path(source).relative_to('sources')
    if '..' in relative.parts or relative.suffix != '.blend':
        raise ValueError('Expected a repository-relative Blender source owner')
    return predecessor(root, relative.with_suffix('').as_posix(), 'sources')


def predecessor(root, aid, kind):
    """Return the exact validated predecessor for a scoped current source/export.

    Unchanged/unscoped files retain the ordinary current-byte behavior. A scoped
    changed file fails closed on missing/stale receipts or incomplete preservation.
    """
    if kind not in ('sources', 'exports'):
        raise ValueError('Expected sources or exports')
    root = Path(root)
    path = root / kind / (aid + ('.blend' if kind == 'sources' else '.glb'))
    current = sha(path)
    if aid not in ASSETS or not (root / 'docs/ai-textures/baseline.json').exists():
        return current
    baseline = json.loads((root / 'docs/ai-textures/baseline.json').read_text())
    original = next(a for a in baseline['assets'] if a['id'] == aid)
    if current == original[kind]['sha256']:
        return current
    report = json.loads((root / 'docs/ai-textures/validation.json').read_text())
    assert report['baseline_revision'] == baseline['revision']
    assert report['verifier_sha256'] == sha(root / 'tools/asset_pack/verify_ai_textures_blender.py'), 'stale texture verifier receipt'
    record = report['assets'][aid]
    source = record['source_preservation']
    assert source['signature_before'] == source['signature_after_normalized']
    for key in ('geometry_uv_slots_hierarchy_actions_equal', 'all_other_nodes_defaults_render_settings_equal', 'all_original_packed_images_exact'):
        assert source[key], (aid, key)
    exported = record['export_preservation']
    for key in ('non_color_materials_and_embedded_data_maps_equal', 'exact_animation_targets_samples_loop_extras'):
        assert exported[key], (aid, key)
    geometry = exported['all_serialized_triangle_corners_normals_uvs_equal']
    assert geometry['normals_asserted'] and geometry['all_triangle_corners_checked_bidirectionally']
    assert geometry['one_to_one_source_triangle_connectivity_winding_equal'] and geometry['per_material_triangle_multiplicity_equal']
    assert max(geometry['max_position_error_m'], geometry['max_normal_component_error'], geometry['max_uv_error']) < .00002
    assert record['source_before_sha256'] == original['sources']['sha256']
    assert record['source_after_sha256'] == sha(root / 'sources' / (aid + '.blend')), 'stale texture source receipt'
    assert exported['before']['version'] == original['exports']['sha256']
    assert exported['after']['version'] == sha(root / 'exports' / (aid + '.glb')), 'stale texture export receipt'
    assert exported['after']['triangles'] == exported['before']['triangles']
    if (root / 'docs/ai-textures/seams/baseline.json').exists() or 'immediate_predecessor' in record:
        manifest = json.loads((root / 'docs/ai-textures/seams/baseline.json').read_text())
        delivered = next(a for a in manifest['assets'] if a['id'] == aid)
        assert 'immediate_predecessor' in record, 'Missing delivered predecessor proof'
        immediate = record['immediate_predecessor']
        assert immediate['revision'] == manifest['revision']
        assert immediate['source_sha256'] == delivered['sources']['sha256']
        assert immediate['export']['before']['version'] == delivered['exports']['sha256']
        assert immediate['export']['after']['version'] == exported['after']['version']
        assert immediate['source_signature_before'] == immediate['source_signature_after_normalized']
        assert immediate['all_predecessor_images_exact']
        for key in ('non_color_materials_and_embedded_data_maps_equal', 'exact_animation_targets_samples_loop_extras'):
            assert immediate['export'][key], (aid, 'immediate predecessor', key)
        immediate_geometry = immediate['export']['all_serialized_triangle_corners_normals_uvs_equal']
        assert immediate_geometry['normals_asserted'] and immediate_geometry['all_triangle_corners_checked_bidirectionally']
        assert immediate_geometry['one_to_one_source_triangle_connectivity_winding_equal']
        assert immediate_geometry['per_material_triangle_multiplicity_equal']
        assert max(immediate_geometry['max_position_error_m'], immediate_geometry['max_normal_component_error'],
                   immediate_geometry['max_uv_error']) < .00002
    return original[kind]['sha256']
