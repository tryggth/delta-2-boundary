import csv
import sys
import time
import spectre_boundary_solver
from spectre_boundary_solver import generate_inflated_patch, LatticePoint, extract_boundary_loop, PlacedTile, vec_to_dir

def align_lattice_point(pt, start_v, start_d):
    shifted = pt.sub(start_v)
    steps = (12 - start_d) % 12
    curr = shifted
    for _ in range(steps):
        curr = curr.rot30()
    return curr

def is_boundary_contiguous(tile, loop_edges) -> bool:
    tile_edges_set = set()
    for src, dst, _ in tile.edges:
        tile_edges_set.add((src, dst))
        tile_edges_set.add((dst, src))
    indices = []
    for idx, (src, dst) in enumerate(loop_edges):
        if (src.to_tuple(), dst.to_tuple()) in tile_edges_set:
            indices.append(idx)
    if len(indices) <= 1:
        return True
    indices.sort()
    n = len(loop_edges)
    diffs_greater_than_1 = 0
    k = len(indices)
    for i in range(k):
        next_idx = indices[(i + 1) % k]
        diff = (next_idx - indices[i]) % n
        if diff > 1:
            diffs_greater_than_1 += 1
    return diffs_greater_than_1 <= 1

# Load N8 database
all_locks = {}
DEG_TO_STEPS = {
    -90: -3,
    -60: -2,
    0: 0,
    60: 2,
    90: 3
}

print("Loading N8 database...")
with open('/home/tryggth2009/boundary/spectre_optimized_sieve_N8.csv', 'r') as f:
    reader = csv.reader(f)
    next(reader)
    for row in reader:
        length = int(row[0])
        path_id = row[1]
        seq_deg_str = row[2]
        cleaned = seq_deg_str.replace('[', '').replace(']', '').replace('°', '').replace(' ', '')
        if cleaned:
            degs = [int(x) for x in cleaned.split(',')]
            steps = tuple(DEG_TO_STEPS[d] for d in degs)
        else:
            steps = ()
        status = row[4]
        if "Absolute Holographic Lock" in status:
            all_locks[steps] = path_id

print(f"Loaded {len(all_locks)} absolute holographic locks.")

print("1. Generating Gen-2 Delta Patch (71 tiles)...")
patch = generate_inflated_patch('Delta', 2, LatticePoint(0,0,0,0), 0, reflected=False)

# Extract boundary loop
boundary_poly, loop_edges = extract_boundary_loop(patch)

# Find first edge in loop_edges that goes in direction 0
k = None
for idx, edge in enumerate(loop_edges):
    d = vec_to_dir(edge[1].sub(edge[0]))
    if d == 0:
        k = idx
        break

if k is None:
    raise ValueError("Could not find a boundary edge in direction 0")

print(f"CCW loop edge in direction 0 is at index {k}. Aligning patch...")
start_v = loop_edges[k][0]
start_d = 0

aligned_patch = []
for tile in patch:
    new_origin = align_lattice_point(tile.origin, start_v, start_d)
    new_ori = (tile.orientation - start_d) % 12
    aligned_patch.append(PlacedTile(new_origin, new_ori, reflected=False))

# Extract aligned boundary loop
aligned_boundary_poly, aligned_loop_edges = extract_boundary_loop(aligned_patch)

# Rotate aligned loop by k steps so that the direction-0 edge starting at (0,0,0,0) is at index 0
aligned_loop_edges_rot = aligned_loop_edges[k:] + aligned_loop_edges[:k]
assert aligned_loop_edges_rot[0][0].to_tuple() == (0, 0, 0, 0)
assert vec_to_dir(aligned_loop_edges_rot[0][1].sub(aligned_loop_edges_rot[0][0])) == 0

def get_turns(edges):
    dirs = [vec_to_dir(dst.sub(src)) for src, dst in edges]
    n = len(dirs)
    turns = []
    for i in range(n):
        d_curr = dirs[i]
        d_next = dirs[(i + 1) % n]
        diff = (d_next - d_curr) % 12
        if diff > 6: diff -= 12
        turns.append(diff)
    return turns

def diff_to_turn_name(diff):
    if diff == -3: return "Turn.r90"
    elif diff == 2: return "Turn.l60"
    elif diff == 0: return "Turn.straight"
    elif diff == -2: return "Turn.r60"
    elif diff == 3: return "Turn.l90"
    else: raise ValueError(f"Unknown turn step: {diff}")

initial_turns = get_turns(aligned_loop_edges_rot)
lean_turns = [diff_to_turn_name(d) for d in initial_turns]

def find_tile_covering_edge(patch_list, src, dst):
    src_tup = src.to_tuple()
    dst_tup = dst.to_tuple()
    for tile in patch_list:
        for t_src, t_dst, _ in tile.edges:
            if (t_src == src_tup and t_dst == dst_tup) or (t_dst == src_tup and t_src == dst_tup):
                return tile
    return None

print("2. Running connected locked cascade solver on the aligned patch...")
current_patch = list(aligned_patch)
peel_steps = []

