"""
Parser for Yaoundé Urban Communication
CS4110 - Compiler Construction
Syntactic analysis of informal Yaoundé statements
"""

from typing import List, Optional, Tuple, Dict, Any
from dataclasses import dataclass, field
from lexical_analyzer import Token, TokenType, LexicalAnalyzer


@dataclass
class ParseNode:
    """Represents a node in the parse tree"""
    rule: str
    children: List['ParseNode'] = field(default_factory=list)
    token: Optional[Token] = None
    
    def __repr__(self):
        if self.token:
            return f"Node({self.rule}: {self.token.value})"
        return f"Node({self.rule})"
    
    def print_tree(self, indent=0):
        """Print parse tree in human-readable format"""
        print("  " * indent + str(self))
        for child in self.children:
            if isinstance(child, ParseNode):
                child.print_tree(indent + 1)
            else:
                print("  " * (indent + 1) + repr(child))

    def to_dict(self):
        """Convert to a nested dict structure for AST output."""
        if self.token is not None:
            return {
                "type": self.rule,
                "value": self.token.value,
                "token_type": self.token.type.value,
            }

        children = []
        for child in self.children:
            if isinstance(child, ParseNode):
                children.append(child.to_dict())
            else:
                children.append({"type": "TOKEN", "value": child.value, "token_type": child.type.value})

        return {
            "type": self.rule,
            "children": children,
        }


