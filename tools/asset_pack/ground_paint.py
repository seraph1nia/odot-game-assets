"""Authored painted forest-ground fields; portable images, not procedural shaders.

Explicit unequal patch layouts own macro composition. Seeded brush variation adds
subordinate leaves/blades/cushions within those patches, never particle geometry.
"""
import math
import random

import numpy as np

try:
    from . import art_style as style
except ImportError:
    import art_style as style

PATCHES = {
    'moss': ((-1.25, .78, 1.02, .65, -.45), (.53, 1.07, .85, .54, .32),
             (1.30, -.42, .63, .96, -.71), (-.81, -1.05, 1.02, .61, .22), (.07, -.11, .43, .31, .82)),
    'grass': ((-1.31, -.48, .83, .99, -.32), (-.57, 1.06, 1.10, .45, .18),
              (.78, .50, 1.01, .67, -.54), (.62, -1.24, .83, .47, .3)),
    'dirt': ((-1.10, .56, .90, .51, -.73), (.31, 1.32, .87, .36, .1),
             (1.22, -.52, .59, .86, -.45), (-.51, -1.28, 1.02, .37, .13)),
    'leaf_litter': ((-1.23, .17, .75, 1.14, -.23), (.40, 1.18, 1.04, .50, -.34),
                    (1.04, -.42, .78, .91, .42), (-.50, -1.24, 1.06, .45, -.38), (.1, .15, .38, .40, .4)),
    'pine_duff': ((-1.23, .65, .98, .54, -.8), (.68, 1.16, .78, .52, .7),
                  (1.16, -.44, .64, .89, -.4), (-.78, -1.04, 1.04, .51, 2.4), (.14, -.13, .40, .32, .2)),
}


class Painting:
    def __init__(self, family, size):
        self.size = size
        self.radius = style.HEX.radius
        self.base, self.light, self.dark = map(np.array, style.GROUND.colors(family))
        v, u = np.mgrid[0:size, 0:size].astype(np.float32)/(size-1)
        self.x, self.y = (u-.5)*2*self.radius, (v-.5)*2*self.radius
        wash = (np.sin(self.x*4+self.y*2) + .5*np.sin(self.y*9-self.x*5))/1.5
        grain = np.sin(self.x*87+self.y*51)*np.cos(self.y*113-self.x*63)
        self.rgb = np.clip(self.base*(1+.055*wash[:, :, None]+.015*grain[:, :, None]), 0, 1)
        self.height = .0003*wash + .00012*grain
        self.rng = random.Random(218 + sum(map(ord, family)))

    def brush(self, x, y, rx, ry, angle, color, kind='leaf', opacity=1):
        """Antialiased local stamp with related-color edge/root variation."""
        radius = math.hypot(rx, ry)*1.4
        scale = (self.size-1)/(2*self.radius)
        ix0, ix1 = max(0, int((x-radius+self.radius)*scale)), min(self.size, int((x+radius+self.radius)*scale)+1)
        iy0, iy1 = max(0, int((y-radius+self.radius)*scale)), min(self.size, int((y+radius+self.radius)*scale)+1)
        if ix1 <= ix0 or iy1 <= iy0:
            return
        sl = np.s_[iy0:iy1, ix0:ix1]
        dx, dy = self.x[sl]-x, self.y[sl]-y
        s = (dx*math.cos(angle)+dy*math.sin(angle))/rx
        t = (-dx*math.sin(angle)+dy*math.cos(angle))/ry
        if kind in ('leaf', 'fallen'):
            # Pointed blades or lobed decomposing oak leaves; curved midribs.
            s = s - .12*np.sin(t*math.pi)
            boundary = np.maximum(0, 1-t*t)
            if kind == 'fallen':
                boundary *= .91+.17*np.cos(t*17)
            distance = np.abs(s)/np.maximum(.02, boundary*.86)
            mask = np.clip((1-distance)*10, 0, 1)*np.clip((1-abs(t))*14, 0, 1)
            vein = np.exp(-(s/.06)**2)*np.clip(1-abs(t), 0, 1)
            fine = np.exp(-(np.sin(t*19-abs(s)*13)/.15)**2)
            value = .80+.16*(1-abs(s))+.10*vein+.036*fine
        elif kind == 'cushion':
            phi = np.arctan2(t, s)
            edge = 1+.07*np.sin(phi*5)+.04*np.sin(phi*9+.4)
            distance = np.hypot(s, t)/edge
            mask = np.clip((1-distance)*9, 0, 1)
            value = .74+.30*np.clip(1-distance, 0, 1)+.045*np.sin(s*19+t*13)
        else:
            distance = np.sqrt(s*s+t*t)
            mask = np.clip((1-distance)*8, 0, 1)
            value = .86+.12*np.clip(1-distance, 0, 1)
        shadow = np.exp(-((distance-1.01)/.11)**2)*.09*opacity
        self.rgb[sl] *= 1-shadow[:, :, None]
        blend = mask*opacity
        self.rgb[sl] = self.rgb[sl]*(1-blend[:, :, None]) + np.array(color)*value[:, :, None]*blend[:, :, None]
        self.height[sl] += .0011*mask*opacity

    def line(self, points, width, color, opacity=1):
        for a, b in zip(points, points[1:]):
            dx, dy = b[0]-a[0], b[1]-a[1]
            self.brush((a[0]+b[0])/2, (a[1]+b[1])/2, math.hypot(dx, dy)/2+width,
                       width, math.atan2(dy, dx), color, 'stone', opacity)

    def patch(self, patch, color, strength):
        x, y, rx, ry, a = patch
        s = ((self.x-x)*math.cos(a)+(self.y-y)*math.sin(a))/rx
        t = (-(self.x-x)*math.sin(a)+(self.y-y)*math.cos(a))/ry
        phi = np.arctan2(t, s)
        radius = np.hypot(s, t)/(1+.12*np.sin(phi*5+.7)+.08*np.sin(phi*3))
        mask = np.clip((1.35-radius)*2.5, 0, 1)*strength
        self.rgb = self.rgb*(1-mask[:, :, None])+np.array(color)*mask[:, :, None]

    def cluster_points(self, patch, count):
        x, y, rx, ry, a = patch
        for _ in range(count):
            phi = self.rng.uniform(0, math.tau)
            r = math.sqrt(self.rng.random())*.96
            dx, dy = rx*r*math.cos(phi), ry*r*math.sin(phi)
            yield x+dx*math.cos(a)-dy*math.sin(a), y+dx*math.sin(a)+dy*math.cos(a)

    def finish(self):
        # Every edge has the same neutral profile; arbitrary rotations match.
        distance = np.minimum.reduce([style.HEX.half_height - self.x*n[0] - self.y*n[1]
                                      for n in [(-math.sin(e*math.pi/3), math.cos(e*math.pi/3)) for e in range(6)]])
        keep = np.clip(distance/style.GROUND.edge_fade, 0, 1)
        self.rgb = self.base*(1-keep[:, :, None])+self.rgb*keep[:, :, None]
        self.height *= keep
        return self.rgb, self.height


