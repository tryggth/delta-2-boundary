/-
Copyright (c) 2026 Tryggth. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Tryggth
-/
import SpectreDeltaBoundary.Bedrock
import SpectreDeltaBoundary.Paths
import SpectreDeltaBoundary.Monotile

/-!
# Local Lock Verification Engine

Provides computable predicates to exhaustively prove that a given boundary turn
sequence physically forces a unique tile orientation via local geometric exclusion.
-/

set_option linter.style.longLine false
set_option linter.style.emptyLine false


/-- Helper to extract segment pairs from a list of vertices. -/
def verticesToSegments (verts : List LatticePoint) : List (LatticePoint × LatticePoint) :=
  match verts with
  | [] => []
  | [_] => []
  | v1 :: v2 :: vs => (v1, v2) :: verticesToSegments (v2 :: vs)

/-- Checks if any segment of a proposed tile intersects/crosses any segment of the boundary path. -/
def tileEdgesCrossPath (tile : PlacedTile) (path : List LatticePoint) : Bool :=
  let tileSegs := verticesToSegments (tileVertices tile)
  let pathSegs := verticesToSegments path
  tileSegs.any (fun (a, b) =>
    pathSegs.any (fun (c, d) =>
      discreteSegmentsIntersectOrTouch a b c d
    )
  )

/-- Tests a specific tile orientation against a localized boundary path.
    Returns true if the tile fits the path layout cleanly without collision or crossing. -/
def testOrientationValid (path : List LatticePoint) (orientation : Nat) : Bool :=
  -- Align a candidate tile rooted at the path's origin
  match path with
  | [] => false
  | origin :: _ =>
    let candidate := PlacedTile.mk origin orientation
    !tileEdgesCrossPath candidate path

/-- Exhaustively evaluates all 12 rotational headings (0 to 11) for a tile placement.
    Returns true if and only if exactly one unique orientation passes the geometric filter. -/
def proveLockUniqueness (path : List LatticePoint) (forcedOri : Nat) : Bool :=
  let orientations := List.range 12
  let validMask := orientations.map (fun ori => testOrientationValid path ori)
  -- Count how many orientations successfully fit the spatial pocket
  let validCount := (validMask.filter (fun b => b == true)).length
  -- Verify uniqueness and that it matches our expected certificate orientation
  validCount == 1 && testOrientationValid path forcedOri

#print axioms proveLockUniqueness

/-- Maps a lattice vector back to its discrete direction identifier (0 to 11). -/
def vec_to_dir (step_vec : LatticePoint) : Nat :=
  let rec find (d : Nat) : Nat :=
    match d with
    | 0 => 0
    | d' + 1 =>
      if dir_to_vec d' == step_vec then d'
      else find d'
  find 12

/-- Computes the local turn steps between consecutive vertices in a path. -/
def extractPathTurns (path : List LatticePoint) : List Int :=
  -- Extracts the relative direction changes to map back to our turn grammar
  match path with
  | [] => []
  | [_] => []
  | [_, _] => []
  | v1 :: v2 :: v3 :: vs =>
    let d1 : Int := vec_to_dir (v2.sub v1)
    let d2 : Int := vec_to_dir (v3.sub v2)
    let diff := ((d2 - d1) % 12 + 12) % 12
    let turn := if diff > 6 then diff - 12 else diff
    turn :: extractPathTurns (v2 :: v3 :: vs)

/-- Checks if a placed tile's precomputed edges contain all directed segments in `reqEdges`. -/
def tileEdgesCoverSegments (tEdges : List DirectedEdge) :
    List (LatticePoint × LatticePoint) → Bool
  | [] => true
  | (e1, e2) :: rest =>
    if tEdges.any (fun te => te.v1 == e1 && te.v2 == e2) then
      tileEdgesCoverSegments tEdges rest
    else
      false

/-- Checks if a placed tile contains all directed segments in `reqEdges` along its perimeter. -/
def tileCoversSegments (tile : PlacedTile) (reqEdges : List (LatticePoint × LatticePoint)) : Bool :=
  tileEdgesCoverSegments (tileEdges tile) reqEdges

/-- Exhaustively evaluates all 14 possible edge alignments (`tile_edge_idx` 0..13) of a Spectre
    monotile against the starting directed edge `(v0, v1)` and filters for tiles covering `reqEdges`. -/
def matchingAlignedTiles (v0 v1 : LatticePoint)
    (reqEdges : List (LatticePoint × LatticePoint)) : List PlacedTile :=
  let d0 := vec_to_dir (v1.sub v0)
  let rec loop (idx : Nat) (acc : List PlacedTile) : List PlacedTile :=
    match idx with
    | 0 => acc
    | i + 1 =>
      let cand := alignToPathEdge v0 v1 d0 i
      if tileCoversSegments cand reqEdges then
        loop i (cand :: acc)
      else
        loop i acc
  loop 14 []

