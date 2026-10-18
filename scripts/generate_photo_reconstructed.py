import os
import sys
import random
import cv2
import numpy as np
from PIL import Image, ImageFilter, ImageDraw

sys.path.append('/tmp')
from workspace.generate_hd_stage import generate_golden_stage
from workspace.test_pipeline import add_floor_reflection, add_building_uplight, add_starburst

OUTPUT_DIR = "/tmp/repo/campus_skyline_photo_reconstructed"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def get_clean_bbox_building(cid):
    path = f'/tmp/cutout_{cid}.png'
    im = Image.open(path).convert('RGBA')
    arr = np.array(im)
    alpha = arr[:, :, 3]
    y_solid = np.where(alpha > 20)[0]
    x_solid = np.where(alpha > 20)[1]
    if len(y_solid) == 0:
        return im
    return im.crop((x_solid.min(), y_solid.min(), x_solid.max() + 1, y_solid.max() + 1))

def shade_building_photo(cutout_img, 
                         light_dir=(0.55, -0.60, 0.65), 
                         style="champagne_plaster",
                         night_mode=False,
                         specular_power=1.5,
                         relief_strength=1.2):
    """
    High-fidelity Architectural Normal & Relief Shader
    Preserves 100% of the authentic photographic geometry, window mullions, 
    grand stairs, louvers, cornices, columns.
    """
    arr = np.array(cutout_img).astype(np.float32)
    alpha = arr[:, :, 3] / 255.0
    rgb = arr[:, :, :3]
    
    # 1. Luminance
    lum = 0.299 * rgb[:, :, 0] + 0.587 * rgb[:, :, 1] + 0.114 * rgb[:, :, 2]
    
    # 2. Edge-preserving bilateral filter
    lum_u8 = np.clip(lum, 0, 255).astype(np.uint8)
    smooth = cv2.bilateralFilter(lum_u8, d=9, sigmaColor=32, sigmaSpace=32).astype(np.float32)
    
    # 3. Gradients and Surface Normals
    gx = cv2.Sobel(smooth, cv2.CV_32F, 1, 0, ksize=3)
    gy = cv2.Sobel(smooth, cv2.CV_32F, 0, 1, ksize=3)
    
    lx, ly, lz = light_dir
    l_len = np.sqrt(lx*lx + ly*ly + lz*lz)
    lx, ly, lz = lx/l_len, ly/l_len, lz/l_len
    
    k = 0.055 * relief_strength
    nx = -k * gx
    ny = -k * gy
    nz = np.ones_like(nx)
    norm = np.sqrt(nx*nx + ny*ny + nz*nz) + 1e-6
    nx /= norm
    ny /= norm
    nz /= norm
    
    # Diffuse lighting
    diffuse = np.clip(nx * lx + ny * ly + nz * lz, 0.0, 1.0)
    
    # Structural details
    grad_mag = np.sqrt(gx*gx + gy*gy)
    edge_mask = np.clip(grad_mag / 24.0, 0.0, 1.0)
    norm_lum = smooth / 255.0
    
    # Combined lighting factor
    lit = 0.40 * diffuse + 0.60 * norm_lum
    lit = np.clip(lit, 0.0, 1.0)
    
    if style == "champagne_plaster":
        # Calibrated to exact percentiles of 参考图.png:
        r = 145.0 + 110.0 * (lit ** 0.8)
        g =  95.0 + 157.0 * (lit ** 1.1)
        b =  55.0 + 190.0 * (lit ** 1.4)
        
        recess = (1.0 - norm_lum) ** 1.4
        ao = 1.0 - recess * 0.35
        r *= ao
        g *= ao
        b *= ao
        
        bevel = np.clip(-ny * 0.7 - nx * 0.3, 0.0, 1.0) * edge_mask
        r += (bevel ** 3) * 65.0 * specular_power
        g += (bevel ** 3) * 55.0 * specular_power
        b += (bevel ** 3) * 45.0 * specular_power
        
    elif style == "gold_foil_emboss":
        # High contrast with metallic gold edges
        r = 150.0 + 105.0 * (lit ** 0.75)
        g = 100.0 + 150.0 * (lit ** 1.0)
        b =  50.0 + 175.0 * (lit ** 1.3)
        
        recess = (1.0 - norm_lum) ** 1.5
        ao = 1.0 - recess * 0.40
        r *= ao
        g *= ao
        b *= ao
        
        bevel = np.clip(-ny * 0.8 - nx * 0.3, 0.0, 1.0) * edge_mask
        r += (bevel ** 2) * 90.0 * specular_power
        g += (bevel ** 2) * 75.0 * specular_power
        b += (bevel ** 2) * 35.0 * specular_power
        
    elif style == "pure_alabaster":
        # Pure porcelain alabaster
        r = 170.0 + 85.0 * (lit ** 0.85)
        g = 140.0 + 115.0 * (lit ** 0.95)
        b = 110.0 + 145.0 * (lit ** 1.1)
        
        recess = (1.0 - norm_lum) ** 1.3
        ao = 1.0 - recess * 0.30
        r *= ao
        g *= ao
        b *= ao
        
        bevel = np.clip(-ny * 0.7 - nx * 0.3, 0.0, 1.0) * edge_mask
        r += (bevel ** 3) * 50.0 * specular_power
        g += (bevel ** 3) * 45.0 * specular_power
        b += (bevel ** 3) * 40.0 * specular_power

    if night_mode:
        # Window incandescent warm amber glow
        window_mask = (norm_lum < 0.38) * (edge_mask > 0.10)
        window_glow = cv2.GaussianBlur(window_mask.astype(np.float32), (7, 7), 0)
        r += window_glow * 175.0
        g += window_glow * 135.0
        b += window_glow *  45.0
        
    out_rgb = np.stack([r, g, b], axis=-1)
    out_rgb = np.clip(out_rgb, 0, 255).astype(np.uint8)
    out_alpha = (alpha * 255.0).astype(np.uint8)
    
    return Image.fromarray(np.dstack([out_rgb, out_alpha]))

