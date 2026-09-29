"""
Python bridge for the AFJEN web app.

The Node.js server (server.js) starts this script once and talks to it with one JSON object per line:
    request : {"id": 1, "op": "analyze", "args": {"text": "You dey ok?"}}
    response: {"id": 1, "ok": true, "result": {...}}
so the web front end always uses the real AFJEN engine (lexer, LL(1) parser, translator, dictionary).
"""

import json
import os
import sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))
sys.stdout.reconfigure(encoding="utf-8")
sys.stdin.reconfigure(encoding="utf-8")

import engine  # noqa: E402

OPS = {
    "analyze": lambda a: engine.analyze(a.get("text", "")),
    "dictionary": lambda a: engine.dictionary_rows(),
    "addWord": lambda a: engine.add_word(a.get("word", ""), a.get("type", "noun"), a.get("english", ""),
                                         a.get("french", ""), a.get("gender", "m")),
    "removeWord": lambda a: engine.remove_word(a.get("word", "")),
    "statements": lambda a: engine.statement_rows(),
    "addStatement": lambda a: engine.add_statement(a.get("text", ""), a.get("english", ""), a.get("french", ""),
                                                   a.get("topic", "")),
    "removeStatement": lambda a: engine.remove_statement(a.get("text", "")),
    "insights": lambda a: engine.insights(),
    "health": lambda a: {"status": "ok", "python": sys.version.split()[0]},
}


def main():
    for line in sys.stdin:
        line = line.strip()
        if not line:
            continue
        try:
            request = json.loads(line)
            result = OPS[request["op"]](request.get("args") or {})
            reply = {"id": request.get("id"), "ok": True, "result": result}
        except Exception as exc:  # never let one bad request kill the bridge
            reply = {"id": (locals().get("request") or {}).get("id"), "ok": False, "error": str(exc)}
        sys.stdout.write(json.dumps(reply, ensure_ascii=False) + "\n")
        sys.stdout.flush()


if __name__ == "__main__":
    main()
