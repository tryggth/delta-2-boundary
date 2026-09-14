import math
from PIL import Image, ImageDraw

SQRT3 = math.sqrt(3)
BASE_VERTS = [
    (0.0, 0.0), (1.0, 0.0), (1.5, -SQRT3 / 2),
    (1.5 + SQRT3 / 2, 0.5 - SQRT3 / 2), (1.5 + SQRT3 / 2, 1.5 - SQRT3 / 2),
    (2.5 + SQRT3 / 2, 1.5 - SQRT3 / 2), (3.0 + SQRT3 / 2, 1.5), (3.0, 2.0),
    (3.0 - SQRT3 / 2, 1.5), (2.5 - SQRT3 / 2, 1.5 + SQRT3 / 2),
    (1.5 - SQRT3 / 2, 1.5 + SQRT3 / 2), (0.5 - SQRT3 / 2, 1.5 + SQRT3 / 2),
    (-SQRT3 / 2, 1.5), (0.0, 1.0)
]

def make_pwa_icon(size, is_maskable=False):
    # Dark slate background
    img = Image.new("RGBA", (size, size), (15, 23, 42, 255))
    draw = ImageDraw.Draw(img)

    # Calculate scaling & position
    scale = size / 6.5
    margin_factor = 0.8 if is_maskable else 0.95
    scale *= margin_factor

    cx_base = sum(v[0] for v in BASE_VERTS) / 14.0
    cy_base = sum(v[1] for v in BASE_VERTS) / 14.0

    scaled_pts = []
    for x, y in BASE_VERTS:
        px = (x - cx_base) * scale + size / 2.0
        py = -(y - cy_base) * scale + size / 2.0
        scaled_pts.append((px, py))

    # Draw subtle background glow
    if not is_maskable:
        glow_size = int(size * 0.45)
        glow_center = (size // 2, size // 2)
        # Gradient background circle
        draw.ellipse([size//2 - glow_size, size//2 - glow_size, size//2 + glow_size, size//2 + glow_size], fill=(99, 102, 241, 60))

    # Draw Spectre monotile polygon with indigo/cyan gradient fill simulation & white border
    draw.polygon(scaled_pts, fill=(99, 102, 241, 255), outline=(255, 255, 255, 255), width=max(2, int(size * 0.02)))

    return img

icon_192 = make_pwa_icon(192)
icon_192.save("icon-192.png")

icon_512 = make_pwa_icon(512)
icon_512.save("icon-512.png")

icon_maskable = make_pwa_icon(512, is_maskable=True)
icon_maskable.save("icon-maskable.png")

print("Generated icon-192.png, icon-512.png, icon-maskable.png successfully!")
