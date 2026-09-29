"""
Strict table-driven LL(1) parser for Yaoundé Urban Communication
CS4110 - Compiler Construction

Reads the token stream from the lexical analyzer and decides whether the
statement belongs to the language defined in grammar.py. Uses an explicit
stack and the predictive parsing table (one token of lookahead), builds a
parse tree, and reports precise syntax errors (position, found token,
expected tokens, and the grammar rule that was being applied).

The earlier permissive recursive-descent parser is kept in lenient_parser.py
for comparison.
"""

from dataclasses import dataclass, field
from typing import List, Optional, Tuple

import grammar
from grammar import EPS, END, GRAMMAR, TABLE
from lexical_analyzer import Token, TokenType, LexicalAnalyzer


@dataclass
class ParseNode:
    """Node of the parse tree (non-terminal with children, or terminal with a token)."""
    rule: str
    children: List["ParseNode"] = field(default_factory=list)
    token: Optional[Token] = None

    def __repr__(self):
        if self.token:
            return f"Node({self.rule}: {self.token.value})"
        return f"Node({self.rule})"

    def format_tree(self, indent: int = 0) -> str:
        lines = ["  " * indent + str(self)]
        for child in self.children:
            lines.append(child.format_tree(indent + 1))
        return "\n".join(lines)

    def print_tree(self, indent: int = 0):
        print(self.format_tree(indent))

    def to_dict(self):
        if self.token is not None:
            return {"type": self.rule, "value": self.token.value, "token_type": self.token.type.value}
        return {"type": self.rule, "children": [c.to_dict() for c in self.children]}

    def compact(self) -> "ParseNode":
        """Copy of the tree without empty non-terminals and single-child chains."""
        if self.token is not None:
            return ParseNode(self.rule, [], self.token)
        kids = [c.compact() for c in self.children]
        kids = [k for k in kids if k.token is not None or k.children]
        if len(kids) == 1 and kids[0].token is None:
            return ParseNode(self.rule, kids[0].children, None)
        return ParseNode(self.rule, kids, None)


@dataclass
class SyntaxErrorInfo:
    message: str
    token: Optional[Token]
    expected: List[str]
    rule: str

    def __str__(self):
        return self.message


class Parser:
    """Predictive (table-driven) LL(1) parser."""

    def __init__(self, tokens: List[Token]):
        self.tokens = tokens
        self.errors: List[str] = []
        self.error_info: Optional[SyntaxErrorInfo] = None
        self.steps: List[Tuple[str, str, str]] = []   # (stack, lookahead, action) - for traces

    def _lookahead(self, pos: int) -> str:
        if pos >= len(self.tokens):
            return END
        tok = self.tokens[pos]
        return END if tok.type == TokenType.EOF else tok.type.value

    def parse(self, trace: bool = False) -> Tuple[Optional[ParseNode], bool]:
        root = ParseNode(grammar.START)
        end_marker = ParseNode(END)
        stack: List[Tuple[str, ParseNode]] = [(END, end_marker), (grammar.START, root)]
        pos = 0

        while stack:
            symbol, node = stack.pop()
            look = self._lookahead(pos)
            if trace:
                names = " ".join(s for s, _ in reversed(stack + [(symbol, node)]))
                self.steps.append((names, look, ""))

            if symbol == END:
                if look == END:
                    if trace:
                        self.steps[-1] = (self.steps[-1][0], look, "ACCEPT")
                    return root, True
                self._fail(pos, ["end of statement"], "S", "extra input after a complete statement")
                return None, False

            if symbol in GRAMMAR:
                idx = TABLE.get((symbol, look))
                if idx is None:
                    expected = sorted(t for (nt, t) in TABLE if nt == symbol)
                    self._fail(pos, expected, symbol)
                    return None, False
                prod = GRAMMAR[symbol][idx]
                if trace:
                    self.steps[-1] = (self.steps[-1][0], look, grammar.production_to_str(symbol, idx))
                if prod == [EPS]:
                    continue
                children = [ParseNode(sym) for sym in prod]
                node.children = children
                for sym, child in reversed(list(zip(prod, children))):
                    stack.append((sym, child))
            else:
                if symbol == look:
                    node.token = self.tokens[pos]
                    if trace:
                        self.steps[-1] = (self.steps[-1][0], look, f"match {self.tokens[pos].value!r}")
                    pos += 1
                else:
                    self._fail(pos, [symbol], symbol)
                    return None, False
        return None, False

    def _fail(self, pos: int, expected: List[str], rule: str, note: str = ""):
        token = self.tokens[pos] if pos < len(self.tokens) else self.tokens[-1]
        found = "end of input" if token.type == TokenType.EOF else f"'{token.value}' ({token.type.value})"
        where = f"line {token.line}, column {token.column}"
        exp = ", ".join(expected[:8]) + (" ..." if len(expected) > 8 else "")
        msg = f"Syntax error at {where}: unexpected {found} while parsing {rule}; expected one of: {exp}"
        if note:
            msg = f"Syntax error at {where}: {note}"
        self.error_info = SyntaxErrorInfo(msg, token, expected, rule)
        self.errors.append(msg)

    def parse_with_diagnostics(self) -> Tuple[Optional[ParseNode], bool, List[str]]:
        tree, success = self.parse()
        return tree, success, (["No syntax errors detected."] if success else list(self.errors))


