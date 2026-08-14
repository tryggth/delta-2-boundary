import math
import numpy as np
import os
from collections import defaultdict
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely.ops import unary_union, linemerge

# ----------------------------------------------------
# 1. MATHEMATICAL GENERATION OF SPECTRE MONOTILE
# ----------------------------------------------------

def pt(x, y):
    return (float(x), float(y))

def radians(deg):
    return deg * math.pi / 180.0

ident = [1.0, 0.0, 0.0, 0.0, 1.0, 0.0]

def inv(T):
    det = T[0]*T[4] - T[1]*T[3]
    return [T[4]/det, -T[1]/det, (T[1]*T[5]-T[2]*T[4])/det,
            -T[3]/det, T[0]/det, (T[2]*T[3]-T[0]*T[5])/det]

def mul(A, B):
    return [A[0]*B[0] + A[1]*B[3], 
            A[0]*B[1] + A[1]*B[4],
            A[0]*B[2] + A[1]*B[5] + A[2],

            A[3]*B[0] + A[4]*B[3], 
            A[3]*B[1] + A[4]*B[4],
            A[3]*B[2] + A[4]*B[5] + A[5]]

def trot(ang):
    c = math.cos(ang)
    s = math.sin(ang)
    return [c, -s, 0.0, s, c, 0.0]

def ttrans(tx, ty):
    return [1.0, 0.0, float(tx), 0.0, 1.0, float(ty)]

def transTo(p, q):
    return ttrans(q[0] - p[0], q[1] - p[1])

def transPt(M, P):
    return (M[0]*P[0] + M[1]*P[1] + M[2], M[3]*P[0] + M[4]*P[1] + M[5])

class Shape:
    def __init__(self, pts, quad, label):
        self.pts = pts
        self.quad = quad
        self.label = label

    def get_tiles(self, T=ident):
        transformed_pts = [transPt(T, p) for p in self.pts]
        return [(self.label, transformed_pts)]

class Meta:
    def __init__(self):
        self.geoms = []
        self.quad = []

    def addChild(self, g, T):
        self.geoms.append({'geom': g, 'xform': T})

    def get_tiles(self, T=ident):
        tiles = []
        for child in self.geoms:
            combined_T = mul(T, child['xform'])
            tiles.extend(child['geom'].get_tiles(combined_T))
        return tiles

def buildSpectreBase():
    # Spectre tile geometry (Smith et al. 2023)
    spectre = [
        pt(0, 0),
        pt(1.0, 0.0),
        pt(1.5, -0.8660254037844386),
        pt(2.366025403784439, -0.36602540378443865),
        pt(2.366025403784439, 0.6339745962155614),
        pt(3.366025403784439, 0.6339745962155614),
        pt(3.866025403784439, 1.5),
        pt(3.0, 2.0),
        pt(2.133974596215561, 1.5),
        pt(1.6339745962155614, 2.3660254037844393),
        pt(0.6339745962155614, 2.3660254037844393),
        pt(-0.3660254037844386, 2.3660254037844393),
        pt(-0.866025403784439, 1.5),
        pt(0.0, 1.0)
    ]
    spectre_keys = [spectre[3], spectre[5], spectre[7], spectre[11]]

    ret = {}
    for lab in ['Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Phi', 'Psi']:
        ret[lab] = Shape(spectre, spectre_keys, lab)

    mystic = Meta()
    mystic.addChild(Shape(spectre, spectre_keys, 'Gamma1'), ident)
    mystic.addChild(Shape(spectre, spectre_keys, 'Gamma2'),
                    mul(ttrans(spectre[8][0], spectre[8][1]), trot(math.pi / 6.0)))
    mystic.quad = spectre_keys
    ret['Gamma'] = mystic
    return ret

