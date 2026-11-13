"""Build the v5 designs: out/<style>/step, stl, assembly + interference report.

    cadenv/Scripts/python.exe build_v5.py [style ...|all] [--quick]
"""
import os, sys, time, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "case_v3"))
sys.path.insert(0, os.path.join(HERE, "..", "case_v4"))
import cadquery as cq
from params import *
import parts, v4
import v5_cases as C
from v5_styles import STYLES
from kle import key_centres_mm

KLE = os.path.join(HERE, "..", "VLT-layout.json")
QUICK = "--quick" in sys.argv
which = [a for a in sys.argv[1:] if not a.startswith("--")]
which = list(STYLES) if (not which or which == ["all"]) else which


def bb(wp):
    b = wp.val().BoundingBox()
    return "x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f" % (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)


def build_style(key, keys0):
    env = STYLES[key]
    out = os.path.join(HERE, "out", key)
    os.makedirs(os.path.join(out, "step"), exist_ok=True); os.makedirs(os.path.join(out, "stl"), exist_ok=True)
    keys = v4.layout_keys(keys0, dict(screen_frow=(env.screen == "frow")))
    P = {}
    def add(name, fn, *a):
        t = time.time()
        try:
            r = fn(*a)
        except Exception as e:
            import traceback
            print("  %-18s FAILED: %r" % (name, e)); traceback.print_exc(limit=3); return
        if r is None:
            return
        P[name] = r; print("  %-18s %5.1fs %s vol %.0f" % (name, time.time() - t, bb(r), r.val().Volume()))
    print("== style", key, "(%s)" % env.name)
    add("top_case", C.top_case, env, keys)
    add("bottom_case", C.bottom_case, env)
    add("plate", C.plate, env, keys)
    cart, disp = C.display_parts(env)
    P["cartridge"], P["display_module"] = cart, disp
    bf = C.bottom_face_frame(env)
    add("weight", C.weight, env, bf)
    add("top_light_inserts", C.top_light_inserts, env)
    add("front_light_inserts", C.front_light_inserts, env)
    add("underglow_inserts", C.underglow_inserts, env, bf)
    add("pcb", parts.pcb)
    add("usb_board", lambda: parts.usb_board().translate((0, 0, v4.USB4_BOARD_TOP - USB_BOARD_TOP_Z)))
    add("pogo_board", parts.pogo_board)
    add("gaskets", C.gaskets, env)
    add("knob", C.knob, env)
    if not QUICK:
        add("keycaps_preview", v4.keycaps_cherry, keys)
    pairs = [("top_case", "plate"), ("top_case", "cartridge"), ("top_case", "display_module"), ("top_case", "bottom_case"),
             ("top_case", "knob"), ("bottom_case", "plate"), ("bottom_case", "pcb"), ("bottom_case", "weight"), ("bottom_case", "usb_board"),
             ("bottom_case", "pogo_board"), ("top_case", "gaskets"), ("bottom_case", "gaskets"), ("top_case", "top_light_inserts"),
             ("bottom_case", "front_light_inserts"), ("bottom_case", "underglow_inserts"), ("weight", "underglow_inserts"),
             ("top_case", "keycaps_preview"), ("plate", "keycaps_preview"), ("display_module", "keycaps_preview"), ("knob", "keycaps_preview"),
             ("top_light_inserts", "keycaps_preview"), ("cartridge", "display_module"), ("plate", "display_module"), ("top_case", "usb_board")]
    rep = {}
    for a, b in pairs:
        if a in P and b in P:
            try:
                v = P[a].intersect(P[b]).val().Volume()
            except Exception:
                v = -1
            rep[a + "+" + b] = v
            if v > 1.0:
                print("   %-34s %8.1f  <-- OVERLAP" % (a + " x " + b, v))
    vol = lambda n: (P[n].val().Volume() if n in P else 0.0)
    print("  mass: top %.0f g, bottom %.0f g, weight %.0f g (brass);  size %.1f x %.1f, front %.1f, bezel top %.1f" % (
        vol("top_case") / 1000 * 2.7, vol("bottom_case") / 1000 * 2.7, vol("weight") / 1000 * 8.5, env.W, env.D, env.h_front, env.top_z))
    glass = (0.9, 0.9, 0.95, 0.6)
    colors = {"top_case": (0.12, 0.12, 0.13, 1), "bottom_case": (0.15, 0.15, 0.16, 1), "plate": (0.6, 0.6, 0.62, 1), "cartridge": (0.4, 0.4, 0.42, 1),
              "display_module": (0.05, 0.05, 0.05, 1), "weight": (0.72, 0.55, 0.25, 1), "top_light_inserts": glass, "front_light_inserts": glass,
              "underglow_inserts": glass, "pcb": (0.1, 0.3, 0.15, 1), "usb_board": (0.1, 0.3, 0.15, 1), "pogo_board": (0.1, 0.3, 0.15, 1),
              "gaskets": (0.9, 0.3, 0.3, 1), "knob": (0.2, 0.2, 0.2, 1), "keycaps_preview": (0.9, 0.9, 0.88, 1)}
    asm = cq.Assembly(name="VLT_case_v5_" + key)
    for n, wp in P.items():
        cq.exporters.export(wp, os.path.join(out, "step", n + ".step"))
        if not QUICK:
            cq.exporters.export(wp, os.path.join(out, "stl", n + ".stl"), tolerance=0.03, angularTolerance=0.15)
        asm.add(wp, name=n, color=cq.Color(*colors.get(n, (0.5, 0.5, 0.5, 1))))
    asm.save(os.path.join(out, "step", "VLT_case_v5_%s_assembly.step" % key))
    json.dump({"interference_mm3": rep, "bbox": {n: bb(w) for n, w in P.items()}}, open(os.path.join(out, "build_report.json"), "w"), indent=1)


if __name__ == "__main__":
    keys0 = key_centres_mm(KLE) + [(ENC_CX, ENC_CY, 1.0, "ENC")]
    t0 = time.time()
    for k in which:
        build_style(k, keys0)
    print("done in %.0f s" % (time.time() - t0))