def parse_statement(statement: str) -> Tuple[Optional[ParseNode], bool, List[Token]]:
    """Tokenize and parse a statement. Returns (parse_tree or None, accepted, tokens)."""
    tokens = LexicalAnalyzer().tokenize(statement)
    tree, success = Parser(tokens).parse()
    return tree, success, tokens


def parse_statement_detailed(statement: str) -> Tuple[Optional[ParseNode], bool, List[Token], List[str]]:
    """Like parse_statement but also returns readable diagnostics."""
    tokens = LexicalAnalyzer().tokenize(statement)
    tree, success, diagnostics = Parser(tokens).parse_with_diagnostics()
    return tree, success, tokens, diagnostics


def trace_statement(statement: str) -> List[Tuple[str, str, str]]:
    """Return the (stack, lookahead, action) steps of the LL(1) parse."""
    tokens = LexicalAnalyzer().tokenize(statement)
    parser = Parser(tokens)
    parser.parse(trace=True)
    return parser.steps


def main():
    import sys
    text = " ".join(sys.argv[1:]) or "The light done cut again"
    tree, ok, tokens, diag = parse_statement_detailed(text)
    print(f"{'ACCEPTED' if ok else 'REJECTED'}: {text}")
    if ok:
        tree.compact().print_tree()
    else:
        print(diag[0])


if __name__ == "__main__":
    main()


# ---------------------------------------------------------------------------
# Never-reject analysis (used by the AFJEN GUI): any text is analysed
# ---------------------------------------------------------------------------
import re as _re


def analyze_robust(text: str) -> dict:
    """
    Analyse arbitrarily long text without ever refusing it.

    Each sentence is parsed with the strict LL(1) parser. If the whole sentence does not match, it is
    split into clauses (at commas / connectors) and each clause is parsed on its own; clauses that still
    do not match are reported as informal fragments. Result kinds: 'full', 'partial', 'informal'.
    """
    lexer = LexicalAnalyzer()
    sentences = [s.strip() for s in _re.split(r"(?<=[.!?])\s+|\n+", text.strip()) if s.strip()]
    results = []
    matched_total = clause_total = 0
    for sentence in sentences:
        tree, ok, tokens, diagnostics = parse_statement_detailed(sentence)
        real = [t for t in tokens if t.type != TokenType.EOF]
        if ok:
            results.append({"text": sentence, "kind": "full", "trees": [tree.compact()], "fragments": [],
                            "matched": 1, "total": 1, "tokens": real})
            matched_total += 1
            clause_total += 1
            continue
        clauses, cur = [], []
        for t in real:
            if t.type == TokenType.CONNECTOR and t.value == ",":
                if cur:
                    clauses.append(cur)
                cur = []
            else:
                cur.append(t)
        if cur:
            clauses.append(cur)
        trees, fragments = [], []
        for clause in clauses:
            eof = Token(TokenType.EOF, "", clause[-1].line, clause[-1].column + len(clause[-1].value))
            parser = Parser(list(clause) + [eof])
            sub, sub_ok = parser.parse()
            words = " ".join(t.value for t in clause)
            if sub_ok:
                trees.append(sub.compact())
            else:
                fragments.append((words, parser.errors[0] if parser.errors else ""))
        matched = len(trees)
        total = max(len(clauses), 1)
        kind = "partial" if matched else "informal"
        results.append({"text": sentence, "kind": kind, "trees": trees, "fragments": fragments,
                        "matched": matched, "total": total, "tokens": real, "diagnostic": diagnostics[0]})
        matched_total += matched
        clause_total += total
    all_tokens = [t for r in results for t in r["tokens"]]
    return {"sentences": results, "tokens": all_tokens, "matched": matched_total, "total": max(clause_total, 1),
            "coverage": round(100 * matched_total / max(clause_total, 1))}