/-- Specification for the 3 Anchor Locks used in the priority algorithm (`L2 > L1 > L4`):
    - `300049` (Priority 1 — Lock #2, High Lock `[60°, 90°, 60°]`): CCW turns `[2, 3, 2]`, 4 tile edges covered.
    - `300033` (Priority 2 — Lock #1, Low Lock `[60°, 0°, -60°]`): CCW turns `[2, 0, -2]`, 3 tile edges covered.
    - `400110` (Priority 3 — Lock #4, Long Lock `[90°, -60°, 90°, 60°]`): CCW turns `[3, -2, 3, 2]`, 5 tile edges covered.
    Any other lock ID is rejected (`none`). -/
def getAnchorLockSpec (lockId : Nat) : Option (List Int × Nat) :=
  match lockId with
  | 300049 => some ([2, 3, 2], 4)
  | 300033 => some ([2, 0, -2], 3)
  | 400110 => some ([3, -2, 3, 2], 5)
  | _      => none

/-- Computes the signed 30°-step turn (-3, -2, 0, 2, 3) between two consecutive edge directions. -/
def turnBetweenDirs (d1 d2 : Nat) : Int :=
  let diff := (((d2 : Int) - (d1 : Int)) % 12 + 12) % 12
  if diff > 6 then diff - 12 else diff

/-- Given one of the 3 anchor lock IDs (`300049`, `300033`, `400110`) and a boundary vertex
    subpath starting at the lock, verifies that:
    1. The subpath starts with the exact required turn sequence for `lockId`.
    2. Exhaustive alignment across all 14 tile edges (`0..13`) yields **uniquely one** (`length == 1`)
       valid `PlacedTile` covering the required boundary edges.
    Returns `some uniqueTile` if and only if both conditions hold. -/
def findUniqueForcedTileAtSubpath (lockId : Nat) (subpath : List LatticePoint) : Option PlacedTile :=
  match getAnchorLockSpec lockId with
  | none => none
  | some (expectedTurns, numTileEdges) =>
    let totalEdges := expectedTurns.length + 1
    let prefixVerts := subpath.take (totalEdges + 1)
    if prefixVerts.length == totalEdges + 1 && extractPathTurns prefixVerts == expectedTurns then
      match prefixVerts with
      | v0 :: v1 :: _ =>
        let reqEdges := verticesToSegments (subpath.take (numTileEdges + 1))
        match matchingAlignedTiles v0 v1 reqEdges with
        | [uniqueTile] => some uniqueTile
        | _ => none
      | _ => none
    else
      none

/-- Computable predicate verifying that `subpath` triggers anchor lock `lockId` and
    uniquely forces `expectedTile` (both origin and orientation) across all 14 edge alignments. -/
def proveAnchorLockUniqueness (lockId : Nat) (subpath : List LatticePoint)
    (expectedTile : PlacedTile) : Bool :=
  findUniqueForcedTileAtSubpath lockId subpath == some expectedTile

#print axioms proveAnchorLockUniqueness

/-- Canonical reference subpath for Priority 1 Lock #2 (`300049`, `[60°, 90°, 60°]`, edges 4..7 of ref tile 0). -/
def canonicalSubpathLock2 : List LatticePoint :=
  ((tileVertices (PlacedTile.mk LatticePoint.zero 0)).drop 4).take 5

/-- Canonical reference subpath for Priority 2 Lock #1 (`300033`, `[60°, 0°, -60°]`, edges 8..10 of ref tile 0
    followed by an adjacent boundary edge turning `-60°` in direction 4). -/
def canonicalSubpathLock1 : List LatticePoint :=
  let v8_to_11 := ((tileVertices (PlacedTile.mk LatticePoint.zero 0)).drop 8).take 4
  let v11 := v8_to_11.getLastD LatticePoint.zero
  v8_to_11 ++ [v11.add (dir_to_vec 4)]

/-- Canonical reference subpath for Priority 3 Lock #4 (`400110`, `[90°, -60°, 90°, 60°]`, edges 13, 0..3 of ref tile 0). -/
def canonicalSubpathLock4 : List LatticePoint :=
  let v := tileVertices (PlacedTile.mk LatticePoint.zero 0)
  (v.drop 13).take 1 ++ v.take 5

/-- Verified uniqueness theorem for Anchor Lock #2 (`300049`, `[2, 3, 2]`):
    exhaustively testing all 14 tile edge alignments forces uniquely `PlacedTile.mk 0 0`. -/
theorem anchor_lock_2_unique :
    proveAnchorLockUniqueness 300049 canonicalSubpathLock2 (PlacedTile.mk LatticePoint.zero 0) = true := by
  decide

/-- Verified uniqueness theorem for Anchor Lock #1 (`300033`, `[2, 0, -2]`):
    exhaustively testing all 14 tile edge alignments forces uniquely `PlacedTile.mk 0 0`. -/
theorem anchor_lock_1_unique :
    proveAnchorLockUniqueness 300033 canonicalSubpathLock1 (PlacedTile.mk LatticePoint.zero 0) = true := by
  decide

/-- Verified uniqueness theorem for Anchor Lock #4 (`400110`, `[3, -2, 3, 2]`):
    exhaustively testing all 14 tile edge alignments forces uniquely `PlacedTile.mk 0 0`. -/
theorem anchor_lock_4_unique :
    proveAnchorLockUniqueness 400110 canonicalSubpathLock4 (PlacedTile.mk LatticePoint.zero 0) = true := by
  decide

#print axioms anchor_lock_2_unique
#print axioms anchor_lock_1_unique
#print axioms anchor_lock_4_unique

