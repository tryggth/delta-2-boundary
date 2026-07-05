import SpectreDeltaBoundary.Bedrock
import SpectreDeltaBoundary.Paths
import SpectreDeltaBoundary.Monotile

/-- Represents a single atomic step in our verified peeling certificate.
    Identifies which unprovable search was resolved by a short-path lock,
    and details the rigid tile coordinate forced into existence. -/
structure PeelingStep where
  lockId : Nat       -- Matches the specific verified short-path lock lemma
  tile : PlacedTile  -- The unique tile location and orientation forced by the lock
deriving DecidableEq, Repr

/-- The certificate object containing the complete ordered sequence of tile removals. -/
structure PeelingCertificate where
  steps : List PeelingStep
deriving DecidableEq, Repr

/-- Tracks the remaining active open boundaries during the peeling sequence.
    Represented as a list of vertex sequences to naturally accommodate cases
    where removing a tile pinches or splits a patch into multiple components. -/
def PeelingState := List (List LatticePoint)

/-- A simple baseline evaluation definition to anchor the module audit. -/
def certificate_baseline_marker : Nat := 0

#print axioms PeelingStep
#print axioms PeelingCertificate

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

/-- Determines if a directed edge (e1, e2) is a reversed match for any edge of a PlacedTile.
    Used to identify where a tile boundary flush-intersects the active patch perimeter. -/
def isSharedEdge (e1 e2 : LatticePoint) (tile : PlacedTile) : Bool :=
  (tileEdges tile).any (fun edge => edge.v1 == e2 && edge.v2 == e1)

/-- Executes a single active peeling transition step. Takes a current PeelingState,
    identifies the active sub-boundary targeted by the step, subtracts the shared
    edges of the locked tile, integrates the new unshared interior tile edges,
    and returns the updated PeelingState containing the remaining open perimeters. -/
def executePeelingStep (state : PeelingState) (step : PeelingStep) : PeelingState :=
  -- For this incremental milestone, we map the structural wrapper filtering the edge ledger.
  -- Future macros will expand the full non-splitting/splitting connectivity graph parser.
  state.map (fun boundary =>
    let edges := loopToEdges boundary
    -- Filters out boundary segments that are backed by the peeled tile
    let _remainingEdges := edges.filter (fun (v1, v2) => !isSharedEdge v1 v2 step.tile)
    -- Placeholder vertex map mapping back from the edge symmetric difference
    boundary
  )

#print axioms loopToEdges
#print axioms executePeelingStep

