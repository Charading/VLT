"""Build the v4 variants: out/<style>/step, out/<style>/stl + assembly + interference report.

    cadenv/Scripts/python.exe build_v4.py [ore|blade|all] [--quick]
"""
import os, sys, time, json
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, "..", "case_v3"))
import cadquery as cq
from params import *
import parts, v4
from kle import key_centres_mm

KLE = os.path.join(HERE, "..", "VLT-layout.json")
QUICK = "--quick" in sys.argv
which = [a for a in sys.argv[1:] if not a.startswith("--")]
which = list(v4.STYLES) if (not which or which == ["all"]) else which


def bb(wp):
    b = wp.val().BoundingBox()
    return "x %.1f..%.1f y %.1f..%.1f z %.1f..%.1f" % (b.xmin, b.xmax, b.ymin, b.ymax, b.zmin, b.zmax)


def build_style(key, keys):
    st = v4.STYLES[key]
    out = os.path.join(HERE, "out", key)
    os.makedirs(os.path.join(out, "step"), exist_ok=True); os.makedirs(os.path.join(out, "stl"), exist_ok=True)
    P = {}
    def add(name, fn, *a):
        t = time.time(); r = fn(*a)
        if r is None:
            return
        P[name] = r; print("  %-16s %5.1fs %s vol %.0f" % (name, time.time() - t, bb(r), r.val().Volume()))
    print("== style", key)
    keys = v4.layout_keys(keys, st)
    add("top_case", v4.top_case_v4, st, keys)
    add("bottom_case", v4.bottom_case_v4, st)
    add("plate", v4.plate_v4, st, keys)
    add("cartridge", v4.cartridge_v4, st)
    add("display_module", v4.display_module_v4, st)
    add("weight", v4.weight_v4, st)
    add("badge", v4.badge_v4, st)
    add("bar_inserts", v4.bar_inserts_v4, st)
    if st.get("crease_light"):
        add("crease_inserts", v4.crease_inserts, st)
    if st["underglow"] == "ring":
        add("underglow_ring", lambda: _ring(st))
    if st["underglow"] == "front_strip":
        add("front_strip_insert", v4.front_strip_insert, st)
    if st.get("front_light"):
        add("front_light_insert", v4.front_light_insert, st)
    if st.get("corner_cut"):
        add("corner_inserts", v4.corner_inserts, st)
    if st.get("back_window"):
        add("back_window_inserts", v4.back_window_inserts, st)
    if st.get("bottom_panel"):
        add("bottom_panel", v4.bottom_panel_part, st)
    if st.get("v_light"):
        add("v_light_inserts", v4.v_light_inserts, st)
    if st.get("diag_slots"):
        add("diag_inserts", v4.diag_inserts, st)
    if st.get("front_bar"):
        add("front_bar", v4.front_bar_part, st)
    if st.get("deck_raise"):
        add("deck_light_insert", v4.deck_light_insert, st)
    add("pcb", parts.pcb)
    add("usb_board", lambda: parts.usb_board().translate((0, 0, v4.USB4_BOARD_TOP - USB_BOARD_TOP_Z)))
    add("pogo_board", parts.pogo_board)
    add("gaskets", v4.gaskets_v4, st)
    add("knob", v4.knob_v4, st)
    if not QUICK:
        add("keycaps_preview", v4.keycaps_cherry, keys)
    pairs = [("top_case", "plate"), ("top_case", "cartridge"), ("top_case", "display_module"), ("top_case", "bottom_case"),
             ("top_case", "knob"), ("bottom_case", "plate"), ("bottom_case", "pcb"), ("bottom_case", "weight"),
             ("bottom_case", "usb_board"), ("bottom_case", "pogo_board"), ("top_case", "gaskets"), ("bottom_case", "gaskets"),
             ("top_case", "bar_inserts"), ("weight", "badge"), ("bottom_case", "badge"), ("top_case", "usb_board"),
             ("bottom_case", "underglow_ring"), ("top_case", "crease_inserts"), ("bottom_case", "crease_inserts"), ("top_case", "keycaps_preview"),
             ("plate", "keycaps_preview"), ("display_module", "keycaps_preview"), ("knob", "keycaps_preview"),
             ("bottom_case", "corner_inserts"), ("bottom_case", "back_window_inserts"), ("bottom_case", "bottom_panel"), ("bottom_panel", "badge"),
             ("bottom_case", "v_light_inserts"), ("bottom_case", "diag_inserts"), ("bottom_case", "front_bar"), ("top_case", "deck_light_insert"),
             ("bottom_case", "front_strip_insert"), ("bottom_case", "front_light_insert"), ("top_case", "front_bar"), ("weight", "diag_inserts"),
             ("deck_light_insert", "keycaps_preview"), ("plate", "deck_light_insert")]
    rep = {}
    print("  -- interference --")
    for a, b in pairs:
        if a in P and b in P:
            v = P[a].intersect(P[b]).val().Volume()
            rep[a + "+" + b] = v
            if v > 1.0:
                print("   %-30s %8.1f  <-- OVERLAP" % (a + " x " + b, v))
    print("  mass: top %.0f g, bottom %.0f g, weight %.0f g (brass)" % (P["top_case"].val().Volume() / 1000 * 2.7, P["bottom_case"].val().Volume() / 1000 * 2.7,
          (P["weight"].val().Volume() if "weight" in P else 0) / 1000 * 8.5 + (P["front_bar"].val().Volume() if "front_bar" in P else 0) / 1000 * 8.5))
    glass = (0.9, 0.9, 0.95, 0.6)
    colors = {"top_case": (0.12, 0.12, 0.13, 1), "bottom_case": (0.15, 0.15, 0.16, 1), "plate": (0.6, 0.6, 0.62, 1), "cartridge": (0.4, 0.4, 0.42, 1),
              "display_module": (0.05, 0.05, 0.05, 1), "weight": (0.72, 0.55, 0.25, 1), "badge": (0.85, 0.85, 0.88, 1), "bar_inserts": glass,
              "crease_inserts": glass, "underglow_ring": glass, "front_strip_insert": glass, "front_light_insert": glass, "corner_inserts": glass,
              "back_window_inserts": glass, "bottom_panel": glass, "v_light_inserts": glass, "diag_inserts": glass, "deck_light_insert": glass,
              "front_bar": (0.72, 0.55, 0.25, 1), "pcb": (0.1, 0.3, 0.15, 1), "usb_board": (0.1, 0.3, 0.15, 1),
              "pogo_board": (0.1, 0.3, 0.15, 1), "gaskets": (0.9, 0.3, 0.3, 1), "knob": (0.2, 0.2, 0.2, 1), "keycaps_preview": (0.9, 0.9, 0.88, 1)}
    asm = cq.Assembly(name="VLT_case_v4_" + key)
    for n, wp in P.items():
        cq.exporters.export(wp, os.path.join(out, "step", n + ".step"))
        if not QUICK:
            cq.exporters.export(wp, os.path.join(out, "stl", n + ".stl"), tolerance=0.03, angularTolerance=0.15)
        asm.add(wp, name=n, color=cq.Color(*colors.get(n, (0.5, 0.5, 0.5, 1))))
    asm.save(os.path.join(out, "step", "VLT_case_v4_%s_assembly.step" % key))
    json.dump({"interference_mm3": rep, "bbox": {n: bb(w) for n, w in P.items()}}, open(os.path.join(out, "build_report.json"), "w"), indent=1)


def _ring(st):
    from geom import rrect_prism, desk_to_plate
    ri = st["ring_in"]; zb = -v4.H4_FRONT
    o = rrect_prism(DCX, DCY, W - 2 * (ri - RING_W / 2) - 0.1, DL - 2 * (ri - RING_W / 2) - 0.1, zb, zb + RING_D - 0.05, 3.95)
    i = rrect_prism(DCX, DCY, W - 2 * (ri + RING_W / 2) + 0.1, DL - 2 * (ri + RING_W / 2) + 0.1, zb - 1, zb + RING_D + 1, 1.05)
    return desk_to_plate(o.cut(i))


if __name__ == "__main__":
    keys = key_centres_mm(KLE) + [(ENC_CX, ENC_CY, 1.0, "ENC")]
    t0 = time.time()
    for k in which:
        build_style(k, keys)
    print("done in %.0f s" % (time.time() - t0))
