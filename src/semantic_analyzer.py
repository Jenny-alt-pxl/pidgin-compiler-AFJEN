"""
Semantic Analyzer for Yaoundé Compiler
Adds a practical enhancement: intent and category detection on top of parsing.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

from lexical_analyzer import LexicalAnalyzer, TokenType, Token
from parser import parse_statement


@dataclass
class SemanticNode:
    """A simple AST node for semantic analysis."""
    kind: str
    value: Optional[str] = None
    children: List["SemanticNode"] = field(default_factory=list)

    def __repr__(self):
        if self.value is not None:
            return f"SemanticNode({self.kind}: {self.value})"
        return f"SemanticNode({self.kind})"


class SemanticAnalyzer:
    """Classify statements by topic and intent after syntax validation."""

    def __init__(self):
        self.analyzer = LexicalAnalyzer()

    def _detect_category(self, tokens: List[Token]) -> str:
        text = " ".join(t.value for t in tokens if t.type != TokenType.EOF).lower()

        # statements from the collection carry their own topic
        try:
            import statements
            import translator
            norm = translator._norm(" ".join(t.value for t in tokens if t.type != TokenType.EOF))
            for row in statements.all_statements():
                if translator._norm(str(row["text"])).replace(" ,", ",") == norm.replace(" ,", ","):
                    return str(row["topic"])
        except Exception:
            pass

        keywords = {
            "transport": ["taxi", "transport", "carrefour", "road", "traffic", "bus", "passenger", "driver", "junction", "bendskin", "moto"],
            "internet": ["internet", "modem", "network", "mtn", "signal", "browser", "airtime"],
            "market": ["money", "francs", "tomatoes", "price", "market", "buy", "charge", "price"],
            "security": ["checkpoint", "document", "road", "rain", "mud", "police", "careful"],
            "energy": ["light", "generator", "petrol", "pump", "empty", "fuel", "electricity", "candle", "station"],
            "university": ["lecture", "exam", "semester", "class", "prof", "student", "beer"],
        }

        for category, words in keywords.items():
            if any(word in text for word in words):
                return category
        return "general"

    def _detect_intent(self, tokens: List[Token]) -> str:
        text = " ".join(t.value for t in tokens if t.type != TokenType.EOF).lower()

        if "how much" in text or "how" in text and "much" in text:
            return "question"
        if any(word in text for word in ["drop", "fill", "load", "give", "reduce", "come", "wait", "relax", "start"]):
            return "action"
        if any(word in text for word in ["done", "dey", "fit", "go"]):
            return "narration"
        return "statement"

    def _build_ast(self, tokens: List[Token]) -> SemanticNode:
        text = [token.value for token in tokens if token.type != TokenType.EOF]
        root = SemanticNode("Program")
        root.children.append(SemanticNode("Statement", " ".join(text)))
        return root

    def analyze(self, statement: str) -> Dict[str, Any]:
        """Perform semantic classification on a statement."""
        tokens = self.analyzer.tokenize(statement)
        tree, success, _ = parse_statement(statement)

        category = self._detect_category(tokens)
        intent = self._detect_intent(tokens)

        return {
            "tokens": tokens,
            "category": category,
            "intent": intent,
            "valid_syntax": bool(success),
            "ast": self._build_ast(tokens),
        }

    def generate_report(self, output_file: str = "analysis/semantic_report.json") -> str:
        """Write a JSON report for all statements from the project corpus."""
        from pathlib import Path

        import corpus as _corpus
        corpus = _corpus.texts()

        report = {
            "project": "AFJEN Compiler",
            "statements": [],
        }

        for index, statement in enumerate(corpus, start=1):
            result = self.analyze(statement)
            report["statements"].append({
                "id": f"stmt_{index:03d}",
                "text": statement,
                "category": result["category"],
                "intent": result["intent"],
                "valid_syntax": result["valid_syntax"],
                "ast": {
                    "kind": result["ast"].kind,
                    "children": [child.kind for child in result["ast"].children],
                },
            })

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(json.dumps(report, indent=2, ensure_ascii=False), encoding="utf-8")
        return str(output_path)

    def generate_summary(self, output_file: str = "analysis/semantic_summary.txt") -> str:
        """Write a human-readable summary from the same corpus."""
        from pathlib import Path

        import corpus as _corpus
        corpus = _corpus.texts()

        lines = [
            "AFJEN COMPILER SEMANTIC SUMMARY",
            "=" * 38,
        ]

        for index, statement in enumerate(corpus, start=1):
            result = self.analyze(statement)
            lines.append(f"{index:02d}. {result['category']} | {result['intent']} | {'VALID' if result['valid_syntax'] else 'INVALID'}")
            lines.append(f"    {statement}")
            lines.append("")

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text("\n".join(lines), encoding="utf-8")
        return str(output_path)


def main():
    examples = [
        "Brother, drop me na at Carrefour Yaoundé, the traffic done tire me small",
        "How much for this phone airtime? OK, load me two thousand balance make I browse",
        "The light done cut again, zéro-zéro, na generator we dey use since morning",
    ]

    semantic = SemanticAnalyzer()
    for sentence in examples:
        result = semantic.analyze(sentence)
        print(f"Sentence: {sentence}")
        print(f"Category: {result['category']}")
        print(f"Intent: {result['intent']}")
        print(f"Valid syntax: {result['valid_syntax']}")
        print(result['ast'])
        print("-" * 80)


if __name__ == "__main__":
    main()
