# VLT case v5 — six designs with their own envelopes

Rev A, 2026-11-06. Answer to "all of these boards have the same profiles and shapes": in v5 the **envelope is part
of the design**. Each `Env` in `v5_styles.py` sets its own bezel width per side, corner treatment per corner, bezel
height, typing angle, front height, wall lean or bulge (the shell is lofted between a top outline and a base outline),
sloped bezel ring, and where the screen goes. Every design has a front-face ambient feature and top-side case-LED
lighting of its own shape, plus the shared interior (per-group windows, flush screen, ball catch, gasket pockets,
daughterboards).

```bash
cadenv/Scripts/python build_v5.py all          # out/<style>/step|stl + build_report.json
blender -b --python render_v5.py -- slab        # out/slab/png
cadenv/Scripts/python compare_v5.py             # out/compare_v5.jpg
```

Files: `v5_env.py` (Env dataclass, lofted shell, chamfer caps, sloped bezel), `v5_cases.py` (top/bottom case,
top lights, front lights, underglow, weight placement), `v5_styles.py` (the six designs).

## The six

| | Envelope | Screen | Case LEDs (top) | Front ambient | Underglow | Weight |
|--|--|--|--|--|--|--|
| **SLAB** | 18 mm front chin, 7/8 mm elsewhere, R9 corners, bezel only 6 mm above the plate, 7°, 19 mm front | island (raised 1.5 mm tile) | light line across the chin + 0.5u bar | band in the front wall | ring | 220 × 60 octagon |
| **SHIELD** | 18 mm chamfered front corners, sides and front lean in 2.5 mm to the base, tall 9 mm bezel, 6.5°, 22 mm front | island | five dots on the back bezel (one per F-row group) | V light on the front | nine diagonal slots | 230 × 56 plate, back half, "VLT" |
| **PILLOW** | convex walls (3.5 mm belly), R12 corners, 10 mm bezels sloping 2 mm towards the keys, 5°, 23 mm front | F-row, left of the knob | halo line around the whole key area | wide band, full height of the front wall | whole-bottom frosted panel | none (panel) |
| **WEDGE** | octagonal plan (C7 corners), bezel 5.5 mm above the plate (switch tops show), front face splayed 5 mm outward, 8°, 18 mm front | island (raised 2 mm tile) | back-bezel bar + 0.5u bar | band in the splayed front | front strip | 200 × 56 octagon |
| **TOWER** | 18 mm right bezel, back-right corner cut C18, 8 mm bezel height, 6°, 21 mm front | island | vertical 5 mm bar down the right bezel + a corner triangle | row of short vertical slots | two side strips | 300 × 40 mirror bar, star + "VLT" |
| **STEP** | 14 mm back bezel raised 3 mm with the riser light line, back wall leans in 4 mm, R2 corners, 6°, 20 mm front | F-row, left of the knob | two side lines along the bezels + riser line | frosted lip along the whole front bottom edge | ring | 240 × 80 plate, "VLT" |

Masses (top / bottom / brass): SLAB 334 / 562 / 434 · SHIELD 371 / 598 / 319 · PILLOW 458 / 658 / 0 · WEDGE 244 / 583 / 369 ·
TOWER 355 / 607 / 301 · STEP 353 / 538 / 480. Sizes: 329–340 wide, 136–149 deep.

## Rules the envelopes obey

- Bezels carrying gasket pockets (back, front) and plungers (all four) are ≥ 8 mm at the top; a leaning wall is
  checked so the wall is still > 6 mm at the plunger height.
- Plungers sit 1.8 mm below the seam, skirt tabs reach 1.6 mm below that; on low fronts (18–20 mm) the cavity floor
  comes within 0.5–1 mm of the tab ends, which is as low as a front can go with this catch.
- Top and bottom chamfers are boolean "caps" (lofts), because OCC chamfers fail on lofted outlines.
- The screen tile rises above low bezels (SLAB, WEDGE) and sits in the raised tier on STEP.
- Top light shapes get a 1.2 mm flush frosted insert over a 3.5 mm LED cavity for a 4 mm COB flex strip; the 0.5u bar
  is fed from PCB LEDs through a slot as before. Front features sit in the bottom case's front wall below the seam,
  between the plungers, lit by a vertical flex strip inside.

## Open points

1. The LED strips for top/front/underside lights are specified (channels, cavities), not drawn as parts; wire holes
   into the cavity are to be added per chosen design.
2. PILLOW's convex loft has planar-approximated arcs (8 segments per corner); the CNC shop should receive the STEP
   with a note to smooth, or the outline can be regenerated with more segments.
3. Front lights in the bottom case are only ~3 mm tall at the front on the low designs; the "band_wide" and "lip"
   variants are the ones that read as big ambient from the typing position.
