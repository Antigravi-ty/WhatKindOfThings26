import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from generate_hd_stage import generate_golden_stage
from test_pipeline import add_floor_reflection, add_building_uplight, add_starburst
from render_campus_models import *

W, H = 2730, 1535
HORIZON_Y = 1280

# 1. Base stage with celebratory golden warmth
stage = generate_golden_stage(W, H, HORIZON_Y, seed=707)

# Add celebratory golden aura / sunburst rays emanating from the center horizon
aura = Image.new("RGBA", (W, H), (0, 0, 0, 0))
adraw = ImageDraw.Draw(aura)
cx, cy = W // 2, HORIZON_Y
# Radial soft rays
for angle_deg in range(-75, 76, 5):
    rad = np.radians(angle_deg - 90)
    ray_len = 1100
    rx = cx + ray_len * np.cos(rad)
    ry = cy + ray_len * np.sin(rad)
    adraw.line([(cx, cy), (rx, ry)], fill=(255, 240, 200, 14), width=18)

# Center golden arc halo
adraw.arc([(cx - 450, cy - 450), (cx + 450, cy + 450)], start=190, end=350, fill=(255, 235, 180, 25), width=4)
adraw.arc([(cx - 520, cy - 520), (cx + 520, cy + 520)], start=195, end=345, fill=(255, 230, 170, 18), width=2)

aura = aura.filter(ImageFilter.GaussianBlur(35))
stage.paste(aura, (0, 0), aura)

# 2. Rich Multi-Scale Building Symphony
# Palette: Warm champagne ivory with rich bronze shadows
PALETTE['front'] = (255, 253, 248)
PALETTE['front_subtle'] = (248, 242, 234)
PALETTE['side_right'] = (205, 160, 115)
PALETTE['side_right_dark'] = (180, 135, 90)
PALETTE['top'] = (250, 232, 210)
PALETTE['window'] = (220, 200, 178)
PALETTE['window_deep'] = (195, 165, 135)

bg_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fg_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

mr_bg = ModelRenderer(image=bg_img, width=W, height=H, dx=14, dy=-9)
mr_fg = ModelRenderer(image=fg_img, width=W, height=H, dx=18, dy=-12)

# Background Layer across horizon
draw_engineering_base_09(mr_bg, x=140, baseline_y=HORIZON_Y, scale=0.85)
draw_materials_hall_05(mr_bg, x=620, baseline_y=HORIZON_Y, scale=0.88)
draw_training_center_06(mr_bg, x=1850, baseline_y=HORIZON_Y, scale=0.82)
draw_engineering_base_09(mr_bg, x=2280, baseline_y=HORIZON_Y, scale=0.90)

# Foreground Master Arrangement:
# Left cluster (Historical roots & science):
p1_x, p1_y = draw_historic_mech_02(mr_fg, x=40, baseline_y=HORIZON_Y, scale=1.05)
p2_x, p2_y = draw_car_tractor_01(mr_fg, x=240, baseline_y=HORIZON_Y, scale=1.20)
p3_x, p3_y = draw_basic_science_04(mr_fg, x=620, baseline_y=HORIZON_Y, scale=1.15)
draw_teaching_bldg3_08(mr_fg, x=1000, baseline_y=HORIZON_Y, scale=0.88)

# Center transition gateway:
draw_teaching_bldg3_08(mr_fg, x=1540, baseline_y=HORIZON_Y, scale=0.88)

# Right cluster (Modern engineering & future research):
p4_x, p4_y = draw_training_center_06(mr_fg, x=1710, baseline_y=HORIZON_Y, scale=0.96)
p5_x, p5_y = draw_chain_drive_07(mr_fg, x=1950, baseline_y=HORIZON_Y, scale=1.20)
p6_x, p6_y = draw_materials_hall_05(mr_fg, x=2220, baseline_y=HORIZON_Y, scale=1.24)


# Background fade
bg_arr = np.array(bg_img)
bg_arr[:, :, 3] = (bg_arr[:, :, 3] * 0.42).astype(np.uint8)
bg_faded = Image.fromarray(bg_arr)

# Combine
combined = Image.new("RGBA", (W, H), (0, 0, 0, 0))
combined.paste(bg_faded, (0, 0), bg_faded)
combined.paste(fg_img, (0, 0), fg_img)

# Uplight glow
combined = add_building_uplight(combined, HORIZON_Y)

# Stage floor reflection
stage_with_reflection = add_floor_reflection(stage, combined, HORIZON_Y)
stage_with_reflection.paste(combined, (0, 0), combined)

# Starbursts on peaks
add_starburst(stage_with_reflection, int(p2_x), int(p2_y), size=18)
add_starburst(stage_with_reflection, int(p3_x), int(p3_y), size=20)
add_starburst(stage_with_reflection, int(p5_x), int(p5_y), size=18)
add_starburst(stage_with_reflection, int(p6_x), int(p6_y), size=22)
add_starburst(stage_with_reflection, int(p1_x), int(p1_y), size=14)

# Horizon razor line
draw_final = ImageDraw.Draw(stage_with_reflection, "RGBA")
draw_final.line([(0, HORIZON_Y), (W, HORIZON_Y)], fill=(255, 255, 245, 235), width=2)

stage_with_reflection.save("/tmp/workspace/variant7_anniversary_grandeur.png", format="PNG")
stage_with_reflection.save("/tmp/workspace/variant7_anniversary_grandeur.jpg", quality=95)
print("Variant 7 generated successfully!")
