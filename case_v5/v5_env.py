"""VLT case v5 — envelope-driven generator.  Each design has its own outer shape:
bezel per side, corner treatment per corner, bezel height, typing angle, front height, wall lean / bulge
(lofted outlines), trapezoid plans and sloped bezel rings.  Interior (key windows, display, ball catch, gasket
pockets, daughterboards) is shared with v3/v4.
"""
import os, sys, math
from dataclasses import dataclass, field
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "case_v3"))
sys.path.insert(0, os.path.join(HERE, "..", "case_v4"))
import cadquery as cq
from params import *
import geom, parts, v4
from geom import box, rrect_prism, cyl_z, cyl_y, cyl_x, sphere
from v4 import key_groups, window_solid, W_CLR, Y_STEP, SF_CX, SF_CY, SF_X0, SF_X1, SF_TABS, SF_NOTCH_Y1, SF_SCREW_Y, layout_keys

FLOOR5 = 3.5


@dataclass
class Env:
    name: str
    bez: tuple = (8.0, 8.0, 8.0, 8.0)                 # left, right, back, front (at the top surface)
    top_z: float = 7.5                                 # bezel top above the plate top
    seam_z: float = -6.0
    tilt: float = 6.0
    h_front: float = 21.5                              # desk → top of the front edge
    corners: tuple = (("r", 3.0),) * 4                 # FL, FR, BR, BL : ("r", radius) | ("c", chamfer)
    bottom_off: tuple = (0.0, 0.0, 0.0, 0.0)           # outline offset at desk level: left, right, back, front (+ = wider base)
    bulge: float = 0.0                                 # convex walls: mid-height outward bulge (mm)
    top_slope: float = 0.0                             # bezel ring descends this much at the window edge
    top_chamfer: float = 1.5
    bottom_chamfer: float = 1.2
    screen: str = "island"                             # "island" (between PgDn and →) | "frow" (left of the knob)
    deck_raise: float = 0.0
    top_light: tuple = ("bar05",)
    front_light: str = "band"
    underglow: str = "ring"
    weight: dict = field(default_factory=lambda: dict(kind="octagon", size=(200.0, 56.0, 4.0, 12.0), pocket=3.0, dy=0.0))
    bumpon_in: float = 20.0
    bar_chan_w: float = 4.5
    bar_slot_w: float = 3.0
    extra: dict = field(default_factory=dict)

    # ---- derived ----
    @property
    def x0(self): return -self.bez[0]
    @property
    def x1(self): return KEYS_W + self.bez[1]
    @property
    def y1(self): return self.bez[2]
    @property
    def y0(self): return -(KEYS_H + self.bez[3])
    @property
    def W(self): return self.x1 - self.x0
    @property
    def D(self): return self.y1 - self.y0
    @property
    def tilt_r(self): return math.radians(self.tilt)
    @property
    def island_top(self):
        base = self.top_z + (self.deck_raise if self.screen == "frow" else 0.0)
        return max(base, TOP_Z)
    @property
    def dz_screen(self): return self.island_top - TOP_Z
    @property
    def tabs(self): return SF_TABS if self.screen == "frow" else PLATE_TAB_X

    def desk_z(self, y):
        """z of the desk plane in the plate frame at plate-frame y"""
        return self.top_z - self.h_front / math.cos(self.tilt_r) - (y - self.y0) * math.tan(self.tilt_r)

    def desk_to_plate(self, wp):
        return wp.rotate((0, 0, 0), (1, 0, 0), -self.tilt).translate((0, self.y0, self.top_z))

    def desk_box(self, x0, x1, yd0, yd1, zd0, zd1):
        return self.desk_to_plate(box(x0, x1, yd0, yd1, zd0, zd1))

    @property
    def floor_zd(self): return -self.h_front + FLOOR5


# ---------------------------------------------------------------- outline + shell
def outline_pts(env, off=(0, 0, 0, 0), scale_corner=1.0):
    """closed polyline (list of points) of the plan outline with per-corner round/chamfer, offset per side"""
    x0, x1 = env.x0 - off[0], env.x1 + off[1]
    y1, y0 = env.y1 + off[2], env.y0 - off[3]
    corners = [((x0, y0), (1, 1)), ((x1, y0), (-1, 1)), ((x1, y1), (-1, -1)), ((x0, y1), (1, -1))]   # FL, FR, BR, BL (ccw)
    pts = []
    for (cx, cy), (sx, sy), spec in [(c[0], c[1], s) for c, s in zip(corners, env.corners)]:
        kind, v = spec
        v = v * scale_corner
        if kind == "c":
            # chamfer: two points, order depends on travel direction (ccw starting at FL going +x)
            a, b = (cx, cy + sy * v), (cx + sx * v, cy)
            pts += [a, b] if (sx, sy) in ((1, 1), (-1, -1)) else [b, a]
        else:
            r = v
            ccx, ccy = cx + sx * r, cy + sy * r
            # arc from the incoming edge to the outgoing edge, 8 segments
            ang0 = {(1, 1): 180, (-1, 1): 270, (-1, -1): 0, (1, -1): 90}[(sx, sy)]
            for i in range(9):
                a = math.radians(ang0 + 90 * i / 8)
                pts.append((ccx + r * math.cos(a), ccy + r * math.sin(a)))
    return pts


