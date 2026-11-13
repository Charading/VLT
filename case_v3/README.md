# VLT case v3 — CNC aluminium, flush touch display, ball catch, gasket mount, underglow

Rev A, 2026-11-05. Generated from the parametric CadQuery model in this folder; nothing has been machined or
test-fitted yet. Every number below comes from `params.py`; change a number there, run `build.py` and
`drawings.py`, and every STEP, STL, DXF and PDF is regenerated.

## What is in `out/`

| Folder | Contents |
|--------|----------|
| `out/step/` | one STEP per part + `VLT_case_v3_assembly.step` (all parts, positioned, coloured). Send these to the CNC shop. |
| `out/stl/` | the same parts as STL for quick viewing (plus the assembly). Not for manufacturing. |
| `out/dxf/` | dimensioned sheets: `display_HD085019C12_custom_cover_glass`, `top_case_drawing`, `bottom_case_drawing`, `side_profile`, `plate_drawing`, `weight_and_diffusers`, `pcb_outline_reference`, and `plate_cut_1to1` (bare cut file). |
| `out/pdf/` | the same sheets as PDF (what you actually e-mail). |
| `out/png/` | `dwg_*.png` previews of the sheets and Blender renders (`iso_front_right`, `display_closeup`, `bottom_iso`, `exploded`, `top_case_underside*`, `bottom_case_interior*`, `side_right`, `front`, `top*`). |
| `out/build_report.json` | bounding boxes, volumes and the pairwise interference check (all pairs 0 mm³ except a 0.9 mm³ corner-radius artefact between cartridge and island). |

Parts: `top_case`, `bottom_case`, `plate`, `cartridge` (display carrier), `cover_glass` (the custom glass alone),
`display_module` (glass + LCM + flex, for fit), `weight`, `bar_inserts` (2 frosted PC strips), `underglow_ring`
(frosted PC frame), `led_bars` (4 LED strips), `pcb` (the current VLT PCB as a reference slab), `usb_board`,
`pogo_board`, `gaskets`, `ball_plungers`, `knob`, `keycaps_preview`.

## Regenerate

```bash
py -3.13 -m venv cadenv && cadenv/Scripts/python -m pip install -r requirements.txt
cadenv/Scripts/python build.py          # STEP + STL + interference report (~10 s)
cadenv/Scripts/python drawings.py       # DXF + PDF + PNG sheets (~30 s)
"C:/Program Files/Blender Foundation/Blender 4.3/blender.exe" -b --python render.py   # Cycles CPU renders (~4 min)
```

Frames: the model is built in the **plate frame** — x to the right, y towards the back (KLE y negated), z up,
z = 0 at the top of the plate, origin at the top-left corner of Esc. The bottom face and everything on it live in
the **desk frame** (the plate frame tilted by 6°). Walls are perpendicular to the plate, so the case is a tilted
block like a Keycult / Zoom: every wall has one thickness over its full height.

## The design in numbers

| | |
|--|--|
| Layout | 81 keys + encoder, 16.5u × 6.5u, from `hardware/VLT/VLT-layout.json` (arrow cluster dropped 0.25u, nav column 0.5u right of the main block) |
| Outer size | 330.3 × 139.8 mm, R3 vertical corners, bezel 8.0 on every side at the top surface |
| Typing angle / heights | 6°, 21.5 mm front, 36.2 mm back (desk to top of bezel) |
| Top case | 9.5 tall ring (z −2.0 … +7.5): the bezel top is 7.5 above the plate, hiding the switches; C1.0 outer top edge |
| Seam | 2.0 below the plate top, parallel to the top surface |
| Bottom case | floor 4.0 parallel to the desk, C1.2 bottom edge, walls 7.4 |
| Plate | 1.5 mm, 314.325 × 123.825 (= key area), 8 gasket tabs 20 × 4.5 |
| PCB | the current 310 × 123 board fits unchanged in position; see "PCB changes" for what the redesign needs |
| Front bezel | 12.2 mm along the main rows, 7.4 at the arrow cluster (the keycap window steps 0.25u at x = 250) |
| Mass | aluminium 950 g (top 188, bottom 665, plate 91, cartridge 3) + brass weight 368 g ≈ 1.3 kg bare case |

