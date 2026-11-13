"""Headless Blender renders of out/stl/*.stl → out/png/*.png  (Workbench engine, object colours, cavity shading).

    "C:/Program Files/Blender Foundation/Blender 4.3/blender.exe" -b --python render.py -- [view ...]
"""
import bpy, os, sys, math
from mathutils import Vector

HERE = os.path.dirname(os.path.abspath(__file__))
STL = os.path.join(HERE, "out", "stl")
PNG = os.path.join(HERE, "out", "png")
os.makedirs(PNG, exist_ok=True)

COL = {"top_case": (0.10, 0.10, 0.11, 1), "bottom_case": (0.13, 0.13, 0.14, 1), "plate": (0.65, 0.65, 0.68, 1),
       "cartridge": (0.45, 0.45, 0.48, 1), "display_module": (0.02, 0.02, 0.03, 1), "weight": (0.80, 0.60, 0.25, 1),
       "bar_inserts": (0.85, 0.95, 1.0, 1), "underglow_ring": (0.85, 0.95, 1.0, 1), "led_bars": (0.1, 0.7, 0.2, 1),
       "pcb": (0.08, 0.30, 0.15, 1), "usb_board": (0.08, 0.30, 0.15, 1), "pogo_board": (0.08, 0.30, 0.15, 1),
       "gaskets": (0.9, 0.25, 0.25, 1), "ball_plungers": (0.9, 0.9, 0.9, 1), "knob": (0.2, 0.2, 0.22, 1),
       "keycaps_preview": (0.22, 0.22, 0.24, 1)}

VIEWS = {
    #  name: (parts, camera direction (from target), ortho?, ortho scale / distance, target, resolution)
    "iso_front_right": (["top_case", "bottom_case", "plate", "cartridge", "display_module", "weight", "bar_inserts",
                         "underglow_ring", "knob", "keycaps_preview"], (0.55, -0.75, 0.42), False, 620, (157, -62, 0), (2400, 1500)),
    "display_closeup": (["top_case", "plate", "cartridge", "display_module", "bar_inserts", "knob", "keycaps_preview"],
                        (0.35, -0.75, 0.55), False, 150, (300, -75, 5), (2000, 1400)),
    "display_closeup_top": (["top_case", "plate", "cartridge", "display_module", "bar_inserts", "knob", "keycaps_preview"],
                            (0.0, -0.001, 1.0), True, 70, (296, -60, 5), (1600, 1600)),
    "top": (["top_case", "plate", "cartridge", "display_module", "bar_inserts", "knob", "keycaps_preview"],
            (0.0, -0.001, 1.0), True, 350, (157, -62, 0), (2400, 1100)),
    "top_no_caps": (["top_case", "plate", "cartridge", "display_module", "bar_inserts", "knob"],
                    (0.0, -0.001, 1.0), True, 350, (157, -62, 0), (2400, 1100)),
    "bottom": (["bottom_case", "weight", "underglow_ring"], (0.0, -0.001, -1.0), True, 350, (157, -62, -20), (2400, 1100)),
    "bottom_iso": (["bottom_case", "weight", "underglow_ring", "top_case", "knob"], (0.5, -0.7, -0.5), False, 620, (157, -62, -10), (2400, 1500)),
    "top_case_underside": (["top_case", "cartridge", "display_module", "bar_inserts"], (0.25, -0.35, -1.0), False, 560, (157, -62, 0), (2400, 1200)),
    "top_case_underside_display": (["top_case", "cartridge", "display_module"], (0.4, -0.5, -1.0), False, 120, (305, -92, 2), (1800, 1400)),
    "bottom_case_interior": (["bottom_case", "usb_board", "pogo_board", "led_bars", "ball_plungers", "gaskets"],
                             (0.25, -0.45, 1.0), False, 560, (157, -62, -10), (2400, 1200)),
    "bottom_case_interior_back": (["bottom_case", "usb_board", "pogo_board", "led_bars", "ball_plungers"],
                                  (0.3, -0.6, 0.8), False, 170, (157, -15, -12), (2000, 1300)),
    "side_right": (["top_case", "bottom_case", "plate", "weight", "knob", "keycaps_preview", "display_module"],
                   (1.0, 0.0, 0.0), True, 160, (157, -62, -8), (2000, 900)),
    "front": (["top_case", "bottom_case", "weight", "knob", "keycaps_preview"], (0.0, -1.0, 0.0), True, 350, (157, -62, -8), (2400, 700)),
    "exploded": (["top_case", "bottom_case", "plate", "cartridge", "display_module", "weight", "bar_inserts",
                  "underglow_ring", "pcb", "usb_board", "pogo_board", "gaskets", "ball_plungers", "knob", "keycaps_preview", "led_bars"],
                 (0.6, -0.8, 0.5), False, 900, (157, -62, 0), (2000, 2200)),
}
EXPLODE_Z = {"keycaps_preview": 70, "knob": 70, "display_module": 56, "bar_inserts": 50, "top_case": 42, "cartridge": 34,
             "gaskets": 24, "plate": 20, "pcb": 10, "pogo_board": 0, "usb_board": 0, "ball_plungers": -8, "bottom_case": -14,
             "led_bars": -14, "underglow_ring": -40, "weight": -48}


