import argparse
import time
import sys
import os

from spectre_solver.geometry import (
    LatticePoint, PlacedTile, Point2D, Z3,
    polygons_overlap, use_optimization, BASE_CENTROIDS,
    vec_to_dir, VEC_TO_DIR, dir_to_vec
)
from spectre_solver.tiling import (
    generate_inflated_patch, extract_boundary_loop,
    extract_perimeter_sequence
)
from spectre_solver.peeling import run_peeling_cascade

# Solver-specific globals
original_boundary_set = set()
uncovered_boundary = set()
total_backtracks = 0
last_telemetry_time = 0.0
solutions = []
global_float_boundary = []
guide_tile_map = {}

def get_candidate_tiles(target_src: LatticePoint, target_dst: LatticePoint) -> list[PlacedTile]:
    target_vec = target_dst.sub(target_src)
    candidates = []
    for orientation in range(12):
        t = PlacedTile(LatticePoint(0, 0, 0, 0), orientation, reflected=False)
        for i in range(14):
            v1 = t.vertices[i]
            v2 = t.vertices[i+1]
            edge_vec = v2.sub(v1)
            if edge_vec.to_tuple() == target_vec.to_tuple():
                origin = target_src.sub(v1)
                candidates.append(PlacedTile(origin, orientation, reflected=False))
    return candidates

def tile_leaks_outside(tile: PlacedTile, boundary_poly: list[Point2D]) -> bool:
    global use_optimization, global_float_boundary
    
    # 1. Centroid distance fast float check
    if use_optimization and global_float_boundary:
        fx, fy = tile.centroid_float
        close_to_boundary = False
        for i in range(len(global_float_boundary) - 1):
            x1, y1 = global_float_boundary[i]
            x2, y2 = global_float_boundary[i+1]
            dx = x2 - x1
            dy = y2 - y1
            t = 0.0
            denom = dx*dx + dy*dy
            if denom > 1e-9:
                t = ((fx - x1) * dx + (fy - y1) * dy) / denom
                t = max(0.0, min(1.0, t))
            dist = math_hypot(fx - (x1 + t * dx), fy - (y1 + t * dy))
            if dist < 3.0:
                close_to_boundary = True
                break
                
        if not close_to_boundary:
            count = 0
            n = len(global_float_boundary) - 1
            for i in range(n):
                x1, y1 = global_float_boundary[i]
                x2, y2 = global_float_boundary[i+1]
                if ((y1 >= fy) != (y2 >= fy)):
                    if fx < (x2 - x1) * (fy - y1) / (y2 - y1 + 1e-9) + x1:
                        count += 1
            if count % 2 == 0:
                return True
            return False

    # 2. Strict exact segment intersection check
    tile_pts = [v.to_point2d() for v in tile.vertices]
    n_t = len(tile_pts) - 1
    n_b = len(boundary_poly) - 1
    
    from spectre_solver.geometry import segments_intersect_float
    for i in range(n_t):
        t1, t2 = tile_pts[i], tile_pts[i+1]
        t1_f, t2_f = t1.to_float_coords(), t2.to_float_coords()
        for j in range(n_b):
            b1, b2 = boundary_poly[j], boundary_poly[j+1]
            b1_f, b2_f = b1.to_float_coords(), b2.to_float_coords()
            if segments_intersect_float(t1_f, t2_f, b1_f, b2_f):
                return True
                
    # 3. Exact centroid in polygon check
    sum_a = sum(v.a for v in tile.vertices[:-1])
    sum_b = sum(v.b for v in tile.vertices[:-1])
    sum_c = sum(v.c for v in tile.vertices[:-1])
    sum_d = sum(v.d for v in tile.vertices[:-1])
    sum_lp = LatticePoint(sum_a, sum_b, sum_c, sum_d)
    centroid_pt = sum_lp.to_point2d()
    
    boundary_scaled = [Point2D(p.x * Z3(14, 0), p.y * Z3(14, 0)) for p in boundary_poly]
    from spectre_solver.geometry import point_in_polygon
    if not point_in_polygon(centroid_pt, boundary_scaled):
        return True
        
    return False

def math_hypot(dx, dy):
    import math
    return math.hypot(dx, dy)

