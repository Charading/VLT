"""VLT case v4 — sculpted CNC case with Shego75-style per-group windows, styled variants.

Builds on the v3 model (hardware/VLT/case_v3): same frames, plate, cartridge, display, daughterboards.
What changes here: the top case has one window per key group (bars of metal between the F-row groups, the main block,
the nav column, the arrow cluster and the screen), the seam sits low (z = -6), the plate assembly hangs in the top
case (gasket pockets in the top case, gasket ledges rising from the bottom case), and the outer skin is sculpted per
STYLE: oblique facets on the walls, light lines, engraved weights.

    cadenv/Scripts/python.exe build_v4.py [ore|blade|all] [--quick]
"""
import os, sys, math
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "case_v3"))
import cadquery as cq
from params import *
import geom, parts
from geom import box, rrect_prism, cyl_z, cyl_y, cyl_x, sphere, desk_to_plate, desk_box, slab, weight_outline

W_CLR = 0.57                 # window clearance per side (Shego75 value)
WIN_R = 1.2                  # window corner radius
SEAM4 = -6.0                 # seam below the plate top
FLOOR4 = 3.5
BC4_Z = -8.5                 # plunger axis
BC4_TAB_Z0 = -10.5
USB4_PORT_Z = -8.5
USB4_BOARD_TOP = -9.6
H4_FRONT = 21.5

STYLES = {
    "ore": dict(
        name="Ore", top_chamfer=2.5,
        side_facet=dict(h_front=6.0, h_back=22.0, angle=16.0),     # crease rises front→back, lower band leans in 16°
        front_facet=dict(h=6.0, angle=12.0), back_facet=dict(h=22.0, angle=16.0),   # the crease runs all the way round
        crease_light=True,                                         # 2 mm frosted line 2.5 below the crease, both sides
        weight="pinwheel", weight_size=(220.0, 62.0, 4.0, 14.0), badge=True,
        underglow="front_strip",                                    # slot along the bottom front edge
        bumpon_in=22.0),
    "envy": dict(
        name="Envy", top_chamfer=1.2,
        side_facet=dict(h_front=7.0, h_back=7.0, angle=14.0),      # gentle band all round, sharp top edge
        front_facet=dict(h=7.0, angle=14.0), back_facet=dict(h=7.0, angle=14.0),
        crease_light=False,
        weight="plate", weight_size=(262.0, 100.0, 3.0, 10.0), pocket_d=2.0, badge=False,
        plate_window=(120.0, 40.0), engrave_text="VLT",            # window in the plate shows a mesh engraved in the floor
        underglow="ring", ring_in=10.5,
        bumpon_in=20.0),
    # ---- round 2: five more, bigger light areas everywhere ----
    "syrin": dict(
        name="Syrin", top_chamfer=2.0,
        side_facet=dict(h_front=8.0, h_back=8.0, angle=10.0), front_facet=dict(h=8.0, angle=10.0), back_facet=None,
        weight="bar_wide", weight_size=(300.0, 40.0, 3.0, 6.0), pocket_d=2.0, weight_dy=+26.0, emblem="star", engrave_text="VLT",
        diag_slots=dict(n=9, pitch=11.0, length=22.0, width=3.5, angle=52.0, cx=-60.0, cy=-26.0),   # "///" strip, front half
        usb_ribs=True, underglow="front_strip", bar_chan_w=4.5, bar_slot_w=3.0, bumpon_in=20.0, badge=False),
    "velota": dict(
        name="Velota", top_chamfer=1.5,
        side_facet=None, front_facet=None, back_facet=None,
        corner_cut=14.0,                                           # front bottom corners cut 45°, frosted panels behind
        back_window=dict(h=5.0, z=-15.0),                          # two wide light windows in the back wall
        weight="bar", weight_size=(220.0, 60.0, 4.0, 12.0), underglow="ring", ring_in=10.5,
        bar_chan_w=4.5, bar_slot_w=3.0, bumpon_in=20.0, badge=False),
    "icev": dict(
        name="Ice V", top_chamfer=2.5,
        side_facet=None, front_facet=dict(h=5.0, angle=10.0), back_facet=None,
        weight=None, bottom_panel=(262.0, 92.0), v_light=True, badge="pyramid",
        underglow="panel", bar_chan_w=5.0, bar_slot_w=3.0, bumpon_in=20.0),
    "deck": dict(
        name="Deck", top_chamfer=1.5,
        side_facet=dict(h_front=5.0, h_back=5.0, angle=12.0), front_facet=dict(h=5.0, angle=12.0), back_facet=dict(h=5.0, angle=12.0),
        deck_raise=2.0,                                            # F-row tier 2 mm higher, 300 mm light line in the step
        weight="plate", weight_size=(240.0, 80.0, 3.0, 12.0), pocket_d=2.0, plate_window=(0, 0), engrave_text="VLT",
        underglow="ring", ring_in=10.5, bar_chan_w=4.5, bar_slot_w=3.0, bumpon_in=20.0, badge=False),
    "brassbar": dict(
        name="Brass bar", top_chamfer=2.0,
        side_facet=dict(h_front=7.0, h_back=18.0, angle=14.0), front_facet=None, back_facet=dict(h=18.0, angle=14.0),
        front_bar=dict(h=6.0, t=5.0, margin=14.0),                 # brass bar along the whole front bottom edge
        front_light=True, front_light_z=10.5,                      # light line in the front wall above the bar
        weight="bar", weight_size=(200.0, 56.0, 4.0, 12.0), underglow="ring", ring_in=10.5,
        bar_chan_w=4.5, bar_slot_w=3.0, bumpon_in=20.0, badge=False),
    # ---- layout variant: screen in the F-row left of the knob, Del moves under the knob (4-key nav column) ----
    "syrin_sf": dict(
        name="Syrin, screen in F-row", top_chamfer=2.0, screen_frow=True,
        side_facet=dict(h_front=8.0, h_back=8.0, angle=10.0), front_facet=dict(h=8.0, angle=10.0), back_facet=None,
        weight="bar_wide", weight_size=(300.0, 40.0, 3.0, 6.0), pocket_d=2.0, weight_dy=+26.0, emblem="star", engrave_text="VLT",
        diag_slots=dict(n=9, pitch=11.0, length=22.0, width=3.5, angle=52.0, cx=-60.0, cy=-26.0),
        usb_ribs=True, underglow="front_strip", bar_chan_w=4.5, bar_slot_w=3.0, bumpon_in=20.0, badge=False),
    "blade": dict(
        name="Blade", top_chamfer=2.5,
        side_facet=dict(h_front=9.0, h_back=9.0, angle=18.0),      # uniform band around the base
        front_facet=dict(h=9.0, angle=18.0), back_facet=dict(h=9.0, angle=18.0),
        crease_light=False, front_light=True,                      # light line through the front band
        weight="bar", weight_size=(200.0, 56.0, 4.0, 12.0), badge=False,
        underglow="ring", ring_in=13.5,
        bumpon_in=24.0),
}


