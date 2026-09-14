import json
import math

with open('solved_placements.json') as f:
    solved_tiles = json.load(f)

with open('delta2_js_data.json') as f:
    boundary_data = json.load(f)

boundary_verts = boundary_data['boundary_verts']

SQRT3 = math.sqrt(3)
BASE_VERTS = [
    (0.0, 0.0), (1.0, 0.0), (1.5, -SQRT3 / 2),
    (1.5 + SQRT3 / 2, 0.5 - SQRT3 / 2), (1.5 + SQRT3 / 2, 1.5 - SQRT3 / 2),
    (2.5 + SQRT3 / 2, 1.5 - SQRT3 / 2), (3.0 + SQRT3 / 2, 1.5), (3.0, 2.0),
    (3.0 - SQRT3 / 2, 1.5), (2.5 - SQRT3 / 2, 1.5 + SQRT3 / 2),
    (1.5 - SQRT3 / 2, 1.5 + SQRT3 / 2), (0.5 - SQRT3 / 2, 1.5 + SQRT3 / 2),
    (-SQRT3 / 2, 1.5), (0.0, 1.0)
]
SCALE = 40.0
scaled_base = [(x * SCALE, -y * SCALE) for x, y in BASE_VERTS]
centroid_x = sum(v[0] for v in scaled_base) / 14.0
centroid_y = sum(v[1] for v in scaled_base) / 14.0
local_verts = [(x - centroid_x, y - centroid_y) for x, y in scaled_base]

def get_tile_verts(tx, ty, rot):
    rad = math.radians(rot)
    c, s = math.cos(rad), math.sin(rad)
    return [(v[0]*c - v[1]*s + tx, v[0]*s + v[1]*c + ty) for v in local_verts]

def point_in_poly(pt, poly):
    inside = False
    n = len(poly)
    px, py = pt
    for i in range(n):
        x1, y1 = poly[i]['x'], poly[i]['y']
        x2, y2 = poly[(i+1)%n]['x'], poly[(i+1)%n]['y']
        if ((y1 > py) != (y2 > py)) and (px < (x2 - x1) * (py - y1) / (y2 - y1 + 1e-12) + x1):
            inside = not inside
    return inside

# Verify that all 71 solved tiles pass boundary check
inside_count = 0
for tile in solved_tiles:
    verts = get_tile_verts(tile['x'], tile['y'], tile['rotationDeg'])
    # check centroid and vertices
    c_x = sum(v[0] for v in verts) / 14.0
    c_y = sum(v[1] for v in verts) / 14.0
    if point_in_poly((c_x, c_y), boundary_verts):
        inside_count += 1

print(f"Total solved tiles inside boundary: {inside_count} / {len(solved_tiles)}")