def check_frontier_loops(frontier) -> bool:
    global VEC_TO_DIR
    adj = {}
    for src, dst in frontier:
        s_tup = src.to_tuple()
        d_tup = dst.to_tuple()
        edge_vec = dst.sub(src).to_tuple()
        if edge_vec not in VEC_TO_DIR:
            return True
        if s_tup not in adj:
            adj[s_tup] = []
        adj[s_tup].append((d_tup, VEC_TO_DIR[edge_vec]))
        
    visited_edges = set()
    
    for start in adj:
        while True:
            next_edge = None
            for dst, d in adj[start]:
                if (start, dst) not in visited_edges:
                    next_edge = (dst, d)
                    break
            if not next_edge:
                break
                
            path = [start]
            path_dirs = []
            curr = start
            cycle = None
            cycle_dirs = None
            
            while True:
                edge = None
                if curr in adj:
                    for dst, d in adj[curr]:
                        if (curr, dst) not in visited_edges:
                            edge = (dst, d)
                            break
                if not edge:
                    break
                    
                dst, d = edge
                visited_edges.add((curr, dst))
                path.append(dst)
                path_dirs.append(d)
                
                if dst in path[:-1]:
                    idx = path.index(dst)
                    cycle = path[idx:-1]
                    cycle_dirs = path_dirs[idx:]
                    break
                curr = dst
                
            if cycle and cycle_dirs:
                n_nodes = len(cycle)
                area_float = 0.0
                pts_float = [LatticePoint(*v).to_float_coords() for v in cycle]
                pts_float.append(pts_float[0])
                for i in range(len(pts_float) - 1):
                    x1, y1 = pts_float[i]
                    x2, y2 = pts_float[i+1]
                    area_float += (x1 * y2) - (y1 * x2)
                area_float = 0.5 * area_float
                
                # Corrected area pruning threshold from 59.0 to 12.0
                if abs(area_float) < 12.0:
                    return False
                    
    return True

def solve_internal_patch(placed_tiles: list[PlacedTile], frontier: list[tuple[LatticePoint, LatticePoint]], boundary_poly: list[Point2D], start_time: float, args):
    global total_backtracks, last_telemetry_time, solutions, global_float_boundary, original_boundary_set, uncovered_boundary, guide_tile_map
    
    if args.optimize and not global_float_boundary:
        global_float_boundary = [(p.x.to_float(), p.y.to_float()) for p in boundary_poly]

    curr_time = time.time()
    if curr_time - last_telemetry_time >= 2.0 or total_backtracks % 5000 == 0:
        elapsed = curr_time - start_time
        print(f"Telemetry: Elapsed={elapsed:.2f}s | Backtracks={total_backtracks} | Tiles Placed={len(placed_tiles)}", flush=True)
        last_telemetry_time = curr_time
        
    if args.boundary_only:
        if not uncovered_boundary:
            solutions.append(list(placed_tiles))
            sol_idx = len(solutions)
            print(f"SUCCESS: Found boundary ring solution {sol_idx}! (Tiles={len(placed_tiles)})", flush=True)
            if sol_idx <= 5:
                export_single_solution_to_svg(placed_tiles, sol_idx, "./solutions/")
            return
    else:
        if not frontier:
            solutions.append(list(placed_tiles))
            sol_idx = len(solutions)
            print(f"SUCCESS: Found solution {sol_idx}! (Tiles={len(placed_tiles)})", flush=True)
            if sol_idx <= 5:
                export_single_solution_to_svg(placed_tiles, sol_idx, "./solutions/")
            return
        
    target_src, target_dst = frontier[0]
    
    covered = False
    for tile in placed_tiles:
        for t_src, t_dst, _ in tile.edges:
            if t_src == target_src.to_tuple() and t_dst == target_dst.to_tuple():
                covered = True
                break
        if covered:
            break
            
    if covered:
        solve_internal_patch(placed_tiles, frontier[1:], boundary_poly, start_time, args)
        return
        
    candidates = get_candidate_tiles(target_src, target_dst)
    
    # Guided search prioritization
    if args.guide and guide_tile_map:
        target_key = (target_src.to_tuple(), target_dst.to_tuple())
        expected = guide_tile_map.get(target_key)
        if expected is None:
            expected = guide_tile_map.get((target_key[1], target_key[0]))
        if expected is not None:
            candidates.sort(key=lambda c: 0 if (c.origin.to_tuple() == expected.origin.to_tuple() and c.orientation == expected.orientation and c.reflected == expected.reflected) else 1)

    for candidate in candidates:
        if args.boundary_only:
            shares_boundary = False
            for src, dst, _ in candidate.edges:
                if (src, dst) in original_boundary_set or (dst, src) in original_boundary_set:
                    shares_boundary = True
                    break
            if not shares_boundary:
                continue

        overlap = False
        for tile in placed_tiles:
            if polygons_overlap(candidate, tile):
                overlap = True
                break
        if overlap:
            continue
            
        if tile_leaks_outside(candidate, boundary_poly):
            continue
            
        new_frontier = list(frontier)
        removed_from_uncovered = []
        if args.boundary_only:
            for src, dst, _ in candidate.edges:
                if (src, dst) in uncovered_boundary:
                    uncovered_boundary.remove((src, dst))
                    removed_from_uncovered.append((src, dst))
                elif (dst, src) in uncovered_boundary:
                    uncovered_boundary.remove((dst, src))
                    removed_from_uncovered.append((dst, src))

        for v1_tup, v2_tup, d in candidate.edges:
            v1 = LatticePoint(*v1_tup)
            v2 = LatticePoint(*v2_tup)
            found_idx = -1
            for idx, (f_src, f_dst) in enumerate(new_frontier):
                if f_src.to_tuple() == v1.to_tuple() and f_dst.to_tuple() == v2.to_tuple():
                    found_idx = idx
                    break
            if found_idx != -1:
                new_frontier.pop(found_idx)
            else:
                is_already_covered = False
                for tile in placed_tiles:
                    for t_src, t_dst, _ in tile.edges:
                        if t_src == v1.to_tuple() and t_dst == v2.to_tuple():
                            is_already_covered = True
                            break
                    if is_already_covered:
                        break
                if not is_already_covered:
                    new_frontier.append((v2, v1))
                    
        if check_frontier_loops(new_frontier):
            solve_internal_patch(placed_tiles + [candidate], new_frontier, boundary_poly, start_time, args)
            
        if args.boundary_only:
            for edge in removed_from_uncovered:
                uncovered_boundary.add(edge)

        total_backtracks += 1

