import sys
sys.path.append('/home/tryggth2009/spectre-delta-boundary')
import spectre_boundary_solver as sbs
from shapely.geometry import Polygon
from shapely.ops import unary_union
import numpy as np
import math
import json

SQRT3 = math.sqrt(3)

# Base Spectre tile vertices (unscaled L=1.0)
BASE_VERTS = [
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
scaled_base = [(x * SCALE, -y * SCALE) for x, y in BASE_VERTS]
centroid_x = sum(v[0] for v in scaled_base) / 14.0
centroid_y = sum(v[1] for v in scaled_base) / 14.0
local_verts = [(x - centroid_x, y - centroid_y) for x, y in scaled_base]

def get_rotated_verts(rot_deg):
    rad = math.radians(rot_deg)
    c, s = math.cos(rad), math.sin(rad)
    return [(v[0]*c - v[1]*s, v[0]*s + v[1]*c) for v in local_verts]

# Generate Delta_2 patch from solver
patch = sbs.generate_inflated_patch('Delta', 2, sbs.LatticePoint(0,0,0,0), 0, reflected=False)
print(f"Total tiles generated in patch: {len(patch)}")

raw_tiles_pts = [tile.vertices_float[:-1] for tile in patch]
unit_tiles_pts = [[(x/2.0, y/2.0) for x, y in poly] for poly in raw_tiles_pts]

shapely_polys = [Polygon(pts) for pts in unit_tiles_pts]
union_poly = unary_union(shapely_polys)
unit_boundary_coords = list(union_poly.exterior.coords)[:-1]

all_pts = np.array(unit_boundary_coords)
min_x, min_y = all_pts.min(axis=0)
max_x, max_y = all_pts.max(axis=0)
center_x = (min_x + max_x) / 2.0
center_y = (min_y + max_y) / 2.0

# Colors palette (4 distinct colors)
COLORS = ["#6366f1", "#06b6d4", "#f59e0b", "#f43f5e"] # Indigo, Cyan, Amber, Rose

solved_tiles_js = []

for idx, tile in enumerate(patch):
    # Get raw vertices divided by 2
    poly_unit = unit_tiles_pts[idx]
    
    # Orientation of tile from solver (0..11 corresponding to 0..330 degrees)
    # Solver orientation is in 30 deg steps (orientation * 30 deg counterclockwise)
    # Invert Y for SVG coordinates
    orient_deg = (tile.orientation * 30) % 360
    
    # Calculate expected local rotated vertices
    rot_verts = get_rotated_verts(orient_deg)
    
    # Real world SVG coordinates of vertices
    svg_poly = [( (x - center_x)*SCALE, -(y - center_y)*SCALE ) for x, y in poly_unit]
    
    # Shift tile origin (X, Y) so that rot_verts + (X, Y) == svg_poly
    # Calculate offset using average of all vertices
    avg_svg_x = sum(v[0] for v in svg_poly) / 14.0
    avg_svg_y = sum(v[1] for v in svg_poly) / 14.0
    
    avg_rot_x = sum(v[0] for v in rot_verts) / 14.0
    avg_rot_y = sum(v[1] for v in rot_verts) / 14.0
    
    tx = round(avg_svg_x - avg_rot_x, 3)
    ty = round(avg_svg_y - avg_rot_y, 3)
    
    color = COLORS[idx % len(COLORS)]
    
    solved_tiles_js.append({
        "id": idx + 1,
        "x": tx,
        "y": ty,
        "rotationDeg": orient_deg,
        "color": color
    })

print(f"Converted {len(solved_tiles_js)} solved tiles.")
print("Sample solved tile 0:", solved_tiles_js[0])

# Verify that solved tiles reconstruct the exact patch without error
max_error = 0
for idx, st in enumerate(solved_tiles_js):
    rot_verts = get_rotated_verts(st['rotationDeg'])
    reconstructed = [(v[0] + st['x'], v[1] + st['y']) for v in rot_verts]
    target_svg_poly = [((x - center_x)*SCALE, -(y - center_y)*SCALE) for x, y in unit_tiles_pts[idx]]
    for p1, p2 in zip(reconstructed, target_svg_poly):
        err = math.hypot(p1[0] - p2[0], p1[1] - p2[1])
        if err > max_error:
            max_error = err

print(f"Max reconstruction error: {max_error:.6f} pixels")

with open('solved_tiles_data.json', 'w') as f:
    json.dump(solved_tiles_js, f, indent=2)