# ---------------------------------------------------------------- layout variant: screen in the F-row
# Glass is unrotated here (17.58 wide × 20.82 tall module, flex leaving towards the back wall), centred between the
# F12 window and the knob.  The back bezel gets the cartridge notch; the 4th gasket tab moves left to clear it.
SF_X0 = 13.75 * U + W_CLR                 # right edge of the F9-F12 window (262.5)
SF_X1 = ENC_CX - KNOB_D / 2               # knob edge (295.8)
SF_CX = (SF_X0 + SF_X1) / 2               # 279.15
SF_CY = -(U + CAP_G + 0.8) + CG_L / 2     # glass from 0.8 above the number-row caps up into the back bezel (-10.7)
SF_TABS = [40.0, 135.0, 200.0, 250.0]
SF_NOTCH_Y1 = CLR + 5.6
SF_SCREW_Y = CLR + 3.4


def layout_keys(keys, st):
    """apply the style's layout change: drop the F-row Del, add Del under the knob at (16u, 4.75u)"""
    if not st.get("screen_frow"):
        return keys
    out = [k for k in keys if not (k[3] == "Del" and -k[1] / U < 1.0)]
    out.append((16.0 * U, -4.75 * U, 1.0, "Del"))
    return out


def tabs_for(st):
    return SF_TABS if st.get("screen_frow") else PLATE_TAB_X


# ---------------------------------------------------------------- key groups → windows
def key_groups(keys):
    """split the layout into the Shego75 window groups; each is a list of (cx, cy, w)"""
    g = {"esc": [], "f1": [], "f2": [], "f3": [], "del": [], "main": [], "nav": [], "arrows": []}
    for cx, cy, w, l in keys:
        if l == "ENC":
            continue
        ux, uy = cx / U, -cy / U            # key-unit centre (KLE y down)
        if uy < 1.0:                        # F-row
            if ux < 1.1: g["esc"].append((cx, cy, w))
            elif ux < 5.3: g["f1"].append((cx, cy, w))
            elif ux < 9.6: g["f2"].append((cx, cy, w))
            elif ux < 13.9: g["f3"].append((cx, cy, w))
            else: g["del"].append((cx, cy, w))
        elif ux > 15.4:                     # nav column
            g["nav"].append((cx, cy, w))
        elif uy > 4.4 and ux > 13.2 and w == 1.0 and (uy > 5.4 or ux > 14.0):
            g["arrows"].append((cx, cy, w))  # ↑ ← ↓ →
        else:
            g["main"].append((cx, cy, w))
    return g


def window_solid(cells, z0=-1.0, z1=TOP_Z + 1, clr=W_CLR):
    s = None
    for cx, cy, w in cells:
        b = box(cx - w * U / 2 - clr, cx + w * U / 2 + clr, cy - U / 2 - clr, cy + U / 2 + clr, z0, z1)
        s = b if s is None else s.union(b)
    try:
        s = s.edges("|Z").fillet(WIN_R)
    except Exception:
        pass
    return s


# ---------------------------------------------------------------- oblique facets on the outer skin
def desk_z(y):
    """z of the desk plane in the plate frame at plate-frame y (the front outer edge is at y = OY0)"""
    return TOP_Z - H4_FRONT / math.cos(TILT_R) - (y - OY0) * math.tan(TILT_R)


def _rotate_about(wp, p0, p1, ang):
    return wp.rotate(p0, p1, ang)


def facet(shell, side, h_a, h_b, angle):
    """cut an oblique facet below a crease line on one wall.  side: left/right (h_a = front height, h_b = back height)
    or front/back (h_a = h_b = height above the desk).  Heights are measured above the desk at the wall."""
    big = 600
    if side in ("left", "right"):
        x = OX0 if side == "left" else OX1
        p0 = (x, OY0, desk_z(OY0) + h_a / math.cos(TILT_R))
        p1 = (x, OY1, desk_z(OY1) + h_b / math.cos(TILT_R))
        hs = box(x - big, x, OY0 - big, OY1 + big, -big, big) if side == "left" else box(x, x + big, OY0 - big, OY1 + big, -big, big)
    else:
        y = OY0 if side == "front" else OY1
        zc = desk_z(y) + h_a / math.cos(TILT_R)
        p0 = (OX0 - big, y, zc); p1 = (OX1 + big, y, zc)
        hs = box(OX0 - big, OX1 + big, y - big, y, -big, big) if side == "front" else box(OX0 - big, OX1 + big, y, y + big, -big, big)
    # pick the rotation sign that moves the half-space INTO the body below the crease
    probe = cq.Workplane("XY").box(0.5, 0.5, 0.5).translate(((p0[0] + p1[0]) / 2 + (0 if side in ("left", "right") else 0),
                                                              (p0[1] + p1[1]) / 2, (p0[2] + p1[2]) / 2 - 10))
    for sgn in (1, -1):
        test = _rotate_about(hs, p0, p1, sgn * angle)
        if test.intersect(probe).val().Volume() > 0.01:
            return shell.cut(test)
    raise RuntimeError("facet sign")


def crease_line_points(side, st):
    f = st["side_facet"]
    x = OX0 if side == "left" else OX1
    return ((x, OY0, desk_z(OY0) + f["h_front"] / math.cos(TILT_R)), (x, OY1, desk_z(OY1) + f["h_back"] / math.cos(TILT_R)))


def bar_along(p0, p1, w_x, h_z, x_len=None):
    """a box running from p0 to p1 (same x), w_x wide in x (centred), h_z tall perpendicular to the run, in the y-z plane"""
    dy, dz = p1[1] - p0[1], p1[2] - p0[2]
    L = math.hypot(dy, dz)
    ang = math.degrees(math.atan2(dz, dy))
    b = box(-w_x / 2, w_x / 2, 0, L, -h_z / 2, h_z / 2).rotate((0, 0, 0), (1, 0, 0), ang).translate(p0)
    return b