def export_single_solution_to_svg(solution: list[PlacedTile], idx: int, output_dir: str):
    os.makedirs(output_dir, exist_ok=True)
    all_x, all_y = [], []
    for tile in solution:
        for v in tile.vertices:
            fx, fy = v.to_float_coords()
            all_x.append(fx)
            all_y.append(fy)
    if not all_x: return
    min_x, max_x = min(all_x), max(all_x)
    min_y, max_y = min(all_y), max(all_y)
    
    width = max_x - min_x
    height = max_y - min_y
    padding = max(1.0, 0.05 * max(width, height))
    
    svg_content = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x - padding:.4f} {min_y - padding:.4f} {width + 2 * padding:.4f} {height + 2 * padding:.4f}" width="100%" height="100%">'
    ]
    for tile in solution:
        points = " ".join(f"{v.to_float_coords()[0]:.4f},{v.to_float_coords()[1]:.4f}" for v in tile.vertices[:-1])
        fill_color = "#ffb3b3" if tile.reflected else "#aaccff"
        svg_content.append(f'  <polygon points="{points}" fill="{fill_color}" stroke="#111111" stroke-width="0.05" />')
    svg_content.append('</svg>')
    
    filepath = os.path.join(output_dir, f"solution_{idx}.svg")
    with open(filepath, "w") as f:
        f.write("\n".join(svg_content))
    print(f"Dynamically exported solution {idx} to {filepath}", flush=True)

