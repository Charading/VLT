"""
VLT case v3 — every dimension in one place.  Units: mm.

Frames
------
PLATE frame (the modelling/assembly frame, used for every STEP):
    x  → right, along the key rows
    y  → towards the BACK of the board (KLE y is negated: the F-row is at y≈0, the arrows at y≈-124)
    z  → up, perpendicular to the plate.  z = 0 is the TOP surface of the plate.
DESK frame: the same, rotated by TILT about the x axis, so that the desk is flat (z_desk = const).
    Only the bottom face of the case and everything on it (weight, underglow ring, bumpons) live in this frame.
    The walls are perpendicular to the plate (the case is a tilted block, like Keycult / Zoom), so every wall
    has the same thickness over its whole height.
"""
import math

U = 19.05                      # key unit
KEYS_W = 16.5 * U              # key area 314.325
KEYS_H = 6.5 * U               # key area 123.825 (arrows are dropped 0.25u)
CAP = 18.3                     # keycap base, worst case (Cherry profile ≈18.1–18.3)
CAP_G = (U - CAP) / 2          # 0.375 — gap from the key cell edge to the keycap edge

# ---------- case envelope ----------
BEZEL = 8.0                    # bezel width at the top surface, all four sides
CLR = 0.6                      # opening / cavity clearance around the key area
W = KEYS_W + 2 * BEZEL         # 330.325 outer width
D = KEYS_H + 2 * BEZEL         # 139.825 outer depth
OX0, OX1 = -BEZEL, KEYS_W + BEZEL
OY1 = +BEZEL                   # back outer edge  (y positive = back)
OY0 = -(KEYS_H + BEZEL)        # front outer edge
TOP_Z = 7.5                    # top surface of the bezel above the plate top (high profile: hides the switches)
SEAM_Z = -2.0                  # top case / bottom case split
TILT = 6.0                     # typing angle, degrees
H_FRONT = 21.5                 # desk → top of the front bezel, measured perpendicular to the desk
FLOOR_T = 4.0                  # bottom case floor
CORNER_R = 3.0                 # vertical outer corners
TOP_CHAMFER = 1.0              # outer top edge of the top case
BOTTOM_CHAMFER = 1.2           # outer bottom edge of the bottom case

# ---------- plate / PCB stack ----------
PLATE_T = 1.5
PCB_TOP_Z = -5.0               # MX: plate top → PCB top = 5.0
PCB_T = 1.6
PCB_X0, PCB_Y1 = 2.17, -0.38   # the current VLT PCB (310 × 123) sits here in the plate frame
PCB_W, PCB_H = 310.0, 123.0
PLATE_TAB_X = [40.0, 135.0, 200.0, KEYS_W - 40.0]   # gasket tabs, back and front edges (clear of the USB pocket at 143.7..170.7)
PLATE_TAB_W = 20.0
PLATE_TAB_L = 4.5              # how far a tab reaches into the wall (pocket 5.6 deep in the 7.4 wall → 1.8 skin)
GASKET_T = 2.0                 # Poron, uncompressed; 1.5 compressed
POCKET_X_CLR = 0.3

# ---------- ball catch ----------
# M3 × 6 spring ball plungers (ball Ø2, ~3 N) screwed horizontally into the bottom case walls,
# engaging hemispherical dimples in skirt tabs that hang down from the top case.
# Back catches sit in the 0.25u gaps of the F-row (F4|F5 and F8|F9) so the plate notch does not thin the web above a cutout;
# the right-side catch sits beside the → key (the nav column's cutouts come within 2.5 mm of the plate edge).
BC_BACK_X = [102.4, 183.35]
BC_FRONT_X = [90.0, 230.0]
BC_LEFT_Y = -62.0
BC_RIGHT_Y = -114.0
BC_TAB_W = 8.0
BC_TAB_T = 1.5
BC_TAB_Z0 = -8.0               # tabs hang from SEAM_Z down to here
BC_Z = -5.0                    # plunger axis
BC_TAP = 2.5                   # M3 tap drill
BC_DEPTH = 7.0
BC_DIMPLE_R = 1.5              # sphere radius; centre 0.5 outside the tab face → 1.0 deep dimple
BC_PLATE_NOTCH = 1.8           # plate edge recess under each tab

# ---------- signature features in the top case ----------
BAR_CX = 15.25 * U             # light bar centre, in the 0.5u gap between the main block and the nav column
BAR_W = 6.0
BAR_Z0 = 4.5                   # bar underside (bar is 3.0 thick)
BAR_CHAN_W = 3.5               # frosted PC insert, flush with the top
BAR_CHAN_D = 1.2
BAR_SLOT_W = 2.5               # light slot under the insert
BAR_SEGMENTS = [(+4.0, -18.0), (-24.0, -79.5)]   # (y_start, y_end) of the two insert segments

# island that carries the display, between PgDn (above) and → (below), joined to the right bezel
ISL_CLR = 0.8
ISL_Y1 = -(3.75 * U) - CAP / 2 - ISL_CLR      # just under the PgDn keycap  (-81.39)
ISL_Y0 = -(6.00 * U) + CAP / 2 + ISL_CLR      # just above the → keycap     (-104.35)
ISL_X0 = 15.25 * U - CAP_G + 0.9              # right of the ↑ keycap        (291.04)
ISL_CY = (ISL_Y0 + ISL_Y1) / 2                # -92.87
ISL_Z0 = 3.0                                  # bridge underside (bridge is 4.5 thick)

