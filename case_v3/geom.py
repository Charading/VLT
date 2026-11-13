"""Helpers + the two case halves.  All functions return cq.Workplane solids in the PLATE frame."""
import math
import cadquery as cq
from params import *


# ---------------------------------------------------------------- primitives
def box(x0, x1, y0, y1, z0, z1):
    return cq.Workplane("XY").box(x1 - x0, y1 - y0, z1 - z0, centered=False).translate((x0, y0, z0))


def rrect_prism(cx, cy, lx, ly, z0, z1, r):
    s = cq.Workplane("XY").center(cx, cy).rect(lx, ly).extrude(z1 - z0).translate((0, 0, z0))
    return s.edges("|Z").fillet(r) if r > 0 else s


def poly_prism(pts, z0, z1):
    return cq.Workplane("XY").polyline(pts).close().extrude(z1 - z0).translate((0, 0, z0))


def cyl_z(cx, cy, z0, z1, r):
    return cq.Workplane("XY").center(cx, cy).circle(r).extrude(z1 - z0).translate((0, 0, z0))


def cyl_y(cx, cz, y0, y1, r):
    """cylinder along +y from y0 to y1"""
    return cyl_z(0, 0, 0, y1 - y0, r).rotate((0, 0, 0), (1, 0, 0), -90).translate((cx, y0, cz))


def cyl_x(cy, cz, x0, x1, r):
    """cylinder along +x from x0 to x1"""
    return cyl_z(0, 0, 0, x1 - x0, r).rotate((0, 0, 0), (0, 1, 0), 90).translate((x0, cy, cz))


def sphere(cx, cy, cz, r):
    return cq.Workplane("XY").sphere(r).translate((cx, cy, cz))


def desk_to_plate(wp):
    """DESK frame → PLATE frame.  Desk origin = the top-front outer edge of the case at x=0."""
    return wp.rotate((0, 0, 0), (1, 0, 0), -TILT).translate((0, OY0, TOP_Z))


def slab(z0, z1):
    return box(-60, W + 60, OY0 - 60, OY1 + 60, z0, z1)


def desk_box(x0, x1, yd0, yd1, zd0, zd1):
    """axis-aligned box in the DESK frame, returned in the PLATE frame"""
    return desk_to_plate(box(x0, x1, yd0, yd1, zd0, zd1))


def opening_polygon():
    """the keycap window in the top case: key area + CLR, with the 0.25u step for the dropped arrow cluster"""
    xs = 13.125 * U
    return [(-CLR, CLR), (KEYS_W + CLR, CLR), (KEYS_W + CLR, -(KEYS_H + CLR)),
            (xs, -(KEYS_H + CLR)), (xs, -(6.25 * U + CLR)), (-CLR, -(6.25 * U + CLR))]


def tab_pocket_ranges():
    """y ranges of the gasket-tab pockets in the walls: (back, front)"""
    back = (CLR - 0.01, CLR + PLATE_TAB_L + 0.6)
    front = (-(KEYS_H + CLR) - PLATE_TAB_L - 0.6, -(KEYS_H + CLR) + 0.01)
    return back, front


# ---------------------------------------------------------------- outer skin
def outer_shell():
    """the case envelope: walls perpendicular to the plate, R3 corners, bottom face parallel to the desk, bottom chamfer"""
    s = rrect_prism(KEYS_W / 2, (OY0 + OY1) / 2, W, D, -80, 45, CORNER_R)
    s = s.intersect(desk_box(-100, W + 100, -100, D + 100, -H_FRONT, 90))
    s = s.faces("<Z").edges().chamfer(BOTTOM_CHAMFER)
    return s


