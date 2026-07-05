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

/-- Computes whether any vertex of a PlacedTile collides with an explicit list of path vertices. -/
def tileCollidesWithPath (tile : PlacedTile) (path : List LatticePoint) : Bool :=
  let tileVerts := tileVertices tile
  tileVerts.any (fun tv => path.contains tv)

/-- Tests a specific tile orientation against a localized boundary path.
    Returns true if the tile fits the path layout cleanly without collision. -/
def testOrientationValid (path : List LatticePoint) (orientation : Nat) : Bool :=
  -- Align a candidate tile rooted at the path's origin
  match path with
  | [] => false
  | origin :: _ =>
    let candidate := PlacedTile.mk origin orientation
    -- In future phases, this will check explicit segment crossings via `segmentsIntersect`.
    -- For this structural milestone, we evaluate direct vertex boundary exclusion.
    !tileCollidesWithPath candidate path

/-- Exhaustively evaluates all 12 rotational headings (0 to 11) for a tile placement.
    Returns true if and only if exactly one unique orientation passes the geometric filter. -/
def proveLockUniqueness (path : List LatticePoint) (forcedOri : Nat) : Bool :=
  let orientations := List.range 12
  let validMask := orientations.map (fun ori => testOrientationValid path ori)
  -- Count how many orientations successfully fit the spatial pocket
  let validCount := (validMask.filter (fun b => b == true)).length
  -- Verify uniqueness and that it matches our expected certificate orientation
  validCount == 1 && testOrientationValid path forcedOri

#print axioms tileCollidesWithPath
#print axioms proveLockUniqueness
