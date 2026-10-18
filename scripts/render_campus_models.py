import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFilter
import math

PALETTE = {
    'front': (255, 253, 250),
    'front_subtle': (248, 244, 238),
    'side_right': (200, 155, 110),
    'side_right_dark': (175, 130, 88),
    'side_left': (235, 215, 190),
    'top': (248, 228, 204),
    'top_bright': (255, 245, 230),
    'window': (215, 195, 175),
    'window_deep': (185, 155, 125),
    'groove': (195, 165, 135),
    'highlight': (255, 255, 255),
    'gold_accent': (255, 215, 130),
}

class ModelRenderer:
    def __init__(self, draw=None, image=None, width=2730, height=1535, dx=18, dy=-12):
        self.width = width
        self.height = height
        self.dx = dx
        self.dy = dy
        if image is not None:
            self.image = image
            self.draw = draw or ImageDraw.Draw(self.image)
        else:
            self.image = Image.new("RGBA", (width, height), (0, 0, 0, 0))
            self.draw = ImageDraw.Draw(self.image)

    def draw_prism(self, x, y, w, h, depth_scale=1.0, color_front=None, color_side=None, color_top=None):
        dx = self.dx * depth_scale
        dy = self.dy * depth_scale
        
        c_front = color_front or PALETTE['front']
        c_side = color_side or PALETTE['side_right']
        c_top = color_top or PALETTE['top']

        p_front = [(x, y - h), (x + w, y - h), (x + w, y), (x, y)]
        p_top = [(x, y - h), (x + dx, y - h + dy), (x + w + dx, y - h + dy), (x + w, y - h)]
        p_side = [(x + w, y - h), (x + w + dx, y - h + dy), (x + w + dx, y + dy), (x + w, y)]

        self.draw.polygon(p_top, fill=c_top)
        self.draw.polygon(p_side, fill=c_side)
        self.draw.polygon(p_front, fill=c_front)
        
        self.draw.line([(x, y - h), (x + w, y - h)], fill=PALETTE['highlight'] + (180,), width=1)
        self.draw.line([(x, y - h), (x, y)], fill=PALETTE['highlight'] + (140,), width=1)
        self.draw.line([(x + w, y - h), (x + w + dx, y - h + dy)], fill=PALETTE['highlight'] + (160,), width=1)

    def draw_cylinder(self, cx, y, r, h, depth_scale=1.0, segments=16):
        dx = self.dx * depth_scale
        dy = self.dy * depth_scale
        
        angles = np.linspace(np.pi, 0, segments + 1)
        top_pts = []
        for a in angles:
            px = cx + r * np.cos(a)
            py = y - h + r * 0.3 * np.sin(a)
            top_pts.append((px, py))
        
        for i in range(len(angles) - 1):
            a1, a2 = angles[i], angles[i+1]
            x1 = cx + r * np.cos(a1)
            x2 = cx + r * np.cos(a2)
            y_base1 = y + r * 0.3 * np.sin(a1)
            y_base2 = y + r * 0.3 * np.sin(a2)
            y_top1 = y - h + r * 0.3 * np.sin(a1)
            y_top2 = y - h + r * 0.3 * np.sin(a2)
            
            mid_a = (a1 + a2) / 2
            diffuse = (np.cos(mid_a - 0.8) + 1) / 2
            c_r = int(PALETTE['front'][0] * diffuse + PALETTE['side_right'][0] * (1 - diffuse))
            c_g = int(PALETTE['front'][1] * diffuse + PALETTE['side_right'][1] * (1 - diffuse))
            c_b = int(PALETTE['front'][2] * diffuse + PALETTE['side_right'][2] * (1 - diffuse))
            
            poly = [(x1, y_top1), (x2, y_top2), (x2, y_base2), (x1, y_base1)]
            self.draw.polygon(poly, fill=(c_r, c_g, c_b))
        
        self.draw.polygon(top_pts, fill=PALETTE['top'])
        self.draw.line(top_pts, fill=PALETTE['highlight'] + (200,), width=1)