def outer_shell_v4(st):
    s = geom.outer_shell()
    if st.get("side_facet"):
        f = st["side_facet"]
        s = facet(s, "left", f["h_front"], f["h_back"], f["angle"])
        s = facet(s, "right", f["h_front"], f["h_back"], f["angle"])
    if st.get("front_facet"):
        f = st["front_facet"]; s = facet(s, "front", f["h"], f["h"], f["angle"])
    if st.get("back_facet"):
        f = st["back_facet"]; s = facet(s, "back", f["h"], f["h"], f["angle"])
    return s


# ---------------------------------------------------------------- top case
Y_STEP = -(U + W_CLR + 3.62)      # front face of the bar between the F-row and the number row (-23.24)
DECK_TOP = TOP_Z                  # patched per style when the F-row tier is raised


def top_case_v4(st, keys):
    shell = outer_shell_v4(st)
    raise_ = st.get("deck_raise", 0.0)
    tc = shell.intersect(slab(SEAM4, TOP_Z + raise_))
    if raise_:
        tc = tc.cut(box(OX0 - 1, OX1 + 1, OY0 - 1, Y_STEP, TOP_Z, TOP_Z + raise_ + 1))     # lower deck in front of the step
        tc = tc.faces(">Z").edges().chamfer(st["top_chamfer"])                             # raised tier incl. the step edge
        try:
            tc = tc.edges(cq.selectors.BoxSelector((OX0 - 1, OY0 - 1, TOP_Z - 0.1), (OX1 + 1, Y_STEP - 0.5, TOP_Z + 0.1))).chamfer(1.0)
        except Exception as e:
            print("  lower deck chamfer skipped:", e)
        # light line in the riser: 1.3 tall channel 1.5 deep, fed by a vertical slot through the bar from the plate
        tc = tc.cut(box(-4.0, KEYS_W + 4.0, Y_STEP - 0.01, Y_STEP + 1.5, TOP_Z + 0.35, TOP_Z + raise_ - 0.35))
        tc = tc.cut(box(2.0, KEYS_W - 2.0, Y_STEP + 0.6, Y_STEP + 2.4, 0.2, TOP_Z + raise_ - 0.35))
    else:
        tc = tc.faces(">Z").edges().chamfer(st["top_chamfer"])
    for name, cells in key_groups(keys).items():
        if cells:
            tc = tc.cut(window_solid(cells, z1=TOP_Z + raise_ + 1))
    tc = tc.cut(box(-CLR, KEYS_W + CLR, -(KEYS_H + CLR), CLR, SEAM4 - 0.01, 0.3))          # plate relief
    tc = tc.cut(cyl_z(ENC_CX, ENC_CY, -1, TOP_Z + raise_ + 1, 4.75))                        # encoder shaft
    # light bar channels + slots in the 0.5u bar
    bcw, bsw = st.get("bar_chan_w", BAR_CHAN_W), st.get("bar_slot_w", BAR_SLOT_W)
    for ya, yb in BAR_SEGMENTS:
        ztop = TOP_Z + (raise_ if ya > Y_STEP else 0.0)
        tc = tc.cut(box(BAR_CX - bcw / 2, BAR_CX + bcw / 2, yb, ya, ztop - BAR_CHAN_D, ztop + 1))
        ya2, yb2 = min(ya, -1.5), yb + 1.0
        if ya2 > yb2:
            tc = tc.cut(box(BAR_CX - bsw / 2, BAR_CX + bsw / 2, yb2, ya2, -1, ztop - BAR_CHAN_D + 0.01))
    if st.get("seam_groove"):
        d, h = st["seam_groove"]
        tc = tc.cut(perimeter_ring(SEAM4, SEAM4 + h, d))
    if st.get("screen_frow"):
        # display in the F-row: relief under the block, glass opening, notch in the back wall, M2 holes in its ceiling
        tc = tc.cut(box(SF_X0 + 0.5, SF_X1 + 0.5, -(U + 3.5), CLR + 0.01, 0.2, ISL_Z0))
        tc = tc.cut(rrect_prism(SF_CX, SF_CY, CG_W + 2 * CG_GAP, CG_L + 2 * CG_GAP, ISL_Z0 - 1, TOP_Z + raise_ + 1, CG_R + CG_GAP))
        tc = tc.cut(box(SF_CX - CART_NOTCH_W / 2, SF_CX + CART_NOTCH_W / 2, CLR - 0.01, SF_NOTCH_Y1, SEAM4 - 1, ISL_Z0))
        for dx in (-CART_SCREW_DY, CART_SCREW_DY):
            tc = tc.cut(cyl_z(SF_CX + dx, SF_SCREW_Y, ISL_Z0 - 0.5, ISL_Z0 + 3.5, BOSS_TAP / 2))
    else:
        # display island: relief under it for the cartridge flange, glass opening, wall notch, M2 holes
        tc = tc.cut(box(ISL_X0 - 0.5, KEYS_W + CLR + 0.01, ISL_Y0 - 0.5, ISL_Y1 + 0.5, 0.2, ISL_Z0))
        tc = tc.cut(rrect_prism(CG_CX, ISL_CY, CG_L + 2 * CG_GAP, CG_W + 2 * CG_GAP, ISL_Z0 - 1, TOP_Z + 1, CG_R + CG_GAP))
        tc = tc.cut(box(KEYS_W + CLR - 0.01, CART_NOTCH_X1, ISL_CY - CART_NOTCH_W / 2, ISL_CY + CART_NOTCH_W / 2, SEAM4 - 1, ISL_Z0))
        for dy in (-CART_SCREW_DY, CART_SCREW_DY):
            tc = tc.cut(cyl_z(CART_SCREW_X, ISL_CY + dy, ISL_Z0 - 0.5, ISL_Z0 + 3.5, BOSS_TAP / 2))
    # gasket pockets, open to the seam: ledge from the bottom case + bottom gasket + tab + top gasket
    back, front = geom.tab_pocket_ranges()
    for xt in tabs_for(st):
        for y0, y1 in (back, front):
            tc = tc.cut(box(xt - PLATE_TAB_W / 2 - POCKET_X_CLR, xt + PLATE_TAB_W / 2 + POCKET_X_CLR, y0, y1, SEAM4 - 1, GASKET_T - 0.5))
    # ball-catch skirt tabs
    for xc in BC_BACK_X:
        tc = tc.union(box(xc - BC_TAB_W / 2, xc + BC_TAB_W / 2, CLR - 0.1 - BC_TAB_T, CLR - 0.1, BC4_TAB_Z0, SEAM4 + 0.01))
        tc = tc.cut(sphere(xc, CLR - 0.1 + 0.5, BC4_Z, BC_DIMPLE_R))
    for xc in BC_FRONT_X:
        yf = -(KEYS_H + CLR) + 0.1
        tc = tc.union(box(xc - BC_TAB_W / 2, xc + BC_TAB_W / 2, yf, yf + BC_TAB_T, BC4_TAB_Z0, SEAM4 + 0.01))
        tc = tc.cut(sphere(xc, yf - 0.5, BC4_Z, BC_DIMPLE_R))
    xl = -CLR + 0.1
    tc = tc.union(box(xl, xl + BC_TAB_T, BC_LEFT_Y - BC_TAB_W / 2, BC_LEFT_Y + BC_TAB_W / 2, BC4_TAB_Z0, SEAM4 + 0.01))
    tc = tc.cut(sphere(xl - 0.5, BC_LEFT_Y, BC4_Z, BC_DIMPLE_R))
    xr = KEYS_W + CLR - 0.1
    tc = tc.union(box(xr - BC_TAB_T, xr, BC_RIGHT_Y - BC_TAB_W / 2, BC_RIGHT_Y + BC_TAB_W / 2, BC4_TAB_Z0, SEAM4 + 0.01))
    tc = tc.cut(sphere(xr + 0.5, BC_RIGHT_Y, BC4_Z, BC_DIMPLE_R))
    # crease light line (Ore): a 2 mm slot 2.5 below the crease, horizontal through the wall, both sides, in the top case part
    if st.get("crease_light"):
        for side in ("left", "right"):
            tc = tc.cut(crease_slot(side, st, SEAM4 + 0.5, TOP_Z - 2.0))
    return tc


