"""Top case, bottom case, lights, weights for v5 (envelope-driven)."""
import math
import cadquery as cq
from v5_env import *
from v5_env import Env, outer_shell, slab, slope_bezel, outline_pts, top_cap
from v4 import USB4_PORT_Z, USB4_BOARD_TOP, CHERRY_H, keycaps_cherry, corner_diamond, weight_poly, weight_screws


def bc_z(env):      # plunger axis: 1.8 below the seam (the front floor can be as high as z -9.9 on low fronts)
    return env.seam_z - 1.8


def tab_z0(env):    # skirt tabs reach 1.6 below the plunger axis
    return bc_z(env) - 1.6

LED_CAV_D = 3.5          # LED cavity under a top light channel (COB flex strip 4 mm)


# ---------------------------------------------------------------- top case
def top_case(env, keys):
    shell = outer_shell(env)
    zt = env.top_z + env.deck_raise
    tc = shell.intersect(slab(env, env.seam_z, zt))
    if env.deck_raise:
        tc = tc.cut(box(env.x0 - 1, env.x1 + 1, env.y0 - 1, Y_STEP, env.top_z, zt + 1))
    if env.top_chamfer > 0:
        tc = tc.intersect(top_cap(env, env.top_chamfer, zt))                      # chamfer of the raised tier / whole top
        if env.deck_raise:
            lower = top_cap(env, env.top_chamfer, env.top_z).intersect(box(env.x0 - 5, env.x1 + 5, env.y0 - 5, Y_STEP - 0.3, -90, env.top_z + 5))
            keep_back = box(env.x0 - 5, env.x1 + 5, Y_STEP - 0.3, env.y1 + 5, -90, zt + 5)
            tc = tc.intersect(lower.union(keep_back))
    if env.top_slope:
        tc = slope_bezel(tc, env)
    if env.deck_raise:
        tc = tc.cut(box(-4.0, KEYS_W + 4.0, Y_STEP - 0.01, Y_STEP + 1.5, env.top_z + 0.35, zt - 0.35))
        tc = tc.cut(box(2.0, KEYS_W - 2.0, Y_STEP + 0.6, Y_STEP + 2.4, 0.2, zt - 0.35))
    # raised screen tile for low bezels
    it = env.island_top
    if env.screen == "island" and it > env.top_z + 0.01:
        tc = tc.union(box(ISL_X0, KEYS_W + CLR + 1.0, ISL_Y0, ISL_Y1, env.top_z - 1, it))
    if env.screen == "frow" and it > env.top_z + 0.01:
        tc = tc.union(box(SF_X0, SF_X1 + 1.0, -(U + 3.5), CLR, env.top_z - 1, it))
    for name, cells in key_groups(keys).items():
        if cells:
            tc = tc.cut(window_solid(cells, z1=it + env.deck_raise + 1))
    tc = tc.cut(box(-CLR, KEYS_W + CLR, -(KEYS_H + CLR), CLR, env.seam_z - 0.01, 0.3))     # plate relief
    tc = tc.cut(cyl_z(ENC_CX, ENC_CY, -1, it + env.deck_raise + 1, 4.75))
    # screen
    dz = env.dz_screen
    if env.screen == "frow":
        tc = tc.cut(box(SF_X0 + 0.5, SF_X1 + 0.5, -(U + 3.5), CLR + 0.01, 0.2, ISL_Z0 + dz))
        tc = tc.cut(rrect_prism(SF_CX, SF_CY, CG_W + 2 * CG_GAP, CG_L + 2 * CG_GAP, ISL_Z0 + dz - 1, it + 1, CG_R + CG_GAP))
        tc = tc.cut(box(SF_CX - CART_NOTCH_W / 2, SF_CX + CART_NOTCH_W / 2, CLR - 0.01, SF_NOTCH_Y1, env.seam_z - 1, ISL_Z0 + dz))
        for dx in (-CART_SCREW_DY, CART_SCREW_DY):
            tc = tc.cut(cyl_z(SF_CX + dx, SF_SCREW_Y, ISL_Z0 + dz - 0.5, ISL_Z0 + dz + 3.5, BOSS_TAP / 2))
    else:
        tc = tc.cut(box(ISL_X0 - 0.5, KEYS_W + CLR + 0.01, ISL_Y0 - 0.5, ISL_Y1 + 0.5, 0.2, ISL_Z0 + dz))
        tc = tc.cut(rrect_prism(CG_CX, ISL_CY, CG_L + 2 * CG_GAP, CG_W + 2 * CG_GAP, ISL_Z0 + dz - 1, it + 1, CG_R + CG_GAP))
        tc = tc.cut(box(KEYS_W + CLR - 0.01, CART_NOTCH_X1, ISL_CY - CART_NOTCH_W / 2, ISL_CY + CART_NOTCH_W / 2, env.seam_z - 1, ISL_Z0 + dz))
        for dy in (-CART_SCREW_DY, CART_SCREW_DY):
            tc = tc.cut(cyl_z(CART_SCREW_X, ISL_CY + dy, ISL_Z0 + dz - 0.5, ISL_Z0 + dz + 3.5, BOSS_TAP / 2))
    # gasket pockets
    back, front = geom.tab_pocket_ranges()
    for xt in env.tabs:
        for y0, y1 in (back, front):
            tc = tc.cut(box(xt - PLATE_TAB_W / 2 - POCKET_X_CLR, xt + PLATE_TAB_W / 2 + POCKET_X_CLR, y0, y1, env.seam_z - 1, GASKET_T - 0.5))
    # ball-catch skirt tabs
    for xc in BC_BACK_X:
        tc = tc.union(box(xc - BC_TAB_W / 2, xc + BC_TAB_W / 2, CLR - 0.1 - BC_TAB_T, CLR - 0.1, tab_z0(env), env.seam_z + 0.01))
        tc = tc.cut(sphere(xc, CLR - 0.1 + 0.5, bc_z(env), BC_DIMPLE_R))
    for xc in BC_FRONT_X:
        yf = -(KEYS_H + CLR) + 0.1
        tc = tc.union(box(xc - BC_TAB_W / 2, xc + BC_TAB_W / 2, yf, yf + BC_TAB_T, tab_z0(env), env.seam_z + 0.01))
        tc = tc.cut(sphere(xc, yf - 0.5, bc_z(env), BC_DIMPLE_R))
    xl = -CLR + 0.1
    tc = tc.union(box(xl, xl + BC_TAB_T, BC_LEFT_Y - BC_TAB_W / 2, BC_LEFT_Y + BC_TAB_W / 2, tab_z0(env), env.seam_z + 0.01))
    tc = tc.cut(sphere(xl - 0.5, BC_LEFT_Y, bc_z(env), BC_DIMPLE_R))
    xr = KEYS_W + CLR - 0.1
    tc = tc.union(box(xr - BC_TAB_T, xr, BC_RIGHT_Y - BC_TAB_W / 2, BC_RIGHT_Y + BC_TAB_W / 2, tab_z0(env), env.seam_z + 0.01))
    tc = tc.cut(sphere(xr + 0.5, BC_RIGHT_Y, bc_z(env), BC_DIMPLE_R))
    # case-LED light shapes on the top
    for feat in top_light_cuts(env):
        tc = tc.cut(feat)
    return tc


