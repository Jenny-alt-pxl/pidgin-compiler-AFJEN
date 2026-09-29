"""
User dictionary for AFJEN
CS4110 - Compiler Construction

Words taught through the GUI are stored in data/user_dictionary.json and applied to both the lexical
analyzer (token type) and the translator (English / French meaning), so a new word immediately works
everywhere: tokenizing, parsing, translating.
"""

import csv
import json
import os
import re
from typing import Dict, List, Tuple

import lexical_analyzer as L
import translator as T

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
USER_PATH = os.path.join(ROOT, "data", "user_dictionary.json")

TYPES = ["noun", "verb", "adjective", "adverb", "interjection", "proper noun"]
_TOKEN = {"verb": L.TokenType.VERB, "adjective": L.TokenType.ADJECTIVE, "adverb": L.TokenType.ADVERB,
          "interjection": L.TokenType.INTERJECTION, "proper noun": L.TokenType.PROPER_NOUN}
WORD_RE = re.compile(r"^[a-zà-ÿ][a-zà-ÿ'’-]{0,29}$", re.IGNORECASE)


def load() -> List[Dict[str, str]]:
    try:
        with open(USER_PATH, encoding="utf-8") as f:
            data = json.load(f)
        return [e for e in data.get("words", []) if isinstance(e, dict) and e.get("word")]
    except (OSError, ValueError):
        return []


def save(entries: List[Dict[str, str]]) -> None:
    os.makedirs(os.path.dirname(USER_PATH), exist_ok=True)
    with open(USER_PATH, "w", encoding="utf-8") as f:
        json.dump({"words": sorted(entries, key=lambda e: e["word"].lower())}, f, ensure_ascii=False, indent=1)


def _fr_forms(inf: str) -> Tuple[str, str, str, str]:
    """(infinitive, past participle, auxiliary, tu-imperative) derived from a French infinitive."""
    inf = inf.strip().lower()
    if inf.startswith("se ") or inf.startswith("s'"):
        return inf, inf, "être", inf
    if inf.endswith("er"):
        stem = inf[:-2]
        return inf, stem + "é", "avoir", stem + "e"
    if inf.endswith("ir"):
        stem = inf[:-2]
        return inf, stem + "i", "avoir", stem + "is"
    if inf.endswith("re"):
        stem = inf[:-2]
        return inf, stem + "u", "avoir", stem + "s"
    return inf, inf, "avoir", inf


def validate(word: str, kind: str, english: str, french: str) -> str:
    """Return an error message, or '' if the entry is valid."""
    word = word.strip()
    if not word:
        return "Type the word first."
    if " " in word:
        return "Add one word at a time (no spaces)."
    if not WORD_RE.match(word):
        return "Use letters, hyphens or apostrophes only (max 30 characters)."
    if kind not in TYPES:
        return "Choose a word type."
    if not english.strip() or not french.strip():
        return "Give both the English and the French meaning."
    if word.lower() in T.BUILTIN_WORDS:
        return f"“{word}” is already a built-in word."
    return ""


def add_word(word: str, kind: str, english: str, french: str, gender: str = "m") -> Tuple[bool, str]:
    err = validate(word, kind, english, french)
    if err:
        return False, err
    entries = [e for e in load() if e["word"].lower() != word.lower()]
    replaced = len(entries) != len(load())
    entries.append({"word": word.strip().lower(), "type": kind, "english": english.strip(),
                    "french": french.strip(), "gender": gender if gender in ("m", "f") else "m"})
    save(entries)
    apply()
    return True, f"{'Updated' if replaced else 'Added'} “{word.strip().lower()}”."


def remove_word(word: str) -> bool:
    entries = load()
    kept = [e for e in entries if e["word"].lower() != word.lower()]
    if len(kept) == len(entries):
        return False
    save(kept)
    apply()
    return True


def export_csv(path: str) -> int:
    entries = load()
    with open(path, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["word", "type", "english", "french", "gender"])
        for e in entries:
            w.writerow([e["word"], e["type"], e["english"], e["french"], e.get("gender", "m")])
    return len(entries)


def import_csv(path: str) -> Tuple[int, int]:
    added = skipped = 0
    with open(path, encoding="utf-8", newline="") as f:
        for row in csv.DictReader(f):
            ok, _ = add_word(row.get("word", ""), (row.get("type") or "noun").lower(), row.get("english", ""),
                             row.get("french", ""), row.get("gender") or "m")
            added += ok
            skipped += not ok
    return added, skipped


def apply() -> int:
    """Push user words into the translator tables and the lexer. Returns how many were applied."""
    for table, keys in T.USER_ADDED.items():
        for key in keys:
            getattr(T, table).pop(key, None)
        keys.clear()
    L.USER_TOKEN_TYPES.clear()
    count = 0
    for e in load():
        w, kind, en, fr = e["word"].lower(), e["type"], e["english"], e["french"]
        if w in T.BUILTIN_WORDS:
            continue
        count += 1
        if kind == "noun":
            T.NOUNS[w] = (en, fr, e.get("gender", "m"), False)
            T.USER_ADDED["NOUNS"].add(w)
        elif kind == "proper noun":
            T.PROPER[w] = (en, fr)
            T.USER_ADDED["PROPER"].add(w)
        elif kind == "adjective":
            T.ADJ[w] = (en, fr)
            T.USER_ADDED["ADJ"].add(w)
        elif kind == "adverb":
            T.ADV[w] = (en, fr)
            T.USER_ADDED["ADV"].add(w)
        elif kind == "interjection":
            T.INTERJ[w] = (en, fr)
            T.USER_ADDED["INTERJ"].add(w)
        elif kind == "verb":
            T.FR[w] = _fr_forms(fr)
            first, _, rest = en.strip().partition(" ")
            third, pp, ing = T._en_forms(first)
            suffix = " " + rest if rest else ""
            T.EN_IRREG[w] = (third + suffix, pp + suffix, ing + suffix)
            T.EN_BASE[w] = en.strip()
            T.PAST_EN[w] = pp + suffix
            for table in ("FR", "EN_IRREG", "EN_BASE", "PAST_EN"):
                T.USER_ADDED[table].add(w)
        if kind in _TOKEN:
            L.USER_TOKEN_TYPES[w] = _TOKEN[kind]
    return count


apply()
