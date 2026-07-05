"""
=============================================================================
             SPECTRENG: STATEFUL FRONTIER OPTIMIZATION TEST (WITH CSV)
=============================================================================
"""

import time
import math
import csv

# =====================================================================
# PHASE 1: EXACT DIOPHANTINE ARITHMETIC ENGINES 
# =====================================================================

class Z3:
    def __init__(self, u: int, v: int):
        self.u = u
        self.v = v

    def __add__(self, other): 
        return Z3(self.u + other.u, self.v + other.v)
        
    def __sub__(self, other): 
        return Z3(self.u - other.u, self.v - other.v)
        
    def __mul__(self, other):
        return Z3(
            self.u * other.u + 3 * self.v * other.v,
            self.u * other.v + self.v * other.u
        )

    def is_non_neg(self) -> bool:
        if self.u >= 0 and self.v >= 0: return True
        if self.u <= 0 and self.v <= 0: return False
        if self.u < 0 and self.v > 0: return 3 * self.v * self.v >= self.u * self.u
        return self.u * self.u >= 3 * self.v * self.v

    def sign(self) -> int:
        if self.u == 0 and self.v == 0: return 0
        return 1 if self.is_non_neg() else -1

    def scale2(self):
        return Z3(self.u * 2, self.v * 2)


class Point2D:
    def __init__(self, x: Z3, y: Z3):
        self.x = x
        self.y = y

    def scale2(self):
        return Point2D(self.x.scale2(), self.y.scale2())


class LatticePoint:
    def __init__(self, a: int, b: int, c: int, d: int):
        self.a = a
        self.b = b
        self.c = c
        self.d = d

    def add(self, other):
        return LatticePoint(self.a + other.a, self.b + other.b, self.c + other.c, self.d + other.d)

    def sub(self, other):
        return LatticePoint(self.a - other.a, self.b - other.b, self.c - other.c, self.d - other.d)

    def rot30(self):
        return LatticePoint(-self.d, self.a, self.b + self.d, self.c)

    def to_tuple(self):
        return (self.a, self.b, self.c, self.d)

    def to_point2d(self) -> Point2D:
        return Point2D(Z3(2 * self.a + self.c, self.b), Z3(self.b + 2 * self.d, self.c))


# =====================================================================
# PHASE 2: GEOMETRY & VECTOR INTERSECTION PRUNING
# =====================================================================

SPECTRE_TURNS = [90, -60, 90, 60, 0, 60, -90, 60, 90, 60, -90, 60, 90, -60]
TURN_STEPS = {-90: -3, -60: -2, 0: 0, 60: 2, 90: 3}
STEP_TO_DEG = {-3: -90, -2: -60, 0: 0, 2: 60, 3: 90}
ALLOWED_STEPS = {-3, -2, 0, 2, 3}
SPECTRE_INT_ANGLES = [180 - SPECTRE_TURNS[13]] + [180 - SPECTRE_TURNS[k] for k in range(13)]

def dir_to_vec(d: int) -> LatticePoint:
    pt = LatticePoint(1, 0, 0, 0)
    for _ in range(d % 12): pt = pt.rot30()
    return pt

def cross_product(p1: Point2D, p2: Point2D, p3: Point2D) -> Z3:
    return ((p2.x - p1.x) * (p3.y - p1.y)) - ((p2.y - p1.y) * (p3.x - p1.x))

def segments_intersect(a: Point2D, b: Point2D, c: Point2D, d: Point2D) -> bool:
    s1, s2 = cross_product(a, b, c).sign(), cross_product(a, b, d).sign()
    s3, s4 = cross_product(c, d, a).sign(), cross_product(c, d, b).sign()
    return (s1 * s2 < 0) and (s3 * s4 < 0)

def point_in_polygon(pt: Point2D, poly: list[Point2D]) -> bool:
    count = 0
    for i in range(len(poly) - 1):
        a, b = poly[i], poly[i+1]
        
        # EXACT ARITHMETIC BOUNDARY CHECK
        cp = cross_product(a, b, pt).sign()
        if cp == 0:
            dx_sign = (pt.x - a.x).sign() * (pt.x - b.x).sign()
            dy_sign = (pt.y - a.y).sign() * (pt.y - b.y).sign()
            if dx_sign <= 0 and dy_sign <= 0:
                return False  
                
        cond1, cond2 = (pt.y - a.y).sign(), (pt.y - b.y).sign()
        if (cond1 >= 0 and cond2 < 0) or (cond2 >= 0 and cond1 < 0):
            if (a.y - b.y).sign() < 0:
                if cp > 0: count += 1
            elif cp < 0: count += 1
            
    return count % 2 == 1


