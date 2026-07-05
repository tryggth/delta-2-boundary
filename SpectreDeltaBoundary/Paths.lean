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

/-- A quadratic integer structure r + s*sqrt(3) used for discrete continuous segment crossings. -/
structure QuadInt where
  r : Int
  s : Int
deriving DecidableEq, Repr

/-- Computes the sign (-1, 0, or 1) of a QuadInt value using exact integer arithmetic. -/
def quadSign (x : QuadInt) : Int :=
  if x.r == 0 && x.s == 0 then 0
  else if x.r >= 0 && x.s >= 0 then 1
  else if x.r <= 0 && x.s <= 0 then -1
  else
    let r2 := x.r * x.r
    let s2 := 3 * x.s * x.s
    if x.r > 0 then
      if r2 > s2 then 1 else -1
    else
      if r2 > s2 then -1 else 1

/-- Computes the scaled cross product of vectors (p2 - p1) and (p3 - p1)
    on the cyclotomic lattice. -/
def discreteCrossProduct (p1 p2 p3 : LatticePoint) : QuadInt :=
  let cp := crossProduct2D p1.toPoint2D p2.toPoint2D p3.toPoint2D
  ⟨cp.u, cp.v⟩

#print axioms discreteCrossProduct


/-- Ordering comparison for Z3 elements. -/
def Z3.le (z1 z2 : Z3) : Bool :=
  Z3.isNonNeg (Z3.sub z2 z1)

/-- Bounding box check for collinear points on the cyclotomic lattice. -/
def onSegment (p1 p2 p3 : LatticePoint) : Bool :=
  let cp := discreteCrossProduct p1 p2 p3
  if quadSign cp != 0 then false
  else
    let a := p1.toPoint2D
    let b := p2.toPoint2D
    let c := p3.toPoint2D
    ((Z3.le a.x c.x && Z3.le c.x b.x) || (Z3.le b.x c.x && Z3.le c.x a.x)) &&
    ((Z3.le a.y c.y && Z3.le c.y b.y) || (Z3.le b.y c.y && Z3.le c.y a.y))

/-- Computes if segment AB intersects or touches segment CD on the Diophantine grid. -/
def discreteSegmentsIntersectOrTouch (a b c d : LatticePoint) : Bool :=
  let s1 := quadSign (discreteCrossProduct a b c)
  let s2 := quadSign (discreteCrossProduct a b d)
  let s3 := quadSign (discreteCrossProduct c d a)
  let s4 := quadSign (discreteCrossProduct c d b)
  ((s1 * s2 < 0) && (s3 * s4 < 0)) ||
  (s1 == 0 && onSegment a b c) ||
  (s2 == 0 && onSegment a b d) ||
  (s3 == 0 && onSegment c d a) ||
  (s4 == 0 && onSegment c d b)

#print axioms discreteSegmentsIntersectOrTouch