def outer_shell(env):
    z_top, z_bot = env.top_z, -45.0
    z_ref = env.desk_z(env.y0)                       # desk at the front edge: where bottom_off is defined
    k = (z_top - z_bot) / (z_top - z_ref)            # extrapolate the offsets to the loft's bottom
    off_bot = tuple(o * k for o in env.bottom_off)
    wp = cq.Workplane("XY").workplane(offset=z_top).polyline(outline_pts(env)).close()
    if env.bulge:
        z_mid = (z_top + z_ref) / 2
        off_mid = tuple(o * (z_top - z_mid) / (z_top - z_ref) + env.bulge for o in env.bottom_off)
        wp = wp.workplane(offset=z_mid - z_top).polyline(outline_pts(env, off_mid)).close()
        wp = wp.workplane(offset=z_bot - z_mid).polyline(outline_pts(env, off_bot)).close()
        s = wp.loft(ruled=False)
    else:
        wp = wp.workplane(offset=z_bot - z_top).polyline(outline_pts(env, off_bot)).close()
        s = wp.loft(ruled=True)
    s = s.intersect(env.desk_box(-200, env.W + 200, -200, env.D + 200, -env.h_front, 120))
    if env.bottom_chamfer > 0:
        s = s.intersect(bottom_cap(env, env.bottom_chamfer))
    return s


def _loft2(pts_a, za, pts_b, zb):
    return (cq.Workplane("XY").workplane(offset=za).polyline(pts_a).close()
            .workplane(offset=zb - za).polyline(pts_b).close().loft(ruled=True))


def top_cap(env, c, z_top):
    """keep-solid whose top is a c × 45° chamfer of the outline: intersect the top case with it (robust on lofted shells)"""
    cap = _loft2(outline_pts(env, (0.2, 0.2, 0.2, 0.2)), z_top - c, outline_pts(env, (-c + 0.2,) * 4), z_top)
    below = cq.Workplane("XY").workplane(offset=-80).polyline(outline_pts(env, (20, 20, 20, 20))).close().extrude(80 + z_top - c + 0.01)
    return below.union(cap)


def bottom_cap(env, c):
    """same idea for the bottom edge, built in the desk frame around the loft's outline at desk level"""
    ob = tuple(o + 0.4 for o in env.bottom_off)
    zd0 = -env.h_front
    ct, tt = math.cos(env.tilt_r), math.tan(env.tilt_r)
    def dpts(off):   # plate-frame outline → desk-frame footprint (y stretched by the tilt, pivot at the front edge)
        return [(x, (y - env.y0) / ct + env.h_front * tt) for x, y in outline_pts(env, off)]
    cap = _loft2(dpts(tuple(o - c for o in ob)), zd0, dpts(ob), zd0 + c)
    above = cq.Workplane("XY").workplane(offset=zd0 + c - 0.01).polyline(dpts(tuple(o + 20 for o in ob))).close().extrude(90)
    return env.desk_to_plate(above.union(cap))


def slab(env, z0, z1):
    return box(env.x0 - 60, env.x1 + 60, env.y0 - 60, env.y1 + 60, z0, z1)


def bezel_ring_footprint(env, z0, z1):
    outer = cq.Workplane("XY").workplane(offset=z0).polyline(outline_pts(env, (3, 3, 3, 3))).close().extrude(z1 - z0)
    hull = box(-CLR, KEYS_W + CLR, -(KEYS_H + CLR), CLR, z0 - 1, z1 + 1)
    return outer.cut(hull)


def slope_bezel(tc, env):
    """the bezel ring descends env.top_slope from the outer edge to the window edge, on all four sides"""
    big = 600
    ring = bezel_ring_footprint(env, env.top_z - 30, env.top_z + 30)
    for side in ("left", "right", "front", "back"):
        # each side's plane only acts on its own bezel strip (the strips overlap at the corners → natural mitre)
        if side == "left":
            p0, p1 = (env.x0, env.y0 - big, env.top_z), (env.x0, env.y1 + big, env.top_z); bw = env.bez[0]
            hs = box(env.x0 - 5, env.x0 + bw + CLR + 0.5, env.y0 - big, env.y1 + big, env.top_z, env.top_z + big)
        elif side == "right":
            p0, p1 = (env.x1, env.y0 - big, env.top_z), (env.x1, env.y1 + big, env.top_z); bw = env.bez[1]
            hs = box(env.x1 - bw - CLR - 0.5, env.x1 + 5, env.y0 - big, env.y1 + big, env.top_z, env.top_z + big)
        elif side == "back":
            p0, p1 = (env.x0 - big, env.y1, env.top_z), (env.x1 + big, env.y1, env.top_z); bw = env.bez[2]
            hs = box(env.x0 - big, env.x1 + big, env.y1 - bw - CLR - 0.5, env.y1 + 5, env.top_z, env.top_z + big)
        else:
            p0, p1 = (env.x0 - big, env.y0, env.top_z), (env.x1 + big, env.y0, env.top_z); bw = env.bez[3]
            hs = box(env.x0 - big, env.x1 + big, env.y0 - 5, env.y0 + bw + CLR + 0.5, env.top_z, env.top_z + big)
        ang = math.degrees(math.atan2(env.top_slope, bw))
        probe = cq.Workplane("XY").box(0.5, 0.5, 0.5)
        if side in ("left", "right"):
            probe = probe.translate((env.x0 + bw / 2 if side == "left" else env.x1 - bw / 2, (env.y0 + env.y1) / 2, env.top_z - env.top_slope / 4))
        else:
            probe = probe.translate(((env.x0 + env.x1) / 2, env.y1 - bw / 2 if side == "back" else env.y0 + bw / 2, env.top_z - env.top_slope / 4))
        for sgn in (1, -1):
            cutter = hs.rotate(p0, p1, sgn * ang)
            if cutter.intersect(probe).val().Volume() > 0.001:
                tc = tc.cut(cutter.intersect(ring))
                break
    return tc