step_num = 1
while len(current_patch) > 1:
    b_poly, b_edges = extract_boundary_loop(current_patch)
    n_loop = len(b_edges)
    turns_curr = get_turns(b_edges)
    extended_turns = turns_curr + turns_curr
    
    # Find matching locks
    matching_locks = []
    for length in range(3, 9):
        for i in range(n_loop):
            subpath = tuple(extended_turns[i : i + length])
            if subpath in all_locks:
                matching_locks.append((i, length, subpath))
                
    if not matching_locks:
        raise ValueError(f"No locks found at step {step_num}!")
        
    # Sort by length
    matching_locks.sort(key=lambda x: x[1])
    
    target = None
    chosen_idx = None
    chosen_len = None
    
    for start_idx, length, subpath in matching_locks:
        src, dst = b_edges[start_idx]
        tile = find_tile_covering_edge(current_patch, src, dst)
        if tile and is_boundary_contiguous(tile, b_edges):
            target = tile
            chosen_idx = start_idx
            chosen_len = length
            break
            
    if not target:
        # Fallback
        start_idx, length, subpath = matching_locks[0]
        src, dst = b_edges[start_idx]
        target = find_tile_covering_edge(current_patch, src, dst)
        chosen_idx = start_idx
        chosen_len = length
        
    # Find boundary edges of target
    tile_edges = set((src, dst) for src, dst, _ in target.edges)
    tile_edges.update((dst, src) for src, dst, _ in target.edges)
    
    indices = []
    for idx, (src, dst) in enumerate(b_edges):
        if (src.to_tuple(), dst.to_tuple()) in tile_edges:
            indices.append(idx)
            
    indices.sort()
    gaps = []
    for i in range(len(indices)):
        gaps.append((indices[(i+1)%len(indices)] - indices[i]) % n_loop)
    max_gap_idx = gaps.index(max(gaps))
    start_idx = (indices[max_gap_idx] + 1) % n_loop
    num_edges = len(indices)
    
    b_edges_rot = b_edges[start_idx:] + b_edges[:start_idx]
    turns_rot = get_turns(b_edges_rot)
    
    current_patch.remove(target)
    next_b_poly, next_b_edges = extract_boundary_loop(current_patch)
    turns_next = get_turns(next_b_edges)
    
    repl_len = len(turns_next) - (n_loop - num_edges)
    
    ref_edge = b_edges_rot[0]
    next_idx = None
    for idx, edge in enumerate(next_b_edges):
        if edge[0].to_tuple() == ref_edge[0].to_tuple() and edge[1].to_tuple() == ref_edge[1].to_tuple():
            next_idx = idx
            break
            
    shift = next_idx % len(next_b_edges)
    next_b_edges_rot = next_b_edges[shift:] + next_b_edges[:shift]
    turns_next_rot = get_turns(next_b_edges_rot)
    
    surviving_len = n_loop - num_edges
    replacement = turns_next_rot[surviving_len - 1 :]
    
    # Verify mutation
    reconstructed = turns_rot[0 : surviving_len - 1] + replacement
    assert reconstructed == turns_next_rot, f"Mismatch at step {step_num}"
    
    # Store step info for Lean
    rot_lean = (start_idx - k) % n_loop
    len_lean = num_edges + 1
    replacement_lean = [diff_to_turn_name(d) for d in replacement]
    
    peel_steps.append({
        "tile": target,
        "rot": rot_lean,
        "len": len_lean,
        "replacement": replacement_lean
    })
    
    # Update alignment k for next step
    next_k = None
    for idx, edge in enumerate(next_b_edges):
        if edge[0].to_tuple() == ref_edge[0].to_tuple() and edge[1].to_tuple() == ref_edge[1].to_tuple():
            next_k = idx
            break
    if next_k is None:
        raise ValueError(f"Could not find CCW reference edge at step {step_num}")
    k = next_k
    step_num += 1

last_tile = current_patch[0]
print(f"Cascade complete. Final remaining tile is at {last_tile.origin.to_tuple()}")

# Write to Lean file
lean_lines = []
lean_lines.append("import SpectreNG.Topology")
lean_lines.append("")
lean_lines.append("open LatticePoint")
lean_lines.append("")
lean_lines.append("/-- Structure representing a single peeling step certificate -/")
lean_lines.append("structure PeelStep where")
lean_lines.append("  tile : PlacedTile")
lean_lines.append("  rot : Nat")
lean_lines.append("  len : Nat")
lean_lines.append("  replacement : Path")
lean_lines.append("  deriving DecidableEq, Repr")
lean_lines.append("")
lean_lines.append("/-- Boundary turn path of the Delta-2 Patch -/")
lean_lines.append("def delta2_boundary : Path := [")
for i in range(0, len(lean_turns), 10):
    chunk = lean_turns[i:i+10]
    line = "  " + ", ".join(chunk) + ","
    lean_lines.append(line)
if lean_lines[-1].endswith(","):
    lean_lines[-1] = lean_lines[-1][:-1]
lean_lines.append("]")
lean_lines.append("")
lean_lines.append("/-- Concrete 70-step peeling certificate for the Delta-2 Patch -/")
lean_lines.append("def delta2_certificate : List PeelStep := [")

for step_info in peel_steps:
    tile = step_info["tile"]
    a, b, c, d = tile.origin.to_tuple()
    ori = tile.orientation
    rot = step_info["rot"]
    length = step_info["len"]
    repl = ", ".join(step_info["replacement"])
    lean_lines.append(f"  ⟨⟨⟨{a}, {b}, {c}, {d}⟩, {ori}⟩, {rot}, {length}, [{repl}]⟩,")

if lean_lines[-1].endswith(","):
    lean_lines[-1] = lean_lines[-1][:-1]

lean_lines.append("]")
lean_lines.append("")
lean_lines.append("/-- The final remaining base tile of the Delta-2 Patch -/")
a, b, c, d = last_tile.origin.to_tuple()
lean_lines.append(f"def delta2_last_tile : PlacedTile := ⟨⟨{a}, {b}, {c}, {d}⟩, {last_tile.orientation}⟩")

output_path = "/home/tryggth2009/SpectreNG/SpectreNG/Delta2Certificate.lean"
with open(output_path, "w") as f:
    f.write("\n".join(lean_lines) + "\n")

print(f"Successfully generated Lean 4 certificate: {output_path}")
