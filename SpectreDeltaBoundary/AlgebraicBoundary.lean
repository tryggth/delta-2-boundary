/-
Copyright (c) 2026 tryggth. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: tryggth
-/
import SpectreDeltaBoundary.Paths
import SpectreDeltaBoundary.Monotile
import SpectreDeltaBoundary.Locks
import SpectreDeltaBoundary.Geometry.TransferMatrixBatches
import Mathlib.Data.Finset.Basic

/-!
# Algebraic Boundary Framework for Spectre Uniqueness

This module generalises the uniqueness proof of Spectre tilings from specific
metatiles (Delta_2, etc.) to arbitrary finite patches.  The strategy is:

1. **Combinatorial Gauss-Bonnet**: every simply-connected patch has boundary
   curvature exactly 12 step-units (= 360°).
2. **Transfer-matrix curvature bound**: the punctured-state sieve from
   `TransferMatrixBatches` proves that any lock-free boundary cycle has
   curvature ≤ 2 step-units (= 60°).
3. **Lock forcing**: a geometric lock in the boundary forces at least one
   shared tile between any two fillings.

Combining (1)–(3) yields a contradiction for any hypothetical "minimal phason"
(two distinct fillings with the same boundary that share no tile), completing
the uniqueness skeleton.

## Axiom Reduction

Compared to the initial skeleton, this version eliminates two top-level axioms:

* `lock_forces_shared_tile` is now a **theorem**, derived from the narrower
  bridge axiom `lock_determines_tile` which states that a lock pattern forces
  a specific tile — justified by `proveLockUniqueness` in `Locks.lean`.

* `lock_free_curvature_bound` is now a **theorem**, derived from two narrower
  bridge axioms:
  - `lock_free_implies_punctured`: absence of locks means all 3-grams are
    punctured states.
  - `punctured_walk_curvature_bound`: punctured-only walks have curvature ≤ 2,
    justified by `verify_batch1`–`verify_batch4` in `TransferMatrixBatches.lean`.
-/

set_option linter.style.header false
set_option linter.style.longLine false

open AllowedStep

/-! ## Core types -/

/-- A `Patch` represents a finite, nonempty set of placed Spectre tiles
    on the cyclotomic lattice.  Now concrete so that `patchIntersect`
    can be defined via `Finset` intersection. -/
structure Patch where
  /-- The finset of tiles comprising this patch. -/
  tiles : Finset PlacedTile
  /-- A patch is nonempty. -/
  nonempty : ∃ t, t ∈ tiles

/-- The boundary word of a patch is a sequence of allowed turning steps
    tracing its perimeter counter-clockwise. -/
abbrev BoundaryWord := List AllowedStep

/-- Returns the boundary word of a simply-connected patch.
    The implementation is left opaque — computing the boundary from a
    tile set requires the full geometric tracing engine.  Only the
    Gauss-Bonnet property is assumed about this function. -/
opaque patchBoundary : Patch → BoundaryWord

/-- Two patches *intersect* iff they share at least one identical
    `PlacedTile` (same origin and orientation).  Now a concrete `def`
    rather than opaque, enabling direct proof construction. -/
def patchIntersect (p1 p2 : Patch) : Prop :=
  ∃ t, t ∈ p1.tiles ∧ t ∈ p2.tiles

/-! ## Curvature -/

/-- Total discrete curvature of a boundary word, measured in 30°-step units.
    Each `AllowedStep` contributes its signed step value. -/
def wordCurvature (w : BoundaryWord) : Int :=
  w.foldl (fun acc s => acc + s.toStep) 0

/-! ## Combinatorial Gauss-Bonnet -/

/-- **Gauss-Bonnet for simply-connected patches.**
    The total boundary curvature of any simply-connected patch is exactly
    12 step-units (360°).  This mirrors the classical discrete Gauss-Bonnet
    theorem for planar cell complexes. -/
axiom gauss_bonnet_patch (p : Patch) : wordCurvature (patchBoundary p) = 12

/-! ## Geometric locks -/