class Parser:
    """Recursive descent parser for Yaoundé statements"""
    
    def __init__(self, tokens: List[Token]):
        """
        Initialize parser with tokens
        
        Args:
            tokens: List of Token objects from lexical analyzer
        """
        self.tokens = tokens
        self.current = 0
        self.errors = []
    
    def peek(self) -> Token:
        """Get current token without consuming it"""
        if self.current < len(self.tokens):
            return self.tokens[self.current]
        return self.tokens[-1]  # EOF
    
    def advance(self) -> Token:
        """Consume and return current token"""
        token = self.peek()
        if token.type != TokenType.EOF:
            self.current += 1
        return token
    
    def expect(self, token_type: TokenType) -> Optional[Token]:
        """Expect a specific token type"""
        if self.peek().type == token_type:
            return self.advance()
        else:
            self.errors.append(f"Expected {token_type.value}, got {self.peek().type.value}")
            return None
    
    def match(self, *token_types: TokenType) -> bool:
        """Check if current token matches any of the given types"""
        return self.peek().type in token_types
    
    # ========== PARSING RULES ==========
    
    def parse(self) -> Tuple[Optional[ParseNode], bool]:
        """
        Main parsing entry point
        S → STATEMENT
        """
        node = self.parse_statement()
        
        # Success if we parsed a statement and are at or near EOF
        # (lenient parser doesn't require consuming all tokens)
        success = node is not None
        
        return node, success

    def parse_with_diagnostics(self) -> Tuple[Optional[ParseNode], bool, List[str]]:
        """Return parse tree and a readable list of parser diagnostics."""
        node = self.parse_statement()
        success = node is not None
        diagnostics = list(self.errors)
        if diagnostics:
            return node, success, diagnostics
        return node, success, ["No syntax errors detected."]
    
    def parse_statement(self) -> Optional[ParseNode]:
        """
        STATEMENT → ACTION CLAUSE*
        or STATEMENT → GREETING ACTION CLAUSE*
        Enhanced to handle real Yaoundé patterns
        """
        node = ParseNode("STATEMENT", [])
        
        # Check for optional greeting (Brother, Mama, etc.)
        if self.match(TokenType.PROPER_NOUN) and self.peek().value in ["Brother", "Mama", "Prof"]:
            greeting = self.advance()
            node.children.append(ParseNode("GREETING", [], greeting))
            # Skip optional comma/punctuation after greeting
            if self.match(TokenType.CONNECTOR, TokenType.PUNCTUATION):
                self.advance()
        
        # Parse multiple actions/clauses (separated by commas or connectors)
        action_count = 0
        while self.current < len(self.tokens) - 1:  # Until EOF
            action = self.parse_action_lenient()
            if action:
                node.children.append(action)
                action_count += 1
            else:
                # Try to skip punctuation and continue
                if self.match(TokenType.CONNECTOR, TokenType.PUNCTUATION, TokenType.INTERJECTION):
                    self.advance()
                    continue
                else:
                    break
            
            # Check for clause separator
            if self.match(TokenType.CONNECTOR, TokenType.PUNCTUATION):
                self.advance()
            else:
                break
        
        # Success if we parsed at least one action
        return node if action_count > 0 else None
    
    def parse_action(self) -> Optional[ParseNode]:
        """
        ACTION → IMPERATIVE | NARRATIVE | QUESTION
        """
        node = ParseNode("ACTION", [])
        
        # Try QUESTION first (starts with QUESTION_WORD or "How much")
        if self.match(TokenType.QUESTION_WORD):
            question = self.parse_question()
            if question:
                node.children.append(question)
                return node
        
        # Try IMPERATIVE (starts with VERB or VERB_PHRASE)
        if self.match(TokenType.VERB, TokenType.PIDGIN_VERB):
            imperative = self.parse_imperative()
            if imperative:
                node.children.append(imperative)
                return node
        
        # Try NARRATIVE (starts with NP or PRONOUN)
        if self.match(TokenType.ARTICLE, TokenType.PROPER_NOUN, TokenType.NOUN, TokenType.PRONOUN):
            narrative = self.parse_narrative()
            if narrative:
                node.children.append(narrative)
                return node
        
        self.errors.append(f"Expected ACTION at token {self.peek().value}")
        return None
    
    def parse_action_lenient(self) -> Optional[ParseNode]:
        """
        Lenient ACTION parser for real Yaoundé speech
        Accepts verb-initial, noun-initial, or fragment patterns
        """
        # Skip initial interjections
        while self.match(TokenType.INTERJECTION, TokenType.SLANG):
            self.advance()
        
        # End of statement
        if self.match(TokenType.EOF):
            return None
        
        node = ParseNode("ACTION", [])
        
        # Collect tokens until we hit a clause boundary
        phrase_tokens = []
        start_pos = self.current
        paren_depth = 0
        
        while self.current < len(self.tokens) - 1:
            token = self.peek()
            
            # Stop at clause boundaries
            if token.type in [TokenType.EOF]:
                break
            if token.type == TokenType.CONNECTOR and paren_depth == 0:
                break
            if token.type == TokenType.PUNCTUATION and token.value in [".", "?"]:
                phrase_tokens.append(self.advance())
                break
            
            phrase_tokens.append(self.advance())
        
        # Parse the collected tokens
        if phrase_tokens:
            # Try to identify main verb and objects
            verb_idx = None
            for i, token in enumerate(phrase_tokens):
                if token.type in [TokenType.VERB, TokenType.PIDGIN_VERB]:
                    verb_idx = i
                    break
            
            def wrap_tokens(tokens: List[Token]) -> ParseNode:
                return ParseNode("TOKENS", [ParseNode("TOKEN", token=token) for token in tokens])

            if verb_idx is not None:
                # Verb-based phrase
                node.children.append(ParseNode("PHRASE", [wrap_tokens(phrase_tokens[:verb_idx + 1])]))
                if verb_idx < len(phrase_tokens) - 1:
                    node.children.append(ParseNode("PHRASE", [wrap_tokens(phrase_tokens[verb_idx + 1:])]))
            else:
                # Noun-based or other phrase
                node.children.append(ParseNode("PHRASE", [wrap_tokens(phrase_tokens)]))
            
            return node
        
        return None
    
    def parse_imperative(self) -> Optional[ParseNode]:
        """
        IMPERATIVE → VERB NP+ | VERB NP PP+
        """
        node = ParseNode("IMPERATIVE", [])
        
        # Parse verb
        verb = self.parse_verb()
        if verb:
            node.children.append(verb)
        else:
            return None
        
        # Parse noun phrases
        np_count = 0
        while self.match(TokenType.ARTICLE, TokenType.NOUN, TokenType.PRONOUN, TokenType.PROPER_NOUN):
            np = self.parse_noun_phrase()
            if np:
                node.children.append(np)
                np_count += 1
            else:
                break
        
        # Parse prepositional phrases
        while self.match(TokenType.PREPOSITION):
            pp = self.parse_prepositional_phrase()
            if pp:
                node.children.append(pp)
            else:
                break
        
        if np_count > 0:
            return node
        
        self.errors.append("IMPERATIVE requires at least one noun phrase")
        return None
    
    def parse_narrative(self) -> Optional[ParseNode]:
        """
        NARRATIVE → NP VP | NP VP PP
        """
        node = ParseNode("NARRATIVE", [])
        
        # Parse noun phrase
        np = self.parse_noun_phrase()
        if np:
            node.children.append(np)
        else:
            self.errors.append("Expected NP in NARRATIVE")
            return None
        
        # Parse verb phrase
        vp = self.parse_verb_phrase()
        if vp:
            node.children.append(vp)
        else:
            self.errors.append("Expected VP in NARRATIVE")
            return None
        
        # Parse optional prepositional phrase
        if self.match(TokenType.PREPOSITION):
            pp = self.parse_prepositional_phrase()
            if pp:
                node.children.append(pp)
        
        return node
    
    def parse_question(self) -> Optional[ParseNode]:
        """
        QUESTION → QWORD VP? | QWORD NP?
        """
        node = ParseNode("QUESTION", [])
        
        # Parse question word
        qword = self.advance()
        node.children.append(ParseNode("QWORD", [], qword))
        
        # Parse optional VP or NP
        if self.match(TokenType.VERB, TokenType.PIDGIN_VERB):
            vp = self.parse_verb_phrase()
            if vp:
                node.children.append(vp)
        elif self.match(TokenType.ARTICLE, TokenType.NOUN, TokenType.PRONOUN):
            np = self.parse_noun_phrase()
            if np:
                node.children.append(np)
        
        return node
    
    def parse_clause(self) -> Optional[ParseNode]:
        """
        CLAUSE → ACTION
        """
        node = ParseNode("CLAUSE", [])
        action = self.parse_action()
        if action:
            node.children.append(action)
            return node
        return None
    
    def parse_verb_phrase(self) -> Optional[ParseNode]:
        """
        VP → PIDGIN_V V NP? PP* | V NP? PP*
        """
        node = ParseNode("VP", [])
        
        # Check for pidgin verb
        if self.match(TokenType.PIDGIN_VERB):
            pv = self.advance()
            node.children.append(ParseNode("PIDGIN_V", [], pv))
        
        # Parse main verb
        verb = self.parse_verb()
        if verb:
            node.children.append(verb)
        else:
            return None
        
        # Parse optional noun phrase
        if self.match(TokenType.ARTICLE, TokenType.NOUN, TokenType.PRONOUN, TokenType.PROPER_NOUN):
            np = self.parse_noun_phrase()
            if np:
                node.children.append(np)
        
        # Parse zero or more prepositional phrases
        while self.match(TokenType.PREPOSITION):
            pp = self.parse_prepositional_phrase()
            if pp:
                node.children.append(pp)
            else:
                break
        
        # Parse modifiers (adjectives, adverbs, slang)
        while self.match(TokenType.ADJECTIVE, TokenType.ADVERB, TokenType.SLANG, TokenType.INTERJECTION, TokenType.PIDGIN_MARKER):
            modifier = self.advance()
            node.children.append(ParseNode("MODIFIER", [], modifier))
        
        return node
    
    def parse_noun_phrase(self) -> Optional[ParseNode]:
        """
        NP → ARTICLE? N (MODIFIER)*
        """
        node = ParseNode("NP", [])
        
        # Optional article
        if self.match(TokenType.ARTICLE):
            article = self.advance()
            node.children.append(ParseNode("ARTICLE", [], article))
        
        # Noun (required)
        if self.match(TokenType.NOUN, TokenType.PROPER_NOUN):
            noun = self.advance()
            node.children.append(ParseNode("N", [], noun))
        else:
            self.errors.append(f"Expected NOUN in NP, got {self.peek().type.value}")
            return None
        
        # Zero or more modifiers
        while self.match(TokenType.ADJECTIVE, TokenType.ADVERB, TokenType.NUMBER):
            modifier = self.advance()
            node.children.append(ParseNode("MODIFIER", [], modifier))
        
        return node
    
    def parse_verb(self) -> Optional[ParseNode]:
        """
        V → VERB
        """
        if self.match(TokenType.VERB):
            verb = self.advance()
            return ParseNode("V", [], verb)
        self.errors.append(f"Expected VERB, got {self.peek().type.value}")
        return None
    
    def parse_prepositional_phrase(self) -> Optional[ParseNode]:
        """
        PP → PREP NP
        """
        node = ParseNode("PP", [])
        
        # Preposition
        if self.match(TokenType.PREPOSITION):
            prep = self.advance()
            node.children.append(ParseNode("PREP", [], prep))
        else:
            return None
        
        # Noun phrase
        np = self.parse_noun_phrase()
        if np:
            node.children.append(np)
        else:
            self.errors.append("Expected NP after PREP")
            return None
        
        return node


