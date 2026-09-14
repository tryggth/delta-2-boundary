import math
sqrt3 = math.sqrt(3)

# Smith et al. Spectre 14-gon edges defined by step directions from origin.
# Stepping with unit length 1 in directions on 30° grid:
# Let e(deg) = (cos(deg), sin(deg))
# Let's test the 14-vertex sequence:
def e(deg):
    rad = math.radians(deg)
    return (math.cos(rad), math.sin(rad))

# Steps: 0°, 300°, 30°, 90°, 0°, 300°, 210°, 150°, 240°, 180°, 180°, 240°, 330°, 270°
# Let's test summing these steps:
steps = [0, 300, 30, 90, 0, 300, 210, 150, 240, 180, 180, 240, 330, 270]
x, y = 0.0, 0.0
pts = [(0.0, 0.0)]
for st in steps:
    dx, dy = e(st)
    x += dx
    y += dy
    pts.append((x, y))

print("Is loop closed? End:", round(x, 6), round(y, 6))
if abs(x) < 1e-5 and abs(y) < 1e-5:
    print("SUCCESS! 14 unit steps form a closed polygon!")
    for i in range(14):
        p1 = pts[i]
        p2 = pts[i+1]
        print(f"v{i}: ({p1[0]:.4f}, {p1[1]:.4f}) -> edge {steps[i]}°")
