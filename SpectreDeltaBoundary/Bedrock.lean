import Mathlib.Tactic.Ext

/-- A lattice point in Z[ζ12] represented by four exact integer coordinates. -/
@[ext]
structure LatticePoint where
  a : Int
  b : Int
  c : Int
  d : Int
deriving DecidableEq, Repr

instance : Add LatticePoint where
  add p q := ⟨p.a + q.a, p.b + q.b, p.c + q.c, p.d + q.d⟩

instance : Sub LatticePoint where
  sub p q := ⟨p.a - q.a, p.b - q.b, p.c - q.c, p.d - q.d⟩

instance : Neg LatticePoint where
  neg p := ⟨-p.a, -p.b, -p.c, -p.d⟩

/-- Rotates a lattice point by 30 degrees counterclockwise.
    Maps (a, b, c, d) to (-d, a, b + d, c). -/
def rot30 (pt : LatticePoint) : LatticePoint :=
  ⟨-pt.d, pt.a, pt.b + pt.d, pt.c⟩

/-- Composition of rot30 exactly 12 times to represent a full 360-degree rotation. -/
def rot12_30 (pt : LatticePoint) : LatticePoint :=
  rot30 (rot30 (rot30 (rot30 (rot30 (rot30 (rot30 (rot30 (rot30 (rot30 (rot30 (rot30 pt)))))))))))

/-- Theorem verifying that rotating 12 times yields the exact identity point. -/
theorem rot12_identity (pt : LatticePoint) : rot12_30 pt = pt := by
  cases pt
  simp [rot12_30, rot30, LatticePoint.mk.injEq]
  omega

#print axioms rot12_identity

/-- Vector addition of two points on the cyclotomic lattice. -/
def LatticePoint.add (p1 p2 : LatticePoint) : LatticePoint :=
  ⟨p1.a + p2.a, p1.b + p2.b, p1.c + p2.c, p1.d + p2.d⟩

/-- Vector subtraction of two points on the cyclotomic lattice. -/
def LatticePoint.sub (p1 p2 : LatticePoint) : LatticePoint :=
  ⟨p1.a - p2.a, p1.b - p2.b, p1.c - p2.c, p1.d - p2.d⟩

/-- The origin point (zero vector) of the lattice. -/
def LatticePoint.zero : LatticePoint := ⟨0, 0, 0, 0⟩

/-- Helper function to apply rot30 recursively 'n' times. -/
def rot30N (n : Nat) (pt : LatticePoint) : LatticePoint :=
  match n with
  | 0 => pt
  | n + 1 => rot30 (rot30N n pt)

/-- Maps a discrete direction identifier (0 to 11) to its corresponding unit lattice vector.
    Perfectly mirrors the Python engine's dir_to_vec unrolled translation loop. -/
def dir_to_vec (d : Nat) : LatticePoint :=
  rot30N (d % 12) ⟨1, 0, 0, 0⟩

/-- Fundamental lemma verifying that a step in direction index (d + 1) matches
    the 30-degree rotation of the vector for direction d. -/
lemma rot30N_step (n : Nat) (pt : LatticePoint) : rot30N (n + 1) pt = rot30 (rot30N n pt) := by
  rfl

#print axioms LatticePoint.add
#print axioms dir_to_vec

/-- Represents an exact quadratic integer of the form u + v*sqrt(3). -/
structure Z3 where
  u : Int
  v : Int
deriving DecidableEq, Repr

/-- Exact addition within the Z3 quadratic ring. -/
def Z3.add (z1 z2 : Z3) : Z3 :=
  ⟨z1.u + z2.u, z1.v + z2.v⟩

/-- Exact subtraction within the Z3 quadratic ring. -/
def Z3.sub (z1 z2 : Z3) : Z3 :=
  ⟨z1.u - z2.u, z1.v - z2.v⟩

/-- Exact multiplication within the Z3 quadratic ring.
    Derived from (u1 + v1√3)(u2 + v2√3)
    = (u1*u2 + 3*v1*v2) + (u1*v2 + v1*u2)√3. -/
def Z3.mul (z1 z2 : Z3) : Z3 :=
  ⟨z1.u * z2.u + 3 * z1.v * z2.v, z1.u * z2.v + z1.v * z2.u⟩

/-- A 2D coordinate point structure utilizing exact Z3 coordinates for both axes. -/
structure Point2D where
  x : Z3
  y : Z3
deriving DecidableEq, Repr

/-- Projects a 4D cyclotomic LatticePoint down to a discrete 2D Point2D space.
    Perfectly matches Phase 1 of the paths.py exact arithmetic mapping specification. -/
def LatticePoint.toPoint2D (pt : LatticePoint) : Point2D :=
  ⟨⟨2 * pt.a + pt.c, pt.b⟩, ⟨pt.b + 2 * pt.d, pt.c⟩⟩

#print axioms Z3.mul
#print axioms LatticePoint.toPoint2D
