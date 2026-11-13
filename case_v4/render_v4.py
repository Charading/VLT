"""Headless Blender renders for a v4 style: out/<style>/stl → out/<style>/png.

    blender -b --python render_v4.py -- <style> [view ...]
"""
import bpy, os, sys, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
STYLE = argv[0] if argv else "ore"
VIEWSEL = argv[1:]
STL = os.path.join(HERE, "out", STYLE, "stl")
PNG = os.path.join(HERE, "out", STYLE, "png")
os.makedirs(PNG, exist_ok=True)

COL = {"top_case": (0.10, 0.10, 0.11, 1), "bottom_case": (0.11, 0.11, 0.12, 1), "plate": (0.65, 0.65, 0.68, 1),
       "cartridge": (0.45, 0.45, 0.48, 1), "display_module": (0.02, 0.02, 0.03, 1), "weight": (0.80, 0.60, 0.25, 1),
       "badge": (0.9, 0.9, 0.92, 1), "bar_inserts": (0.85, 0.95, 1.0, 1), "crease_inserts": (0.85, 0.95, 1.0, 1),
       "underglow_ring": (0.85, 0.95, 1.0, 1), "pcb": (0.08, 0.30, 0.15, 1), "usb_board": (0.08, 0.30, 0.15, 1),
       "pogo_board": (0.08, 0.30, 0.15, 1), "gaskets": (0.9, 0.25, 0.25, 1), "knob": (0.16, 0.16, 0.18, 1),
       "keycaps_preview": (0.92, 0.91, 0.88, 1), "front_bar": (0.80, 0.60, 0.25, 1)}
GLOW = ["bar_inserts", "underglow_ring", "crease_inserts", "front_strip_insert", "front_light_insert", "corner_inserts",
        "back_window_inserts", "bottom_panel", "v_light_inserts", "diag_inserts", "deck_light_insert"]
for g in GLOW:
    COL.setdefault(g, (0.85, 0.95, 1.0, 1))
FULL = ["top_case", "bottom_case", "plate", "cartridge", "display_module", "weight", "badge", "knob", "keycaps_preview", "front_bar"] + GLOW
VIEWS = {
    "iso_front_right": (FULL, (0.55, -0.75, 0.42), False, 640, (157, -62, 0), (2400, 1500)),
    "iso_front_left": (FULL, (-0.6, -0.7, 0.4), False, 640, (157, -62, 0), (2400, 1500)),
    "low_front": (FULL, (0.35, -0.9, 0.12), False, 600, (157, -62, -4), (2400, 1300)),
    "display_closeup": (FULL, (0.35, -0.75, 0.55), False, 150, (300, -75, 5), (2000, 1400)),
    "frow_closeup": (FULL, (0.25, -0.8, 0.5), False, 170, (282, -18, 6), (2000, 1400)),
    "frow_top": ([p for p in FULL if p != "keycaps_preview"], (0.0, -0.001, 1.0), True, 90, (280, -45, 5), (1600, 1600)),
    "top": (FULL, (0.0, -0.001, 1.0), True, 350, (157, -62, 0), (2400, 1100)),
    "top_no_caps": ([p for p in FULL if p != "keycaps_preview"], (0.0, -0.001, 1.0), True, 350, (157, -62, 0), (2400, 1100)),
    "side_right": (FULL, (1.0, 0.0, 0.0), True, 160, (157, -62, -8), (2000, 900)),
    "side_right_low": (FULL, (1.0, -0.35, 0.08), False, 420, (157, -62, -8), (2400, 1200)),
    "bottom": (["bottom_case", "weight", "badge", "front_bar"] + GLOW, (0.0, -0.001, -1.0), True, 350, (157, -62, -20), (2400, 1100)),
    "bottom_iso": (["bottom_case", "weight", "badge", "front_bar", "top_case", "knob"] + GLOW, (0.5, -0.7, -0.5), False, 640, (157, -62, -10), (2400, 1500)),
    "back_iso": (FULL, (0.45, 0.8, 0.35), False, 640, (157, -62, 0), (2400, 1500)),
    "top_case_underside": (["top_case", "cartridge", "display_module", "bar_inserts", "crease_inserts", "deck_light_insert"], (0.25, -0.35, -1.0), False, 560, (157, -62, 0), (2400, 1200)),
    "bottom_case_interior": (["bottom_case", "usb_board", "pogo_board", "gaskets"], (0.25, -0.45, 1.0), False, 560, (157, -62, -10), (2400, 1200)),
}


