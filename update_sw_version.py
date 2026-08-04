#!/usr/bin/env python3
import os
import re
import time

def update_sw_cache_name():
    version = os.getenv('BUILD_VERSION') or f"v1.0.{int(time.time() * 1000)}"
    cache_name = f"spectre-puzzle-pwa-{version}"
    
    paths = ['puzzle/sw.js', 'docs/sw.js']
    for p in paths:
        if os.path.exists(p):
            with open(p, 'r') as f:
                content = f.read()
            content = re.sub(r"const CACHE_NAME = '.*?';", f"const CACHE_NAME = '{cache_name}';", content)
            with open(p, 'w') as f:
                f.write(content)
            print(f"Updated {p} CACHE_NAME -> {cache_name}")

if __name__ == '__main__':
    update_sw_cache_name()
