"""Evidence chain from immutable landed art receipts to optimized runtime bytes."""
import json
from pathlib import Path


def export_chain(root, aid, landed_sha):
    """Require exact landed identity and current hash-bound independent validation.

    Old renders remain records of landed detailed exports, never relabeled as new
    runtime renders. A changed successor is accepted only through its own checks.
    """
    root = Path(root)
    from tools.asset_pack.ai_texture_contract import predecessor, source_predecessor
    current = predecessor(root, aid, 'exports')
    if current == landed_sha:
        return None
    baseline = json.loads((root/'docs/runtime-optimization/baseline.json').read_text())
    result = json.loads((root/'docs/runtime-optimization/validation.json').read_text())['assets'][aid]
    original = baseline['assets'][aid]
    assert original['facts']['version'] == landed_sha, aid + ': landed export differs'
    assert result['glb_sha256'] == current, aid + ': stale runtime validation'
    source = original['job']['source']
    assert source_predecessor(root, source) == baseline['sources'][source] == result['source_sha256'], aid + ': source changed'
    surfaces = result['serialized_surfaces']
    assert surfaces['one_to_one_transformed_triangle_attributes_equal'] and surfaces['zero_area_triangles_not_filtered'], aid
    for name in ('source_to_raw_buffers', 'source_to_exported_buffers', 'reimport'):
        fidelity = result[name]
        assert fidelity['one_to_one_source_triangle_connectivity_winding_equal'], aid
        assert fidelity['all_triangle_corners_checked_bidirectionally'] and fidelity['per_material_triangle_multiplicity_equal'], aid
        assert fidelity['normals_asserted'] == (name != 'reimport'), aid
    assert result['exact_material_contracts_and_texture_bindings'] and result['exact_animation_targets_samples_and_loop_extras'], aid
    assert result['playback']['glb_sha256'] == current, aid + ': stale runtime loop'
    return result