def paste_with_drop_shadow(base_layer, elem_img, pos, shadow_offset=(18, 10), shadow_blur=23, shadow_opacity=0.48):
    """
    Pastes elem_img onto base_layer at pos=(x, y).
    If base_layer already has content, elem_img casts a soft contact drop shadow onto it.
    """
    w_base, h_base = base_layer.size
    ex, ey = pos
    
    elem_alpha = elem_img.split()[3]
    shadow_mask = Image.new("L", (w_base, h_base), 0)
    sx = ex + shadow_offset[0]
    sy = ey + shadow_offset[1]
    shadow_mask.paste(elem_alpha, (sx, sy))
    shadow_mask = shadow_mask.filter(ImageFilter.GaussianBlur(shadow_blur))
    
    base_arr = np.array(base_layer).astype(np.float32)
    s_arr = np.array(shadow_mask).astype(np.float32) / 255.0 * shadow_opacity
    
    for c in range(3):
        base_arr[:, :, c] = base_arr[:, :, c] * (1.0 - s_arr)
    base_layer = Image.fromarray(np.clip(base_arr, 0, 255).astype(np.uint8))
    
    base_layer.paste(elem_img, (ex, ey), elem_img)
    return base_layer

def finalize_and_save(stage, building_layer, horizon_y, output_path, flares=[]):
    """
    Combines stage, uplight, floor reflections, buildings, and optical flares.
    """
    print(f"Applying uplight and floor reflections for {os.path.basename(output_path)}...")
    b_lit = add_building_uplight(building_layer, horizon_y=horizon_y)
    final_img = add_floor_reflection(stage, b_lit, horizon_y=horizon_y)
    final_img.paste(b_lit, (0, 0), b_lit)
    
    for fx, fy, fsize in flares:
        add_starburst(final_img, fx, fy, size=fsize)
        
    final_img.save(output_path, quality=95)
    print(f"Saved: {output_path}")

