# Spectre Delta Boundary Verification

This repository contains the formal mathematical verification of the boundary uniqueness and tile reduction cascade for a Generation-2 **Delta** metatile patch of Spectre aperiodic monotiles. 

For a detailed mathematical exposition of the proof and pipeline, read the accompanying paper: [paper/paper.pdf](paper/paper.pdf).

By unifying an optimized discrete combinatorial search pipeline written in Python with a rigorous, axiom-pure type-theoretic state machine written in **Lean 4**, this framework independently proves that local boundary turn constraints uniquely force a deterministic tiling cascade.

![Spectre Delta-2 Metatile Patch Boundary](./delta.svg)

---

## 📐 Project Architecture & Pipeline

The verification framework is engineered as a multi-stage verification pipeline:

```
[generate-n8-sieve.py]       --> Generates the foundational aperiodic lock database (CSV)
         │
[generate-lean-data.py]      --> Simulates the 70-step tile cascade & serializes 4D coordinates
         │
[Locks.lean]                 --> Proves the 5 core computational lock lemmas (Axiom-Free)
         │
[Certificate.lean]           --> Executes the edge-ledger symmetric difference state machine
         │
[Theorem.lean]               --> Triggers the Lean Kernel VM via 'decide' for the final QED
```

*   **The Explorer (Python):** Handles the intensive geometric search loops, tracking explicit vertex coordinates across the 4D cyclotomic integer ring $\mathbb{Z}[\zeta_{12}]$ and caching the aperiodic lock sieve.
*   **The Judge (Lean 4):** Re-calculates and type-checks every edge transition, local neighborhood collision, and turning constraint completely independently of the Python generation logic, discharging the final proof within the core kernel.

---

## 🗂️ File Directory Structure

```text
├── generate-n8-sieve.py          # Stateful Frontier Optimization engine for database generation
├── generate-lean-data.py         # Cascading geometric simulation & Lean serialization script
├── lakefile.lean                 # Lean 4 project configuration file
├── lean-toolchain                # Specifies the target Lean 4 compiler version
└── SpectreDeltaBoundary
    ├── Bedrock.lean              # 4D lattice algebra and rigid transformation matrix structures
    ├── Paths.lean                # Discrete direction step grammar and boundary lookback functions
    ├── Monotile.lean             # Rigidly aligned Spectre monotile vertex extraction engines
    ├── Locks.lean                # 5 standalone computational holographic lock lemmas
    ├── Certificate.lean          # Topological edge-annihilation state machine validator
    ├── CertificateData.lean      # Auto-generated 70-step explicit coordinate data payload
    └── Theorem.lean              # Main boundary uniqueness theorem and kernel entry point
```

---

## 🚀 Step-by-Step Replication Guide

Follow these instructions to clone the repository, recreate the localized database dependencies, and execute the formal kernel compilation.

### 1. Environment Setup

Ensure you have Python 3.x and the Lean 4 deployment tool (`elan`) fully configured on your local machine.

```bash
# Verify Lean 4 interactive environment toolchain
lake --version
python3 --version
```

### 2. Clone the Repository

Clone this workspace to your local system and navigate to the project directory:

```bash
git clone https://github.com/tryggth/delta-2-boundary.git
cd delta-2-boundary
```

### 3. Generate the Foundational Lock Database

Execute the optimization sieve script to construct the lookup database containing verified turn sequences and localized spatial profiles. This tool populates the CSV file that drives the cascade simulation.

```bash
python3 generate-n8-sieve.py
```

### 4. Run the Cascading Simulation & Serialize Coordinates

Execute the geometric peeling script. This engine runs the 70-step tile removal sequence, tracks the shifting boundaries, and exports the explicit coordinate arrays into a compile-ready Lean 4 anonymous constructor payload module.

```bash
python3 generate-lean-data.py
```

### 5. Execute the Formal Lean 4 Kernel Verification

Trigger the Lean 4 build engine. This step compiles the whole library and invokes the `decide` tactic on the top-level uniqueness theorem, forcing Lean's virtual machine to compute the entire reduction chain and verify its total logical purity.

```bash
lake build
```

A successful compilation output with zero errors or warnings confirms that the Lean kernel has formally evaluated and certified the complete boundary reduction proof.

---

## 🛡️ Axiom Purity & Audit

The proof stack is engineered to avoid any unproven shortcuts, translation assumptions, or custom extensions. You can verify the foundational logical dependencies of the terminal proof by inspecting the environment axioms directly:

```lean
#print axioms verify_delta2_uniqueness
```

The mathematical reduction depends solely on standard core foundations:
*   `propext` (Propositional Extensionality) — The standard identity axiom of Lean core logic.
*   `sorryAx` — **Completely Absent** from the entire dependency tree, guaranteeing a closed, verified proof.

---

## 🚀 Continuous Integration (CI/CD)

This repository features an automated GitHub Actions pipeline (`.github/workflows/compile-paper.yml`) that validates the entire verification pipeline on every push or pull request touching Lean source files or the LaTeX document source.

The pipeline ensures:
1.  **Lean Proof Purity:** Automatically fetches dependencies, compiles the proof library via `lake build`, and checks for axiom purity.
2.  **LaTeX Syntax Linting:** Runs a `chktex` validation pass on the expository paper source (`paper/paper.tex`) to maintain clean markup.
3.  **Automated PDF Compilation:** Compiles the paper to a PDF using `latexmk` and uploads the compiled paper as a workflow artifact, keeping the expository narrative rigidly synchronized with the verified codebase.

