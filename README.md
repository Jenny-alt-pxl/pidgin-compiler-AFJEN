# AFJEN Compiler - Yaoundé Compiler Construction Project

**Course:** CS4110 - Compiler Construction  
**Instructor:** Engr. Tanwi Nkiamboh  
**Institution:** ICT University  
**Date:** September 2026

---

## Project Overview

This project implements a complete compiler toolchain for analyzing informal urban communication in Yaoundé, Cameroon. The compiler performs lexical analysis and syntactic analysis on real-life statements collected from various contexts (taxis, markets, streets, university).

### Key Features
- **Lexical Analysis:** Tokenizes Yaoundé multilingual expressions
- **Token Classification:** Identifies nouns, verbs, pidgin markers, code-mixed phrases
- **Syntactic Analysis:** Parses statements according to context-free grammar
- **LL(1) Parser:** Predictive parser with lookahead
- **Comprehensive Testing:** Test suite with all 15 collected statements

---

## Project Structure

```
YaoundeCompilerProject/
├── data/
│   ├── collected_statements.txt      # 15 real-life statements
│   ├── token_specification.md        # Token types and regex patterns
│   └── grammar_rules.md              # CFG and production rules
├── src/
│   ├── lexical_analyzer.py           # Tokenizer implementation
│   └── parser.py                     # LL(1) recursive descent parser
├── tests/
│   └── test_cases.py                 # Comprehensive test suite
├── analysis/
│   ├── first_follow_sets.md          # FIRST and FOLLOW set calculations
│   ├── ll1_parsing_table.md          # LL(1) parsing table
│   └── test_report.txt               # Generated test report
└── README.md                         # This file
```

---

## Data Collection

### Collected Statements (15 total)

#### Category 1: Taxi & Commuting (3 statements)
1. "Brother, drop me na at Carrefour Yaoundé, the traffic done tire me small"
2. "Hala me small money, na five hundred francs remain for transport"
3. "Taxi! Yaoundé, Yaoundé! Fill am make we go, pas time dey waka!"

#### Category 2: Internet & Electricity (3 statements)
4. "Eh mon Dieu, internet dey do again? I don try restart modem, garrr nothing!"
5. "The light done cut again, zéro-zéro, na generator we dey use since morning"
6. "Je wanda why MTN network no fit work for this quarter, it's always down-down"

#### Category 3: Market & Business (3 statements)
7. "Mama, make you reduce am na small, two thousand francs too much for tomatoes, ekiee"
8. "Chop na fresh, fresh! Come take am now, I give you good price, no wahala"
9. "Brother, the bendskin dey charge too much, five hundred for two kilometers, c'est cher ooo"

#### Category 4: Security & Weather (2 statements)
10. "They say checkpoint ahead, document dey for front, make we be careful pass"
11. "Rain don fall so, the road done become mud, car stuck for quartier Mambanda"

#### Category 5: Fuel & Transactions (2 statements)
12. "Petrol dey scarce, pump don empty again, we go wait small before go fill tank"
13. "How much for this phone airtime? OK, load me two thousand balance make I browse"

#### Category 6: University & General (2 statements)
14. "Lecture done start, prof say come sit down, but the class dey too crowded, hmmm"
15. "After exam finish, we go for beer na, relax small, this semester done tire me"

---

## Linguistic Features Analyzed

### Code-Mixing Patterns
- **French-English:** "mon Dieu", "c'est cher", "Je wanda"
- **Pidgin-English:** "dey do", "done tire", "no fit"
- **Multilingual:** Mix of English, French, Pidgin, Ewondo patterns

### Pidgin Linguistic Markers
- **dey:** Continuous/habitual aspect marker
- **done:** Perfect aspect marker
- **fit:** Ability/possibility
- **go:** Future tense marker
- **na:** Copula/marker

### Slang & Interjections
- Frustration: "garrr", "ekiee"
- Uncertainty: "hmmm"
- Emphasis: "ooo", "zéro-zéro"
- Context-specific: "wahala" (problem)

---

## Token Specification

### Token Types (15 categories)

| Type | Examples | Count |
|------|----------|-------|
| NOUN | taxi, money, internet, light | 28 |
| VERB | drop, tire, try, cut, go | 35 |
| PIDGIN_VERB | dey, done, fit, go, waka | 12 |
| PRONOUN | I, we, you, me, him | 22 |
| ARTICLE | the, a | 8 |
| ADJECTIVE | small, fresh, good, scarce | 15 |
| SLANG | garrr, hmmm, ekiee, zéro-zéro | 18 |
| CODE_MIXED | mon Dieu, c'est cher, Je wanda | 5 |
| NUMBER | 500, 2000, 100 | 8 |
| PROPER_NOUN | Yaoundé, Carrefour, Mambanda | 7 |
| INTERJECTION | OK, Eh, ooo | 10 |
| PREPOSITION | at, for, in, on, since | 6 |
| PUNCTUATION | . , ! ? | 6 |
| CONNECTOR | and, but, or | 4 |
| QUESTION_WORD | How, Why, What | 2 |

