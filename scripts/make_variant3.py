import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from generate_hd_stage import generate_golden_stage
from test_pipeline import add_floor_reflection, add_building_uplight, add_starburst
from render_campus_models import *

W, H = 2730, 1535
HORIZON_Y = 1280

# 1. Base stage with custom center spotlight illumination
stage = generate_golden_stage(W, H, HORIZON_Y, seed=303)

# Add a subtle majestic upward beam in the center behind the central hall
spotlight_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
spot_draw = ImageDraw.Draw(spotlight_overlay)
# Upward radiant trapezoid/fan beam behind center
beam_poly = [(W//2 - 90, HORIZON_Y), (W//2 + 90, HORIZON_Y), (W//2 + 400, 200), (W//2 - 400, 200)]
spot_draw.polygon(beam_poly, fill=(255, 240, 200, 35))
spotlight_overlay = spotlight_overlay.filter(ImageFilter.GaussianBlur(80))
stage.paste(spotlight_overlay, (0, 0), spotlight_overlay)

# 2. Building Layers
bg_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fg_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

mr_bg = ModelRenderer(image=bg_img, width=W, height=H, dx=14, dy=-10)
mr_fg = ModelRenderer(image=fg_img, width=W, height=H, dx=18, dy=-12)

# --- BACKGROUND LAYER ---
# Flanking towers in depth
draw_materials_hall_05(mr_bg, x=260, baseline_y=HORIZON_Y, scale=0.85)
draw_engineering_base_09(mr_bg, x=2050, baseline_y=HORIZON_Y, scale=0.88)
draw_training_center_06(mr_bg, x=1750, baseline_y=HORIZON_Y, scale=0.75)
draw_historic_mech_02(mr_bg, x=650, baseline_y=HORIZON_Y, scale=0.75)

# --- FOREGROUND CEREMONIAL HIERARCHY ---
# CENTERPIECE HERO: 04 基础科学实验馆 (Grand monumental staircase + stepped symmetry, enlarged to 1.35x!)
# Center is W//2 = 1365. Center hall total width at scale 1.35 is ~430px.
center_hall_x = 1365 - int(320 * 1.35 / 2) # ~1149
p_center_x, p_center_y = draw_basic_science_04(mr_fg, x=center_hall_x, baseline_y=HORIZON_Y, scale=1.35)

# LEFT WING COURT:
# Transition: 08 三教正门 pavilion leading to center hall
draw_teaching_bldg3_08(mr_fg, x=920, baseline_y=HORIZON_Y, scale=0.95)

# Left Anchor Hero: 01 长春汽车拖拉机学院旧址 (Iconic rounded corner tower facing inward!)
p_left_x, p_left_y = draw_car_tractor_01(mr_fg, x=530, baseline_y=HORIZON_Y, scale=1.20)

# Far Left Historic Heritage: 02 机械工程系旧址 (Pitched roofs + chimney)
p_farleft_x, p_farleft_y = draw_historic_mech_02(mr_fg, x=180, baseline_y=HORIZON_Y, scale=1.10)


# RIGHT WING COURT:
# Transition: 08 三教门楼 / 06 训练中心 leading from center hall to right
draw_teaching_bldg3_08(mr_fg, x=1600, baseline_y=HORIZON_Y, scale=0.95)

# Right Sculptural Hero: 07 链传动研究所 (Vertical louvers & tiered cubes, looking inward!)
p_right_x, p_right_y = draw_chain_drive_07(mr_fg, x=1820, baseline_y=HORIZON_Y, scale=1.22)

# Far Right Modern Anchor: 05 机械材料馆 (10-story grand academic complex)
p_farright_x, p_farright_y = draw_materials_hall_05(mr_fg, x=2150, baseline_y=HORIZON_Y, scale=1.25)


# Atmospheric fade on background
bg_arr = np.array(bg_img)
bg_arr[:, :, 3] = (bg_arr[:, :, 3] * 0.40).astype(np.uint8)
bg_faded = Image.fromarray(bg_arr)

# Combine buildings
combined = Image.new("RGBA", (W, H), (0, 0, 0, 0))
combined.paste(bg_faded, (0, 0), bg_faded)
combined.paste(fg_img, (0, 0), fg_img)

# Uplight glow
combined = add_building_uplight(combined, HORIZON_Y)

# Stage floor reflection
stage_with_reflection = add_floor_reflection(stage, combined, HORIZON_Y)

# Paste buildings
stage_with_reflection.paste(combined, (0, 0), combined)

# Add starburst glints on key architectural peaks
add_starburst(stage_with_reflection, int(p_center_x), int(p_center_y), size=24) # Majestic center starburst
add_starburst(stage_with_reflection, int(p_left_x), int(p_left_y), size=16)
add_starburst(stage_with_reflection, int(p_right_x), int(p_right_y), size=16)
add_starburst(stage_with_reflection, int(p_farright_x), int(p_farright_y), size=20)
add_starburst(stage_with_reflection, int(p_farleft_x), int(p_farleft_y), size=14)

# Razor horizon light line
draw_final = ImageDraw.Draw(stage_with_reflection, "RGBA")
draw_final.line([(0, HORIZON_Y), (W, HORIZON_Y)], fill=(255, 255, 250, 230), width=2)

stage_with_reflection.save("/tmp/workspace/variant3_monumental_center.png", format="PNG")
stage_with_reflection.save("/tmp/workspace/variant3_monumental_center.jpg", quality=95)
print("Variant 3 generated successfully!")
