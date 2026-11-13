"""Plate, display cartridge, weight, diffusers, daughterboards, display module and preview bodies (PLATE frame)."""
import cadquery as cq
from params import *
from geom import box, rrect_prism, cyl_z, cyl_x, cyl_y, desk_to_plate, weight_outline, poly_prism

# the 22 mounting holes of the current VLT PCB, in PCB coordinates (mm from its top-left corner, y down)
PCB_HOLES = [(4.981, 61.500), (19.269, 9.113), (21.650, 109.125), (31.175, 71.025), (35.937, 32.888),
             (45.463, 109.125), (59.750, 90.075), (88.325, 71.025), (93.087, 32.888), (100.231, 9.113),
             (135.950, 90.075), (140.713, 51.975), (181.194, 9.113), (188.338, 109.125), (197.863, 51.975),
             (212.150, 90.075), (240.725, 71.025), (257.394, 90.075), (262.156, 9.113), (278.825, 51.975),
             (288.350, 113.888), (302.638, 21.019)]
STAB_SPACING = {2.0: 11.9, 2.25: 11.9, 2.75: 11.9, 6.25: 50.0, 7.0: 57.15}


def pcb_holes_plate_frame():
    return [(PCB_X0 + hx, PCB_Y1 - hy) for hx, hy in PCB_HOLES]


# ---------------------------------------------------------------- plate
def plate(keys, fpc_slot=True):
    p = box(0, KEYS_W, -KEYS_H, 0, -PLATE_T, 0)
    for xt in PLATE_TAB_X:
        p = p.union(box(xt - PLATE_TAB_W / 2, xt + PLATE_TAB_W / 2, -0.01, PLATE_TAB_L, -PLATE_T, 0))
        p = p.union(box(xt - PLATE_TAB_W / 2, xt + PLATE_TAB_W / 2, -KEYS_H - PLATE_TAB_L, -KEYS_H + 0.01, -PLATE_T, 0))
    sw = [(cx, cy) for cx, cy, w, l in keys if l != "ENC"]
    p = p.cut(cq.Workplane("XY").pushPoints(sw).rect(14, 14).extrude(10).translate((0, 0, -5)))
    stabs = []
    for cx, cy, w, l in keys:
        s = STAB_SPACING.get(w)
        if s:
            stabs += [(cx - s, cy + 0.5), (cx + s, cy + 0.5)]
    p = p.cut(cq.Workplane("XY").pushPoints(stabs).rect(6.65, 12.3).extrude(10).translate((0, 0, -5)))
    p = p.cut(cyl_z(ENC_CX, ENC_CY, -5, 5, ENC_PLATE_HOLE / 2))
    # light slot under the bar, FPC slot under the display, ball-catch notches, standoff holes
    p = p.cut(box(BAR_CX - 2.0, BAR_CX + 2.0, -78.0, -2.0, -5, 5))
    if fpc_slot:
        p = p.cut(box(306.0, KEYS_W + 1, ISL_CY - 5.0, ISL_CY + 5.0, -5, 5))
    nw = BC_TAB_W / 2 + 0.75
    for xc in BC_BACK_X:
        p = p.cut(box(xc - nw, xc + nw, -BC_PLATE_NOTCH, 1, -5, 5))
    for xc in BC_FRONT_X:
        p = p.cut(box(xc - nw, xc + nw, -KEYS_H - 1, -KEYS_H + BC_PLATE_NOTCH, -5, 5))
    p = p.cut(box(-1, BC_PLATE_NOTCH, BC_LEFT_Y - nw, BC_LEFT_Y + nw, -5, 5))
    p = p.cut(box(KEYS_W - BC_PLATE_NOTCH, KEYS_W + 1, BC_RIGHT_Y - nw, BC_RIGHT_Y + nw, -5, 5))
    p = p.cut(cq.Workplane("XY").pushPoints(pcb_holes_plate_frame()).circle(1.55).extrude(10).translate((0, 0, -5)))
    return p


# ---------------------------------------------------------------- display cartridge
def cartridge():
    z_ledge = ISL_Z0 + CART_BOSS_H
    c = rrect_prism(CG_CX, ISL_CY, CART_BOSS_L, CART_BOSS_W, ISL_Z0, z_ledge, CG_R + CG_GAP - 0.05)
    c = c.cut(box(LCM_X0 - 0.25, LCM_X0 + LCM_L + 0.25, ISL_CY - LCM_W / 2 - 0.2, ISL_CY + LCM_W / 2 + 0.2,
                  ISL_Z0 + CART_FLOOR_T, z_ledge + 1))
    c = c.cut(box(LCM_X0 + LCM_L - 3.0, CG_CX + CART_BOSS_L / 2 + 1, ISL_CY - FPC_W / 2, ISL_CY + FPC_W / 2, ISL_Z0 - 1, z_ledge + 1))
    c = c.union(box(CG_CX - 2.0, CART_FLANGE_X1, ISL_CY - CART_FLANGE_W / 2, ISL_CY + CART_FLANGE_W / 2, ISL_Z0 - CART_FLANGE_T, ISL_Z0 + 0.01))
    c = c.cut(box(LCM_X0 + LCM_L - 1.5, LCM_X0 + LCM_L + 2.5, ISL_CY - FPC_W / 2, ISL_CY + FPC_W / 2, ISL_Z0 - CART_FLANGE_T - 1, ISL_Z0 + 0.5))
    for dy in (-CART_SCREW_DY, CART_SCREW_DY):
        c = c.cut(cyl_z(CART_SCREW_X, ISL_CY + dy, ISL_Z0 - CART_FLANGE_T - 1, ISL_Z0 + 1, 1.1))
    return c


