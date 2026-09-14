import json

with open('solved_placements.json') as f:
    solved_tiles = json.load(f)

with open('delta2_js_data.json') as f:
    boundary_data = json.load(f)

boundary_verts = boundary_data['boundary_verts']

solved_tiles_json = json.dumps(solved_tiles)
boundary_verts_json = json.dumps(boundary_verts)

html_content = f'''<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
  <title>Spectre Monotile Δ₂ Jigsaw Puzzle PWA</title>
  <meta name="description" content="Interactive Spectre Aperiodic Monotile Jigsaw Puzzle Progressive Web App (PWA).">

  <!-- PWA Manifest & Theme Color -->
  <link rel="manifest" href="manifest.json">
  <meta name="theme-color" content="#6366f1">

  <!-- iOS / Mobile Web App Meta Tags -->
  <meta name="mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-capable" content="yes">
  <meta name="apple-mobile-web-app-status-bar-style" content="black-translucent">
  <meta name="apple-mobile-web-app-title" content="Spectre Δ₂">
  <link rel="apple-touch-icon" href="icon-192.png">
  <link rel="icon" type="image/png" sizes="192x192" href="icon-192.png">

  <style>
    :root {{
      --bg-color: #0f172a;
      --panel-bg: #1e293b;
      --card-bg: #334155;
      --card-hover: #475569;
      --text-main: #f8fafc;
      --text-muted: #94a3b8;
      --accent-color: #6366f1;
      --accent-hover: #4f46e5;
      --border-color: #334155;
      --danger-color: #ef4444;
      --success-color: #10b981;
      --warning-color: #f59e0b;
      --grid-line: rgba(255, 255, 255, 0.04);
      --shadow-lg: 0 20px 25px -5px rgba(0, 0, 0, 0.5), 0 8px 10px -6px rgba(0, 0, 0, 0.5);
    }}

    * {{
      box-sizing: border-box;
      margin: 0;
      padding: 0;
      user-select: none;
    }}

    body {{
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
      background-color: var(--bg-color);
      color: var(--text-main);
      display: flex;
      height: 100vh;
      width: 100vw;
      overflow: hidden;
    }}

    /* Sidebar Panel */
    #sidebar {{
      width: 320px;
      background-color: var(--panel-bg);
      border-right: 1px solid var(--border-color);
      display: flex;
      flex-direction: column;
      padding: 1.25rem;
      gap: 1rem;
      z-index: 10;
      box-shadow: 4px 0 20px rgba(0, 0, 0, 0.3);
    }}

    .header-box {{
      display: flex;
      flex-direction: column;
      gap: 0.25rem;
    }}

    .header-title {{
      font-size: 1.35rem;
      font-weight: 800;
      background: linear-gradient(135deg, #a5b4fc, #6366f1, #38bdf8);
      -webkit-background-clip: text;
      -webkit-text-fill-color: transparent;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    .subtitle {{
      font-size: 0.8rem;
      color: var(--text-muted);
      line-height: 1.3;
    }}

    /* Primary Action Toggle Button */
    .btn-primary-action {{
      background: linear-gradient(135deg, #6366f1, #4f46e5);
      color: white;
      border: none;
      border-radius: 10px;
      padding: 0.85rem 1rem;
      font-size: 0.95rem;
      font-weight: 700;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      box-shadow: 0 4px 14px rgba(99, 102, 241, 0.4);
      transition: all 0.2s ease;
    }}

    .btn-primary-action:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 20px rgba(99, 102, 241, 0.6);
    }}

    .btn-primary-action:active {{
      transform: translateY(0);
    }}

    /* PWA Install Button */
    .btn-pwa-install {{
      background: linear-gradient(135deg, #06b6d4, #0891b2);
      color: white;
      border: none;
      border-radius: 8px;
      padding: 0.65rem 0.85rem;
      font-size: 0.85rem;
      font-weight: 700;
      cursor: pointer;
      display: none; /* Auto-displays when PWA prompt is ready */
      align-items: center;
      justify-content: center;
      gap: 0.5rem;
      box-shadow: 0 4px 12px rgba(6, 182, 212, 0.35);
      transition: all 0.2s ease;
    }}

    .btn-pwa-install:hover {{
      transform: translateY(-2px);
      box-shadow: 0 6px 18px rgba(6, 182, 212, 0.5);
    }}

    .section-label {{
      font-size: 0.75rem;
      text-transform: uppercase;
      letter-spacing: 0.05em;
      color: var(--text-muted);
      font-weight: 700;
    }}

    /* 4-Color Palette Tray */
    #tile-palette {{
      flex: 1;
      background-color: rgba(15, 23, 42, 0.6);
      border-radius: 12px;
      border: 1px solid var(--border-color);
      padding: 0.85rem;
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 0.75rem;
      overflow-y: auto;
    }}

    .palette-card {{
      background-color: var(--card-bg);
      border: 2px solid transparent;
      border-radius: 10px;
      padding: 0.6rem;
      display: flex;
      flex-direction: column;
      align-items: center;
      cursor: grab;
      transition: all 0.2s ease;
    }}

    .palette-card:hover {{
      transform: translateY(-3px);
      background-color: var(--card-hover);
      border-color: var(--accent-color);
      box-shadow: 0 6px 16px rgba(0,0,0,0.3);
    }}

    .palette-card svg {{
      width: 75px;
      height: 75px;
      pointer-events: none;
    }}

    .palette-card span {{
      font-size: 0.75rem;
      color: var(--text-main);
      margin-top: 0.3rem;
      font-weight: 600;
    }}

    /* Control Buttons */
    .controls-grid {{
      display: grid;
      grid-template-columns: repeat(2, 1fr);
      gap: 0.5rem;
    }}

    .btn {{
      background-color: var(--card-bg);
      color: var(--text-main);
      border: 1px solid var(--border-color);
      border-radius: 8px;
      padding: 0.6rem 0.75rem;
      font-size: 0.8rem;
      font-weight: 600;
      cursor: pointer;
      display: flex;
      align-items: center;
      justify-content: center;
      gap: 0.35rem;
      transition: all 0.2s ease;
    }}

    .btn:hover {{
      background-color: var(--card-hover);
      border-color: var(--text-muted);
    }}

    .btn.active {{
      background-color: rgba(99, 102, 241, 0.2);
      border-color: var(--accent-color);
      color: #a5b4fc;
    }}

    .btn-danger {{
      background-color: rgba(239, 68, 68, 0.15);
      border-color: rgba(239, 68, 68, 0.4);
      color: #fca5a5;
    }}

    .btn-danger:hover {{
      background-color: rgba(239, 68, 68, 0.3);
      border-color: var(--danger-color);
      color: #ffffff;
    }}

    /* Main Workspace Canvas */
    #workspace {{
      flex: 1;
      height: 100vh;
      position: relative;
      background-color: var(--bg-color);
      cursor: default;
    }}

    #workspace-svg {{
      width: 100%;
      height: 100%;
      display: block;
    }}

    .tile-polygon {{
      stroke: rgba(15, 23, 42, 0.8);
      stroke-width: 1.5;
      stroke-linejoin: round;
      cursor: pointer;
      transition: filter 0.15s ease;
    }}

    .tile-polygon:hover {{
      filter: brightness(1.2) drop-shadow(0 0 6px rgba(255,255,255,0.4));
    }}

    .tile-polygon.selected {{
      stroke: #ffffff;
      stroke-width: 2.5;
      filter: brightness(1.25) drop-shadow(0 0 10px rgba(99,102,241,0.8));
    }}

    /* Ghost Tile (Validation Drag Feedback) */
    .ghost-tile {{
      stroke-width: 2.0;
      stroke-linejoin: round;
      pointer-events: none;
    }}

    .ghost-tile.valid {{
      opacity: 0.85;
      stroke: #ffffff;
      filter: drop-shadow(0 0 8px rgba(16, 185, 129, 0.6));
    }}

    .ghost-tile.invalid {{
      fill: rgba(239, 68, 68, 0.45) !important;
      stroke: #ef4444 !important;
      stroke-width: 3.0 !important;
      filter: drop-shadow(0 0 12px rgba(239, 68, 68, 0.8));
    }}

    /* HUD Bar */
    #hud {{
      position: absolute;
      top: 1.25rem;
      right: 1.25rem;
      background: rgba(30, 41, 59, 0.85);
      backdrop-filter: blur(12px);
      border: 1px solid var(--border-color);
      border-radius: 10px;
      padding: 0.6rem 1rem;
      display: flex;
      align-items: center;
      gap: 1.25rem;
      font-size: 0.85rem;
      z-index: 5;
      box-shadow: var(--shadow-lg);
    }}

    #hud span {{
      display: flex;
      align-items: center;
      gap: 0.35rem;
    }}

    #hud strong {{
      color: #a5b4fc;
      font-weight: 700;
    }}

    /* Toast Notification Banner */
    #toast-banner {{
      position: absolute;
      bottom: 2rem;
      left: 50%;
      transform: translateX(-50%) translateY(100px);
      background-color: rgba(239, 68, 68, 0.95);
      color: white;
      font-size: 0.9rem;
      font-weight: 700;
      padding: 0.75rem 1.5rem;
      border-radius: 30px;
      box-shadow: 0 10px 25px rgba(239, 68, 68, 0.5);
      z-index: 100;
      opacity: 0;
      transition: transform 0.3s cubic-bezier(0.175, 0.885, 0.32, 1.275), opacity 0.3s ease;
      pointer-events: none;
      display: flex;
      align-items: center;
      gap: 0.5rem;
    }}

    #toast-banner.show {{
      transform: translateX(-50%) translateY(0);
      opacity: 1;
    }}

    /* Instructions Modal */
    .modal-overlay {{
      position: fixed;
      top: 0;
      left: 0;
      width: 100vw;
      height: 100vh;
      background-color: rgba(0, 0, 0, 0.7);
      backdrop-filter: blur(6px);
      display: flex;
      align-items: center;
      justify-content: center;
      z-index: 1000;
      opacity: 0;
      pointer-events: none;
      transition: opacity 0.25s ease;
    }}

    .modal-overlay.open {{
      opacity: 1;
      pointer-events: auto;
    }}

    .modal-card {{
      background-color: var(--panel-bg);
      border: 1px solid var(--border-color);
      border-radius: 16px;
      width: 520px;
      max-width: 90vw;
      padding: 1.75rem;
      box-shadow: var(--shadow-lg);
      display: flex;
      flex-direction: column;
      gap: 1rem;
    }}

    .modal-card h2 {{
      font-size: 1.35rem;
      color: #a5b4fc;
    }}

    .modal-card p {{
      font-size: 0.9rem;
      color: var(--text-muted);
      line-height: 1.5;
    }}

    .modal-card ul {{
      list-style-type: disc;
      padding-left: 1.25rem;
      font-size: 0.875rem;
      color: var(--text-main);
      display: flex;
      flex-direction: column;
      gap: 0.5rem;
    }}
  </style>
</head>
<body>

  <!-- Left Sidebar Controls -->
  <div id="sidebar">
    <div class="header-box">
      <div class="header-title">🧩 Spectre Monotile</div>
      <div class="subtitle">&Delta;<sub>2</sub> Jigsaw Puzzle</div>
    </div>

    <!-- Game Flow Primary Toggle Button -->
    <button id="btn-game-toggle" class="btn-primary-action" title="Toggle between solution view and active play mode">
      🎮 Start Game
    </button>

    <!-- PWA Install Prompt Button -->
    <button id="btn-pwa-install" class="btn-pwa-install" title="Install as Progressive Web App on Desktop or Mobile">
      📲 Install App
    </button>

    <div class="section-label">4-Color Tile Palette</div>
    <div id="tile-palette"></div>

    <div class="section-label">Board Controls</div>
    <div class="controls-grid">
      <button id="btn-boundary" class="btn active" title="Toggle 1D Delta_2 Boundary Frame">
        🖼️ Frame: ON
      </button>
      <button id="btn-snap" class="btn active" title="Toggle automatic vertex & edge snapping">
        ⚡ Snap: ON
      </button>
      <button id="btn-grid" class="btn active" title="Toggle background isometric grid">
        🌐 Grid: ON
      </button>
      <button id="btn-reset" class="btn" title="Reset View & Center Canvas">
        🎯 Reset View
      </button>
      <button id="btn-help" class="btn" title="View Instructions & Shortcuts">
        ❓ Rules / Help
      </button>
    </div>

    <button id="btn-clear" class="btn btn-danger" style="margin-top: auto;" title="Clear all placed tiles from board">
      🗑️ Clear Board
    </button>
  </div>

  <!-- Main Canvas Workspace -->
  <div id="workspace">
    <svg id="workspace-svg">
      <defs>
        <!-- Background Isometric Grid Pattern -->
        <pattern id="iso-grid" width="60" height="103.923" patternUnits="userSpaceOnUse">
          <path d="M 30 0 L 60 17.32 L 60 51.96 L 30 69.28 L 0 51.96 L 0 17.32 Z" fill="none" stroke="var(--grid-line)" stroke-width="0.8" />
          <path d="M 30 51.96 L 60 69.28 L 60 103.92 L 30 86.6 L 0 103.92 L 0 69.28 Z" fill="none" stroke="var(--grid-line)" stroke-width="0.8" />
        </pattern>
      </defs>

      <!-- Background Rect for Grid -->
      <rect id="bg-rect" width="100%" height="100%" fill="url(#iso-grid)" />

      <!-- Main Transformed Layer for Pan & Zoom -->
      <g id="viewport-layer">
        <g id="boundary-layer"></g>
        <g id="placed-tiles-group"></g>
        <g id="ghost-tile-group"></g>
      </g>
    </svg>

    <!-- Top Right HUD -->
    <div id="hud">
      <span>Tiles: <strong id="hud-tile-count">0</strong></span>
      <span>Angle: <strong id="hud-angle">0°</strong></span>
      <span>Snap: <strong id="hud-snap-status">Enabled</strong></span>
      <span>Status: <strong id="hud-valid-status" style="color: #10b981;">Valid</strong></span>
    </div>

    <!-- Error Toast Notification -->
    <div id="toast-banner">
      ⚠️ Invalid Placement: Must be inside boundary and cannot overlap existing tiles!
    </div>
  </div>

  <!-- Instructions Modal -->
  <div id="help-modal" class="modal-overlay">
    <div class="modal-card">
      <h2>Spectre Aperiodic Monotile Rules</h2>
      <p>Discovered in 2023 by Smith, Myers, Kaplan, and Goodman-Strauss, the <strong>Spectre</strong> is a strictly chiral aperiodic monotile (an "einstein") that tiles the 2D plane infinitely without repeating a periodic pattern.</p>
      <ul>
        <li><strong>Start Game / Solution Toggle:</strong> Click <strong>Start Game</strong> to start solving. Toggle <strong>Show Solution</strong> anytime to view the solution — your in-progress work is automatically stashed and restored when resuming!</li>
        <li><strong>PWA Offline Install:</strong> Install this application onto your desktop or mobile home screen via the <strong>📲 Install App</strong> button.</li>
        <li><strong>Drag & Drop:</strong> Drag tiles from the 4-color palette onto the board.</li>
        <li><strong>Rotation:</strong> Scroll the mouse wheel while dragging or hovering directly over a tile (or press <kbd>R</kbd>) to rotate in 30° steps.</li>
        <li><strong>Strict Boundary & Overlap Validation:</strong> Tiles turn RED if placed outside the $\Delta_2$ boundary or overlapping another tile. Invalid drops are rejected.</li>
        <li><strong>Canvas Pan & Zoom:</strong> Drag empty background space to pan; scroll on background to zoom in/out.</li>
      </ul>
      <button id="btn-close-modal" class="btn active" style="width: 100%; margin-top: 1rem;">Got it!</button>
    </div>
  </div>

  <!-- JavaScript Application Engine -->
  <script>
    (function() {{
      "use strict";

      // PWA Service Worker Registration
      if ('serviceWorker' in navigator) {{
        window.addEventListener('load', () => {{
          navigator.serviceWorker.register('./sw.js')
            .then(reg => console.log('PWA ServiceWorker registered with scope:', reg.scope))
            .catch(err => console.error('PWA ServiceWorker registration failed:', err));
        }});
      }}

      // 1. EXACT SPECTRE BASE GEOMETRY & CONSTANTS
      const SQRT3 = Math.sqrt(3);

      const SPECTRE_BASE_VERTICES = [
        {{ x: 0.0, y: 0.0 }},
        {{ x: 1.0, y: 0.0 }},
        {{ x: 1.5, y: -SQRT3 / 2 }},
        {{ x: 1.5 + SQRT3 / 2, y: 0.5 - SQRT3 / 2 }},
        {{ x: 1.5 + SQRT3 / 2, y: 1.5 - SQRT3 / 2 }},
        {{ x: 2.5 + SQRT3 / 2, y: 1.5 - SQRT3 / 2 }},
        {{ x: 3.0 + SQRT3 / 2, y: 1.5 }},
        {{ x: 3.0, y: 2.0 }},
        {{ x: 3.0 - SQRT3 / 2, y: 1.5 }},
        {{ x: 2.5 - SQRT3 / 2, y: 1.5 + SQRT3 / 2 }},
        {{ x: 1.5 - SQRT3 / 2, y: 1.5 + SQRT3 / 2 }},
        {{ x: 0.5 - SQRT3 / 2, y: 1.5 + SQRT3 / 2 }},
        {{ x: -SQRT3 / 2, y: 1.5 }},
        {{ x: 0.0, y: 1.0 }}
      ];

      const SCALE = 40;
      const SCALED_VERTICES = SPECTRE_BASE_VERTICES.map(v => ({{
        x: v.x * SCALE,
        y: -v.y * SCALE
      }}));

      const CENTROID = SCALED_VERTICES.reduce(
        (acc, v) => ({{ x: acc.x + v.x / 14, y: acc.y + v.y / 14 }}),
        {{ x: 0, y: 0 }}
      );

      const LOCAL_VERTICES = SCALED_VERTICES.map(v => ({{
        x: v.x - CENTROID.x,
        y: v.y - CENTROID.y
      }}));

      // 4-Color Distinct Harmonious Palette
      const TILE_COLORS = [
        {{ name: "Indigo", fill: "#6366f1", label: "01" }},
        {{ name: "Cyan", fill: "#06b6d4", label: "02" }},
        {{ name: "Amber", fill: "#f59e0b", label: "03" }},
        {{ name: "Rose", fill: "#f43f5e", label: "04" }}
      ];

      const DELTA2_BOUNDARY_VERTICES = {boundary_verts_json};
      const SOLVED_DELTA2_TILES = {solved_tiles_json};

      // 2. STATE MANAGEMENT
      const state = {{
        tiles: [], // Active board tiles: {{ id, x, y, rotationDeg, color }}
        solvedTiles: SOLVED_DELTA2_TILES,
        savedUserTiles: [], // Stashed player layout when viewing solution
        isGameActive: false,
        nextTileId: 1000,
        selectedTileId: null,
        snappingEnabled: true,
        boundaryVisible: true,
        gridVisible: true,
        snapDistanceThreshold: 18,

        // Dragging & Interaction
        dragMode: null, // 'PALETTE', 'PLACED', 'PAN'
        draggedTileId: null,
        dragPaletteColor: null,
        dragRotationDeg: 0,
        dragStartPos: {{ x: 0, y: 0 }},
        dragOffset: {{ x: 0, y: 0 }},

        // Viewport Pan & Zoom
        view: {{ x: 0, y: 0, zoom: 0.65 }}
      }};

      // 3. DOM ELEMENTS
      const workspaceSvg = document.getElementById('workspace-svg');
      const viewportLayer = document.getElementById('viewport-layer');
      const boundaryLayer = document.getElementById('boundary-layer');
      const placedTilesGroup = document.getElementById('placed-tiles-group');
      const ghostTileGroup = document.getElementById('ghost-tile-group');
      const tilePaletteContainer = document.getElementById('tile-palette');
      const bgRect = document.getElementById('bg-rect');

      const btnGameToggle = document.getElementById('btn-game-toggle');
      const btnPwaInstall = document.getElementById('btn-pwa-install');
      const btnSnap = document.getElementById('btn-snap');
      const btnBoundary = document.getElementById('btn-boundary');
      const btnGrid = document.getElementById('btn-grid');
      const btnReset = document.getElementById('btn-reset');
      const btnHelp = document.getElementById('btn-help');
      const btnClear = document.getElementById('btn-clear');
      const helpModal = document.getElementById('help-modal');
      const btnCloseModal = document.getElementById('btn-close-modal');
      const toastBanner = document.getElementById('toast-banner');

      const hudTileCount = document.getElementById('hud-tile-count');
      const hudAngle = document.getElementById('hud-angle');
      const hudSnapStatus = document.getElementById('hud-snap-status');
      const hudValidStatus = document.getElementById('hud-valid-status');

      // PWA Install Prompt Listener
      let deferredPrompt = null;
      window.addEventListener('beforeinstallprompt', (e) => {{
        e.preventDefault();
        deferredPrompt = e;
        if (btnPwaInstall) {{
          btnPwaInstall.style.display = 'flex';
        }}
      }});

      btnPwaInstall.addEventListener('click', async () => {{
        if (!deferredPrompt) return;
        deferredPrompt.prompt();
        const {{ outcome }} = await deferredPrompt.userChoice;
        if (outcome === 'accepted') {{
          btnPwaInstall.style.display = 'none';
        }}
        deferredPrompt = null;
      }});

      window.addEventListener('appinstalled', () => {{
        if (btnPwaInstall) btnPwaInstall.style.display = 'none';
        showToast("🎉 Spectre Δ₂ PWA installed successfully!");
      }});

      // 4. COMPUTATIONAL GEOMETRY & VALIDATION ENGINE
      function getRotatedVertices(rotationDeg) {{
        const rad = (rotationDeg * Math.PI) / 180;
        const cos = Math.cos(rad);
        const sin = Math.sin(rad);
        return LOCAL_VERTICES.map(v => ({{
          x: v.x * cos - v.y * sin,
          y: v.x * sin + v.y * cos
        }}));
      }}

      function getTransformedVertices(x, y, rotationDeg) {{
        const rotVerts = getRotatedVertices(rotationDeg);
        return rotVerts.map(v => ({{
          x: v.x + x,
          y: v.y + y
        }}));
      }}

      function verticesToSvgPoints(verts) {{
        return verts.map(v => `${{v.x.toFixed(2)}},${{v.y.toFixed(2)}}`).join(' ');
      }}

      // Point-in-Polygon (Ray casting)
      function pointInPolygon(pt, poly) {{
        let inside = false;
        const n = poly.length;
        for (let i = 0, j = n - 1; i < n; j = i++) {{
          const xi = poly[i].x, yi = poly[i].y;
          const xj = poly[j].x, yj = poly[j].y;
          const intersect = ((yi > pt.y) !== (yj > pt.y)) &&
              (pt.x < (xj - xi) * (pt.y - yi) / (yj - yi + 1e-12) + xi);
          if (intersect) inside = !inside;
        }}
        return inside;
      }}

      function pointOnSegment(pt, a, b, tol = 1e-3) {{
        const cross = (pt.y - a.y) * (b.x - a.x) - (pt.x - a.x) * (b.y - a.y);
        if (Math.abs(cross) > tol) return false;
        const dot = (pt.x - a.x) * (b.x - a.x) + (pt.y - a.y) * (b.y - a.y);
        if (dot < -tol) return false;
        const lenSq = (b.x - a.x) * (b.x - a.x) + (b.y - a.y) * (b.y - a.y);
        if (dot > lenSq + tol) return false;
        return true;
      }}

      function pointInOrOnPolygon(pt, poly) {{
        const n = poly.length;
        for (let i = 0; i < n; i++) {{
          if (pointOnSegment(pt, poly[i], poly[(i + 1) % n])) return true;
        }}
        return pointInPolygon(pt, poly);
      }}

      // Check if tile vertices & edge midpoints lie inside boundary
      function isTileInsideBoundary(tileVerts) {{
        const n = tileVerts.length;
        for (let i = 0; i < n; i++) {{
          if (!pointInOrOnPolygon(tileVerts[i], DELTA2_BOUNDARY_VERTICES)) return false;
          const mid = {{
            x: (tileVerts[i].x + tileVerts[(i + 1) % n].x) / 2,
            y: (tileVerts[i].y + tileVerts[(i + 1) % n].y) / 2
          }};
          if (!pointInOrOnPolygon(mid, DELTA2_BOUNDARY_VERTICES)) return false;
        }}
        return true;
      }}

      // Line Segment Intersection
      function segmentsCrossProperly(a, b, c, d) {{
        const cp1 = (b.x - a.x) * (c.y - a.y) - (b.y - a.y) * (c.x - a.x);
        const cp2 = (b.x - a.x) * (d.y - a.y) - (b.y - a.y) * (d.x - a.x);
        const cp3 = (d.x - c.x) * (a.y - c.y) - (d.y - c.y) * (a.x - c.x);
        const cp4 = (d.x - c.x) * (b.y - c.y) - (d.y - c.y) * (b.x - c.x);

        if (((cp1 > 1e-4 && cp2 < -1e-4) || (cp1 < -1e-4 && cp2 > 1e-4)) &&
            ((cp3 > 1e-4 && cp4 < -1e-4) || (cp3 < -1e-4 && cp4 > 1e-4))) {{
          return true;
        }}
        return false;
      }}

      // Check polygon overlap
      function doTilesOverlap(poly1, poly2) {{
        const n1 = poly1.length;
        const n2 = poly2.length;

        // Bounding box pre-check
        let minX1 = Infinity, maxX1 = -Infinity, minY1 = Infinity, maxY1 = -Infinity;
        let minX2 = Infinity, maxX2 = -Infinity, minY2 = Infinity, maxY2 = -Infinity;
        for (let i = 0; i < n1; i++) {{
          minX1 = Math.min(minX1, poly1[i].x); maxX1 = Math.max(maxX1, poly1[i].x);
          minY1 = Math.min(minY1, poly1[i].y); maxY1 = Math.max(maxY1, poly1[i].y);
        }}
        for (let j = 0; j < n2; j++) {{
          minX2 = Math.min(minX2, poly2[j].x); maxX2 = Math.max(maxX2, poly2[j].x);
          minY2 = Math.min(minY2, poly2[j].y); maxY2 = Math.max(maxY2, poly2[j].y);
        }}
        if (maxX1 < minX2 || maxX2 < minX1 || maxY1 < minY2 || maxY2 < minY1) return false;

        // Line segment intersection
        for (let i = 0; i < n1; i++) {{
          const a = poly1[i], b = poly1[(i + 1) % n1];
          for (let j = 0; j < n2; j++) {{
            const c = poly2[j], d = poly2[(j + 1) % n2];
            if (segmentsCrossProperly(a, b, c, d)) return true;
          }}
        }}

        // Interior point check
        const c1 = poly1.reduce((acc, v) => ({{ x: acc.x + v.x / n1, y: acc.y + v.y / n1 }}), {{ x: 0, y: 0 }});
        const c2 = poly2.reduce((acc, v) => ({{ x: acc.x + v.x / n2, y: acc.y + v.y / n2 }}), {{ x: 0, y: 0 }});

        if (pointInPolygon(c1, poly2) || pointInPolygon(c2, poly1)) return true;
        return false;
      }}

      // Validate candidate placement
      function validateTilePlacement(candVerts, ignoreTileId = null) {{
        if (!isTileInsideBoundary(candVerts)) {{
          return {{ valid: false, reason: "OUTSIDE_BOUNDARY" }};
        }}

        for (const tile of state.tiles) {{
          if (tile.id === ignoreTileId) continue;
          const placedVerts = getTransformedVertices(tile.x, tile.y, tile.rotationDeg);
          if (doTilesOverlap(candVerts, placedVerts)) {{
            return {{ valid: false, reason: "OVERLAP" }};
          }}
        }}

        return {{ valid: true }};
      }}

      // Convert Screen Pixel Coordinates to World SVG Coordinates
      function screenToWorldPos(screenX, screenY) {{
        const rect = workspaceSvg.getBoundingClientRect();
        const mouseSvgX = screenX - rect.left;
        const mouseSvgY = screenY - rect.top;
        return {{
          x: (mouseSvgX - state.view.x) / state.view.zoom,
          y: (mouseSvgY - state.view.y) / state.view.zoom
        }};
      }}

      function centerViewport() {{
        const rect = workspaceSvg.getBoundingClientRect();
        state.view.x = rect.width / 2;
        state.view.y = rect.height / 2;
        state.view.zoom = 0.65;
        updateViewportTransform();
      }}

      function updateViewportTransform() {{
        viewportLayer.setAttribute('transform', `translate(${{state.view.x}}, ${{state.view.y}}) scale(${{state.view.zoom}})`);
      }}

      // Toast Notification
      let toastTimeout = null;
      function showToast(msg) {{
        toastBanner.textContent = msg;
        toastBanner.classList.add('show');
        if (toastTimeout) clearTimeout(toastTimeout);
        toastTimeout = setTimeout(() => {{
          toastBanner.classList.remove('show');
        }}, 2800);
      }}

      // 5. SNAPPING ENGINE
      function findSnapPosition(targetX, targetY, rotationDeg, ignoreTileId = null) {{
        if (!state.snappingEnabled) {{
          return {{ x: targetX, y: targetY, snapped: false }};
        }}

        const candidateVerts = getTransformedVertices(targetX, targetY, rotationDeg);
        let bestSnapOffset = {{ x: 0, y: 0 }};
        let foundSnap = false;
        let maxMatchedVerts = 0;
        let minSingleDist = Infinity;

        const existingVertsList = [];
        for (const existingTile of state.tiles) {{
          if (existingTile.id === ignoreTileId) continue;
          const evs = getTransformedVertices(existingTile.x, existingTile.y, existingTile.rotationDeg);
          existingVertsList.push(...evs);
        }}

        if (state.boundaryVisible && DELTA2_BOUNDARY_VERTICES) {{
          existingVertsList.push(...DELTA2_BOUNDARY_VERTICES);
        }}

        if (existingVertsList.length === 0) {{
          return {{ x: targetX, y: targetY, snapped: false }};
        }}

        for (let i = 0; i < candidateVerts.length; i++) {{
          const cVert = candidateVerts[i];
          for (let j = 0; j < existingVertsList.length; j++) {{
            const eVert = existingVertsList[j];
            const dist = Math.hypot(cVert.x - eVert.x, cVert.y - eVert.y);
            if (dist > state.snapDistanceThreshold) continue;

            const offsetX = eVert.x - cVert.x;
            const offsetY = eVert.y - cVert.y;

            let matchedCount = 0;
            for (let k = 0; k < candidateVerts.length; k++) {{
              const testX = candidateVerts[k].x + offsetX;
              const testY = candidateVerts[k].y + offsetY;
              for (let m = 0; m < existingVertsList.length; m++) {{
                const d = Math.hypot(testX - existingVertsList[m].x, testY - existingVertsList[m].y);
                if (d < 3.0) {{
                  matchedCount++;
                  break;
                }}
              }}
            }}

            if (matchedCount > maxMatchedVerts || (matchedCount === maxMatchedVerts && dist < minSingleDist)) {{
              maxMatchedVerts = matchedCount;
              minSingleDist = dist;
              bestSnapOffset = {{ x: offsetX, y: offsetY }};
              foundSnap = true;
            }}
          }}
        }}

        if (foundSnap) {{
          return {{
            x: targetX + bestSnapOffset.x,
            y: targetY + bestSnapOffset.y,
            snapped: true
          }};
        }}

        return {{ x: targetX, y: targetY, snapped: false }};
      }}

      // 6. RENDERERS
      function renderBoundaryFrame() {{
        if (!boundaryLayer) return;
        boundaryLayer.innerHTML = '';
        if (!state.boundaryVisible || typeof DELTA2_BOUNDARY_VERTICES === 'undefined') return;

        const path = document.createElementNS('http://www.w3.org/2000/svg', 'path');
        const pathD = "M " + DELTA2_BOUNDARY_VERTICES.map(v => `${{v.x.toFixed(2)}},${{v.y.toFixed(2)}}`).join(" L ") + " Z";
        path.setAttribute('d', pathD);
        path.setAttribute('id', 'delta2-boundary-path');
        path.setAttribute('fill', 'rgba(56, 189, 248, 0.06)');
        path.setAttribute('stroke', '#38bdf8');
        path.setAttribute('stroke-width', '2.5');
        path.setAttribute('stroke-linejoin', 'round');
        path.setAttribute('filter', 'drop-shadow(0 0 10px rgba(56, 189, 248, 0.35))');

        boundaryLayer.appendChild(path);
      }}

      function renderPalette() {{
        tilePaletteContainer.innerHTML = '';
        const miniSvgPoints = verticesToSvgPoints(LOCAL_VERTICES.map(v => ({{ x: v.x * 0.3, y: v.y * 0.3 }})));

        TILE_COLORS.forEach(colorItem => {{
          const card = document.createElement('div');
          card.className = 'palette-card';
          card.dataset.color = colorItem.fill;

          card.innerHTML = `
            <svg viewBox="-45 -45 90 90">
              <polygon points="${{miniSvgPoints}}" fill="${{colorItem.fill}}" stroke="#0f172a" stroke-width="1.5" />
            </svg>
            <span>${{colorItem.name}}</span>
          `;

          card.addEventListener('mousedown', (e) => {{
            e.preventDefault();
            const worldPos = screenToWorldPos(e.clientX, e.clientY);
            state.dragMode = 'PALETTE';
            state.dragPaletteColor = colorItem.fill;
            state.dragRotationDeg = 0;
            state.dragStartPos = worldPos;
            state.dragOffset = {{ x: 0, y: 0 }};
            updateGhostTile(worldPos.x, worldPos.y, 0, colorItem.fill);
            updateHUD();
          }});

          tilePaletteContainer.appendChild(card);
        }});
      }}

      function renderPlacedTiles() {{
        placedTilesGroup.innerHTML = '';
        state.tiles.forEach(tile => {{
          const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
          const verts = getTransformedVertices(tile.x, tile.y, tile.rotationDeg);
          polygon.setAttribute('points', verticesToSvgPoints(verts));
          polygon.setAttribute('fill', tile.color);
          polygon.setAttribute('class', `tile-polygon ${{tile.id === state.selectedTileId ? 'selected' : ''}}`);
          polygon.dataset.id = tile.id;

          polygon.addEventListener('mousedown', (e) => {{
            e.stopPropagation();
            e.preventDefault();
            const worldPos = screenToWorldPos(e.clientX, e.clientY);
            state.selectedTileId = tile.id;
            state.dragMode = 'PLACED';
            state.draggedTileId = tile.id;
            state.dragRotationDeg = tile.rotationDeg;
            state.dragOffset = {{
              x: worldPos.x - tile.x,
              y: worldPos.y - tile.y
            }};
            updateGhostTile(tile.x, tile.y, tile.rotationDeg, tile.color);
            renderPlacedTiles();
            updateHUD();
          }});

          placedTilesGroup.appendChild(polygon);
        }});

        hudTileCount.textContent = state.tiles.length;
      }}

      function updateGhostTile(x, y, rotationDeg, color) {{
        ghostTileGroup.innerHTML = '';
        if (state.dragMode === null) return;

        const snapResult = findSnapPosition(x, y, rotationDeg, state.draggedTileId);
        const finalX = snapResult.x;
        const finalY = snapResult.y;

        const verts = getTransformedVertices(finalX, finalY, rotationDeg);
        const valResult = validateTilePlacement(verts, state.draggedTileId);

        const polygon = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        polygon.setAttribute('points', verticesToSvgPoints(verts));
        polygon.setAttribute('fill', color);
        polygon.setAttribute('class', `ghost-tile ${{valResult.valid ? 'valid' : 'invalid'}}`);

        ghostTileGroup.appendChild(polygon);

        if (!valResult.valid) {{
          hudValidStatus.textContent = valResult.reason === "OUTSIDE_BOUNDARY" ? "Outside Boundary" : "Overlapping";
          hudValidStatus.style.color = "#ef4444";
        }} else {{
          hudValidStatus.textContent = snapResult.snapped ? "Snapped Valid" : "Valid";
          hudValidStatus.style.color = "#10b981";
        }}
      }}

      function updateHUD() {{
        hudAngle.textContent = `${{(state.dragRotationDeg % 360 + 360) % 360}}°`;
        hudSnapStatus.textContent = state.snappingEnabled ? 'Enabled' : 'Disabled';
        hudSnapStatus.style.color = state.snappingEnabled ? '#10b981' : '#ef4444';
      }}

      // 7. EVENT HANDLERS & INTERACTIONS
      function handleMouseMove(e) {{
        if (state.dragMode === 'PAN') {{
          const dx = e.clientX - state.dragStartPos.x;
          const dy = e.clientY - state.dragStartPos.y;
          state.view.x += dx;
          state.view.y += dy;
          state.dragStartPos = {{ x: e.clientX, y: e.clientY }};
          updateViewportTransform();
          return;
        }}

        if (state.dragMode === 'PALETTE' || state.dragMode === 'PLACED') {{
          const worldPos = screenToWorldPos(e.clientX, e.clientY);
          const targetX = worldPos.x - state.dragOffset.x;
          const targetY = worldPos.y - state.dragOffset.y;
          const color = state.dragMode === 'PALETTE' 
            ? state.dragPaletteColor 
            : state.tiles.find(t => t.id === state.draggedTileId)?.color;

          updateGhostTile(targetX, targetY, state.dragRotationDeg, color);
        }}
      }}

      function handleMouseUp(e) {{
        if (state.dragMode === 'PALETTE' || state.dragMode === 'PLACED') {{
          const worldPos = screenToWorldPos(e.clientX, e.clientY);
          const rawX = worldPos.x - state.dragOffset.x;
          const rawY = worldPos.y - state.dragOffset.y;

          const snapResult = findSnapPosition(rawX, rawY, state.dragRotationDeg, state.draggedTileId);
          const candidateVerts = getTransformedVertices(snapResult.x, snapResult.y, state.dragRotationDeg);

          const valResult = validateTilePlacement(candidateVerts, state.draggedTileId);

          if (!valResult.valid) {{
            if (valResult.reason === "OUTSIDE_BOUNDARY") {{
              showToast("⚠️ Invalid Placement: Tile must be strictly inside boundary!");
            }} else {{
              showToast("⚠️ Invalid Placement: Tile overlaps an existing placed tile!");
            }}
          }} else {{
            if (state.dragMode === 'PALETTE') {{
              const newTile = {{
                id: state.nextTileId++,
                x: snapResult.x,
                y: snapResult.y,
                rotationDeg: (state.dragRotationDeg % 360 + 360) % 360,
                color: state.dragPaletteColor
              }};
              state.tiles.push(newTile);
              state.selectedTileId = newTile.id;
            }} else if (state.dragMode === 'PLACED') {{
              const tile = state.tiles.find(t => t.id === state.draggedTileId);
              if (tile) {{
                tile.x = snapResult.x;
                tile.y = snapResult.y;
                tile.rotationDeg = (state.dragRotationDeg % 360 + 360) % 360;
              }}
            }}
          }}

          ghostTileGroup.innerHTML = '';
          renderPlacedTiles();
        }}

        state.dragMode = null;
        state.draggedTileId = null;
      }}

      function handleWheel(e) {{
        const hoveredTileElement = e.target.closest ? e.target.closest('.tile-polygon') : null;
        const hoveredTileId = hoveredTileElement ? parseInt(hoveredTileElement.dataset.id, 10) : null;

        if (state.dragMode === 'PALETTE' || state.dragMode === 'PLACED') {{
          e.preventDefault();
          const step = e.deltaY < 0 ? 30 : -30;
          state.dragRotationDeg = (state.dragRotationDeg + step) % 360;
          const worldPos = screenToWorldPos(e.clientX, e.clientY);
          const targetX = worldPos.x - state.dragOffset.x;
          const targetY = worldPos.y - state.dragOffset.y;
          const color = state.dragMode === 'PALETTE' 
            ? state.dragPaletteColor 
            : state.tiles.find(t => t.id === state.draggedTileId)?.color;

          updateGhostTile(targetX, targetY, state.dragRotationDeg, color);
          updateHUD();
        }} else if (hoveredTileId !== null) {{
          e.preventDefault();
          const tile = state.tiles.find(t => t.id === hoveredTileId);
          if (tile) {{
            const step = e.deltaY < 0 ? 30 : -30;
            const newRot = (tile.rotationDeg + step) % 360;
            const testVerts = getTransformedVertices(tile.x, tile.y, newRot);
            if (validateTilePlacement(testVerts, tile.id).valid) {{
              tile.rotationDeg = newRot;
              state.dragRotationDeg = tile.rotationDeg;
              renderPlacedTiles();
              updateHUD();
            }} else {{
              showToast("⚠️ Rotation blocked: Would overlap or extend outside boundary!");
            }}
          }}
        }} else {{
          e.preventDefault();
          const zoomFactor = e.deltaY < 0 ? 1.1 : 0.9;
          const mouseX = e.clientX;
          const mouseY = e.clientY;

          state.view.x = mouseX - (mouseX - state.view.x) * zoomFactor;
          state.view.y = mouseY - (mouseY - state.view.y) * zoomFactor;
          state.view.zoom *= zoomFactor;
          updateViewportTransform();
        }}
      }}

      function handleKeyDown(e) {{
        if (e.key === 'r' || e.key === 'R') {{
          if (state.dragMode === 'PALETTE' || state.dragMode === 'PLACED') {{
            state.dragRotationDeg = (state.dragRotationDeg + 30) % 360;
            updateHUD();
          }} else if (state.selectedTileId !== null) {{
            const tile = state.tiles.find(t => t.id === state.selectedTileId);
            if (tile) {{
              const newRot = (tile.rotationDeg + 30) % 360;
              const testVerts = getTransformedVertices(tile.x, tile.y, newRot);
              if (validateTilePlacement(testVerts, tile.id).valid) {{
                tile.rotationDeg = newRot;
                renderPlacedTiles();
              }} else {{
                showToast("⚠️ Rotation blocked: Would overlap or extend outside boundary!");
              }}
            }}
          }}
        }} else if (e.key === 'Delete' || e.key === 'Backspace') {{
          if (state.selectedTileId !== null) {{
            state.tiles = state.tiles.filter(t => t.id !== state.selectedTileId);
            state.selectedTileId = null;
            renderPlacedTiles();
          }}
        }}
      }}

      // Canvas background panning
      workspaceSvg.addEventListener('mousedown', (e) => {{
        if (e.target === workspaceSvg || e.target === bgRect) {{
          state.selectedTileId = null;
          renderPlacedTiles();
          state.dragMode = 'PAN';
          state.dragStartPos = {{ x: e.clientX, y: e.clientY }};
        }}
      }});

      window.addEventListener('mousemove', handleMouseMove);
      window.addEventListener('mouseup', handleMouseUp);
      workspaceSvg.addEventListener('wheel', handleWheel, {{ passive: false }});
      window.addEventListener('keydown', handleKeyDown);

      // GAME TOGGLE LISTENER (With In-Progress Board State Stashing)
      btnGameToggle.addEventListener('click', () => {{
        if (!state.isGameActive) {{
          if (state.savedUserTiles.length > 0) {{
            state.tiles = JSON.parse(JSON.stringify(state.savedUserTiles));
            state.savedUserTiles = [];
            state.isGameActive = true;
            btnGameToggle.textContent = '💡 Show Solution';
            btnGameToggle.style.background = 'linear-gradient(135deg, #10b981, #059669)';
            showToast("🎮 Resumed in-progress game! Restored your placed tiles.");
          }} else {{
            state.tiles = [];
            state.selectedTileId = null;
            state.isGameActive = true;
            btnGameToggle.textContent = '💡 Show Solution';
            btnGameToggle.style.background = 'linear-gradient(135deg, #10b981, #059669)';
            showToast("🎮 Fresh Game Started! Drag tiles into the frame.");
          }}
        }} else {{
          state.savedUserTiles = JSON.parse(JSON.stringify(state.tiles));
          state.tiles = JSON.parse(JSON.stringify(state.solvedTiles));
          state.selectedTileId = null;
          state.isGameActive = false;
          btnGameToggle.textContent = '🙈 Hide Solution';
          btnGameToggle.style.background = 'linear-gradient(135deg, #6366f1, #4f46e5)';
          showToast("💡 Solved layout displayed! Click Hide Solution to resume playing.");
        }}
        renderPlacedTiles();
      }});

      // UI Button Listeners
      btnBoundary.addEventListener('click', () => {{
        state.boundaryVisible = !state.boundaryVisible;
        btnBoundary.classList.toggle('active', state.boundaryVisible);
        btnBoundary.textContent = `🖼️ Frame: ${{state.boundaryVisible ? 'ON' : 'OFF'}}`;
        renderBoundaryFrame();
      }});

      btnSnap.addEventListener('click', () => {{
        state.snappingEnabled = !state.snappingEnabled;
        btnSnap.classList.toggle('active', state.snappingEnabled);
        btnSnap.textContent = `⚡ Snap: ${{state.snappingEnabled ? 'ON' : 'OFF'}}`;
        updateHUD();
      }});

      btnGrid.addEventListener('click', () => {{
        state.gridVisible = !state.gridVisible;
        btnGrid.classList.toggle('active', state.gridVisible);
        btnGrid.textContent = `🌐 Grid: ${{state.gridVisible ? 'ON' : 'OFF'}}`;
        bgRect.style.display = state.gridVisible ? 'block' : 'none';
      }});

      btnReset.addEventListener('click', centerViewport);

      btnClear.addEventListener('click', () => {{
        if (state.tiles.length === 0 || confirm("Clear all tiles from board?")) {{
          state.tiles = [];
          state.savedUserTiles = [];
          state.selectedTileId = null;
          if (!state.isGameActive) {{
            state.isGameActive = true;
            btnGameToggle.textContent = '💡 Show Solution';
            btnGameToggle.style.background = 'linear-gradient(135deg, #10b981, #059669)';
          }}
          renderPlacedTiles();
        }}
      }});

      btnHelp.addEventListener('click', () => helpModal.classList.add('open'));
      btnCloseModal.addEventListener('click', () => helpModal.classList.remove('open'));
      helpModal.addEventListener('click', (e) => {{
        if (e.target === helpModal) helpModal.classList.remove('open');
      }});

      // INITIALIZATION
      function init() {{
        centerViewport();
        renderBoundaryFrame();
        renderPalette();

        state.tiles = JSON.parse(JSON.stringify(state.solvedTiles));
        state.isGameActive = false;
        btnGameToggle.textContent = '🎮 Start Game';
        btnGameToggle.style.background = 'linear-gradient(135deg, #6366f1, #4f46e5)';

        renderPlacedTiles();
        updateHUD();
      }}

      window.addEventListener('load', init);
    }})();
  </script>
</body>
</html>
'''

with open('index.html', 'w') as f:
    f.write(html_content)

print("Generated PWA SPA index.html successfully!")