Vertical stack (plate frame):

| z | what |
|---|---|
| +7.5 | top of bezel, top of the cover glass (flush), top of the light-bar inserts (flush) |
| +6.4 … +7.5 | cover glass 1.10 |
| +6.2 | cartridge ledge (0.2 VHB tape under the glass overhang) |
| +4.5 … +7.5 | light bar (3.0 thick bridge) |
| +3.0 … +7.5 | display island (4.5 thick bridge) |
| +1.5 … +3.0 | cartridge flange, under the island, screwed up into the wall |
| +0.3 | underside of the bezel over the plate (relief, never touches the plate) |
| 0 … −1.5 | plate; top gasket 0 … +1.5, bottom gasket −1.5 … −3.0 (Poron 2.0 compressed to 1.5) |
| −2.0 | seam |
| −2.0 … −8.0 | top-case skirt tabs (ball catch); plunger axis at −5.0 |
| −5.0 … −6.6 | PCB |
| −7.5 | USB-C port axis (board top −8.6) |
| −13.0 | pogo board top (6.0 mm spring pins, 0.4 compression against the PCB underside) |
| −10.7 (front) … −23.7 (back) | cavity floor (tilted) |
| −13.9 (front) … −28.7 (back) | desk |

## Subsystems

### Display — flush cover glass, rotated module, carrier cartridge

The 0.85" Huadi module (HD085019C12, ST7735P3 + CST816D, integrated touch) has a 17.58 × 20.82 LCM whose standard
cover glass overhangs it by only 0.5 mm — not enough ledge to bond a glass into a pocket. The custom glass overhangs
by **1.5 mm on all four sides: 23.8 × 20.6 × 1.10, R1.0, black mask with a 15.61 window, 2.5D or C0.2 top edge**.
That is the only change for the panel maker; the LCM, FPC and pinout stay as drawn by Huadi. The sheet
`display_HD085019C12_custom_cover_glass` is drawn in their orientation (FPC at the bottom) with the notes they need.

Between PgDn and → there are 24.6 mm free (keycap edge to keycap edge). The module is **turned 90°** so its 20.82
length runs along x and the FPC leaves towards the right bezel, where there is room; the short side (17.58 + 2 × 1.5
= 20.6) spans the gap, leaving a 1.2 mm aluminium frame above and below the glass, 0.8 mm to each keycap. The
island joins the right bezel and the glass runs 1.1 mm into the bezel surface. The firmware rotates the image
(MADCTL MV/MX/MY) and swaps the touch axes — the active area is square, so nothing is lost. The AA sits 2.74 from
the glass edge on the ↑ side and 5.47 from the FPC-side edge (a short "chin" of black glass).

The glass is **not bonded to the case**. It sits in a through opening in the island (24.1 × 20.9, 0.15 gap per
side) and is bonded with 0.2 mm VHB to the ledge of the **cartridge**: a 24.0 × 20.8 × 3.2 tray that fills the
opening from below, has a 21.3 × 18.0 pocket for the module (0.6 floor, room for a 0.5 Poron pad behind the
backlight), an 11 mm slot for the flex on the +x end, and a 1.5 mm flange that reaches 5.4 mm into a notch in the
right wall where **2 × M2 screws** go up into blind holes in the wall. To service the display you flip the top case,
undo two screws and the glass + module come out as one unit. The flex drops down the wall notch, through a 10 mm
slot in the plate edge, and folds into a 12-pin FPC connector on the **top** of the PCB at x ≈ 302…308 (flex entering
from +x). The 35 mm flex has ~15 mm of spare length; the top case can be lifted and the flex unplugged.

