import math
sqrt3 = math.sqrt(3)

# Base Spectre 14 vertices
spectre = [
    (0.0, 0.0),                                       # 0
    (1.0, 0.0),                                       # 1
    (1.5, -sqrt3 / 2),                                # 2
    (1.5 + sqrt3 / 2, -0.36602540378443865),          # 3
    (1.5 + sqrt3 / 2, 0.6339745962155614),           # 4
    (2.5 + sqrt3 / 2, 0.6339745962155614),           # 5
    (2.5 + sqrt3, 1.5),                               # 6
    (3.0, 2.0),                                       # 7
    (1.5 + sqrt3 / 2, 1.5),                           # 8
    (1.0 + sqrt3 / 2, 1.5 + sqrt3 / 2),               # 9
    (sqrt3 / 2, 1.5 + sqrt3 / 2),                     # 10
    (-0.5 + sqrt3 / 2, 1.5 + sqrt3 / 2),              # 11
    (-sqrt3 / 2, 1.5),                                # 12
    (0.0, 1.0)                                        # 13
]

print("Vertex count:", len(spectre))
edges = []
for i in range(len(spectre)):
    p1 = spectre[i]
    p2 = spectre[(i + 1) % len(spectre)]
    dx = p2[0] - p1[0]
    dy = p2[1] - p1[1]
    length = math.hypot(dx, dy)
    angle_deg = round(math.atan2(dy, dx) * 180 / math.pi) % 360
    print(f"Edge {i}->{(i+1)%14}: len={length:.4f}, angle={angle_deg}°")
