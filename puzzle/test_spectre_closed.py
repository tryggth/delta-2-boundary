import math
# The famous 14 edge directions for Spectre(1,1) (Hat with curved edges converted to straight segments):
# Angles: 0, 300, 30, 90, 0, 60, 150, 210, 120, 180, 240, 270, 330, 270 -- wait, let's test:
angles = [0, 300, 30, 90, 0, 60, 150, 210, 120, 180, 240, 300, 210, 150]
x, y = 0.0, 0.0
pts = [(0.0, 0.0)]
for deg in angles:
    rad = math.radians(deg)
    x += math.cos(rad)
    y += math.sin(rad)
    pts.append((x,y))

print(f"End point: {x:.6f}, {y:.6f}")