# ---------------------------------------------------------------- top case
def top_case():
    shell = outer_shell()
    tc = shell.intersect(slab(SEAM_Z, TOP_Z))
    tc = tc.faces(">Z").edges().chamfer(TOP_CHAMFER)

    # keycap window, and a relief so the bezel never touches the plate (the front bezel overhangs the plate's
    # strip under the dropped arrow cluster; the plate top is z = 0, the relief ceiling z = +0.3)
    tc = tc.cut(poly_prism(opening_polygon(), SEAM_Z - 1, TOP_Z + 1))
    tc = tc.cut(box(-CLR, KEYS_W + CLR, -(KEYS_H + CLR), CLR, SEAM_Z - 0.01, 0.3))

    # islands: the light bar and the display bridge
    bar = box(BAR_CX - BAR_W / 2, BAR_CX + BAR_W / 2, ISL_Y1 - 0.01, CLR + 1.0, BAR_Z0, TOP_Z)
    isl = box(ISL_X0, KEYS_W + CLR + 1.0, ISL_Y0, ISL_Y1, ISL_Z0, TOP_Z)
    tc = tc.union(bar).union(isl)

    # light bar: flush PC insert channel + light slot (slot only over the plate, y <= -1.5)
    for ya, yb in BAR_SEGMENTS:
        tc = tc.cut(box(BAR_CX - BAR_CHAN_W / 2, BAR_CX + BAR_CHAN_W / 2, yb, ya, TOP_Z - BAR_CHAN_D, TOP_Z + 1))
        ya2, yb2 = min(ya, -1.5), yb + 1.0
        if ya2 > yb2:
            tc = tc.cut(box(BAR_CX - BAR_SLOT_W / 2, BAR_CX + BAR_SLOT_W / 2, yb2, ya2, BAR_Z0 - 1, TOP_Z - BAR_CHAN_D + 0.01))

    # display: through-opening for the glass, wall notch for the cartridge flange, M2 blind holes
    tc = tc.cut(rrect_prism(CG_CX, ISL_CY, CG_L + 2 * CG_GAP, CG_W + 2 * CG_GAP, ISL_Z0 - 1, TOP_Z + 1, CG_R + CG_GAP))
    tc = tc.cut(box(KEYS_W + CLR - 0.01, CART_NOTCH_X1, ISL_CY - CART_NOTCH_W / 2, ISL_CY + CART_NOTCH_W / 2, SEAM_Z - 1, ISL_Z0))
    for dy in (-CART_SCREW_DY, CART_SCREW_DY):
        tc = tc.cut(cyl_z(CART_SCREW_X, ISL_CY + dy, ISL_Z0 - 0.5, ISL_Z0 + 3.5, BOSS_TAP / 2))

    # gasket pockets: tab + top gasket (compressed) sit between SEAM_Z and +1.5
    back, front = tab_pocket_ranges()
    for xt in PLATE_TAB_X:
        for y0, y1 in (back, front):
            tc = tc.cut(box(xt - PLATE_TAB_W / 2 - POCKET_X_CLR, xt + PLATE_TAB_W / 2 + POCKET_X_CLR,
                            y0, y1, SEAM_Z - 1, GASKET_T - 0.5))

    # ball-catch skirt tabs with dimples
    for xc in BC_BACK_X:
        tc = tc.union(box(xc - BC_TAB_W / 2, xc + BC_TAB_W / 2, CLR - 0.1 - BC_TAB_T, CLR - 0.1, BC_TAB_Z0, SEAM_Z + 0.01))
        tc = tc.cut(sphere(xc, CLR - 0.1 + 0.5, BC_Z, BC_DIMPLE_R))
    for xc in BC_FRONT_X:
        yf = -(KEYS_H + CLR) + 0.1
        tc = tc.union(box(xc - BC_TAB_W / 2, xc + BC_TAB_W / 2, yf, yf + BC_TAB_T, BC_TAB_Z0, SEAM_Z + 0.01))
        tc = tc.cut(sphere(xc, yf - 0.5, BC_Z, BC_DIMPLE_R))
    xl = -CLR + 0.1
    tc = tc.union(box(xl, xl + BC_TAB_T, BC_LEFT_Y - BC_TAB_W / 2, BC_LEFT_Y + BC_TAB_W / 2, BC_TAB_Z0, SEAM_Z + 0.01))
    tc = tc.cut(sphere(xl - 0.5, BC_LEFT_Y, BC_Z, BC_DIMPLE_R))
    xr = KEYS_W + CLR - 0.1
    tc = tc.union(box(xr - BC_TAB_T, xr, BC_RIGHT_Y - BC_TAB_W / 2, BC_RIGHT_Y + BC_TAB_W / 2, BC_TAB_Z0, SEAM_Z + 0.01))
    tc = tc.cut(sphere(xr + 0.5, BC_RIGHT_Y, BC_Z, BC_DIMPLE_R))
    return tc