class PlacedTile:
    def __init__(self, origin: LatticePoint, orientation: int):
        self.origin = origin
        self.orientation = orientation
        self.vertices = []
        self.edges = []
        self._build_geometry()

    def _build_geometry(self):
        curr_dir = self.orientation
        curr_pos = self.origin
        self.vertices.append(curr_pos)
        dirs = []
        for t in SPECTRE_TURNS:
            dirs.append(curr_dir)
            curr_dir = (curr_dir + TURN_STEPS[t]) % 12
        for d in dirs:
            next_pos = curr_pos.add(dir_to_vec(d))
            self.edges.append((curr_pos.to_tuple(), next_pos.to_tuple(), d))
            curr_pos = next_pos
            self.vertices.append(curr_pos)

    @staticmethod
    def align_to_path_edge(p_v1: tuple, p_v2: tuple, p_dir: int, tile_edge_idx: int):
        ref_tile = PlacedTile(LatticePoint(0,0,0,0), 0)
        ref_dir = ref_tile.edges[tile_edge_idx][2]
        orientation = (p_dir - ref_dir) % 12
        oriented_ref = PlacedTile(LatticePoint(0,0,0,0), orientation)
        ref_v1 = LatticePoint(*oriented_ref.edges[tile_edge_idx][0])
        target_v1 = LatticePoint(*p_v1)
        origin = target_v1.sub(ref_v1)
        return PlacedTile(origin, orientation)


def polygons_overlap(t1: PlacedTile, t2: PlacedTile) -> bool:
    if t1.origin.to_tuple() == t2.origin.to_tuple() and t1.orientation == t2.orientation:
        return True

    pts1 = [v.to_point2d() for v in t1.vertices]
    pts2 = [v.to_point2d() for v in t2.vertices]

    for i in range(14):
        for j in range(14):
            if segments_intersect(pts1[i], pts1[i+1], pts2[j], pts2[j+1]): 
                return True

    for v in pts1[:-1]:
        if point_in_polygon(v, pts2): return True
    for v in pts2[:-1]:
        if point_in_polygon(v, pts1): return True

    pts1_scaled = [p.scale2() for p in pts1]
    pts2_scaled = [p.scale2() for p in pts2]

    for i in range(14):
        mid = Point2D(pts1[i].x + pts1[i+1].x, pts1[i].y + pts1[i+1].y)
        if point_in_polygon(mid, pts2_scaled): return True

    for j in range(14):
        mid = Point2D(pts2[j].x + pts2[j+1].x, pts2[j].y + pts2[j+1].y)
        if point_in_polygon(mid, pts1_scaled): return True

    return False

def trace_absolute_path_vertices(path_steps: tuple) -> list:
    vertices = [LatticePoint(0,0,0,0)]
    curr_pos = LatticePoint(0,0,0,0)
    curr_dir = 0
    edges_pool = [0] + list(path_steps)
    for step in edges_pool:
        curr_dir = (curr_dir + step) % 12
        curr_pos = curr_pos.add(dir_to_vec(curr_dir))
        vertices.append(curr_pos)
    return [v.to_tuple() for v in vertices]

def extract_path_fingerprints(tiles: list[PlacedTile]) -> set:
    return set((t.origin.to_tuple(), t.orientation) for t in tiles)


# =====================================================================
# PHASE 3: STATEFUL FRONTIER ALGORITHM 
# =====================================================================

def verify_frontier_wedge(tiles: list[PlacedTile], path_steps: tuple, path_verts: list) -> tuple[bool, str]:
    num_turns = len(path_steps)
    for turn_idx in range(num_turns):
        vertex_coords = path_verts[turn_idx + 1]
        turn_deg = STEP_TO_DEG.get(path_steps[turn_idx], path_steps[turn_idx] * 30)
        expected_interior_angle = 180 - turn_deg
        
        cluster_angle_sum = 0
        for single_tile in tiles:
            tile_verts_tuples = [v.to_tuple() for v in single_tile.vertices[:-1]]
            if vertex_coords in tile_verts_tuples:
                v_index = tile_verts_tuples.index(vertex_coords)
                cluster_angle_sum += SPECTRE_INT_ANGLES[v_index]
        
        interior_gap = expected_interior_angle - cluster_angle_sum
        exterior_gap = 360 - cluster_angle_sum
        
        if interior_gap < 0:
            return False, f"Rejected: Boundary Spill (Node {turn_idx+1})"
        if 0 < interior_gap < 90:
            return False, f"Rejected: Unfillable <90° Interior Wedge (Node {turn_idx+1})"
        if 0 < exterior_gap < 90:
            return False, f"Rejected: Unfillable <90° Exterior Wedge (Node {turn_idx+1})"

    return True, "Valid"

