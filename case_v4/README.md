# VLT case v4 — sculpted CNC case, three styled variants

Rev A, 2026-11-06. Builds on v3 (`../case_v3`, same frames, plate, display cartridge, daughterboards). v4 changes
the top case to **one window per key group** (the Shego75 scheme: bars of aluminium between the F-row groups, the
main block, the nav column, the arrow cluster and the screen), moves the seam down to z = −6 so the plate assembly
hangs in the top case, and sculpts the outer skin per variant. Everything is generated: `v4.py` (styles + geometry),
`build_v4.py` (STEP/STL per style + interference report), `render_v4.py` (Blender), `compare.py` (contact sheet).

```bash
cadenv/Scripts/python build_v4.py all            # out/<style>/step, out/<style>/stl, build_report.json
"C:/Program Files/Blender Foundation/Blender 4.3/blender.exe" -b --python render_v4.py -- ore   # out/ore/png
cadenv/Scripts/python compare.py                 # out/compare.jpg
```

## Shared skeleton (all variants)

| | |
|--|--|
| Windows | key cells grown by 0.57 mm per side, R1.2 corners; bars 3.6 mm wide in every 0.25u gap, 8.4 mm in the 0.5u gap. Groups: Esc, F1–F4, F5–F8, F9–F12, Del, main block (stepped at the right: 15u / 14u / 13u), nav column (Home–PgDn), arrow T (↑ + ← ↓ →), screen island between PgDn and → joined to the right bezel |
| Encoder | Ø9.5 hole in the solid F-row corner, knob Ø18 × 11 above the surface |
| Light bar | two flush frosted-PC channels (22 and 55 long) in the 0.5u bar with a 2.5 light slot to the PCB LEDs |
| Display | as v3: custom cover glass 23.8 × 20.6 flush in a 24.1 × 20.9 opening, bonded to the cartridge, 2 × M2 into the right wall; flex down the wall notch to a top-side PCB connector |
| Top case | z −6 … +7.5 (13.5 tall ring), bezel 8, underside relieved to 0.3 above the plate; the bars go down to the same relief |
| Mount | gasket: 8 plate tabs in pockets that are open to the seam; the bottom case has 3 mm ledges rising into them (they also index the halves) |
| Ball catch | 6 × M3 × 6 plungers at z −8.5 in the bottom case walls, 8 × 1.5 skirt tabs on the top case hanging to −10.5 |
| Bottom case | floor 3.5, desk at 6°, 21.5 front / 36.2 back; USB-C at z −8.5, pogo board as v3 |
| Keycaps | Cherry profile assumed (18.2 base, rows 9.3 / 8.1 / 7.3); the render caps are procedural lofts |

Outer skin sculpting is done with oblique planes: a facet is a plane through a "crease" line on a wall, leaning
inward below the crease. Because one plane cuts the whole shell before it is split at the seam, the facet runs
across the seam without a step.

## Variants

### ORE — faceted body, vortex weight, crease light
Crease at 6 mm above the desk at the front, rising to 22 mm at the back, all the way round (sides 16°, front 12°,
back 16°). Wide 2.5 mm top chamfer. A 2 mm frosted light line runs 2.5 mm below the crease on both sides (LED strip
inside, slot through the wall). Weight: 220 × 62 × 4 octagon, 36 engraved vortex grooves around a Ø32 ring, diamond
badge (separate polished part, faceted top) in the centre; brass 442 g. Underglow: a 220 mm frosted strip 6 mm in
from the front bottom edge. Reference: the Ore photos you sent (faceted top, sunburst weight), Athena 1800 side.

### ENVY — copper plate, mesh window
Gentle 14° band 7 mm tall all round, sharp 1.2 top chamfer. The bottom is a 262 × 100 × 3 plate (copper/brass, 1 mm
proud, "VLT" engraved) with a 120 × 40 window through which a hexagonal mesh (5 mm pitch, 0.4 deep) engraved into
the case floor shows, interrupted by a smooth sine-wave band. Underglow: frosted ring 10.5 mm in from the edge,
outside the plate. Reference: Envy65 (clickclack.io) — the only shop page that let itself be fetched.

### BLADE — chamfered base, front light line
Uniform 18° band 9 mm tall around the whole base (hull look), 2.5 top chamfer. A 2.5 mm light line through the
front band (180 long) plus the underglow ring at 13.5 mm. Weight: v3's 200 × 56 × 4 octagon bar. Reference: Razer
BlackWidow V4 underglow, Athena-style bevels.

Masses (aluminium 6061 / brass): ORE top 292 g, bottom 453 g, weight 442 g · ENVY 298 / 483 / 539 · BLADE 292 / 511 / 369.

## Round 2 — five more, bigger light areas (`out/compare_round2.jpg`)

