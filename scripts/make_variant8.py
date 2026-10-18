import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from generate_hd_stage import generate_golden_stage
from test_pipeline import add_floor_reflection, add_building_uplight, add_starburst
from render_campus_models import *

W, H = 2730, 1535
HORIZON_Y = 1280

# 1. Base stage
stage = generate_golden_stage(W, H, HORIZON_Y, seed=808)

# 2. Gold-Foil & Metallic Champagne Relief Palette
PALETTE['front'] = (255, 248, 235)
PALETTE['front_subtle'] = (248, 238, 220)
PALETTE['side_right'] = (195, 145, 95)
PALETTE['side_right_dark'] = (165, 118, 72)
PALETTE['top'] = (255, 235, 205)
PALETTE['top_bright'] = (255, 248, 230)
PALETTE['window'] = (225, 195, 155)
PALETTE['window_deep'] = (185, 145, 105)
PALETTE['highlight'] = (255, 250, 230)

bg_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fg_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

mr_bg = ModelRenderer(image=bg_img, width=W, height=H, dx=14, dy=-9)
mr_fg = ModelRenderer(image=fg_img, width=W, height=H, dx=20, dy=-13)

# Background Layer:
draw_engineering_base_09(mr_bg, x=220, baseline_y=HORIZON_Y, scale=0.85)
draw_materials_hall_05(mr_bg, x=580, baseline_y=HORIZON_Y, scale=0.88)
draw_training_center_06(mr_bg, x=1820, baseline_y=HORIZON_Y, scale=0.82)
draw_engineering_base_09(mr_bg, x=2250, baseline_y=HORIZON_Y, scale=0.90)

# Foreground Layer (Dynamic Sinuous Skyline):
# Left:
p1_x, p1_y = draw_historic_mech_02(mr_fg, x=50, baseline_y=HORIZON_Y, scale=1.05)
p2_x, p2_y = draw_car_tractor_01(mr_fg, x=240, baseline_y=HORIZON_Y, scale=1.22)
p3_x, p3_y = draw_basic_science_04(mr_fg, x=640, baseline_y=HORIZON_Y, scale=1.15)
draw_teaching_bldg3_08(mr_fg, x=1020, baseline_y=HORIZON_Y, scale=0.90)

# Right:
draw_teaching_bldg3_08(mr_fg, x=1550, baseline_y=HORIZON_Y, scale=0.90)
p4_x, p4_y = draw_training_center_06(mr_fg, x=1710, baseline_y=HORIZON_Y, scale=0.98)
p5_x, p5_y = draw_chain_drive_07(mr_fg, x=1950, baseline_y=HORIZON_Y, scale=1.22)
p6_x, p6_y = draw_materials_hall_05(mr_fg, x=2220, baseline_y=HORIZON_Y, scale=1.26)

# Background fade
bg_arr = np.array(bg_img)
bg_arr[:, :, 3] = (bg_arr[:, :, 3] * 0.40).astype(np.uint8)
bg_faded = Image.fromarray(bg_arr)

# Combine
combined = Image.new("RGBA", (W, H), (0, 0, 0, 0))
combined.paste(bg_faded, (0, 0), bg_faded)
combined.paste(fg_img, (0, 0), fg_img)

# Gold-Foil Embossed Edge Enhancement:
# Extract edges of foreground buildings and overlay a delicate glowing gold wireframe
fg_edges = fg_img.filter(ImageFilter.FIND_EDGES)
fe_arr = np.array(fg_edges)
# Gold tint on edges
gold_edge = np.zeros_like(fe_arr)
edge_intensity = fe_arr[:, :, :3].mean(axis=-1) / 255.0
gold_edge[:, :, 0] = np.clip(edge_intensity * 255.0, 0, 255)
gold_edge[:, :, 1] = np.clip(edge_intensity * 225.0, 0, 255)
gold_edge[:, :, 2] = np.clip(edge_intensity * 150.0, 0, 255)
gold_edge[:, :, 3] = (np.clip(edge_intensity * 1.5, 0, 1.0) * 160).astype(np.uint8)
combined.paste(Image.fromarray(gold_edge), (0, 0), Image.fromarray(gold_edge))

# Uplight glow
combined = add_building_uplight(combined, HORIZON_Y)

# Stage floor reflection
stage_with_reflection = add_floor_reflection(stage, combined, HORIZON_Y)
stage_with_reflection.paste(combined, (0, 0), combined)

# Delicate starbursts
add_starburst(stage_with_reflection, int(p2_x), int(p2_y), size=18)
add_starburst(stage_with_reflection, int(p3_x), int(p3_y), size=20)
add_starburst(stage_with_reflection, int(p5_x), int(p5_y), size=18)
add_starburst(stage_with_reflection, int(p6_x), int(p6_y), size=22)
add_starburst(stage_with_reflection, int(p1_x), int(p1_y), size=14)

# Razor line
draw_final = ImageDraw.Draw(stage_with_reflection, "RGBA")
draw_final.line([(0, HORIZON_Y), (W, HORIZON_Y)], fill=(255, 250, 235, 240), width=2)

stage_with_reflection.save("/tmp/workspace/variant8_gold_foil_emboss.png", format="PNG")
stage_with_reflection.save("/tmp/workspace/variant8_gold_foil_emboss.jpg", quality=95)
print("Variant 8 generated successfully!")
