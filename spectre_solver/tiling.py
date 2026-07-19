from spectre_solver.geometry import (
    LatticePoint, PlacedTile, reflect_lattice_point,
    vec_to_dir, VEC_TO_DIR
)

# =====================================================================
# PHASE 3: SPECTRE MONOTILE INFLATION (STEP 1)
# =====================================================================
SUPER_RULES = {
    "Gamma":  ["Pi",  "Delta", None,  "Theta", "Sigma", "Xi",  "Phi",    "Gamma"],
    "Delta":  ["Xi",  "Delta", "Xi",  "Phi",   "Sigma", "Pi",  "Phi",    "Gamma"],
    "Theta":  ["Psi", "Delta", "Pi",  "Phi",   "Sigma", "Pi",  "Phi",    "Gamma"],
    "Lambda": ["Psi", "Delta", "Xi",  "Phi",   "Sigma", "Pi",  "Phi",    "Gamma"],
    "Xi":     ["Psi", "Delta", "Pi",  "Phi",   "Sigma", "Psi", "Phi",    "Gamma"],
    "Pi":     ["Psi", "Delta", "Xi",  "Phi",   "Sigma", "Psi", "Phi",    "Gamma"],
    "Sigma":  ["Xi",  "Delta", "Xi",  "Phi",   "Sigma", "Pi",  "Lambda", "Gamma"],
    "Phi":    ["Psi", "Delta", "Psi", "Phi",   "Sigma", "Pi",  "Phi",    "Gamma"],
    "Psi":    ["Psi", "Delta", "Psi", "Phi",   "Sigma", "Psi", "Phi",    "Gamma"]
}

CHILDREN_PARAMS = [
    {"grid_rot": 0, "offset": LatticePoint(0, 0, 0, 0)},
    {"grid_rot": 2, "offset": LatticePoint(2, 0, -1, 0)},
    {"grid_rot": 2, "offset": LatticePoint(1, 2, 1, -1)},
    {"grid_rot": 4, "offset": LatticePoint(2, 2, -1, -1)},
    {"grid_rot": 6, "offset": LatticePoint(1, 2, -2, -1)},
    {"grid_rot": 6, "offset": LatticePoint(3, 1, -3, -2)},
    {"grid_rot": 8, "offset": LatticePoint(1, 1, -2, -2)},
    {"grid_rot": 4, "offset": LatticePoint(0, -2, -3, 1)}
]

def generate_inflated_patch(supertile_type: str, generation: int, current_origin: LatticePoint, current_orientation: int, reflected: bool = False) -> list[PlacedTile]:
    if generation == 0:
        if supertile_type == 'Gamma':
            t1 = PlacedTile(current_origin, current_orientation % 12, reflected)
            ref_t = PlacedTile(LatticePoint(0,0,0,0), current_orientation % 12, reflected)
            idx = 6 if reflected else 8
            v8 = ref_t.vertices[idx]
            t2_origin = current_origin.add(v8)
            t2_orientation = (current_orientation + 1) % 12
            t2 = PlacedTile(t2_origin, t2_orientation, reflected)
            return [t1, t2]
        else:
            return [PlacedTile(current_origin, current_orientation % 12, reflected)]
        
    tiles = []
    substitutions = SUPER_RULES.get(supertile_type, [])
    for i, child_type in enumerate(substitutions):
        if child_type is None:
            continue
            
        child_grid_rot = CHILDREN_PARAMS[i]['grid_rot']
        base_offset = CHILDREN_PARAMS[i]['offset']
        if generation > 1 and i == 7:
            base_offset = LatticePoint(0, 2, -3, 1)
            
        child_offset = base_offset.inflate_n(generation - 1)
        
        if not reflected:
            child_orientation = (current_orientation + child_grid_rot) % 12
            rotated_offset = child_offset
            rot_steps = current_orientation % 12
        else:
            child_orientation = (-current_orientation + child_grid_rot) % 12
            rotated_offset = reflect_lattice_point(child_offset)
            rot_steps = (12 - current_orientation) % 12
            
        for _ in range(rot_steps):
            rotated_offset = rotated_offset.rot30()
            
        child_origin = current_origin.add(rotated_offset)
        tiles.extend(generate_inflated_patch(child_type, generation - 1, child_origin, child_orientation, not reflected))
        
    return tiles

