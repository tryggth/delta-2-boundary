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
# Local Lock Frustration Matrix Diagnostics

Loops through all 11 incorrect orientations for each of the 5 core lock paths
and evaluates whether they are successfully blocked by vertex collisions or edge crossings.
-/

/-- Runs the diagnostic loop for a single lock path. -/
def diagnoseLock (lockId : Nat) (path : List LatticePoint) (validOri : Nat) : String :=
  let orientations := List.range 12
  let rec loop (oris : List Nat) (acc : String) : String :=
    match oris with
    | [] => acc
    | o :: os =>
      if o == validOri then
        loop os acc
      else
        match path with
        | [] => loop os acc
        | origin :: _ =>
          let candidate := PlacedTile.mk origin o
          let vCol := tileCollidesWithPath candidate path
          let eCross := tileEdgesCrossPath candidate path
          let vStr := if vCol then "TRUE " else "FALSE"
          let eStr := if eCross then "TRUE " else "FALSE"
          let line := s!"Lock ID: {lockId} | Orientation: {o} | " ++
            s!"Vertex Collision: {vStr} | Edge Crossing: {eStr}\n"
          loop os (acc ++ line)
  loop orientations ""

/-- Aggregates the diagnostic ledger for all 5 unique lock paths. -/
def diagnoseAllLocks : String :=
  let p_300033 := tracePathVertices [.z0, .p60, .z0]
  let p_300049 := tracePathVertices [.p60, .p90, .p60]
  let p_400074 := tracePathVertices [.z0, .m60, .p90, .p60]
  let p_400110 := tracePathVertices [.p60, .p90, .m60, .p90]
  let p_400129 := tracePathVertices [.p90, .m60, .p90, .p60]
  
  diagnoseLock 300033 p_300033 0 ++
  diagnoseLock 300049 p_300049 2 ++
  diagnoseLock 400074 p_400074 3 ++
  diagnoseLock 400110 p_400110 0 ++
  diagnoseLock 400129 p_400129 8

#eval IO.print diagnoseAllLocks
