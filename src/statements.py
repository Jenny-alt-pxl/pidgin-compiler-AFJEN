"""
Statements: built-in corpus + statements added by the user
CS4110 - Compiler Construction

User statements are stored in data/user_statements.json with their own English / French translation
and are used as verified translations by the translator.
"""

import csv
import json
import os
from typing import Dict, List, Tuple

import corpus
import translator as T

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
USER_PATH = os.path.join(ROOT, "data", "user_statements.json")


def load_user() -> List[Dict[str, object]]:
    try:
        with open(USER_PATH, encoding="utf-8") as f:
            return [e for e in json.load(f).get("statements", []) if e.get("text")]
    except (OSError, ValueError):
        return []


def save_user(entries: List[Dict[str, object]]) -> None:
    os.makedirs(os.path.dirname(USER_PATH), exist_ok=True)
    with open(USER_PATH, "w", encoding="utf-8") as f:
        json.dump({"statements": entries}, f, ensure_ascii=False, indent=1)


def all_statements() -> List[Dict[str, object]]:
    """Built-in corpus followed by the user's statements (numbered on from the corpus)."""
    rows = [dict(c) for c in corpus.CORPUS]
    n = len(rows)
    for e in load_user():
        n += 1
        rows.append({"id": f"stmt_{n:03d}", "n": n, "topic": e.get("topic") or "Everyday Transactions",
                     "source": "yours", "text": e["text"], "en": e.get("en", ""), "fr": e.get("fr", "")})
    return rows


def topics() -> List[str]:
    extra = sorted({str(e.get("topic")) for e in load_user() if e.get("topic")} - set(corpus.TOPICS))
    return corpus.TOPICS + extra


def add_statement(text: str, en: str, fr: str, topic: str) -> Tuple[bool, str]:
    text, en, fr, topic = text.strip(), en.strip(), fr.strip(), (topic or "").strip()
    if not text:
        return False, "Type the Pidgin statement first."
    if not en or not fr:
        return False, "Give both the English and the French translation."
    key = T._norm(text)
    if any(T._norm(str(c["text"])) == key for c in corpus.CORPUS):
        return False, "That statement is already in the collection."
    entries = [e for e in load_user() if T._norm(e["text"]) != key]
    replaced = len(entries) != len(load_user())
    entries.append({"text": text, "en": en, "fr": fr, "topic": topic or "Everyday Transactions"})
    save_user(entries)
    apply()
    return True, "Statement updated." if replaced else "Statement added to the collection."


def remove_statement(text: str) -> bool:
    key = T._norm(text)
    entries = load_user()
    kept = [e for e in entries if T._norm(e["text"]) != key]
    if len(kept) == len(entries):
        return False
    save_user(kept)
    apply()
    return True


def export_csv(path: str) -> int:
    rows = all_statements()
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["n", "topic", "source", "pidgin", "english", "francais"])
        for r in rows:
            w.writerow([r["n"], r["topic"], r["source"], r["text"], r["en"], r["fr"]])
    return len(rows)


def apply() -> int:
    """Make every statement (built-in and user) a verified translation."""
    T.VERIFIED.clear()
    for r in all_statements():
        if r["en"] and r["fr"]:
            T.VERIFIED[str(r["text"])] = {"en": str(r["en"]), "fr": str(r["fr"])}
    T.rebuild_verified_index()
    return len(T.VERIFIED)


apply()