def clear():
    bpy.ops.object.select_all(action="SELECT"); bpy.ops.object.delete()


def load(name):
    path = os.path.join(STL, name + ".stl")
    if not os.path.exists(path):
        return None
    bpy.ops.wm.stl_import(filepath=path)
    ob = bpy.context.selected_objects[0]; ob.name = name
    return ob


def material_for(name):
    m = bpy.data.materials.get("m_" + name)
    if m is None:
        m = bpy.data.materials.new("m_" + name); m.use_nodes = True
        b = m.node_tree.nodes["Principled BSDF"]
        b.inputs["Base Color"].default_value = COL.get(name, (0.5, 0.5, 0.5, 1))
        metal = name in ("weight", "plate", "cartridge", "top_case", "bottom_case", "knob", "badge")
        b.inputs["Metallic"].default_value = 0.85 if metal else 0.0
        b.inputs["Roughness"].default_value = {"weight": 0.35, "badge": 0.15, "display_module": 0.05, "front_bar": 0.3}.get(name, 0.42 if metal else 0.55)
        if name == "front_bar":
            b.inputs["Metallic"].default_value = 0.9
        if name in GLOW:
            b.inputs["Emission Color"].default_value = (0.55, 0.85, 1.0, 1); b.inputs["Emission Strength"].default_value = 2.5
    return m


def look(cam, direction, target, ortho, sod):
    d = Vector(direction).normalized()
    cam.data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale = sod; cam.location = Vector(target) + d * 1500
    else:
        cam.data.lens = 50; cam.location = Vector(target) + d * sod
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler(); cam.data.clip_end = 10000


def setup_scene(res):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"; sc.cycles.device = "CPU"; sc.cycles.samples = 28; sc.cycles.use_denoising = True; sc.cycles.max_bounces = 4
    sc.render.resolution_x, sc.render.resolution_y = res; sc.render.resolution_percentage = 70
    if sc.world is None:
        sc.world = bpy.data.worlds.new("w")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes["Background"]; bg.inputs["Color"].default_value = (0.5, 0.5, 0.53, 1); bg.inputs["Strength"].default_value = 1.2
    sun = bpy.data.lights.new("sun", "SUN"); sun.energy = 3.0; sun.angle = math.radians(8)
    so = bpy.data.objects.new("sun", sun); sc.collection.objects.link(so); so.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
    sc.view_settings.view_transform = "Standard"
    for ob in sc.objects:
        if ob.type == "MESH":
            ob.data.materials.clear(); ob.data.materials.append(material_for(ob.name))
            if ob.name in ("top_case", "bottom_case", "weight", "knob", "keycaps_preview", "badge"):
                for p in ob.data.polygons:
                    p.use_smooth = False


def render_view(name):
    parts, direction, ortho, sod, target, res = VIEWS[name]
    clear()
    for p in parts:
        load(p)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam")); bpy.context.scene.collection.objects.link(cam); bpy.context.scene.camera = cam
    look(cam, direction, target, ortho, sod); setup_scene(res)
    bpy.context.scene.render.filepath = os.path.join(PNG, name + ".png"); bpy.ops.render.render(write_still=True)
    print("rendered", STYLE, name)


if __name__ == "__main__":
    for v in (VIEWSEL or list(VIEWS)):
        render_view(v)
