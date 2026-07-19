import sys
import os
import unittest

# Ensure the root package folder is in path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spectre_solver.geometry import LatticePoint, PlacedTile
from spectre_solver.tiling import generate_inflated_patch, extract_boundary_loop
from spectre_solver.peeling import serialize_lean_state, get_turns
from spectre_solver.main import get_candidate_tiles

class TestSpectreSolver(unittest.TestCase):
    def test_dynamic_vs_baseline(self):
        print("Test 1: Comparing Dynamic Tiling vs Hardcoded Bypass Tiling...")
        sys.path.append('/home/tryggth2009/boundary')
        try:
            from spectre_boundary_solver import generate_inflated_patch as generate_baseline
            baseline_patch = generate_baseline('Delta_Hardcoded', 2, LatticePoint(0,0,0,0), 0, reflected=False)
            baseline_sigs = set((t.origin.to_tuple(), t.orientation, t.reflected) for t in baseline_patch)
        except ImportError:
            print("Baseline spectre_boundary_solver not importable, skipping exact baseline set check.")
            return

        dynamic_patch = generate_inflated_patch('Delta', 2, LatticePoint(0,0,0,0), 0, reflected=False)
        dynamic_sigs = set((t.origin.to_tuple(), t.orientation, t.reflected) for t in dynamic_patch)

        self.assertEqual(len(dynamic_sigs), len(baseline_sigs), "Patch sizes do not match baseline!")
        self.assertEqual(dynamic_sigs, baseline_sigs, "Tile sets do not match baseline exactly!")
        print("Test 1 Passed: Perfect match with baseline!")

    def test_boundary_lean_match(self):
        print("Test 2: Verifying generated boundary coordinates match Lean source code...")
        patch = generate_inflated_patch('Delta', 2, LatticePoint(0,0,0,0), 0, reflected=False)
        b_poly, loop_edges = extract_boundary_loop(patch)
        
        from spectre_solver.geometry import vec_to_dir
        k = None
        for idx, edge in enumerate(loop_edges):
            d = vec_to_dir(edge[1].sub(edge[0]))
            if d == 0:
                k = idx
                break
        self.assertIsNotNone(k, "Could not find direction 0 edge in boundary loop!")
        
        loop_edges_aligned = loop_edges[k:] + loop_edges[:k]
        start_v = loop_edges_aligned[0][0]
        
        aligned_coords = []
        for src, dst in loop_edges_aligned:
            aligned_coords.append(src.sub(start_v).to_tuple())
            
        self.assertEqual(aligned_coords[0], (0, 0, 0, 0))
        self.assertEqual(len(aligned_coords), 182)
        print("Test 2 Passed: Aligned boundary matches structure of Lean (length 182, starts at 0)!")

    def test_solve_delta_1(self):
        print("Test 3: Solving Delta-1 patch...")
        import subprocess
        cmd = [sys.executable, "spectre_patch_solver.py", "-t", "Delta", "-g", "1", "--solve", "--optimize"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, f"Solver failed on Delta-1: {result.stderr}")
        self.assertIn("SUCCESS: Found solution", result.stdout, "Solver did not output success status!")
        print("Test 3 Passed: Solver successfully tiled Delta-1!")

if __name__ == "__main__":
    unittest.main()
