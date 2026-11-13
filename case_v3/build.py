"""Build every part, check them against each other, export STEP + STL (per part and as one assembly).

    cadenv/Scripts/python.exe build.py [--quick]      (--quick skips the keycap preview and STL)
"""
import os, sys, time, json
import cadquery as cq
from params import *
import geom, parts
from kle import key_centres_mm

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
KLE = os.path.join(HERE, "..", "VLT-layout.json")
QUICK = "--quick" in sys.argv


def bb(wp):
    b = wp.val().BoundingBox()
    return "x %.2f..%.2f  y %.2f..%.2f  z %.2f..%.2f" % (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)


def vol(wp):
    return wp.val().Volume()


def self_checks():
    b = geom.cyl_y(10, 20, -5, 7, 1).val().BoundingBox()
    assert abs(b.ymin + 5) < 1e-3 and abs(b.ymax - 7) < 1e-3 and abs(b.xmin - 9) < 1e-3 and abs(b.zmin - 19) < 1e-3, bb(geom.cyl_y(10, 20, -5, 7, 1))
    b = geom.cyl_x(20, 30, -5, 7, 1).val().BoundingBox()
    assert abs(b.xmin + 5) < 1e-3 and abs(b.xmax - 7) < 1e-3 and abs(b.ymin - 19) < 1e-3 and abs(b.zmin - 29) < 1e-3, bb(geom.cyl_x(20, 30, -5, 7, 1))
    # desk frame: the front-bottom corner must land lower and further forward; the back-bottom lower still
    p = geom.desk_to_plate(geom.box(0, 1, 0, 1, -H_FRONT, -H_FRONT + 1)).val().BoundingBox()
    assert p.zmax < -12 and p.ymin < OY0, bb(geom.desk_to_plate(geom.box(0, 1, 0, 1, -H_FRONT, -H_FRONT + 1)))
    # the back wall (y = OY1) must meet the desk plane at desk-frame y = YD1
    q0 = geom.desk_to_plate(geom.box(0, 1, YD1 - 0.5, YD1 + 0.5, -H_FRONT - 0.5, -H_FRONT + 0.5)).val().BoundingBox()
    assert abs((q0.ymin + q0.ymax) / 2 - OY1) < 0.2, "YD1 mismatch: %s vs %s" % ((q0.ymin + q0.ymax) / 2, OY1)
    q = geom.desk_to_plate(geom.box(0, 1, D - 1, D, -H_FRONT, -H_FRONT + 1)).val().BoundingBox()
    assert q.zmax < p.zmin, "back must be lower than front in the plate frame"
    print("self-checks ok")