# ---------------------------------------------------------------- top lights ("case LEDs")
def top_light_shapes(env):
    """list of (plan-shape workplane-2D maker, z_top) → each gives a flush frosted insert 1.2 deep + LED cavity below"""
    shapes = []
    zt = env.top_z
    ztf = env.top_z + env.deck_raise           # F-row tier
    for kind in env.top_light:
        if kind == "bar05":
            bcw = env.bar_chan_w
            for ya, yb in BAR_SEGMENTS:
                z = ztf if ya > Y_STEP else zt
                shapes.append((("rect", BAR_CX - bcw / 2, yb, BAR_CX + bcw / 2, ya), z, True))   # True = fed from the PCB through a slot
        elif kind == "back_bar":
            shapes.append((("rect", 12.0, env.y1 - env.bez[2] + 2.0, KEYS_W - 12.0, env.y1 - env.bez[2] + 5.5), ztf, False))
        elif kind == "chin_line":
            yc = env.y0 + env.bez[3] / 2
            shapes.append((("rect", 14.0, yc - 1.75, KEYS_W - 14.0, yc + 1.75), zt, False))
        elif kind == "frow_dots":
            for ux in (0.5, 2.75, 7.0, 11.25, 14.5):
                shapes.append((("circle", ux * U, env.y1 - env.bez[2] + 4.0, 2.0), ztf, False))
        elif kind == "halo":
            shapes.append((("ring", -CLR - 2.5, -(KEYS_H + CLR) - 2.5, KEYS_W + CLR + 2.5, CLR + 2.5, 1.8), zt, False))
        elif kind == "tower_bar":
            x = KEYS_W + CLR + env.bez[1] * 0.55
            shapes.append((("rect", x - 2.5, -112.0, x + 2.5, -8.0), zt, False))
        elif kind == "side_lines":
            for x in (env.x0 + env.bez[0] * 0.5, env.x1 - env.bez[1] * 0.5):
                shapes.append((("rect", x - 1.2, -(KEYS_H) + 6.0, x + 1.2, -6.0), zt, False))
        elif kind == "corner_tri":
            shapes.append((("tri", env.x1 - 4.0, env.y1 - 4.0, 22.0), ztf, False))
    return shapes