def crease_slot(side, st, zmin, zmax, w=2.0, below=2.5, inset_margin=30.0):
    p0, p1 = crease_line_points(side, st)
    p0 = (p0[0], p0[1] + inset_margin, p0[2] - below)
    p1 = (p1[0], p1[1] - inset_margin, p1[2] - below)
    x = p0[0]
    depth = BEZEL + 2.0
    b = bar_along((0, p0[1], p0[2]), (0, p1[1], p1[2]), 2 * depth, w)
    b = b.translate((x, 0, 0))
    return b.intersect(box(OX0 - 50, OX1 + 50, OY0 - 50, OY1 + 50, zmin, zmax))


# ---------------------------------------------------------------- bottom case
def bottom_case_v4(st):
    shell = outer_shell_v4(st)
    bc = shell.intersect(slab(-80, SEAM4))
    floor_zd = -H4_FRONT + FLOOR4
    cav = box(-CLR, KEYS_W + CLR, -(KEYS_H + CLR), CLR, -80, SEAM4 + 1).intersect(desk_box(-100, W + 100, -100, D + 100, floor_zd, 80))
    bc = bc.cut(cav)
    # gasket ledges rising into the top-case pockets
    back, front = geom.tab_pocket_ranges()
    for xt in tabs_for(st):
        for y0, y1 in (back, front):
            yy0, yy1 = (y0 + 0.3, y1 - 0.3) if y0 > 0 else (y0 + 0.3, y1 - 0.3)
            bc = bc.union(box(xt - PLATE_TAB_W / 2, xt + PLATE_TAB_W / 2, yy0, yy1, SEAM4 - 0.01, -3.0))
    # bosses
    boss_tops = [(USB_CX + dx, USB_SCREW_Y, USB4_BOARD_TOP - BOARD_T) for dx in (-USB_SCREW_DX, USB_SCREW_DX)]
    boss_tops += [(POGO_CX + sx, POGO_CY + sy, POGO_BOARD_TOP_Z - BOARD_T) for sx, sy in
                  ((-POGO_SCREW[0], -POGO_SCREW[1]), (POGO_SCREW[0], -POGO_SCREW[1]), (-POGO_SCREW[0], POGO_SCREW[1]), (POGO_SCREW[0], POGO_SCREW[1]))]
    bosses = None
    for bx, by, bz in boss_tops:
        c = cyl_z(bx, by, -80, bz, BOSS_D / 2); bosses = c if bosses is None else bosses.union(c)
    bc = bc.union(bosses).intersect(shell)
    for bx, by, bz in boss_tops:
        bc = bc.cut(cyl_z(bx, by, bz - 5.0, bz + 0.1, BOSS_TAP / 2))
    # USB-C
    plug = rrect_prism(USB_CX, 0, USB_PLUG_W, USB_PLUG_H, 0, 14, USB_PLUG_R).rotate((0, 0, 0), (1, 0, 0), -90)
    bc = bc.cut(plug.translate((0, CLR - 1, USB4_PORT_Z)))
    bc = bc.cut(box(USB_CX - 13.5, USB_CX + 13.5, CLR - 0.01, USB_BOARD_Y1, USB4_BOARD_TOP - BOARD_T - 0.3, SEAM4 + 0.01))
    # plunger holes
    for xc in BC_BACK_X:
        bc = bc.cut(cyl_y(xc, BC4_Z, CLR - 0.5, CLR + BC_DEPTH, BC_TAP / 2))
    for xc in BC_FRONT_X:
        bc = bc.cut(cyl_y(xc, BC4_Z, -(KEYS_H + CLR) - BC_DEPTH, -(KEYS_H + CLR) + 0.5, BC_TAP / 2))
    bc = bc.cut(cyl_x(BC_LEFT_Y, BC4_Z, -CLR - BC_DEPTH, -CLR + 0.5, BC_TAP / 2))
    bc = bc.cut(cyl_x(BC_RIGHT_Y, BC4_Z, KEYS_W + CLR - 0.5, KEYS_W + CLR + BC_DEPTH, BC_TAP / 2))
    # crease light (lower part of the slot lives in the bottom case where the seam crosses it)
    if st.get("crease_light"):
        for side in ("left", "right"):
            bc = bc.cut(crease_slot(side, st, -60, SEAM4 - 0.5))
    # ---- wall features of round 2 ----
    if st.get("corner_cut"):
        cw = st["corner_cut"]
        for x in (OX0, OX1):
            bc = bc.cut(corner_diamond(x, OY0, cw, -80, SEAM4 + 0.01))
            bc = bc.cut(corner_diamond(x, OY0, cw + 2.0 * math.sqrt(2), -80, SEAM4 + 0.01).intersect(
                box(OX0 - 1, OX1 + 1, OY0 - 1, OY1, desk_z(OY0) + 2.5, SEAM4 - 1.5)))   # 2 mm recess for the frosted panel
    if st.get("back_window"):
        h, z = st["back_window"]["h"], st["back_window"]["z"]
        for x0, x1 in back_window_spans():
            bc = bc.cut(box(x0, x1, CLR - 1, OY1 + 1, z - h / 2, z + h / 2))
    if st.get("usb_ribs"):
        for i in range(-6, 7):
            if abs(i) < 3:
                continue
            xr = USB_CX + i * 2.2
            bc = bc.cut(box(xr - 0.5, xr + 0.5, OY1 - 0.6, OY1 + 1, USB4_PORT_Z - 5.0, USB4_PORT_Z + 5.0))
    if st.get("front_bar"):
        fb = st["front_bar"]
        bc = bc.cut(desk_to_plate(box(OX0 + fb["margin"], OX1 - fb["margin"], YD0 - 5, YD0 + fb["t"], -H4_FRONT - 1, -H4_FRONT + fb["h"])))
    if st.get("front_light"):
        zc = desk_z(OY0) + st.get("front_light_z", 5.0) / math.cos(TILT_R)
        bc = bc.cut(box(DCX - 110, DCX + 110, OY0 - 20, -(KEYS_H + CLR) + 1.0, zc - 1.25, zc + 1.25))
    # ---- bottom face (desk frame) ----
    zb = -H4_FRONT
    cx, cy = DCX, DCY
    floor_zd = floor_zd
    if st.get("weight"):
        L, Wd, T, C = st["weight_size"]
        pd = st.get("pocket_d", WEIGHT_POCKET_D)
        wy = cy + st.get("weight_dy", 0.0)
        pocket = weight_poly(L + 2 * WEIGHT_CLR, Wd + 2 * WEIGHT_CLR, C).extrude(pd + 1).translate((cx, wy, zb - 1))
        bc = bc.cut(desk_to_plate(pocket))
        for sx, sy in weight_screws(L, Wd):
            bc = bc.cut(desk_to_plate(cyl_z(cx + sx, wy + sy, zb - 1, floor_zd + 1, 1.7)))
    if st.get("bottom_panel"):
        L, Wd = st["bottom_panel"]
        bc = bc.cut(desk_to_plate(rrect_prism(cx, cy, L + 0.4, Wd + 0.4, zb - 1, zb + 2.5, 6.0)))
        for k in (-1, 1):                                                             # two long light slots + LED channels
            yy = cy + k * Wd * 0.28
            bc = bc.cut(desk_to_plate(box(cx - L / 2 + 12, cx + L / 2 - 12, yy - 1.75, yy + 1.75, zb - 1, zb + FLOOR4 + 1)))
            bc = bc.cut(desk_to_plate(box(cx - L / 2 + 10, cx + L / 2 - 10, yy - 2.6, yy + 2.6, floor_zd - 0.01, floor_zd + LED_CHAN_D)))
        if st.get("badge") == "pyramid":
            bc = bc.cut(desk_to_plate(cq.Workplane("XY").polyline([(-11, 0), (0, -19), (11, 0), (0, 19)]).close().extrude(3).translate((cx, cy, zb + 2.5 - 2.0))))
    if st.get("v_light"):
        yv = cy + DL / 2 - 16.0
        for sgn in (-1, 1):
            arm = box(0, 62.0, -1.6, 1.6, zb - 1, zb + FLOOR4 + 1).rotate((0, 0, 0), (0, 0, 1), sgn * 28.0).translate((cx, yv - 14.0, 0))
            bc = bc.cut(desk_to_plate(arm))
    if st.get("diag_slots"):
        ds = st["diag_slots"]
        for i in range(ds["n"]):
            sx = cx + ds["cx"] + (i - (ds["n"] - 1) / 2) * ds["pitch"]
            s = box(-ds["width"] / 2, ds["width"] / 2, -ds["length"] / 2, ds["length"] / 2, zb - 1, zb + FLOOR4 + 1).rotate((0, 0, 0), (0, 0, 1), ds["angle"])
            bc = bc.cut(desk_to_plate(s.translate((sx, cy + ds["cy"], 0))))
        bc = bc.cut(desk_to_plate(box(cx + ds["cx"] - ds["n"] * ds["pitch"] / 2 - 8, cx + ds["cx"] + ds["n"] * ds["pitch"] / 2 + 8,
                                      cy + ds["cy"] - 9, cy + ds["cy"] + 9, floor_zd - 0.01, floor_zd + LED_CHAN_D)))
    if st.get("plate_window") and st["plate_window"][0] > 0:
        # mesh engraved into the pocket floor, visible through the plate's window; a smooth wave band is left plain
        ww, wh = st["plate_window"]
        zf = zb + pd                       # pocket floor
        pitch, r, depth = 5.0, 2.0, 0.4
        nx, ny = int(ww / pitch) + 2, int(wh / (pitch * 0.866)) + 2
        for j in range(-ny, ny + 1):
            for i in range(-nx, nx + 1):
                hx = i * pitch + (pitch / 2 if j % 2 else 0)
                hy = j * pitch * 0.866
                if abs(hx) > ww / 2 - 3 or abs(hy) > wh / 2 - 3:
                    continue
                if abs(hy - 9.0 * math.sin(2 * math.pi * hx / 70.0)) < 5.5:
                    continue
                hexa = cq.Workplane("XY").polygon(6, 2 * r).extrude(depth + 1).translate((cx + hx, cy + hy, zf - 1))
                bc = bc.cut(desk_to_plate(hexa))
    bi = st["bumpon_in"]
    for bx in (OX0 + bi, OX1 - bi):
        for by in (YD0 + bi, YD1 - bi):
            bc = bc.cut(desk_to_plate(cyl_z(bx, by, zb - 1, zb + BUMPON_DEPTH, BUMPON_D / 2)))
    if st["underglow"] == "ring":
        ri = st["ring_in"]
        ring_out = rrect_prism(cx, cy, W - 2 * (ri - RING_W / 2), DL - 2 * (ri - RING_W / 2), zb - 1, zb + RING_D, 4.0)
        ring_in = rrect_prism(cx, cy, W - 2 * (ri + RING_W / 2), DL - 2 * (ri + RING_W / 2), zb - 2, zb + RING_D + 1, 1.0)
        bc = bc.cut(desk_to_plate(ring_out.cut(ring_in)))
        for feat in ring_slots_v4(ri, zb, zb + FLOOR4 + 1, RING_SLOT_W) + ring_slots_v4(ri, floor_zd - 0.01, floor_zd + LED_CHAN_D, LED_CHAN_W):
            bc = bc.cut(desk_to_plate(feat))
    elif st["underglow"] == "front_strip":
        # a 3 wide frosted strip 6 mm in from the front bottom edge, 220 long, slot through the floor, LED channel inside
        y0 = YD0 + 6.0
        bc = bc.cut(desk_to_plate(box(cx - 110, cx + 110, y0 - 1.5, y0 + 1.5, zb - 1, zb + RING_D)))
        bc = bc.cut(desk_to_plate(box(cx - 100, cx + 100, y0 - 1.0, y0 + 1.0, zb - 1, zb + FLOOR4 + 1)))
        bc = bc.cut(desk_to_plate(box(cx - 101, cx + 101, y0 - 2.5, y0 + 2.5, floor_zd - 0.01, floor_zd + LED_CHAN_D)))
    if st.get("front_light"):
        # light line through the front band: 2.5 tall slot at desk+5, 180 long, into the cavity
        zc = desk_z(OY0) + 5.0 / math.cos(TILT_R)
        bc = bc.cut(box(cx - 90, cx + 90, OY0 - 20, -(KEYS_H + CLR) + 1.0, zc - 1.25, zc + 1.25))
    return bc


