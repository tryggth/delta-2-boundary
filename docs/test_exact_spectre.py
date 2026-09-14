import math
sqrt3 = math.sqrt(3)

# 14 steps along unit vector directions (angles in degrees: 0, 30, 60, 90, 120, 150, 180, 210, 240, 270, 300, 330)
# A standard Spectre tile is built from 14 unit steps:
# a = 1, b = 1 (Spectre(1,1)). The edge angles sequence:
angles_deg = [0, 300, 30, 90, 0, 60, 150, 210, 120, 180, 240, 270, 330, 270]

pts = [(0.0, 0.0)]
x, y = 0.0, 0.0
for a in angles_deg:
    rad = a * math.pi / 180.0
    x += math.cos(rad)
    y += math.sin(rad)
    pts.append((x, y))

print("Is closed? End point:", x, y)
print("Vertex count:", len(pts) - 1)
for i in range(14):
    print(f"v{i}: ({pts[i][0]:.4f}, {pts[i][1]:.4f})")
