import csv
import sys
import time
import os
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

def serialize_lean_state(edges_list):
    """Extracts ordered vertices from an active boundary loop and formats them into Lean code."""
    verts = [edge[0] for edge in edges_list]
    pt_strs = [f"⟨{v.to_tuple()[0]}, {v.to_tuple()[1]}, {v.to_tuple()[2]}, {v.to_tuple()[3]}⟩" for v in verts]
    return f"[{', '.join(pt_strs)}]"

def parse_lock_id_to_nat(path_id_str):
    """Extracts the unique trailing numerical index from the database path ID string for Lean's Nat type."""
    try:
        return int("".join(filter(str.isdigit, path_id_str)))
    except ValueError:
        return 99999 # Safe fallback token

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

# Extract aligned boundary loop and rotate it to pin origin at index 0
aligned_boundary_poly, aligned_loop_edges = extract_boundary_loop(aligned_patch)
aligned_loop_edges_rot = aligned_loop_edges[k:] + aligned_loop_edges[:k]
assert aligned_loop_edges_rot[0][0].to_tuple() == (0, 0, 0, 0)

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

print("2. Running connected locked cascade solver on the aligned patch...")
current_patch = list(aligned_patch)
peel_steps = []

step_num = 1
while len(current_patch) > 1:
    b_poly, b_edges = extract_boundary_loop(current_patch)
    n_loop = len(b_edges)
    turns_curr = get_turns(b_edges)
    extended_turns = turns_curr + turns_curr
    
    matching_locks = []
    for length in range(3, 9):
        for i in range(n_loop):
            subpath = tuple(extended_turns[i : i + length])
            if subpath in all_locks:
                matching_locks.append((i, length, subpath))
                
    if not matching_locks:
        raise ValueError(f"No locks found at step {step_num}!")
        
    matching_locks.sort(key=lambda x: x[1])
    
    target = None
    chosen_idx = None
    chosen_len = None
    
    for start_idx, length, subpath in matching_locks:
        src, dst = b_edges[start_idx]
        def find_tile_covering_edge(patch_list, s, d):
            s_tup, d_tup = s.to_tuple(), d.to_tuple()
            for t in patch_list:
                for t_src, t_dst, _ in t.edges:
                    if (t_src == s_tup and t_dst == d_tup) or (t_dst == s_tup and t_src == d_tup):
                        return t
            return None
        tile = find_tile_covering_edge(current_patch, src, dst)
        if tile and is_boundary_contiguous(tile, b_edges):
            target = tile
            chosen_idx = start_idx
            chosen_len = length
            break
            
    if not target:
        start_idx, length, subpath = matching_locks[0]
        src, dst = b_edges[start_idx]
        target = find_tile_covering_edge(current_patch, src, dst)
        chosen_idx = start_idx
        chosen_len = length
        
    path_id_str = all_locks[subpath]
    nat_lock_id = parse_lock_id_to_nat(path_id_str)
    
    # Track tile data before removal
    a, b, c, d_coord = target.origin.to_tuple()
    ori = target.orientation
    
    current_patch.remove(target)
    next_b_poly, next_b_edges = extract_boundary_loop(current_patch)
    
    # Log step payload with geometric coordinate tracking loops
    peel_steps.append({
        "lock_id": nat_lock_id,
        "a": a, "b": b, "c": c, "d": d_coord,
        "ori": ori,
        "next_state_serialized": serialize_lean_state(next_b_edges)
    })
    
    step_num += 1

last_tile = current_patch[0]
print(f"Cascade complete. Final remaining tile is at {last_tile.origin.to_tuple()}")

# Generate the CertificateData.lean file
lean_lines = [
    "import SpectreDeltaBoundary.Bedrock",
    "import SpectreDeltaBoundary.Paths",
    "import SpectreDeltaBoundary.Monotile",
    "import SpectreDeltaBoundary.Certificate",
    "",
    "/-!",
    "# Automated Peeling Certificate Data Payload",
    "Generated directly from the local Python discrete cascade simulation engine.",
    "-/",
    "",
    f"def initialMetatileBoundary : PeelingState := [{serialize_lean_state(aligned_loop_edges_rot)}]",
    "",
    "def pythonPeelingCertificate : PeelingCertificate := ⟨[",
]

step_blocks = []
for idx, s in enumerate(peel_steps, 1):
    step_str = (
        f"  -- Step {idx}\n"
        f"  ⟨{s['lock_id']}, ⟨⟨{s['a']}, {s['b']}, {s['c']}, {s['d']}⟩, {s['ori']}⟩, [{s['next_state_serialized']}]⟩"
    )
    step_blocks.append(step_str)

lean_lines.append(",\n\n".join(step_blocks))
lean_lines.append("]⟩\n")

output_dir = "/home/tryggth2009/spectre-delta-boundary/SpectreDeltaBoundary"
os.makedirs(output_dir, exist_ok=True)
output_path = os.path.join(output_dir, "CertificateData.lean")

with open(output_path, "w") as f:
    f.write("\n".join(lean_lines))

print(f"Successfully generated clean-slate coordinate file: {output_path}")