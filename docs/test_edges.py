import test_spectre as ts
from collections import defaultdict
import numpy as np

sys_0 = ts.buildSpectreBase()
sys_1 = ts.buildSupertiles(sys_0)
sys_2 = ts.buildSupertiles(sys_1)

raw_tiles = sys_2['Delta'].get_tiles()

def round_pt(p, decimals=5):
    return (round(p[0], decimals), round(p[1], decimals))

edge_counts = defaultdict(int)
edge_map = {}

for label, pts in raw_tiles:
    # 14 vertices
    N = len(pts)
    for i in range(N):
        p1 = round_pt(pts[i])
        p2 = round_pt(pts[(i+1)%N])
        if p1 == p2:
            continue
        # Canonical edge key
        key = tuple(sorted([p1, p2]))
        edge_counts[key] += 1
        edge_map[key] = (p1, p2)

internal_edges = []
boundary_edges = []
other_edges = []

for key, count in edge_counts.items():
    if count == 2:
        internal_edges.append(key)
    elif count == 1:
        boundary_edges.append(key)
    else:
        other_edges.append((key, count))

print(f"Total unique edges: {len(edge_counts)}")
print(f"Internal edges (count=2): {len(internal_edges)}")
print(f"Boundary edges (count=1): {len(boundary_edges)}")
print(f"Other count edges: {len(other_edges)}")
