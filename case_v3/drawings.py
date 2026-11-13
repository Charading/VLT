"""Dimensioned 2D drawings (DXF + PNG preview) from the CadQuery solids.

    cadenv/Scripts/python.exe drawings.py
"""
import os, math, datetime
import cadquery as cq
import ezdxf
from ezdxf.enums import TextEntityAlignment
from ezdxf.addons.drawing.matplotlib import qsave
from params import *
import geom, parts
from kle import key_centres_mm

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out", "dxf")
PNG = os.path.join(HERE, "out", "png")
KLE = os.path.join(HERE, "..", "VLT-layout.json")
TODAY = datetime.date.today().isoformat()
TXT = 2.2           # dimension text height


# ---------------------------------------------------------------- dxf helpers
def new_doc():
    doc = ezdxf.new("R2010", setup=True)
    doc.header["$INSUNITS"] = 4
    for name, color, lt in (("OUTLINE", 7, "CONTINUOUS"), ("HIDDEN", 8, "DASHED"), ("DIM", 1, "CONTINUOUS"),
                            ("NOTES", 3, "CONTINUOUS"), ("CENTER", 4, "CENTER"), ("TITLE", 7, "CONTINUOUS"),
                            ("ZONE", 6, "DASHED")):
        doc.layers.add(name, color=color, linetype=lt)
    return doc


def add_edges(msp, wp, layer="OUTLINE", dx=0.0, dy=0.0, scale=1.0):
    """every edge of a (flattened) CadQuery section → DXF line / arc / circle / polyline"""
    for e in wp.edges().vals():
        t = e.geomType()
        attrs = {"layer": layer}
        if t == "LINE":
            p, q = e.startPoint(), e.endPoint()
            msp.add_line((p.x * scale + dx, p.y * scale + dy), (q.x * scale + dx, q.y * scale + dy), dxfattribs=attrs)
        elif t == "CIRCLE":
            c, r = e.arcCenter(), e.radius()
            p, q = e.startPoint(), e.endPoint()
            if (p - q).Length < 1e-6:
                msp.add_circle((c.x * scale + dx, c.y * scale + dy), r * scale, dxfattribs=attrs)
            else:
                m = e.positionAt(0.5)
                a0 = math.degrees(math.atan2(p.y - c.y, p.x - c.x))
                a1 = math.degrees(math.atan2(q.y - c.y, q.x - c.x))
                am = math.degrees(math.atan2(m.y - c.y, m.x - c.x))
                # DXF arcs run counter-clockwise from a0 to a1: make sure the mid point lies on that sweep
                def ccw_between(a, b, x):
                    return ((x - a) % 360) <= ((b - a) % 360)
                if not ccw_between(a0, a1, am):
                    a0, a1 = a1, a0
                msp.add_arc((c.x * scale + dx, c.y * scale + dy), r * scale, a0, a1, dxfattribs=attrs)
        else:
            n = 24
            pts = [e.positionAt(i / n) for i in range(n + 1)]
            msp.add_lwpolyline([(p.x * scale + dx, p.y * scale + dy) for p in pts], dxfattribs=attrs)


def section(wp, z):
    """planar section of a solid at height z, flattened to z = 0"""
    return cq.Workplane("XY").add(wp.val()).section(z).translate((0, 0, -z))


def rect(msp, x0, y0, x1, y1, layer="OUTLINE"):
    msp.add_lwpolyline([(x0, y0), (x1, y0), (x1, y1), (x0, y1)], close=True, dxfattribs={"layer": layer})


