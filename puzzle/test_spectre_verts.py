import math
sqrt3 = math.sqrt(3)
spectre = [
    (0, 0),
    (1.0, 0.0),
    (1.5, -sqrt3/2),
    (1.5 + sqrt3/2, -0.5 + sqrt3/2 - sqrt3/2), # let's check exact formula
    (1.5 + sqrt3/2, 0.5 + sqrt3/2 - sqrt3/2),
]
for i, (x, y) in enumerate(spectre):
    print(f"v{i}: {x:.6f}, {y:.6f}")
