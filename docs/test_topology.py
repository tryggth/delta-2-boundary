import test_spectre as ts
from shapely.geometry import Polygon, MultiPolygon, LineString, MultiLineString
from shapely.ops import unary_union, polygonize, linemerge
import numpy as np

# Generate raw Spectre tiles for Delta_2
sys_0 = ts.buildSpectreBase()
sys_1 = ts.buildSupertiles(sys_0)
sys_2 = ts.buildSupertiles(sys_1)

raw_tiles = sys_2['Delta'].get_tiles()
print(f"Total raw tiles: {len(raw_tiles)}")

# Convert each tile to Shapely Polygon
polygons = []
for label, pts in raw_tiles:
    p = Polygon(pts)
    if not p.is_valid:
        p = p.buffer(0)
    polygons.append(p)

# Unary union of all tiles
union_poly = unary_union(polygons)
print(f"Union geom type: {union_poly.geom_type}")
if union_poly.geom_type == 'Polygon':
    boundary = union_poly.exterior
    print(f"Boundary length: {boundary.length:.3f}, num coords: {len(boundary.coords)}")
elif union_poly.geom_type == 'MultiPolygon':
    print(f"Number of polygons in union: {len(union_poly.geoms)}")