# ==================== VARIANT 1 ====================
def generate_variant_01():
    print("\n--- Generating Variant 01: User Panorama Golden Relief ---")
    W, H = 2730, 1535
    horizon_y = 1260
    stage = generate_golden_stage(width=W, height=H, horizon_y=horizon_y, seed=101)
    building_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    
    b05 = shade_building_photo(get_clean_bbox_building('05'), style="champagne_plaster")
    b04 = shade_building_photo(get_clean_bbox_building('04'), style="champagne_plaster")
    b07 = shade_building_photo(get_clean_bbox_building('07'), style="champagne_plaster")
    b01 = shade_building_photo(get_clean_bbox_building('01'), style="champagne_plaster")
    
    # 05 (机械材料馆): Left flank
    h05 = 470
    w05 = int(b05.size[0] * (h05 / b05.size[1]))
    b05_s = b05.resize((w05, h05), Image.Resampling.LANCZOS)
    
    # 04 (基础科学实验馆): Mid-left, grand stairs
    h04 = 570
    w04 = int(b04.size[0] * (h04 / b04.size[1]))
    b04_s = b04.resize((w04, h04), Image.Resampling.LANCZOS)
    
    # 07 (链传动研究所): Center-right, iconic vertical louvers & tower
    h07 = 630
    w07 = int(b07.size[0] * (h07 / b07.size[1]))
    b07_s = b07.resize((w07, h07), Image.Resampling.LANCZOS)
    
    # 01 (汽车拖拉机学院旧址): Right flank, rounded tower & stepped wing
    h01 = 540
    w01 = int(b01.size[0] * (h01 / b01.size[1]))
    b01_s = b01.resize((w01, h01), Image.Resampling.LANCZOS)
    
    # Back to front placement with realistic drop shadows
    building_layer = paste_with_drop_shadow(building_layer, b05_s, (50, horizon_y - h05))
    building_layer = paste_with_drop_shadow(building_layer, b04_s, (680, horizon_y - h04))
    building_layer = paste_with_drop_shadow(building_layer, b07_s, (1330, horizon_y - h07))
    building_layer = paste_with_drop_shadow(building_layer, b01_s, (1960, horizon_y - h01))
    
    flares = [
        (1500, horizon_y - h07 + 35, 22),
        (2190, horizon_y - h01 + 30, 20),
        (980, horizon_y - h04 + 25, 18),
        (450, horizon_y - h05 + 40, 16)
    ]
    out_path = os.path.join(OUTPUT_DIR, "01_user_panorama_golden_relief.jpg")
    finalize_and_save(stage, building_layer, horizon_y, out_path, flares)