def draw_car_tractor_01(mr, x, baseline_y, scale=1.0):
    """01 长春汽车拖拉机学院旧址 (Curved corner tower + classic wing + windows)"""
    wing_w = 260 * scale
    wing_h = 100 * scale
    tower_r = 45 * scale
    tower_h = 150 * scale
    
    mr.draw_prism(x, baseline_y, wing_w, 12 * scale, depth_scale=1.1, color_front=PALETTE['front_subtle'])
    mr.draw_prism(x, baseline_y - 12 * scale, wing_w - tower_r*0.6, wing_h, depth_scale=1.0)
    
    rows, cols = 2, 8
    win_w, win_h = 12 * scale, 24 * scale
    for r in range(rows):
        wy = baseline_y - 12 * scale - 18 * scale - r * 42 * scale
        for c in range(cols):
            wx = x + 16 * scale + c * 24 * scale
            mr.draw.rectangle([wx, wy - win_h, wx + win_w, wy], fill=PALETTE['window'])
            mr.draw.line([wx, wy - win_h, wx + win_w, wy - win_h], fill=PALETTE['window_deep'], width=1)

    mr.draw_prism(x - 4*scale, baseline_y - 12*scale - wing_h, wing_w - tower_r*0.5, 10 * scale, depth_scale=1.2, color_front=PALETTE['top_bright'])
    mr.draw_prism(x + 80 * scale, baseline_y, 40 * scale, 25 * scale, depth_scale=1.4)
    mr.draw_prism(x + 78 * scale, baseline_y - 25 * scale, 44 * scale, 6 * scale, depth_scale=1.5, color_front=PALETTE['top_bright'])

    tower_cx = x + wing_w - tower_r * 0.7
    mr.draw_cylinder(tower_cx, baseline_y, tower_r, tower_h, depth_scale=1.0)
    
    for fl in range(3):
        f_y = baseline_y - 30 * scale - fl * 40 * scale
        for a_deg in [135, 90, 45]:
            rad = math.radians(a_deg)
            wx = tower_cx + (tower_r - 2) * math.cos(rad)
            wy = f_y + (tower_r - 2) * 0.3 * math.sin(rad)
            mr.draw.rectangle([wx - 4*scale, wy - 18*scale, wx + 4*scale, wy], fill=PALETTE['window_deep'])
            
    mr.draw_cylinder(tower_cx, baseline_y - tower_h, tower_r + 3*scale, 8 * scale, depth_scale=1.0)
    mr.draw.line([(tower_cx, baseline_y - tower_h - 8*scale), (tower_cx, baseline_y - tower_h - 35*scale)], fill=PALETTE['highlight'], width=int(2*scale))
    return tower_cx, baseline_y - tower_h - 35*scale

def draw_chain_drive_07(mr, x, baseline_y, scale=1.0):
    """07 链传动研究所 (Modernist vertical fins / louvers + tiered cubic volumes)"""
    mr.draw_prism(x, baseline_y, 110 * scale, 75 * scale, depth_scale=1.0)
    for c in range(4):
        wx = x + 12*scale + c * 24*scale
        mr.draw.rectangle([wx, baseline_y - 60*scale, wx + 15*scale, baseline_y - 25*scale], fill=PALETTE['window'])

    tower_x = x + 100 * scale
    tower_w = 120 * scale
    tower_h = 165 * scale
    mr.draw_prism(tower_x, baseline_y, tower_w, tower_h, depth_scale=1.0)
    
    fin_count = 8
    fin_w = 6 * scale
    fin_spacing = (tower_w - 20 * scale) / fin_count
    for i in range(fin_count):
        fx = tower_x + 10 * scale + i * fin_spacing
        fy = baseline_y - 35 * scale
        fh = 115 * scale
        mr.draw_prism(fx, fy, fin_w, fh, depth_scale=0.7, color_front=PALETTE['front'], color_side=PALETTE['side_right_dark'])
        if i < fin_count - 1:
            mr.draw.rectangle([fx + fin_w, fy - fh, fx + fin_spacing, fy], fill=PALETTE['window_deep'])

    mr.draw_prism(tower_x - 15*scale, baseline_y, 70*scale, 28*scale, depth_scale=1.4)
    mr.draw_prism(tower_x - 18*scale, baseline_y - 28*scale, 76*scale, 7*scale, depth_scale=1.5, color_front=PALETTE['top_bright'])
    mr.draw_prism(tower_x - 10*scale, baseline_y, 6*scale, 28*scale, depth_scale=1.4, color_side=PALETTE['side_right_dark'])
    mr.draw_prism(tower_x + 40*scale, baseline_y, 6*scale, 28*scale, depth_scale=1.4, color_side=PALETTE['side_right_dark'])

    mr.draw_prism(tower_x + tower_w - 5*scale, baseline_y, 80 * scale, 120 * scale, depth_scale=0.9, color_front=PALETTE['front_subtle'])
    return tower_x + tower_w/2, baseline_y - tower_h