### Light bar (the signature strip)

A 6.0 × 3.0 bar in the 0.5u gap between the main block and the nav column, from the back bezel down to the display
island (keycap clearance 2.1 mm each side, 4.7 mm to the ↑ cap). Two flush channels 3.5 × 1.2 take frosted PC
inserts (21.9 and 55.4 long — the split between the F-row and the number row echoes the current render), each over a
2.5 mm light slot. The plate has a 4 × 76 slot and the PCB gets a row of 2020 LEDs at x = 290.5, y −3 … −77.

### Underglow ring

A 3.0 × 2.0 groove around the bottom face, centreline 10.0 from the edge (R4 corners), filled flush with a frosted
PC frame (313.2 × 123.5). Under each straight run a 2.0 through slot (stopping 18 mm from the corners) opens into a
5.0 × 1.2 channel on the cavity floor that locates a 4 mm LED bar (LEDs facing down). Light hits the desk under the
board and spreads outward; the brass weight sits inside the ring. The LED bars connect to the pogo board (or the
PCB) — not modelled.

### Ball catch (no visible screws)

Six **M3 × 6 spring ball plungers** (steel ball Ø2, ~3 N) screw horizontally into tap-drilled holes in the bottom
case walls at z = −5: back wall at x 102.4 and 183.35 (in the F4|F5 and F8|F9 0.25u gaps, so the plate notch does
not thin the web above a cutout), front wall at x 90 and 230, left wall at y 62, right wall at y 114 (beside →, clear
of the display notch and the nav-column cutouts). The top case has six 8 × 1.5 × 6 **skirt tabs** hanging inside the
cavity wall with a 1.0-deep R1.5 spherical dimple each. The plate has 9.5 × 1.8 edge notches under the tabs. Force
is set by how far each plunger is screwed in (Monsgeek M1 V5 style). Press the top case on; lift at a corner to
remove.

### Gasket mount

8 plate tabs 20 × 4.5 (4 back, 4 front at x 40, 135, 200, 274.3), each sandwiched between two Poron strips
20 × 4 × 2. Pockets 20.6 wide × 5.6 deep straddle the seam: ceiling in the top case at +1.5, floor in the bottom
case at −3.0; the wall keeps a 1.8 mm skin behind each pocket. Tab 135/200 spacing leaves the USB pocket clear.

### Weight

Stretched octagon 200 × 56 × 4.0 (C12 corners), brass 368 g (stainless 329 g, copper 371 g), sitting in a 3.0 pocket
on the bottom face so it stands 1.0 proud with a C1.0 visible edge, held by 4 × M3 from inside (blind tapped 3.2 in
the weight; 3.4 holes through the 1.0 floor left under the pocket). Finish freely: PVD, mirror, brushed, blasted.

### Daughterboards and PCB changes

- **USB-C board** 25 × 14 at the back wall centre (x 157.16): its back edge sits 4.4 mm inside a wall pocket so the
  receptacle lip reaches the outer face; plug window 9.6 × 3.6 R1.5 at z −7.5; 2 × M2 bosses (board top −8.6).
- **Pogo board** 40 × 18 at (157.16, −20): 2 × 5 spring pins 2.54 pitch pointing up at pads on the PCB underside;
  4 × M2 bosses (board top −13.0). The 10-pin 0.5 FFC between the two boards is not modelled.
- **PCB** (sheet `pcb_outline_reference`, KiCad-importable): keep the 310 × 123 outline and 22 holes; add the
  2 × 5 pad field on the bottom at (157.16, −20); move the display connector to the top side at x 302…308,
  y ±4 around −92.87, flex entering from +x; add the light-bar LED row; keep y −98…−88 at the right edge free of tall
  parts (flex path); delete the on-board USB and route it through the pogo field. Hall sensors have no through pins,
  so the underside is free.

