"""
Generates the grammar documentation files from src/grammar.py so they can
never disagree with the parser:

    data/grammar_rules.md            - productions
    analysis/first_follow_sets.md    - FIRST and FOLLOW sets
    analysis/ll1_parsing_table.md    - LL(1) predictive parsing table + conflict check

Run:  python analysis/generate_tables.py
"""

import os
import sys

ROOT = os.path.join(os.path.dirname(__file__), "..")
sys.path.insert(0, os.path.join(ROOT, "src"))

import grammar as g  # noqa: E402


def rules_md() -> str:
    out = ["# Grammar Rules (LL(1))", "",
           "Generated from `src/grammar.py`. Terminals are lexer token types; ε is the empty string.",
           "State 0 / state 1 (`U0`,`BODY0`,`R0` vs `F1`,`G1`,`BODY1`,`R1`) track whether a predicate",
           "has been seen: every valid statement must contain at least one predicate.", "",
           "```"]
    for i, (nt, prods) in enumerate(g.GRAMMAR.items(), 1):
        out.append(f"{nt:<8} → " + "\n         | ".join(" ".join(p) for p in prods))
    out += ["```", "",
            f"* Non-terminals: {len(g.GRAMMAR)}",
            f"* Productions: {sum(len(p) for p in g.GRAMMAR.values())}",
            f"* Terminals: {len(g.terminals())} ({', '.join(sorted(g.terminals()))})",
            "* Left recursion: none (removed - see report section 3.2)",
            "* Left factoring: applied (VP/VTAIL, PPX/PPY, COMPS/COMPSA, NPB/NPB2)",
            f"* LL(1) conflicts: {len(g.find_conflicts())}"]
    return "\n".join(out) + "\n"


def first_follow_md() -> str:
    out = ["# FIRST and FOLLOW Sets", "", "Computed by fixed-point iteration in `src/grammar.py`.", "",
           "| Non-terminal | FIRST | FOLLOW |", "|---|---|---|"]
    for nt in g.GRAMMAR:
        out.append(f"| {nt} | {', '.join(sorted(g.FIRST[nt]))} | {', '.join(sorted(g.FOLLOW[nt]))} |")
    return "\n".join(out) + "\n"


def table_md() -> str:
    conflicts = g.find_conflicts()
    out = ["# LL(1) Predictive Parsing Table", "",
           "Cell (A, a) = production to apply when the top of the stack is A and the lookahead is a.",
           "Empty cell = syntax error.", "",
           f"**Conflicts: {len(conflicts)}** " + ("(the grammar is LL(1))" if not conflicts else ""), "",
           "## Productions (numbered)", ""]
    numbering = {}
    n = 0
    for nt, prods in g.GRAMMAR.items():
        for idx in range(len(prods)):
            n += 1
            numbering[(nt, idx)] = n
            out.append(f"{n}. {g.production_to_str(nt, idx)}")
    terms = sorted(g.terminals()) + [g.END]
    out += ["", "## Parsing table (production numbers)", "",
            "| | " + " | ".join(terms) + " |", "|---|" + "---|" * len(terms)]
    for nt in g.GRAMMAR:
        row = []
        for t in terms:
            idx = g.TABLE.get((nt, t))
            row.append("" if idx is None else str(numbering[(nt, idx)]))
        out.append(f"| **{nt}** | " + " | ".join(row) + " |")
    return "\n".join(out) + "\n"


def main():
    targets = {
        os.path.join(ROOT, "data", "grammar_rules.md"): rules_md(),
        os.path.join(ROOT, "analysis", "first_follow_sets.md"): first_follow_md(),
        os.path.join(ROOT, "analysis", "ll1_parsing_table.md"): table_md(),
    }
    for path, text in targets.items():
        with open(path, "w", encoding="utf-8") as f:
            f.write(text)
        print("wrote", os.path.normpath(path))
    print("LL(1) conflicts:", len(g.find_conflicts()))


if __name__ == "__main__":
    main()
