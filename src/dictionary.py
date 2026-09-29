"""
AFJEN dictionary and word bank
CS4110 - Compiler Construction

* build_dictionary() collects every word the lexer/translator knows (200+ entries):
  word, category, English, Français.
* WordBank records every word the user analyzes (with counts) in data/word_bank.json, so the
  application keeps collecting vocabulary as it is used.
"""

import json
import os
from datetime import datetime
from typing import Dict, List, Tuple

import translator as T
import userdict

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
BANK_PATH = os.path.join(ROOT, "data", "word_bank.json")

# Pidgin / franc-anglais function words handled by the lexer and the translator rules
PIDGIN_WORDS = [
    ("dey", "Pidgin aspect", "is/are (progressive)", "est en train de"),
    ("done", "Pidgin aspect", "has/have (perfect)", "a / ont (passé composé)"),
    ("don", "Pidgin aspect", "has/have (perfect)", "a / ont (passé composé)"),
    ("di", "Pidgin aspect", "is/are (progressive, Anglophone)", "est en train de"),
    ("bin", "Pidgin aspect", "did / was (past)", "passé composé"),
    ("wan", "Pidgin modal", "want to", "vouloir"),
    ("the", "Determiner", "the", "le / la / les"), ("a", "Determiner", "a", "un / une"),
    ("an", "Determiner", "an", "un / une"), ("this", "Determiner", "this", "ce / cette"),
    ("that", "Determiner", "that", "ce / cette"), ("dis", "Determiner", "this (Pidgin)", "ce / cette"),
    ("dat", "Determiner", "that (Pidgin)", "ce / cette"), ("my", "Determiner", "my", "mon / ma"),
    ("your", "Determiner", "your", "ton / ta / votre"), ("our", "Determiner", "our", "notre"),
    ("their", "Determiner", "their", "leur"), ("his", "Determiner", "his", "son / sa"),
    ("and", "Conjunction", "and", "et"), ("but", "Conjunction", "but", "mais"), ("or", "Conjunction", "or", "ou"),
    ("mos", "Pidgin modal", "must", "devoir"),
    ("fit", "Pidgin aspect", "can / be able to", "pouvoir"),
    ("no", "Negation", "no / not", "ne ... pas"),
    ("make", "Subjunctive", "let / please / so that", "que / pour que"),
    ("na", "Particle", "it is / (emphasis)", "c'est / (insistance)"),
    ("am", "Particle", "it / him / her", "le / la"),
    ("me", "Particle", "me", "moi"),
    ("small", "Particle", "a little", "un peu"),
]

_CATEGORY_ORDER = ["Pidgin aspect", "Pidgin modal", "Determiner", "Conjunction", "Negation", "Subjunctive", "Particle", "Verb", "Noun", "Proper noun",
                   "Number", "Adjective", "Adverb", "Preposition", "Pronoun", "Interjection", "Code-mixed",
                   "Question word"]


def build_dictionary() -> List[Tuple[str, str, str, str]]:
    """Return sorted (word, category, english, french) rows."""
    rows: Dict[str, Tuple[str, str, str, str]] = {}

    def add(word, cat, en, fr):
        rows.setdefault(word.lower(), (word, cat, en, fr))

    for w, cat, en, fr in PIDGIN_WORDS:
        add(w, cat, en, fr)
    for w, (inf, _pp, _aux, _imp) in T.FR.items():
        en = T.EN_BASE.get(w, w)
        add(w, "Verb", en, inf)
    for w, e in T.NOUNS.items():
        add(w, "Noun", e[0], e[1])
    for w, e in T.PROPER.items():
        add(w, "Proper noun", e[0], e[1])
    for w, e in T.NUMBERS.items():
        add(w, "Number", e[0], e[1])
    for w, e in T.ADJ.items():
        add(w, "Adjective", e[0], e[1])
    for w, e in T.ADV.items():
        add(w, "Adverb", e[0], e[1])
    for w, e in T.PREP.items():
        add(w, "Preposition", e[0], e[1])
    for w, e in T.INTERJ.items():
        add(w, "Interjection", e[0] or "(emphasis)", e[1] or "(insistance)")
    for w, e in T.CODE.items():
        add(w, "Code-mixed", e[0], e[1])
    for w, e in T.QWORDS.items():
        add(w, "Question word", e[0], e[1])
    for w, (en, fr, _p) in T.PRON_EN.items():
        add(w, "Pronoun", en, fr)
    for entry in userdict.load():
        key = entry["word"].lower()
        if key in rows:
            rows[key] = (rows[key][0], "★ " + entry["type"], rows[key][2], rows[key][3])
    return sorted(rows.values(), key=lambda r: (0 if r[1].startswith("★") else 1,
                                                _CATEGORY_ORDER.index(r[1]) if r[1] in _CATEGORY_ORDER else 99,
                                                r[0].lower()))


def known_words():
    return {row[0].lower() for row in build_dictionary()}


DICTIONARY = build_dictionary()
KNOWN = {row[0].lower() for row in DICTIONARY}


class WordBank:
    """Persistent counter of every word analyzed, flagged known/unknown."""

    def __init__(self, path: str = BANK_PATH):
        self.path = path
        self.words: Dict[str, Dict[str, object]] = {}
        self.load()

    def load(self):
        try:
            with open(self.path, encoding="utf-8") as f:
                self.words = json.load(f).get("words", {})
        except (OSError, ValueError):
            self.words = {}

    def save(self):
        try:
            os.makedirs(os.path.dirname(self.path), exist_ok=True)
            with open(self.path, "w", encoding="utf-8") as f:
                json.dump({"updated": datetime.now().isoformat(timespec="seconds"), "words": self.words},
                          f, ensure_ascii=False, indent=1, sort_keys=True)
        except OSError:
            pass

    def record(self, words: List[str]):
        known = known_words()
        for w in words:
            key = w.lower()
            if not key or not any(ch.isalpha() for ch in key):
                continue
            entry = self.words.setdefault(key, {"count": 0, "known": key in known})
            entry["count"] = int(entry["count"]) + 1
        self.save()

    @property
    def total_unique(self) -> int:
        return len(self.words)

    @property
    def unknown_words(self) -> List[str]:
        known = known_words()
        return sorted(w for w in self.words if w not in known)

    def top_words(self, n: int = 10) -> List[Tuple[str, int]]:
        return sorted(((w, int(e["count"])) for w, e in self.words.items()), key=lambda x: (-x[1], x[0]))[:n]


def main():
    print(f"AFJEN dictionary: {len(DICTIONARY)} words")
    for row in DICTIONARY[:15]:
        print("  %-12s %-14s %-24s %s" % row)


if __name__ == "__main__":
    main()