def extend_neighborhoods(cached_layouts: list, path_steps: tuple) -> tuple[list, str]:
    num_edges = len(path_steps) + 1
    path_verts = trace_absolute_path_vertices(path_steps)
    path_pts2d = [LatticePoint(*v).to_point2d() for v in path_verts]
    
    last_edge_idx = num_edges - 1
    for i in range(last_edge_idx - 1):
        if segments_intersect(path_pts2d[i], path_pts2d[i+1], path_pts2d[last_edge_idx], path_pts2d[last_edge_idx+1]):
            return [], "Rejected: Path Self-Intersection"
            
    curr_dir = 0
    edges_pool = [0] + list(path_steps)
    for idx in range(num_edges):
        curr_dir = (curr_dir + edges_pool[idx]) % 12
    p_dir = curr_dir
    
    new_v1, new_v2 = path_verts[-2], path_verts[-1]
    
    valid_new_layouts = []
    seen_fingerprints = set()
    global_failure_reason = "Rejected: Tile Spatial Collision"

    for layout in cached_layouts:
        edge_covered = False
        for tile in layout:
            if any(e[0] == new_v1 and e[1] == new_v2 for e in tile.edges):
                edge_covered = True
                break
        
        candidate_extensions = []
        if edge_covered:
            candidate_extensions.append(layout)
        else:
            for tile_edge_idx in range(14):
                candidate_tile = PlacedTile.align_to_path_edge(new_v1, new_v2, p_dir, tile_edge_idx)
                has_collision = False
                for existing_tile in layout:
                    if polygons_overlap(candidate_tile, existing_tile):
                        has_collision = True
                        break
                if not has_collision:
                    candidate_extensions.append(layout + [candidate_tile])
                    
        for ext_layout in candidate_extensions:
            is_valid, wedge_status = verify_frontier_wedge(ext_layout, path_steps, path_verts)
            if is_valid:
                fingerprint = tuple(sorted([(t.origin.to_tuple(), t.orientation) for t in ext_layout]))
                if fingerprint not in seen_fingerprints:
                    seen_fingerprints.add(fingerprint)
                    valid_new_layouts.append(ext_layout)
            else:
                global_failure_reason = wedge_status
                
    if valid_new_layouts:
        return valid_new_layouts, "Valid Boundaries Found"
        
    return [], global_failure_reason


def generate_base_neighborhoods(path_steps: tuple) -> list:
    num_edges = len(path_steps) + 1
    path_verts = trace_absolute_path_vertices(path_steps)
    
    path_edges = []
    curr_dir = 0
    edges_pool = [0] + list(path_steps)
    for idx in range(num_edges):
        curr_dir = (curr_dir + edges_pool[idx]) % 12
        path_edges.append((path_verts[idx], path_verts[idx+1], curr_dir))
        
    valid_layouts = []
    seen_fingerprints = set()
    
    def bind_edge(edge_idx: int, current_tiles: list):
        if edge_idx == num_edges:
            is_valid, _ = verify_frontier_wedge(current_tiles, path_steps, path_verts)
            if is_valid:
                fingerprint = tuple(sorted([(t.origin.to_tuple(), t.orientation) for t in current_tiles]))
                if fingerprint not in seen_fingerprints:
                    seen_fingerprints.add(fingerprint)
                    valid_layouts.append(current_tiles)
            return

        p_v1, p_v2, p_dir = path_edges[edge_idx]
        
        edge_covered = False
        for tile in current_tiles:
            if any(e[0] == p_v1 and e[1] == p_v2 for e in tile.edges):
                edge_covered = True
                break
                
        if edge_covered:
            bind_edge(edge_idx + 1, current_tiles)
            return

        for tile_edge_idx in range(14):
            candidate_tile = PlacedTile.align_to_path_edge(p_v1, p_v2, p_dir, tile_edge_idx)
            has_collision = False
            for existing_tile in current_tiles:
                if polygons_overlap(candidate_tile, existing_tile):
                    has_collision = True
                    break
            if not has_collision:
                bind_edge(edge_idx + 1, current_tiles + [candidate_tile])

    bind_edge(0, [])
    return valid_layouts


# =====================================================================
# PHASE 4: STATEFUL SIEVE EXECUTION (DP)
# =====================================================================