def draw_basic_science_04(mr, x, baseline_y, scale=1.0):
    """04 基础科学实验馆 (Grand monumental entrance staircase + stepped symmetry)"""
    total_w = 320 * scale
    center_w = 130 * scale
    center_x = x + (total_w - center_w) / 2
    
    mr.draw_prism(x, baseline_y, (total_w - center_w)/2 + 10*scale, 125 * scale, depth_scale=0.95)
    for r in range(4):
        wy = baseline_y - 20*scale - r * 25*scale
        for c in range(4):
            wx = x + 10*scale + c * 20*scale
            mr.draw.rectangle([wx, wy - 15*scale, wx + 12*scale, wy], fill=PALETTE['window'])

    mr.draw_prism(center_x + center_w - 10*scale, baseline_y, (total_w - center_w)/2 + 10*scale, 125 * scale, depth_scale=0.95)
    for r in range(4):
        wy = baseline_y - 20*scale - r * 25*scale
        for c in range(4):
            wx = center_x + center_w + c * 20*scale
            mr.draw.rectangle([wx, wy - 15*scale, wx + 12*scale, wy], fill=PALETTE['window'])

    center_h = 180 * scale
    mr.draw_prism(center_x, baseline_y, center_w, center_h, depth_scale=1.1)
    
    bay_count = 5
    bw = (center_w - 20*scale) / bay_count
    for b in range(bay_count):
        bx = center_x + 10*scale + b * bw
        for r in range(4):
            by = baseline_y - 65*scale - r * 25*scale
            mr.draw.rectangle([bx + 3*scale, by - 16*scale, bx + bw - 3*scale, by], fill=PALETTE['window_deep'])
            
    mr.draw_prism(center_x + 20*scale, baseline_y - center_h, center_w - 40*scale, 14 * scale, depth_scale=1.15, color_front=PALETTE['top_bright'])
    tip_y = baseline_y - center_h - 14*scale - 45*scale
    mr.draw.line([(center_x + center_w/2, baseline_y - center_h - 14*scale), (center_x + center_w/2, tip_y)], fill=PALETTE['highlight'], width=int(2*scale))

    stairs_w = 90 * scale
    stairs_x = center_x + (center_w - stairs_w) / 2
    steps_count = 6
    step_h = 6 * scale
    for s in range(steps_count):
        sw = stairs_w + (steps_count - s) * 5 * scale
        sx = center_x + (center_w - sw) / 2
        sy = baseline_y - s * step_h
        mr.draw_prism(sx, sy, sw, step_h, depth_scale=1.2 + (steps_count - s)*0.08, color_front=PALETTE['front_subtle'])

    mr.draw_prism(stairs_x + 10*scale, baseline_y - steps_count*step_h, stairs_w - 20*scale, 28 * scale, depth_scale=1.25)
    mr.draw_prism(stairs_x + 6*scale, baseline_y - steps_count*step_h - 28*scale, stairs_w - 12*scale, 8 * scale, depth_scale=1.3, color_front=PALETTE['top_bright'])
    return center_x + center_w/2, tip_y