def ring_slots_v4(ri, z0, z1, w):
    s = RING_CORNER_STOP
    return [box(OX0 + s, OX1 - s, YD0 + ri - w / 2, YD0 + ri + w / 2, z0, z1),
            box(OX0 + s, OX1 - s, YD1 - ri - w / 2, YD1 - ri + w / 2, z0, z1),
            box(OX0 + ri - w / 2, OX0 + ri + w / 2, YD0 + s, YD1 - s, z0, z1),
            box(OX1 - ri - w / 2, OX1 - ri + w / 2, YD0 + s, YD1 - s, z0, z1)]


# ---------------------------------------------------------------- weights
def weight_poly(L, Wd, c):
    hl, hw = L / 2, Wd / 2
    pts = [(-hl + c, -hw), (hl - c, -hw), (hl, -hw + c), (hl, hw - c), (hl - c, hw), (-hl + c, hw), (-hl, hw - c), (-hl, -hw + c)]
    return cq.Workplane("XY").polyline(pts).close()


def weight_screws(L, Wd):
    return [(-L * 0.4, -Wd * 0.32), (L * 0.4, -Wd * 0.32), (-L * 0.4, Wd * 0.32), (L * 0.4, Wd * 0.32)]


def weight_v4(st):
    if not st.get("weight"):
        return None
    L, Wd, T, C = st["weight_size"]
    pd = st.get("pocket_d", WEIGHT_POCKET_D)
    zb = -H4_FRONT
    w = weight_poly(L, Wd, C).extrude(T).translate((0, 0, zb - (T - pd)))
    w = w.faces("<Z").edges().chamfer(0.8)
    for sx, sy in weight_screws(L, Wd):
        w = w.cut(cyl_z(sx, sy, zb + pd - min(3.2, T - 0.8), zb + pd + 1, 1.25))
    zface = zb - (T - pd)                        # visible (bottom) face
    if st["weight"] == "bar_wide":
        if st.get("emblem") == "star":
            pts = []
            for i in range(16):
                r = 15.0 if i % 2 == 0 else 6.5
                a = math.pi / 8 * i
                pts.append((r * math.cos(a), r * math.sin(a)))
            w = w.cut(cq.Workplane("XY").polyline(pts).close().extrude(1.0).translate((0, 0, zface - 0.6)))
            w = w.cut(cyl_z(0, 0, zface - 1, zface + 0.4, 17.5).cut(cyl_z(0, 0, zface - 2, zface + 1, 16.5)))
        if st.get("engrave_text"):
            try:
                txt = cq.Workplane("XY").text(st["engrave_text"], 8.0, -0.3, kind="bold").mirror("XZ").translate((L / 2 - 30, 0, zface + 0.3))
                w = w.cut(txt)
            except Exception as e:
                print("  text engraving skipped:", e)
    if st["weight"] == "plate":
        ww, wh = st["plate_window"]
        if ww > 0:
            w = w.cut(rrect_prism(0, 0, ww, wh, zface - 1, zface + T + 1, 4.0))
        else:
            wh = -20.0
        if st.get("engrave_text"):
            try:
                # mirrored in y so it reads correctly when the board is turned over; sits 16 mm below the window
                txt = cq.Workplane("XY").text(st["engrave_text"], 9.0, -0.3, kind="bold").mirror("XZ").translate((0, -wh / 2 - 16, zface + 0.3))
                w = w.cut(txt)
            except Exception as e:
                print("  text engraving skipped:", e)
    if st["weight"] == "pinwheel":
        # vortex engraving: N grooves, each leaving a ring around the badge at a tangent-ish angle, 0.3 deep
        N, r0, gw, gd = 36, 16.0, 0.5, 0.3
        for i in range(N):
            a = 2 * math.pi * i / N
            px, py = r0 * math.cos(a), r0 * math.sin(a)
            d = a + math.radians(62)
            g = box(0, L, -gw / 2, gw / 2, zface - 1, zface + gd).rotate((0, 0, 0), (0, 0, 1), math.degrees(d)).translate((px, py, 0))
            w = w.cut(g.intersect(weight_poly(L - 6, Wd - 6, C).extrude(10).translate((0, 0, zface - 2))))
        # diamond badge pocket (badge is a separate polished part, 1.0 proud)
        w = w.cut(cq.Workplane("XY").polyline([(-9, 0), (0, -16), (9, 0), (0, 16)]).close().extrude(3).translate((0, 0, zface - 1)))
    return desk_to_plate(w.translate((DCX, DCY + st.get("weight_dy", 0.0), 0)))