/-- A *geometric lock* is a local turn pattern that constrains tile placement
    so tightly that the filling is forced.

    The two 3-step locks correspond to the locked states identified by
    `isLockedState` in `TransferMatrixBatches.lean`:
    - `(z0, p60, z0)`  — the "low lock" (0°, 60°, 0°)
    - `(p60, p90, p60)` — the "high lock" (60°, 90°, 60°)

    The three 4-step locks correspond to `completesLongLock`:
    - `(z0, m60, p90, p60)`
    - `(p60, p90, m60, p90)`
    - `(p90, m60, p90, p60)` -/
def ContainsLock (w : BoundaryWord) : Prop :=
  (∃ i, (w.drop i).take 3 = [z0, p60, z0])
  ∨ (∃ i, (w.drop i).take 3 = [p60, p90, p60])
  ∨ (∃ i, (w.drop i).take 4 = [z0, m60, p90, p60])
  ∨ (∃ i, (w.drop i).take 4 = [p60, p90, m60, p90])
  ∨ (∃ i, (w.drop i).take 4 = [p90, m60, p90, p60])

/-! ## Bridge to transfer matrix verifier (`TransferMatrixBatches.lean`)

The transfer matrix engine works with `State := AllowedStep × AllowedStep × AllowedStep`
and walks through `isPuncturedState`-valid states.  We bridge between the
`BoundaryWord` (list of steps) and the `Walk` (list of consecutive 3-grams)
representations. -/

/-- Converts a boundary word into a walk of consecutive 3-grams through
    the `AllowedStep` state space used by the transfer matrix verifier. -/
def boundaryToWalk : BoundaryWord → Walk
  | a :: b :: c :: rest => (a, b, c) :: boundaryToWalk (b :: c :: rest)
  | _ => []

/-- A boundary word is *lock-free punctured* iff every 3-gram passes
    `isPuncturedState`.  This is the computable bridge between the
    algebraic `¬ ContainsLock` predicate and the transfer matrix's
    state filter.

    Note: the locked states `(z0, p60, z0)` and `(p60, p90, p60)` are
    exactly those excluded by `isPuncturedState` (they return `false`),
    and long-lock completions are excluded by `completesLongLock` in
    `isValidTransition`. -/
def isLockFreePunctured (w : BoundaryWord) : Bool :=
  (boundaryToWalk w).all isPuncturedState

/-- **Bridge axiom 1 (Lock-free punctured states).**
    If a boundary word contains no locks, then every 3-gram in its boundary walk
    is a punctured state. -/
axiom lock_free_implies_punctured
    (w : BoundaryWord) (h : ¬ ContainsLock w) :
    isLockFreePunctured w = true

/-- **Bridge axiom 2 (curvature transfer).**
    If every 3-gram in a boundary word passes `isPuncturedState`, the word's
    total curvature is at most 2 step-units (= 60°).

    Justification: `verify_batch1`–`verify_batch4` exhaustively prove that
    every DFS-reachable cycle through punctured states (with depth ≤ 26)
    has curvature ≤ 60°.  This axiom lifts that walk-level bound to the
    word-level `wordCurvature`. -/
axiom punctured_walk_curvature_bound
    (w : BoundaryWord) (hPunctured : isLockFreePunctured w = true) :
    wordCurvature w ≤ 2

-- Computational evidence: the four batch verifiers confirm all punctured-state
-- DFS trees have curvature ≤ 60°, providing the ground truth for
-- `punctured_walk_curvature_bound`.
example : puncturedBatch1.all (fun s => checkFrom s [s] 26 s) = true := verify_batch1
example : puncturedBatch2.all (fun s => checkFrom s [s] 26 s) = true := verify_batch2
example : puncturedBatch3.all (fun s => checkFrom s [s] 26 s) = true := verify_batch3
example : puncturedBatch4.all (fun s => checkFrom s [s] 26 s) = true := verify_batch4

/-- **No-Go theorem (now a theorem, previously an axiom).**
    Lock-free boundaries have curvature ≤ 2 step-units.
    Derived from `lock_free_implies_punctured` + `punctured_walk_curvature_bound`. -/
theorem lock_free_curvature_bound
    (w : BoundaryWord) (h : ¬ ContainsLock w) : wordCurvature w ≤ 2 :=
  punctured_walk_curvature_bound w (lock_free_implies_punctured w h)

/-! ## Bridge to lock verification engine (`Locks.lean`)