def floor_fields(family, size):
    p = Painting(family, size)
    if family == 'foundation':
        return p.rgb, p.height, np.full((size, size), .90, dtype=np.float32)
    patches = PATCHES[family]
    for i, patch in enumerate(patches):
        color = p.light if i % 2 == 0 else p.dark
        if family == 'grass':
            color = np.array((.44, .38, .23)) if i%2 else p.dark
        p.patch(patch, color, .68 if family in ('moss', 'grass') else .48)
        if family == 'moss':
            for x, y in p.cluster_points(patch, 140):
                r = p.rng.uniform(.034, .115)
                color = p.light*(p.rng.uniform(.83, 1.06)) if i%2==0 else p.base*p.rng.uniform(.88, 1.14)
                p.brush(x, y, r, r*.78, p.rng.random()*6, color, 'cushion', .88)
        elif family == 'grass':
            for x, y in p.cluster_points(patch, 140):
                direction = patch[4] + p.rng.uniform(-.8, .8)
                for j in range(3):
                    p.brush(x+.023*j, y-.012*j, p.rng.uniform(.012, .023), p.rng.uniform(.045, .12),
                            direction+j*.35, p.light*p.rng.uniform(.76, 1.04), opacity=.8)
        elif family == 'leaf_litter':
            for x, y in p.cluster_points(patch, 95):
                colors = (p.light, p.base*1.12, np.array((.48, .28, .15)), np.array((.37, .38, .18)))
                length = p.rng.uniform(.055, .22)
                p.brush(x, y, length*.47, length, p.rng.random()*math.tau,
                        colors[p.rng.randrange(len(colors))]*p.rng.uniform(.90, 1.05), kind='fallen', opacity=.93)
        elif family == 'pine_duff':
            for x, y in p.cluster_points(patch, 90):
                direction = patch[4]+p.rng.uniform(-.9, .9)
                for j in range(3):
                    length = p.rng.uniform(.05, .14)
                    end = (x+length*math.cos(direction+j*.16), y+length*math.sin(direction+j*.16))
                    p.line([(x, y), end], .004, p.light*p.rng.uniform(.82, 1.06), .9)
    # Ground-story traces, intentionally placed rather than uniformly scattered.
    roots = (((-1.70, -.25), (-1.20, -.02), (-.95, .22), (-.56, .27)),
             ((.70, -1.59), (.51, -1.27), (.29, -.93), (.08, -.81)),
             ((1.51, .77), (1.28, .55), (.92, .51)))
    for root in roots:
        p.line(root, .027 if family == 'dirt' else .017, p.dark*.80, .87)
        p.line(root, .010 if family == 'dirt' else .006, p.light*.80, .85)
        a = root[1]
        p.line([a, (a[0]+.14, a[1]+.15), (a[0]+.28, a[1]+.18)], .009, p.dark*.84, .85)
    if family == 'dirt':
        # Small branched erosion marks within the broad worn pockets, not a web.
        for x, y in p.cluster_points(patches[0], 16):
            p.line([(x-.10, y-.03), (x-.035, y+.01), (x+.027, y), (x+.09, y+.045)],
                   .0035, p.dark*.83, .66)
    # Sparse embedded pebbles and fragment leaves follow a few contact drifts.
    for patch in (patches[0], patches[2], patches[3]):
        for x, y in p.cluster_points(patch, 18 if family == 'dirt' else 5):
            r = p.rng.uniform(.025, .075) if family == 'dirt' else p.rng.uniform(.013, .037)
            p.brush(x, y, r, r*.69, p.rng.random()*6, (.52, .50, .38), 'stone', .85)
        if family in ('dirt', 'moss', 'grass'):
            for x, y in p.cluster_points(patch, 9):
                p.brush(x, y, .04, .09, p.rng.random()*6, (.43, .34, .19), opacity=.88)
    if family == 'pine_duff':
        # Paired, tapered leaflets create recognizable flattened fern silhouettes.
        for x, y, angle, length in ((-1.23, .65, -.8, .55), (.65, 1.23, .7, .48),
                                     (1.18, -.36, -.4, .62), (-.72, -1.05, 2.4, .51), (.15, -.12, .2, .38)):
            axis = (math.sin(angle), math.cos(angle))
            p.line([(x, y), (x+axis[0]*length, y+axis[1]*length)], .007, (.49, .53, .24))
            for j in range(1, 9):
                t = j/10
                px, py = x+axis[0]*length*t, y+axis[1]*length*t
                reach = .11*math.sin(math.pi*t)**.7
                for side in (-1, 1):
                    a = angle + side*1.07
                    p.brush(px+side*math.cos(angle)*reach*.5, py-side*math.sin(angle)*reach*.5,
                            .016, reach, a, (.39+.04*t, .49+.06*t, .22), opacity=.96)
    rgb, height = p.finish()
    rough = np.clip(.87 - 9*height + .04*np.sin(p.x*6)*np.cos(p.y*5), .76, .94)
    return rgb, height, rough


