/-
Copyright (c) 2026 Tryggth. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Tryggth
-/
import SpectreDeltaBoundary.Bedrock
import SpectreDeltaBoundary.Paths
import SpectreDeltaBoundary.Monotile
import SpectreDeltaBoundary.Locks

/-!
# Peeling Certificate Validation

This module defines the peeling certificate structures and the state transition validation logic.
-/

set_option linter.style.longLine false
set_option linter.style.emptyLine false

/-- Tracks the remaining active open boundaries during the peeling sequence.
    Represented as a list of vertex sequences to naturally accommodate cases
    where removing a tile pinches or splits a patch into multiple components. -/
abbrev PeelingState := List (List LatticePoint)

/-- Represents a single atomic step in our verified peeling certificate.
    Explicitly bundles the expected next state to turn edge subtraction
    into a pure validation check rather than a search problem. -/
structure PeelingStep where
  lockId : Nat            -- Matches the specific verified short-path lock lemma
  tile : PlacedTile       -- The unique tile location and orientation forced by the lock
  nextState : PeelingState -- The pre-calculated expected remaining boundaries
deriving DecidableEq, Repr

/-- The certificate object containing the complete ordered sequence of tile removals. -/
structure PeelingCertificate where
  steps : List PeelingStep
deriving DecidableEq, Repr

/-- Converts a closed loop of vertices into a list of directed coordinate pairs (edges). -/
def loopToEdges (loop : List LatticePoint) : List (LatticePoint × LatticePoint) :=
  let rec worker (verts : List LatticePoint) (first : LatticePoint)
      (acc : List (LatticePoint × LatticePoint)) : List (LatticePoint × LatticePoint) :=
    match verts with
    | [] => acc.reverse
    | [v] => ((v, first) :: acc).reverse
    | v1 :: v2 :: vs => worker (v2 :: vs) first ((v1, v2) :: acc)
  match loop with
  | [] => []
  | v :: vs => worker (v :: vs) v []

/-- Flattens a multi-component PeelingState into a single unified list of directed edges. -/
def stateToAllEdges (state : PeelingState) : List (LatticePoint × LatticePoint) :=
  state.flatMap loopToEdges

/-- Converts a closed loop of vertices into a list of `DirectedEdge`s with precomputed directions
    in a single linear pass. -/
def loopToDirectedEdges (loop : List LatticePoint) : List DirectedEdge :=
  let rec worker (verts : List LatticePoint) (first : LatticePoint)
      (acc : List DirectedEdge) : List DirectedEdge :=
    match verts with
    | [] => acc.reverse
    | [v] => (⟨v, first, vec_to_dir (first.sub v)⟩ :: acc).reverse
    | v1 :: v2 :: vs =>
      worker (v2 :: vs) first (⟨v1, v2, vec_to_dir (v2.sub v1)⟩ :: acc)
  match loop with
  | [] => []
  | v :: vs => worker (v :: vs) v []

/-- Computes the turn at the end of each edge in a sequence of `DirectedEdge`s in a single pass. -/
def directedEdgesWithTurns : List DirectedEdge → List (DirectedEdge × Int)
  | e1 :: e2 :: rest =>
    (e1, turnBetweenDirs e1.dir e2.dir) :: directedEdgesWithTurns (e2 :: rest)
  | _ => []

/-- Extracts the raw `(v1, v2)` coordinate pairs from the first `k` items of an edge-turn list. -/
def takeEdgePairs : Nat → List (DirectedEdge × Int) → List (LatticePoint × LatticePoint)
  | 0, _ => []
  | _ + 1, [] => []
  | k + 1, (e, _) :: rest => (e.v1, e.v2) :: takeEdgePairs k rest

/-- Checks if the prefix of an edge-turn list matches the expected turn sequence `expectedTurns`. -/
def matchesTurnPrefix : List Int → List (DirectedEdge × Int) → Bool
  | [], _ => true
  | _ :: _, [] => false
  | t :: ts, (_, actualTurn) :: rest =>
    if t == actualTurn then matchesTurnPrefix ts rest else false

/-- Scans a precomputed `(DirectedEdge × Int)` list from left to right for the first occurrence of
    `expectedTurns`, and verifies via `matchingAlignedTiles` across all 14 tile edge alignments that
    it forces a unique `PlacedTile` covering `numTileEdges` consecutive boundary edges. -/
def scanEdgeTurnsForUniqueLock (expectedTurns : List Int) (numTileEdges : Nat) :
    List (DirectedEdge × Int) → Option PlacedTile
  | [] => none
  | (e0, t0) :: rest =>
    let stream := (e0, t0) :: rest
    if matchesTurnPrefix expectedTurns stream then
      let reqEdges := takeEdgePairs numTileEdges stream
      match matchingAlignedTiles e0.v1 e0.v2 reqEdges with
      | [uniqueTile] => some uniqueTile
      | _ => none
    else
      scanEdgeTurnsForUniqueLock expectedTurns numTileEdges rest

/-- Searches a single precomputed `(DirectedEdge × Int)` loop for one of the 3 anchor locks. -/
def findLockInEdgeTurns (lockId : Nat)
    (edgeTurns : List (DirectedEdge × Int)) : Option PlacedTile :=
  match getAnchorLockSpec lockId with
  | none => none
  | some (expectedTurns, numTileEdges) =>
    scanEdgeTurnsForUniqueLock expectedTurns numTileEdges edgeTurns