# ==================== VARIANT 2 ====================
def generate_variant_02():
    print("\n--- Generating Variant 02: Bilateral Gala Stage Framing ---")
    W, H = 2730, 1535
    horizon_y = 1260
    stage = generate_golden_stage(width=W, height=H, horizon_y=horizon_y, seed=202)
    building_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    
    # Symmetrical gala framing:
    # Left wing: 01 (汽车拖拉机学院旧址) + 05 (机械材料馆)
    # Right wing: 04 (基础科学实验馆) + 07 (链传动研究所)
    # Center: Open golden horizon for theatrical ceremony projection
    b01 = shade_building_photo(get_clean_bbox_building('01'), style="champagne_plaster")
    b05 = shade_building_photo(get_clean_bbox_building('05'), style="champagne_plaster")
    b04 = shade_building_photo(get_clean_bbox_building('04'), style="champagne_plaster")
    b07 = shade_building_photo(get_clean_bbox_building('07'), style="champagne_plaster")
    
    # Left side: 05 slightly recessed, 01 prominent in foreground
    h05 = 450
    w05 = int(b05.size[0] * (h05 / b05.size[1]))
    b05_s = b05.resize((w05, h05), Image.Resampling.LANCZOS)
    
    h01 = 580
    w01 = int(b01.size[0] * (h01 / b01.size[1]))
    b01_s = b01.resize((w01, h01), Image.Resampling.LANCZOS)
    
    # Right side: 07 recessed, 04 prominent in foreground
    h07 = 560
    w07 = int(b07.size[0] * (h07 / b07.size[1]))
    b07_s = b07.resize((w07, h07), Image.Resampling.LANCZOS)
    
    h04 = 600
    w04 = int(b04.size[0] * (h04 / b04.size[1]))
    b04_s = b04.resize((w04, h04), Image.Resampling.LANCZOS)
    
    # Paste Left Wing
    building_layer = paste_with_drop_shadow(building_layer, b05_s, (40, horizon_y - h05))
    building_layer = paste_with_drop_shadow(building_layer, b01_s, (320, horizon_y - h01))
    
    # Paste Right Wing
    building_layer = paste_with_drop_shadow(building_layer, b07_s, (1820, horizon_y - h07))
    building_layer = paste_with_drop_shadow(building_layer, b04_s, (1580, horizon_y - h04))
    
    flares = [
        (560, horizon_y - h01 + 30, 24),
        (1880, horizon_y - h04 + 25, 24),
        (2250, horizon_y - h07 + 35, 18),
        (1365, horizon_y - 20, 28) # Center stage light core flare
    ]
    out_path = os.path.join(OUTPUT_DIR, "02_bilateral_gala_stage.jpg")
    finalize_and_save(stage, building_layer, horizon_y, out_path, flares)

# ==================== VARIANT 3 ====================
def generate_variant_03():
    print("\n--- Generating Variant 03: Deep Perspective Multi-Tier Skyline ---")
    W, H = 2730, 1535
    horizon_y = 1260
    stage = generate_golden_stage(width=W, height=H, horizon_y=horizon_y, seed=303)
    building_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    
    # 3-Tier Layering:
    # Background: 09 (工科基地 with iconic brick chimney) + 02 (机械工程系旧址)
    # Midground: 07 (链传动研究所) + 06 (工程训练中心)
    # Foreground: 04 (基础科学实验馆, grand staircase hero) + 01 (汽车拖拉机学院旧址)
    b09 = shade_building_photo(get_clean_bbox_building('09'), style="champagne_plaster", relief_strength=1.0)
    b02 = shade_building_photo(get_clean_bbox_building('02'), style="champagne_plaster", relief_strength=1.1)
    b07 = shade_building_photo(get_clean_bbox_building('07'), style="champagne_plaster", relief_strength=1.3)
    b06 = shade_building_photo(get_clean_bbox_building('06'), style="champagne_plaster", relief_strength=1.2)
    b04 = shade_building_photo(get_clean_bbox_building('04'), style="champagne_plaster", relief_strength=1.4)
    b01 = shade_building_photo(get_clean_bbox_building('01'), style="champagne_plaster", relief_strength=1.3)
    
    # Tier 1: Background (tall silhouette)
    h09 = 680
    w09 = int(b09.size[0] * (h09 / b09.size[1]))
    b09_s = b09.resize((w09, h09), Image.Resampling.LANCZOS)
    
    h02 = 420
    w02 = int(b02.size[0] * (h02 / b02.size[1]))
    b02_s = b02.resize((w02, h02), Image.Resampling.LANCZOS)
    
    building_layer = paste_with_drop_shadow(building_layer, b09_s, (1750, horizon_y - h09), shadow_opacity=0.35)
    building_layer = paste_with_drop_shadow(building_layer, b02_s, (80, horizon_y - h02), shadow_opacity=0.35)
    
    # Tier 2: Midground
    h07 = 580
    w07 = int(b07.size[0] * (h07 / b07.size[1]))
    b07_s = b07.resize((w07, h07), Image.Resampling.LANCZOS)
    
    h06 = 460
    w06 = int(b06.size[0] * (h06 / b06.size[1]))
    b06_s = b06.resize((w06, h06), Image.Resampling.LANCZOS)
    
    building_layer = paste_with_drop_shadow(building_layer, b06_s, (450, horizon_y - h06), shadow_blur=25, shadow_opacity=0.45)
    building_layer = paste_with_drop_shadow(building_layer, b07_s, (1280, horizon_y - h07), shadow_blur=25, shadow_opacity=0.45)
    
    # Tier 3: Foreground Hero Buildings
    h04 = 620
    w04 = int(b04.size[0] * (h04 / b04.size[1]))
    b04_s = b04.resize((w04, h04), Image.Resampling.LANCZOS)
    
    h01 = 560
    w01 = int(b01.size[0] * (h01 / b01.size[1]))
    b01_s = b01.resize((w01, h01), Image.Resampling.LANCZOS)
    
    building_layer = paste_with_drop_shadow(building_layer, b04_s, (820, horizon_y - h04), shadow_blur=28, shadow_opacity=0.55)
    building_layer = paste_with_drop_shadow(building_layer, b01_s, (1950, horizon_y - h01), shadow_blur=28, shadow_opacity=0.55)
    
    flares = [
        (1980, horizon_y - h09 + 40, 26), # Tall chimney top
        (1120, horizon_y - h04 + 25, 24), # Grand stairs center
        (2200, horizon_y - h01 + 30, 22),
        (1450, horizon_y - h07 + 35, 20)
    ]
    out_path = os.path.join(OUTPUT_DIR, "03_deep_perspective_tiered.jpg")
    finalize_and_save(stage, building_layer, horizon_y, out_path, flares)

