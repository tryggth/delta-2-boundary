import math
import numpy as np

SQRT3 = math.sqrt(3)

# Fixed Spectre base vertices
SPECTRE_BASE_VERTICES = [
    (0.0, 0.0),
    (1.0, 0.0),
    (1.5, -SQRT3 / 2),
    (1.5 + SQRT3 / 2, 0.5 - SQRT3 / 2),
    (1.5 + SQRT3 / 2, 1.5 - SQRT3 / 2),
    (2.5 + SQRT3 / 2, 1.5 - SQRT3 / 2),
    (3.0 + SQRT3 / 2, 1.5),
    (3.0, 2.0),
    (3.0 - SQRT3 / 2, 1.5),
    (2.5 - SQRT3 / 2, 1.5 + SQRT3 / 2),
    (1.5 - SQRT3 / 2, 1.5 + SQRT3 / 2),
    (0.5 - SQRT3 / 2, 1.5 + SQRT3 / 2),
    (-SQRT3 / 2, 1.5),
    (0.0, 1.0)
]

SCALE = 40.0
scaled_verts = [(x * SCALE, -y * SCALE) for x, y in SPECTRE_BASE_VERTICES]

centroid_x = sum(v[0] for v in scaled_verts) / 14.0
centroid_y = sum(v[1] for v in scaled_verts) / 14.0

local_verts = [(x - centroid_x, y - centroid_y) for x, y in scaled_verts]

def get_transformed_vertices(x, y, rotation_deg):
    rad = math.radians(rotation_deg)
    c, s = math.cos(rad), math.sin(rad)
    return [(v[0]*c - v[1]*s + x, v[0]*s + v[1]*c + y) for v in local_verts]

# Tile 1: placed at origin (0, 0), rot 0
t1 = get_transformed_vertices(0, 0, 0)

# Tile 2: placed so that vertex 0 of t2 matches vertex 1 of t1, rotated by 60 degrees
# Find offset: t2 vertex 0 must align with t1 vertex 1
t2_rot_local = get_transformed_vertices(0, 0, 60)
offset_x = t1[1][0] - t2_rot_local[0][0]
offset_y = t1[1][1] - t2_rot_local[0][1]

t2 = get_transformed_vertices(offset_x, offset_y, 60)

# Verify distance between matched vertices
d01 = math.hypot(t1[1][0] - t2[0][0], t1[1][1] - t2[0][1])
print(f"Matched vertex distance: {d01:.6f}")

# Check edge sharing distance
# Edge 1-2 of t1 should align with edge 0-13 of t2
d_edge = math.hypot(t1[2][0] - t2[13][0], t1[2][1] - t2[13][1])
print(f"Adjacent vertex alignment distance: {d_edge:.6f}")
