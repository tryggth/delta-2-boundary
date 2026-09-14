#!/usr/bin/env python3
import os
import re
import time

def update_version():
    build_num = os.getenv('BUILD_VERSION')
    if build_num:
        version_str = build_num if build_num.startswith('v') else f"v{build_num}"
    else:
        version_str = f"v1.0.{int(time.time() * 1000)}"
        
    cache_name = f"spectre-puzzle-pwa-{version_str}"
    
    # 1. Update Service Workers
    sw_paths = ['puzzle/sw.js', 'docs/sw.js']
    for p in sw_paths:
        if os.path.exists(p):
            with open(p, 'r') as f:
                content = f.read()
            content = re.sub(r"const CACHE_NAME = '.*?';", f"const CACHE_NAME = '{cache_name}';", content)
            with open(p, 'w') as f:
                f.write(content)
            print(f"Updated {p} CACHE_NAME -> {cache_name}")

    # 2. Update HTML files version badges
    html_paths = ['puzzle/index.html', 'docs/index.html']
    for p in html_paths:
        if os.path.exists(p):
            with open(p, 'r') as f:
                content = f.read()

            # Update CSS badge if needed
            css_badge = """    .version-badge {
      font-size: 0.7rem;
      font-weight: 600;
      color: var(--accent-color);
      background-color: rgba(99, 102, 241, 0.15);
      border: 1px solid rgba(99, 102, 241, 0.35);
      padding: 0.1rem 0.45rem;
      border-radius: 6px;
      margin-left: 0.35rem;
      vertical-align: middle;
      display: inline-block;
    }"""
            if '.version-badge {' not in content:
              content = content.replace('.btn-pwa-install:hover {', css_badge + '\n    .btn-pwa-install:hover {')

            # Update subtitle version badge
            old_subtitle = '<div class="subtitle">&Delta;<sub>2</sub> Jigsaw Puzzle</div>'
            new_subtitle = f'<div class="subtitle">&Delta;<sub>2</sub> Jigsaw Puzzle <span id="app-version" class="version-badge">{version_str}</span></div>'
            
            if 'id="app-version"' in content:
                content = re.sub(r'<span id="app-version" class="version-badge">.*?</span>', f'<span id="app-version" class="version-badge">{version_str}</span>', content)
            else:
                content = content.replace(old_subtitle, new_subtitle)

            # Update JS constant
            if 'const APP_VERSION =' in content:
                content = re.sub(r'const APP_VERSION = ".*?";', f'const APP_VERSION = "{version_str}";', content)
            else:
                content = content.replace('"use strict";', f'"use strict";\n      const APP_VERSION = "{version_str}";')

            with open(p, 'w') as f:
                f.write(content)
            print(f"Updated {p} APP_VERSION -> {version_str}")

if __name__ == '__main__':
    update_version()