All five keep the ball catch (6 × M3 ball plungers in the bottom case, dimpled skirt tabs on the top, Lucky65-style
pull-off), the per-group windows, the flush display island and a wider 4.5 mm light bar in the 0.5u gap.

| Style | Shaping | Light | Weight |
|-------|---------|-------|--------|
| **SYRIN** | 10° band on sides and front, 2.0 top chamfer, ribbed grooves around the USB-C port | nine 45° "///" slots (3.5 × 22) through the floor in front of the bar, plus a 220 mm front strip | **full-width mirror stainless bar 300 × 40 × 3** across the back of the underside, 1 mm proud, engraved 8-point star in a ring + "VLT" |
| **VELOTA** | square body, the two **front bottom corners cut at 45°** (14 mm legs) below the seam; sharp 1.5 top chamfer | the cut corners carry 2 mm frosted panels that open into the cavity (glowing corners); two 5 mm tall light windows across the back wall either side of the USB; underglow ring | 220 × 60 octagon, brass 437 g |
| **ICE V** | plain walls, 10° front band, 2.5 top chamfer | **the underside is one 262 × 92 frosted panel** over two long slots and LED channels (the whole bottom glows), a V-shaped light line towards the back | no metal weight; brass pyramid badge in the panel centre |
| **DECK** | **raised F-row tier**: the back bezel, F-row bars and nav corner stand 2 mm above the main deck, 12° band all round | a **300 mm light line in the riser** between the F-row and the number row, facing the typist; underglow ring | 240 × 80 plate, "VLT" engraved, brass 480 g |
| **BRASS BAR** | Athena-style crease 7 → 18 mm on the sides and back (14°) | 2.5 mm light line along the front wall above the bar; underglow ring | **brass bar 300 × 6 × 5 spanning the whole front bottom edge**, flush with the front and the bottom (76 g) + 200 × 56 octagon |

Masses (top / bottom / brass): SYRIN 294 / 572 / 301 · VELOTA 297 / 502 / 437 · ICE V 291 / 487 / 0 · DECK 308 / 531 / 480 · BRASS BAR 294 / 470 / 438.

Round-2 notes: the corner panels (Velota) and the front bar (Brass bar) are glued/screwed parts, not modelled with
screws yet; the Syrin's diagonal slots and the Ice V panel need an LED strip on the floor channels drawn in the
bottom case; the Deck riser line is fed from a 2.5 mm slot in the plate's F-row web (add to the plate before cutting).

## Layout variant: screen in the F-row, Del under the knob (`screen_frow=True`, built as `syrin_sf`)

Any style takes `screen_frow=True`. What it changes:

- The F-row Del key is gone; the screen sits between F12 and the knob, centred in that 34 mm span (x 279.15), with
  the glass running 0.8 mm above the number-row caps up 1.2 mm into the back bezel (y −22.6 … +1.2). The module is
  **not rotated** here: 17.58 wide × 20.82 tall, flex leaving towards the back wall into a 23 × 5.6 notch in the back
  bezel; the cartridge flange screws up into that notch (2 × M2). The flex drops through a 12 × 3 notch in the plate's
  back edge to a top-side PCB connector at about (279, −4), flex entering from +y. Firmware shows the image rotated
  180° (MADCTL MX+MY), no touch axis swap.
- The nav column window grows from three to four keys: Del, Home, PgUp, PgDn at y 1.25 … 5.25u. The new key sits
  where the old screen island was; a 3.6 mm bar separates it from the → key below. The PCB needs a hall sensor and
  LED at (16u, 4.75u).
- Gasket tabs move to x 40 / 135 / 200 / 250 (both edges) so the back-wall notch stays clear.
- The 0.5u light bar is unchanged; the F-row segment now runs beside the screen.

Renders: `out/syrin_sf/png/frow_closeup.png`, `frow_top.png`, `iso_front_right.png`.

## What I could not do

Every shop you listed answers scripted fetches with HTTP 429 (also from the remote fetcher), so only the Envy65
gallery came through. Sebas, Margo 65, Secret 65, 700E, Spectacle60, Kraze 65, Syrin, Chamber, Velora, Paper 65,
Eclipse TKL and the Prototypist list were designed from memory of those boards, not from their current photos.
If you save their images into a folder I can build contact sheets from it and tune the variants.

## Open points (in addition to v3's list)

1. The ORE back wall thins to about 2 mm at the floor level behind the 16° facet — fine for aluminium, but the CNC
   shop should know; reduce `h_back` or the angle if they object.
2. Window edges are drawn sharp; ask for a 0.3 mm break or specify a 0.5 chamfer (not modelled, CadQuery chamfers
   on 40+ window edges are fragile).
3. The crease light line (ORE) crosses the seam; the two insert halves must be cut to the seam, or the line can stop
   at the seam if that looks better.
4. Drawings (DXF/PDF) exist only for v3; once you pick a variant I will generate the v4 sheets the same way.
