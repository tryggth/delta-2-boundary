import sys
sys.path.append('/home/tryggth2009/spectre-delta-boundary')
import spectre_boundary_solver as sbs
from shapely.geometry import Polygon
from shapely.ops import unary_union
import numpy as np
import math
import json

SQRT3 = math.sqrt(3)

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

def get_rotated_local_verts(rot_deg):
    rad = math.radians(rot_deg)
    c, s = math.cos(rad), math.sin(rad)
    return [(v[0]*c - v[1]*s, v[0]*s + v[1]*c) for v in local_verts]

# Generate Delta_2 patch
patch = sbs.generate_inflated_patch('Delta', 2, sbs.LatticePoint(0,0,0,0), 0, reflected=False)
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

# 4 distinct colors
COLORS = ["#6366f1", "#06b6d4", "#f59e0b", "#f43f5e"]

solved_placements = []
total_max_err = 0.0

for idx, poly_unit in enumerate(unit_tiles_pts):
    # Convert poly_unit to target SVG coordinates
    svg_target_poly = [((x - center_x)*SCALE, -(y - center_y)*SCALE) for x, y in poly_unit]
    
    best_rot = None
    best_tx = None
    best_ty = None
    min_err = Infinity if 'Infinity' in globals() else 1e9
    
    # Try all 12 rotation angles (0, 30, 60, ..., 330)
    for rot in range(0, 360, 30):
        rot_lverts = get_rotated_local_verts(rot)
        
        # Proposed translation (tx, ty) = avg(svg_target) - avg(rot_lverts)
        tx = sum(v[0] for v in svg_target_poly)/14.0 - sum(v[0] for v in rot_lverts)/14.0
        ty = sum(v[1] for v in svg_target_poly)/14.0 - sum(v[1] for v in rot_lverts)/14.0
        
        # Test error across all 14 vertices
        max_v_err = max(math.hypot(rot_lverts[i][0] + tx - svg_target_poly[i][0],
                                  rot_lverts[i][1] + ty - svg_target_poly[i][1])
                        for i in range(14))
        
        if max_v_err < min_err:
            min_err = max_v_err
            best_rot = rot
            best_tx = tx
            best_ty = ty
            
    if min_err > total_max_err:
        total_max_err = min_err
        
    solved_placements.append({
        "id": idx + 1,
        "x": round(best_tx, 3),
        "y": round(best_ty, 3),
        "rotationDeg": best_rot,
        "color": COLORS[idx % len(COLORS)]
    })

print(f"Max reconstruction error across all {len(solved_placements)} tiles: {total_max_err:.8f} pixels!")
with open('solved_placements.json', 'w') as f:
    json.dump(solved_placements, f, indent=2)

print("Saved solved_placements.json successfully!")
