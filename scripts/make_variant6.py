import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from generate_hd_stage import generate_golden_stage
from test_pipeline import add_floor_reflection, add_building_uplight, add_starburst
from render_campus_models import *

W, H = 2730, 1535
HORIZON_Y = 1280

# 1. Base stage with ultra-clean, subtle champagne glow
stage = generate_golden_stage(W, H, HORIZON_Y, seed=606)

# Pure papercraft palette: ultra-clean matte white with delicate subtle shading
PALETTE['front'] = (255, 255, 255)
PALETTE['front_subtle'] = (250, 248, 245)
PALETTE['side_right'] = (215, 185, 150)
PALETTE['side_right_dark'] = (195, 160, 125)
PALETTE['top'] = (252, 242, 230)
PALETTE['top_bright'] = (255, 255, 255)
PALETTE['window'] = (235, 222, 205)
PALETTE['window_deep'] = (210, 188, 165)

fg_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
mr_fg = ModelRenderer(image=fg_img, width=W, height=H, dx=15, dy=-10)

# Minimalist Elegant Rhythm (Left to Right):
# 1. Historic Heritage: 02 机械系旧址
p1_x, p1_y = draw_historic_mech_02(mr_fg, x=100, baseline_y=HORIZON_Y, scale=1.0)

# 2. Hero Corner Tower: 01 长春汽车拖拉机学院旧址
p2_x, p2_y = draw_car_tractor_01(mr_fg, x=290, baseline_y=HORIZON_Y, scale=1.15)

# 3. Grand Monument: 04 基础科学实验馆
p3_x, p3_y = draw_basic_science_04(mr_fg, x=680, baseline_y=HORIZON_Y, scale=1.10)

# 4. Courtyard Transition: 08 三教正门
draw_teaching_bldg3_08(mr_fg, x=1060, baseline_y=HORIZON_Y, scale=0.85)

# Open serene breathing space in center...

# 5. Engineering Training: 06 工程训练中心
draw_training_center_06(mr_fg, x=1540, baseline_y=HORIZON_Y, scale=0.88)

# 6. Modernist Fin Sculpture: 07 链传动研究所
p4_x, p4_y = draw_chain_drive_07(mr_fg, x=1800, baseline_y=HORIZON_Y, scale=1.15)

# 7. Anchor Complex: 05 机械材料馆
p5_x, p5_y = draw_materials_hall_05(mr_fg, x=2080, baseline_y=HORIZON_Y, scale=1.20)

# 8. Landmark Chimney Base: 09 工科基地
p6_x, p6_y = draw_engineering_base_09(mr_fg, x=2420, baseline_y=HORIZON_Y, scale=0.95)

# Uplight glow
fg_with_glow = add_building_uplight(fg_img, HORIZON_Y)

# Mirror reflection on glossy floor
stage_with_reflection = add_floor_reflection(stage, fg_with_glow, HORIZON_Y)
stage_with_reflection.paste(fg_with_glow, (0, 0), fg_with_glow)

# Delicate starbursts on pure white tips
add_starburst(stage_with_reflection, int(p2_x), int(p2_y), size=14)
add_starburst(stage_with_reflection, int(p3_x), int(p3_y), size=16)
add_starburst(stage_with_reflection, int(p4_x), int(p4_y), size=14)
add_starburst(stage_with_reflection, int(p5_x), int(p5_y), size=18)
add_starburst(stage_with_reflection, int(p6_x), int(p6_y), size=14)

# Horizon line
draw_final = ImageDraw.Draw(stage_with_reflection, "RGBA")
draw_final.line([(0, HORIZON_Y), (W, HORIZON_Y)], fill=(255, 255, 255, 240), width=2)

stage_with_reflection.save("/tmp/workspace/variant6_minimalist_papercraft.png", format="PNG")
stage_with_reflection.save("/tmp/workspace/variant6_minimalist_papercraft.jpg", quality=95)
print("Variant 6 generated successfully!")
