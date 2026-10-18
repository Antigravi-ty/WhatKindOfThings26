import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from generate_hd_stage import generate_golden_stage
from test_pipeline import add_floor_reflection, add_building_uplight, add_starburst
from render_campus_models import *

W, H = 2730, 1535
HORIZON_Y = 1280

# 1. Base stage with deeper evening golden tone
stage = generate_golden_stage(W, H, HORIZON_Y, seed=505)

# Adjust tone to deeper richer bronze evening
stage_arr = np.array(stage).astype(np.float32)
stage_arr[:, :, 0] = np.clip(stage_arr[:, :, 0] * 0.95 + 10, 0, 255) # R
stage_arr[:, :, 1] = np.clip(stage_arr[:, :, 1] * 0.90 + 5, 0, 255)  # G
stage_arr[:, :, 2] = np.clip(stage_arr[:, :, 2] * 0.82, 0, 255)      # B
stage = Image.fromarray(stage_arr.astype(np.uint8))

# 2. Add dramatic upward volumetric stage spotlights behind iconic buildings
spotlight_overlay = Image.new("RGBA", (W, H), (0, 0, 0, 0))
spot_draw = ImageDraw.Draw(spotlight_overlay)

# Beams behind:
# Beam 1: behind 01 Car-Tractor tower (x ~ 450)
spot_draw.polygon([(420, HORIZON_Y), (480, HORIZON_Y), (350, 100), (550, 100)], fill=(255, 235, 180, 28))
# Beam 2: behind 04 Science Hall (x ~ 800)
spot_draw.polygon([(760, HORIZON_Y), (840, HORIZON_Y), (700, 50), (950, 50)], fill=(255, 240, 190, 32))
# Beam 3: behind 07 Chain Drive (x ~ 2050)
spot_draw.polygon([(2010, HORIZON_Y), (2090, HORIZON_Y), (1950, 50), (2200, 50)], fill=(255, 240, 190, 32))
# Beam 4: behind 05 Materials Hall tower (x ~ 2350)
spot_draw.polygon([(2310, HORIZON_Y), (2390, HORIZON_Y), (2250, 80), (2480, 80)], fill=(255, 235, 180, 28))

spotlight_overlay = spotlight_overlay.filter(ImageFilter.GaussianBlur(65))
stage.paste(spotlight_overlay, (0, 0), spotlight_overlay)

# 3. Render buildings with illuminated glowing golden windows!
# We override window colors temporarily
PALETTE['window'] = (255, 228, 140)      # Glowing warm amber/gold
PALETTE['window_deep'] = (240, 195, 95)  # Golden window frames

bg_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
fg_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

mr_bg = ModelRenderer(image=bg_img, width=W, height=H, dx=14, dy=-10)
mr_fg = ModelRenderer(image=fg_img, width=W, height=H, dx=18, dy=-12)

# Background
draw_materials_hall_05(mr_bg, x=100, baseline_y=HORIZON_Y, scale=0.90)
draw_engineering_base_09(mr_bg, x=2200, baseline_y=HORIZON_Y, scale=0.92)

# Foreground Left
draw_historic_mech_02(mr_fg, x=50, baseline_y=HORIZON_Y, scale=1.0)
p1_x, p1_y = draw_car_tractor_01(mr_fg, x=230, baseline_y=HORIZON_Y, scale=1.18)
p2_x, p2_y = draw_basic_science_04(mr_fg, x=610, baseline_y=HORIZON_Y, scale=1.12)
draw_teaching_bldg3_08(mr_fg, x=960, baseline_y=HORIZON_Y, scale=0.88)

# Foreground Right
draw_teaching_bldg3_08(mr_fg, x=1580, baseline_y=HORIZON_Y, scale=0.88)
draw_training_center_06(mr_fg, x=1730, baseline_y=HORIZON_Y, scale=0.95)
p3_x, p3_y = draw_chain_drive_07(mr_fg, x=1970, baseline_y=HORIZON_Y, scale=1.18)
p4_x, p4_y = draw_materials_hall_05(mr_fg, x=2240, baseline_y=HORIZON_Y, scale=1.22)

# Restore default palette
PALETTE['window'] = (215, 195, 175)
PALETTE['window_deep'] = (185, 155, 125)

# Background fade
bg_arr = np.array(bg_img)
bg_arr[:, :, 3] = (bg_arr[:, :, 3] * 0.45).astype(np.uint8)
bg_faded = Image.fromarray(bg_arr)

# Combine buildings
combined = Image.new("RGBA", (W, H), (0, 0, 0, 0))
combined.paste(bg_faded, (0, 0), bg_faded)
combined.paste(fg_img, (0, 0), fg_img)

# Window bloom / outer glow on glowing windows
window_glow = fg_img.filter(ImageFilter.GaussianBlur(8))
w_arr = np.array(window_glow)
w_arr[:, :, 3] = (w_arr[:, :, 3] * 0.35).astype(np.uint8)
combined.paste(Image.fromarray(w_arr), (0, 0), Image.fromarray(w_arr))

# Base uplight
combined = add_building_uplight(combined, HORIZON_Y)

# Floor reflection
stage_with_reflection = add_floor_reflection(stage, combined, HORIZON_Y)
stage_with_reflection.paste(combined, (0, 0), combined)

# Add celebratory starbursts
add_starburst(stage_with_reflection, int(p1_x), int(p1_y), size=18)
add_starburst(stage_with_reflection, int(p2_x), int(p2_y), size=20)
add_starburst(stage_with_reflection, int(p3_x), int(p3_y), size=18)
add_starburst(stage_with_reflection, int(p4_x), int(p4_y), size=22)
add_starburst(stage_with_reflection, 470, 1150, size=14)
add_starburst(stage_with_reflection, 2150, 1140, size=14)

# Razor horizon light line
draw_final = ImageDraw.Draw(stage_with_reflection, "RGBA")
draw_final.line([(0, HORIZON_Y), (W, HORIZON_Y)], fill=(255, 255, 240, 240), width=2)

stage_with_reflection.save("/tmp/workspace/variant5_golden_luminous_night.png", format="PNG")
stage_with_reflection.save("/tmp/workspace/variant5_golden_luminous_night.jpg", quality=95)
print("Variant 5 generated successfully!")
