#!/usr/bin/env python3
"""
One-command launcher for the AFJEN web app (JavaScript + Node.js + Express).

    python run_web.py

It finds Node.js, installs the web dependencies the first time, starts the server on a free port with the same
Python you used to run this script, and opens the browser. Press Ctrl+C to stop.
"""

import os
import shutil
import socket
import subprocess
import sys
import threading
import time
import webbrowser

ROOT = os.path.dirname(os.path.abspath(__file__))
WEB = os.path.join(ROOT, "web")


def find_tool(name):
    """Locate node / npm, also in the default Windows install folders (the PATH may not be updated yet)."""
    found = shutil.which(name)
    if found:
        return found
    for base in (os.environ.get("ProgramFiles", r"C:\Program Files"), os.environ.get("ProgramFiles(x86)", r"C:\Program Files (x86)"),
                 os.path.join(os.environ.get("LOCALAPPDATA", ""), "Programs")):
        for ext in (".cmd", ".exe", ""):
            candidate = os.path.join(base, "nodejs", name + ext)
            if os.path.isfile(candidate):
                return candidate
    return None


def free_port(start=3000):
    for port in range(start, start + 30):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) != 0:
                return port
    return start


def open_when_ready(port):
    url = f"http://localhost:{port}"
    for _ in range(60):
        with socket.socket() as s:
            if s.connect_ex(("127.0.0.1", port)) == 0:
                webbrowser.open(url)
                return
        time.sleep(0.5)


def main():
    node, npm = find_tool("node"), find_tool("npm")
    if not node or not npm:
        print("Node.js was not found on this computer.\n"
              "  1. Install the LTS version from https://nodejs.org\n"
              "  2. Close and reopen the terminal (or VS Code)\n"
              "  3. Run:  python run_web.py")
        return 1
    print(f"Node.js: {node}")

    if not os.path.isdir(os.path.join(WEB, "node_modules", "express")):
        print("First run: installing the web dependencies (needs internet, takes about a minute)...")
        result = subprocess.run([npm, "install"], cwd=WEB, shell=(os.name == "nt"))
        if result.returncode != 0:
            print("npm install failed. Check your internet connection, then run this command again.")
            return result.returncode

    port = free_port(int(os.environ.get("PORT", "3000")))
    env = dict(os.environ, PORT=str(port), AFJEN_PYTHON=sys.executable)
    print(f"Starting AFJEN Compiler on http://localhost:{port}   (press Ctrl+C to stop)")
    if not os.environ.get("AFJEN_NO_BROWSER"):
        threading.Thread(target=open_when_ready, args=(port,), daemon=True).start()
    try:
        return subprocess.run([node, "server.js"], cwd=WEB, env=env).returncode
    except KeyboardInterrupt:
        print("\nStopped.")
        return 0


if __name__ == "__main__":
    sys.exit(main())
