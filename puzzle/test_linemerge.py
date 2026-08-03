import test_edges as te
from shapely.geometry import LineString, MultiLineString
from shapely.ops import linemerge

lines = [LineString([p1, p2]) for (p1, p2) in te.internal_edges]
merged = linemerge(lines)

if isinstance(merged, LineString):
    merged_lines = [merged]
elif isinstance(merged, MultiLineString):
    merged_lines = list(merged.geoms)

print(f"Number of merged internal path chains: {len(merged_lines)}")
for i, line in enumerate(merged_lines[:10]):
    print(f" Chain {i}: length {line.length:.3f}, num points: {len(line.coords)}")