def draw_materials_hall_05(mr, x, baseline_y, scale=1.0):
    """05 机械材料馆 (10-story grand academic complex)"""
    mr.draw_prism(x, baseline_y, 70*scale, 110*scale, depth_scale=0.9)
    for r in range(4):
        wy = baseline_y - 15*scale - r * 24*scale
        for c in range(2):
            wx = x + 10*scale + c * 26*scale
            mr.draw.rectangle([wx, wy - 14*scale, wx + 18*scale, wy], fill=PALETTE['window'])

    tower_x = x + 60*scale
    tower_w = 170*scale
    tower_h = 230*scale
    mr.draw_prism(tower_x, baseline_y, tower_w, tower_h, depth_scale=1.05)
    
    rows, cols = 7, 6
    for r in range(rows):
        wy = baseline_y - 25*scale - r * 26*scale
        for c in range(cols):
            wx = tower_x + 12*scale + c * 24*scale
            mr.draw.rectangle([wx, wy - 15*scale, wx + 16*scale, wy], fill=PALETTE['window'])
            mr.draw.line([wx + 8*scale, wy - 15*scale, wx + 8*scale, wy], fill=PALETTE['window_deep'], width=1)

    mr.draw_prism(tower_x + 30*scale, baseline_y - tower_h, 70*scale, 25*scale, depth_scale=1.1, color_front=PALETTE['front_subtle'])
    mr.draw_prism(tower_x + 115*scale, baseline_y - tower_h, 35*scale, 18*scale, depth_scale=1.1, color_front=PALETTE['front_subtle'])
    spire_tip = baseline_y - tower_h - 25*scale - 55*scale
    mr.draw.line([(tower_x + 50*scale, baseline_y - tower_h - 25*scale), (tower_x + 50*scale, spire_tip)], fill=PALETTE['highlight'], width=int(2*scale))

    right_x = tower_x + tower_w - 10*scale
    mr.draw_prism(right_x, baseline_y, 100*scale, 95*scale, depth_scale=0.95)
    for r in range(3):
        wy = baseline_y - 15*scale - r * 24*scale
        for c in range(3):
            wx = right_x + 12*scale + c * 26*scale
            mr.draw.rectangle([wx, wy - 14*scale, wx + 18*scale, wy], fill=PALETTE['window'])

    return tower_x + 50*scale, spire_tip

def draw_engineering_base_09(mr, x, baseline_y, scale=1.0):
    """09 工科基地 (Modernist block + landmark industrial chimney)"""
    chimney_x = x + 160*scale
    chimney_h = 240*scale
    chimney_w = 16*scale
    mr.draw_prism(chimney_x, baseline_y, chimney_w, chimney_h, depth_scale=0.7, color_front=PALETTE['front_subtle'])
    for s in range(4):
        sy = baseline_y - 120*scale - s * 30*scale
        mr.draw.rectangle([chimney_x, sy - 12*scale, chimney_x + chimney_w, sy], fill=PALETTE['side_right_dark'])

    block_w = 200*scale
    block_h = 135*scale
    mr.draw_prism(x, baseline_y, block_w, block_h, depth_scale=1.0)
    
    for r in range(3):
        wy = baseline_y - 25*scale - r * 38*scale
        mr.draw_prism(x + 15*scale, wy, block_w - 30*scale, 16*scale, depth_scale=0.9, color_front=PALETTE['window'], color_side=PALETTE['window_deep'])
        for m in range(7):
            mx = x + 15*scale + m * ((block_w - 30*scale)/7)
            mr.draw.line([mx, wy - 16*scale, mx, wy], fill=PALETTE['window_deep'], width=1)

    mr.draw_prism(x + 30*scale, baseline_y, 45*scale, 20*scale, depth_scale=1.3)
    return chimney_x + chimney_w/2, baseline_y - chimney_h

