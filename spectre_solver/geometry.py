import math
import sys

# Global configuration variables
use_optimization = False
BASE_CENTROIDS = {}

# =====================================================================
# EXACT DIOPHANTINE ARITHMETIC ENGINES
# =====================================================================
class Z3:
    def __init__(self, u: int, v: int):
        self.u = u
        self.v = v

    def __add__(self, other): return Z3(self.u + other.u, self.v + other.v)
    def __sub__(self, other): return Z3(self.u - other.u, self.v - other.v)
    def __mul__(self, other):
        return Z3(self.u * other.u + 3 * self.v * other.v, self.u * other.v + self.v * other.u)

    def is_non_neg(self) -> bool:
        if self.u >= 0 and self.v >= 0: return True
        if self.u <= 0 and self.v <= 0: return False
        if self.u < 0 and self.v > 0: return 3 * self.v * self.v >= self.u * self.u
        return self.u * self.u >= 3 * self.v * self.v

    def sign(self) -> int:
        if self.u == 0 and self.v == 0: return 0
        return 1 if self.is_non_neg() else -1

    def to_float(self) -> float:
        return float(self.u) + float(self.v) * math.sqrt(3.0)

    def scale2(self):
        return Z3(self.u * 2, self.v * 2)

class Point2D:
    def __init__(self, x: Z3, y: Z3):
        self.x = x
        self.y = y
    def scale2(self):
        return Point2D(self.x.scale2(), self.y.scale2())
    def to_float_coords(self) -> tuple[float, float]:
        return (self.x.to_float(), self.y.to_float())

class LatticePoint:
    def __init__(self, a: int, b: int, c: int, d: int):
        self.a, self.b, self.c, self.d = a, b, c, d

    def add(self, other):
        return LatticePoint(self.a + other.a, self.b + other.b, self.c + other.c, self.d + other.d)

    def sub(self, other):
        return LatticePoint(self.a - other.a, self.b - other.b, self.c - other.c, self.d - other.d)

    def rot30(self):
        return LatticePoint(-self.d, self.a, self.b + self.d, self.c)
        
    def inflate(self):
        """Applies the canonical 4x4 cyclotomic inflation matrix for the Spectre substitution."""
        a_new = 4 * self.a + 3 * self.b
        b_new = 2 * self.a + 1 * self.b - self.c - self.d
        c_new = 4 * self.c + 3 * self.d
        d_new = 1 * self.a + 1 * self.b + 3 * self.c + 2 * self.d
        return LatticePoint(a_new, b_new, c_new, d_new)
        
    def inflate_n(self, n: int):
        """Iteratively inflates the coordinate vector by N generations."""
        pt = self
        for _ in range(n):
            pt = pt.inflate()
        return pt

    def to_tuple(self):
        return (self.a, self.b, self.c, self.d)

    def to_point2d(self) -> Point2D:
        return Point2D(Z3(2 * self.a + self.c, self.b), Z3(self.b + 2 * self.d, self.c))

    def to_float_coords(self) -> tuple[float, float]:
        return self.to_point2d().to_float_coords()

# =====================================================================
# MONOTILE GEOMETRY & VECTOR INTERSECTION PRUNING
# =====================================================================
SPECTRE_TURNS = [90, -60, 90, 60, -90, 60, 90, 60, -90, 60, 0, 60, 90, -60]
TURN_STEPS = {-90: -3, -60: -2, 0: 0, 60: 2, 90: 3}
STEP_TO_DEG = {-3: -90, -2: -60, 0: 0, 2: 60, 3: 90}

def dir_to_vec(d: int) -> LatticePoint:
    pt = LatticePoint(1, 0, 0, 0)
    for _ in range(d % 12): pt = pt.rot30()
    return pt

VEC_TO_DIR = {}
for _d in range(12):
    _vec = dir_to_vec(_d)
    VEC_TO_DIR[_vec.to_tuple()] = _d

def cross_product(p1: Point2D, p2: Point2D, p3: Point2D) -> Z3:
    return ((p2.x - p1.x) * (p3.y - p1.y)) - ((p2.y - p1.y) * (p3.x - p1.x))

def point_in_polygon(pt: Point2D, poly: list[Point2D]) -> bool:
    count = 0
    for i in range(len(poly) - 1):
        a, b = poly[i], poly[i+1]
        
        cp = cross_product(a, b, pt).sign()
        if cp == 0:
            dx_sign = (pt.x - a.x).sign() * (pt.x - b.x).sign()
            dy_sign = (pt.y - a.y).sign() * (pt.y - b.y).sign()
            if dx_sign <= 0 and dy_sign <= 0:
                return False  
                
        cond1, cond2 = (pt.y - a.y).sign(), (pt.y - b.y).sign()
        if (cond1 >= 0 and cond2 < 0) or (cond2 >= 0 and cond1 < 0):
            if (a.y - b.y).sign() < 0:
                if cp > 0: count += 1
            elif cp < 0: count += 1
            
    return count % 2 == 1

def reflect_lattice_point(lp: LatticePoint) -> LatticePoint:
    return LatticePoint(-lp.a - lp.c, -lp.b, lp.c, lp.b + lp.d)

