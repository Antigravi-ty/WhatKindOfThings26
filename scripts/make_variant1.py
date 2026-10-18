import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from generate_hd_stage import generate_golden_stage
from test_pipeline import add_floor_reflection, add_building_uplight, add_starburst
from render_campus_models import *

W, H = 2730, 1535
HORIZON_Y = 1280

# 1. Base stage
stage = generate_golden_stage(W, H, HORIZON_Y, seed=101)

# 2. Building Layers
bg_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fg_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

mr_bg = ModelRenderer(image=bg_img, width=W, height=H, dx=14, dy=-10)
mr_fg = ModelRenderer(image=fg_img, width=W, height=H, dx=18, dy=-12)

# --- LEFT CLUSTER ---
# Background depth: Materials hall 05 in distance
draw_materials_hall_05(mr_bg, x=80, baseline_y=HORIZON_Y, scale=0.92)

# Midground: 02 Historic mechanical workshops
draw_historic_mech_02(mr_fg, x=50, baseline_y=HORIZON_Y, scale=1.0)

# Foreground Hero 1: 01 长春汽车拖拉机学院旧址
p1_x, p1_y = draw_car_tractor_01(mr_fg, x=220, baseline_y=HORIZON_Y, scale=1.15)

# Foreground Hero 2: 04 基础科学实验馆 (Grand hall + staircase)
p2_x, p2_y = draw_basic_science_04(mr_fg, x=580, baseline_y=HORIZON_Y, scale=1.10)

# Transition pavilion towards center: 08 三教正门
draw_teaching_bldg3_08(mr_fg, x=940, baseline_y=HORIZON_Y, scale=0.85)


# --- RIGHT CLUSTER ---
# Background depth: 09 Engineering base with chimney in distance
p_bg_x, p_bg_y = draw_engineering_base_09(mr_bg, x=2180, baseline_y=HORIZON_Y, scale=0.95)

# Transition pavilion towards center: 08 三教正门
draw_teaching_bldg3_08(mr_fg, x=1620, baseline_y=HORIZON_Y, scale=0.85)

# Midground Right: 06 工程训练中心
draw_training_center_06(mr_fg, x=1760, baseline_y=HORIZON_Y, scale=0.95)

# Foreground Hero 3: 07 链传动研究所 (Vertical fins + tiered cubes)
p3_x, p3_y = draw_chain_drive_07(mr_fg, x=1980, baseline_y=HORIZON_Y, scale=1.15)

# Foreground Hero 4: 05 机械材料馆 (10-story grand academic complex)
p4_x, p4_y = draw_materials_hall_05(mr_fg, x=2240, baseline_y=HORIZON_Y, scale=1.20)


# Fade background layer opacity to 40% for atmospheric depth
bg_arr = np.array(bg_img)
bg_arr[:, :, 3] = (bg_arr[:, :, 3] * 0.42).astype(np.uint8)
bg_faded = Image.fromarray(bg_arr)

# Combine buildings
combined = Image.new("RGBA", (W, H), (0, 0, 0, 0))
combined.paste(bg_faded, (0, 0), bg_faded)
combined.paste(fg_img, (0, 0), fg_img)

# Uplight glow at base of buildings
combined = add_building_uplight(combined, HORIZON_Y)

# Floor reflection onto stage
stage_with_reflection = add_floor_reflection(stage, combined, HORIZON_Y)

# Paste buildings onto stage
stage_with_reflection.paste(combined, (0, 0), combined)

# Add landmark starburst glints
add_starburst(stage_with_reflection, int(p1_x), int(p1_y), size=16)
add_starburst(stage_with_reflection, int(p2_x), int(p2_y), size=18)
add_starburst(stage_with_reflection, int(p3_x), int(p3_y), size=15)
add_starburst(stage_with_reflection, int(p4_x), int(p4_y), size=20)
add_starburst(stage_with_reflection, int(p_bg_x), int(p_bg_y), size=12)

# Crisp horizon ground line re-emphasis
draw_final = ImageDraw.Draw(stage_with_reflection, "RGBA")
draw_final.line([(0, HORIZON_Y), (W, HORIZON_Y)], fill=(255, 255, 250, 220), width=2)

stage_with_reflection.save("/tmp/workspace/variant1_bilateral_gala.png", format="PNG")
stage_with_reflection.save("/tmp/workspace/variant1_bilateral_gala.jpg", quality=95)
print("Variant 1 generated successfully!")