# ---------------------------------------------------------------- bottom case
def bottom_case():
    shell = outer_shell()
    bc = shell.intersect(slab(-80, SEAM_Z))

    # cavity: vertical walls (plate frame), floor parallel to the desk
    cav = box(-CLR, KEYS_W + CLR, -(KEYS_H + CLR), CLR, -80, SEAM_Z + 1)
    cav = cav.intersect(desk_box(-100, W + 100, -100, D + 100, FLOOR_ZD, 80))
    bc = bc.cut(cav)

    # bosses for the two daughterboards (trimmed to the skin afterwards)
    bosses = None
    boss_tops = []
    for dx in (-USB_SCREW_DX, USB_SCREW_DX):
        boss_tops.append((USB_CX + dx, USB_SCREW_Y, USB_BOARD_TOP_Z - BOARD_T))
    for sx, sy in ((-POGO_SCREW[0], -POGO_SCREW[1]), (POGO_SCREW[0], -POGO_SCREW[1]),
                   (-POGO_SCREW[0], POGO_SCREW[1]), (POGO_SCREW[0], POGO_SCREW[1])):
        boss_tops.append((POGO_CX + sx, POGO_CY + sy, POGO_BOARD_TOP_Z - BOARD_T))
    for bx, by, bz in boss_tops:
        c = cyl_z(bx, by, -80, bz, BOSS_D / 2)
        bosses = c if bosses is None else bosses.union(c)
    bc = bc.union(bosses).intersect(shell)
    for bx, by, bz in boss_tops:
        bc = bc.cut(cyl_z(bx, by, bz - 5.0, bz + 0.1, BOSS_TAP / 2))

    # USB-C: plug window through the back wall + pocket for the board end
    plug = rrect_prism(USB_CX, 0, USB_PLUG_W, USB_PLUG_H, 0, 14, USB_PLUG_R).rotate((0, 0, 0), (1, 0, 0), -90)
    bc = bc.cut(plug.translate((0, CLR - 1, USB_PORT_Z)))
    bc = bc.cut(box(USB_CX - 13.5, USB_CX + 13.5, CLR - 0.01, USB_BOARD_Y1, USB_BOARD_TOP_Z - BOARD_T - 0.3, -4.5))

    # bottom gasket pockets (the gasket under each plate tab sits on z = -3.0)
    back, front = tab_pocket_ranges()
    for xt in PLATE_TAB_X:
        for y0, y1 in (back, front):
            bc = bc.cut(box(xt - PLATE_TAB_W / 2 - POCKET_X_CLR, xt + PLATE_TAB_W / 2 + POCKET_X_CLR, y0, y1, -3.0, SEAM_Z + 1))

    # ball plunger holes (M3 tap drill), horizontal, from the cavity face
    for xc in BC_BACK_X:
        bc = bc.cut(cyl_y(xc, BC_Z, CLR - 0.5, CLR + BC_DEPTH, BC_TAP / 2))
    for xc in BC_FRONT_X:
        bc = bc.cut(cyl_y(xc, BC_Z, -(KEYS_H + CLR) - BC_DEPTH, -(KEYS_H + CLR) + 0.5, BC_TAP / 2))
    bc = bc.cut(cyl_x(BC_LEFT_Y, BC_Z, -CLR - BC_DEPTH, -CLR + 0.5, BC_TAP / 2))
    bc = bc.cut(cyl_x(BC_RIGHT_Y, BC_Z, KEYS_W + CLR - 0.5, KEYS_W + CLR + BC_DEPTH, BC_TAP / 2))

    # ---- bottom face (desk frame; the face spans x OX0..OX1, y YD0..YD1) ----
    zb = -H_FRONT                                   # bottom face
    cx, cy = DCX, DCY
    ring_out = rrect_prism(cx, cy, W - 2 * (RING_IN - RING_W / 2), DL - 2 * (RING_IN - RING_W / 2), zb - 1, zb + RING_D, 4.0)
    ring_in = rrect_prism(cx, cy, W - 2 * (RING_IN + RING_W / 2), DL - 2 * (RING_IN + RING_W / 2), zb - 2, zb + RING_D + 1, 1.0)
    bc = bc.cut(desk_to_plate(ring_out.cut(ring_in)))
    for feat in ring_slots(zb, zb + FLOOR_T + 1, RING_SLOT_W) + ring_slots(FLOOR_ZD - 0.01, FLOOR_ZD + LED_CHAN_D, LED_CHAN_W):
        bc = bc.cut(desk_to_plate(feat))
    wpk = weight_outline(WEIGHT_CLR).extrude(WEIGHT_POCKET_D + 1).translate((0, 0, zb - 1))
    bc = bc.cut(desk_to_plate(wpk.translate((cx, cy, 0))))
    for sx, sy in WEIGHT_SCREWS:
        bc = bc.cut(desk_to_plate(cyl_z(cx + sx, cy + sy, zb - 1, FLOOR_ZD + 1, 1.7)))
    for bx in (OX0 + BUMPON_IN, OX1 - BUMPON_IN):
        for by in (YD0 + BUMPON_IN, YD1 - BUMPON_IN):
            bc = bc.cut(desk_to_plate(cyl_z(bx, by, zb - 1, zb + BUMPON_DEPTH, BUMPON_D / 2)))
    return bc


def ring_slots(z0, z1, w):
    """4 straight boxes along the ring centreline (desk frame), stopping short of the corners"""
    s = RING_CORNER_STOP
    out = [box(OX0 + s, OX1 - s, YD0 + RING_IN - w / 2, YD0 + RING_IN + w / 2, z0, z1),
           box(OX0 + s, OX1 - s, YD1 - RING_IN - w / 2, YD1 - RING_IN + w / 2, z0, z1),
           box(OX0 + RING_IN - w / 2, OX0 + RING_IN + w / 2, YD0 + s, YD1 - s, z0, z1),
           box(OX1 - RING_IN - w / 2, OX1 - RING_IN + w / 2, YD0 + s, YD1 - s, z0, z1)]
    return out


def weight_outline(grow=0.0):
    """stretched octagon, centred on the origin (2D workplane)"""
    hl, hw, c = WEIGHT_L / 2 + grow, WEIGHT_W / 2 + grow, WEIGHT_CHAMFER
    pts = [(-hl + c, -hw), (hl - c, -hw), (hl, -hw + c), (hl, hw - c), (hl - c, hw), (-hl + c, hw), (-hl, hw - c), (-hl, -hw + c)]
    return cq.Workplane("XY").polyline(pts).close()