def badge_v4(st):
    if not st.get("badge"):
        return None
    zb = -H4_FRONT
    if st.get("badge") == "pyramid":
        # brass pyramid in the centre of the frosted bottom panel, 1.5 proud of the panel face
        zf = zb + 0.5
        b = cq.Workplane("XY").polyline([(-10.8, 0), (0, -18.8), (10.8, 0), (0, 18.8)]).close().extrude(2.0).translate((0, 0, zf - 0.0))
        pyr = (cq.Workplane("XY").polyline([(-10.8, 0), (0, -18.8), (10.8, 0), (0, 18.8)]).close()
               .workplane(offset=-2.5).polyline([(-1.5, 0), (0, -2.6), (1.5, 0), (0, 2.6)]).close().loft())
        b = b.union(pyr.translate((0, 0, zf)))
        return desk_to_plate(b.translate((DCX, DCY, 0)))
    L, Wd, T, C = st["weight_size"]
    zface = zb - (T - st.get("pocket_d", WEIGHT_POCKET_D))
    b = cq.Workplane("XY").polyline([(-8.8, 0), (0, -15.8), (8.8, 0), (0, 15.8)]).close().extrude(3.0).translate((0, 0, zface - 1.0))
    # faceted top: a shallow pyramid
    pyr = cq.Workplane("XY").polyline([(-8.8, 0), (0, -15.8), (8.8, 0), (0, 15.8)]).close().workplane(offset=-1.2).polyline([(-2, 0), (0, -3.6), (2, 0), (0, 3.6)]).close().loft()
    b = b.union(pyr.translate((0, 0, zface - 1.0)))
    return desk_to_plate(b.translate((DCX, DCY, 0)))


