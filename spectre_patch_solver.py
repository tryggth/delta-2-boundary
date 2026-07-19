#!/usr/bin/env python3
"""
Spectre Monotile Inflation, Boundary Extractor, Backtracking Solver & Peeling Certificate Generator.
Delegates to the modular spectre_solver package.
"""
import sys

# Ensure package can be imported from root folder
import os
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spectre_solver.main import main

if __name__ == "__main__":
    main()