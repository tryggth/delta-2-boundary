import math
sqrt3 = math.sqrt(3)

# Canonical Spectre 14 vertices from Smith, Myers, Kaplan, Goodman-Strauss (2023)
spectre_verts = [
    (0, 0),
    (1.0, 0.0),
    (1.5, -sqrt3/2),
    (1.5 + sqrt3/2, -0.5), # (2.366, -0.5)
    (1.5 + sqrt3/2, 0.5),  # (2.366, 0.5)
    (2.5 + sqrt3/2, 0.5),  # (3.366, 0.5)
    (3.0 + sqrt3/2, 0.5 + sqrt3/2), # (3.866, 1.366)
    (2.5 + sqrt3/2, 1.0 + sqrt3/2), # (3.366, 1.866)
    (1.5 + sqrt3/2, 1.0 + sqrt3/2), # (2.366, 1.866)
    (1.0 + sqrt3/2, 1.5 + sqrt3/2), # (1.866, 2.366)
    (sqrt3/2, 1.5 + sqrt3/2),       # (0.866, 2.366)
    (-0.5 + sqrt3/2, 1.5 + sqrt3/2),# (0.366, 2.366)
    (-0.5, 1.0 + sqrt3/2),          # (-0.5, 1.866)
    (-0.5, 0.5)                     # (-0.5, 0.5)
]

# Let's verify each edge length
for i in range(14):
    p1 = spectre_verts[i]
    p2 = spectre_verts[(i+1)%14]
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    l = math.hypot(dx, dy)
    ang = round(math.degrees(math.atan2(dy, dx))) % 360
    print(f"Edge {i:2d}->{(i+1)%14:2d}: len={l:.4f}, ang={ang:3d}°")