# ---------- display (custom cover glass on the Huadi HD085019C12 0.85" module) ----------
# The module is turned 90°: its FPC leaves towards +x, under the right bezel.
LCM_L, LCM_W, LCM_T = 20.82, 17.58, 1.89      # module: length along x (FPC end at +x), width along y, thickness below the glass
LCM_AA = 15.21                                # active area (square)
LCM_AA_FROM_TOP = 1.44                        # AA edge from the module's non-FPC end
LCM_AA_FROM_SIDE = 1.185
CG_OVERHANG = 1.5                             # cover glass beyond the module, all four sides
CG_L = LCM_L + 2 * CG_OVERHANG                # 23.82 → 23.8
CG_W = LCM_W + 2 * CG_OVERHANG                # 20.58 → 20.6
CG_T = 1.10
CG_R = 1.0
CG_GAP = 0.15                                 # glass ↔ island opening, per side
VA = 15.61                                    # touch/visible window in the black mask
TAPE_T = 0.2                                  # VHB between the glass and the cartridge ledge
CG_X0 = ISL_X0 + 1.2                          # 292.24: glass left edge (1.2 mm of island frame to the left)
CG_CX = CG_X0 + CG_L / 2                      # 304.15
LCM_X0 = CG_X0 + CG_OVERHANG                  # 293.74
AA_CX = LCM_X0 + LCM_AA_FROM_TOP + LCM_AA / 2  # 302.79

# cartridge (display carrier): tray that fills the island opening from below, flange screwed into the right wall
CART_BOSS_L = CG_L + 2 * CG_GAP - 0.1         # 24.1 opening, boss 24.0
CART_BOSS_W = CG_W + 2 * CG_GAP - 0.1
CART_BOSS_H = TOP_Z - CG_T - TAPE_T - ISL_Z0  # 3.2: ledge at z 6.2
CART_FLOOR_T = 0.6
CART_FLANGE_T = 1.5
CART_FLANGE_W = 22.0
CART_FLANGE_X1 = KEYS_W + CLR + 5.4           # 320.3, inside the wall notch
CART_NOTCH_X1 = KEYS_W + CLR + 5.6            # 320.5
CART_NOTCH_W = 23.0
CART_SCREW_X = 318.3
CART_SCREW_DY = 8.0
FPC_W = 11.0                                  # slot for the LCM flex (it is ~10 wide at the module)

# ---------- bottom case features ----------
RING_IN = 10.0                                # underglow ring centreline from the outer edge (slot lands 2.6 inside the cavity wall)
RING_W = 3.0
RING_D = 2.0                                  # frosted PC ring, flush with the bottom face
RING_SLOT_W = 2.0
RING_CORNER_STOP = 18.0                       # slot ends this far from the corners (strength)
LED_CHAN_W = 5.0                              # locating channel for the 4 LED bars on the inner floor
LED_CHAN_D = 1.2
WEIGHT_L, WEIGHT_W, WEIGHT_T = 200.0, 56.0, 4.0
WEIGHT_CHAMFER = 12.0                         # 45° corner cuts of the weight outline
WEIGHT_POCKET_D = 3.0                         # weight stands 1.0 proud
WEIGHT_CLR = 0.25
WEIGHT_SCREWS = [(-80.0, -18.0), (80.0, -18.0), (-80.0, 18.0), (80.0, 18.0)]   # M3 from inside
BUMPON_D, BUMPON_IN, BUMPON_DEPTH = 10.0, 20.0, 1.0

# USB-C daughterboard (back wall, centre) and pogo daughterboard (under the PCB)
USB_CX = KEYS_W / 2
USB_BOARD_L, USB_BOARD_W = 25.0, 14.0         # along x, along y
USB_BOARD_Y1 = 5.0                            # back edge, inside the wall pocket
USB_BOARD_TOP_Z = -8.6
USB_PORT_Z = -7.5
USB_PLUG_W, USB_PLUG_H, USB_PLUG_R = 9.6, 3.6, 1.5
USB_SCREW_DX, USB_SCREW_Y = 9.5, -5.5
POGO_CX, POGO_CY = KEYS_W / 2, -20.0
POGO_BOARD_L, POGO_BOARD_W = 40.0, 18.0
POGO_BOARD_TOP_Z = -13.0                      # 6.0 mm spring pins reach the PCB underside with 0.4 compression
POGO_PINS = (5, 2)                            # 2 rows × 5, 2.54 mm pitch
POGO_SCREW = (17.0, 6.5)
BOARD_T = 1.6
BOSS_D, BOSS_TAP = 5.0, 1.6

# ---------- encoder / knob ----------
ENC_CX, ENC_CY = 16.0 * U, -0.5 * U
ENC_PLATE_HOLE = 8.0
KNOB_D, KNOB_H = 18.0, 12.0

# derived
TILT_R = math.radians(TILT)
FLOOR_ZD = -H_FRONT + FLOOR_T                 # cavity floor in the desk frame (relative to the top front edge)
# the bottom face, seen in the desk frame: x spans OX0..OX1, y spans YD0..YD1 (the walls are tilted in this frame)
YD0 = H_FRONT * math.tan(TILT_R)              # 2.26
YD1 = D / math.cos(TILT_R) + YD0              # 142.86
DCX, DCY = KEYS_W / 2, (YD0 + YD1) / 2        # centre of the bottom face
DL = YD1 - YD0                                # 140.6 — length of the bottom face
H_BACK = H_FRONT + D * math.tan(TILT_R)       # 36.2 — desk → top of the back bezel
