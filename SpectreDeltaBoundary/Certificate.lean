/-
Copyright (c) 2026 Tryggth. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: Tryggth
-/
import SpectreDeltaBoundary.Bedrock
import SpectreDeltaBoundary.Paths
import SpectreDeltaBoundary.Monotile

/-!
# Peeling Certificate Validation

This module defines the peeling certificate structures and the state transition validation logic.
-/

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

/-- Determines if a directed edge (e1, e2) matches the reversed edge of a PlacedTile. -/
def isSharedEdge (e1 e2 : LatticePoint) (tile : PlacedTile) : Bool :=
  (tileEdges tile).any (fun edge => edge.v1 == e2 && edge.v2 == e1)

/-- Checks if a directed edge (e1, e2) from a tile is completely unshared with the current boundary.
    These represent the newly exposed interior boundary segments. -/
def isNewInteriorEdge (e1 e2 : LatticePoint)
    (currentEdges : List (LatticePoint × LatticePoint)) : Bool :=
  !currentEdges.any (fun (b1, b2) => b1 == e2 && b2 == e1)

/-- Executes and validates a single active peeling transition step.
    Computes the exact ledger of remaining boundary edges and newly exposed interior tile edges,
    then verifies it matches the edge set of the proposed next state.
    Returns the nextState if valid, or an empty state (failure) if the ledger misaligns. -/
def executePeelingStep (state : PeelingState) (step : PeelingStep) : PeelingState :=
  let currentEdges := stateToAllEdges state
    
  -- 1. Retain boundary edges that are NOT shared with (annihilated by) the peeled tile
  let remainingBoundary := currentEdges.filter (fun (v1, v2) => !isSharedEdge v1 v2 step.tile)
    
  -- 2. Extract the tile's perimeter edges as raw pairs
  let tilePairs := (tileEdges step.tile).map (fun edge => (edge.v1, edge.v2))
    
  -- 3. Retain tile edges that are NOT shared with the current boundary (newly exposed interior)
  let newInterior := tilePairs.filter (fun (t1, t2) => isNewInteriorEdge t1 t2 currentEdges)
    
  -- 4. Compute total expected edges for the next boundary configuration
  let calculatedEdges := remainingBoundary ++ newInterior
    
  -- 5. Extract the edge ledger of the certificate's proposed next state
  let expectedEdges := stateToAllEdges step.nextState
    
  -- 6. Validate structural equivalence via list inclusion checks (order-invariant)
  let validForward := calculatedEdges.all (fun e => expectedEdges.contains e)
  let validBackward := expectedEdges.all (fun e => calculatedEdges.contains e)
  let correctCount := calculatedEdges.length == expectedEdges.length
    
  if validForward && validBackward && correctCount then step.nextState else []

#print axioms executePeelingStep

/-- Recursively executes an entire chain of peeling steps starting from an initial PeelingState.
    If any intermediate step fails validation (evaluates to an empty list of boundaries),
    the execution instantly short-circuits and returns an empty state (failure). -/
def executeCertificate (initialState : PeelingState)
    (cert : PeelingCertificate) : PeelingState :=
  let rec loop (state : PeelingState) (steps : List PeelingStep) : PeelingState :=
    match steps with
    | [] => state
    | s :: ss =>
      let next := executePeelingStep state s
      match next with
      | [] => [] -- Structural failure shortcut
      | validState => loop validState ss
  loop initialState cert.steps

#print axioms executeCertificate