def cover_glass():
    """the custom cover glass alone (what the panel maker changes), with its 0.2 x 45 top-edge chamfer"""
    g = rrect_prism(CG_CX, ISL_CY, CG_L, CG_W, TOP_Z - CG_T, TOP_Z, CG_R)
    return g.faces(">Z").edges().chamfer(0.2)


def display_module():
    """cover glass + LCM + a schematic FPC path down to a top-side PCB connector"""
    z_cg0 = TOP_Z - CG_T
    glass = rrect_prism(CG_CX, ISL_CY, CG_L, CG_W, z_cg0, TOP_Z, CG_R)
    lcm = box(LCM_X0, LCM_X0 + LCM_L, ISL_CY - LCM_W / 2, ISL_CY + LCM_W / 2, z_cg0 - LCM_T, z_cg0)
    xe = LCM_X0 + LCM_L
    fpc = (box(xe - 4, xe + 0.9, ISL_CY - 3.5, ISL_CY + 3.5, z_cg0 - LCM_T - 0.3, z_cg0 - LCM_T)
           .union(box(xe + 0.6, xe + 0.9, ISL_CY - 3.5, ISL_CY + 3.5, PCB_TOP_Z + 0.3, z_cg0 - LCM_T))
           .union(box(308.2, xe + 0.9, ISL_CY - 3.5, ISL_CY + 3.5, PCB_TOP_Z + 1.0, PCB_TOP_Z + 1.3)))
    return glass.union(lcm).union(fpc)


# ---------------------------------------------------------------- weight (desk frame → plate frame)
def weight():
    zb = -H_FRONT
    w = weight_outline().extrude(WEIGHT_T).translate((0, 0, zb - (WEIGHT_T - WEIGHT_POCKET_D)))
    w = w.faces("<Z").edges().chamfer(1.0)
    for sx, sy in WEIGHT_SCREWS:
        w = w.cut(cyl_z(sx, sy, zb + WEIGHT_POCKET_D - 3.2, zb + WEIGHT_POCKET_D + 1, 1.25))
    return desk_to_plate(w.translate((DCX, DCY, 0)))


# ---------------------------------------------------------------- diffusers
def bar_inserts():
    s = None
    for ya, yb in BAR_SEGMENTS:
        b = box(BAR_CX - BAR_CHAN_W / 2 + 0.05, BAR_CX + BAR_CHAN_W / 2 - 0.05, yb + 0.05, ya - 0.05, TOP_Z - BAR_CHAN_D + 0.02, TOP_Z)
        s = b if s is None else s.union(b)
    return s


def underglow_ring():
    zb = -H_FRONT
    cx, cy = DCX, DCY
    o = rrect_prism(cx, cy, W - 2 * (RING_IN - RING_W / 2) - 0.1, DL - 2 * (RING_IN - RING_W / 2) - 0.1, zb, zb + RING_D - 0.05, 3.95)
    i = rrect_prism(cx, cy, W - 2 * (RING_IN + RING_W / 2) + 0.1, DL - 2 * (RING_IN + RING_W / 2) + 0.1, zb - 1, zb + RING_D + 1, 1.05)
    return desk_to_plate(o.cut(i))


def led_bars():
    """4 LED bars (4 × 1.0 mm PCB strips, LEDs facing down) lying in the floor channels over the ring slots"""
    s = None
    z0 = FLOOR_ZD
    e = RING_CORNER_STOP + 1
    for b in (box(OX0 + e, OX1 - e, YD0 + RING_IN - 2, YD0 + RING_IN + 2, z0, z0 + 1.0),
              box(OX0 + e, OX1 - e, YD1 - RING_IN - 2, YD1 - RING_IN + 2, z0, z0 + 1.0),
              box(OX0 + RING_IN - 2, OX0 + RING_IN + 2, YD0 + e, YD1 - e, z0, z0 + 1.0),
              box(OX1 - RING_IN - 2, OX1 - RING_IN + 2, YD0 + e, YD1 - e, z0, z0 + 1.0)):
        s = b if s is None else s.union(b)
    return desk_to_plate(s)


