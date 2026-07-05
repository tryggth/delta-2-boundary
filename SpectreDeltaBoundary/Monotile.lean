import SpectreDeltaBoundary.Bedrock
import SpectreDeltaBoundary.Paths

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
