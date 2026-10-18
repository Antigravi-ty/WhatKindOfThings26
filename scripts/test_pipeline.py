import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter

def add_floor_reflection(stage_img, building_layer, horizon_y=1280):
    """
    Creates a photorealistic glossy stage floor reflection:
    - Vertically mirrors the building layer below the horizon
    - Applies directional vertical surface roughness blur
    - Applies exponential Fresnel distance falloff
    - Blends smoothly with the reflective floor surface
    """
    w, h = stage_img.size
    
    b_arr = np.array(building_layer)
    alpha = b_arr[:, :, 3].astype(np.float32) / 255.0
    rgb = b_arr[:, :, :3].astype(np.float32)
    
    # Only keep stuff above horizon for reflection
    mask_above = np.zeros_like(alpha)
    mask_above[:horizon_y, :] = 1.0
    alpha = alpha * mask_above
    
    reflection_h = h - horizon_y
    if reflection_h <= 0:
        return stage_img
        
    src_crop_rgb = rgb[horizon_y - reflection_h : horizon_y, :, :][::-1, :, :]
    src_crop_alpha = alpha[horizon_y - reflection_h : horizon_y, :][::-1, :]
    
    # Vertical directional blur for floor sheen
    blurred_rgb = cv2.GaussianBlur(src_crop_rgb, (9, 35), 0)
    blurred_alpha = cv2.GaussianBlur(src_crop_alpha, (9, 25), 0)
    
    # Distance falloff below horizon
    y_dist = np.arange(reflection_h, dtype=np.float32)[:, None]
    falloff = np.exp(-y_dist / 75.0) * 0.65
    
    refl_alpha = np.clip(blurred_alpha * falloff, 0.0, 1.0)[:, :, None]
    
    # Tint reflection warm golden
    tint = np.array([1.0, 0.92, 0.80])
    refl_rgb = blurred_rgb * tint
    
    stage_arr = np.array(stage_img).astype(np.float32)
    stage_floor = stage_arr[horizon_y:, :, :3]
    
    blended_floor = stage_floor * (1.0 - refl_alpha) + refl_rgb * refl_alpha
    stage_arr[horizon_y:, :, :3] = np.clip(blended_floor, 0, 255)
    
    return Image.fromarray(stage_arr.astype(np.uint8))

def add_building_uplight(building_layer, horizon_y=1280):
    b_arr = np.array(building_layer).astype(np.float32)
    alpha = b_arr[:, :, 3] / 255.0
    
    h, w = b_arr.shape[:2]
    y_coords = np.arange(h)[:, None]
    
    dist_up = np.maximum(0.0, horizon_y - y_coords)
    uplight = np.exp(-dist_up / 70.0) * 80.0
    
    b_arr[:, :, 0] += uplight * alpha * 1.0
    b_arr[:, :, 1] += uplight * alpha * 0.90
    b_arr[:, :, 2] += uplight * alpha * 0.65
    
    return Image.fromarray(np.clip(b_arr, 0, 255).astype(np.uint8))

def add_starburst(img, x, y, size=16, color=(255, 255, 255, 240)):
    draw = ImageDraw.Draw(img, "RGBA")
    draw.line([(x - size, y), (x + size, y)], fill=color, width=2)
    draw.line([(x, y - size), (x, y + size)], fill=color, width=2)
    d_size = int(size * 0.5)
    draw.line([(x - d_size, y - d_size), (x + d_size, y + d_size)], fill=(color[0], color[1], color[2], color[3]//2), width=1)
    draw.line([(x - d_size, y + d_size), (x + d_size, y - d_size)], fill=(color[0], color[1], color[2], color[3]//2), width=1)
    draw.ellipse([(x - 2, y - 2), (x + 2, y + 2)], fill=(255, 255, 255, 255))
