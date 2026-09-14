import sys
sys.path.append('/home/tryggth2009/spectre-delta-boundary')
import spectre_boundary_solver as sbs
from shapely.geometry import Polygon
from shapely.ops import unary_union
import numpy as np
import json

patch = sbs.generate_inflated_patch('Delta', 2, sbs.LatticePoint(0,0,0,0), 0, reflected=False)
raw_tiles_pts = [tile.vertices_float[:-1] for tile in patch]

# Divide all tile vertices by 2.0 to convert to unit L=1.0 coordinates
unit_tiles_pts = [[(x/2.0, y/2.0) for x, y in poly] for poly in raw_tiles_pts]

shapely_polys = [Polygon(pts) for pts in unit_tiles_pts]
union_poly = unary_union(shapely_polys)
unit_boundary_coords = list(union_poly.exterior.coords)

print(f"Number of unit boundary coords: {len(unit_boundary_coords)}")

# Scale up for index.html (SCALE = 40, invert Y)
SCALE = 40.0

# Calculate centroid of unit_boundary_coords or align with workspace origin
scaled_boundary = [(x * SCALE, -y * SCALE) for x, y in unit_boundary_coords]

# Print JS array format for index.html
js_boundary_verts = [{"x": round(x, 4), "y": round(y, 4)} for x, y in scaled_boundary]

print("Sample JS boundary vertex 0:", js_boundary_verts[0])

# Save formatted JSON for embedding into index.html
with open('delta2_boundary_verts.json', 'w') as f:
    json.dump(js_boundary_verts, f)

print("Saved delta2_boundary_verts.json successfully!")
