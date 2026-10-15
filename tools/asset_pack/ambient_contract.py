"""Explicit localized-motion inventory and evidence-chain rules, not a runtime."""
import hashlib
import json
from pathlib import Path

# mode, existing mesh-name prefixes (all matching suffix variants), description.
BUILDINGS = {
    'archery_range': ('banner', ('Cloth heraldic banner', 'Gold banner border', 'Heraldic shaft', 'Heraldic pointed blade', 'Arrow fletching'), 'Small heraldic banner and its attached arrow sway together'),
    'arrow_tower': ('lantern', (), 'One suspended lantern rocks from its top hanger'),
    'bakery': ('lantern', (), 'The existing warm entrance lantern rocks gently'),
    'barracks': ('flag', ('Barracks blue flag',), 'Small blue lookout flag pivots at its pole edge'),
    'bombarding_tower': ('lantern', (), 'One suspended lantern rocks; cannon and carriage stay fixed'),
    'gold_mine': ('lantern', (), 'One front mine lantern rocks; carts and tracks stay fixed'),
    'magic_academy': ('crystal', ('Academy purple crystal',), 'Crown crystal turns gently about its own vertical center'),
    'metal_mine': ('lantern', (), 'One hanging mine lantern rocks; hoist, rope and loaded cart stay fixed'),
    'research_tower': ('armillary', ('Armillary outer orbit', 'Armillary tilted orbit'), 'Armillary rings turn gently around their fixed center; telescope and tower stay fixed'),
    'stone_cutter': ('hook', ('Hoist iron hook',), 'Suspended hoist hook sways below the fixed rope'),
    'tavern': ('sign', ('Carved hanging sign', 'Foamy mug sign emblem', 'Sign foam', 'Sign mug handle'), 'Beer sign and attached mug ornament sway; bracket remains fixed'),
    'town_hall': ('bell', ('Golden civic bell', 'Bell clapper'), 'Civic bell and clapper rock very slightly on their suspension'),
    'trade_market': ('sign', ('Carved hanging sign', 'Scale sign ', 'Scale pan emblem'), 'Scales sign and attached balance ornament sway together'),
    'tree_house': ('banner', ('Blue treehouse banner', 'Banner white tree emblem'), 'Blue banner and white tree emblem breathe together below their top edge'),
    'weaver': ('shuttle', ('Loom shuttle',), 'Loom shuttle travels a few centimeters; threads and cloth remain fixed'),
    'woodcutter_hut': ('sign', ('Woodcutter hanging log sign', 'Raised log sign emblem', 'Log sign endgrain'), 'Carved log sign and its relief sway; saw, supports and vegetation stay fixed'),
}
WATER = {
    'environment/components/forest_hex_stream': 'Existing reflected-current highlights drift; channel, depth and endpoints stay fixed',
    'environment/components/forest_foam': 'Existing foam rings and beads drift softly together',
    'environment/components/forest_waterfall': 'Existing waterfall streaks shimmer sideways; the falling sheet stays fixed',
    'environment/hex_woodland_bridge': 'Existing channel highlights, pool foam and waterfall streaks drift; banks, bridge and water sheets stay fixed',
    'environment/hex_lantern_bridge': 'Existing channel highlights, pool foam and waterfall streaks drift; banks, bridge and water sheets stay fixed',
    **{'environment/hex_river_overlay_' + p: 'One tiny interior shimmer strip drifts; original painted ribbon, banks, alpha, width and exact connector profile stay fixed'
       for p in ('straight', 'turn_60', 'turn_120', 'end')},
}
ASSETS = tuple('buildings/' + b for b in BUILDINGS) + tuple(WATER)
PALETTE_COMMIT = 'ac41b74'


def sha(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def receipts(root):
    path = Path(root) / 'docs/ambient-motion/authored.json'
    return json.loads(path.read_text()) if path.exists() else {}


def source_chain(root, path, palette_sha):
    """Require exact palette -> localized-motion -> current-byte continuity."""
    current = sha(Path(root) / path)
    if current == palette_sha:
        return None
    record = receipts(root)[path]
    assert record['sha256_before'] == palette_sha, path + ': palette checkpoint differs'
    assert record['sha256_after'] == current, path + ': stale ambient source receipt'
    assert record['preservation_verified_after_reload'], path + ': unverified saved motion'
    return record


def expected_resource_delta(aid):
    """Only four explicitly added 8-triangle shimmer strips may grow geometry."""
    shimmer = aid.startswith('environment/hex_river_overlay_') and aid in WATER
    return {'meshes': int(shimmer), 'triangles': 8 * int(shimmer), 'materials': int(shimmer),
            'animations': int(aid in ASSETS), 'active_mesh_nodes': int(shimmer),
            'active_primitive_instances': int(shimmer), 'active_triangle_instances': 8 * int(shimmer)}
