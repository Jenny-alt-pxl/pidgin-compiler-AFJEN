"""
Lexical Analyzer for Yaoundé Urban Communication
CS4110 - Compiler Construction
Lexical analysis of informal Yaoundé statements
"""

import re
from enum import Enum
from dataclasses import dataclass
from typing import List, Optional, Tuple


class TokenType(Enum):
    """Token type enumeration"""
    # Structural
    NOUN = "NOUN"
    VERB = "VERB"
    PIDGIN_VERB = "PIDGIN_VERB"
    PRONOUN = "PRONOUN"
    ARTICLE = "ARTICLE"
    PREPOSITION = "PREPOSITION"
    
    # Modifiers
    ADJECTIVE = "ADJECTIVE"
    ADVERB = "ADVERB"
    INTERJECTION = "INTERJECTION"
    SLANG = "SLANG"
    CODE_MIXED = "CODE_MIXED"
    
    # Other
    NUMBER = "NUMBER"
    PROPER_NOUN = "PROPER_NOUN"
    CONNECTOR = "CONNECTOR"
    QUESTION_WORD = "QUESTION_WORD"
    PUNCTUATION = "PUNCTUATION"
    
    # Special
    PIDGIN_MARKER = "PIDGIN_MARKER"  # na, am, me (as particle), go (as auxiliary)
    EOF = "EOF"


@dataclass
class Token:
    """Token representation"""
    type: TokenType
    value: str
    line: int
    column: int
    
    def __repr__(self):
        return f"Token({self.type.value}, '{self.value}', L{self.line}:C{self.column})"


class LexicalAnalyzer:
    """Lexical analyzer for Yaoundé statements"""
    
    def __init__(self):
        """Initialize token patterns"""
        
        # Define token patterns in order of priority
        self.token_patterns = [
            # Code-mixed expressions (must come early)
            (r"\bmon\s+Dieu\b", TokenType.CODE_MIXED),
            (r"\bc'est\s+cher\b", TokenType.CODE_MIXED),
            (r"\bJe\s+wanda\b", TokenType.CODE_MIXED),
            
            # Pidgin verbs (specific)
            (r"\b(dey|done|fit|waka|go)\b(?!\s*\S*ing)", TokenType.PIDGIN_VERB),
            
            # Question words
            (r"\b(How|Why|What|where)\b", TokenType.QUESTION_WORD),
            
            # Interjections
            (r"\b(garrr|zéro-zéro|ekiee|hmmm|OK|Eh|ooo)\b", TokenType.INTERJECTION),
            
            # Pidgin markers/particles
            (r"\b(na|am|me|small)\b(?!\s+\w+ing)", TokenType.PIDGIN_MARKER),
            
            # Connectors
            (r"\b(and|but|or)\b", TokenType.CONNECTOR),
            (r"[,]", TokenType.CONNECTOR),  # Comma as connector
            
            # Prepositions
            (r"\b(at|for|in|on|before|since)\b", TokenType.PREPOSITION),
            
            # Articles
            (r"\b(the|a|an)\b", TokenType.ARTICLE),
            
            # Pronouns
            (r"\b(I|we|you|me|him|her|it|they)\b", TokenType.PRONOUN),
            
            # Adjectives
            (r"\b(small|fresh|good|scarce|crowded|cher|down-down|too\s+much|careful|tired)\b", TokenType.ADJECTIVE),
            
            # Adverbs
            (r"\b(again|so|too|just|even|already|always)\b", TokenType.ADVERB),
            
            # Proper nouns (capitalized)
            (r"\b(Yaoundé|Carrefour|Mambanda|MTN|Mama|Brother|Prof|ICT)\b", TokenType.PROPER_NOUN),
            
            # Verbs (general, must come after specific verbs)
            (r"\b(drop|tire|hala|try|cut|remain|fill|go|take|load|start|finish|work|fit|charge|reduce|browse|relax|say|come|use|give|wait|empty|pass|fall|stuck|restart)\b", TokenType.VERB),
            
            # Nouns (catch-all, but exclude known non-nouns)
            (r"\b[a-z]+(?:skin|er|ey|or|ment|time)?\b", TokenType.NOUN),
            
            # Numbers
            (r"\b\d+(?:\s+\d+)?\b", TokenType.NUMBER),
            
            # Punctuation
            (r"[.!?\"'\-]", TokenType.PUNCTUATION),
        ]
        
        # Compile patterns
        self.compiled_patterns = [
            (re.compile(pattern, re.IGNORECASE), token_type)
            for pattern, token_type in self.token_patterns
        ]
    
    def tokenize(self, text: str) -> List[Token]:
        """
        Tokenize input text
        
        Args:
            text: Input statement to tokenize
            
        Returns:
            List of Token objects
        """
        tokens = []
        line = 1
        column = 1
        i = 0
        
        # Remove extra whitespace
        text = text.strip()
        
        while i < len(text):
            # Skip whitespace
            if text[i].isspace():
                if text[i] == '\n':
                    line += 1
                    column = 1
                else:
                    column += 1
                i += 1
                continue
            
            # Try to match patterns
            matched = False
            for pattern, token_type in self.compiled_patterns:
                match = pattern.match(text, i)
                if match:
                    value = match.group(0)
                    tokens.append(Token(token_type, value, line, column))
                    column += len(value)
                    i = match.end()
                    matched = True
                    break
            
            if not matched:
                # Unknown character, skip or handle as error
                column += 1
                i += 1
        
        tokens.append(Token(TokenType.EOF, "", line, column))
        return tokens
    
    def print_tokens(self, tokens: List[Token]):
        """Pretty print tokens"""
        print(f"{'Type':<15} {'Value':<20} {'Line:Col':<10}")
        print("-" * 45)
        for token in tokens:
            if token.type != TokenType.EOF:
                print(f"{token.type.value:<15} {token.value:<20} {token.line}:{token.column:<8}")


def main():
    """Test the lexical analyzer"""
    
    # Test statements
    test_statements = [
        "Brother, drop me na at Carrefour Yaoundé, the traffic done tire me small",
        "Hala me small money, na five hundred francs remain for transport",
        "Eh mon Dieu, internet dey do again? I don try restart modem, garrr nothing!",
        "The light done cut again, zéro-zéro, na generator we dey use since morning",
        "Je wanda why MTN network no fit work for this quarter, it's always down-down",
    ]
    
    analyzer = LexicalAnalyzer()
    
    for stmt_num, stmt in enumerate(test_statements, 1):
        print(f"\n{'='*60}")
        print(f"STATEMENT {stmt_num}: {stmt}")
        print(f"{'='*60}")
        
        tokens = analyzer.tokenize(stmt)
        analyzer.print_tokens(tokens)
        
        # Print token count and types
        token_types = {}
        for token in tokens:
            if token.type != TokenType.EOF:
                type_name = token.type.value
                token_types[type_name] = token_types.get(type_name, 0) + 1
        
        print("\nToken Summary:")
        for type_name, count in sorted(token_types.items()):
            print(f"  {type_name}: {count}")


if __name__ == "__main__":
    main()
