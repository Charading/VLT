"""Six v5 designs, each with its own envelope."""
from v5_env import Env

STYLES = {
    # 1. SLAB — wide front chin, big round corners, low bezel, steeper angle
    "slab": Env(name="Slab", bez=(7.0, 8.0, 7.0, 18.0), corners=(("r", 9.0),) * 4, top_z=6.0, tilt=7.0, h_front=19.0,
                top_chamfer=1.0, screen="island", top_light=("chin_line", "bar05"), front_light="band", underglow="ring",
                weight=dict(kind="octagon", size=(220.0, 60.0, 4.0, 14.0), pocket=3.0)),
    # 2. SHIELD — chamfered front corners, sides and front lean in, tall bezel
    "shield": Env(name="Shield", bez=(10.0, 10.0, 10.0, 9.0), corners=(("c", 18.0), ("c", 18.0), ("r", 5.0), ("r", 5.0)),
                  bottom_off=(-2.5, -2.5, 0.0, -2.5), top_z=9.0, tilt=6.5, h_front=22.0, top_chamfer=2.0, screen="island",
                  top_light=("frow_dots",), front_light="v", underglow="diag",
                  weight=dict(kind="plate", size=(230.0, 56.0, 3.0, 12.0), pocket=2.0, dy=22.0, text="VLT")),
    # 3. PILLOW — convex walls, big radii, sloped bezel ring, halo light, panel underglow, screen in the F-row
    "pillow": Env(name="Pillow", bez=(10.0, 10.0, 10.0, 10.0), corners=(("r", 12.0),) * 4, bulge=3.5, bottom_off=(1.5, 1.5, 1.5, 1.5),
                  top_slope=2.0, top_z=7.5, tilt=5.0, h_front=23.0, top_chamfer=0.8, screen="frow",
                  top_light=("halo",), front_light="band_wide", underglow="panel", weight=None),
    # 4. WEDGE — low bezel (switches show), octagonal plan, splayed front face, raised screen tile
    "wedge": Env(name="Wedge", bez=(8.0, 8.0, 8.0, 8.0), corners=(("c", 7.0),) * 4, top_z=5.5, tilt=8.0, h_front=18.0,
                 bottom_off=(0.0, 0.0, 0.0, 5.0), top_chamfer=0.8, screen="island", top_light=("back_bar", "bar05"),
                 front_light="band", underglow="front_strip", weight=dict(kind="octagon", size=(200.0, 56.0, 4.0, 12.0), pocket=3.0)),
    # 5. TOWER — wide right bezel with a vertical light bar, cut back-right corner, slotted front, side underglow
    "tower": Env(name="Tower", bez=(8.0, 18.0, 8.0, 8.0), corners=(("r", 4.0), ("r", 4.0), ("c", 18.0), ("r", 4.0)), top_z=8.0,
                 tilt=6.0, h_front=21.0, top_chamfer=1.5, screen="island", top_light=("tower_bar", "corner_tri"),
                 front_light="slots", underglow="side_strips",
                 weight=dict(kind="bar_wide", size=(300.0, 40.0, 3.0, 6.0), pocket=2.0, dy=26.0, emblem="star", text="VLT")),
    # 6. STEP — wide raised back tier with the riser light line, leaning back wall, frosted front lip, screen in the F-row
    "step": Env(name="Step", bez=(9.0, 9.0, 14.0, 8.0), corners=(("r", 2.0),) * 4, top_z=7.5, deck_raise=3.0, tilt=6.0, h_front=20.0,
                bottom_off=(0.0, 0.0, -4.0, 0.0), top_chamfer=1.2, screen="frow", top_light=("side_lines",), front_light="lip",
                underglow="ring", weight=dict(kind="plate", size=(240.0, 80.0, 3.0, 12.0), pocket=2.0, text="VLT")),
}