## Hardware BOM (per keyboard)

| Qty | Part |
|----:|------|
| 6 | M3 × 6 spring ball plunger, Ø2 steel ball, 2–4 N (generic "M3*6 ball spring plunger", GN 614-M3 class) |
| 16 | Poron gasket strip 20 × 4 × 2 (50 Shore 00), PSA one side |
| 22 | M2 self-clinch standoff 3.5 mm (PEM SO-M2-3.5 class) in the plate + 22 × M2 × 4 screws for the PCB |
| 2 | M2 × 5 pan head (cartridge flange into the wall) |
| 6 | M2 × 5 pan head (USB board 2, pogo board 4) |
| 4 | M3 × 6 button head (weight, from inside) |
| 10 | spring pin 2.54 pitch, 6.0 mm nominal, 1 mm travel (pogo board) |
| 1 | custom cover-glass display module VLT-DISP-085-CG (Huadi, from the sheet) |
| 1 | 3M VHB 0.2 × 1.3 wide frame cut to the cartridge ledge; 1 Poron 0.5 pad 20 × 17 behind the module |
| 2 | frosted PC strips 3.4 × 1.18 (21.9 and 55.4 long) |
| 1 | frosted PC ring 313.2 × 123.5 × 1.95, 3.0 wide |
| 4 | LED bars 4 × 1.0 (2020 WS2812 class), lengths 294 (front/back) and 105 (sides) |
| 4 | bumpons Ø10 × 2 |

## Assembly order

1. Bottom case: screw in the six plungers (set to ~2 turns short of flush, tune later), drop the LED bars into the
   floor channels, press the frosted ring into the bottom groove (UV adhesive or 0.1 PSA), bolt the weight on from
   inside, mount the USB and pogo boards, connect the FFC.
2. Plate + PCB: standoffs in the plate, switches, PCB screwed on, gaskets stuck to both faces of the eight tabs.
3. Top case upside down: slide the cartridge (with the bonded glass + module) up into the island and the wall
   notch, two M2 screws; press the two PC strips into the bar. Plug the flex into the PCB connector.
4. Lay the plate assembly into the bottom case (tabs into pockets), press the top case on until the balls click.

## Where the look comes from

- Keycult-style single sharp chamfer on the top edge, walls square to the top, seam low and parallel to the top,
  a heavy proud brass weight framed by a light line — the bottom is the showpiece.
- Zoom75-class proportions: 22 mm front height, 6°, 8 mm bezels.
- Neo-style ball catch sized for narrow bezels (8 mm wide tabs, M3 plungers); Monsgeek-style force tuning by screw depth.
- Your own render: the knob at the top right, the light strip split across the F-row gap, the screen above →.

## Open points before machining

1. **Keycap profile check**: all clearances assume an 18.3 mm keycap base. With a wider profile (some MT3/SA at 18.4)
   the island frame (0.8 to PgDn and →) and the bar (2.1) still clear, but check your set.
2. **Ball-catch force**: start with 3 N plungers; the tabs are 1.5 thick 6061 — if the clicks feel harsh, deepen the
   dimple to 1.2 or drop to 2 N plungers.
3. **Glass tolerance**: the 0.15 gap per side needs ±0.05 on the glass and ±0.05 on the island opening — tell the CNC
   shop the opening is a datum feature.
4. **Flex length / connector**: verify the 35 mm flex reaches the connector position once the real PCB layout is
   known; a 12-pin board-to-board or pogo link for the display would make the top case fully tool-free.
5. **Firmware**: MADCTL rotation + touch axis swap for the 90° module (see memory `ctp-touch-mapping`).
6. **Stabiliser cutouts** are generic Cherry plate-mount; confirm against the stabilisers you buy.
7. The underglow LED bars and their harness are specified, not designed; the pogo board gets the extra pins.
8. Blender renders use plain boxes for keycaps; the real look needs your `vlt_scene.blend` materials.
