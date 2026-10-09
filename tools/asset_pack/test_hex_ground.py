"""Fast topology tests; saved-source/GLB integration is verify_ground_blender.py."""
import itertools
import math
import unittest

from tools.asset_pack import art_style as style, hex_ground as ground


class GroundTopology(unittest.TestCase):
    def test_full_rotation_coverage(self):
        pairs, ends = ground.coverage()
        self.assertEqual(set(pairs), set(itertools.combinations(range(6), 2)))
        self.assertEqual(set(ends), {(edge,) for edge in range(6)})
        self.assertEqual(len(ground.IDS), 13)

    def test_ribbons_inside_footprint_and_height_envelope(self):
        for family in ('path', 'river'):
            for piece in ground.PIECES:
                vertices, faces, uvs = ground.ribbon(family, piece)
                self.assertEqual(len(vertices), len(uvs))
                self.assertTrue(all(style.HEX.contains(x, y, 1e-6) for x, y, z in vertices))
                self.assertGreaterEqual(min(p[2] for p in vertices), .006)
                self.assertLessEqual(max(p[2] for p in vertices), .016)
                self.assertTrue(all(0 <= index < len(vertices) for face in faces for index in face))
                self.assertTrue(all(math.isfinite(c) for uv in uvs for c in uv))

    def test_water_width_and_edge_normal_approaches(self):
        profile = style.GROUND.profile('river')
        self.assertAlmostEqual((profile[4][0]-profile[2][0])*style.GROUND.width('river'), style.HEX.water_width)
        for piece in ground.PIECES:
            points, tangents = ground.centerline(piece)
            for edge, index, adjacent in [(0, 0, 1)] + ([] if piece == 'end' else
                                       [(ground.PIECES[piece][1], -1, -2)]):
                n = ground.normal(edge)
                self.assertAlmostEqual(sum(points[index][j]*n[j] for j in range(2)), style.HEX.half_height)
                delta = tuple(points[adjacent][j]-points[index][j] for j in range(2))
                self.assertAlmostEqual(delta[0]*n[1]-delta[1]*n[0], 0)
                self.assertAlmostEqual(abs(tangents[index][0]*n[0]+tangents[index][1]*n[1]), 1)

    def test_end_is_centered_not_an_opposite_connector(self):
        for family in ('path', 'river'):
            vertices, _, _ = ground.ribbon(family, 'end')
            self.assertAlmostEqual(min(v[1] for v in vertices), -style.GROUND.width(family)/2*math.sin(8*math.pi/17))
            self.assertGreater(min(v[1] for v in vertices), -style.HEX.half_height)


if __name__ == '__main__':
    unittest.main()
