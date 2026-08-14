import math
import numpy as np

def pt(x, y):
    return (float(x), float(y))

def radians(deg):
    return deg * math.pi / 180.0

# Affine 2D matrix: [a, b, c, d, e, f] representing x' = a*x + b*y + c, y' = d*x + e*y + f
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
        # Transformed vertices for this single tile
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

# Build level 0 base system
sys_0 = buildSpectreBase()
# Build level 1 supertiles
sys_1 = buildSupertiles(sys_0)
# Build level 2 supertiles (Delta_2)
sys_2 = buildSupertiles(sys_1)

delta_2 = sys_2['Delta']
tiles = delta_2.get_tiles()
print(f"Number of tiles in Delta_2 cluster: {len(tiles)}")

# Inspect bounding box of Delta_2
all_pts = []
for lab, pts in tiles:
    all_pts.extend(pts)
all_pts = np.array(all_pts)
min_x, min_y = all_pts.min(axis=0)
max_x, max_y = all_pts.max(axis=0)
width = max_x - min_x
height = max_y - min_y
print(f"Bounding box min: ({min_x:.3f}, {min_y:.3f}), max: ({max_x:.3f}, {max_y:.3f})")
print(f"Span width: {width:.3f}, height: {height:.3f}")

# Single tile span
single_tile_pts = np.array(tiles[0][1])
st_min = single_tile_pts.min(axis=0)
st_max = single_tile_pts.max(axis=0)
st_width = st_max[0] - st_min[0]
st_height = st_max[1] - st_min[1]
st_span = math.hypot(st_width, st_height)
print(f"Single tile bounding box width: {st_width:.3f}, height: {st_height:.3f}, max span: {st_span:.3f}")
