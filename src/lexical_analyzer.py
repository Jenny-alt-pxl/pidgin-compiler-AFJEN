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
    PIDGIN_MARKER = "PIDGIN_MARKER"  # na, am, me, small (discourse particles)
    NEGATION = "NEGATION"            # no
    SUBJUNCTIVE = "SUBJUNCTIVE"      # make (as in "make we go")
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


# words taught by the user (see userdict.py): word -> TokenType, applied to words the catch-all would call NOUN
USER_TOKEN_TYPES = {}


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

            # Interjections / slang (before generic words; zéro-zéro contains a hyphen)
            (r"(?<![\wé-])(garrr|zéro-zéro|ekiee|hmmm|OK|Eh|ooo|wahala|abeg|ehh|haba|chai)(?![\wé-])", TokenType.INTERJECTION),

            # Pidgin aspect auxiliaries: dey (progressive), done/don (perfect), fit (can)
            (r"\b(dey|di|done|don|fit|wan|mos|bin)\b", TokenType.PIDGIN_VERB),

            # Negation and subjunctive marker
            (r"\bno\b", TokenType.NEGATION),
            (r"\bmake\b", TokenType.SUBJUNCTIVE),

            # Question words
            (r"\b(How|Why|What|where|wetin|who|when)\b", TokenType.QUESTION_WORD),

            # Pidgin particles
            (r"\b(na|am|me|small)\b", TokenType.PIDGIN_MARKER),

            # Connectors
            (r"\b(and|but|or)\b", TokenType.CONNECTOR),
            (r"[,]", TokenType.CONNECTOR),  # Comma as connector

            # Prepositions
            (r"\b(at|for|in|on|before|after|since|from|with|to)\b", TokenType.PREPOSITION),

            # Determiners
            (r"\b(the|a|an|this|that|these|those|dis|dat|my|your|our|their|his)\b", TokenType.ARTICLE),

            # Pronouns (it's = it + copula)
            (r"\bit's\b", TokenType.PRONOUN),
            (r"\b(I|we|you|him|her|it|they|she|he|wuna|una|yu|mi|wi)\b", TokenType.PRONOUN),

            # Numbers (digits or number words)
            (r"\b\d+\b", TokenType.NUMBER),
            (r"\b(one|two|three|four|five|six|seven|eight|nine|ten|hundred|thousand)\b", TokenType.NUMBER),

            # Adverbs (before adjectives so "too" stays an adverb)
            (r"\b(again|so|too|just|even|already|always|never|neva|neba|now|down(?!-)|pass|ahead|here|there|today|tomorrow|soon|late|early)\b", TokenType.ADVERB),

            # Adjectives
            (r"(?<![\wé-])(fresh|good|scarce|crowded|cher|down-down|much|careful|tired|slow|cheap|expensive|wet|hot|cold|heavy|dark|long|hungry|big|bad|new)(?![\wé-])", TokenType.ADJECTIVE),

            # Proper nouns
            (r"\b(Yaoundé|Carrefour|Mambanda|MTN|Mama|Brother|Prof|ICT)\b", TokenType.PROPER_NOUN),

            # Verbs
            (r"\b(drop|tire|hala|try|cut|remain|fill|go|waka|take|load|start|finish|work|charge|reduce|browse|relax|say|come|use|give|wait|empty|fall|stuck|restart|become|be|sit|do|buy|see|know|reach|stop|pay|drive|park|arrive|move|sell|cook|eat|drink|call|send|ask|tell|carry|bring|leave|stay|open|close|sleep|cost|pick|stand|hold|climb|turn|run|walk|show|sabi|komot|tif|dance|talk|look|want|need|like|love|help|think|tchop)\b", TokenType.VERB),

            # Nouns (catch-all for remaining words; accents, hyphens, apostrophes allowed inside)
            (r"[a-zà-ÿ]+(?:[-'][a-zà-ÿ]+)*", TokenType.NOUN),

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
            
            if matched and token_type == TokenType.NOUN and tokens[-1].value.lower() in USER_TOKEN_TYPES:
                tokens[-1].type = USER_TOKEN_TYPES[tokens[-1].value.lower()]

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