def rrect(msp, x0, y0, x1, y1, r, layer="OUTLINE"):
    msp.add_lwpolyline([(x0 + r, y0), (x1 - r, y0), (x1, y0 + r), (x1, y1 - r), (x1 - r, y1), (x0 + r, y1), (x0, y1 - r), (x0, y0 + r)],
                       close=True, dxfattribs={"layer": layer})
    # true arcs on the corners
    for cx, cy, a in ((x1 - r, y0 + r, 270), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        msp.add_arc((cx, cy), r, a, a + 90, dxfattribs={"layer": layer})


OV = {"dimtxt": TXT, "dimasz": TXT * 0.7, "dimexo": 0.6, "dimexe": 1.0, "dimtad": 1, "dimgap": 0.5, "dimdec": 2,
      "dimtih": 0, "dimtoh": 0, "dimclrt": 1, "dimclrd": 1, "dimclre": 1, "dimzin": 8}


def hdim(msp, x0, x1, y, off, text=None):
    d = msp.add_linear_dim(base=(x0, y + off), p1=(x0, y), p2=(x1, y), angle=0, dimstyle="EZDXF", override=OV,
                           text=text if text else "<>", dxfattribs={"layer": "DIM"})
    d.render()


def vdim(msp, y0, y1, x, off, text=None):
    d = msp.add_linear_dim(base=(x + off, y0), p1=(x, y0), p2=(x, y1), angle=90, dimstyle="EZDXF", override=OV,
                           text=text if text else "<>", dxfattribs={"layer": "DIM"})
    d.render()


def rdim(msp, cx, cy, r, angle=45, text=None):
    d = msp.add_radius_dim(center=(cx, cy), radius=r, angle=angle, dimstyle="EZDXF", override=OV,
                           text=text if text else "<>", dxfattribs={"layer": "DIM"})
    d.render()


def note(msp, x, y, s, h=TXT, layer="NOTES", align=TextEntityAlignment.LEFT):
    msp.add_text(s, height=h, dxfattribs={"layer": layer}).set_placement((x, y), align=align)


def notes(msp, x, y, lines, h=TXT, gap=1.7):
    for i, s in enumerate(lines):
        note(msp, x, y - i * h * gap, s, h)


def title_block(msp, x, y, w, title, part, material, finish, scale="1:1", rev="A"):
    """x,y = bottom-left corner"""
    w = max(w, 190)
    h = 26
    rect(msp, x, y, x + w, y + h, "TITLE")
    msp.add_line((x, y + 13), (x + w, y + 13), dxfattribs={"layer": "TITLE"})
    msp.add_line((x + w * 0.5, y), (x + w * 0.5, y + h), dxfattribs={"layer": "TITLE"})
    note(msp, x + 2, y + 20, "MARSVLT - VLT keyboard, case v3", 2.4, "TITLE")
    note(msp, x + 2, y + 15, title, 2.0, "TITLE")
    note(msp, x + 2, y + 8.5, "Part: " + part, 1.8, "TITLE")
    note(msp, x + 2, y + 4, "Mat.: " + material + "   Finish: " + finish, 1.6, "TITLE")
    note(msp, x + w * 0.5 + 2, y + 20, "Units mm   Scale " + scale + "   Rev " + rev + "   " + TODAY, 1.8, "TITLE")
    note(msp, x + w * 0.5 + 2, y + 15, "Drawn: Claude / CadQuery (hardware/VLT/case_v3)", 1.6, "TITLE")
    note(msp, x + w * 0.5 + 2, y + 8.5, "Tolerance +/-0.10 unless noted. Break edges 0.2.", 1.6, "TITLE")
    note(msp, x + w * 0.5 + 2, y + 4, "Third-angle projection.", 1.6, "TITLE")


def save(doc, name, size=(20, 12)):
    os.makedirs(OUT, exist_ok=True)
    os.makedirs(PNG, exist_ok=True)
    p = os.path.join(OUT, name + ".dxf")
    doc.saveas(p)
    qsave(doc.modelspace(), os.path.join(PNG, "dwg_" + name + ".png"), bg="#FFFFFF", fg="#000000", dpi=140, size_inches=size)
    os.makedirs(os.path.join(HERE, "out", "pdf"), exist_ok=True)
    qsave(doc.modelspace(), os.path.join(HERE, "out", "pdf", name + ".pdf"), bg="#FFFFFF", fg="#000000", dpi=200, size_inches=size)
    print("wrote", p)


# ---------------------------------------------------------------- 1. custom cover glass for the display maker
def draw_display():
    doc = new_doc(); msp = doc.modelspace()
    S = 3.0                                 # the views are drawn 3:1 (dimension texts carry the true values)
    # Drawn in the panel maker's orientation: FPC exits at the BOTTOM.  CG is 20.6 wide × 23.8 tall.
    gw, gh = CG_W * S, CG_L * S
    mw, mh = LCM_W * S, LCM_L * S
    ox = (gw - mw) / 2
    oy = (gh - mh) / 2
    # front view, origin = CG bottom-left
    rrect(msp, 0, 0, gw, gh, CG_R * S)
    rect(msp, ox, oy, ox + mw, oy + mh, "HIDDEN")                               # LCM outline
    aa_x0 = ox + LCM_AA_FROM_SIDE * S; aa_y1 = gh - oy - LCM_AA_FROM_TOP * S
    rect(msp, aa_x0, aa_y1 - LCM_AA * S, aa_x0 + LCM_AA * S, aa_y1, "HIDDEN")   # LCD active area
    va_x0 = (gw - VA * S) / 2; va_y1 = aa_y1 + 0.2 * S
    rrect(msp, va_x0, va_y1 - VA * S, va_x0 + VA * S, va_y1, 0.3 * S)           # VA = window in the black mask
    msp.add_line((va_x0, va_y1 - VA * S), (va_x0 + VA * S, va_y1), dxfattribs={"layer": "CENTER"})
    msp.add_line((va_x0, va_y1), (va_x0 + VA * S, va_y1 - VA * S), dxfattribs={"layer": "CENTER"})
    note(msp, gw / 2, va_y1 - VA * S / 2 - 7, "VA / touch area / mask window", 1.8, align=TextEntityAlignment.CENTER)
    note(msp, ox + 1, oy + 1.5, "LCM outline (ref)", 1.6)
    # FPC stub leaving the module bottom edge
    fx0 = gw / 2 - 5.0 * S
    msp.add_lwpolyline([(fx0, oy), (fx0, -12 * S), (fx0 + 10 * S, -12 * S), (fx0 + 10 * S, oy)], dxfattribs={"layer": "HIDDEN"})
    note(msp, gw / 2, -12 * S - 4, "FPC unchanged: 12-pin 0.5 mm, 35 +/-0.3 long, pinout per HD085019C12", 1.8, align=TextEntityAlignment.CENTER)
    # dimensions (true values written explicitly)
    hdim(msp, 0, gw, gh, 8, "CG %.2f +/-0.05" % CG_W)
    hdim(msp, ox, ox + mw, gh, 15, "LCM %.2f (ref)" % LCM_W)
    hdim(msp, va_x0, va_x0 + VA * S, gh, 22, "VA / mask window %.2f +/-0.10" % VA)
    hdim(msp, 0, va_x0, 0, -8, "%.3f" % ((CG_W - VA) / 2))
    vdim(msp, 0, gh, gw, 8, "CG %.2f +/-0.05" % CG_L)
    vdim(msp, oy, oy + mh, gw, 15, "LCM %.2f (ref)" % LCM_L)
    vdim(msp, va_y1 - VA * S, va_y1, gw, 22, "%.2f" % VA)
    vdim(msp, va_y1, gh, 0, -8, "%.2f" % ((gh - va_y1) / S))
    vdim(msp, 0, va_y1 - VA * S, 0, -16, "%.2f (chin)" % ((va_y1 - VA * S) / S))
    rdim(msp, gw - CG_R * S, gh - CG_R * S, CG_R * S, 45, "R%.1f x4" % CG_R)
    # side view (section) to the right
    sx = gw + 45
    rect(msp, sx, gh - CG_T * S, sx + 6.0, gh)                                 # glass seen edge-on (symbolic width)
    rect(msp, sx + 0.5, gh - (CG_T + LCM_T) * S, sx + 5.5, gh - CG_T * S, "HIDDEN")
    vdim(msp, gh - CG_T * S, gh, sx + 6, 5, "CG %.2f +/-0.05" % CG_T)
    vdim(msp, gh - (CG_T + LCM_T) * S, gh, sx + 6, 14, "total %.2f +/-0.20" % (CG_T + LCM_T))
    note(msp, sx - 4, gh + 12, "SECTION (edge view, 3:1)", 2.0)
    note(msp, 0, gh + 32, "FRONT VIEW, 3:1  (viewed from the glass side)", 2.4)
    notes(msp, 0, -12 * S - 12, [
        "NOTES",
        "1. Base module: Huadi HD085019C12 (0.85in 128x128 IPS, ST7735P3 + CST816D, integrated touch & display).",
        "   Only the cover glass (CG) changes.  Everything inside the LCM outline, the FPC and the pinout stay as drawn by Huadi.",
        "2. CG: 1.10 mm chemically strengthened glass (AGC Dragontrail / Corning GG3 or equivalent), surface hardness >= 6H,",
        "   anti-fingerprint (AF) coating on the outer face.  Outline %.2f x %.2f, corner R%.1f, all 4 sides overhang the LCM by 1.5." % (CG_W, CG_L, CG_R),
        "3. CG top edge: 2.5D polish, OR a C0.20 x 45 deg chamfer.  Edges ground, no chips.  The glass sits FLUSH in an aluminium pocket,",
        "   so the outline tolerance is +/-0.05 and the thickness tolerance +/-0.05.",
        "4. Black mask (BM) printed on the CG rear over the whole area except the VA window (%.2f x %.2f, corner R0.3), window position +/-0.10." % (VA, VA),
        "   Mask colour: deep black, matte or gloss to match the sample.  The mask must be opaque over the 1.5 mm overhang (it hides the adhesive ledge).",
        "5. Touch sensor (G+F) laminated to the CG rear with full-area OCA (0.18).  Touch active area = VA.",
        "6. Rear side of the LCM: black plastic + steel bracket as the standard part.  No tape on the rear (we add a 0.5 mm Poron pad).",
        "7. Ship flat (FPC not folded).  Protective film on the CG front face.",
        "8. A 0.15 mm steel ground tab on the FPC as the standard part.  Backlight: 1 white LED, VF 2.8-3.0 V @ 20 mA.",
    ], 1.8)
    title_block(msp, 0, -12 * S - 12 - 13 * 1.8 * 1.7 - 30, 190, "Custom cover glass - integrated touch display 0.85in",
                "VLT-DISP-085-CG  (HD085019C12 variant)", "CG strengthened glass 1.10", "AF coat, black mask", "3:1")
    save(doc, "display_HD085019C12_custom_cover_glass", (18, 16))


# ---------------------------------------------------------------- 2. plate
def draw_plate(keys):
    p = parts.plate(keys)
    sec = section(p, -0.75)
    # a) bare cut file, 1:1, nothing but the outline
    doc = new_doc(); msp = doc.modelspace()
    add_edges(msp, sec)
    doc.header["$INSUNITS"] = 4
    os.makedirs(OUT, exist_ok=True)
    doc.saveas(os.path.join(OUT, "plate_cut_1to1.dxf"))
    # b) dimensioned sheet
    doc = new_doc(); msp = doc.modelspace()
    add_edges(msp, sec)
    hdim(msp, 0, KEYS_W, PLATE_TAB_L, 10, "%.3f (16.5u)" % KEYS_W)
    vdim(msp, -KEYS_H, 0, KEYS_W, 12, "%.3f (6.5u)" % KEYS_H)
    vdim(msp, 0, PLATE_TAB_L, KEYS_W + 2, 4, "%.1f" % PLATE_TAB_L)
    for xt in PLATE_TAB_X:
        hdim(msp, 0, xt, -KEYS_H - PLATE_TAB_L, -8 - 6 * PLATE_TAB_X.index(xt), "%.2f" % xt)
    hdim(msp, PLATE_TAB_X[0] - PLATE_TAB_W / 2, PLATE_TAB_X[0] + PLATE_TAB_W / 2, PLATE_TAB_L, 4, "%.0f" % PLATE_TAB_W)
    cx, cy = keys[0][0], keys[0][1]
    hdim(msp, cx - 7, cx + 7, cy + 7, 5, "14.00 typ")
    hdim(msp, 0, cx, 0, 18, "%.3f (first key centre)" % cx)
    vdim(msp, cy, 0, 0, -14, "%.3f" % -cy)
    note(msp, 0, -KEYS_H - 34, "PLATE  -  1.5 mm 6061-T6 aluminium (or 1.5 PC / 1.6 FR4 / CF), bead-blast + anodise.", 2.6)
    notes(msp, 0, -KEYS_H - 40, [
        "81 x MX cutouts 14.00 x 14.00 (+0.05/-0) at the key centres of VLT-layout.json (16.5u x 6.5u grid, origin = top-left of Esc).",
        "Stabiliser cutouts 6.65 x 12.3 at +/-11.9 (2u, 2.25u) and +/-50.0 (6.25u) - Cherry plate-mount spec, verify against the stabiliser datasheet.",
        "Encoder: 8.0 dia hole at (%.2f, %.2f).   22 x 3.1 dia holes = M2 self-clinch standoffs (PEM SO-M2-x) for the PCB, pattern of the current VLT PCB." % (ENC_CX, -ENC_CY),
        "8 gasket tabs 20 x %.1f on the back and front edges (Poron 20 x 4 x 2 both faces).  6 edge notches %.1f x %.1f for the ball-catch skirt tabs." % (PLATE_TAB_L, BC_TAB_W + 1.5, BC_PLATE_NOTCH),
        "Slot 4 x 76 under the light bar (x %.1f) and slot 10 wide to the right edge at y %.1f for the display flex." % (BAR_CX, -ISL_CY),
        "Use plate_cut_1to1.dxf for cutting; this sheet is for reference.",
    ], 2.0)
    title_block(msp, 180, -KEYS_H - 92, 134, "Plate - gasket mount, 81 keys + encoder", "VLT-C3-PLATE", "6061-T6 1.5 mm", "bead blast + anodise", "1:2")
    save(doc, "plate_drawing", (22, 11))


# ---------------------------------------------------------------- 3. top case
def draw_top_case(tc):
    doc = new_doc(); msp = doc.modelspace()
    add_edges(msp, section(tc, TOP_Z - 0.05))                   # top surface: opening, islands, light channels
    add_edges(msp, section(tc, BC_Z), "HIDDEN")                 # z = -5: skirt tabs + gasket pockets, dashed
    hdim(msp, OX0, OX1, OY1, 10, "%.2f" % W)
    vdim(msp, OY0, OY1, OX1, 12, "%.2f" % D)
    hdim(msp, OX0, -CLR, OY1, 4, "%.1f" % (BEZEL - CLR))
    vdim(msp, -(6.25 * U + CLR), OY0, OX0, -6, "%.2f" % (-(OY0) - 6.25 * U - CLR))
    vdim(msp, -(KEYS_H + CLR), OY0, 13.125 * U + 30, -6, "%.2f" % (-(OY0) - KEYS_H - CLR))
    hdim(msp, 13.125 * U, OX1, OY0, -12, "%.2f (arrow step)" % (OX1 - 13.125 * U))
    # island + bar
    hdim(msp, ISL_X0, KEYS_W + CLR, ISL_Y0, -4, "%.2f" % (KEYS_W + CLR - ISL_X0))
    vdim(msp, ISL_Y0, ISL_Y1, ISL_X0 - 2, -3, "%.2f" % (ISL_Y1 - ISL_Y0))
    hdim(msp, CG_CX - (CG_L + 2 * CG_GAP) / 2, CG_CX + (CG_L + 2 * CG_GAP) / 2, ISL_Y1, 4, "%.2f glass opening" % (CG_L + 2 * CG_GAP))
    vdim(msp, ISL_CY - (CG_W + 2 * CG_GAP) / 2, ISL_CY + (CG_W + 2 * CG_GAP) / 2, OX1, 8, "%.2f" % (CG_W + 2 * CG_GAP))
    hdim(msp, 0, CG_CX, OY1, 22, "%.2f glass centre" % CG_CX)
    vdim(msp, ISL_CY, 0, OX1, 28, "%.2f" % -ISL_CY)
    hdim(msp, BAR_CX - BAR_W / 2, BAR_CX + BAR_W / 2, 0, 16, "%.1f bar" % BAR_W)
    hdim(msp, 0, BAR_CX, OY1, 28, "%.2f (15.25u)" % BAR_CX)
    rdim(msp, OX1 - CORNER_R, OY1 - CORNER_R, CORNER_R, 45, "R%.0f x4" % CORNER_R)
    notes(msp, OX0, OY0 - 24, [
        "TOP CASE  -  CNC 6061-T6, %.1f tall ring (z %.1f to %.1f relative to the plate top).  Bezel %.0f on all sides at the top surface." % (TOP_Z - SEAM_Z, SEAM_Z, TOP_Z, BEZEL),
        "Outer top edge C%.1f.  Keycap window = key area + %.1f per side, with a 0.25u step for the dropped arrow cluster." % (TOP_CHAMFER, CLR),
        "Light bar %.1f wide x 3.0 thick between the main block and the nav column: two flush channels %.1f x %.1f deep for frosted PC inserts, %.1f light slot below." % (BAR_W, BAR_CHAN_W, BAR_CHAN_D, BAR_SLOT_W),
        "Display island %.2f x %.2f, 4.5 thick, joined to the right bezel; through opening %.2f x %.2f R%.2f for the cover glass (0.15 gap/side, glass flush)." % (KEYS_W + CLR - ISL_X0, ISL_Y1 - ISL_Y0, CG_L + 2 * CG_GAP, CG_W + 2 * CG_GAP, CG_R + CG_GAP),
        "Wall notch under the island (x %.1f to %.1f, %.0f wide, z %.1f to %.1f) for the cartridge flange; 2 x M2 blind tapped 3.5 deep in its ceiling." % (KEYS_W + CLR, CART_NOTCH_X1, CART_NOTCH_W, SEAM_Z, ISL_Z0),
        "8 gasket pockets (20.6 wide x 5.6 deep, z %.1f to +1.5) on the back and front walls.  6 skirt tabs %.0f x 1.5 x 6 (dashed) with a 1.0 deep spherical dimple R1.5 at z %.1f." % (SEAM_Z, BC_TAB_W, BC_Z),
        "Plate relief: the bezel underside is 0.3 above the plate everywhere inside the key area + %.1f." % CLR,
    ], 2.0)
    title_block(msp, 170, OY0 - 24 - 7 * 2.0 * 1.7 - 28, 150, "Top case", "VLT-C3-TOP", "6061-T6", "bead blast + anodise / PVD", "1:2")
    save(doc, "top_case_drawing", (22, 12))


# ---------------------------------------------------------------- 4. bottom case (plan + underside in the desk frame)
def draw_bottom_case(bc):
    doc = new_doc(); msp = doc.modelspace()
    add_edges(msp, section(bc, BC_Z))                           # z = -5: cavity, bosses, plunger holes, USB pocket
    hdim(msp, OX0, OX1, OY1, 10, "%.2f" % W)
    vdim(msp, OY0, OY1, OX1, 12, "%.2f" % D)
    hdim(msp, -CLR, KEYS_W + CLR, OY1, 4, "%.2f cavity" % (KEYS_W + 2 * CLR))
    vdim(msp, -(KEYS_H + CLR), CLR, OX1, 6, "%.2f cavity" % (KEYS_H + 2 * CLR))
    for i, xc in enumerate(BC_BACK_X):
        hdim(msp, 0, xc, OY1, 16 + 6 * i, "%.0f ball catch" % xc)
    vdim(msp, BC_LEFT_Y, 0, OX0, -8, "%.0f ball catch (left)" % -BC_LEFT_Y)
    vdim(msp, BC_RIGHT_Y, 0, OX1, 20, "%.0f ball catch (right)" % -BC_RIGHT_Y)
    hdim(msp, 0, USB_CX, OY0, -8, "%.2f USB-C" % USB_CX)
    hdim(msp, POGO_CX - POGO_SCREW[0], POGO_CX + POGO_SCREW[0], POGO_CY - 10, -4, "%.0f pogo bosses" % (2 * POGO_SCREW[0]))
    vdim(msp, POGO_CY, 0, POGO_CX + 30, 6, "%.0f" % -POGO_CY)
    # underside, seen from below (desk frame), mirrored in x so it reads like a bottom view
    bcd = bc.rotate((0, OY0, TOP_Z), (1, OY0, TOP_Z), TILT)          # plate frame → desk frame
    us = section(bcd, TOP_Z - H_FRONT + 0.4)                          # 0.4 above the bottom face: ring, weight pocket, bumpons
    ub = us.val().BoundingBox()
    dy = (OY0 - 30) - ub.ymax                                         # place the underside view below the plan view
    add_edges(msp, us, "OUTLINE", dx=0, dy=dy)
    note(msp, OX0, OY0 - 26, "UNDERSIDE (desk frame, looking at the bottom face; the wedge is %.1f at the front and %.1f at the back)" % (H_FRONT, H_BACK), 2.4)
    hdim(msp, OX0 + RING_IN, OX0 + RING_IN + 0.001, ub.ymin + dy, -6, "ring centre %.1f from the edge" % RING_IN)
    dy = ub.ymin + dy
    notes(msp, OX0, dy - 12, [
        "BOTTOM CASE  -  CNC 6061-T6.  Walls perpendicular to the plate, bottom face at %.0f deg; floor %.1f thick parallel to the desk." % (TILT, FLOOR_T),
        "Cavity = key area + %.1f.  6 x M3 tap-drill holes (2.5 dia x 7 deep) at z %.1f for M3 x 6 spring ball plungers (ball 2.0, ~3 N)." % (CLR, BC_Z),
        "8 gasket pockets 20.6 x 5.6, floor at z -3.0.  USB-C: plug window %.1f x %.1f R%.1f at z %.1f through the back wall + board pocket 27 x 4.4." % (USB_PLUG_W, USB_PLUG_H, USB_PLUG_R, USB_PORT_Z),
        "Bosses 5 dia, M2 tapped x 5: USB board top at z %.1f (2x), pogo board top at z %.1f (4x)." % (USB_BOARD_TOP_Z - BOARD_T, POGO_BOARD_TOP_Z - BOARD_T),
        "Underside: underglow ring groove %.1f wide x %.1f deep, centreline %.1f from the edge, R4 corners; through slot %.1f wide on the straights (stops %.0f from the corners);" % (RING_W, RING_D, RING_IN, RING_SLOT_W, RING_CORNER_STOP),
        "  5.0 x 1.2 channel on the inner floor over each slot for the LED bars.  Weight pocket (octagon %.0f x %.0f, C%.0f) %.1f deep + 4 x 3.4 dia through for M3." % (WEIGHT_L + 2 * WEIGHT_CLR, WEIGHT_W + 2 * WEIGHT_CLR, WEIGHT_CHAMFER, WEIGHT_POCKET_D),
        "  4 x 10 dia x 1.0 bumpon pockets %.0f from the corners.  Outer bottom edge C%.1f." % (BUMPON_IN, BOTTOM_CHAMFER),
    ], 2.0)
    title_block(msp, 130, dy - 12 - 7 * 2.0 * 1.7 - 30, 190, "Bottom case", "VLT-C3-BOTTOM", "6061-T6", "bead blast + anodise / PVD", "1:2")
    save(doc, "bottom_case_drawing", (22, 22))


# ---------------------------------------------------------------- 5. side profile (desk frame)
def draw_side(tc, bc):
    doc = new_doc(); msp = doc.modelspace()
    comp = cq.Workplane().add(cq.Compound.makeCompound([tc.val(), bc.val()]))
    d = comp.rotate((0, OY0, TOP_Z), (1, OY0, TOP_Z), TILT)                   # desk frame
    d = d.rotate((0, 0, 0), (0, 0, 1), -90).rotate((0, 0, 0), (1, 0, 0), -90)  # new x = old y, new y = old z, new z = old x
    sec = section(d, 100.0)                                                   # x = 100 in the original
    add_edges(msp, sec)
    for extra in (parts.plate(key_centres_mm(KLE) + [(ENC_CX, ENC_CY, 1.0, "ENC")]), parts.pcb()):
        e = extra.rotate((0, OY0, TOP_Z), (1, OY0, TOP_Z), TILT).rotate((0, 0, 0), (0, 0, 1), -90).rotate((0, 0, 0), (1, 0, 0), -90)
        add_edges(msp, section(e, 100.0), "HIDDEN")
    b = sec.val().BoundingBox()
    hdim(msp, b.xmin, b.xmax, b.ymin, -8, "%.2f (bottom face, desk frame)" % (b.xmax - b.xmin))
    vdim(msp, b.ymin, b.ymin + H_FRONT, b.xmin, -8, "%.1f front" % H_FRONT)
    vdim(msp, b.ymin, b.ymax, b.xmax, 8, "%.1f back" % H_BACK)
    note(msp, b.xmin, b.ymax + 8, "SIDE PROFILE at x = 100 (through a gasket tab and the front/back ball catches).  Typing angle %.0f deg.  Seam %.1f below the plate top." % (TILT, -SEAM_Z), 2.4)
    title_block(msp, b.xmin, b.ymin - 50, 150, "Side profile", "VLT-C3 assembly", "-", "-", "1:1")
    save(doc, "side_profile", (16, 9))


# ---------------------------------------------------------------- 6. weight + diffusers
def draw_weight_and_diffusers():
    doc = new_doc(); msp = doc.modelspace()
    hl, hw, c = WEIGHT_L / 2, WEIGHT_W / 2, WEIGHT_CHAMFER
    pts = [(-hl + c, -hw), (hl - c, -hw), (hl, -hw + c), (hl, hw - c), (hl - c, hw), (-hl + c, hw), (-hl, hw - c), (-hl, -hw + c)]
    msp.add_lwpolyline(pts, close=True, dxfattribs={"layer": "OUTLINE"})
    for sx, sy in WEIGHT_SCREWS:
        msp.add_circle((sx, sy), 1.25, dxfattribs={"layer": "OUTLINE"})
    hdim(msp, -hl, hl, hw, 8, "%.1f" % WEIGHT_L)
    vdim(msp, -hw, hw, hl, 8, "%.1f" % WEIGHT_W)
    hdim(msp, -hl, -hl + c, -hw, -6, "C%.0f x8" % c)
    hdim(msp, -80, 80, -hw, -12, "160.0")
    vdim(msp, -18, 18, -hl, -6, "36.0")
    note(msp, -hl, -hw - 22, "WEIGHT  -  %.1f thick, 4 x M3 blind tapped 3.2 deep from the top (inside) face.  Visible edge C1.0.  Stands %.1f proud of the case." % (WEIGHT_T, WEIGHT_T - WEIGHT_POCKET_D), 2.2)
    note(msp, -hl, -hw - 27, "Material options: brass (%.0f g), stainless 304 (%.0f g), copper (%.0f g), aluminium (%.0f g).  Finish: PVD (gold/black/rose), mirror polish, brushed, sandblast." % (
        WEIGHT_L * WEIGHT_W * WEIGHT_T * 8.5 / 1000 * 0.93, WEIGHT_L * WEIGHT_W * WEIGHT_T * 7.9 / 1000 * 0.93, WEIGHT_L * WEIGHT_W * WEIGHT_T * 8.9 / 1000 * 0.93, WEIGHT_L * WEIGHT_W * WEIGHT_T * 2.7 / 1000 * 0.93), 2.2)
    # diffusers below
    oy = -hw - 70
    rw, rh = W - 2 * (RING_IN - RING_W / 2) - 0.1, DL - 2 * (RING_IN - RING_W / 2) - 0.1
    rrect(msp, -rw / 2, oy - rh, rw / 2, oy, 3.95)
    rrect(msp, -rw / 2 + RING_W, oy - rh + RING_W, rw / 2 - RING_W, oy - RING_W, 1.05)
    hdim(msp, -rw / 2, rw / 2, oy, 8, "%.2f" % rw)
    vdim(msp, oy - rh, oy, rw / 2, 8, "%.2f" % rh)
    hdim(msp, -rw / 2, -rw / 2 + RING_W, oy - rh, -6, "%.1f" % RING_W)
    note(msp, -rw / 2, oy - rh - 16, "UNDERGLOW RING  -  frosted polycarbonate (or cast acrylic) %.2f thick, laser cut or CNC, flush in the %.1f deep groove.  Light enters through the %.1f slot behind it." % (RING_D - 0.05, RING_D, RING_SLOT_W), 2.2)
    oy2 = oy - rh - 40
    x = -rw / 2
    for ya, yb in BAR_SEGMENTS:
        L = ya - yb - 0.1
        rect(msp, x, oy2 - BAR_CHAN_W + 0.1, x + L, oy2)
        hdim(msp, x, x + L, oy2, 6, "%.2f" % L)
        x += L + 15
    vdim(msp, oy2 - BAR_CHAN_W + 0.1, oy2, -rw / 2, -6, "%.2f" % (BAR_CHAN_W - 0.1))
    note(msp, -rw / 2, oy2 - 14, "LIGHT BAR INSERTS  -  2 pcs frosted PC %.2f thick (flush in the %.1f deep channel), %.2f wide.  Edges polished.  Glued with UV adhesive or 0.1 PSA." % (BAR_CHAN_D - 0.02, BAR_CHAN_D, BAR_CHAN_W - 0.1), 2.2)
    title_block(msp, -hl, oy2 - 60, 150, "Weight + diffusers", "VLT-C3-WEIGHT / -RING / -BARS", "see notes", "see notes", "1:2")
    save(doc, "weight_and_diffusers", (16, 18))


# ---------------------------------------------------------------- 7. PCB outline reference (for the KiCad redesign)
def draw_pcb_reference(keys):
    doc = new_doc(); msp = doc.modelspace()
    rrect(msp, PCB_X0, PCB_Y1 - PCB_H, PCB_X0 + PCB_W, PCB_Y1, 1.0)
    for hx, hy in parts.pcb_holes_plate_frame():
        msp.add_circle((hx, hy), 1.55, dxfattribs={"layer": "OUTLINE"})
    for cx, cy, w, l in keys:
        if l == "ENC":
            msp.add_circle((cx, cy), 3.5, dxfattribs={"layer": "CENTER"})
        else:
            rect(msp, cx - w * U / 2 + 0.5, cy - U / 2 + 0.5, cx + w * U / 2 - 0.5, cy + U / 2 - 0.5, "CENTER")
    rect(msp, POGO_CX - 7, POGO_CY - 3, POGO_CX + 7, POGO_CY + 3, "ZONE")
    note(msp, POGO_CX - 7, POGO_CY - 6, "POGO PAD FIELD on the BOTTOM: 2 x 5 pads, 2.54 pitch, 1.8 dia, centre (%.2f, %.2f)" % (POGO_CX, -POGO_CY), 1.6)
    rect(msp, 302, ISL_CY - 4, 308, ISL_CY + 4, "ZONE")
    note(msp, 280, ISL_CY - 8, "DISPLAY FPC 12p 0.5mm, TOP side, flex enters from +x", 1.6)
    rect(msp, BAR_CX - 2, -78, BAR_CX + 2, -2, "ZONE")
    note(msp, BAR_CX - 40, -80.5, "LIGHT BAR LED ROW (x %.2f): 2020 LEDs facing up, y -3 to -77" % BAR_CX, 1.6)
    rect(msp, 306, ISL_CY - 5, PCB_X0 + PCB_W, ISL_CY + 5, "ZONE")
    hdim(msp, PCB_X0, PCB_X0 + PCB_W, PCB_Y1, 8, "%.1f" % PCB_W)
    vdim(msp, PCB_Y1 - PCB_H, PCB_Y1, PCB_X0 + PCB_W, 8, "%.1f" % PCB_H)
    hdim(msp, 0, PCB_X0, PCB_Y1, 3, "%.2f" % PCB_X0)
    vdim(msp, PCB_Y1, 0, 0, -3, "%.2f" % -PCB_Y1)
    notes(msp, PCB_X0, PCB_Y1 - PCB_H - 10, [
        "PCB OUTLINE REFERENCE  -  the current VLT PCB (310 x 123, R1, 22 holes) fits the v3 case as is.  Coordinates = plate frame (origin top-left of Esc, y up).",
        "For the redesign: keep the outline and holes; add the pogo pad field (bottom), move the display connector to the TOP side at the marked spot,",
        "add the LED row under the light bar, keep the area under the right bezel at y %.1f +/-5 free of tall parts (display flex comes down there)." % -ISL_CY,
        "USB-C moves to the daughterboard (back wall, x %.2f).  Encoder stays at (%.2f, %.2f).  No through-hole switch pins (hall sensors), so the bottom is free." % (USB_CX, ENC_CX, -ENC_CY),
    ], 2.0)
    title_block(msp, 170, PCB_Y1 - PCB_H - 10 - 4 * 2 * 1.7 - 28, 150, "PCB outline reference", "VLT PCB rev 4 (to do)", "FR4 1.6", "-", "1:2")
    save(doc, "pcb_outline_reference", (22, 11))


if __name__ == "__main__":
    keys = key_centres_mm(KLE) + [(ENC_CX, ENC_CY, 1.0, "ENC")]
    draw_display()
    draw_plate(keys)
    tc = geom.top_case(); bc = geom.bottom_case()
    draw_top_case(tc)
    draw_bottom_case(bc)
    draw_side(tc, bc)
    draw_weight_and_diffusers()
    draw_pcb_reference(keys)
    print("drawings done")
