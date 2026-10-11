"""Canonical topology and editable-source contracts; native proof is separate."""
import hashlib
import json
import unittest
from collections import Counter
from pathlib import Path
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[2]
SOURCE = ROOT / 'sources/ui/worldtree'
ART = ROOT / 'ui/preview/UI/art/worldtree'


def validate(topology):
    nodes = topology['nodes']
    edges = topology['edges']
    by_id = {node['id']: node for node in nodes}
    assert len(nodes) == len(by_id) == 24
    assert len(edges) == len({edge['id'] for edge in edges}) == 23
    assert Counter(node['role'] for node in nodes) == {'root': 1, 'trunk': 2, 'primary': 3, 'secondary': 6, 'terminal': 12}
    assert by_id['root']['parent'] is None
    pairs = {(edge['from'], edge['to']) for edge in edges}
    assert len(pairs) == 23
    assert pairs == {(node['parent'], node['id']) for node in nodes if node['parent'] is not None}
    children = Counter(edge['from'] for edge in edges)
    for node in nodes:
        expected = {'root': 1, 'trunk': 1 if node['id'] == 'trunk_1' else 3, 'primary': 2, 'secondary': 2, 'terminal': 0}[node['role']]
        assert children[node['id']] == expected
        current = node['id']
        seen = set()
        while current is not None:
            assert current in by_id and current not in seen
            seen.add(current)
            current = by_id[current]['parent']
        assert 'root' in seen
    return {'nodes': 24, 'edges': 23, 'unique_ids': True, 'canonical_parent_edges': True, 'acyclic': True,
            'roles': dict(Counter(node['role'] for node in nodes)), 'stage_counts': [len(f['owned']) for f in topology['activation_fixtures']]}


class WorldtreeContracts(unittest.TestCase):
    def test_exact_canonical_topology(self):
        canonical = json.loads((SOURCE / 'reference/canonical/worldtree_topology.json').read_text())
        runtime = json.loads((ART / 'topology.json').read_text())
        self.assertEqual(runtime, canonical)
        self.assertEqual(validate(runtime)['stage_counts'], [1, 3, 6, 10])
        self.assertEqual(set(runtime['activation_fixtures'][3]['owned']), {'root', 'trunk_1', 'trunk_2'} | {n['id'] for n in runtime['nodes'] if n['group'] == 'left'})

    def test_negative_topology_witnesses(self):
        canonical = json.loads((ART / 'topology.json').read_text())
        for failure in ('duplicate-node', 'duplicate-edge', 'cycle', 'parent'):
            broken = json.loads(json.dumps(canonical))
            if failure == 'duplicate-node': broken['nodes'][1]['id'] = 'root'
            if failure == 'duplicate-edge': broken['edges'][1]['id'] = broken['edges'][0]['id']
            if failure == 'cycle': broken['nodes'][0]['parent'] = 'trunk_1'
            if failure == 'parent': broken['nodes'][4]['parent'] = 'root'
            with self.assertRaises(AssertionError): validate(broken)

    def test_sources_icons_and_anchors(self):
        topology = json.loads((ART / 'topology.json').read_text())
        modules = json.loads((ART / 'modules.json').read_text())
        nodes = {n['id']: n for n in topology['nodes']}
        icons = sorted((ART / 'icons').glob('*.svg'))
        self.assertEqual(len(icons), 30)
        self.assertEqual({p.stem for p in icons}, set(topology['icon_catalog']))
        self.assertEqual(len({hashlib.sha256(p.read_bytes()).hexdigest() for p in icons}), 30)
        for path in ART.rglob('*'):
            if path.suffix in ('.json', '.svg'):
                self.assertEqual(path.read_bytes(), (SOURCE / path.relative_to(ART)).read_bytes())
                if path.suffix == '.svg': ET.fromstring(path.read_text())
        self.assertEqual(set(modules), {e['id'] for e in topology['edges']})
        for edge in topology['edges']:
            module = modules[edge['id']]
            self.assertTrue((ART / 'branches' / (edge['id'] + '.svg')).is_file())
            for index, node in ((0, edge['from']), (-1, edge['to'])):
                self.assertEqual(module['points'][index], list(nodes[node]['position'].values()))


if __name__ == '__main__':
    unittest.main()
