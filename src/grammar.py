"""
LL(1) grammar for Yaoundé urban speech - single source of truth.
CS4110 - Compiler Construction

The grammar works on the token TYPES produced by the lexical analyzer.
FIRST/FOLLOW sets and the predictive parsing table are computed from the
productions below (nothing is written by hand), and any LL(1) conflict is
reported by `find_conflicts()`.

Two "states" of the grammar (suffix 0 / 1) record whether a predicate
(verb phrase, adjectival or prepositional predicate) has already been seen.
A statement is only valid if it contains at least one predicate, so lone
fragments such as "Brother" or "the the the" are rejected, while noun
fragments around a predicate ("Taxi! Yaoundé, Yaoundé! Fill am ...") are accepted.
"""

from typing import Dict, List, Set, Tuple

EPS = "ε"
END = "$"

# ---------------------------------------------------------------------------
# Productions (after removal of EBNF operators, left recursion and left factoring)
# ---------------------------------------------------------------------------
GRAMMAR: Dict[str, List[List[str]]] = {
    "S": [["U0"]],

    # ---- state 0: no predicate seen yet -------------------------------------
    "U0": [["PARTS", "U0B"]],
    "U0B": [["BODY0"], ["SEPS", "U0"]],
    "BODY0": [
        ["NP", "PARTS", "R0"],
        ["IMP", "F1"],
        ["QCL", "F1"],
        ["SUBCL", "F1"],
        ["PREPOSITION", "PPX", "SEPS", "U0"],  # fronted phrase: "After exam finish, ..."
    ],
    "R0": [["PRED", "F1"], ["SEPS", "U0"], ["PRONOUN", "PARTS", "R0"], ["ARTICLE", "NPB", "PARTS", "R0"]],

    # ---- state 1: a predicate has been seen ----------------------------------
    "F1": [["SEPS", "G1"], [EPS]],
    "G1": [["PARTS", "G2"]],
    "G2": [["BODY1"], ["SEPS", "G1"], [EPS]],
    "BODY1": [
        ["NP", "PARTS", "R1"],
        ["IMP", "F1"],
        ["QCL", "F1"],
        ["SUBCL", "F1"],
        ["PREPOSITION", "PPX", "F1"],
        ["ADJP", "F1"],                # exclamation fragment: "fresh!"
        ["NEGATION", "PARTS", "F1"],   # "no wahala"
    ],
    "R1": [["PRED", "F1"], ["PRONOUN", "PARTS", "R1"], ["ARTICLE", "NPB", "PARTS", "R1"], ["F1"]],

    # ---- separators and discourse particles ----------------------------------
    "SEPS": [["SEP"]],
    "SEP": [["CONNECTOR"], ["PUNCTUATION"]],
    "PARTS": [["PART", "PARTS"], [EPS]],
    "PART": [["PIDGIN_MARKER"], ["INTERJECTION"], ["CODE_MIXED"]],

    # ---- predicates -----------------------------------------------------------
    "PRED": [["VP"], ["ADJP", "COMPS"], ["PREPOSITION", "PPX"]],
    "IMP": [["VERB", "VTAIL"]],
    "VP": [["NEGATION", "VP"], ["PIDGIN_VERB", "VPA"], ["VERB", "VTAIL"]],
    "VPA": [["VERB", "VTAIL"], ["ADJP", "COMPS"], ["PREPOSITION", "PPX"]],
    "VTAIL": [["VERB", "VTAIL"], ["COMPS"]],           # serial verbs: "say come sit down"
    "ADJP": [["ADVERB", "ADJP"], ["ADJECTIVE"]],

    # ---- complements ----------------------------------------------------------
    "COMPS": [["NP", "COMPSA"], ["PREPOSITION", "PPX"], ["NONNP", "COMPS"], ["SUBCL"], [EPS]],
    "COMPSA": [["PREPOSITION", "PPX"], ["NONNP", "COMPS"], ["SUBCL"], [EPS]],
    "NONNP": [["PART"], ["ADVERB"], ["ADJECTIVE"]],

    # ---- clauses --------------------------------------------------------------
    "SUBCL": [["SUBJUNCTIVE", "NP", "PARTS", "VP"]],   # "make we go", "make you reduce am"
    "QCL": [["QUESTION_WORD", "QA"]],
    "QA": [["ADJECTIVE", "QA"], ["ADVERB", "QA"], ["PREPOSITION", "PPX"], ["NP", "QB"], [EPS]],
    "QB": [["VP"], [EPS]],

    # ---- phrases --------------------------------------------------------------
    # Prepositional phrase after the preposition: a noun phrase (optionally followed
    # by more complements) or a clause ("before go fill tank", "After exam finish").
    "PPX": [["VP"], ["NP", "PPY"]],
    "PPY": [["VP"], ["COMPSA"]],
    "NP": [["ARTICLE", "NPB"], ["NPB"]],
    "NPB": [["NUMBER", "NPB2"], ["NOUN", "NPB2"], ["PROPER_NOUN", "NPB2"], ["PRONOUN"]],
    "NPB2": [["NUMBER", "NPB2"], ["NOUN", "NPB2"], ["PROPER_NOUN", "NPB2"], [EPS]],
}