def draw_training_center_06(mr, x, baseline_y, scale=1.0):
    """06 工程训练中心 (Modern training building + rooftop truss sign)"""
    main_w = 220*scale
    main_h = 120*scale
    mr.draw_prism(x, baseline_y, main_w, main_h, depth_scale=1.0)
    
    for r in range(3):
        wy = baseline_y - 15*scale - r * 32*scale
        for c in range(8):
            wx = x + 12*scale + c * 24*scale
            mr.draw.rectangle([wx, wy - 18*scale, wx + 15*scale, wy], fill=PALETTE['window'])

    mr.draw_prism(x + 25*scale, baseline_y - main_h, main_w - 50*scale, 20*scale, depth_scale=1.05, color_front=PALETTE['top_bright'])
    mr.draw.rectangle([x + 35*scale, baseline_y - main_h - 15*scale, x + main_w - 35*scale, baseline_y - main_h - 5*scale], fill=PALETTE['window'])
    mr.draw_prism(x - 10*scale, baseline_y, main_w + 20*scale, 15*scale, depth_scale=1.3, color_front=PALETTE['front_subtle'])
    return x + main_w/2, baseline_y - main_h - 20*scale

def draw_historic_mech_02(mr, x, baseline_y, scale=1.0):
    """02 机械工程系旧址 (Historic pitched roofs + chimney)"""
    mr.draw_prism(x + 30*scale, baseline_y, 14*scale, 180*scale, depth_scale=0.7, color_front=PALETTE['side_right'])
    
    for i in range(2):
        bx = x + 50*scale + i * 85*scale
        bw = 80*scale
        bh = 70*scale
        mr.draw_prism(bx, baseline_y, bw, bh, depth_scale=1.0)
        for c in range(3):
            wx = bx + 10*scale + c * 22*scale
            mr.draw.rectangle([wx, baseline_y - 45*scale, wx + 14*scale, baseline_y - 15*scale], fill=PALETTE['window'])
        p_front_roof = [(bx, baseline_y - bh), (bx + bw/2, baseline_y - bh - 28*scale), (bx + bw, baseline_y - bh)]
        mr.draw.polygon(p_front_roof, fill=PALETTE['top_bright'])
        dx = mr.dx * 1.0
        dy = mr.dy * 1.0
        p_side_roof = [(bx + bw/2, baseline_y - bh - 28*scale), (bx + bw/2 + dx, baseline_y - bh - 28*scale + dy),
                       (bx + bw + dx, baseline_y - bh + dy), (bx + bw, baseline_y - bh)]
        mr.draw.polygon(p_side_roof, fill=PALETTE['side_right'])
    return x + 37*scale, baseline_y - 180*scale

def draw_teaching_bldg3_08(mr, x, baseline_y, scale=1.0):
    """08 三教正门 (Teaching Building 3 Entrance Portico + Courtyard Pavilion)"""
    main_w = 160 * scale
    main_h = 65 * scale
    mr.draw_prism(x, baseline_y, main_w, main_h, depth_scale=1.0)
    
    # Grand entrance canopy & columns
    canopy_w = 90 * scale
    canopy_x = x + (main_w - canopy_w) / 2
    canopy_h = 35 * scale
    # Entrance glass doors
    mr.draw.rectangle([canopy_x + 10*scale, baseline_y - canopy_h + 5*scale, canopy_x + canopy_w - 10*scale, baseline_y], fill=PALETTE['window_deep'])
    # Canopy slab
    mr.draw_prism(canopy_x - 5*scale, baseline_y - canopy_h, canopy_w + 10*scale, 10*scale, depth_scale=1.4, color_front=PALETTE['top_bright'])
    # Entrance columns
    mr.draw_prism(canopy_x + 5*scale, baseline_y, 8*scale, canopy_h, depth_scale=1.35, color_side=PALETTE['side_right_dark'])
    mr.draw_prism(canopy_x + canopy_w - 13*scale, baseline_y, 8*scale, canopy_h, depth_scale=1.35, color_side=PALETTE['side_right_dark'])
    # Steps
    mr.draw_prism(canopy_x - 10*scale, baseline_y, canopy_w + 20*scale, 8*scale, depth_scale=1.5, color_front=PALETTE['front_subtle'])
    return canopy_x + canopy_w/2, baseline_y - canopy_h - 10*scale

print("Refactored campus building models ready.")
