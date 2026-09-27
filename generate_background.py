#!/usr/bin/env python3
"""生成高端新中式背景图 - 抽象山水意境"""

from PIL import Image, ImageDraw, ImageFilter, ImageEnhance
import math

# 画布尺寸 (1920x1080)
width, height = 1920, 1080
img = Image.new('RGB', (width, height), '#0a0c10')
draw = ImageDraw.Draw(img)

# 1. 创建渐变背景 - 深空蓝到墨黑
for y in range(height):
    ratio = y / height
    r = int(10 + ratio * 8)  # 10 -> 18
    g = int(12 + ratio * 6)  # 12 -> 18
    b = int(16 + ratio * 4)  # 16 -> 20
    draw.line([(0, y), (width, y)], fill=(r, g, b))

# 2. 添加抽象山峦轮廓 - 多层叠加
def draw_mountain(draw, points, color, blur_level=3):
    """绘制山脉轮廓"""
    mountain_img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
    mdraw = ImageDraw.Draw(mountain_img)

    # 绘制多边形
    mdraw.polygon(points, fill=color[:3], outline=None)

    # 添加模糊效果
    if blur_level > 0:
        mountain_img = mountain_img.filter(ImageFilter.GaussianBlur(blur_level))

    return mountain_img

# 远处山脉 - 最淡
far_mountain = [
    (0, 500), (200, 380), (400, 420), (600, 350),
    (800, 400), (1000, 320), (1200, 380), (1400, 300),
    (1600, 360), (1800, 320), (1920, 350), (1920, height), (0, height)
]
far_layer = draw_mountain(draw, far_mountain, (25, 28, 35), blur_level=2)
img.paste(Image.alpha_composite(Image.new('RGBA', img.size, (0, 0, 0, 0)), far_layer), (0, 0))

# 中层山脉
mid_mountain = [
    (0, 600), (150, 520), (350, 560), (500, 480),
    (700, 530), (900, 450), (1100, 500), (1300, 420),
    (1500, 480), (1700, 440), (1920, 480), (1920, height), (0, height)
]
mid_layer = draw_mountain(draw, mid_mountain, (18, 22, 30), blur_level=3)
img.paste(Image.alpha_composite(Image.new('RGBA', img.size, (0, 0, 0, 0)), mid_layer), (0, 0))

# 近处山脉 - 最深
near_mountain = [
    (0, 750), (100, 680), (250, 720), (400, 650),
    (600, 700), (800, 620), (1000, 680), (1200, 600),
    (1400, 660), (1600, 620), (1800, 680), (1920, 650),
    (1920, height), (0, height)
]
near_layer = draw_mountain(draw, near_mountain, (12, 15, 22), blur_level=4)
img.paste(Image.alpha_composite(Image.new('RGBA', img.size, (0, 0, 0, 0)), near_layer), (0, 0))

# 3. 添加雾气效果 - 柔和渐变
for i in range(200):
    y = 400 + i * 2
    alpha = int(15 * (1 - i / 200))
    if alpha > 0:
        for x in range(0, width, 50):
            noise = int(math.sin(x * 0.01) * 5)
            draw.ellipse(
                [x - 25, y - 10 + noise, x + 25, y + 10 + noise],
                fill=(30 + alpha, 35 + alpha, 45 + alpha)
            )

# 4. 添加金色光晕 - 月亮/太阳位置
center_x, center_y = 960, 400
for radius in range(200, 0, -5):
    alpha = int(8 * (1 - radius / 200))
    if alpha > 0:
        color = (201 + alpha, 169 + alpha, 98)
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            fill=color
        )

# 添加光晕扩散
for radius in range(300, 100, -10):
    alpha = int(3 * (1 - radius / 300))
    if alpha > 0:
        color = (201, 169, 98)
        draw.ellipse(
            [center_x - radius, center_y - radius, center_x + radius, center_y + radius],
            fill=tuple(min(c + alpha, 255) for c in color)
        )

# 5. 添加微妙粒子效果
import random
random.seed(42)  # 固定种子确保可复现

for _ in range(50):
    x = random.randint(0, width)
    y = random.randint(0, height)
    size = random.randint(1, 3)
    brightness = random.randint(40, 80)
    draw.ellipse([x, y, x + size, y + size], fill=(brightness, brightness + 5, brightness + 10))

# 6. 最终增强
img = ImageEnhance.Contrast(img).enhance(1.1)
img = ImageEnhance.Brightness(img).enhance(0.95)

# 保存
output_path = 'assets/hero-bg-v2.jpg'
img.save(output_path, 'JPEG', quality=95, optimize=True)
print(f"Background image saved to: {output_path}")
print(f"Size: {img.size}, Format: {img.format}")