# ---------------------------------------------------------------- Cherry-profile keycaps for the renders
CHERRY_H = {0: 9.3, 1: 9.3, 2: 8.1, 3: 7.3, 4: 7.3, 5: 8.1}


def keycaps_cherry(keys):
    s = None
    for cx, cy, w, l in keys:
        if l == "ENC":
            continue
        uy = -cy / U
        row = 0 if uy < 1 else (1 if uy < 2.25 else (2 if uy < 3.25 else (3 if uy < 4.25 else (4 if uy < 5.4 else 5))))
        h = CHERRY_H[row]
        bw, bd = w * U - 0.85, U - 0.85
        tw, td = bw - 5.5, bd - 5.0
        cap = (cq.Workplane("XY").rect(bw, bd).workplane(offset=h).center(0, -0.6).rect(tw, td).loft()
               .translate((cx, cy, 6.3)))
        s = cap if s is None else s.union(cap)
    return s


def knob_v4(st=None):
    z0 = TOP_Z + 0.7 + (st.get("deck_raise", 0.0) if st else 0.0)
    k = cyl_z(ENC_CX, ENC_CY, z0, z0 + 11.0, 9.0).faces(">Z").edges().chamfer(1.2)
    return k


def bar_inserts_v4(st=None):
    st = st or {}
    bcw = st.get("bar_chan_w", BAR_CHAN_W)
    raise_ = st.get("deck_raise", 0.0)
    s = None
    for ya, yb in BAR_SEGMENTS:
        ztop = TOP_Z + (raise_ if ya > Y_STEP else 0.0)
        b = box(BAR_CX - bcw / 2 + 0.05, BAR_CX + bcw / 2 - 0.05, yb + 0.05, ya - 0.05, ztop - BAR_CHAN_D + 0.02, ztop)
        s = b if s is None else s.union(b)
    return s


def crease_inserts(st):
    s = None
    for side in ("left", "right"):
        b = crease_slot(side, st, -60, TOP_Z, w=1.9, inset_margin=30.2)
        x = OX0 if side == "left" else OX1
        b = b.intersect(box(x - 0.3, x + 2.2, OY0 - 50, OY1 + 50, -60, 60)) if side == "left" else b.intersect(box(x - 2.2, x + 0.3, OY0 - 50, OY1 + 50, -60, 60))
        s = b if s is None else s.union(b)
    return s


# ---------------------------------------------------------------- parts that depend on the layout variant
def plate_v4(st, keys):
    if not st.get("screen_frow"):
        return parts.plate(keys)
    import geom as g3
    old = parts.PLATE_TAB_X
    parts.PLATE_TAB_X = SF_TABS
    try:
        p = parts.plate(keys, fpc_slot=False)
    finally:
        parts.PLATE_TAB_X = old
    return p.cut(box(SF_CX - 6.0, SF_CX + 6.0, -3.0, 1.0, -5, 5))          # flex notch in the back edge


def gaskets_v4(st):
    old = parts.PLATE_TAB_X
    parts.PLATE_TAB_X = tabs_for(st)
    try:
        return parts.gaskets()
    finally:
        parts.PLATE_TAB_X = old


def cartridge_v4(st):
    if not st.get("screen_frow"):
        return parts.cartridge()
    z_ledge = ISL_Z0 + CART_BOSS_H
    bw, bl = CART_BOSS_W, CART_BOSS_L                                        # 20.78 along x, 24.02 along y
    c = rrect_prism(SF_CX, SF_CY, bw, bl, ISL_Z0, z_ledge, CG_R + CG_GAP - 0.05)
    c = c.cut(box(SF_CX - LCM_W / 2 - 0.2, SF_CX + LCM_W / 2 + 0.2, SF_CY - LCM_L / 2 - 0.25, SF_CY + LCM_L / 2 + 0.25, ISL_Z0 + CART_FLOOR_T, z_ledge + 1))
    ye = SF_CY + LCM_L / 2                                                   # flex leaves the module here (towards the back)
    c = c.cut(box(SF_CX - FPC_W / 2, SF_CX + FPC_W / 2, ye - 3.0, SF_CY + bl / 2 + 1, ISL_Z0 - 1, z_ledge + 1))
    c = c.union(box(SF_CX - CART_FLANGE_W / 2, SF_CX + CART_FLANGE_W / 2, SF_CY + 2.0, SF_NOTCH_Y1 - 0.2, ISL_Z0 - CART_FLANGE_T, ISL_Z0 + 0.01))
    c = c.cut(box(SF_CX - FPC_W / 2, SF_CX + FPC_W / 2, ye - 1.5, ye + 2.5, ISL_Z0 - CART_FLANGE_T - 1, ISL_Z0 + 0.5))
    for dx in (-CART_SCREW_DY, CART_SCREW_DY):
        c = c.cut(cyl_z(SF_CX + dx, SF_SCREW_Y, ISL_Z0 - CART_FLANGE_T - 1, ISL_Z0 + 1, 1.1))
    return c