def _shape_solid(sh, z0, z1):
    kind = sh[0]
    if kind == "rect":
        _, x0, y0, x1, y1 = sh
        return box(x0, x1, y0, y1, z0, z1)
    if kind == "circle":
        _, cx, cy, r = sh
        return cyl_z(cx, cy, z0, z1, r)
    if kind == "ring":
        _, x0, y0, x1, y1, w = sh
        o = rrect_prism((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0, y1 - y0, z0, z1, 4.0)
        i = rrect_prism((x0 + x1) / 2, (y0 + y1) / 2, x1 - x0 - 2 * w, y1 - y0 - 2 * w, z0 - 1, z1 + 1, 4.0 - w)
        return o.cut(i)
    if kind == "tri":
        _, x, y, s = sh
        return cq.Workplane("XY").polyline([(x, y), (x - s, y), (x, y - s)]).close().extrude(z1 - z0).translate((0, 0, z0))
    raise ValueError(kind)


def top_light_cuts(env):
    cuts = []
    for sh, z, from_pcb in top_light_shapes(env):
        cuts.append(_shape_solid(sh, z - BAR_CHAN_D, z + 1))                              # insert channel
        if from_pcb:
            kind, x0, y0, x1, y1 = sh
            ya2, yb2 = min(y1, -1.5), y0 + 1.0
            if ya2 > yb2:
                cuts.append(box((x0 + x1) / 2 - env.bar_slot_w / 2, (x0 + x1) / 2 + env.bar_slot_w / 2, yb2, ya2, -1, z - BAR_CHAN_D + 0.01))
        else:
            cuts.append(_shape_solid(_shrink(sh, 0.3), z - BAR_CHAN_D - LED_CAV_D, z - BAR_CHAN_D + 0.01))   # LED cavity
    return cuts


def _shrink(sh, d):
    if sh[0] == "rect":
        return ("rect", sh[1] + d, sh[2] + d, sh[3] - d, sh[4] - d)
    if sh[0] == "circle":
        return ("circle", sh[1], sh[2], max(sh[3] - d, 0.5))
    if sh[0] == "ring":
        return ("ring", sh[1] + d, sh[2] + d, sh[3] - d, sh[4] - d, max(sh[5] - 2 * d, 0.5))
    if sh[0] == "tri":
        return ("tri", sh[1] - d, sh[2] - d, sh[3] - 2.5 * d)
    return sh


def top_light_inserts(env):
    s = None
    for sh, z, _ in top_light_shapes(env):
        p = _shape_solid(_shrink(sh, 0.05), z - BAR_CHAN_D + 0.02, z)
        s = p if s is None else s.union(p)
    return s


# ---------------------------------------------------------------- bottom case
def bottom_case(env):
    shell = outer_shell(env)
    bc = shell.intersect(slab(env, -80, env.seam_z))
    cav = box(-CLR, KEYS_W + CLR, -(KEYS_H + CLR), CLR, -80, env.seam_z + 1).intersect(env.desk_box(-200, env.W + 200, -200, env.D + 200, env.floor_zd, 80))
    bc = bc.cut(cav)
    back, front = geom.tab_pocket_ranges()
    for xt in env.tabs:
        for y0, y1 in (back, front):
            bc = bc.union(box(xt - PLATE_TAB_W / 2, xt + PLATE_TAB_W / 2, y0 + 0.3, y1 - 0.3, env.seam_z - 0.01, -3.0))
    boss_tops = [(USB_CX + dx, USB_SCREW_Y, USB4_BOARD_TOP - BOARD_T) for dx in (-USB_SCREW_DX, USB_SCREW_DX)]
    boss_tops += [(POGO_CX + sx, POGO_CY + sy, POGO_BOARD_TOP_Z - BOARD_T) for sx, sy in
                  ((-POGO_SCREW[0], -POGO_SCREW[1]), (POGO_SCREW[0], -POGO_SCREW[1]), (-POGO_SCREW[0], POGO_SCREW[1]), (POGO_SCREW[0], POGO_SCREW[1]))]
    bosses = None
    for bx, by, bz in boss_tops:
        c = cyl_z(bx, by, -80, bz, BOSS_D / 2); bosses = c if bosses is None else bosses.union(c)
    bc = bc.union(bosses).intersect(shell)
    for bx, by, bz in boss_tops:
        bc = bc.cut(cyl_z(bx, by, bz - 5.0, bz + 0.1, BOSS_TAP / 2))
    plug = rrect_prism(USB_CX, 0, USB_PLUG_W, USB_PLUG_H, 0, env.bez[2] + 8, USB_PLUG_R).rotate((0, 0, 0), (1, 0, 0), -90)
    bc = bc.cut(plug.translate((0, CLR - 1, USB4_PORT_Z)))
    bc = bc.cut(box(USB_CX - 13.5, USB_CX + 13.5, CLR - 0.01, USB_BOARD_Y1, USB4_BOARD_TOP - BOARD_T - 0.3, env.seam_z + 0.01))
    for xc in BC_BACK_X:
        bc = bc.cut(cyl_y(xc, bc_z(env), CLR - 0.5, CLR + BC_DEPTH, BC_TAP / 2))
    for xc in BC_FRONT_X:
        bc = bc.cut(cyl_y(xc, bc_z(env), -(KEYS_H + CLR) - BC_DEPTH, -(KEYS_H + CLR) + 0.5, BC_TAP / 2))
    bc = bc.cut(cyl_x(BC_LEFT_Y, bc_z(env), -CLR - BC_DEPTH, -CLR + 0.5, BC_TAP / 2))
    bc = bc.cut(cyl_x(BC_RIGHT_Y, bc_z(env), KEYS_W + CLR - 0.5, KEYS_W + CLR + BC_DEPTH, BC_TAP / 2))
    # front ambient
    for feat in front_light_cuts(env):
        bc = bc.cut(feat)
    # bottom face
    bf = bottom_face_frame(env)
    zb = -env.h_front
    cx, cy = bf["cx"], bf["cy"]
    w = env.weight
    if w:
        L, Wd, T, C = w["size"]
        pd = w.get("pocket", 3.0)
        wy = cy + w.get("dy", 0.0)
        bc = bc.cut(env.desk_to_plate(weight_poly(L + 2 * WEIGHT_CLR, Wd + 2 * WEIGHT_CLR, C).extrude(pd + 1).translate((cx, wy, zb - 1))))
        for sx, sy in weight_screws(L, Wd):
            bc = bc.cut(env.desk_to_plate(cyl_z(cx + sx, wy + sy, zb - 1, env.floor_zd + 1, 1.7)))
    bi = env.bumpon_in
    for bx in (bf["x0"] + bi, bf["x1"] - bi):
        for by in (bf["yd0"] + bi, bf["yd1"] - bi):
            bc = bc.cut(env.desk_to_plate(cyl_z(bx, by, zb - 1, zb + BUMPON_DEPTH, BUMPON_D / 2)))
    for feat in underglow_cuts(env, bf):
        bc = bc.cut(env.desk_to_plate(feat))
    return bc


def bottom_face_frame(env):
    """extents of the bottom face in the desk frame (the loft may widen/narrow it)"""
    sh = outer_shell(env).rotate((0, env.y0, env.top_z), (1, env.y0, env.top_z), env.tilt)
    sec = cq.Workplane("XY").add(sh.val()).section(env.top_z - env.h_front + 0.5)
    b = sec.val().BoundingBox()
    # back to desk-frame coordinates relative to the pivot (y0 → yd 0)
    return dict(x0=b.xmin, x1=b.xmax, yd0=b.ymin - env.y0, yd1=b.ymax - env.y0, cx=(b.xmin + b.xmax) / 2, cy=(b.ymin + b.ymax) / 2 - env.y0,
                L=b.ymax - b.ymin)


# ---------------------------------------------------------------- front ambient (bottom case front wall, below the seam)
def front_segments(margin=6.0):
    """x spans of the front wall that are free of plungers and gasket ledges"""
    blocked = [(xc - BC_TAB_W / 2 - margin, xc + BC_TAB_W / 2 + margin) for xc in BC_FRONT_X]
    segs, x = [], 12.0
    for b0, b1 in sorted(blocked):
        if b0 - x > 25:
            segs.append((x, b0))
        x = b1
    if KEYS_W - 12.0 - x > 25:
        segs.append((x, KEYS_W - 12.0))
    return segs


def front_light_cuts(env):
    cuts = []
    zf_in = env.desk_z(-(KEYS_H + CLR)) + FLOOR5 / math.cos(env.tilt_r)       # cavity floor at the front wall
    zc = (env.seam_z + zf_in) / 2
    y_in = -(KEYS_H + CLR) + 1.0
    y_out = env.y0 - 25
    k = env.front_light
    if k == "band":
        for x0, x1 in front_segments():
            cuts.append(box(x0, x1, y_out, y_in, zc - 1.5, zc + 1.5))
    elif k == "slots":
        for x0, x1 in front_segments():
            x = x0 + 4
            while x + 4 <= x1:
                cuts.append(box(x, x + 4.0, y_out, y_in, zc - 1.7, zc + 1.7)); x += 9.0
    elif k == "v":
        for sgn in (-1, 1):
            arm = box(0, 60.0, -1.5, 1.5, -30, 30).rotate((0, 0, 0), (0, 1, 0), sgn * 18.0).rotate((0, 0, 0), (0, 0, 1), 90)
            cuts.append(arm.translate((KEYS_W / 2, (y_out + y_in) / 2, zc)).intersect(box(KEYS_W / 2 - 58, KEYS_W / 2 + 58, y_out, y_in, zf_in + 0.6, env.seam_z - 0.6)))
    elif k == "corners":
        for x in (env.x0, env.x1):
            cuts.append(corner_diamond(x, env.y0, 14.0, -80, env.seam_z + 0.01))
            cuts.append(corner_diamond(x, env.y0, 14.0 + 2.0 * math.sqrt(2), -80, env.seam_z + 0.01).intersect(
                box(env.x0 - 1, env.x1 + 1, env.y0 - 1, env.y1, env.desk_z(env.y0) + 2.5, env.seam_z - 1.5)))
    elif k == "lip":
        # the whole front bottom edge becomes a frosted lip: 3 tall × 4 deep rebate along the full length
        cuts.append(env.desk_box(env.x0 + 10, env.x1 - 10, -5, 4.0, -env.h_front - 1, -env.h_front + 3.0))
    elif k == "band_wide":
        for x0, x1 in front_segments():
            cuts.append(box(x0, x1, y_out, y_in, zf_in + 0.8, env.seam_z - 0.8))
    return cuts


def front_light_inserts(env):
    s = None
    for c in front_light_cuts(env):
        p = c.intersect(box(env.x0 - 1, env.x1 + 1, env.y0 - 0.05, env.y0 + 2.0, -80, 20)) if env.front_light != "lip" else \
            c.intersect(env.desk_box(env.x0, env.x1, -1, 3.9, -env.h_front, -env.h_front + 2.9))
        if env.front_light == "corners":
            p = c.intersect(box(env.x0 - 1, env.x1 + 1, env.y0 - 1, env.y1, env.desk_z(env.y0) + 2.6, env.seam_z - 1.6))
        try:
            p = p.intersect(outer_shell(env))
        except Exception:
            pass
        if p.val().Volume() < 0.5:
            continue
        s = p if s is None else s.union(p)
    return s


# ---------------------------------------------------------------- underglow (bottom face, desk frame)
def underglow_cuts(env, bf):
    zb = -env.h_front
    cuts = []
    k = env.underglow
    cx, cy, L = bf["cx"], bf["cy"], bf["L"]
    Wb = bf["x1"] - bf["x0"]
    if k == "ring":
        ri = 10.5
        o = rrect_prism(cx, cy, Wb - 2 * (ri - 1.5), L - 2 * (ri - 1.5), zb - 1, zb + RING_D, 4.0)
        i = rrect_prism(cx, cy, Wb - 2 * (ri + 1.5), L - 2 * (ri + 1.5), zb - 2, zb + RING_D + 1, 1.0)
        cuts.append(o.cut(i))
        s = 18.0
        for x0, x1, y0, y1 in ((bf["x0"] + s, bf["x1"] - s, bf["yd0"] + ri - 1, bf["yd0"] + ri + 1), (bf["x0"] + s, bf["x1"] - s, bf["yd1"] - ri - 1, bf["yd1"] - ri + 1),
                               (bf["x0"] + ri - 1, bf["x0"] + ri + 1, bf["yd0"] + s, bf["yd1"] - s), (bf["x1"] - ri - 1, bf["x1"] - ri + 1, bf["yd0"] + s, bf["yd1"] - s)):
            cuts.append(box(x0, x1, y0, y1, zb - 1, zb + FLOOR5 + 1))
            cuts.append(box(x0 - 1.5, x1 + 1.5, y0 - 1.5, y1 + 1.5, env.floor_zd - 0.01, env.floor_zd + LED_CHAN_D))
    elif k == "panel":
        Lp, Wp = Wb - 60, L - 36
        cuts.append(rrect_prism(cx, cy, Lp + 0.4, Wp + 0.4, zb - 1, zb + 2.5, 6.0))
        for kk in (-1, 1):
            yy = cy + kk * Wp * 0.3
            cuts.append(box(cx - Lp / 2 + 12, cx + Lp / 2 - 12, yy - 1.75, yy + 1.75, zb - 1, zb + FLOOR5 + 1))
            cuts.append(box(cx - Lp / 2 + 10, cx + Lp / 2 - 10, yy - 2.6, yy + 2.6, env.floor_zd - 0.01, env.floor_zd + LED_CHAN_D))
    elif k == "front_strip":
        y0 = bf["yd0"] + 6.0
        cuts.append(box(cx - 110, cx + 110, y0 - 1.5, y0 + 1.5, zb - 1, zb + RING_D))
        cuts.append(box(cx - 100, cx + 100, y0 - 1.0, y0 + 1.0, zb - 1, zb + FLOOR5 + 1))
        cuts.append(box(cx - 101, cx + 101, y0 - 2.5, y0 + 2.5, env.floor_zd - 0.01, env.floor_zd + LED_CHAN_D))
    elif k == "diag":
        n, pitch, ln, wd, ang = 11, 12.0, 24.0, 3.5, 52.0
        for i in range(n):
            sx = cx - 70 + (i - (n - 1) / 2) * pitch
            cuts.append(box(-wd / 2, wd / 2, -ln / 2, ln / 2, zb - 1, zb + FLOOR5 + 1).rotate((0, 0, 0), (0, 0, 1), ang).translate((sx, cy - 24, 0)))
        cuts.append(box(cx - 70 - n * pitch / 2 - 8, cx - 70 + n * pitch / 2 + 8, cy - 34, cy - 14, env.floor_zd - 0.01, env.floor_zd + LED_CHAN_D))
    elif k == "side_strips":
        for x in (bf["x0"] + 9.0, bf["x1"] - 9.0):
            cuts.append(box(x - 1.5, x + 1.5, bf["yd0"] + 18, bf["yd1"] - 18, zb - 1, zb + RING_D))
            cuts.append(box(x - 1.0, x + 1.0, bf["yd0"] + 20, bf["yd1"] - 20, zb - 1, zb + FLOOR5 + 1))
            cuts.append(box(x - 2.5, x + 2.5, bf["yd0"] + 19, bf["yd1"] - 19, env.floor_zd - 0.01, env.floor_zd + LED_CHAN_D))
    return cuts


def underglow_inserts(env, bf):
    zb = -env.h_front
    s = None
    for c in underglow_cuts(env, bf):
        p = c.intersect(box(-500, 500, -500, 500, zb + 0.05, zb + RING_D - 0.05))
        if p.val().Volume() < 0.5:
            continue
        s = p if s is None else s.union(p)
    return env.desk_to_plate(s) if s is not None else None


# ---------------------------------------------------------------- weight (reuse v4's engraving kinds)
def weight(env, bf):
    w = env.weight
    if not w:
        return None
    st = dict(weight=w["kind"] if w["kind"] != "octagon" else "bar", weight_size=w["size"], pocket_d=w.get("pocket", 3.0),
              weight_dy=w.get("dy", 0.0), emblem=w.get("emblem"), engrave_text=w.get("text"), plate_window=w.get("window", (0, 0)))
    import v4 as _v4
    old = (_v4.DCX, _v4.DCY, _v4.H4_FRONT)
    _v4.DCX, _v4.DCY, _v4.H4_FRONT = bf["cx"], bf["cy"], env.h_front
    try:
        part = _v4.weight_v4(st)
    finally:
        _v4.DCX, _v4.DCY, _v4.H4_FRONT = old
    # weight_v4 applied v4's desk_to_plate (rotate -TILT about the origin, then translate (0, OY0, TOP_Z)); invert it exactly
    part = part.translate((0, -OY0, -TOP_Z)).rotate((0, 0, 0), (1, 0, 0), TILT)   # back to the desk frame
    return env.desk_to_plate(part)


def knob(env):
    z0 = env.top_z + env.deck_raise + 0.7
    return cyl_z(ENC_CX, ENC_CY, z0, z0 + 11.0, 9.0).faces(">Z").edges().chamfer(1.2)


def display_parts(env):
    st = dict(screen_frow=(env.screen == "frow"))
    dz = env.dz_screen
    c = v4.cartridge_v4(st).translate((0, 0, dz))
    if not dz:
        return c, v4.display_module_v4(st)
    # raised screen: glass + module move up, the flex still ends on the PCB
    z_cg0 = TOP_Z - CG_T + dz
    if env.screen == "frow":
        glass = rrect_prism(SF_CX, SF_CY, CG_W, CG_L, z_cg0, z_cg0 + CG_T, CG_R)
        lcm = box(SF_CX - LCM_W / 2, SF_CX + LCM_W / 2, SF_CY - LCM_L / 2, SF_CY + LCM_L / 2, z_cg0 - LCM_T, z_cg0)
        ye = SF_CY + LCM_L / 2
        fpc = (box(SF_CX - 3.5, SF_CX + 3.5, ye - 4, ye + 0.9, z_cg0 - LCM_T - 0.3, z_cg0 - LCM_T)
               .union(box(SF_CX - 3.5, SF_CX + 3.5, ye + 0.6, ye + 0.9, PCB_TOP_Z + 0.3, z_cg0 - LCM_T))
               .union(box(SF_CX - 3.5, SF_CX + 3.5, -8.0, ye + 0.9, PCB_TOP_Z + 1.0, PCB_TOP_Z + 1.3)))
    else:
        glass = rrect_prism(CG_CX, ISL_CY, CG_L, CG_W, z_cg0, z_cg0 + CG_T, CG_R)
        lcm = box(LCM_X0, LCM_X0 + LCM_L, ISL_CY - LCM_W / 2, ISL_CY + LCM_W / 2, z_cg0 - LCM_T, z_cg0)
        xe = LCM_X0 + LCM_L
        fpc = (box(xe - 4, xe + 0.9, ISL_CY - 3.5, ISL_CY + 3.5, z_cg0 - LCM_T - 0.3, z_cg0 - LCM_T)
               .union(box(xe + 0.6, xe + 0.9, ISL_CY - 3.5, ISL_CY + 3.5, PCB_TOP_Z + 0.3, z_cg0 - LCM_T))
               .union(box(308.2, xe + 0.9, ISL_CY - 3.5, ISL_CY + 3.5, PCB_TOP_Z + 1.0, PCB_TOP_Z + 1.3)))
    return c, glass.union(lcm).union(fpc)


def plate(env, keys):
    return v4.plate_v4(dict(screen_frow=(env.screen == "frow")), keys)


def gaskets(env):
    return v4.gaskets_v4(dict(screen_frow=(env.screen == "frow")))
