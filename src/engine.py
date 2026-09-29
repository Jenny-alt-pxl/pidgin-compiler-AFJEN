"""
AFJEN engine - one JSON-friendly entry point to the whole toolchain
CS4110 - Compiler Construction

Used by the web front end (web/server.js talks to web/bridge.py, which calls this module) and by the
desktop GUI. Nothing here refuses input: any text is translated and analysed.
"""

import re
from typing import Dict, List, Tuple

import dictionary as D
import statements as S
import userdict
from lexical_analyzer import TokenType
from parser import analyze_robust
from semantic_analyzer import SemanticAnalyzer
from translator import translate, translate_ex

_semantic = SemanticAnalyzer()
_bank = D.WordBank()


def translate_all(text: str, lang: str) -> Tuple[str, str, List[str]]:
    """Translate any text: verified statements first, expressions and the rule engine for the rest.
    Returns (translation, method, unknown_words) with method in verified / partial / automatic."""
    whole = translate(text, lang)
    if whole[1] == "verified":
        return whole[0], "verified", []
    pieces, methods, unknown = [], [], []
    for line in [ln for ln in text.splitlines() if ln.strip()]:
        hit = translate(line, lang)
        if hit[1] == "verified":
            pieces.append(hit[0])
            methods.append("verified")
            continue
        for sentence in re.split(r"(?<=[.!?])\s+", line.strip()):
            if not sentence.strip():
                continue
            r = translate_ex(sentence, lang)
            pieces.append(r["text"])
            methods.append(r["method"])
            unknown += r["unknown"]
    method = "verified" if methods and all(m == "verified" for m in methods) else (
        "partial" if "verified" in methods else "automatic")
    return " ".join(pieces), method, sorted(set(unknown))


def analyze(text: str) -> Dict[str, object]:
    """Full analysis of any text: both translations, tokens, sentence structure, topic and intent."""
    text = (text or "").strip()
    if not text:
        return {"empty": True}
    translations = {}
    for lang in ("en", "fr"):
        out, method, unknown = translate_all(text, lang)
        translations[lang] = {"text": out, "method": method, "unknown": unknown}
    result = analyze_robust(text)
    tokens = [{"value": t.value, "type": t.type.name, "pos": f"{t.line}:{t.column}"} for t in result["tokens"]]
    sentences = [{
        "text": s["text"], "kind": s["kind"], "matched": s["matched"], "total": s["total"],
        "trees": [tree.to_dict() for tree in s["trees"]],
        "fragments": [w for w, _err in s["fragments"]],
    } for s in result["sentences"]]
    words = [t.value for t in result["tokens"]
             if t.type not in (TokenType.PUNCTUATION, TokenType.CONNECTOR) or t.value.lower() in ("and", "but", "or")]
    _bank.record(words)
    sem = _semantic.analyze(text)
    return {
        "empty": False, "translations": translations, "tokens": tokens, "sentences": sentences,
        "coverage": result["coverage"], "matched": result["matched"], "total": result["total"],
        "wordCount": len(words), "topic": sem["category"], "intent": sem["intent"],
        "allFull": all(s["kind"] == "full" for s in result["sentences"]),
    }


def dictionary_rows() -> Dict[str, object]:
    rows = D.build_dictionary()
    return {"rows": [{"word": w, "type": t, "english": e, "french": f} for w, t, e, f in rows],
            "letters": D.letters(rows), "total": len(rows),
            "mine": sum(1 for r in rows if r[1].startswith("★")), "types": userdict.TYPES}


def add_word(word, kind, english, french, gender="m") -> Dict[str, object]:
    ok, message = userdict.add_word(word, kind, english, french, gender)
    return {"ok": ok, "message": message}


def remove_word(word) -> Dict[str, object]:
    return {"ok": userdict.remove_word(word)}


def statement_rows() -> Dict[str, object]:
    rows = S.all_statements()
    return {"rows": rows, "topics": S.topics(), "total": len(rows),
            "collected": sum(1 for r in rows if r["source"] == "collected"),
            "examples": sum(1 for r in rows if r["source"] == "example"),
            "mine": sum(1 for r in rows if r["source"] == "yours")}


def add_statement(text, english, french, topic) -> Dict[str, object]:
    ok, message = S.add_statement(text, english, french, topic)
    return {"ok": ok, "message": message}


def remove_statement(text) -> Dict[str, object]:
    return {"ok": S.remove_statement(text)}


def insights() -> Dict[str, object]:
    return {"top": [{"word": w, "count": n} for w, n in _bank.top_words(10)],
            "collected": _bank.total_unique, "unknown": _bank.unknown_words[:50],
            "dictionary": len(D.build_dictionary()), "statements": len(S.all_statements())}
