import csv
import sys
import os
import json
from datetime import datetime
from spectre_solver.geometry import LatticePoint, PlacedTile, vec_to_dir
from spectre_solver.tiling import extract_boundary_loop, extract_boundary_loops_multi

DEG_TO_STEPS = {-90: -3, -60: -2, 0: 0, 60: 2, 90: 3}
STEPS_TO_DEG = {-3: -90, -2: -60, 0: 0, 2: 60, 3: 90}

# Known anchor lock types with human-readable labels
LOCK_LABELS = {
    300033: "L3-033 [0°,60°,0°]",
    300049: "L3-049 [60°,90°,60°]",
    400074: "L4-074 [0°,-60°,90°,60°]",
    400110: "L4-110 [60°,90°,-60°,90°]",
    400129: "L4-129 [90°,-60°,90°,60°]",
    600094: "L6-094 [-90°,60°,-90°,60°,90°,60°]",
    700175: "L7-175 [-90°,60°,-90°,60°,90°,-60°,90°]",
}

def analyze_boundary(b_edges, all_locks):
    """Compute boundary analytics: length, turn histogram, lock counts, cycle count."""
    n_edges = len(b_edges)
    # Compute turns
    turns = get_turns(b_edges)
    # Convert step-units to degrees
    turn_degs = [STEPS_TO_DEG.get(t, t * 30) for t in turns]
    # Turn histogram
    turn_hist = {-90: 0, -60: 0, 0: 0, 60: 0, 90: 0}
    for d in turn_degs:
        if d in turn_hist:
            turn_hist[d] += 1
        else:
            turn_hist[d] = turn_hist.get(d, 0) + 1

    # Lock counts: scan for each known lock on this boundary
    extended_turns = turns + turns
    lock_counts = {}
    for length in range(3, 9):
        for i in range(n_edges):
            subpath = tuple(extended_turns[i : i + length])
            if subpath in all_locks:
                lock_id_str = all_locks[subpath]
                nat_id = parse_lock_id_to_nat(lock_id_str)
                lock_counts[nat_id] = lock_counts.get(nat_id, 0) + 1

    return {
        "length": n_edges,
        "turn_histogram": turn_hist,
        "lock_counts": lock_counts,
    }

def count_boundary_cycles(patch):
    """Count the number of distinct boundary loops in a patch."""
    loops = extract_boundary_loops_multi(patch)
    return len(loops)

def generate_boundary_report(report_data, supertile_type, generation, report_path=None):
    """Write or print a CSV boundary report with one row per boundary step."""
    import io

    # Collect all distinct lock IDs that appear in any boundary's lock_counts
    all_lock_ids = set()
    for entry in report_data:
        all_lock_ids.update(entry["boundary_info"]["lock_counts"].keys())
    all_lock_ids = sorted(all_lock_ids)

    # Build header
    header = [
        "step",
        "tiles_remaining",
        "boundary_length",
        "boundary_cycles",
        "turns_-90",
        "turns_-60",
        "turns_0",
        "turns_+60",
        "turns_+90",
        "locks_total",
        "locks_distinct",
    ]
    # Add a column for each lock type found on any boundary
    for lid in all_lock_ids:
        label = LOCK_LABELS.get(lid, f"L?-{lid}")
        header.append(f"present_{label}")

    header.extend([
        "lock_used_id",
        "lock_used_label",
        "peeled_origin",
        "peeled_ori",
    ])

    # Build rows
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(header)

    for entry in report_data:
        step = entry["step"]
        tiles_remaining = entry["tiles_remaining"]
        info = entry["boundary_info"]
        cycles = entry["cycles"]
        lock_used = entry.get("lock_used", None)
        tile_peeled = entry.get("tile_peeled", None)

        th = info["turn_histogram"]
        lc = info["lock_counts"]

        row = [
            step,
            tiles_remaining,
            info["length"],
            cycles,
            th.get(-90, 0),
            th.get(-60, 0),
            th.get(0, 0),
            th.get(60, 0),
            th.get(90, 0),
            sum(lc.values()) if lc else 0,
            len(lc),
        ]

        # Per-lock-type columns
        for lid in all_lock_ids:
            row.append(lc.get(lid, 0))

        # Lock used and tile peeled
        if lock_used is not None:
            row.append(lock_used)
            row.append(LOCK_LABELS.get(lock_used, f"L?-{lock_used}"))
        else:
            row.extend(["", ""])

        if tile_peeled is not None:
            row.append(f"({tile_peeled['origin'][0]},{tile_peeled['origin'][1]},{tile_peeled['origin'][2]},{tile_peeled['origin'][3]})")
            row.append(tile_peeled["ori"])
        else:
            row.extend(["", ""])

        writer.writerow(row)

    csv_text = output.getvalue()

    if report_path:
        os.makedirs(os.path.dirname(report_path) if os.path.dirname(report_path) else ".", exist_ok=True)
        with open(report_path, "w", newline="") as f:
            f.write(csv_text)
        print(f"Boundary report written to {report_path}")
    else:
        print(csv_text)

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
    verts = [edge[0] for edge in edges_list]
    pt_strs = [f"⟨{v.to_tuple()[0]}, {v.to_tuple()[1]}, {v.to_tuple()[2]}, {v.to_tuple()[3]}⟩" for v in verts]
    return f"[[{', '.join(pt_strs)}]]"

