/-
Copyright (c) 2026 tryggth. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: tryggth
-/
import SpectreDeltaBoundary.Paths
import SpectreDeltaBoundary.Monotile

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
-/

set_option linter.style.header false

open AllowedStep

/-! ## Core types -/

/-- A `Patch` represents a finite, simply-connected set of placed Spectre
    tiles on the cyclotomic lattice.  The internal structure is left opaque;
    only its boundary-word and intersection API are used in the uniqueness
    argument. -/
opaque Patch : Type

/-- The boundary word of a patch is a sequence of allowed turning steps
    tracing its perimeter counter-clockwise. -/
abbrev BoundaryWord := List AllowedStep

/-- Returns the boundary word of a simply-connected patch. -/
opaque patchBoundary : Patch → BoundaryWord

/-- Predicate: two patches *intersect* iff they share at least one
    identical `PlacedTile` (same origin and orientation). -/
opaque patchIntersect : Patch → Patch → Prop

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

/-! ## Transfer-matrix curvature bound (No-Go theorem) -/

/-- **No-Go theorem.**
    The transfer-matrix exhaustive DFS (`verify_batch1`–`verify_batch4` in
    `TransferMatrixBatches.lean`) proves that every valid cycle through
    punctured (= lock-free) states has curvature at most 60° = 2 step-units.
    We axiomatise this global result as a curvature bound on lock-free
    boundary words. -/
axiom lock_free_curvature_bound
    (w : BoundaryWord) (h : ¬ ContainsLock w) : wordCurvature w ≤ 2

/-! ## Lock forcing -/

/-- **Lock Forcing axiom.**
    If a boundary word contains a geometric lock, the local geometry is so
    constrained that any valid filling of that boundary *must* place a
    specific tile at the lock site.  Therefore, any two patches sharing
    that boundary must share at least one placed tile. -/
axiom lock_forces_shared_tile
    {w : BoundaryWord} (hLock : ContainsLock w)
    (p1 p2 : Patch)
    (hB1 : patchBoundary p1 = w)
    (hB2 : patchBoundary p2 = w) :
    patchIntersect p1 p2

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
    - If `w` contains no lock, the transfer-matrix bound gives
      `wordCurvature w ≤ 2`, contradicting `12 ≤ 2`.
    - If `w` contains a lock, lock forcing gives `patchIntersect p1 p2`,
      contradicting the phason assumption `¬ patchIntersect p1 p2`.  ∎ -/
theorem no_minimal_phason (p1 p2 : Patch) : ¬ IsMinimalPhason p1 p2 := by
  intro ⟨hBdry, hDisjoint⟩
  -- Gauss-Bonnet: wordCurvature (patchBoundary p1) = 12
  have hGB : wordCurvature (patchBoundary p1) = 12 := gauss_bonnet_patch p1
  -- Case split on whether the boundary contains a lock (classical)
  rcases Classical.em (ContainsLock (patchBoundary p1)) with hLock | hNoLock
  · -- Case 1: boundary contains a lock ⟹ shared tile ⟹ contradiction
    exact hDisjoint (lock_forces_shared_tile hLock p1 p2 rfl (hBdry ▸ rfl))
  · -- Case 2: no lock ⟹ curvature ≤ 2 ⟹ contradicts 12 = curvature
    have hBound : wordCurvature (patchBoundary p1) ≤ 2 :=
      lock_free_curvature_bound (patchBoundary p1) hNoLock
    omega

#print axioms no_minimal_phason
