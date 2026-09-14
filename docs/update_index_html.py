import json

with open('boundary_js_snippet.js') as f:
    boundary_snippet = f.read().strip()

with open('index.html') as f:
    html = f.read()

# 1. Insert button into controls-grid
btn_html = '''      <button id="btn-boundary" class="btn active" title="Toggle 1D Delta_2 Boundary Frame">
        🖼️ Frame: ON
      </button>
      <button id="btn-snap" class="btn active" title="Toggle automatic vertex & edge snapping">'''

html = html.replace('<button id="btn-snap" class="btn active" title="Toggle automatic vertex & edge snapping">', btn_html)

# 2. Insert boundary-layer into viewport-layer
layers_html = '''      <!-- Main Transformed Layer for Pan & Zoom -->
      <g id="viewport-layer">
        <g id="boundary-layer"></g>
        <g id="placed-tiles-group"></g>'''

html = html.replace('<g id="placed-tiles-group"></g>', '<g id="boundary-layer"></g>\n        <g id="placed-tiles-group"></g>')

# 3. Add DELTA2_BOUNDARY_VERTICES constant before state management
snippet_to_insert = boundary_snippet + '\n\n      // 2. STATE MANAGEMENT'
html = html.replace('// 2. STATE MANAGEMENT', snippet_to_insert)

# 4. Add boundaryVisible to state
html = html.replace('snappingEnabled: true,', 'snappingEnabled: true,\n        boundaryVisible: true,')

# 5. Add DOM element reference for boundaryLayer & btnBoundary
dom_refs = '''      const placedTilesGroup = document.getElementById('placed-tiles-group');
      const boundaryLayer = document.getElementById('boundary-layer');
      const ghostTileGroup = document.getElementById('ghost-tile-group');
      const tilePaletteContainer = document.getElementById('tile-palette');
      const bgRect = document.getElementById('bg-rect');

      const btnSnap = document.getElementById('btn-snap');
      const btnBoundary = document.getElementById('btn-boundary');'''

html = html.replace('''      const placedTilesGroup = document.getElementById('placed-tiles-group');
      const ghostTileGroup = document.getElementById('ghost-tile-group');
      const tilePaletteContainer = document.getElementById('tile-palette');
      const bgRect = document.getElementById('bg-rect');

      const btnSnap = document.getElementById('btn-snap');''', dom_refs)

# 6. Update centerViewport zoom to 0.65 for optimal framing
html = html.replace('state.view.zoom = 1.0;', 'state.view.zoom = 0.65;')

# 7. Update findSnapPosition to include boundaryVerts
snap_code_old = '''        // Collect all placed tile vertices
        const existingVertsList = [];
        for (const existingTile of state.tiles) {
          if (existingTile.id === ignoreTileId) continue;
          const evs = getTransformedVertices(existingTile.x, existingTile.y, existingTile.rotationDeg);
          existingVertsList.push(...evs);
        }'''

snap_code_new = '''        // Collect all target snapping vertices (placed tiles + 1D Delta_2 boundary)
        const existingVertsList = [];
        for (const existingTile of state.tiles) {
          if (existingTile.id === ignoreTileId) continue;
          const evs = getTransformedVertices(existingTile.x, existingTile.y, existingTile.rotationDeg);
          existingVertsList.push(...evs);
        }

        if (state.boundaryVisible && typeof DELTA2_BOUNDARY_VERTICES !== 'undefined') {
          existingVertsList.push(...DELTA2_BOUNDARY_VERTICES);
        }'''

html = html.replace(snap_code_old, snap_code_new)

# 8. Add renderBoundaryFrame function & button click listener & init call
render_boundary_fn = '''      function renderBoundaryFrame() {
        if (!boundaryLayer) return;
        boundaryLayer.innerHTML = '';
        if (!state.boundaryVisible || typeof DELTA2_BOUNDARY_VERTICES === 'undefined') return;

        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const pathD = "M " + DELTA2_BOUNDARY_VERTICES.map(v => `${v.x.toFixed(2)},${v.y.toFixed(2)}`).join(" L ") + " Z";
        path.setAttribute('d', pathD);
        path.setAttribute('id', 'delta2-boundary-path');
        path.setAttribute('fill', 'rgba(56, 189, 248, 0.06)');
        path.setAttribute('stroke', '#38bdf8');
        path.setAttribute('stroke-width', '2.5');
        path.setAttribute('stroke-linejoin', 'round');
        path.setAttribute('filter', 'drop-shadow(0 0 10px rgba(56, 189, 248, 0.35))');

        boundaryLayer.appendChild(path);
      }
'''

html = html.replace('// 6. RENDERERS', render_boundary_fn + '\n      // 6. RENDERERS')

listener_code = '''      btnBoundary.addEventListener('click', () => {
        state.boundaryVisible = !state.boundaryVisible;
        btnBoundary.classList.toggle('active', state.boundaryVisible);
        btnBoundary.textContent = `🖼️ Frame: ${state.boundaryVisible ? 'ON' : 'OFF'}`;
        renderBoundaryFrame();
      });

      btnSnap.addEventListener('click', () => {'''

html = html.replace('btnSnap.addEventListener(\'click\', () => {', listener_code)

init_code = '''      function init() {
        centerViewport();
        renderBoundaryFrame();
        renderPalette();
        renderPlacedTiles();
        updateHUD();
      }'''

html = html.replace('''      function init() {
        centerViewport();
        renderPalette();
        renderPlacedTiles();
        updateHUD();
      }''', init_code)

with open('index.html', 'w') as f:
    f.write(html)

print("Updated index.html with 1D Delta_2 boundary frame & snapping successfully!")
