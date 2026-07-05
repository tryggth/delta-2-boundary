import SpectreDeltaBoundary.Bedrock

/-- The restricted set of allowed turning steps for Spectre boundaries.
    Represents angles: -90°, -60°, 0°, 60°, 90°. -/
inductive AllowedStep where
  | m90 -- -90 degrees (-3 step units)
  | m60 -- -60 degrees (-2 step units)
  | z0  --   0 degrees (0 step units)
  | p60 --  60 degrees (2 step units)
  | p90 --  90 degrees (3 step units)
deriving DecidableEq, Repr

/-- Maps an AllowedStep token to its corresponding integer step value. -/
def AllowedStep.toStep (s : AllowedStep) : Int :=
  match s with
  | .m90 => -3
  | .m60 => -2
  | .z0  => 0
  | .p60 => 2
  | .p90 => 3

/-- Traces a relative sequence of allowed boundary turning steps
    and accumulates a list of absolute LatticePoint vertices.
    Perfectly mirrors the initialization and loop logic of
    Python's trace_absolute_path_vertices engine. -/
def tracePathVertices
    (steps : List AllowedStep) : List LatticePoint :=
  let rec loop
      (st : List Int) (curr_pos : LatticePoint)
      (curr_dir : Int) (acc : List LatticePoint)
      : List LatticePoint :=
    match st with
    | [] => acc.reverse
    | s :: ss =>
      let next_dir := curr_dir + s
      let dir_nat := ((next_dir % 12 + 12) % 12).toNat
      let next_pos := curr_pos.add (dir_to_vec dir_nat)
      loop ss next_pos next_dir (next_pos :: acc)
  loop
    (0 :: steps.map AllowedStep.toStep)
    LatticePoint.zero 0 [LatticePoint.zero]

/-- A simple baseline evaluation definition to anchor
    the module audit. -/
def paths_baseline_marker : Nat := 0

#print axioms AllowedStep.toStep
#print axioms tracePathVertices
