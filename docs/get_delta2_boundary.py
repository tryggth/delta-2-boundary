import sys
sys.path.append('/home/tryggth2009/spectre-delta-boundary')
import spectre_boundary_solver as sbs
from shapely.geometry import Polygon
from shapely.ops import unary_union
import math

# Generate Delta_2 patch from solver
patch = sbs.generate_inflated_patch('Delta', 2, sbs.LatticePoint(0,0,0,0), 0, reflected=False)
raw_tiles_pts = [tile.vertices_float[:-1] for tile in patch]

# Unary union to get exact boundary ring
shapely_polys = [Polygon(pts) for pts in raw_tiles_pts]
union_poly = unary_union(shapely_polys)
boundary_coords = list(union_poly.exterior.coords)

print(f"Number of boundary vertices: {len(boundary_coords)}")
print("First 5 boundary coords (raw solver scale):", boundary_coords[:5])

# Compare raw solver Spectre base tile vertices with index.html SPECTRE_BASE_VERTICES
# Raw solver Spectre tile 0 (origin 0, orientation 0, reflected False)
t0 = patch[0]
print("Solver Tile 0 origin:", t0.origin.to_float_coords())
print("Solver Tile 0 orientation:", t0.orientation)
print("Solver Tile 0 vertices:", t0.vertices_float[:3])