# ==================== VARIANT 4 ====================
def generate_variant_04():
    print("\n--- Generating Variant 04: Golden Night Illuminated Edition ---")
    W, H = 2730, 1535
    horizon_y = 1260
    stage = generate_golden_stage(width=W, height=H, horizon_y=horizon_y, seed=404)
    building_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    
    # Night mode: Shaded in champagne porcelain with warm glowing interior windows
    b08 = shade_building_photo(get_clean_bbox_building('08'), style="champagne_plaster", night_mode=True)
    b04 = shade_building_photo(get_clean_bbox_building('04'), style="champagne_plaster", night_mode=True)
    b07 = shade_building_photo(get_clean_bbox_building('07'), style="champagne_plaster", night_mode=True)
    b01 = shade_building_photo(get_clean_bbox_building('01'), style="champagne_plaster", night_mode=True)
    
    # 08 (机械三教正门): Left
    h08 = 520
    w08 = int(b08.size[0] * (h08 / b08.size[1]))
    b08_s = b08.resize((w08, h08), Image.Resampling.LANCZOS)
    
    # 04 (基础科学实验馆): Center
    h04 = 610
    w04 = int(b04.size[0] * (h04 / b04.size[1]))
    b04_s = b04.resize((w04, h04), Image.Resampling.LANCZOS)
    
    # 07 (链传动研究所): Mid-right
    h07 = 640
    w07 = int(b07.size[0] * (h07 / b07.size[1]))
    b07_s = b07.resize((w07, h07), Image.Resampling.LANCZOS)
    
    # 01 (汽车拖拉机学院旧址): Right
    h01 = 550
    w01 = int(b01.size[0] * (h01 / b01.size[1]))
    b01_s = b01.resize((w01, h01), Image.Resampling.LANCZOS)
    
    building_layer = paste_with_drop_shadow(building_layer, b08_s, (60, horizon_y - h08))
    building_layer = paste_with_drop_shadow(building_layer, b04_s, (650, horizon_y - h04))
    building_layer = paste_with_drop_shadow(building_layer, b07_s, (1320, horizon_y - h07))
    building_layer = paste_with_drop_shadow(building_layer, b01_s, (1960, horizon_y - h01))
    
    # Extra dramatic ground upward searchlights grazing the facades
    draw_light = ImageDraw.Draw(building_layer, "RGBA")
    searchlights = [(400, 1260), (1050, 1260), (1700, 1260), (2350, 1260)]
    for sx, sy in searchlights:
        # Draw soft cone
        cone = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        cdraw = ImageDraw.Draw(cone)
        cdraw.polygon([(sx, sy), (sx - 120, sy - 750), (sx + 120, sy - 750)], fill=(255, 235, 170, 32))
        cone = cone.filter(ImageFilter.GaussianBlur(35))
        building_layer.paste(Image.alpha_composite(Image.new("RGBA", (W, H), (0,0,0,0)), cone), (0, 0), cone)
        
    flares = [
        (1050, horizon_y - h04 + 20, 26),
        (1520, horizon_y - h07 + 35, 24),
        (2210, horizon_y - h01 + 25, 22),
        (420, horizon_y - h08 + 30, 20)
    ]
    out_path = os.path.join(OUTPUT_DIR, "04_golden_night_illuminated.jpg")
    finalize_and_save(stage, building_layer, horizon_y, out_path, flares)