# =====================================================================
# PHASE 4: BOUNDARY EXTRACTION (STEP 2)
# =====================================================================
def extract_perimeter_sequence(patch: list[PlacedTile]) -> list[int]:
    unique_patch = []
    seen = set()
    for t in patch:
        key = (t.origin.to_tuple(), t.orientation, t.reflected)
        if key not in seen:
            seen.add(key)
            unique_patch.append(t)
            
    edge_counts = {}
    for tile in unique_patch:
        for src, dst, d in tile.edges:
            canonical_key = tuple(sorted([src, dst]))
            edge_counts[canonical_key] = edge_counts.get(canonical_key, 0) + 1
            
    boundary_keys = {key for key, count in edge_counts.items() if count == 1}
    
    boundary_edges = []
    for tile in unique_patch:
        for src, dst, d in tile.edges:
            canonical_key = tuple(sorted([src, dst]))
            if canonical_key in boundary_keys:
                boundary_edges.append((src, dst, d))
                
    if not boundary_edges:
        return []
        
    adj = {}
    for src, dst, d in boundary_edges:
        if src not in adj: adj[src] = []
        adj[src].append((dst, d))
        
    start_vertex = boundary_edges[0][0]
    curr_vertex = start_vertex
    visited = set()
    loop = []
    
    while True:
        next_choices = adj.get(curr_vertex, [])
        next_vertex = None
        curr_d = None
        for dst, d in next_choices:
            edge_id = (curr_vertex, dst)
            if edge_id not in visited:
                next_vertex = dst
                curr_d = d
                visited.add(edge_id)
                break
        if next_vertex is None:
            break
        loop.append((curr_vertex, next_vertex, curr_d))
        curr_vertex = next_vertex
        if curr_vertex == start_vertex:
            break
            
    n = len(loop)
    turns = []
    for i in range(n):
        d_curr = loop[i][2]
        d_next = loop[(i+1)%n][2]
        diff = (d_next - d_curr) % 12
        if diff > 6: diff -= 12
        turns.append(STEP_TO_DEG_func(diff))
    return turns

def STEP_TO_DEG_func(step_val: int) -> int:
    # helper mapping step units directly to turn degrees
    STEP_TO_DEG = {-3: -90, -2: -60, 0: 0, 2: 60, 3: 90}
    return STEP_TO_DEG.get(step_val, 0)

def extract_boundary_loop(patch: list[PlacedTile]):
    unique_patch = []
    seen = set()
    for t in patch:
        key = (t.origin.to_tuple(), t.orientation, t.reflected)
        if key not in seen:
            seen.add(key)
            unique_patch.append(t)
            
    edge_counts = {}
    for tile in unique_patch:
        for src, dst, d in tile.edges:
            canonical_key = tuple(sorted([src, dst]))
            edge_counts[canonical_key] = edge_counts.get(canonical_key, 0) + 1
            
    boundary_keys = {key for key, count in edge_counts.items() if count == 1}
    
    boundary_edges = []
    for tile in unique_patch:
        for src, dst, d in tile.edges:
            canonical_key = tuple(sorted([src, dst]))
            if canonical_key in boundary_keys:
                boundary_edges.append((src, dst, d))
                
    if not boundary_edges:
        return [], []
        
    adj = {}
    for src, dst, d in boundary_edges:
        if src not in adj: adj[src] = []
        adj[src].append((dst, d))
        
    start_vertex = boundary_edges[0][0]
    curr_vertex = start_vertex
    visited = set()
    loop_vertices = [LatticePoint(*curr_vertex)]
    loop_edges = []
    
    while True:
        next_choices = adj.get(curr_vertex, [])
        next_vertex = None
        for dst, d in next_choices:
            edge_id = (curr_vertex, dst)
            if edge_id not in visited:
                next_vertex = dst
                visited.add(edge_id)
                break
        if next_vertex is None:
            break
        loop_edges.append((LatticePoint(*curr_vertex), LatticePoint(*next_vertex)))
        curr_vertex = next_vertex
        loop_vertices.append(LatticePoint(*curr_vertex))
        if curr_vertex == start_vertex:
            break
            
    boundary_poly = [v.to_point2d() for v in loop_vertices]
    return boundary_poly, loop_edges

def extract_boundary_loops_multi(patch: list[PlacedTile]) -> list[list[tuple[LatticePoint, LatticePoint]]]:
    """Extracts all boundary loops (outer perimeters and inner holes).
       Used to verify if a peeling step splits a patch topological structure."""
    unique_patch = []
    seen = set()
    for t in patch:
        key = (t.origin.to_tuple(), t.orientation, t.reflected)
        if key not in seen:
            seen.add(key)
            unique_patch.append(t)
            
    edge_counts = {}
    for tile in unique_patch:
        for src, dst, d in tile.edges:
            canonical_key = tuple(sorted([src, dst]))
            edge_counts[canonical_key] = edge_counts.get(canonical_key, 0) + 1
            
    boundary_keys = {key for key, count in edge_counts.items() if count == 1}
    
    boundary_edges = []
    for tile in unique_patch:
        for src, dst, d in tile.edges:
            canonical_key = tuple(sorted([src, dst]))
            if canonical_key in boundary_keys:
                boundary_edges.append((src, dst))
                
    if not boundary_edges:
        return []
        
    adj = {}
    for src, dst in boundary_edges:
        if src not in adj: adj[src] = []
        adj[src].append(dst)
        
    visited_edges = set()
    loops = []
    
    for start_v in adj:
        for next_v in adj[start_v]:
            if (start_v, next_v) not in visited_edges:
                loop_edges = []
                curr = start_v
                while True:
                    next_choice = None
                    if curr in adj:
                        for dst in adj[curr]:
                            if (curr, dst) not in visited_edges:
                                next_choice = dst
                                break
                    if next_choice is None:
                        break
                    loop_edges.append((LatticePoint(*curr), LatticePoint(*next_choice)))
                    visited_edges.add((curr, next_choice))
                    curr = next_choice
                    if curr == start_v:
                        break
                if loop_edges:
                    loops.append(loop_edges)
    return loops
