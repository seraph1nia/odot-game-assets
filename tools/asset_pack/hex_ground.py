"""Pure authoring topology for the detailed ground suite, not a runtime generator."""
import math

try:
    from . import art_style as style
except ImportError:
    import art_style as style

BASES = ('moss', 'grass', 'dirt', 'leaf_litter', 'pine_duff')
PIECES = {'straight': (0, 3), 'turn_120': (0, 2), 'turn_60': (0, 1), 'end': (0,)}
IDS = tuple('environment/hex_ground_' + name for name in BASES) + tuple(
    f'environment/hex_{family}_{piece}' for family in ('path', 'river_overlay') for piece in PIECES)


def normal(edge):
    angle = edge * math.pi / 3
    return (-math.sin(angle), math.cos(angle))


def rotate(point, turns):
    a = turns * math.pi / 3
    x, y, *rest = point
    return (math.cos(a)*x - math.sin(a)*y, math.sin(a)*x + math.cos(a)*y, *rest)


def coverage():
    """All unordered pairs once, plus the six center dead ends."""
    pairs, ends = {}, {}
    for piece, edges in PIECES.items():
        for turns in range(3 if piece == 'straight' else 6):
            key = tuple(sorted((edge + turns) % 6 for edge in edges))
            (ends if piece == 'end' else pairs)[key] = (piece, turns)
    return pairs, ends


def centerline(piece):
    """XY centers and exact tangents; endpoint approaches are truly straight."""
    a = style.HEX.half_height
    approach = style.GROUND.approach
    edges = PIECES[piece]
    n0 = normal(edges[0])
    start = tuple(a * v for v in n0)
    shoulder = tuple((a - approach) * v for v in n0)
    if piece in ('straight', 'end'):
        length = 2 * a if piece == 'straight' else a
        count = style.GROUND.curve_steps
        points = [(start[0] - n0[0]*length*i/count, start[1] - n0[1]*length*i/count)
                  for i in range(count+1)]
        return points, [(-n0[0], -n0[1])] * len(points)
    n1 = normal(edges[1])
    end = tuple(a * v for v in n1)
    p3 = tuple((a - approach) * v for v in n1)
    # Inward controls keep even the adjacent-edge bend safely inside the hex.
    handle = .92 if piece == 'turn_60' else 1.22
    p1 = tuple(shoulder[j] - handle*n0[j] for j in range(2))
    p2 = tuple(p3[j] - handle*n1[j] for j in range(2))
    points = [start, shoulder]
    tangents = [(-n0[0], -n0[1])] * 2
    for i in range(1, style.GROUND.curve_steps):
        t = i / style.GROUND.curve_steps
        s = 1 - t
        points.append(tuple(s**3*shoulder[j] + 3*s*s*t*p1[j] + 3*s*t*t*p2[j] + t**3*p3[j]
                            for j in range(2)))
        d = tuple(3*s*s*(p1[j]-shoulder[j]) + 6*s*t*(p2[j]-p1[j]) + 3*t*t*(p3[j]-p2[j])
                  for j in range(2))
        length = math.hypot(*d)
        tangents.append(tuple(v/length for v in d))
    return points + [p3, end], tangents + [n1, n1]


def ribbon(family, piece):
    """Vertices/faces/vertex UVs, with a concentric rounded center terminal."""
    points, tangents = centerline(piece)
    profile = style.GROUND.profile(family)
    width = style.GROUND.width(family)
    distances = [0.0]
    for a, b in zip(points, points[1:]):
        distances.append(distances[-1] + math.dist(a, b))
    verts, uvs = [], []
    for p, t, distance in zip(points, tangents, distances, strict=True):
        for cross, z in profile:
            verts.append((p[0] - t[1]*cross*width, p[1] + t[0]*cross*width, z))
            uvs.append((cross+.5, distance/distances[-1]))
    cols = len(profile)
    faces = [(i*cols+j, (i+1)*cols+j, (i+1)*cols+j+1, i*cols+j+1)
             for i in range(len(points)-1) for j in range(cols-1)]
    if piece == 'end':
        # Half disk beyond center. Radial rings continue the exact ribbon profile;
        # coordinates at theta=0/pi weld to the last row, avoiding coplanar caps.
        middle = cols//2
        center = (len(points)-1)*cols + middle
        rings = []
        for j in range(middle+1, cols):
            radius = profile[j][0]*width
            ring = [(len(points)-1)*cols+j]
            for i in range(1, 17):
                angle = math.pi*i/17
                ring.append(len(verts))
                verts.append((radius*math.cos(angle), -radius*math.sin(angle), profile[j][1]))
                uvs.append((.5 + profile[j][0]*math.cos(angle), 1 - radius*math.sin(angle)/distances[-1]))
            ring.append((len(points)-1)*cols+(cols-1-j))
            rings.append(ring)
        for i in range(17):
            faces.append((center, rings[0][i+1], rings[0][i]))
        for inner, outer in zip(rings, rings[1:]):
            for i in range(17):
                faces.append((inner[i], inner[i+1], outer[i+1], outer[i]))
    return verts, faces, uvs