/-- Converts a boundary loop into its padded `(DirectedEdge × Int)` stream once, then applies
    the 3-Anchor-Lock priority rule (`L2 > L1 > L4`):
    1. If Lock #2 (`300049`, `[2, 3, 2]`) exists on the boundary, return `some (300049, tile)`
    2. Else if Lock #1 (`300033`, `[2, 0, -2]`) exists on the boundary, return `some (300033, tile)`
    3. Else if Lock #4 (`400110`, `[3, -2, 3, 2]`) exists on the boundary, return `some (400110, tile)`. -/
def selectPriorityLockOnEdgeTurns
    (edgeTurns : List (DirectedEdge × Int)) : Option (Nat × PlacedTile) :=
  match findLockInEdgeTurns 300049 edgeTurns with
  | some tile => some (300049, tile)
  | none =>
    match findLockInEdgeTurns 300033 edgeTurns with
    | some tile => some (300033, tile)
    | none =>
      match findLockInEdgeTurns 400110 edgeTurns with
      | some tile => some (400110, tile)
      | none => none

/-- Computes the padded `(DirectedEdge × Int)` stream for a boundary loop in one linear pass. -/
def loopToPaddedEdgeTurns (loop : List LatticePoint) : List (DirectedEdge × Int) :=
  if loop.length < 4 then []
  else
    let dEdges := loopToDirectedEdges loop
    directedEdgesWithTurns (dEdges ++ dEdges.take 5)

/-- Formalization of the 3-Anchor-Lock priority selection rule (`L2 > L1 > L4`) on a `PeelingState`. -/
def selectPriorityLock (state : PeelingState) : Option (Nat × PlacedTile) :=
  match state with
  | [loop] => selectPriorityLockOnEdgeTurns (loopToPaddedEdgeTurns loop)
  | _ => none

/-- Removes the first occurrence of `target` from a list of directed edges, returning `none` if
    `target` is not present. Pure structural recursion avoids zeta-duplication in the kernel. -/
def removeFirstEdge (target : LatticePoint × LatticePoint) :
    List (LatticePoint × LatticePoint) → Option (List (LatticePoint × LatticePoint))
  | [] => none
  | e :: es =>
    if e == target then some es
    else
      match removeFirstEdge target es with
      | none => none
      | some rest => some (e :: rest)

/-- Single-pass partition of `currentEdges` and `tileEdges`:
    - Any edge in `currentEdges` shared with `unsharedTileEdges` is annihilated from both.
    - Unshared boundary edges are accumulated in `remAcc`.
    - Remaining `unsharedTileEdges` at the end are reversed `(t1, t2) ↦ (t2, t1)` to form `newInterior`
      and appended to `remAcc.reverse`. -/
def computeNextBoundaryEdges
    (currentEdges : List (LatticePoint × LatticePoint))
    (unsharedTileEdges : List (LatticePoint × LatticePoint))
    (remAcc : List (LatticePoint × LatticePoint)) :
    Nat × List (LatticePoint × LatticePoint) :=
  match currentEdges with
  | [] =>
    let sharedCount := 14 - unsharedTileEdges.length
    let newInterior := unsharedTileEdges.map (fun (t1, t2) => (t2, t1))
    (sharedCount, remAcc.reverse ++ newInterior)
  | e :: es =>
    match removeFirstEdge e unsharedTileEdges with
    | some unshared' =>
      computeNextBoundaryEdges es unshared' remAcc
    | none =>
      computeNextBoundaryEdges es unsharedTileEdges (e :: remAcc)

/-- Verifies exact multiset equality between two edge lists by structural recursion. -/
def edgeMultisetEq :
    List (LatticePoint × LatticePoint) → List (LatticePoint × LatticePoint) → Bool
  | [], [] => true
  | e :: es, rhs =>
    match removeFirstEdge e rhs with
    | none => false
    | some rhs' => edgeMultisetEq es rhs'
  | _, _ => false

/-- Executes and validates a single active peeling transition step under the 3-Anchor-Lock
    priority algorithm (`L2 > L1 > L4`):
    1. Verifies that `selectPriorityLock state == some (step.lockId, step.tile)`, which guarantees
       that `step.lockId` is the highest-priority lock (`300049`, else `300033`, else `400110`)
       present on `state` and that `step.tile` is the unique `PlacedTile` forced by that lock
       across all 14 tile edge alignments.
    2. Computes the exact ledger of remaining boundary edges and newly exposed (reversed) interior
       tile edges, and verifies exact multiset equality with `step.nextState`.
    Returns `some step.nextState` if valid, or `none` if any check fails. -/
def executePeelingStep (state : PeelingState) (step : PeelingStep) : Option PeelingState :=
  if selectPriorityLock state == some (step.lockId, step.tile) then
    let tilePairs := (tileEdges step.tile).map (fun edge => (edge.v1, edge.v2))
    let (sharedCount, calculatedEdges) :=
      computeNextBoundaryEdges (stateToAllEdges state) tilePairs []
    if sharedCount > 0 && edgeMultisetEq calculatedEdges (stateToAllEdges step.nextState) then
      some step.nextState
    else
      none
  else
    none

#print axioms executePeelingStep

/-- Executes an entire chain of peeling steps starting from `initialState`.
    While the boundary is non-empty, each step must match the 3-lock priority selector
    (`L2 > L1 > L4`), uniquely force the peeled tile, and transition cleanly to the new boundary.
    If any intermediate step fails validation (`none`), execution immediately returns `none`.
    Complete, verified reduction of the interior tiling returns `some []`. -/
def executeCertificate (initialState : PeelingState)
    (cert : PeelingCertificate) : Option PeelingState :=
  let rec loop (state : PeelingState) (steps : List PeelingStep) : Option PeelingState :=
    match steps with
    | [] => some state
    | s :: ss =>
      match executePeelingStep state s with
      | none => none
      | some validState => loop validState ss
  loop initialState cert.steps

#print axioms executeCertificate
