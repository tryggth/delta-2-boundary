import csv
import ast

# Load 5-space.csv
locks_5 = {}
with open('/home/tryggth2009/boundary/5-space.csv') as f:
    r = csv.reader(f)
    next(r)
    for row in r:
        if row[0] == '5':
            path_id = row[1]
            seq_deg = eval(row[2].replace('°', ''))
            step_path = tuple(deg // 30 for deg in seq_deg)
            status = row[4]
            locks_5[step_path] = status

# Delta-2 boundary turns
SPECTRE_TURNS = [90, -60, 90, 60, 0, 60, -90, 60, 90, 60, -90, 60, 90, -60]
TURN_STEPS = {-90: -3, -60: -2, 0: 0, 60: 2, 90: 3}
TURN_TO_STEPS = {
    'straight': 0,
    'r60': -2,
    'l60': 2,
    'r90': -3,
    'l90': 3
}

def turn_str_to_step(turn_str):
    name = turn_str.split('.')[-1].strip()
    return TURN_TO_STEPS[name]

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

# Peeling steps certificate (extracted from Delta2Certificate.lean)
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

# We simulate the first few steps of the peeling cascade to see what window of turns is being removed in each step.
curr_boundary = list(delta2_boundary)
for idx, (rot, length, replacement) in enumerate(cert_data):
    p_rot = curr_boundary[rot:] + curr_boundary[:rot]
    subpath = tuple(p_rot[:length])
    
    if length == 5:
        status = locks_5.get(subpath, "Not in 5-space")
        print(f"Step {idx+1}: length={length}, subpath={subpath}, lock_status={status}")
    else:
        print(f"Step {idx+1}: length={length}, subpath={subpath}")
        
    curr_boundary = replacement + p_rot[length:]
