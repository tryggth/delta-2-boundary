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

/-- Evaluates whether a quadratic integer u + v*sqrt(3)
    is non-negative. Perfectly maps the exact conditional
    sign checks from the Python Z3 engine. -/
def Z3.isNonNeg (z : Z3) : Bool :=
  if z.u >= 0 && z.v >= 0 then true
  else if z.u <= 0 && z.v <= 0 then false
  else if z.u < 0 && z.v > 0 then 3 * z.v * z.v >= z.u * z.u
  else z.u * z.u >= 3 * z.v * z.v

/-- Computes the exact discrete sign (-1, 0, or 1)
    of a Z3 element. -/
def Z3.sign (z : Z3) : Int :=
  if z.u == 0 && z.v == 0 then 0
  else if z.isNonNeg then 1
  else -1

/-- Computes the exact 2D cross product determinant of
    three points. Returns positive if p3 is left of
    p1→p2, negative if right, and 0 if collinear.
    Identical to Phase 2 of the paths.py cross_product
    framework. -/
def crossProduct2D (p1 p2 p3 : Point2D) : Z3 :=
  let dx1 := Z3.sub p2.x p1.x
  let dy1 := Z3.sub p3.y p1.y
  let dy2 := Z3.sub p2.y p1.y
  let dx2 := Z3.sub p3.x p1.x
  Z3.sub (Z3.mul dx1 dy1) (Z3.mul dy2 dx2)

#print axioms Z3.isNonNeg
#print axioms crossProduct2D
