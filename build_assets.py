#!/usr/bin/env python3
"""
Master build script to generate premium vector SVGs for all Tier-1 and Tier-2 metatiles
and run sanity verification checks.
"""
import os
import sys

# Ensure root package is importable
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from spectre_solver.geometry import LatticePoint, polygons_overlap
from spectre_solver.tiling import generate_inflated_patch

SUPERTILER_TYPES = ["Gamma", "Delta", "Theta", "Lambda", "Xi", "Pi", "Sigma", "Phi", "Psi"]

def export_premium_svg(patch, filename, title_text):
    xs = [v[0] for tile in patch for v in tile.vertices_float[:-1]]
    ys = [v[1] for tile in patch for v in tile.vertices_float[:-1]]
    if not xs or not ys:
        return
        
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)
    
    pad = 2.0
    w = max_x - min_x + 2 * pad
    h = max_y - min_y + 2 * pad
    
    # Premium color palette: deep metallic tones and modern cyan/blue accents
    colors = [
        "#1f2833", "#112233", "#1b4d3e", "#004b49",
        "#2d3748", "#1a365d", "#1e3a8a", "#0f766e",
        "#4a5568", "#1d4ed8", "#2563eb", "#0d9488"
    ]
    
    svg_lines = [
        f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{min_x - pad:.4f} {min_y - pad:.4f} {w:.4f} {h:.4f}" width="100%" height="100%">\n',
        f'  <!-- Background -->\n',
        f'  <rect x="{min_x - pad:.4f}" y="{min_y - pad:.4f}" width="{w:.4f}" height="{h:.4f}" fill="#0b0c10" />\n'
    ]
    
    # Render tiles
    for tile in patch:
        pts = " ".join(f"{v[0]:.4f},{v[1]:.4f}" for v in tile.vertices_float[:-1])
        color = colors[tile.orientation % len(colors)]
        stroke_color = "#45a29e" if tile.reflected else "#c5c6c7"
        stroke_width = "0.08" if tile.reflected else "0.06"
        svg_lines.append(f'  <polygon points="{pts}" fill="{color}" stroke="{stroke_color}" stroke-width="{stroke_width}" stroke-linejoin="round" />\n')
        
    svg_lines.append('</svg>\n')
    
    with open(filename, "w") as f:
        f.write("".join(svg_lines))
    print(f"  Successfully exported premium SVG to: {filename}")

def main():
    print("="*60)
    print("SPECTRE METATILE ASSET GENERATOR & VERIFIER")
    print("="*60)
    
    output_dir = "./assets"
    os.makedirs(output_dir, exist_ok=True)
    
    for t_type in SUPERTILER_TYPES:
        for gen in [1, 2]:
            print(f"Processing metatile: {t_type} (Generation {gen})...")
            # Generate patch
            patch = generate_inflated_patch(t_type, gen, LatticePoint(0,0,0,0), 0, reflected=(gen % 2 == 1))
            print(f"  Generated {len(patch)} tiles.")
            
            # Verify overlap check
            overlaps = 0
            for i in range(len(patch)):
                for j in range(i + 1, len(patch)):
                    if polygons_overlap(patch[i], patch[j]):
                        overlaps += 1
            if overlaps > 0:
                print(f"  WARNING: Detected {overlaps} overlapping tile pairs!")
            
            # Export SVG
            filename = os.path.join(output_dir, f"{t_type.lower()}_{gen}.svg")
            export_premium_svg(patch, filename, f"{t_type} Gen-{gen}")
            
    print("\n" + "="*60)
    print("ASSET GENERATION COMPLETE! 🎉")
    print(f"All premium vector SVGs are saved in: {output_dir}")
    print("="*60)

if __name__ == "__main__":
    main()
