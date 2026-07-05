import csv
import sys

# Load spectre_optimized_sieve_N8.csv
# We want to map subpaths (in integer step turns) to their Holographic_Lock_Status and Forced_Tile_Count
all_locks = {} # keys: tuple of turns (e.g. (-3, 2, 3)), values: (status, forced_tile_count, path_id)

TURN_TO_STEPS = {
    'straight': 0,
    'r60': -2,
    'l60': 2,
    'r90': -3,
    'l90': 3
}

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
    header = next(reader)
    for row in reader:
        length = int(row[0])
        path_id = row[1]
        seq_deg_str = row[2]
        # Parse seq_deg_str like "[-90°, 60°, 0°]"
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

print(f"Loaded {len(all_locks)} absolute holographic locks from N8 database.")

# Define delta2_boundary turns
delta2_boundary_str = [
  "straight", "r60", "l90", "r60", "r90", "l60", "straight", "r60", "l90", "r60",
  "l90", "r60", "l90", "r60", "r90", "r60", "l90", "l60", "r90", "l60",
  "straight", "r60", "l90", "r60", "r90", "l60", "l90", "l60", "r90", "l60",
  "straight", "r60", "l90", "l60", "r90", "l60", "straight", "r60", "l90", "r60",
  "r90", "r60", "l90", "l60", "r90", "l60", "straight", "r60", "l90", "r60",
  "r90", "l60", "l90", "l60", "r90", "l60", "straight", "r60", "l90", "l60",
  "r90", "l60", "straight", "r60", "l90", "r60", "r90", "l60", "l90", "l60",
  "r90", "l60", "straight", "r60", "l90", "r60", "r90", "l60", "straight", "r60",
  "l90", "r60", "r90", "r60", "l90", "l60", "r90", "l60", "straight", "r60",
  "l90", "r60", "r90", "l60", "l90", "l60", "r90", "l60", "straight", "r60",
  "l90", "l60", "r90", "l60", "straight", "r60", "l90", "r60", "r90", "r60",
  "l90", "l60", "r90", "l60", "straight", "r60", "l90", "r60", "r90", "l60",
  "l90", "l60", "r90", "l60", "straight", "r60", "l90", "l60", "r90", "l60",
  "straight", "r60", "l90", "r60", "r90", "l60", "l90", "l60", "r90", "l60",
  "straight", "r60", "l90", "r60", "r90", "l60", "straight", "r60", "l90", "r60",
  "r90", "r60", "l90", "l60", "r90", "l60", "straight", "r60", "l90", "r60",
  "r90", "l60", "l90", "l60", "r90", "l60", "straight", "r60", "l90", "l60",
  "r90", "l60", "straight", "r60", "l90", "r60", "r90", "l60", "l90", "l60",
  "r90", "l60"
]
delta2_boundary = [TURN_TO_STEPS[t] for t in delta2_boundary_str]

# Concrete 70-step peeling certificate data
cert_data = [
  (158, 7, [-2, 3, -2, -3, 2, -3, 2, -3, 2]),
  (2, 6, [0, 2, -3, 2, -3, -2, 0, -2, 3, 2]),
  (8, 12, [3, 2, -3, 2]),
  (6, 12, [0, 2, -3, 2]),
  (2, 6, [3, 2, -3, 2, -3, -2, 0, -2, 3, 2]),
  (8, 12, [3, 2, -3, 2]),
  (2, 8, [0, 2, -3, -2, 0, -2, 3, 2]),
  (163, 11, [3, 2, -3, 2, 0]),
  (1, 9, [2, -3, 2, -3, 2, -3, 2]),
  (148, 5, [2, -3, -2, 3, -2, -3, 2, -3, 2, -3, 2]),
  (163, 3, [3, -2, 3, -2, -3, -2, 3, -2, -3, 2, -3, 2, 0]),
  (172, 4, [2, 0, -2, 3, -2, -3, -2, 3, -2, -3, 2, 0]),
  (171, 7, [2, 0, -2, 3, -2, -3, -2, 3, 2]),
  (22, 6, [3, 2, -3, 2, -3, -2, 0, -2, 3, 2]),
  (7, 11, [3, 2, -3, -2, 3]),
  (183, 6, [0, 2, -3, -2, 0, -2, 3, -2, -3, 2]),
  (181, 11, [3, 2, -3, 2, 0]),
  (1, 9, [2, -3, 2, -3, 2, -3, 2]),
  (126, 7, [2, 3, -2, -3, 2, -3, 2, -3, 2]),
  (2, 6, [0, 2, -3, 2, -3, -2, 0, -2, 3, 2])
]

def find_locks_in_loop(boundary):
    # Since boundary is cyclic, we extend it to check subpaths across the boundary wrap-around
    extended = boundary + boundary
    found = []
    n = len(boundary)
    for length in range(3, 9):
        for i in range(n):
            subpath = tuple(extended[i:i+length])
            if subpath in all_locks:
                found.append((i, length, subpath, all_locks[subpath]))
    return found

# 1. Analyze initial boundary
print("\n--- Initial Boundary Analysis ---")
print(f"Boundary length: {len(delta2_boundary)}")
locks_initial = find_locks_in_loop(delta2_boundary)
print(f"Found {len(locks_initial)} holographic locks in the initial boundary cycle.")
# Sort locks by length
locks_initial.sort(key=lambda x: x[1])
for i, length, subpath, info in locks_initial[:10]:
    print(f"  At index {i}: length={length}, subpath={subpath}, path_id={info[2]}, forced_tiles={info[1]}")

# 2. Analyze the peeling steps of the certificate
print("\n--- Peeling Step Analysis ---")
curr_boundary = list(delta2_boundary)
for idx, (rot, length, replacement) in enumerate(cert_data):
    # Rotate boundary
    p_rot = curr_boundary[rot:] + curr_boundary[:rot]
    subpath = tuple(p_rot[:length])
    
    # Check if this subpath (or a subsegment of it) is a lock in our database
    is_lock = subpath in all_locks
    lock_desc = "LOCK!" if is_lock else "NOT A DIRECT LOCK"
    
    # We can also check if the subpath contains a lock as a subsegment
    contained_locks = []
    for l in range(3, min(len(subpath) + 1, 9)):
        for start in range(len(subpath) - l + 1):
            subseg = subpath[start:start+l]
            if subseg in all_locks:
                contained_locks.append((start, l, subseg))
                
    print(f"Step {idx+1}: peel_len={length}, subpath={subpath}")
    if is_lock:
        print(f"  -> Direct lock! ID: {all_locks[subpath][2]}, Forced: {all_locks[subpath][1]}")
    elif contained_locks:
        print(f"  -> Contains {len(contained_locks)} lock subsegments:")
        for start, l, subseg in contained_locks:
            print(f"     * at offset {start}: length={l}, subpath={subseg}, ID={all_locks[subseg][2]}, Forced={all_locks[subseg][1]}")
    else:
        print("  -> NO LOCAL LOCK IN SUBPATH")
        
    # Apply mutation
    curr_boundary = replacement + p_rot[length:]
