/**
 * AFJEN Compiler - web server (Node.js + Express)
 *
 * Serves the browser front end in ./public and exposes a small JSON API. All language work is done by the
 * real AFJEN engine written in Python: this server starts bridge.py once and exchanges one JSON line per
 * request with it, so the web app and the desktop app always behave the same.
 *
 *   npm install
 *   npm start            ->  http://localhost:3000
 */

const express = require("express");
const path = require("path");
const { spawn } = require("child_process");
const readline = require("readline");

const PORT = process.env.PORT || 3000;

// Find a working Python: AFJEN_PYTHON, then python, python3, and finally the Windows launcher "py -3".
function findPython() {
  const { spawnSync } = require("child_process");
  const candidates = [];
  if (process.env.AFJEN_PYTHON) candidates.push([process.env.AFJEN_PYTHON, []]);
  candidates.push(["python", []], ["python3", []], ["py", ["-3"]]);
  for (const [cmd, prefix] of candidates) {
    const probe = spawnSync(cmd, [...prefix, "--version"]);
    if (!probe.error && probe.status === 0) return { cmd, prefix };
  }
  throw new Error("Python 3 was not found. Install it from python.org or set AFJEN_PYTHON to its path.");
}

// ------------------------------------------------------------------ Python bridge --
class PythonBridge {
  constructor() {
    this.pending = new Map();
    this.nextId = 1;
    this.start();
  }

  start() {
    const script = path.join(__dirname, "bridge.py");
    this.python = this.python || findPython();
    this.proc = spawn(this.python.cmd, [...this.python.prefix, script], { stdio: ["pipe", "pipe", "inherit"] });
    this.proc.on("error", (err) => this.failAll(`Could not start Python (${this.python.cmd}): ${err.message}`));
    this.proc.on("exit", () => this.failAll("The Python engine stopped"));
    readline.createInterface({ input: this.proc.stdout }).on("line", (line) => {
      let reply;
      try { reply = JSON.parse(line); } catch { return; }
      const waiting = this.pending.get(reply.id);
      if (!waiting) return;
      this.pending.delete(reply.id);
      reply.ok ? waiting.resolve(reply.result) : waiting.reject(new Error(reply.error || "Engine error"));
    });
  }

  failAll(message) {
    for (const { reject } of this.pending.values()) reject(new Error(message));
    this.pending.clear();
  }

  call(op, args = {}) {
    return new Promise((resolve, reject) => {
      if (!this.proc || this.proc.exitCode !== null) this.start();
      const id = this.nextId++;
      const timer = setTimeout(() => {
        this.pending.delete(id);
        reject(new Error("The Python engine took too long to answer"));
      }, 15000);
      this.pending.set(id, {
        resolve: (v) => { clearTimeout(timer); resolve(v); },
        reject: (e) => { clearTimeout(timer); reject(e); },
      });
      this.proc.stdin.write(JSON.stringify({ id, op, args }) + "\n");
    });
  }

  stop() {
    if (this.proc) this.proc.kill();
  }
}

// -------------------------------------------------------------------------- app --
function createApp(bridge) {
  const app = express();
  app.use(express.json({ limit: "1mb" }));
  app.use(express.static(path.join(__dirname, "public")));

  const route = (method, url, op, pick = (req) => req.body) =>
    app[method](url, async (req, res) => {
      try {
        res.json(await bridge.call(op, pick(req)));
      } catch (err) {
        res.status(500).json({ ok: false, message: err.message });
      }
    });

  route("get", "/api/health", "health", () => ({}));
  route("post", "/api/analyze", "analyze");
  route("get", "/api/dictionary", "dictionary", () => ({}));
  route("post", "/api/dictionary", "addWord");
  route("delete", "/api/dictionary", "removeWord");
  route("get", "/api/statements", "statements", () => ({}));
  route("post", "/api/statements", "addStatement");
  route("delete", "/api/statements", "removeStatement");
  route("get", "/api/insights", "insights", () => ({}));
  return app;
}

if (require.main === module) {
  const bridge = new PythonBridge();
  const app = createApp(bridge);
  const server = app.listen(PORT, () => {
    console.log(`AFJEN Compiler web app running at http://localhost:${PORT}`);
  });
  const shutdown = () => { bridge.stop(); server.close(() => process.exit(0)); };
  process.on("SIGINT", shutdown);
  process.on("SIGTERM", shutdown);
}

module.exports = { PythonBridge, createApp };
