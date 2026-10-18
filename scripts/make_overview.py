from PIL import Image, ImageDraw, ImageFont
import glob, os

variants = [
    ("01_variant_bilateral_gala.jpg", "Variant 1: 经典双侧对流庆典展翼构图 (Bilateral Gala)"),
    ("02_variant_panoramic_skyline.jpg", "Variant 2: 全景连贯学院天际线横卷构图 (Panoramic Skyline)"),
    ("03_variant_monumental_center.jpg", "Variant 3: 殿堂式主楼向心聚焦构图 (Monumental Center)"),
    ("04_variant_physical_sandtable.jpg", "Variant 4: 多层次景深立体沙盘展台构图 (Physical Sandtable)"),
    ("05_variant_golden_luminous_night.jpg", "Variant 5: 鎏金夜景泛光与发光视窗庆典版 (Golden Night)"),
    ("06_variant_minimalist_papercraft.jpg", "Variant 6: 极致极简纯净纸雕浮雕构图 (Minimalist Papercraft)"),
    ("07_variant_anniversary_grandeur.jpg", "Variant 7: 华章庆典金色光晕与全景大师构图 (Anniversary Grandeur)"),
    ("08_variant_gold_foil_emboss.jpg", "Variant 8: 烫金立体浮雕与金属微光天际线 (Gold Foil Emboss)"),
]

cell_w, cell_h = 1000, 562
margin = 40
title_h = 50

grid_w = cell_w * 2 + margin * 3
grid_h = (cell_h + title_h + margin) * 4 + margin

canvas = Image.new("RGB", (grid_w, grid_h), (25, 20, 18))
draw = ImageDraw.Draw(canvas)

for idx, (filename, label) in enumerate(variants):
    r = idx // 2
    c = idx % 2
    x = margin + c * (cell_w + margin)
    y = margin + r * (cell_h + title_h + margin)
    
    img_path = os.path.join("/tmp/repo/campus_skyline_variants", filename)
    img = Image.open(img_path)
    img = img.resize((cell_w, cell_h), Image.Resampling.LANCZOS)
    canvas.paste(img, (x, y))
    
    draw.rectangle([x, y + cell_h, x + cell_w, y + cell_h + title_h], fill=(38, 30, 25))
    draw.text((x + 20, y + cell_h + 15), label, fill=(255, 220, 160))

overview_path = "/tmp/repo/campus_skyline_variants/00_all_variants_overview.jpg"
canvas.save(overview_path, quality=90)
print("Overview sheet generated successfully!")