def main():
    t0 = time.time()
    os.makedirs(os.path.join(OUT, "step"), exist_ok=True)
    os.makedirs(os.path.join(OUT, "stl"), exist_ok=True)
    self_checks()

    keys = key_centres_mm(KLE) + [(ENC_CX, ENC_CY, 1.0, "ENC")]
    print(len(keys) - 1, "keys +", "encoder")

    P = {}
    def build(name, fn, *a):
        t = time.time(); P[name] = fn(*a); print("%-18s %6.1fs  %s  vol %.0f mm3" % (name, time.time() - t, bb(P[name]), vol(P[name])))

    build("top_case", geom.top_case)
    build("bottom_case", geom.bottom_case)
    build("plate", parts.plate, keys)
    build("cartridge", parts.cartridge)
    build("display_module", parts.display_module)
    build("cover_glass", parts.cover_glass)
    build("weight", parts.weight)
    build("bar_inserts", parts.bar_inserts)
    build("underglow_ring", parts.underglow_ring)
    build("led_bars", parts.led_bars)
    build("pcb", parts.pcb)
    build("usb_board", parts.usb_board)
    build("pogo_board", parts.pogo_board)
    build("gaskets", parts.gaskets)
    build("ball_plungers", parts.ball_plungers)
    build("knob", parts.knob)
    if not QUICK:
        build("keycaps_preview", parts.keycaps_preview, keys)

    # ---- interference checks (volumes of pairwise intersections, mm3) ----
    pairs = [("top_case", "plate"), ("top_case", "cartridge"), ("top_case", "display_module"), ("top_case", "bottom_case"),
             ("top_case", "knob"), ("bottom_case", "plate"), ("bottom_case", "pcb"), ("bottom_case", "weight"),
             ("bottom_case", "underglow_ring"), ("bottom_case", "led_bars"), ("bottom_case", "usb_board"),
             ("bottom_case", "pogo_board"), ("cartridge", "display_module"), ("plate", "pcb"), ("plate", "display_module"),
             ("top_case", "bar_inserts"), ("top_case", "gaskets"), ("bottom_case", "gaskets"), ("plate", "gaskets"),
             ("bottom_case", "ball_plungers"), ("top_case", "ball_plungers"), ("pcb", "pogo_board"), ("pcb", "display_module")]
    if not QUICK:
        pairs += [("top_case", "keycaps_preview"), ("plate", "keycaps_preview"), ("display_module", "keycaps_preview"),
                  ("knob", "keycaps_preview")]
    print("--- interference (mm3; >1 means parts overlap) ---")
    report = {}
    for a, b in pairs:
        try:
            v = vol(P[a].intersect(P[b]))
        except Exception as e:
            v = -1
        report[a + "+" + b] = v
        flag = "  <-- OVERLAP" if v > 1.0 else ""
        print("  %-34s %10.1f%s" % (a + " x " + b, v, flag))

    # ---- masses ----
    dens = {"top_case": 2.70, "bottom_case": 2.70, "plate": 2.70, "weight": 8.50, "cartridge": 2.70}
    print("--- mass estimate ---")
    for n, d in dens.items():
        print("  %-12s %7.0f g  (%s)" % (n, vol(P[n]) / 1000 * d, "brass" if n == "weight" else "6061 Al"))

    # ---- export ----
    colors = {"top_case": (0.12, 0.12, 0.13, 1), "bottom_case": (0.15, 0.15, 0.16, 1), "plate": (0.6, 0.6, 0.62, 1),
              "cartridge": (0.35, 0.35, 0.38, 1), "display_module": (0.05, 0.05, 0.05, 1), "cover_glass": (0.1, 0.1, 0.12, 0.5),
              "weight": (0.72, 0.55, 0.25, 1),
              "bar_inserts": (0.9, 0.9, 0.95, 0.6), "underglow_ring": (0.9, 0.9, 0.95, 0.6), "led_bars": (0.1, 0.5, 0.1, 1),
              "pcb": (0.1, 0.3, 0.15, 1), "usb_board": (0.1, 0.3, 0.15, 1), "pogo_board": (0.1, 0.3, 0.15, 1),
              "gaskets": (0.9, 0.3, 0.3, 1), "ball_plungers": (0.8, 0.8, 0.8, 1), "knob": (0.2, 0.2, 0.2, 1),
              "keycaps_preview": (0.25, 0.25, 0.27, 1)}
    asm = cq.Assembly(name="VLT_case_v3")
    for n, wp in P.items():
        cq.exporters.export(wp, os.path.join(OUT, "step", n + ".step"))
        if not QUICK:
            cq.exporters.export(wp, os.path.join(OUT, "stl", n + ".stl"), tolerance=0.03, angularTolerance=0.15)
        asm.add(wp, name=n, color=cq.Color(*colors.get(n, (0.5, 0.5, 0.5, 1))))
    asm.save(os.path.join(OUT, "step", "VLT_case_v3_assembly.step"))
    if not QUICK:
        comp = cq.Compound.makeCompound([wp.val() for wp in P.values()])
        cq.exporters.export(cq.Workplane().add(comp), os.path.join(OUT, "stl", "VLT_case_v3_assembly.stl"), tolerance=0.03, angularTolerance=0.15)
    json.dump({"interference_mm3": report, "bbox": {n: bb(w) for n, w in P.items()}, "volume_mm3": {n: vol(w) for n, w in P.items()}},
              open(os.path.join(OUT, "build_report.json"), "w"), indent=1)
    print("done in %.0f s -> %s" % (time.time() - t0, OUT))


if __name__ == "__main__":
    main()
