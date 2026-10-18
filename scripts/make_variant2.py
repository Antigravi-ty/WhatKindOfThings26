import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from generate_hd_stage import generate_golden_stage
from test_pipeline import add_floor_reflection, add_building_uplight, add_starburst
from render_campus_models import *

W, H = 2730, 1535
HORIZON_Y = 1280

# 1. Base stage with seed for slight particle variation
stage = generate_golden_stage(W, H, HORIZON_Y, seed=202)

# 2. Building Layers (Background silhouettes + Midground + Foreground)
bg_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fg_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

mr_bg = ModelRenderer(image=bg_img, width=W, height=H, dx=12, dy=-8)
mr_fg = ModelRenderer(image=fg_img, width=W, height=H, dx=18, dy=-12)

# --- BACKGROUND SILHOUETTE LAYER (Deep Campus Skyline) ---
# Towering background silhouettes giving panoramic depth across the entire horizon
draw_materials_hall_05(mr_bg, x=150, baseline_y=HORIZON_Y, scale=0.88)
draw_engineering_base_09(mr_bg, x=750, baseline_y=HORIZON_Y, scale=0.85)
draw_training_center_06(mr_bg, x=1250, baseline_y=HORIZON_Y, scale=0.80)
draw_basic_science_04(mr_bg, x=1750, baseline_y=HORIZON_Y, scale=0.85)
draw_chain_drive_07(mr_bg, x=2280, baseline_y=HORIZON_Y, scale=0.85)

# --- FOREGROUND CONTINUOUS SKYLINE (From Left to Right) ---
# 1. Far Left: 02 机械工程系旧址 (Historic 1950s origins, pitched roofs + brick chimney)
draw_historic_mech_02(mr_fg, x=30, baseline_y=HORIZON_Y, scale=1.05)

# 2. Left Peak: 01 长春汽车拖拉机学院旧址 (Iconic rounded corner tower + 2-story wing)
p1_x, p1_y = draw_car_tractor_01(mr_fg, x=220, baseline_y=HORIZON_Y, scale=1.18)

# 3. Mid-Left Grand Hall: 04 基础科学实验馆 (Stepped symmetrical facade + monumental staircase)
p2_x, p2_y = draw_basic_science_04(mr_fg, x=600, baseline_y=HORIZON_Y, scale=1.12)

# 4. Center-Left Transition: 03 工程小院入口门廊
draw_historic_mech_02(mr_fg, x=980, baseline_y=HORIZON_Y, scale=0.68)

# 5. Center Landmark: 08 三教正门 (Teaching Building 3 Portico, grand canopy + entrance columns)
p_center_x, p_center_y = draw_teaching_bldg3_08(mr_fg, x=1180, baseline_y=HORIZON_Y, scale=1.15)

# 6. Center-Right Transition: 06 工程训练中心
draw_training_center_06(mr_fg, x=1420, baseline_y=HORIZON_Y, scale=0.92)

# 7. Mid-Right Sculptural Feature: 07 链传动研究所 (Modernist vertical fins / louvers + tiered cubes)
p3_x, p3_y = draw_chain_drive_07(mr_fg, x=1700, baseline_y=HORIZON_Y, scale=1.20)

# 8. Right Grand Complex: 05 机械材料馆 (10-story academic tower with dense window grid)
p4_x, p4_y = draw_materials_hall_05(mr_fg, x=2020, baseline_y=HORIZON_Y, scale=1.22)

# 9. Far Right Peak: 09 工科基地 (Clean modernist cubic facility + iconic industrial landmark chimney)
p5_x, p5_y = draw_engineering_base_09(mr_fg, x=2380, baseline_y=HORIZON_Y, scale=1.08)


# Atmospheric fade on background layer (38% opacity)
bg_arr = np.array(bg_img)
bg_arr[:, :, 3] = (bg_arr[:, :, 3] * 0.38).astype(np.uint8)
bg_faded = Image.fromarray(bg_arr)

# Combine buildings
combined = Image.new("RGBA", (W, H), (0, 0, 0, 0))
combined.paste(bg_faded, (0, 0), bg_faded)
combined.paste(fg_img, (0, 0), fg_img)

# Uplight glow at base of buildings
combined = add_building_uplight(combined, HORIZON_Y)

# Photorealistic floor reflection
stage_with_reflection = add_floor_reflection(stage, combined, HORIZON_Y)

# Paste buildings onto stage
stage_with_reflection.paste(combined, (0, 0), combined)

# Add landmark starburst glints across the panoramic skyline
add_starburst(stage_with_reflection, int(p1_x), int(p1_y), size=16)
add_starburst(stage_with_reflection, int(p2_x), int(p2_y), size=18)
add_starburst(stage_with_reflection, int(p_center_x), int(p_center_y), size=14)
add_starburst(stage_with_reflection, int(p3_x), int(p3_y), size=16)
add_starburst(stage_with_reflection, int(p4_x), int(p4_y), size=20)
add_starburst(stage_with_reflection, int(p5_x), int(p5_y), size=18)

# Razor horizon light line
draw_final = ImageDraw.Draw(stage_with_reflection, "RGBA")
draw_final.line([(0, HORIZON_Y), (W, HORIZON_Y)], fill=(255, 255, 250, 230), width=2)

stage_with_reflection.save("/tmp/workspace/variant2_panoramic_skyline.png", format="PNG")
stage_with_reflection.save("/tmp/workspace/variant2_panoramic_skyline.jpg", quality=95)
print("Variant 2 generated successfully!")
