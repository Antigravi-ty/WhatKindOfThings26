import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
import random

def generate_golden_stage(width=2730, height=1535, horizon_y=1280, seed=42):
    np.random.seed(seed)
    random.seed(seed)
    
    # 1. Coordinate grids
    x = np.arange(width, dtype=np.float32)
    y = np.arange(height, dtype=np.float32)
    xx, yy = np.meshgrid(x, y)
    
    # Column parameters: period ~248.18 px (11 columns across 2730)
    col_period = width / 11.0  # ~248.18
    # Local coordinate within column [0..1)
    col_u = ((xx + 12.0) % col_period) / col_period
    
    # Column fluting profile:
    # A soft convex curve across the face, followed by a soft shadow crease on the right edge
    # Main face shading: gentle curve
    face_shading = np.cos((col_u - 0.46) * np.pi * 0.9) * 0.12 + 0.88
    # Edge groove: right 15% drops smoothly into warm shadow
    groove = np.clip((1.0 - col_u) / 0.14, 0.0, 1.0)
    # Smooth Hermite curve
    groove = groove * groove * (3.0 - 2.0 * groove)
    col_profile = face_shading * (0.80 + 0.20 * groove)
    
    # Gentle horizontal blur to match optical softness
    col_profile = cv2.GaussianBlur(col_profile, (15, 1), 0)
    
    # 2. Ambient Vertical Lighting
    # Vertical normalized coord above horizon
    y_wall = np.clip(yy / horizon_y, 0.0, 1.0)
    
    # Base wall colors (Champagne Gold / Bronze)
    # Top: R=218, G=168, B=118
    # Mid (y~0.6): R=205, G=152, B=102
    # Bottom (y~0.95): R=238, G=205, B=165
    top_c = np.array([218.0, 168.0, 118.0])
    mid_c = np.array([205.0, 152.0, 102.0])
    bot_c = np.array([238.0, 205.0, 165.0])
    
    wall_r = np.zeros_like(yy)
    wall_g = np.zeros_like(yy)
    wall_b = np.zeros_like(yy)
    
    mask_top = y_wall < 0.6
    t1 = y_wall / 0.6
    wall_r = np.where(mask_top, top_c[0]*(1-t1) + mid_c[0]*t1, 0)
    wall_g = np.where(mask_top, top_c[1]*(1-t1) + mid_c[1]*t1, 0)
    wall_b = np.where(mask_top, top_c[2]*(1-t1) + mid_c[2]*t1, 0)
    
    mask_bot = y_wall >= 0.6
    t2 = (y_wall - 0.6) / 0.4
    wall_r += np.where(mask_bot, mid_c[0]*(1-t2) + bot_c[0]*t2, 0)
    wall_g += np.where(mask_bot, mid_c[1]*(1-t2) + bot_c[1]*t2, 0)
    wall_b += np.where(mask_bot, mid_c[2]*(1-t2) + bot_c[2]*t2, 0)
    
    # Multiply by column profile
    wall_r *= col_profile
    wall_g *= col_profile
    wall_b *= col_profile
    
    # 3. Horizon Uplight Glow (strong atmospheric golden bloom near stage floor)
    dist_to_horizon = np.maximum(0.0, horizon_y - yy)
    glow_intense = np.exp(-dist_to_horizon / 55.0) * 190.0
    glow_broad = np.exp(-dist_to_horizon / 220.0) * 75.0
    
    wall_r += (glow_intense * 1.0 + glow_broad * 0.95)
    wall_g += (glow_intense * 0.95 + glow_broad * 0.82)
    wall_b += (glow_intense * 0.82 + glow_broad * 0.60)
    
    # 4. Reflective Floor below horizon
    dist_down = np.maximum(0.0, yy - horizon_y)
    # Bright immediate reflection zone
    floor_hot = np.exp(-dist_down / 18.0) * 240.0
    # Soft mid reflection zone
    floor_mid = np.exp(-dist_down / 95.0) * 115.0
    # Deep stage floor ambient
    floor_deep = np.exp(-dist_down / 280.0) * 35.0
    
    floor_r = floor_hot * 1.0 + floor_mid * 0.92 + floor_deep * 0.8 + 28.0
    floor_g = floor_hot * 0.96 + floor_mid * 0.72 + floor_deep * 0.4 + 18.0
    floor_b = floor_hot * 0.85 + floor_mid * 0.48 + floor_deep * 0.15 + 12.0
    
    # Merge above/below horizon
    is_wall = yy <= horizon_y
    final_r = np.where(is_wall, wall_r, floor_r)
    final_g = np.where(is_wall, wall_g, floor_g)
    final_b = np.where(is_wall, wall_b, floor_b)
    
    # Horizon light core beam (intense luminous golden razor line)
    beam_dist = np.abs(yy - horizon_y)
    core = np.exp(-beam_dist / 1.8) * 255.0
    halo = np.exp(-beam_dist / 6.0) * 140.0
    final_r += core + halo
    final_g += core * 0.98 + halo * 0.94
    final_b += core * 0.92 + halo * 0.82
    
    # Vignette
    cx = width / 2.0
    cy = height * 0.45
    dist_center = np.sqrt(((xx - cx) / cx)**2 + ((yy - cy) / cy)**2)
    vignette = 1.0 - 0.16 * np.clip(dist_center - 0.4, 0.0, 1.0)
    
    final_r = np.clip(final_r * vignette, 0, 255).astype(np.uint8)
    final_g = np.clip(final_g * vignette, 0, 255).astype(np.uint8)
    final_b = np.clip(final_b * vignette, 0, 255).astype(np.uint8)
    
    rgb = np.stack([final_r, final_g, final_b], axis=-1)
    img = Image.fromarray(rgb)
    
    # 5. Add floating golden bokeh particles & stardust
    draw = ImageDraw.Draw(img, "RGBA")
    
    # Large soft bokeh orbs
    for _ in range(45):
        bx = random.uniform(80, width - 80)
        by = random.uniform(200, horizon_y + 180)
        br = random.uniform(6, 28)
        alpha = random.randint(40, 110)
        # Warm golden color
        c = (255, random.randint(225, 245), random.randint(160, 200), alpha)
        # Draw soft circle
        # Create temp image for soft orb
        orb_dim = int(br * 4) + 4
        orb = Image.new("RGBA", (orb_dim, orb_dim), (0, 0, 0, 0))
        od = ImageDraw.Draw(orb)
        od.ellipse([(orb_dim//2 - br, orb_dim//2 - br), (orb_dim//2 + br, orb_dim//2 + br)], fill=c)
        orb = orb.filter(ImageFilter.GaussianBlur(br * 0.6))
        img.paste(orb, (int(bx - orb_dim//2), int(by - orb_dim//2)), orb)
        
    # Small sparkling stardust points
    for _ in range(160):
        sx = random.uniform(20, width - 20)
        sy = random.uniform(100, height - 30)
        sr = random.uniform(1.0, 2.5)
        alpha = random.randint(140, 255)
        c = (255, random.randint(240, 255), random.randint(210, 240), alpha)
        draw.ellipse([(sx - sr, sy - sr), (sx + sr, sy + sr)], fill=c)
        
    return img

if __name__ == '__main__':
    stage = generate_golden_stage()
    stage.save('/tmp/workspace/hd_golden_stage.jpg', quality=95)
    print('HD golden stage saved!')