def execute_stateful_sieve(max_n=4):
    print(f"\n[INIT] Booting Stateful Frontier Sieve (Target: Length {max_n})...")
    
    filename = f"spectre_optimized_sieve_N{max_n}.csv"
    file = open(filename, mode='w', newline='')
    writer = csv.writer(file)
    writer.writerow(["Length", "Path_ID", "Sequence_Degrees", "Is_Valid_Boundary", "Holographic_Lock_Status", "Forced_Tile_Count", "Ambiguous_Layout_Dumps"])
    
    turn_steps_pool = [-3, -2, 0, 2, 3]
    forbidden_substrings = set()
    
    # [1] Initialize Cache with N=1 logic
    state_cache = {} 
    initial_paths = [(s,) for s in turn_steps_pool]
    valid_paths = []  
    
    print(f"[CACHE] Seeding state cache with N=1 base layouts...")
    for path in initial_paths:
        layouts = generate_base_neighborhoods(path)
        if layouts:
            state_cache[path] = layouts
            valid_paths.append(path)
        else:
            forbidden_substrings.add(path)
            
    global_start = time.time()
    
    # [2] Execute Incremental Sieve (N=2 up to target)
    for current_n in range(2, max_n + 1):
        level_start = time.time()
        
        next_valid_paths = []
        stats = {"generated": 0, "pruned": 0, "evaluated": 0, "invalid": 0, "ambiguous": 0, "locked": 0}
        
        for prefix in valid_paths:
            for turn in turn_steps_pool:
                candidate_path = prefix + (turn,)
                stats["generated"] += 1
                
                deg_list = [STEP_TO_DEG[s] for s in candidate_path]
                human_readable_sequence = ", ".join(f"{d}°" for d in deg_list)
                path_label = f"PATH_SEQ_{current_n}_{stats['generated']:05d}"
                
                # Check for forbidden substrings 
                is_pruned = False
                for i in range(1, len(candidate_path)):
                    if candidate_path[i:] in forbidden_substrings:
                        is_pruned = True
                        break
                        
                if is_pruned:
                    stats["pruned"] += 1
                    writer.writerow([current_n, path_label, f"[{human_readable_sequence}]", "FALSE", "Rejected: Hereditary Prune (Forbidden Substring)", 0, ""])
                    continue
                    
                stats["evaluated"] += 1
                
                # FETCH STATE FROM PREVIOUS N AND EXTEND
                cached_layouts = state_cache[prefix]
                new_layouts, status_msg = extend_neighborhoods(cached_layouts, candidate_path)
                
                if not new_layouts:
                    forbidden_substrings.add(candidate_path)
                    stats["invalid"] += 1
                    writer.writerow([current_n, path_label, f"[{human_readable_sequence}]", "FALSE", status_msg, 0, ""])
                    continue
                    
                # Cache the new physical state
                state_cache[candidate_path] = new_layouts
                next_valid_paths.append(candidate_path)
                
                # Determine Lock vs Ambiguity
                all_local_fingerprints = [extract_path_fingerprints(tiles) for tiles in new_layouts]
                frozen_tiles = all_local_fingerprints[0]
                for coordinate_set in all_local_fingerprints[1:]:
                    frozen_tiles = frozen_tiles.intersection(coordinate_set)
                    
                forced_count = len(frozen_tiles)
                ambiguous_dump = ""
                
                if forced_count >= 1:
                    stats["locked"] += 1
                    lock_status = f"Absolute Holographic Lock: Form forces {forced_count} tile(s) to be completely stationary"
                else:
                    stats["ambiguous"] += 1
                    lock_status = f"True Ambiguity: No tiles are shared across all {len(new_layouts)} layouts"
                    
                    dump_parts = []
                    for idx, config_set in enumerate(all_local_fingerprints):
                        sorted_tiles = sorted(list(config_set))
                        dump_parts.append(f"Layout {idx+1}: {sorted_tiles}")
                    ambiguous_dump = " | ".join(dump_parts)
                    
                writer.writerow([current_n, path_label, f"[{human_readable_sequence}]", "TRUE", lock_status, forced_count, ambiguous_dump])
        
        # [3] Validate Output
        print(f"\n================ APERIODIC HOLOGRAPHY REPORT (N={current_n}) ================")
        print(f" Boundary Length Evaluated        : {current_n} Turns")
        print(f" Total Path Sequences Evaluated   : {stats['evaluated']:,} (Out of {stats['generated']:,} permutations)")
        print(f" Geometrically Invalid Boundaries : {stats['invalid']:,}")
        print(f" Absolute Holographic Locks       : {stats['locked']:,}")
        print(f" True Ambiguity Deviations        : {stats['ambiguous']:,}")
        print(f"--------------------------------------------------------------")
        print(f" Level Processing Time            : {time.time() - level_start:.2f} seconds")
        print(f" Guillotined by Sieve             : {stats['pruned']:,} (Bypassed Physics Engine)")
        print(f" Valid Paths Surviving to N+1     : {len(next_valid_paths):,}")
        print(f"==============================================================\n")
        
        valid_paths = next_valid_paths

    file.close()
    total_time = time.time() - global_start
    print(f"[COMPLETE] Stateful DP Sieve reached N={max_n}")
    print(f" Total Execution Time : {total_time:.2f} seconds")
    print(f" Spreadsheet successfully saved to: '{filename}'")

if __name__ == "__main__":
    execute_stateful_sieve(max_n=4)