# ==================== VARIANT 5 ====================
def generate_variant_05():
    print("\n--- Generating Variant 05: High-Relief Architectural Papercraft & Gold Foil ---")
    W, H = 2730, 1535
    horizon_y = 1260
    stage = generate_golden_stage(width=W, height=H, horizon_y=horizon_y, seed=505)
    building_layer = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    
    # High-Relief Papercraft style with gold foil edge highlights
    b05 = shade_building_photo(get_clean_bbox_building('05'), style="gold_foil_emboss", specular_power=2.0)
    b04 = shade_building_photo(get_clean_bbox_building('04'), style="gold_foil_emboss", specular_power=2.2)
    b07 = shade_building_photo(get_clean_bbox_building('07'), style="gold_foil_emboss", specular_power=2.0)
    b01 = shade_building_photo(get_clean_bbox_building('01'), style="gold_foil_emboss", specular_power=2.2)
    b08 = shade_building_photo(get_clean_bbox_building('08'), style="gold_foil_emboss", specular_power=2.0)
    
    # Monumental 5-building continuous relief
    h05 = 440
    w05 = int(b05.size[0] * (h05 / b05.size[1]))
    b05_s = b05.resize((w05, h05), Image.Resampling.LANCZOS)
    
    h08 = 520
    w08 = int(b08.size[0] * (h08 / b08.size[1]))
    b08_s = b08.resize((w08, h08), Image.Resampling.LANCZOS)
    
    h04 = 620
    w04 = int(b04.size[0] * (h04 / b04.size[1]))
    b04_s = b04.resize((w04, h04), Image.Resampling.LANCZOS)
    
    h07 = 640
    w07 = int(b07.size[0] * (h07 / b07.size[1]))
    b07_s = b07.resize((w07, h07), Image.Resampling.LANCZOS)
    
    h01 = 560
    w01 = int(b01.size[0] * (h01 / b01.size[1]))
    b01_s = b01.resize((w01, h01), Image.Resampling.LANCZOS)
    
    building_layer = paste_with_drop_shadow(building_layer, b05_s, (30, horizon_y - h05))
    building_layer = paste_with_drop_shadow(building_layer, b08_s, (450, horizon_y - h08))
    building_layer = paste_with_drop_shadow(building_layer, b04_s, (950, horizon_y - h04))
    building_layer = paste_with_drop_shadow(building_layer, b07_s, (1520, horizon_y - h07))
    building_layer = paste_with_drop_shadow(building_layer, b01_s, (2080, horizon_y - h01))
    
    flares = [
        (1240, horizon_y - h04 + 20, 26),
        (1700, horizon_y - h07 + 35, 24),
        (2280, horizon_y - h01 + 25, 24),
        (720, horizon_y - h08 + 25, 20)
    ]
    out_path = os.path.join(OUTPUT_DIR, "05_high_relief_papercraft_emboss.jpg")
    finalize_and_save(stage, building_layer, horizon_y, out_path, flares)

if __name__ == '__main__':
    generate_variant_01()
    generate_variant_02()
    generate_variant_03()
    generate_variant_04()
    generate_variant_05()
    print("\nAll 5 variants generated successfully!")