def main():
    global use_optimization, original_boundary_set, uncovered_boundary, guide_tile_map
    
    parser = argparse.ArgumentParser(description="Spectre Monotile Inflation, Solver & Peeling Certificate Generator")
    parser.add_argument("-t", "--type", type=str, default="Delta", help="Base supertile type (default: Delta)")
    parser.add_argument("-g", "--generation", type=int, default=2, help="Inflation generation depth (default: 2)")
    parser.add_argument("--solve", action="store_true", help="Run backtracking solver to reconstruct the interior layout")
    parser.add_argument("--optimize", action="store_true", help="Enable fast float-based centroid-distance pruning")
    parser.add_argument("-b", "--boundary-only", action="store_true", help="Only place tiles that share at least one edge with the original boundary")
    parser.add_argument("--guide", action="store_true", help="Guide the solver using the generated patch solution for fast verification")
    parser.add_argument("--cert", action="store_true", help="Run external boundary peeling cascade solver and generate Lean certificate")
    parser.add_argument("--locks-csv", type=str, default="/home/tryggth2009/boundary/spectre_optimized_sieve_N8.csv", help="Path to lock database N8 CSV file")
    parser.add_argument("--lean-out", type=str, default="./SpectreDeltaBoundary/CertificateData.lean", help="Path to write Lean 4 certificate file")
    parser.add_argument("--report", nargs="?", const="auto", default=None, help="Generate boundary report. Optionally specify output path; if omitted prints to stdout; if 'auto' generates versioned filename.")
    
    args = parser.parse_args()
    if args.generation > 2:
        print(f"Unsupported for generation {args.generation}")
        sys.exit(1)
    use_optimization = args.optimize
    
    print(f"Generating inflated patch of type '{args.type}' at depth {args.generation}...")
    patch = generate_inflated_patch(args.type, args.generation, LatticePoint(0, 0, 0, 0), 0, reflected=(args.generation % 2 == 1))
    print(f"Total tiles generated: {len(patch)}")
    
    overlaps = sum(1 for i in range(len(patch)) for j in range(i + 1, len(patch)) if polygons_overlap(patch[i], patch[j]))
    if overlaps > 0:
        print(f"WARNING: Detected {overlaps} overlapping tile pairs!")
    else:
        print("Success: Generated patch has no overlapping tiles!")
        
    turns = extract_perimeter_sequence(patch)
    print(f"Perimeter sequence length: {len(turns)}")
    print(f"Cumulative turn sum: {sum(turns)} degrees")
    
    # SVG Export
    svg_filename = f"{args.type.lower()}_{args.generation}.svg"
    print(f"Exporting raw patch visualization to {svg_filename}...")
    xs = [v[0] for tile in patch for v in tile.vertices_float[:-1]]
    ys = [v[1] for tile in patch for v in tile.vertices_float[:-1]]
    if xs and ys:
        min_x, max_x = min(xs), max(xs)
        min_y, max_y = min(ys), max(ys)
        pad = 2.0
        w = max_x - min_x + 2*pad
        h = max_y - min_y + 2*pad
        colors = ["#1f2833", "#112233", "#1b4d3e", "#004b49", "#2d3748", "#1a365d", "#1e3a8a", "#0f766e", "#4a5568", "#1d4ed8", "#2563eb", "#0d9488"]
        with open(svg_filename, "w") as f:
            f.write(f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x-pad:.4f} {min_y-pad:.4f} {w:.4f} {h:.4f}" width="100%" height="100%">\n')
            f.write(f'  <rect x="{min_x-pad:.4f}" y="{min_y-pad:.4f}" width="{w:.4f}" height="{h:.4f}" fill="#0b0c10" />\n')
            for tile in patch:
                pts = " ".join(f"{v[0]:.4f},{v[1]:.4f}" for v in tile.vertices_float[:-1])
                color = colors[tile.orientation % len(colors)]
                f.write(f'  <polygon points="{pts}" fill="{color}" stroke="#c5c6c7" stroke-width="0.08" stroke-linejoin="round" />\n')
            f.write('</svg>\n')
        print(f"Successfully wrote {svg_filename}!")

    if args.solve:
        if args.guide:
            guide_tile_map = {}
            for tile in patch:
                for src, dst, _ in tile.edges:
                    guide_tile_map[(src, dst)] = tile
                    
        print("\nInitializing inward backtracking solver...")
        start_time = time.time()
        boundary_poly, loop_edges = extract_boundary_loop(patch)
        print(f"Frontier initialized with {len(loop_edges)} inward-facing boundary edges.")
        
        if args.boundary_only:
            original_boundary_set = { (src.to_tuple(), dst.to_tuple()) for src, dst in loop_edges }
            uncovered_boundary = set(original_boundary_set)
            
        solve_internal_patch([], loop_edges, boundary_poly, start_time, args)
        
        end_time = time.time()
        print("\n" + "="*50)
        print("SOLVER PERFORMANCE LOGS")
        print("="*50)
        print(f"Total Time Taken: {end_time - start_time:.4f} seconds")
        print(f"Total Backtracks: {total_backtracks}")
        print(f"Total Solutions Found: {len(solutions)}")
        print("="*50)

    if args.cert:
        print("\nInitializing peeling cascade solver to generate Lean certificate...")
        # Determine report path
        report_path = None
        if args.report is not None:
            if args.report == "auto":
                # Auto-generate versioned filename
                import glob
                base = f"{args.type.lower()}_{args.generation}_boundary_report"
                existing = glob.glob(f"{base}_v*.csv")
                version = len(existing) + 1
                report_path = f"{base}_v{version}.csv"
            elif args.report:
                report_path = args.report
            # else: report_path stays None => prints to stdout
        run_peeling_cascade(patch, args.locks_csv, args.type, args.generation, args.lean_out, report_path=report_path)

if __name__ == "__main__":
    main()