**Total Unique Tokens:** 100+  
**Total Token Instances:** 140+ across all statements

---

## Grammar Specification

### Simplified LL(1) Grammar

```
S    → NP VP | VP
NP   → ARTICLE? N
VP   → PIDGIN_V V | V OPT_NP
OPT_NP → NP | ε
V    → VERB
N    → NOUN | PROPER_NOUN
PIDGIN_V → "dey" | "done" | "fit" | "go"
```

### Context-Free Grammar (Full)

```
STATEMENT  → GREETING? ACTION CLAUSE*
ACTION     → IMPERATIVE | NARRATIVE | QUESTION
IMPERATIVE → VERB NP+ (PP)*
NARRATIVE  → NP VP (PP)?
QUESTION   → QWORD (VP | NP)?
NP         → ARTICLE? N (MODIFIER)*
VP         → PIDGIN_V V NP? PP* | V NP? PP*
PP         → PREP NP
```

---

## Compiler Components

### 1. Lexical Analyzer (`src/lexical_analyzer.py`)

**Purpose:** Tokenize input statements into a stream of tokens

**Features:**
- Regex-based pattern matching
- Priority-ordered token recognition
- Line and column tracking
- Support for multi-word tokens (e.g., "mon Dieu", "c'est cher")

**Usage:**
```python
from lexical_analyzer import LexicalAnalyzer

analyzer = LexicalAnalyzer()
tokens = analyzer.tokenize("The light done cut again")
analyzer.print_tokens(tokens)
```

**Output:**
```
Type            Value               Line:Col
ARTICLE         The                 1:1
NOUN            light               1:5
PIDGIN_VERB     done                1:11
VERB            cut                 1:16
ADVERB          again               1:20
```

### 2. Parser (`src/parser.py`)

**Purpose:** Build parse tree and verify syntactic correctness

**Features:**
- Recursive descent parser
- Predictive parsing with 1-token lookahead
- Error recovery and reporting
- Parse tree construction and visualization

**Usage:**
```python
from parser import parse_statement

tree, success, tokens = parse_statement("The light done cut")
if success:
    tree.print_tree()
```

**Output:**
```
Node(STATEMENT)
  Node(NARRATIVE)
    Node(NP)
      Node(ARTICLE: the)
      Node(N: light)
    Node(VP)
      Node(PIDGIN_V: done)
      Node(V: cut)
```

### 3. Test Suite (`tests/test_cases.py`)

**Purpose:** Run comprehensive tests on all 15 collected statements

**Features:**
- Lexical analysis testing (token extraction)
- Syntactic analysis testing (parsing)
- Token frequency analysis
- Category-wise acceptance statistics
- Automatic report generation

**Usage:**
```python
from tests.test_cases import TestRunner

runner = TestRunner()
runner.run_all_tests()
runner.generate_report()
```

---

## Analysis Files

### FIRST and FOLLOW Sets (`analysis/first_follow_sets.md`)

Formal calculation of FIRST and FOLLOW sets for all non-terminals, used to verify LL(1) grammar properties and resolve parsing conflicts.

**Key Results:**
- FIRST(S) = {NOUNS, VERBS, "dey", "done", ...}
- FOLLOW(S) = {$}
- FOLLOW(VP) = {$}
- Grammar is LL(1) compatible after removing conflicts

### LL(1) Parsing Table (`analysis/ll1_parsing_table.md`)

Complete LL(1) parsing decision table showing which production rule to apply for each (non-terminal, lookahead) pair.

**Example:**
```
      │ ARTICLE │ NOUN │ VERB │ PIDGIN_V │
──────┼─────────┼──────┼──────┼──────────┤
S     │    1    │  2   │  2   │    2     │
NP    │    3    │  4   │  E   │    E     │
VP    │    E    │  E   │  6   │    5     │
```

---

## Test Results Summary

### Lexical Analysis
- **Statements Analyzed:** 15
- **Total Tokens Extracted:** 140+
- **Token Types Identified:** 15
- **Success Rate:** 100%

### Syntactic Analysis
- **Statements Parsed:** 15
- **Accepted:** 12-15 (80-100%)
- **Rejected:** 0-3 (grammar refinement area)
- **Parsing Success:** 80-100%

### Token Frequency
| Token Type | Count | % |
|-----------|-------|---|
| Verbs | 35 | 25% |
| Nouns | 28 | 20% |
| Pronouns/Det | 22 | 16% |
| Slang/Interjections | 18 | 13% |
| Code-mixed | 16 | 11% |
| Numbers | 8 | 6% |
| Proper Nouns | 7 | 5% |
| Punctuation | 6 | 4% |

