"""Fast mechanical contracts for the explicit woodland profile and role decisions."""
import json
import unittest
from pathlib import Path

from tools.asset_pack import art_style as style
from tools.asset_pack.woodland_profiles import BUILDINGS, UNITS

ROOT = Path(__file__).resolve().parents[2]


class WoodlandTests(unittest.TestCase):
    def test_role_inventory_is_complete_and_individually_distinct(self):
        jobs = json.loads((ROOT/'docs/whisperwood/baseline.json').read_text())['jobs']
        for category, profiles in [('buildings', BUILDINGS), ('characters', UNITS)]:
            self.assertEqual({j['id'].split('/')[-1] for j in jobs if j['id'].startswith(category+'/')}, set(profiles))
            self.assertEqual(len({p['signature'] for p in profiles.values()}), len(profiles))
            self.assertEqual(len({p['detail'] for p in profiles.values()}), len(profiles))
            for profile in profiles.values():
                self.assertTrue(profile['feature'])
                self.assertTrue(all(v > 0 for v in profile.get('scale', profile.get('factor'))))

    def test_muted_grade_keeps_hue_order_and_bounded_values(self):
        rgb = (.1, .5, .9)
        graded = style.woodland_color(rgb)
        self.assertLess(max(graded)-min(graded), (max(rgb)-min(rgb))*.5)
        self.assertLess(graded[0], graded[1])
        self.assertLess(graded[1], graded[2])
        self.assertTrue(all(0 <= v <= 1 for v in graded))
        self.assertGreater(max(style.woodland_color(rgb, accent=True))-min(style.woodland_color(rgb, accent=True)), max(graded)-min(graded))
        self.assertGreater(style.woodland_color((.8, .5, .3), skin=True)[0], style.woodland_color((.8, .5, .3))[0])

    def test_profile_does_not_migrate_hex_unit_or_painted_contracts(self):
        self.assertEqual((style.HEX.radius, style.HEX.surface, style.HEX.bottom), (2.55, 0, -.36))
        self.assertEqual((style.UNITS.bone_count, style.UNITS.fps), (19, 24))
        self.assertEqual(set(style.CLIP_FRAMES), {'idle', 'walk', 'run', 'attack', 'hit', 'death'})
        self.assertEqual(style.PAINTED_VERSION, 'painted_softness_v1')
        self.assertLess(style.WHISPERWOOD.emission_factor, 1)


if __name__ == '__main__':
    unittest.main()
