import sys
import os
import math
import numpy as np
from collections import defaultdict
from shapely.geometry import Polygon, LineString, MultiLineString
from shapely.ops import unary_union, linemerge

# Add spectre-delta-boundary directory to sys.path
sys.path.append('/home/tryggth2009/spectre-delta-boundary')
import spectre_boundary_solver as sbs

# 1. GENERATE DELTA_2 PATCH USING SPECTRE-DELTA-BOUNDARY SOLVER
print("Generating Delta_2 patch using spectre-delta-boundary solver...")
patch = sbs.generate_inflated_patch('Delta', 2, sbs.LatticePoint(0,0,0,0), 0, reflected=False)
print(f"Generated {len(patch)} tiles.")

# Extract raw tile float vertices (each tile has 14 vertices)
raw_tiles_pts = [tile.vertices_float[:-1] for tile in patch]

# Calculate raw bounding box
all_raw_pts = np.array([pt for polygon in raw_tiles_pts for pt in polygon])
raw_min_x, raw_min_y = all_raw_pts.min(axis=0)
raw_max_x, raw_max_y = all_raw_pts.max(axis=0)

raw_center_x = (raw_min_x + raw_max_x) / 2.0
raw_center_y = (raw_min_y + raw_max_y) / 2.0

raw_width = raw_max_x - raw_min_x
raw_height = raw_max_y - raw_min_y

print(f"Raw Delta_2 bounding box: width={raw_width:.3f}, height={raw_height:.3f}")
print(f"Raw center: ({raw_center_x:.3f}, {raw_center_y:.3f})")

# Scale geometry so cluster footprint is ~240mm (height ~240mm) centered at (150mm, 150mm)
# Setting scale S = 240.0 / raw_height (~6.5)
SCALE = 240.0 / raw_height
TARGET_CENTER = (150.0, 150.0)

scaled_tiles = []
for polygon in raw_tiles_pts:
    scaled_poly = []
    for x, y in polygon:
        sx = (x - raw_center_x) * SCALE + TARGET_CENTER[0]
        sy = (y - raw_center_y) * SCALE + TARGET_CENTER[1]
        scaled_poly.append((sx, sy))
    scaled_tiles.append(scaled_poly)

# Calculate single tile span in scaled units (mm)
st_pts = np.array(scaled_tiles[0])
st_min = st_pts.min(axis=0)
st_max = st_pts.max(axis=0)
st_width = st_max[0] - st_min[0]
st_height = st_max[1] - st_min[1]
st_span = math.hypot(st_width, st_height)
print(f"Scaled single tile bounding box: {st_width:.2f}mm x {st_height:.2f}mm, max span: {st_span:.2f}mm")

# 2. PLANAR GRAPH TOPOLOGY & DEDUPLICATION
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

print(f"Deduplicated internal segments (shared cuts): {len(internal_edges)}")
print(f"Deduplicated boundary segments (outer aperture): {len(boundary_edges)}")

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

# 3. SVG & PATH GENERATION
def coords_to_path_d(coords, is_closed=False):
    pts_str = [f"{x:.4f} {y:.4f}" for x, y in coords]
    d = "M " + " L ".join(pts_str)
    if is_closed:
        d += " Z"
    return d

# Outer Rectangular Frame Perimeter (280mm x 280mm with 10mm corner radii)
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

boundary_path_d = coords_to_path_d(boundary_ring.coords, is_closed=True)
internal_paths_d = [coords_to_path_d(line.coords, is_closed=False) for line in internal_paths]

# MANUFACTURING SVG (stroke-width="0.01mm")
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

# PREVIEW SVG (stroke-width="0.5mm" for bold, high-contrast, crystal-clear PNG rendering)
sheet_1_preview_svg = sheet_1_svg.replace('stroke-width="0.01mm"', 'stroke-width="0.8mm"')

internal_paths_preview_xml = "\n".join([
    f'  <path id="internal_tile_cut_{i+1}" d="{d}" fill="none" stroke="#00AA00" stroke-width="0.4mm" />'
    for i, d in enumerate(internal_paths_d)
])

sheet_2_preview_svg = f'''<?xml version="1.0" encoding="UTF-8" standalone="no"?>
<svg
   width="300mm"
   height="300mm"
   viewBox="0 0 300 300"
   version="1.1"
   xmlns="http://www.w3.org/2000/svg">
  <rect width="300" height="300" fill="#F8F9FA" />
  <g id="outer_frame_perimeter_group">
    <path
       id="outer_frame_perimeter"
       d="{frame_path_d}"
       fill="none"
       stroke="#CC0000"
       stroke-width="0.8mm" />
  </g>
  <g id="delta_2_boundary_group">
    <path
       id="delta_2_outer_boundary"
       d="{boundary_path_d}"
       fill="#EBF4FF"
       stroke="#0055FF"
       stroke-width="0.6mm" />
  </g>
  <g id="internal_spectre_cuts_group">
{internal_paths_preview_xml}
  </g>
</svg>
'''

with open('sheet_1_preview.svg', 'w') as f:
    f.write(sheet_1_preview_svg)

with open('sheet_2_preview.svg', 'w') as f:
    f.write(sheet_2_preview_svg)

print("Saved manufacturing SVGs and preview SVGs successfully!")