def buildSupertiles(sys):
    quad = sys['Delta'].quad
    R = [-1.0, 0.0, 0.0, 0.0, 1.0, 0.0]
    t_rules = [
        [60, 3, 1], [0, 2, 0], [60, 3, 1], [60, 3, 1],
        [0, 2, 0], [60, 3, 1], [-120, 3, 3]
    ]

    Ts = [ident]
    total_ang = 0.0
    rot = ident
    tquad = list(quad)

    for ang, from_idx, to_idx in t_rules:
        total_ang += ang
        if ang != 0:
            rot = trot(radians(total_ang))
            for i in range(4):
                tquad[i] = transPt(rot, quad[i])
        ttt = transTo(tquad[to_idx], transPt(Ts[-1], quad[from_idx]))
        Ts.append(mul(ttt, rot))

    for idx in range(len(Ts)):
        Ts[idx] = mul(R, Ts[idx])

    super_rules = {
        'Gamma':  ['Pi','Delta','null','Theta','Sigma','Xi','Phi','Gamma'],
        'Delta':  ['Xi','Delta','Xi','Phi','Sigma','Pi','Phi','Gamma'],
        'Theta':  ['Psi','Delta','Pi','Phi','Sigma','Pi','Phi','Gamma'],
        'Lambda': ['Psi','Delta','Xi','Phi','Sigma','Pi','Phi','Gamma'],
        'Xi':     ['Psi','Delta','Pi','Phi','Sigma','Psi','Phi','Gamma'],
        'Pi':     ['Psi','Delta','Xi','Phi','Sigma','Psi','Phi','Gamma'],
        'Sigma':  ['Xi','Delta','Xi','Phi','Sigma','Pi','Lambda','Gamma'],
        'Phi':    ['Psi','Delta','Psi','Phi','Sigma','Pi','Phi','Gamma'],
        'Psi':    ['Psi','Delta','Psi','Phi','Sigma','Psi','Phi','Gamma']
    }

    super_quad = [
        transPt(Ts[6], quad[2]),
        transPt(Ts[5], quad[1]),
        transPt(Ts[3], quad[2]),
        transPt(Ts[0], quad[1])
    ]

    ret = {}
    for lab, subs in super_rules.items():
        sup = Meta()
        for idx in range(8):
            if subs[idx] == 'null':
                continue
            sup.addChild(sys[subs[idx]], Ts[idx])
        sup.quad = super_quad
        ret[lab] = sup
    return ret

# Build Delta_2 supertile cluster
sys_0 = buildSpectreBase()
sys_1 = buildSupertiles(sys_0)
sys_2 = buildSupertiles(sys_1)
delta_2_cluster = sys_2['Delta'].get_tiles()

# ----------------------------------------------------
# 2. SCALING & CENTERING
# ----------------------------------------------------

# Raw coordinates
raw_tiles_pts = [pts for label, pts in delta_2_cluster]

# Calculate raw bounding box
all_raw_pts = np.array([pt for polygon in raw_tiles_pts for pt in polygon])
raw_min_x, raw_min_y = all_raw_pts.min(axis=0)
raw_max_x, raw_max_y = all_raw_pts.max(axis=0)

raw_center_x = (raw_min_x + raw_max_x) / 2.0
raw_center_y = (raw_min_y + raw_max_y) / 2.0

# Target scale: we want Delta_2 cluster footprint ~240mm x 240mm (height ~240mm)
# Raw height is 36.883. Setting S = 6.5 gives height = 239.74mm.
SCALE = 6.5
TARGET_CENTER = (150.0, 150.0)

scaled_tiles = []
for polygon in raw_tiles_pts:
    scaled_poly = []
    for x, y in polygon:
        # Shift center to (0,0), scale, then shift to target center (150, 150)
        sx = (x - raw_center_x) * SCALE + TARGET_CENTER[0]
        sy = (y - raw_center_y) * SCALE + TARGET_CENTER[1]
        scaled_poly.append((sx, sy))
    scaled_tiles.append(scaled_poly)

# ----------------------------------------------------
# 3. PLANAR GRAPH TOPOLOGY & DEDUPLICATION
# ----------------------------------------------------

def round_pt(p, decimals=4):
    return (round(p[0], decimals), round(p[1], decimals))

edge_counts = defaultdict(int)
edge_coords = {}

for pts in scaled_tiles:
    N = len(pts)
    for i in range(N):
        p1 = round_pt(pts[i])
        p2 = round_pt(pts[(i+1)%N])
        if p1 == p2:
            continue
        key = tuple(sorted([p1, p2]))
        edge_counts[key] += 1
        edge_coords[key] = (p1, p2)

internal_edges = []
boundary_edges = []

