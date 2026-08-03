import sys
sys.path.append('/home/tryggth2009/spectre-delta-boundary')
import spectre_boundary_solver as sbs
from shapely.geometry import Polygon
from shapely.ops import unary_union
import numpy as np

patch = sbs.generate_inflated_patch('Delta', 2, sbs.LatticePoint(0,0,0,0), 0, reflected=False)
raw_tiles_pts = [tile.vertices_float[:-1] for tile in patch]
unit_tiles_pts = [[(x/2.0, y/2.0) for x, y in poly] for poly in raw_tiles_pts]

shapely_polys = [Polygon(pts) for pts in unit_tiles_pts]
union_poly = unary_union(shapely_polys)
boundary_coords = list(union_poly.exterior.coords)[:-1]

boundary_set = set((round(x, 4), round(y, 4)) for x, y in boundary_coords)

# Check how many tile vertices land on the boundary set
matched_boundary_count = 0
for poly in unit_tiles_pts:
    for pt in poly:
        wpt = (round(pt[0], 4), round(pt[1], 4))
        if wpt in boundary_set:
            matched_boundary_count += 1

print(f"Total boundary vertices: {len(boundary_coords)}")
print(f"Total tile vertices landing on boundary: {matched_boundary_count}")
