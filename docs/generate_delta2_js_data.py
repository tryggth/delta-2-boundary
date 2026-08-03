import sys
sys.path.append('/home/tryggth2009/spectre-delta-boundary')
import spectre_boundary_solver as sbs
from shapely.geometry import Polygon
from shapely.ops import unary_union
import numpy as np
import json

# Generate Delta_2 patch from solver
patch = sbs.generate_inflated_patch('Delta', 2, sbs.LatticePoint(0,0,0,0), 0, reflected=False)
raw_tiles_pts = [tile.vertices_float[:-1] for tile in patch]

# Divide all tile vertices by 2.0 (unit edge L=1.0)
unit_tiles_pts = [[(x/2.0, y/2.0) for x, y in poly] for poly in raw_tiles_pts]

# Unary union to get exact boundary ring
shapely_polys = [Polygon(pts) for pts in unit_tiles_pts]
union_poly = unary_union(shapely_polys)
unit_boundary_coords = list(union_poly.exterior.coords)

# Calculate bounding box & center of the Delta_2 cluster
all_pts = np.array(unit_boundary_coords)
min_x, min_y = all_pts.min(axis=0)
max_x, max_y = all_pts.max(axis=0)

center_x = (min_x + max_x) / 2.0
center_y = (min_y + max_y) / 2.0

print(f"Unit bounding box: min=({min_x:.3f}, {min_y:.3f}), max=({max_x:.3f}, {max_y:.3f})")
print(f"Unit center: ({center_x:.3f}, {center_y:.3f})")

# Scale by SCALE = 40 (matching index.html tile scale)
SCALE = 40.0

# Shift so center of Delta_2 is at world origin (0, 0)
# (x_scaled, y_scaled) = ((x - center_x) * SCALE, -(y - center_y) * SCALE)
centered_boundary_verts = []
for x, y in unit_boundary_coords[:-1]: # exclude redundant closing point for clean vertex list
    cx = round((x - center_x) * SCALE, 3)
    cy = round(-(y - center_y) * SCALE, 3)
    centered_boundary_verts.append({'x': cx, 'y': cy})

print(f"Total centered boundary vertices: {len(centered_boundary_verts)}")
print("Sample centered boundary vertex 0:", centered_boundary_verts[0])

# Verify tile 0 shift
t0_shifted_origin_x = round((0.0 - center_x) * SCALE, 3)
t0_shifted_origin_y = round(-(0.0 - center_y) * SCALE, 3)
print(f"Tile 0 origin shifted: ({t0_shifted_origin_x}, {t0_shifted_origin_y})")

with open('delta2_js_data.json', 'w') as f:
    json.dump({
        'boundary_verts': centered_boundary_verts,
        'center_offset': {'x': round(center_x * SCALE, 3), 'y': round(-center_y * SCALE, 3)}
    }, f, indent=2)

print("Saved delta2_js_data.json successfully!")
