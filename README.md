# Spectre Delta Boundary Verification & Aperiodic Holography

This repository contains the complete, axiom-pure formal mathematical verification in **Lean 4** of **Aperiodic Holography** for the **Spectre** chiral aperiodic monotile ($\text{Tile}(1,1)$), defined in the landmark paper **"A chiral aperiodic monotile"** ([arXiv:2305.17743](https://arxiv.org/abs/2305.17743)) by Smith, Myers, Kaplan, and Goodman-Strauss.

For a detailed mathematical exposition of the proof and pipeline, read the accompanying monograph paper: [paper/paper.pdf](paper/paper.pdf). For exhaustive documentation on the algebraic foundations, cyclotomic ring math, 3-anchor-lock registry, simple closed path uniqueness, and zero-phason theorems, visit the [Project Wiki](https://github.com/tryggth/delta-2-boundary/wiki).

By unifying an exact discrete combinatorial solver in Python with a verifiable, axiom-pure type-theoretic state machine in **Lean 4**, this project formally proves four core results with **zero `sorry`s and zero custom axioms**:

1. **3-Anchor-Lock Uniqueness of $\Delta_2$ & All 9 Tier-1 Metatiles (`Theorem.lean`, `Tier1Theorems.lean`):**
   A deterministic priority algorithm (`L2 > L1 > L4`) using strictly 3 boundary turn locks—**Lock #2** (`300049`, `[60°, 90°, 60°]`), **Lock #1** (`300033`, `[60°, 0°, -60°]`), and **Lock #4** (`400110`, `[90°, -60°, 90°, 60°]`)—uniquely forces all 71 interior tiles of the Generation-2 $\Delta_2$ boundary (`55` Lock #2, `10` Lock #1, `6` Lock #4) as well as all 9 Tier-1 metatiles ($\Gamma, \Delta, \Theta, \Lambda, \Xi, \Pi, \Sigma, \Phi, \Psi$).
2. **Uniqueness of Interiors for Simple Closed Paths (`SimplePaths.lean`):**
   Every simple closed path (a closed loop visiting each node/vertex at most once) constructed from edges of the unique interior tiling of $\Delta_2$ has a unique interior sub-patch forced by the 71-step acyclic 3-lock elimination order.
3. **Interactive Spectre $\Delta_2$ Jigsaw Puzzle PWA (`puzzle/`, `docs/`):**
   An offline-capable Progressive Web App synchronized with the exact CCW orientations, `[0°, 330°]` angles, 3-anchor-lock (`L2`, `L1`, `L4`) highlights, and 71-step priority peeling sequence of the Lean 4 proof.
4. **Absence of Phasons in Full Spectre Tilings (`AlgebraicBoundary.lean`):**
   Combining Combinatorial Gauss-Bonnet ($12$ step-units $= 360^\circ$), the verified 4-batch transfer-matrix curvature bound ($\le 2$ step-units $= 60^\circ$ for lock-free cycles), and 3-anchor-lock pocket forcing proves that no minimal phason and no finite phason flip can exist in any full aperiodic tiling by the $\text{Tile}(1,1)$ Spectre monotile.

![Spectre Delta-2 Metatile Patch Boundary](./delta.svg)

---

## 🎬 Peeling Cascade Animation

Watch the complete tile reduction and boundary peeling cascade animation:

[![Spectre Delta-2 Peeling Cascade Animation](https://img.shields.io/badge/Watch-Peeling%20Animation-ff007f?style=for-the-badge&logo=play)](./media/peeling_animation.mp4)

*(The animation highlights the active boundary lock turn sequence, the uniquely forced tile, and the resulting new boundary loop at each step of the deterministic reduction cascade verified in Lean 4.)*

## 🧩 Interactive Spectre Metatile Jigsaw Puzzle PWA

A full-featured Progressive Web App (PWA) jigsaw puzzle for the 71-tile Generation-2 Spectre $\Delta_2$ patch and Tier-1 metatiles is included in this repository under [puzzle/](puzzle/) (mirrored to [docs/](docs/)) and hosted live on GitHub Pages:

[![Play Live PWA](https://img.shields.io/badge/Play_Live-Spectre_Puzzle_PWA-6366f1?style=for-the-badge&logo=github&logoColor=white)](https://tryggth.github.io/delta-2-boundary/)
👉 **[Launch Live Spectre Jigsaw Puzzle App](https://tryggth.github.io/delta-2-boundary/)**

### Key Features:
- **Interactive Drag & Snap Jigsaw Engine:** Drag, rotate (`0°–330°` CCW, matching Lean's `ori ∈ {0..11}`), and snap Spectre monotile pieces onto the board with automatic geometric overlap and boundary validation.
- **Dynamic Metatile Boundary Selector:** Switch between the 71-tile Generation-2 $\Delta_2$ boundary frame, the 9-tile Tier-1 $\Delta$ cluster, and the 8-tile $\Gamma$ metatile.
- **Formal 3-Anchor-LockPlayback (`⏩ Step Next`):** Step one-by-one through the exact 71-step 3-Anchor-Lock (`L2 > L1 > L4`) sequence proven in `CertificateData.lean`, displaying the forcing lock (`L2`, `L1`, or `L4`) at each step.
- **Hidden Mode (`Ctrl+Shift+L` / `Alt+Shift+L`):** Exposes tile IDs, live boundary vertex turn tooltips, session log export, and interactive highlight toggles for the 3 Anchor Locks in priority order:
  - **`L2` (`#300049`, Priority 1):** High Lock `[60°, 90°, 60°]`
  - **`L1` (`#300033`, Priority 2):** Low Lock `[60°, 0°, -60°]`
  - **`L4` (`#400110`, Priority 3):** Long Lock `[90°, -60°, 90°, 60°]`
- **Installable & Offline-Capable PWA:** One-click desktop and mobile installation with an auto-updating Network-First Service Worker (`sw.js`).

---

## 🛠️ Spectre Tiling & Peeling Solver CLI

The project includes a modular Python solver suite located under [spectre_solver/](spectre_solver/) and exposed via the root-level CLI wrapper [spectre_patch_solver.py](spectre_patch_solver.py).

### Core Features:
1. **Dynamic Inflation Generator:** Generates exact hierarchical metatile patches over the cyclotomic lattice $\mathbb{Z}[\zeta_{12}]$ for all 9 supertile types up to Generation 2.
2. **3-Anchor-Lock (`L2 > L1 > L4`) Priority Peeling Engine:** Executes the deterministic priority algorithm:
   - While the interior is not complete:
     - If a Lock #2 (`300049`, `[60°, 90°, 60°]`) sequence exists on the CCW boundary, peel that anchored tile;
     - Else if a Lock #1 (`300033`, `[60°, 0°, -60°]`) sequence exists on the boundary, peel that anchored tile;
     - Else if a Lock #4 (`400110`, `[90°, -60°, 90°, 60°]`) sequence exists on the boundary, peel that anchored tile.
3. **Lean 4 Certificate Serialization:** Directly outputs compiling Lean 4 certificate payloads (`CertificateData.lean` and `Tier1Certificates.lean`) for kernel verification (`--cert`).

### Quick CLI Reference:
* **Run the 3-Anchor-Lock peeling cascade and regenerate the Lean 4 $\Delta_2$ certificate:**
  ```bash
  python3 spectre_patch_solver.py -t Delta -g 2 --cert --lean-out ./SpectreDeltaBoundary/CertificateData.lean
  ```
* **Solve a Gen-2 Delta patch layout via inward backtracking:**
  ```bash
  python3 spectre_patch_solver.py -t Delta -g 2 --solve --optimize --guide
  ```

---

## 📐 Project Architecture & Pipeline

```
[spectre_solver/peeling.py]  --> Simulates the 71-step 3-Anchor-Lock (L2 > L1 > L4) cascade
         │
[Locks.lean]                 --> Proves 14-edge alignment uniqueness for Locks #2, #1, #4
         │
[Certificate.lean]           --> Validates L2 > L1 > L4 priority & edge-ledger annihilation
         │
[Theorem.lean / Tier1Theorems.lean] --> Kernel verification via 'decide' (= some [])
         │
[SimplePaths.lean]           --> Proves unique interiors for all simple closed tile paths
         │
[AlgebraicBoundary.lean]     --> Proves the Global Zero-Phason Theorem (no phason flips)
```

---

## 🗂️ File Directory Structure

```text
├── spectre_patch_solver.py       # Root CLI entry point for tiling & certificate generation
├── spectre_solver/               # Modular Python cyclotomic geometry & 3-lock peeling package
├── puzzle/ & docs/               # Interactive Spectre Δ₂ Jigsaw Puzzle PWA (GitHub Pages)
├── paper/paper.tex               # LaTeX monograph source documenting the formal proof
├── wiki/                         # Technical Wiki documentation pages
├── lakefile.lean                 # Lean 4 project configuration file
├── lean-toolchain                # Target Lean 4 compiler version (v4.31.0)
└── SpectreDeltaBoundary
    ├── Bedrock.lean              # 4D cyclotomic lattice Z[ζ₁₂] & exact 30° rotation algebra
    ├── Paths.lean                # Discrete direction step grammar & exact Z[√3] segment sensors
    ├── Monotile.lean             # Canonical CCW Spectre monotile turns, vertices & edge alignment
    ├── Locks.lean                # 3-Anchor-Lock (300049, 300033, 400110) 14-edge uniqueness engine
    ├── Certificate.lean          # Priority lock selector (L2 > L1 > L4) & edge-ledger state machine
    ├── CertificateData.lean      # 71-step 3-Anchor-Lock certificate payload for Δ₂
    ├── Theorem.lean              # Main Δ₂ tiling uniqueness & 3-lock invariant theorems
    ├── SimplePaths.lean          # Uniqueness of interiors for all simple closed paths in Δ₂
    ├── Tier1Certificates.lean    # 3-Anchor-Lock certificates for all 9 Tier-1 metatiles (Γ..Ψ)
    ├── Tier1Theorems.lean        # Formal uniqueness theorems for all 9 Tier-1 metatiles
    ├── AlgebraicBoundary.lean    # Gauss-Bonnet, Transfer-Matrix bound & Global Zero-Phason Theorem
    └── Geometry
        ├── Topology.lean             # Combinatorial Gauss-Bonnet & interior angle invariants
        └── TransferMatrixBatches.lean # 4-batch punctured-state DFS curvature verification (≤ 60°)
```

---

## 🚀 Step-by-Step Replication Guide

### 1. Environment Setup
Ensure you have Python 3.x and the Lean 4 toolchain manager (`elan`) installed:
```bash
lake --version
python3 --version
```

### 2. Clone the Repository
```bash
git clone https://github.com/tryggth/delta-2-boundary.git
cd delta-2-boundary
```

### 3. Run the Python Solver Integration Tests
```bash
python3 test_solver_integration.py
```

### 4. Execute the Formal Lean 4 Kernel Verification
Compile the entire formal library and verify all theorems across Phases 1–4:
```bash
lake build
```
A clean compilation (`Build completed successfully (777 jobs)`) with zero warnings and zero errors confirms that the Lean 4 kernel has verified the entire proof tree.

---

## 🛡️ Axiom Purity & Audit

Every module in `SpectreDeltaBoundary` is engineered with **zero `sorry`s (`sorryAx`) and zero custom axioms**. You can inspect the logical foundations of the main theorems directly in Lean 4:

```lean
#print axioms verify_delta2_uniqueness
#print axioms delta2_lock_elimination_sequence_valid
#print axioms simple_closed_path_unique_interior
#print axioms no_phason_in_full_tiling
#print axioms spectre_hierarchy_zero_phasons
```

All computational reflection theorems depend solely on `propext`, and the classical contradiction theorems in `AlgebraicBoundary.lean` depend solely on Lean's standard core logical axioms (`[propext, Classical.choice, Quot.sound]`).

---

## 🚀 Continuous Integration (CI/CD)

This repository includes an automated GitHub Actions workflow (`.github/workflows/compile-paper.yml`) that validates the Lean 4 proof library (`lake build`), lints `paper/paper.tex` via `chktex`, and compiles `paper/paper.pdf` via `latexmk` on every push.