START = "S"
NONTERMINALS = set(GRAMMAR)


def is_nonterminal(symbol: str) -> bool:
    return symbol in NONTERMINALS


def terminals() -> Set[str]:
    result = set()
    for prods in GRAMMAR.values():
        for prod in prods:
            for sym in prod:
                if sym != EPS and sym not in NONTERMINALS:
                    result.add(sym)
    return result


def _first_of_sequence(seq: List[str], first: Dict[str, Set[str]]) -> Set[str]:
    out: Set[str] = set()
    for sym in seq:
        f = first[sym] if sym in NONTERMINALS else {sym}
        out |= f - {EPS}
        if EPS not in f:
            return out
    out.add(EPS)
    return out


def compute_first() -> Dict[str, Set[str]]:
    first = {n: set() for n in GRAMMAR}
    changed = True
    while changed:
        changed = False
        for nt, prods in GRAMMAR.items():
            for prod in prods:
                f = {EPS} if prod == [EPS] else _first_of_sequence(prod, first)
                if not f <= first[nt]:
                    first[nt] |= f
                    changed = True
    return first


def compute_follow(first: Dict[str, Set[str]]) -> Dict[str, Set[str]]:
    follow = {n: set() for n in GRAMMAR}
    follow[START].add(END)
    changed = True
    while changed:
        changed = False
        for nt, prods in GRAMMAR.items():
            for prod in prods:
                for i, sym in enumerate(prod):
                    if sym not in NONTERMINALS:
                        continue
                    rest = _first_of_sequence(prod[i + 1:], first)
                    add = rest - {EPS}
                    if EPS in rest:
                        add |= follow[nt]
                    if not add <= follow[sym]:
                        follow[sym] |= add
                        changed = True
    return follow


FIRST = compute_first()
FOLLOW = compute_follow(FIRST)


def build_table() -> Tuple[Dict[Tuple[str, str], int], List[Tuple[str, str, int, int]]]:
    """Return (table, conflicts). table[(nonterminal, lookahead)] = production index."""
    table: Dict[Tuple[str, str], int] = {}
    conflicts: List[Tuple[str, str, int, int]] = []
    for nt, prods in GRAMMAR.items():
        for idx, prod in enumerate(prods):
            f = {EPS} if prod == [EPS] else _first_of_sequence(prod, FIRST)
            select = (f - {EPS}) | (FOLLOW[nt] if EPS in f else set())
            for term in select:
                if (nt, term) in table and table[(nt, term)] != idx:
                    conflicts.append((nt, term, table[(nt, term)], idx))
                else:
                    table[(nt, term)] = idx
    return table, conflicts


TABLE, CONFLICTS = build_table()


def find_conflicts() -> List[Tuple[str, str, int, int]]:
    return CONFLICTS


def production_to_str(nt: str, idx: int) -> str:
    return f"{nt} → {' '.join(GRAMMAR[nt][idx])}"
