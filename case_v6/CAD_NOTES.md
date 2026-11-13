# VLT case: light-bar options — CAD notes

Status, 2026-11-11. The case keeps the existing contour exactly (the `CASE_UPPER` / `CASE_LOWER`
of `blender/vlt_scene.blend`: 326 × 142, 7.6° underside). Nothing below changes the outline. These
are options being compared as renders (`blender/promo/scripts/showcase/`, see `variants.py`);
none is drawn in CAD or checked for machining yet.

**Rejected, do not bring back:** a chin or any part that sticks out past the contour; a PVD
weight bar; feet or other underside features in the renders.

Coordinates: mm, plate level, origin at the centre of the key field, +y to the back, +z up.
Top deck z = 15, top/bottom seam z = 7.5, front face y = −71.

## Accent bars between Backspace and Home (top case)

The two existing slots at x = 133.35: long bar y −19 … 38, short bar y 45.4 … 59.4, 3.0 wide.
Variants change only the ends: round (as now), square, or tapering to a single point over
4.5 mm (1.5 × the width). The slot is cut to the same outline, 0.08 clearance.

## Front light bar (bottom case)

A real part, built the same way as the accent strip:

- A slot cut through the front wall of the bottom case, 270 × 2.6, centred at z = 1.3, so it
  stops about where the right arrow key begins on each side. Its ends taper to a single point
  over 6.2 mm (2.4 × the width). A square-ended version is also rendered.
- A frosted plastic bar sits in the slot from inside, flush with the front face (0.06 recessed),
  with a 274 × 4.4 flange behind the wall to locate and bond it.
- Behind it, an LED strip: the renders use 90 LEDs at about 2.9 mm pitch, 4 mm behind the
  bar. Forty LEDs at 2.4 mm behind showed as separate dots, so keep the pitch fine or the
  distance long.
- The renders cut a 276 × 5.2 pocket 6 mm deep behind the wall for the flange and the strip,
  because the wall is thicker than its nominal 2.7 mm in places. Measure the real wall and
  the gasket ledge above it (z ≥ 3.9) before fixing these numbers.

## Edge cutouts (alternative to the bar)

Pointed diffusers, 2.4 wide, 3.6 above the bottom edge and parallel to it: three on the front
(52, 160 and 52 long) and two on each side (about 50 and 38 long). In the renders they are
simple glowing inserts 1.4 deep; the LEDs behind them are not designed.

## Still wanted, not modelled in the current renders

- Ball catch between the case halves.
- A daughterboard with 8 pogo pins that also carries power and data for case-mounted LEDs.
  Proposed pins: GND, D−, D+, GND, VBUS, VBUS, LED_5V (switched by the PCB's LED gate),
  LED_DATA. CC resistors and ESD parts on the daughterboard.
  **USB High Speed over pogo pins is unproven**: test on a prototype; the fallback is a short
  FPC for USB and pogo pins for power and LEDs only.
- Case LED load: about 90 LEDs behind the front bar at 8.4 mA each (the HoneBright part) is
  about 0.76 A at full white, on top of the per-key LEDs. The dev board already browns out at
  high LED brightness on USB power, so the case zone needs its own brightness cap.
- Firmware and Nova: the case LEDs are new LEDs after the existing chain; LED counts, zone
  tables, the SignalRGB plugin's indices and Nova's zone list change. The screen's Lighting
  menu already has an "Ambient" zone they can live in.
