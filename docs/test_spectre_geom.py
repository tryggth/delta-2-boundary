import math
sqrt3 = math.sqrt(3)
spectre = [
    (0, 0),
    (1.0, 0.0),
    (1.5, -sqrt3/2),
    (1.5 + sqrt3/2, 0.5 - sqrt3/2), # (2.366, -0.366)
    (1.5 + sqrt3/2, 1.5 - sqrt3/2), # (2.366, 0.634)
    (2.5 + sqrt3/2, 1.5 - sqrt3/2), # (3.366, 0.634)
    (2.5 + sqrt3, 1.5),             # (3.866, 1.5)
    (3.0, 2.0),                     # (3.0, 2.0)
    (3.5 - sqrt3, 1.5),             # (2.134, 1.5)
    (2.5 - sqrt3/2, 1.5 + sqrt3/2), # (1.634, 2.366)
    (1.5 - sqrt3/2, 1.5 + sqrt3/2), # (0.634, 2.366)
    (0.5 - sqrt3/2, 1.5 + sqrt3/2), # (-0.366, 2.366)
    (0.0 - sqrt3/2, 1.5),           # (-0.866, 1.5)
    (0.0, 1.0)                      # (0.0, 1.0)
]

for i in range(14):
    p1 = spectre[i]
    p2 = spectre[(i+1)%14]
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    l = math.hypot(dx, dy)
    ang = round(math.degrees(math.atan2(dy, dx))) % 360
    print(f"Edge {i:2d}->{(i+1)%14:2d}: len={l:.4f}, ang={ang:3d}°")