def parse_lock_id_to_nat(path_id_str):
    try:
        return int("".join(filter(str.isdigit, path_id_str)))
    except ValueError:
        return 99999

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

def load_locks_database(csv_path: str) -> dict:
    locks = {}
    if not os.path.exists(csv_path):
        print(f"Warning: Locks database CSV not found at {csv_path}")
        return locks
    with open(csv_path, 'r') as f:
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
                locks[steps] = path_id
    return locks

from spectre_solver.locks_data import LOCKS

def run_peeling_cascade(patch: list[PlacedTile], locks_csv_path: str, supertile_type: str, generation: int, lean_output_path: str, report_path: str = None):
    if locks_csv_path:
        print(f"Loading locks database from {locks_csv_path}...")
        all_locks = load_locks_database(locks_csv_path)
        if not all_locks:
            print("Falling back to built-in locks database.")
            all_locks = LOCKS
    else:
        print("Using built-in locks database.")
        all_locks = LOCKS
    print(f"Loaded {len(all_locks)} absolute holographic locks.")

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
        raise ValueError("Could not find a boundary edge in direction 0 for alignment")

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

    print("Running connected locked cascade peeling solver with roundness and topological heuristics...")
    current_patch = list(aligned_patch)
    peel_steps = []
    report_data = []

    step_num = 0
    while len(current_patch) > 1:
        b_poly, b_edges = extract_boundary_loop(current_patch)
        n_loop = len(b_edges)
        turns_curr = get_turns(b_edges)
        extended_turns = turns_curr + turns_curr

        # Collect boundary analytics for the report
        boundary_info = analyze_boundary(b_edges, all_locks)
        cycles = count_boundary_cycles(current_patch)
        report_entry = {
            "step": step_num,
            "tiles_remaining": len(current_patch),
            "boundary_info": boundary_info,
            "cycles": cycles,
            "lock_used": None,
            "tile_peeled": None,
        }
        
        # 1. Gather all candidate locks
        candidates = []
        for length in range(3, 9):
            for i in range(n_loop):
                subpath = tuple(extended_turns[i : i + length])
                if subpath in all_locks:
                    candidates.append((i, length, subpath))
                    
        if not candidates:
            raise ValueError(f"No locks found at step {step_num}!")
            
        # Helper to find tile covering edge
        def find_tile_covering_edge(patch_list, s, d):
            s_tup, d_tup = s.to_tuple(), d.to_tuple()
            for t in patch_list:
                for t_src, t_dst, _ in t.edges:
                    if (t_src == s_tup and t_dst == d_tup) or (t_dst == s_tup and t_src == d_tup):
                        return t
            return None

        # 2. Score each candidate to pick the mathematically best one
        scored_candidates = []
        for start_idx, length, subpath in candidates:
            src, dst = b_edges[start_idx]
            tile = find_tile_covering_edge(current_patch, src, dst)
            if tile and is_boundary_contiguous(tile, b_edges):
                # Analyze topological split
                current_patch_temp = [t for t in current_patch if t != tile]
                remaining_loops = extract_boundary_loops_multi(current_patch_temp)
                is_split = len(remaining_loops) > 1
                
                # Analyze roundness (shared boundary edge count)
                tile_edges_set = set()
                for t_src, t_dst, _ in tile.edges:
                    tile_edges_set.add((t_src, t_dst))
                    tile_edges_set.add((t_dst, t_src))
                shared_boundary_count = 0
                for edge in b_edges:
                    if (edge[0].to_tuple(), edge[1].to_tuple()) in tile_edges_set:
                        shared_boundary_count += 1
                
                # Priority 1: No split (0 < 1)
                # Priority 2: Higher shared count (maximize -shared_boundary_count)
                # Priority 3: Shorter length
                score = (1 if is_split else 0, -shared_boundary_count, length)
                scored_candidates.append((start_idx, length, subpath, tile, score, len(remaining_loops)))

        if not scored_candidates:
            # Fallback to absolute first lock in list if no contiguous matches exist
            start_idx, length, subpath = candidates[0]
            src, dst = b_edges[start_idx]
            tile = find_tile_covering_edge(current_patch, src, dst)
            score = (1, 0, length)
            scored_candidates.append((start_idx, length, subpath, tile, score, 2))

        # Sort candidates: lowest score is best
        scored_candidates.sort(key=lambda x: x[4])
        chosen_idx, chosen_len, chosen_subpath, target, best_score, loops_count = scored_candidates[0]

        # Log splits if occurred
        if best_score[0] == 1:
            print(f"  Warning: Topological change/split detected at step {step_num}! (Remaining loops: {loops_count})", flush=True)

        path_id_str = all_locks[chosen_subpath]
        nat_lock_id = parse_lock_id_to_nat(path_id_str)
        
        # Track tile data before removal
        a, b, c, d_coord = target.origin.to_tuple()
        ori = target.orientation

        # Update report entry with lock and tile info
        report_entry["lock_used"] = nat_lock_id
        report_entry["tile_peeled"] = {"origin": (a, b, c, d_coord), "ori": ori}
        report_data.append(report_entry)
        
        current_patch.remove(target)
        next_b_poly, next_b_edges = extract_boundary_loop(current_patch)
        
        peel_steps.append({
            "lock_id": nat_lock_id,
            "a": a, "b": b, "c": c, "d": d_coord,
            "ori": ori,
            "next_state_serialized": serialize_lean_state(next_b_edges)
        })
        
        step_num += 1

    last_tile = current_patch[0]
    print(f"Cascade complete. Final remaining tile is at {last_tile.origin.to_tuple()}")

    # Record final single-tile boundary for the report
    final_b_poly, final_b_edges = extract_boundary_loop(current_patch)
    final_info = analyze_boundary(final_b_edges, all_locks)
    final_cycles = count_boundary_cycles(current_patch)
    report_data.append({
        "step": step_num,
        "tiles_remaining": 1,
        "boundary_info": final_info,
        "cycles": final_cycles,
        "lock_used": None,
        "tile_peeled": None,
    })

    # Generate boundary report
    generate_boundary_report(report_data, supertile_type, generation, report_path)

    # Write the CertificateData.lean file
    print(f"Writing Lean 4 certificate to {lean_output_path}...")
    os.makedirs(os.path.dirname(lean_output_path), exist_ok=True)
    
    lean_lines = [
        "/-",
        "Copyright (c) 2026 tryggth. All rights reserved.",
        "Released under Apache 2.0 license as described in the file LICENSE.",
        "Authors: tryggth",
        "-/",
        "import SpectreDeltaBoundary.Bedrock",
        "import SpectreDeltaBoundary.Paths",
        "import SpectreDeltaBoundary.Monotile",
        "import SpectreDeltaBoundary.Certificate",
        "",
        "/-!",
        f"# Peeling cascade certificate data for {supertile_type}_{generation}",
        "-/",
        "",
        "set_option linter.style.longLine false",
        "set_option linter.style.header false",
        "",
        "open LatticePoint",
        "",
        f"/-- Initial boundary of the aligned {supertile_type}_{generation} patch -/",
        f"def initialMetatileBoundary : PeelingState := {serialize_lean_state(aligned_loop_edges_rot)}",
        "",
        f"/-- Peeling certificate payload for {supertile_type}_{generation} -/",
        "def pythonPeelingCertificate : PeelingCertificate := ⟨[",
    ]

    for idx, step_info in enumerate(peel_steps):
        comma = "," if idx < len(peel_steps) - 1 else ""
        line = (
            f"  ⟨{step_info['lock_id']}, "
            f"⟨⟨{step_info['a']}, {step_info['b']}, {step_info['c']}, {step_info['d']}⟩, {step_info['ori']}⟩, "
            f"{step_info['next_state_serialized']}⟩{comma}"
        )
        lean_lines.append(line)

    lean_lines.append("]⟩")
    lean_lines.append("")

    with open(lean_output_path, "w") as f:
        f.write("\n".join(lean_lines) + "\n")
    print("Lean certificate file successfully generated!")