for key, count in edge_counts.items():
    p1, p2 = edge_coords[key]
    line = LineString([p1, p2])
    if count == 2:
        internal_edges.append(line)
    elif count == 1:
        boundary_edges.append(line)

print(f"Deduplicated internal segments: {len(internal_edges)}")
print(f"Deduplicated boundary segments: {len(boundary_edges)}")

# Merge connected internal lines into continuous polylines
merged_internal = linemerge(internal_edges)
if isinstance(merged_internal, LineString):
    internal_paths = [merged_internal]
elif isinstance(merged_internal, MultiLineString):
    internal_paths = list(merged_internal.geoms)
else:
    internal_paths = [LineString(ls) for ls in merged_internal]

# Merge boundary lines into a single outer boundary closed path (LinearRing)
shapely_polys = [Polygon(pts) for pts in scaled_tiles]
union_poly = unary_union(shapely_polys)
boundary_ring = union_poly.exterior

print(f"Merged internal polyline count: {len(internal_paths)}")
print(f"Outer boundary ring vertex count: {len(boundary_ring.coords)}")

# ----------------------------------------------------
# 4. SVG GENERATION (PONOKO SPECIFICATIONS)
# ----------------------------------------------------

def coords_to_path_d(coords, is_closed=False):
    # Format floating point numbers cleanly
    pts_str = [f"{x:.4f} {y:.4f}" for x, y in coords]
    d = "M " + " L ".join(pts_str)
    if is_closed:
        d += " Z"
    return d

# Outer Rectangular Frame Perimeter (280mm x 280mm with 10mm corner radii)
# Centered on 300mm x 300mm canvas (margin 10mm)
frame_path_d = (
    "M 20.0000 10.0000 "
    "L 280.0000 10.0000 "
    "A 10.0000 10.0000 0 0 1 290.0000 20.0000 "
    "L 290.0000 280.0000 "
    "A 10.0000 10.0000 0 0 1 280.0000 290.0000 "
    "L 20.0000 290.0000 "
    "A 10.0000 10.0000 0 0 1 10.0000 280.0000 "
    "L 10.0000 20.0000 "
    "A 10.0000 10.0000 0 0 1 20.0000 10.0000 Z"
)

# Delta_2 Outer Boundary Aperture path d
boundary_path_d = coords_to_path_d(boundary_ring.coords, is_closed=True)

# Internal Spectre Tile cut paths d
internal_paths_d = [coords_to_path_d(line.coords, is_closed=False) for line in internal_paths]

# Generate Sheet 1: Base Plate
sheet_1_svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   width="300mm"
   height="300mm"
   viewBox="0 0 300 300"
   version="1.1"
   xmlns="http://www.w3.org/2000/svg">
  <path
     id="outer_frame_perimeter"
     d="{frame_path_d}"
     fill="none"
     stroke="#FF0000"
     stroke-width="0.01mm" />
</svg>
'''

# Generate Sheet 2: Frame and Tiles
internal_paths_xml = "\n".join([
    f'  <path id="internal_tile_cut_{i+1}" d="{d}" fill="none" stroke="#00FF00" stroke-width="0.01mm" />'
    for i, d in enumerate(internal_paths_d)
])

sheet_2_svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   width="300mm"
   height="300mm"
   viewBox="0 0 300 300"
   version="1.1"
   xmlns="http://www.w3.org/2000/svg">
  <g id="outer_frame_perimeter_group">
    <path
       id="outer_frame_perimeter"
       d="{frame_path_d}"
       fill="none"
       stroke="#FF0000"
       stroke-width="0.01mm" />
  </g>
  <g id="delta_2_boundary_group">
    <path
       id="delta_2_outer_boundary"
       d="{boundary_path_d}"
       fill="none"
       stroke="#0000FF"
       stroke-width="0.01mm" />
  </g>
  <g id="internal_spectre_cuts_group">
{internal_paths_xml}
  </g>
</svg>
'''

with open('sheet_1_base_plate.svg', 'w') as f:
    f.write(sheet_1_svg)

with open('sheet_2_frame_and_tiles.svg', 'w') as f:
    f.write(sheet_2_svg)

print("Saved sheet_1_base_plate.svg and sheet_2_frame_and_tiles.svg successfully!")