def overlay_fields(family, size):
    v, u = np.mgrid[0:size, 0:size].astype(np.float32)/(size-1)
    base, light, dark = map(np.array, style.GROUND.colors(family))
    cross = abs(u-.5)*2
    # Symmetric common endpoint profile, flat in the approach at both map borders.
    endpoint = np.minimum(v, 1-v)
    interior = np.clip((endpoint-.11)*6, 0, 1)
    wash = np.sin(v*39 + np.sin(u*13))*.025 + np.sin(u*117-v*69)*.012
    if family == 'path':
        blend = np.clip(cross**2*.8, 0, 1)
        rgb = light*(1-blend[:, :, None])+dark*blend[:, :, None]
        wear = np.exp(-((abs(u-.5)-.18)/.075)**2)*.075*interior
        rgb *= 1+wash[:, :, None]*interior[:, :, None]-wear[:, :, None]
        fleck = np.clip(np.sin(u*239+v*113)*np.cos(v*331-u*53)-.78, 0, 1)*interior
        rgb += .14*fleck[:, :, None]
        height = .0003*wash*interior + .0006*fleck
        rough = .88+.035*blend-.03*fleck
    else:
        water_edge = style.HEX.water_width/style.GROUND.width('river')
        blend = np.clip(cross/water_edge, 0, 1)**1.4
        rgb = base*(1-blend[:, :, None])+dark*blend[:, :, None]
        ripple = np.exp(-(np.sin(v*67+np.sin(u*13)*2)/.19)**2)
        broken = np.clip(np.sin(u*27-v*17)*2+.4, 0, 1)
        accent = ripple*broken*.21*interior
        rgb = rgb*(1-accent[:, :, None])+light*accent[:, :, None]
        bank = np.clip((cross-water_edge)*120, 0, 1)
        bank_color = np.array((.43, .37, .24))*(.83+.20*(1-cross))[:, :, None]
        rgb = rgb*(1-bank[:, :, None])+bank_color*bank[:, :, None]
        lip = np.exp(-((cross-water_edge-.022)/.017)**2)
        rgb += lip[:, :, None]*np.array((.09, .08, .05))
        height = .0004*ripple*interior*(1-bank)
        rough = .39*(1-bank)+.88*bank
    return np.clip(rgb, 0, 1), height, rough