def display_module_v4(st):
    if not st.get("screen_frow"):
        return parts.display_module()
    z_cg0 = TOP_Z - CG_T
    glass = rrect_prism(SF_CX, SF_CY, CG_W, CG_L, z_cg0, TOP_Z, CG_R)
    lcm = box(SF_CX - LCM_W / 2, SF_CX + LCM_W / 2, SF_CY - LCM_L / 2, SF_CY + LCM_L / 2, z_cg0 - LCM_T, z_cg0)
    ye = SF_CY + LCM_L / 2
    fpc = (box(SF_CX - 3.5, SF_CX + 3.5, ye - 4, ye + 0.9, z_cg0 - LCM_T - 0.3, z_cg0 - LCM_T)
           .union(box(SF_CX - 3.5, SF_CX + 3.5, ye + 0.6, ye + 0.9, PCB_TOP_Z + 0.3, z_cg0 - LCM_T))
           .union(box(SF_CX - 3.5, SF_CX + 3.5, -8.0, ye + 0.9, PCB_TOP_Z + 1.0, PCB_TOP_Z + 1.3)))
    return glass.union(lcm).union(fpc)


# ---------------------------------------------------------------- round-2 helpers and parts
def corner_diamond(x, y, leg, z0, z1):
    """square rotated 45° centred on the corner (x, y): removes a triangle with legs `leg` from the body"""
    side = leg * math.sqrt(2)
    return box(-side / 2, side / 2, -side / 2, side / 2, z0, z1).rotate((0, 0, 0), (0, 0, 1), 45).translate((x, y, 0))


def perimeter_ring(z0, z1, depth):
    outer = rrect_prism(KEYS_W / 2, (OY0 + OY1) / 2, W + 2, D + 2, z0, z1, CORNER_R + 1)
    inner = rrect_prism(KEYS_W / 2, (OY0 + OY1) / 2, W - 2 * depth, D - 2 * depth, z0 - 1, z1 + 1, max(CORNER_R - depth, 0.5))
    return outer.cut(inner)


def back_window_spans():
    return [(OX0 + 14.0, USB_CX - 20.0), (USB_CX + 20.0, OX1 - 14.0)]


def corner_inserts(st):
    """frosted PC panels, 2 mm thick, filling the recess on the cut front corners"""
    cw = st["corner_cut"]
    s = None
    for x in (OX0, OX1):
        p = corner_diamond(x, OY0, cw + 2.0 * math.sqrt(2) - 0.15, -80, SEAM4).cut(corner_diamond(x, OY0, cw + 0.1, -80, SEAM4 + 1))
        p = p.intersect(box(OX0 - 1, OX1 + 1, OY0 - 1, OY1, desk_z(OY0) + 2.6, SEAM4 - 1.6))
        p = p.intersect(geom.outer_shell())
        s = p if s is None else s.union(p)
    return s


def back_window_inserts(st):
    h, z = st["back_window"]["h"], st["back_window"]["z"]
    s = None
    for x0, x1 in back_window_spans():
        b = box(x0 + 0.1, x1 - 0.1, OY1 - 2.0, OY1 - 0.05, z - h / 2 + 0.1, z + h / 2 - 0.1)
        s = b if s is None else s.union(b)
    return s


def bottom_panel_part(st):
    L, Wd = st["bottom_panel"]
    zb = -H4_FRONT
    p = rrect_prism(DCX, DCY, L, Wd, zb + 0.1, zb + 2.5, 5.8)
    if st.get("badge") == "pyramid":
        p = p.cut(cq.Workplane("XY").polyline([(-11.2, 0), (0, -19.2), (11.2, 0), (0, 19.2)]).close().extrude(10).translate((DCX, DCY, zb - 5)))
    return desk_to_plate(p)


def v_light_inserts(st):
    zb = -H4_FRONT
    yv = DCY + DL / 2 - 16.0
    s = None
    for sgn in (-1, 1):
        arm = box(0.2, 61.8, -1.5, 1.5, zb + 0.05, zb + 2.0).rotate((0, 0, 0), (0, 0, 1), sgn * 28.0).translate((DCX, yv - 14.0, 0))
        s = arm if s is None else s.union(arm)
    return desk_to_plate(s)


def diag_inserts(st):
    ds = st["diag_slots"]; zb = -H4_FRONT
    s = None
    for i in range(ds["n"]):
        sx = DCX + ds["cx"] + (i - (ds["n"] - 1) / 2) * ds["pitch"]
        b = box(-ds["width"] / 2 + 0.05, ds["width"] / 2 - 0.05, -ds["length"] / 2 + 0.05, ds["length"] / 2 - 0.05, zb + 0.05, zb + 2.0).rotate((0, 0, 0), (0, 0, 1), ds["angle"])
        b = b.translate((sx, DCY + ds["cy"], 0))
        s = b if s is None else s.union(b)
    return desk_to_plate(s)


def front_bar_part(st):
    fb = st["front_bar"]
    b = box(OX0 + fb["margin"] + 0.1, OX1 - fb["margin"] - 0.1, YD0 - 0.0, YD0 + fb["t"] - 0.1, -H4_FRONT, -H4_FRONT + fb["h"] - 0.1)
    b = desk_to_plate(b).intersect(geom.outer_shell())
    try:
        b = b.edges("|X").chamfer(0.8)
    except Exception:
        pass
    return b


def deck_light_insert(st):
    r = st["deck_raise"]
    return box(-3.9, KEYS_W + 3.9, Y_STEP + 0.0, Y_STEP + 1.45, TOP_Z + 0.4, TOP_Z + r - 0.4)


def front_strip_insert(st):
    zb = -H4_FRONT
    y0 = YD0 + 6.0
    return desk_to_plate(box(DCX - 109.9, DCX + 109.9, y0 - 1.45, y0 + 1.45, zb + 0.05, zb + RING_D - 0.05))


def front_light_insert(st):
    zc = desk_z(OY0) + st.get("front_light_z", 5.0) / math.cos(TILT_R)
    return box(DCX - 109.9, DCX + 109.9, OY0 - 0.05, OY0 + 2.0, zc - 1.2, zc + 1.2).intersect(geom.outer_shell())