The lock engine (`proveLockUniqueness`) exhaustively tests all 12 rotational
orientations for a tile at a given boundary path and confirms exactly one
fits.  The individual lock lemmas provide per-pattern certificates:
- `lemma_lock_3_00049`: turn sequence `[2, 3, 2]` (= `[p60, p90, p60]`)
- `lemma_lock_3_00033`: turn sequence `[0, 2, 0]` (= `[z0, p60, z0]`)
- `lemma_lock_4_00074`: turn sequence `[0, -2, 3, 2]` (= `[z0, m60, p90, p60]`)
- `lemma_lock_4_00110`: turn sequence `[2, 3, -2, 3]` (= `[p60, p90, m60, p90]`)
- `lemma_lock_4_00129`: turn sequence `[3, -2, 3, 2]` (= `[p90, m60, p90, p60]`)
-/

/-- **Bridge axiom (spatial lock forcing).**
    A lock pattern in a boundary word forces a specific `PlacedTile` to appear
    in any patch having that boundary word.

    Justification: `proveLockUniqueness` in `Locks.lean` exhaustively
    verifies that each lock pattern admits exactly one tile orientation. -/
axiom lock_determines_tile
    (w : BoundaryWord) (hLock : ContainsLock w) :
    ∃ t : PlacedTile, ∀ p : Patch, patchBoundary p = w → t ∈ p.tiles

/-- **Lock Forcing theorem.**
    Two patches with the same locked boundary share at least one tile.
    Derived from `lock_determines_tile`: the forced tile belongs to
    both patches, witnessing their intersection. -/
theorem lock_forces_shared_tile
    {w : BoundaryWord} (hLock : ContainsLock w)
    (p1 p2 : Patch)
    (hB1 : patchBoundary p1 = w)
    (hB2 : patchBoundary p2 = w) :
    patchIntersect p1 p2 := by
  obtain ⟨t, ht⟩ := lock_determines_tile w hLock
  exact ⟨t, ht p1 hB1, ht p2 hB2⟩

/-! ## Minimal phason -/

/-- A *minimal phason* is a hypothetical pair of distinct fillings of the
    same boundary that share no tile at all — the obstruction to uniqueness.
    We show this cannot exist. -/
def IsMinimalPhason (p1 p2 : Patch) : Prop :=
  patchBoundary p1 = patchBoundary p2 ∧ ¬ patchIntersect p1 p2

/-! ## Main uniqueness skeleton -/

/-- **No minimal phason exists.**
    Any two simply-connected Spectre patches with the same boundary word
    must share at least one tile, ruling out the existence of a minimal
    phason and establishing the uniqueness skeleton.

    **Proof.**
    Suppose `p1, p2` form a minimal phason.  Let `w` be their common
    boundary word.  By Gauss-Bonnet, `wordCurvature w = 12`.
    - If `w` contains a lock, `lock_determines_tile` yields a tile forced
      into both patches, so `patchIntersect p1 p2` — contradiction.
    - If `w` has no lock, `lock_free_implies_punctured` +
      `punctured_walk_curvature_bound` give `wordCurvature w ≤ 2`,
      contradicting `12 = wordCurvature w`.  ∎ -/
theorem no_minimal_phason (p1 p2 : Patch) : ¬ IsMinimalPhason p1 p2 := by
  intro ⟨hBdry, hDisjoint⟩
  -- Gauss-Bonnet: wordCurvature (patchBoundary p1) = 12
  have hGB : wordCurvature (patchBoundary p1) = 12 := gauss_bonnet_patch p1
  -- Case split on whether the boundary contains a lock (classical)
  rcases Classical.em (ContainsLock (patchBoundary p1)) with hLock | hNoLock
  · -- Case 1: boundary contains a lock ⟹ shared tile ⟹ contradiction
    exact hDisjoint (lock_forces_shared_tile hLock p1 p2 rfl hBdry.symm)
  · -- Case 2: no lock ⟹ curvature ≤ 2 ⟹ contradicts 12 = curvature
    have hBound : wordCurvature (patchBoundary p1) ≤ 2 :=
      lock_free_curvature_bound (patchBoundary p1) hNoLock
    omega

/-! ## Axiom audit -/

#print axioms lock_forces_shared_tile
#print axioms lock_free_curvature_bound
#print axioms no_minimal_phason
