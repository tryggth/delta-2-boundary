import spectre_boundary_solver
from spectre_boundary_solver import get_candidate_tiles, LatticePoint, PlacedTile
from paths import trace_absolute_path_vertices
import json

locks = {
    "PATH_SEQ_3_00049": (2, 3, 2),
    "PATH_SEQ_3_00033": (0, 2, 0),
    "PATH_SEQ_4_00129": (3, -2, 3, 2),
    "PATH_SEQ_4_00074": (0, -2, 3, 2),
    "PATH_SEQ_4_00110": (2, 3, -2, 3)
}

# For each lock, we trace the boundary path vertices, and then run a mini-solver to find all valid completions.
# Since it is a lock, there should be exactly one tile at the origin that covers the first edge.

for name, step_path in locks.items():
    path_verts = trace_absolute_path_vertices(step_path)
    # The first edge goes from path_verts[0] to path_verts[1]
    # We find all candidate tiles that can cover this edge.
    src, dst = LatticePoint(*path_verts[0]), LatticePoint(*path_verts[1])
    candidates = get_candidate_tiles(src, dst)
    
    # Let's filter candidates to find which ones can tile the path without overlap.
    # Since we want to find the unique anchor tile for the path, we can print the candidate(s).
    print(f"\n{name} ({step_path}):")
    for c in candidates:
        # Check if the candidate's boundary is compatible with the turns.
        # Since it's a lock, there is usually only one candidate that fits locally.
        print(f"  Tile origin: {c.origin.to_tuple()}, orientation: {c.orientation}")