# ---------------------------------------------------------------- PCB + daughterboards
def pcb():
    p = rrect_prism(PCB_X0 + PCB_W / 2, PCB_Y1 - PCB_H / 2, PCB_W, PCB_H, PCB_TOP_Z - PCB_T, PCB_TOP_Z, 1.0)
    p = p.cut(cq.Workplane("XY").pushPoints(pcb_holes_plate_frame()).circle(1.55).extrude(10).translate((0, 0, -10)))
    # display FPC connector (12-pin 0.5 mm, top side, flex entering from +x) and the pogo pad field (marked as a 0.05 recess)
    p = p.union(box(302.0, 308.0, ISL_CY - 4.0, ISL_CY + 4.0, PCB_TOP_Z, PCB_TOP_Z + 2.0))
    p = p.cut(box(POGO_CX - 7.0, POGO_CX + 7.0, POGO_CY - 3.0, POGO_CY + 3.0, PCB_TOP_Z - PCB_T - 1, PCB_TOP_Z - PCB_T + 0.05))
    return p


def usb_board():
    b = box(USB_CX - USB_BOARD_L / 2, USB_CX + USB_BOARD_L / 2, USB_BOARD_Y1 - USB_BOARD_W, USB_BOARD_Y1,
            USB_BOARD_TOP_Z - BOARD_T, USB_BOARD_TOP_Z)
    port = box(USB_CX - 4.3, USB_CX + 4.3, USB_BOARD_Y1 - 5.5, USB_BOARD_Y1 + 1.9, USB_PORT_Z - 1.4, USB_PORT_Z + 1.4)
    b = b.union(port)
    for dx in (-USB_SCREW_DX, USB_SCREW_DX):
        b = b.cut(cyl_z(USB_CX + dx, USB_SCREW_Y, -20, 0, 1.1))
    return b


def pogo_board():
    b = box(POGO_CX - POGO_BOARD_L / 2, POGO_CX + POGO_BOARD_L / 2, POGO_CY - POGO_BOARD_W / 2, POGO_CY + POGO_BOARD_W / 2,
            POGO_BOARD_TOP_Z - BOARD_T, POGO_BOARD_TOP_Z)
    n, m = POGO_PINS
    for i in range(n):
        for j in range(m):
            b = b.union(cyl_z(POGO_CX + (i - (n - 1) / 2) * 2.54, POGO_CY + (j - (m - 1) / 2) * 2.54,
                              POGO_BOARD_TOP_Z, PCB_TOP_Z - PCB_T - 0.4, 0.75))
    for sx, sy in ((-POGO_SCREW[0], -POGO_SCREW[1]), (POGO_SCREW[0], -POGO_SCREW[1]),
                   (-POGO_SCREW[0], POGO_SCREW[1]), (POGO_SCREW[0], POGO_SCREW[1])):
        b = b.cut(cyl_z(POGO_CX + sx, POGO_CY + sy, -30, 0, 1.1))
    return b


# ---------------------------------------------------------------- small hardware, for the assembly only
def gaskets():
    s = None
    for xt in PLATE_TAB_X:
        for y0, y1 in ((CLR + 0.1, PLATE_TAB_L), (-KEYS_H - PLATE_TAB_L, -KEYS_H - CLR - 0.1)):
            for z0, z1 in ((0, GASKET_T - 0.5), (-PLATE_T - (GASKET_T - 0.5), -PLATE_T)):
                b = box(xt - PLATE_TAB_W / 2, xt + PLATE_TAB_W / 2, y0, y1, z0, z1)
                s = b if s is None else s.union(b)
    return s


def ball_plungers():
    """M3 x 6 body (drawn at the tap-drill diameter) with a 2 mm ball protruding 1.0 into the cavity"""
    from geom import sphere
    s = None
    bodies = []
    for xc in BC_BACK_X:
        bodies.append(cyl_y(xc, BC_Z, CLR + 0.0, CLR + 6.0, 1.2).union(sphere(xc, CLR, BC_Z, 1.0)))
    for xc in BC_FRONT_X:
        yf = -(KEYS_H + CLR)
        bodies.append(cyl_y(xc, BC_Z, yf - 6.0, yf, 1.2).union(sphere(xc, yf, BC_Z, 1.0)))
    bodies.append(cyl_x(BC_LEFT_Y, BC_Z, -CLR - 6.0, -CLR, 1.2).union(sphere(-CLR, BC_LEFT_Y, BC_Z, 1.0)))
    bodies.append(cyl_x(BC_RIGHT_Y, BC_Z, KEYS_W + CLR, KEYS_W + CLR + 6.0, 1.2).union(sphere(KEYS_W + CLR, BC_RIGHT_Y, BC_Z, 1.0)))
    for b in bodies:
        s = b if s is None else s.union(b)
    return s


def keycaps_preview(keys):
    s = None
    for cx, cy, w, l in keys:
        if l == "ENC":
            continue
        b = box(cx - (w * U - 0.75) / 2, cx + (w * U - 0.75) / 2, cy - (U - 0.75) / 2, cy + (U - 0.75) / 2, 6.0, 14.0)
        s = b if s is None else s.union(b)
    return s


def knob():
    return cyl_z(ENC_CX, ENC_CY, 6.0, 6.0 + KNOB_H, KNOB_D / 2).faces(">Z").edges().fillet(1.0)