def clear():
    bpy.ops.object.select_all(action="SELECT")
    bpy.ops.object.delete()


def load(name, dz=0.0):
    path = os.path.join(STL, name + ".stl")
    if not os.path.exists(path):
        return None
    bpy.ops.wm.stl_import(filepath=path)
    ob = bpy.context.selected_objects[0]
    ob.name = name
    ob.color = COL.get(name, (0.5, 0.5, 0.5, 1))
    ob.location.z += dz
    # tilt the whole assembly into the desk frame so the renders stand on the desk
    return ob


def look(cam, direction, target, ortho, scale_or_dist):
    d = Vector(direction).normalized()
    cam.data.type = "ORTHO" if ortho else "PERSP"
    if ortho:
        cam.data.ortho_scale = scale_or_dist
        cam.location = Vector(target) + d * 1500
    else:
        cam.data.lens = 50
        cam.location = Vector(target) + d * scale_or_dist
    cam.rotation_euler = (-d).to_track_quat("-Z", "Y").to_euler()
    cam.data.clip_end = 10000


def material_for(name):
    m = bpy.data.materials.get("m_" + name)
    if m is None:
        m = bpy.data.materials.new("m_" + name)
        m.use_nodes = True
        bsdf = m.node_tree.nodes["Principled BSDF"]
        c = COL.get(name, (0.5, 0.5, 0.5, 1))
        bsdf.inputs["Base Color"].default_value = c
        metal = name in ("weight", "plate", "ball_plungers", "cartridge", "top_case", "bottom_case", "knob")
        bsdf.inputs["Metallic"].default_value = 0.9 if metal else 0.0
        bsdf.inputs["Roughness"].default_value = 0.45 if metal else 0.6
        if name in ("bar_inserts", "underglow_ring"):
            bsdf.inputs["Emission Color"].default_value = (0.6, 0.85, 1.0, 1)
            bsdf.inputs["Emission Strength"].default_value = 2.0
        if name == "display_module":
            bsdf.inputs["Roughness"].default_value = 0.05
    return m


def setup_scene(res):
    sc = bpy.context.scene
    sc.render.engine = "CYCLES"
    sc.cycles.device = "CPU"
    sc.cycles.samples = 24
    sc.cycles.use_denoising = True
    sc.cycles.max_bounces = 4
    sc.render.resolution_x, sc.render.resolution_y = res
    sc.render.resolution_percentage = 70
    sc.render.film_transparent = False
    if sc.world is None:
        sc.world = bpy.data.worlds.new("w")
    sc.world.use_nodes = True
    bg = sc.world.node_tree.nodes["Background"]
    bg.inputs["Color"].default_value = (0.55, 0.55, 0.58, 1)
    bg.inputs["Strength"].default_value = 1.2
    sun = bpy.data.lights.new("sun", "SUN")
    sun.energy = 3.0
    sun.angle = math.radians(8)
    so = bpy.data.objects.new("sun", sun)
    sc.collection.objects.link(so)
    so.rotation_euler = (math.radians(50), math.radians(10), math.radians(-35))
    sc.view_settings.view_transform = "Standard"
    for ob in sc.objects:
        if ob.type == "MESH":
            ob.data.materials.clear()
            ob.data.materials.append(material_for(ob.name))


def render_view(name):
    parts, direction, ortho, sod, target, res = VIEWS[name]
    clear()
    for p in parts:
        load(p, EXPLODE_Z.get(p, 0) if name == "exploded" else 0.0)
    cam = bpy.data.objects.new("cam", bpy.data.cameras.new("cam"))
    bpy.context.scene.collection.objects.link(cam)
    bpy.context.scene.camera = cam
    look(cam, direction, target, ortho, sod)
    setup_scene(res)
    bpy.context.scene.render.filepath = os.path.join(PNG, name + ".png")
    bpy.ops.render.render(write_still=True)
    print("rendered", name)


if __name__ == "__main__":
    argv = sys.argv[sys.argv.index("--") + 1:] if "--" in sys.argv else []
    for v in (argv or list(VIEWS)):
        render_view(v)