def vec_to_dir(step_vec: LatticePoint) -> int:
    for d in range(12):
        if dir_to_vec(d).to_tuple() == step_vec.to_tuple():
            return d
    return 0

class PlacedTile:
    def __init__(self, origin: LatticePoint, orientation: int, reflected: bool = False):
        self.origin = origin
        self.orientation = orientation
        self.reflected = reflected
        self.vertices = []
        self.edges = []
        self._build_geometry()
        
        if (self.orientation, self.reflected) in BASE_CENTROIDS:
            base_cx, base_cy = BASE_CENTROIDS[(self.orientation, self.reflected)]
            ox, oy = self.origin.to_float_coords()
            self.centroid_float = (base_cx + ox, base_cy + oy)
        else:
            self.centroid_float = (
                sum(v.to_point2d().x.to_float() for v in self.vertices[:-1]) / 14.0,
                sum(v.to_point2d().y.to_float() for v in self.vertices[:-1]) / 14.0
            )
            
        self.vertices_float = [v.to_float_coords() for v in self.vertices]

    def _build_geometry(self):
        curr_dir = self.orientation
        curr_pos = LatticePoint(0, 0, 0, 0)
        self.vertices.append(curr_pos)
        dirs = [curr_dir]
        for t in SPECTRE_TURNS[1:]:
            curr_dir = (curr_dir + TURN_STEPS[t]) % 12
            dirs.append(curr_dir)
        for d in dirs:
            next_pos = curr_pos.add(dir_to_vec(d))
            self.edges.append((curr_pos.to_tuple(), next_pos.to_tuple(), d))
            curr_pos = next_pos
            self.vertices.append(curr_pos)

        if self.reflected:
            self.vertices = [reflect_lattice_point(v) for v in self.vertices]
            self.vertices = [self.vertices[0]] + self.vertices[1:14][::-1] + [self.vertices[0]]
            
            self.edges = []
            for i in range(14):
                v1, v2 = self.vertices[i], self.vertices[i+1]
                step = v2.sub(v1)
                d = vec_to_dir(step)
                self.edges.append((v1.to_tuple(), v2.to_tuple(), d))

        self.vertices = [v.add(self.origin) for v in self.vertices]
        shifted_edges = []
        for src, dst, d in self.edges:
            shifted_src = LatticePoint(*src).add(self.origin).to_tuple()
            shifted_dst = LatticePoint(*dst).add(self.origin).to_tuple()
            shifted_edges.append((shifted_src, shifted_dst, d))
        self.edges = shifted_edges

def cross_product_float(p1, p2, p3):
    return ((p2[0] - p1[0]) * (p3[1] - p1[1])) - ((p2[1] - p1[1]) * (p3[0] - p1[0]))

def segments_intersect_float(a, b, c, d):
    cp1 = cross_product_float(a, b, c)
    cp2 = cross_product_float(a, b, d)
    cp3 = cross_product_float(c, d, a)
    cp4 = cross_product_float(c, d, b)
    if cp1 * cp2 < -1e-9 and cp3 * cp4 < -1e-9:
        return True
    return False

def point_in_polygon_float(pt, poly):
    count = 0
    n = len(poly) - 1
    px, py = pt
    for i in range(n):
        x1, y1 = poly[i]
        x2, y2 = poly[i+1]
        if ((y1 >= py) != (y2 >= py)):
            dy = y2 - y1
            if abs(dy) > 1e-9:
                if px < (x2 - x1) * (py - y1) / dy + x1:
                    count += 1
    return count % 2 != 0

def polygons_overlap(t1: PlacedTile, t2: PlacedTile) -> bool:
    global use_optimization
    if t1.origin.to_tuple() == t2.origin.to_tuple() and t1.orientation == t2.orientation and t1.reflected == t2.reflected:
        return True

    if use_optimization:
        cx1, cy1 = t1.centroid_float
        cx2, cy2 = t2.centroid_float
        dx = cx1 - cx2
        dy = cy1 - cy2
        if dx*dx + dy*dy > 36.0:
            return False

    cx1, cy1 = t1.centroid_float
    cx2, cy2 = t2.centroid_float

    # Shrink polygons inwards slightly to eliminate outer edge-sharing false positives
    pts1 = [(p[0] + (cx1 - p[0]) * 1e-4, p[1] + (cy1 - p[1]) * 1e-4) for p in t1.vertices_float]
    pts2 = [(p[0] + (cx2 - p[0]) * 1e-4, p[1] + (cy2 - p[1]) * 1e-4) for p in t2.vertices_float]

    for i in range(14):
        p1a, p1b = pts1[i], pts1[i+1]
        for j in range(14):
            p2a, p2b = pts2[j], pts2[j+1]
            if segments_intersect_float(p1a, p1b, p2a, p2b):
                return True

    for v in pts1[:-1]:
        if point_in_polygon_float(v, pts2): return True
    for v in pts2[:-1]:
        if point_in_polygon_float(v, pts1): return True

    return False

# Initialize BASE_CENTROIDS pre-computations
for _refl in [False, True]:
    for _orient in range(12):
        _t = PlacedTile(LatticePoint(0, 0, 0, 0), _orient, reflected=_refl)
        BASE_CENTROIDS[(_orient, _refl)] = _t.centroid_float
