import numpy as np
from PIL import Image, ImageDraw, ImageFilter
from generate_hd_stage import generate_golden_stage
from test_pipeline import add_floor_reflection, add_building_uplight, add_starburst
from render_campus_models import *

W, H = 2730, 1535
HORIZON_Y = 1280

# 1. Base stage
stage = generate_golden_stage(W, H, HORIZON_Y, seed=404)

# 2. Three Distinct Depth Layers:
# Layer 0 (Back depth plane, baseline y = HORIZON_Y - 25, scaled 0.78x, soft drop shadow)
# Layer 1 (Mid depth plane, baseline y = HORIZON_Y - 12, scaled 0.95x)
# Layer 2 (Foreground depth plane, baseline y = HORIZON_Y, scaled 1.25x, high contrast)

l0_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
l1_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))
l2_img = Image.new("RGBA", (W, H), (0, 0, 0, 0))

mr0 = ModelRenderer(image=l0_img, width=W, height=H, dx=12, dy=-8)
mr1 = ModelRenderer(image=l1_img, width=W, height=H, dx=16, dy=-11)
mr2 = ModelRenderer(image=l2_img, width=W, height=H, dx=22, dy=-14)

# --- BACK LAYER (L0) ---
draw_engineering_base_09(mr0, x=180, baseline_y=HORIZON_Y - 30, scale=0.85)
draw_materials_hall_05(mr0, x=650, baseline_y=HORIZON_Y - 30, scale=0.85)
draw_training_center_06(mr0, x=1850, baseline_y=HORIZON_Y - 30, scale=0.82)
draw_engineering_base_09(mr0, x=2280, baseline_y=HORIZON_Y - 30, scale=0.90)

# --- MID LAYER (L1) ---
draw_historic_mech_02(mr1, x=80, baseline_y=HORIZON_Y - 14, scale=1.0)
draw_basic_science_04(mr1, x=480, baseline_y=HORIZON_Y - 14, scale=1.05)
draw_teaching_bldg3_08(mr1, x=920, baseline_y=HORIZON_Y - 14, scale=0.90)

draw_teaching_bldg3_08(mr1, x=1650, baseline_y=HORIZON_Y - 14, scale=0.90)
draw_chain_drive_07(mr1, x=1850, baseline_y=HORIZON_Y - 14, scale=1.08)
draw_training_center_06(mr1, x=2200, baseline_y=HORIZON_Y - 14, scale=1.0)

# --- FOREGROUND LAYER (L2 - Hero scale) ---
# Left Hero: 01 长春汽车拖拉机学院旧址 (Prominent corner tower stepping forward)
p_hero_left_x, p_hero_left_y = draw_car_tractor_01(mr2, x=240, baseline_y=HORIZON_Y, scale=1.28)

# Right Hero: 05 机械材料馆 (10-story grand academic complex stepping forward)
p_hero_right_x, p_hero_right_y = draw_materials_hall_05(mr2, x=2020, baseline_y=HORIZON_Y, scale=1.30)


# Generate soft drop shadow between layers to emphasize physical scale model sandtable depth
def generate_layer_shadow(layer_img, offset_x=12, offset_y=8, blur_radius=15, opacity=0.35):
    arr = np.array(layer_img)
    alpha = (arr[:, :, 3] * opacity).astype(np.uint8)
    shadow = Image.fromarray(alpha, mode='L')
    shadow_img = Image.new("RGBA", layer_img.size, (0, 0, 0, 0))
    # Black shadow with blurred alpha
    black = Image.new("RGBA", layer_img.size, (50, 30, 15, 255))
    shadow_img.paste(black, (offset_x, offset_y), shadow)
    return shadow_img.filter(ImageFilter.GaussianBlur(blur_radius))

shadow_l0 = generate_layer_shadow(l0_img, offset_x=10, offset_y=6, blur_radius=12, opacity=0.30)
shadow_l1 = generate_layer_shadow(l1_img, offset_x=14, offset_y=8, blur_radius=16, opacity=0.38)

# Fade back layer for atmospheric perspective
l0_arr = np.array(l0_img)
l0_arr[:, :, 3] = (l0_arr[:, :, 3] * 0.50).astype(np.uint8)
l0_faded = Image.fromarray(l0_arr)

# Assemble physical model stack
model_stack = Image.new("RGBA", (W, H), (0, 0, 0, 0))
model_stack.paste(l0_faded, (0, 0), l0_faded)
model_stack.paste(shadow_l1, (0, 0), shadow_l1)
model_stack.paste(l1_img, (0, 0), l1_img)
model_stack.paste(generate_layer_shadow(l2_img, 18, 10, 20, 0.45), (0, 0), generate_layer_shadow(l2_img, 18, 10, 20, 0.45))
model_stack.paste(l2_img, (0, 0), l2_img)

# Uplight glow from horizon line
model_stack = add_building_uplight(model_stack, HORIZON_Y)

# Stage floor reflection
stage_with_reflection = add_floor_reflection(stage, model_stack, HORIZON_Y)

# Paste physical models onto stage
stage_with_reflection.paste(model_stack, (0, 0), model_stack)

# Add starburst flares
add_starburst(stage_with_reflection, int(p_hero_left_x), int(p_hero_left_y), size=20)
add_starburst(stage_with_reflection, int(p_hero_right_x), int(p_hero_right_y), size=22)
add_starburst(stage_with_reflection, 740, 1055, size=16) # Basic Science hall peak
add_starburst(stage_with_reflection, 2030, 1060, size=16) # Chain Drive peak

# Razor ground line
draw_final = ImageDraw.Draw(stage_with_reflection, "RGBA")
draw_final.line([(0, HORIZON_Y), (W, HORIZON_Y)], fill=(255, 255, 250, 230), width=2)

stage_with_reflection.save("/tmp/workspace/variant4_physical_sandtable.png", format="PNG")
stage_with_reflection.save("/tmp/workspace/variant4_physical_sandtable.jpg", quality=95)
print("Variant 4 generated successfully!")