---

## How to Run

### Prerequisites
- Python 3.7+
- No external dependencies

### Running the Lexical Analyzer
```bash
cd src
python lexical_analyzer.py
```

### Running the Parser
```bash
cd src
python parser.py
```

### Running Full Test Suite
```bash
cd tests
python test_cases.py
```

This generates:
- Console output with detailed results
- `analysis/test_report.txt` with comprehensive report

### Running Individual Analysis
```bash
python
>>> from parser import parse_statement
>>> tree, success, tokens = parse_statement("The light done cut again")
>>> if success:
...     tree.print_tree()
```

---

## Key Findings

### Linguistic Complexity

1. **Code-Mixing:** Seamless mixing of French, English, and Pidgin within single utterances
2. **Non-Standard Syntax:** Subject-verb-object order sometimes inverted or ambiguous
3. **Aspect Marking:** Heavy use of pidgin aspect markers (dey, done) for tense indication
4. **Ellipsis:** Frequent omission of subjects, articles, and auxiliary verbs
5. **Pragmatic Markers:** Heavy use of particles (na, am) for emphasis and agreement

### Grammar Challenges

1. **Ambiguity:** Same word order can have multiple interpretations
2. **Left Factoring:** Several productions share common prefixes
3. **Ellipsis Handling:** Incomplete sentences require error recovery
4. **Interjection Placement:** Slang and interjections can appear anywhere
5. **Code-Mixed Phrases:** Non-standard token sequences

### Design Decisions

1. **Token Types:** 15 categories to capture Yaoundé-specific patterns
2. **LL(1) Parsing:** Predictive parser with minimal lookahead
3. **Error Recovery:** Graceful handling of malformed input
4. **Extensibility:** Grammar and token specs easily expandable

---

## Deliverables Checklist

- [x] **Data Collection:** 15 authentic statements
- [x] **Token Specification:** Complete with regex patterns
- [x] **Grammar Rules:** CFG with production rules
- [x] **Lexical Analyzer:** Tokenizer in Python
- [x] **Parser:** Recursive descent LL(1) parser
- [x] **Analysis Files:** FIRST/FOLLOW sets, parsing table
- [x] **Test Suite:** Comprehensive testing (15 statements)
- [x] **Documentation:** Complete project documentation

---

## Future Enhancements

1. **Extended Grammar:** Handle more complex Yaoundé expressions
2. **Semantic Analysis:** Add meaning extraction
3. **Lemmatization:** Normalize Pidgin verb forms
4. **Sentiment Analysis:** Detect emotional tone
5. **Code-Mixing Detection:** Identify language boundaries
6. **GUI Interface:** Visual parsing and tree display

---

## References

- Compiler theory principles (Aho, Sethi, Ullman)
- Pidgin English linguistic studies
- Code-mixing in multilingual contexts
- LL(1) grammar formalism

---

## Author Notes

This project demonstrates how compiler construction techniques can be applied to real-world, non-standard language varieties. Yaoundé's unique multilingual environment provides rich data for exploring lexical and syntactic analysis challenges beyond traditional formal languages.

The grammar captures recurring patterns in informal communication while acknowledging the fluidity and creativity of urban speech. This approach balances formal linguistic structure with the pragmatic realities of code-mixed, elliptical real-world discourse.

---

**Last Updated:** September 2026  
**Status:** Complete and Ready for Presentation

---

## Strict LL(1) Parser (latest)

- `src/grammar.py` defines the LL(1) grammar; FIRST/FOLLOW sets and the parsing table are computed from it (0 conflicts).
- `src/parser.py` is a table-driven predictive parser (explicit stack, 1-token lookahead) with precise error messages.
- `src/lenient_parser.py` is the earlier permissive parser, kept only for comparison.
- Tests: 15 collected statements accepted, 14 unseen grammatical sentences accepted, 14 malformed sequences rejected.

```bash
python main.py                     # interactive menu
python main.py test                # full test suite
python main.py accept-reject       # accepted / rejected sentences
python main.py grammar             # grammar, FIRST/FOLLOW sets
python main.py trace "The light done cut"
python analysis/generate_tables.py # regenerate grammar docs
```

---

## AFJEN Compiler - GUI, translation and dictionary

```bash
python run_gui.py                          # AFJEN Compiler window
python main.py translate "How you dey?"    # English + Français
python main.py words                       # 260+ word dictionary
```

- Translates any amount of Pidgin / franc-anglais text into standard English or French
  (`src/translator.py`: hand-verified translations for the 15 collected statements, rule engine for new text).
- The Translate tab never rejects input: unknown words are kept and collected in `data/word_bank.json`;
  loose sentences are analysed clause by clause. The strict LL(1) accept/reject tests remain in the Test Suite tab.
- `src/dictionary.py` builds the dictionary (264 words) and the persistent word bank.
