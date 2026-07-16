/-
Copyright (c) 2026 tryggth. All rights reserved.
Released under Apache 2.0 license as described in the file LICENSE.
Authors: tryggth
-/
import SpectreDeltaBoundary.Bedrock
import SpectreDeltaBoundary.Paths

/-!
# Geometry Monotile definitions
-/

set_option linter.style.header false

/-- The rigid, immutable 14-turn cyclic path sequence
    that defines the Spectre monotile.
    Maps perfectly to SPECTRE_TURNS =
    [90, -60, 90, 60, 0, 60, -90, 60,
     90, 60, -90, 60, 90, -60] -/
def spectreTurns : List AllowedStep :=
  [.p90, .m60, .p90, .p60, .z0, .p60, .m90, .p60,
   .p90, .p60, .m90, .p60, .p90, .m60]

/-- Represents a single Spectre monotile rigidly
    positioned on the Diophantine grid. -/
structure PlacedTile where
  origin : LatticePoint
  orientation : Nat
deriving DecidableEq, Repr

/-- Generates the sequence of 14 absolute direction
    values utilized during tile edge tracing. Perfectly
    matches the direction tracking logic inside
    Python's _build_geometry loop. -/
def tileDirections (orientation : Nat) : List Nat :=
  let rec loop
      (turns : List AllowedStep) (curr_dir : Int)
      (acc : List Nat) : List Nat :=
    match turns with
    | [] => acc.reverse
    | t :: ts =>
      let steps := t.toStep
      let next_dir := curr_dir + steps
      let curr_nat := ((curr_dir % 12 + 12) % 12).toNat
      loop ts next_dir (curr_nat :: acc)
  loop spectreTurns (orientation : Int) []

/-- Generates the complete ordered list of 15
    LatticePoint vertices for a placed tile. Starts at
    the origin and trace-steps along the perimeter
    using the basis vectors. -/
def tileVertices (tile : PlacedTile) :
    List LatticePoint :=
  let rec loop
      (dirs : List Nat) (curr_pos : LatticePoint)
      (acc : List LatticePoint) : List LatticePoint :=
    match dirs with
    | [] => acc.reverse
    | d :: ds =>
      let next_pos := curr_pos.add (dir_to_vec d)
      loop ds next_pos (next_pos :: acc)
  loop (tileDirections tile.orientation)
    tile.origin [tile.origin]

#print axioms spectreTurns
#print axioms tileVertices

/-- Represents a directed edge on the lattice grid
    connecting two vertices with a heading direction. -/
structure DirectedEdge where
  v1 : LatticePoint
  v2 : LatticePoint
  dir : Nat
deriving DecidableEq, Repr

/-- Extracts the 14 directed edges forming the
    perimeter of a PlacedTile. Perfectly mirrors
    the self.edges accumulation loop from the
    Python engine. -/
def tileEdges (tile : PlacedTile) :
    List DirectedEdge :=
  let rec loop
      (verts : List LatticePoint)
      (dirs : List Nat) (acc : List DirectedEdge)
      : List DirectedEdge :=
    match verts, dirs with
    | v1 :: v2 :: vs, d :: ds =>
      loop (v2 :: vs) ds (⟨v1, v2, d⟩ :: acc)
    | _, _ => acc.reverse
  loop (tileVertices tile)
    (tileDirections tile.orientation) []

/-- Positionally aligns a tile such that its specified
    edge index rests flush against a target path edge.
    Verbatim translation of Python's
    PlacedTile.align_to_path_edge arithmetic loop. -/
def alignToPathEdge
    (p_v1 _p_v2 : LatticePoint) (p_dir : Nat)
    (tile_edge_idx : Nat) : PlacedTile :=
  let ref_tile_0 := PlacedTile.mk LatticePoint.zero 0
  let ref_edges_0 := tileEdges ref_tile_0
  let dummy_edge :=
    DirectedEdge.mk LatticePoint.zero
      LatticePoint.zero 0
  let ref_edge :=
    ref_edges_0.getD tile_edge_idx dummy_edge
  let ref_dir := ref_edge.dir
  let orientation := (p_dir + 12 - ref_dir) % 12
  let oriented_ref :=
    PlacedTile.mk LatticePoint.zero orientation
  let ref_edges_ori := tileEdges oriented_ref
  let ref_edge_ori :=
    ref_edges_ori.getD tile_edge_idx dummy_edge
  let ref_v1 := ref_edge_ori.v1
  let origin := p_v1.sub ref_v1
  PlacedTile.mk origin orientation

#print axioms tileEdges
#print axioms alignToPathEdge
