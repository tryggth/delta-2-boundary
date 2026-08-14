import math

# A Spectre tile is formed by replacing the straight edges of a Hat polykite with curved edges (or 14-gon straight segments).
# Let's test the 14-vertex Spectre polygon defined in the official paper / reference code:
# Spectre base vertices:
# v0:  (0, 0)
# v1:  (1, 0)
# v2:  (1.5, -sqrt(3)/2)
# v3:  (1.5 + sqrt(3)/2, 0.5 - sqrt(3)/2)
# v4:  (1.5 + sqrt(3)/2, 1.5 - sqrt(3)/2)
# v5:  (2.5 + sqrt(3)/2, 1.5 - sqrt(3)/2)
# v6:  (2.5 + sqrt(3), 1.5)
# v7:  (3.0, 2.0)
# v8:  (3.5 - sqrt(3), 1.5)
# v9:  (2.5 - sqrt(3)/2, 1.5 + sqrt(3)/2)
# v10: (1.5 - sqrt(3)/2, 1.5 + sqrt(3)/2)
# v11: (0.5 - sqrt(3)/2, 1.5 + sqrt(3)/2)
# v12: (-sqrt(3)/2, 1.5)
# v13: (0, 1.0)

sqrt3 = math.sqrt(3)
spectre = [
    (0.0, 0.0),
    (1.0, 0.0),
    (1.5, -sqrt3/2),
    (1.5 + sqrt3/2, 0.5 - sqrt3/2),
    (1.5 + sqrt3/2, 1.5 - sqrt3/2),
    (2.5 + sqrt3/2, 1.5 - sqrt3/2),
    (2.5 + sqrt3, 1.5),
    (3.0, 2.0),
    (3.5 - sqrt3, 1.5),
    (2.5 - sqrt3/2, 1.5 + sqrt3/2),
    (1.5 - sqrt3/2, 1.5 + sqrt3/2),
    (0.5 - sqrt3/2, 1.5 + sqrt3/2),
    (-sqrt3/2, 1.5),
    (0.0, 1.0)
]

print("Total vertices:", len(spectre))

# Check center of mass
cx = sum(p[0] for p in spectre) / 14.0
cy = sum(p[1] for p in spectre) / 14.0
print(f"Center of mass: ({cx:.4f}, {cy:.4f})")