def parse_statement(statement: str) -> Tuple[Optional[ParseNode], bool, List[Token]]:
    """
    Convenience function to parse a statement
    
    Args:
        statement: Input statement string
        
    Returns:
        Tuple of (parse_tree, success, tokens)
    """
    analyzer = LexicalAnalyzer()
    tokens = analyzer.tokenize(statement)
    parser = Parser(tokens)
    tree, success = parser.parse()
    return tree, success, tokens


def parse_statement_detailed(statement: str) -> Tuple[Optional[ParseNode], bool, List[Token], List[str]]:
    """Parse a statement and attach detailed syntax diagnostics and AST data."""
    analyzer = LexicalAnalyzer()
    tokens = analyzer.tokenize(statement)
    parser = Parser(tokens)
    tree, success, diagnostics = parser.parse_with_diagnostics()
    return tree, success, tokens, diagnostics


def main():
    """Test the parser"""
    
    test_statements = [
        "Brother, drop me na at Carrefour Yaoundé, the traffic done tire me small",
        "Hala me small money, na five hundred francs remain for transport",
        "Taxi! Yaoundé, Yaoundé! Fill am make we go, pas time dey waka!",
        "Eh mon Dieu, internet dey do again? I don try restart modem, garrr nothing!",
        "The light done cut again, zéro-zéro, na generator we dey use since morning",
    ]
    
    for stmt_num, stmt in enumerate(test_statements, 1):
        print(f"\n{'='*70}")
        print(f"STATEMENT {stmt_num}: {stmt}")
        print(f"{'='*70}")
        
        tree, success, tokens = parse_statement(stmt)
        
        print(f"\nLexical Analysis ({len(tokens)-1} tokens):")
        for token in tokens[:-1]:  # Skip EOF
            print(f"  {token}")
        
        print(f"\nSyntactic Analysis: {'✓ ACCEPTED' if success else '✗ REJECTED'}")
        
        if tree:
            print("\nParse Tree:")
            tree.print_tree()
        
        if not success:
            parser = Parser(tokens)
            parser.parse()
            print(f"\nErrors: {parser.errors}")


if __name__ == "__main__":
    main()
