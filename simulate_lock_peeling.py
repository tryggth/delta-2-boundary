import csv
import sys
import time
import spectre_boundary_solver
from spectre_boundary_solver import generate_inflated_patch, LatticePoint, extract_boundary_loop, vec_to_dir

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
        forced_count = int(row[5])
        if "Absolute Holographic Lock" in status:
            all_locks[steps] = (status, forced_count, path_id)

print(f"Loaded {len(all_locks)} absolute holographic locks.")

# Generate Gen 2 patch (71 tiles)
print("Generating Gen 2 patch (71 tiles)...")
patch = generate_inflated_patch('Delta', 2, LatticePoint(0,0,0,0), 0, reflected=False)
current_patch = list(patch)

def get_boundary_turns(loop_edges):
    directions = []
    for src, dst in loop_edges:
        directions.append(vec_to_dir(dst.sub(src)))
    n = len(directions)
    boundary_turns = []
    for i in range(n):
        d_curr = directions[i]
        d_next = directions[(i + 1) % n]
        diff = (d_next - d_curr) % 12
        if diff > 6:
            diff -= 12
        boundary_turns.append(diff)
    return boundary_turns

def find_tile_covering_edge(patch_list, src, dst):
    src_tup = src.to_tuple()
    dst_tup = dst.to_tuple()
    for tile in patch_list:
        for t_src, t_dst, _ in tile.edges:
            if (t_src == src_tup and t_dst == dst_tup) or (t_dst == src_tup and t_src == dst_tup):
                return tile
    return None

# We run the cascade
step = 1
start_time = time.time()

print("\n" + "="*80)
print(f"{'Step':<6} | {'Patch Size':<10} | {'Boundary Edges':<15} | {'Lock Used':<20} | {'Lock Length':<12}")
print("="*80)

while len(current_patch) > 0:
    boundary_poly, loop_edges = extract_boundary_loop(current_patch)
    n = len(loop_edges)
    
    # Calculate boundary turns
    turns = get_boundary_turns(loop_edges)
    extended_turns = turns + turns
    
    # Find all matching locks in the boundary
    matching_locks = []
    for length in range(3, 9):
        for i in range(n):
            subpath = tuple(extended_turns[i : i + length])
            if subpath in all_locks:
                matching_locks.append((i, length, subpath, all_locks[subpath]))
                
    if not matching_locks:
        print(f"\nFailed at step {step}: No holographic locks of length <= 8 found in boundary loop!")
        break
        
    # We choose a lock that:
    # 1. Has an anchor tile covering its first edge.
    # 2. Prefer locks where removing the anchor tile preserves boundary contiguousness.
    # 3. Prefer shorter locks to make the proof simpler.
    
    # Sort matching locks by length first
    matching_locks.sort(key=lambda x: x[1])
    
    target_tile = None
    chosen_lock = None
    
    for idx_in_loop, length, subpath, lock_info in matching_locks:
        # First edge of the subpath is at index idx_in_loop
        src, dst = loop_edges[idx_in_loop]
        tile = find_tile_covering_edge(current_patch, src, dst)
        if tile:
            # Check if removing this tile preserves contiguousness
            # (Note: is_boundary_contiguous requires a custom implementation if importing it fails, 
            # but we imported it from spectre_boundary_solver)
            if is_boundary_contiguous(tile, loop_edges):
                target_tile = tile
                chosen_lock = (idx_in_loop, length, subpath, lock_info)
                break
                
    # Fallback to first lock if no contiguous lock preserves boundary loop connectivity
    if not target_tile and matching_locks:
        idx_in_loop, length, subpath, lock_info = matching_locks[0]
        src, dst = loop_edges[idx_in_loop]
        target_tile = find_tile_covering_edge(current_patch, src, dst)
        chosen_lock = (idx_in_loop, length, subpath, lock_info)
        
    if not target_tile:
        print(f"\nFailed at step {step}: Found locks, but could not retrieve corresponding tiles!")
        break
        
    idx_in_loop, length, subpath, lock_info = chosen_lock
    path_id = lock_info[2]
    
    print(f"{step:<6} | {len(current_patch):<10} | {n:<15} | {path_id:<20} | {length:<12}")
    
    current_patch.remove(target_tile)
    step += 1

print("="*80)
if len(current_patch) == 0:
    print(f"Success! Cascade completed using ONLY N8 holographic locks in {time.time() - start_time:.2f} seconds.")
else:
    print(f"Cascade failed. {len(current_patch)} tiles remaining.")
