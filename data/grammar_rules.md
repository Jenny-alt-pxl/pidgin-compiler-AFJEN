# Grammar Rules (LL(1))

Generated from `src/grammar.py`. Terminals are lexer token types; ε is the empty string.
State 0 / state 1 (`U0`,`BODY0`,`R0` vs `F1`,`G1`,`BODY1`,`R1`) track whether a predicate
has been seen: every valid statement must contain at least one predicate.

```
S        → U0
U0       → PARTS U0B
U0B      → BODY0
         | SEPS U0
BODY0    → NP PARTS R0
         | IMP F1
         | QCL F1
         | SUBCL F1
         | PREPOSITION PPX SEPS U0
R0       → PRED F1
         | SEPS U0
         | PRONOUN PARTS R0
         | ARTICLE NPB PARTS R0
F1       → SEPS G1
         | ε
G1       → PARTS G2
G2       → BODY1
         | SEPS G1
         | ε
BODY1    → NP PARTS R1
         | IMP F1
         | QCL F1
         | SUBCL F1
         | PREPOSITION PPX F1
         | ADJP F1
         | NEGATION PARTS F1
R1       → PRED F1
         | PRONOUN PARTS R1
         | ARTICLE NPB PARTS R1
         | F1
SEPS     → SEP
SEP      → CONNECTOR
         | PUNCTUATION
PARTS    → PART PARTS
         | ε
PART     → PIDGIN_MARKER
         | INTERJECTION
         | CODE_MIXED
PRED     → VP
         | ADJP COMPS
         | PREPOSITION PPX
IMP      → VERB VTAIL
VP       → NEGATION VP
         | PIDGIN_VERB VPA
         | VERB VTAIL
VPA      → VERB VTAIL
         | ADJP COMPS
         | PREPOSITION PPX
         | ε
VTAIL    → VERB VTAIL
         | COMPS
ADJP     → ADVERB ADJP
         | ADJECTIVE
COMPS    → NP COMPSA
         | PREPOSITION PPX
         | NONNP COMPS
         | SUBCL
         | ε
COMPSA   → PREPOSITION PPX
         | NONNP COMPS
         | SUBCL
         | ε
NONNP    → PART
         | ADVERB
         | ADJECTIVE
SUBCL    → SUBJUNCTIVE NP PARTS VP
QCL      → QUESTION_WORD QA
QA       → ADJECTIVE QA
         | ADVERB QA
         | PREPOSITION PPX
         | NP QB
         | ε
QB       → VP
         | ε
PPX      → VP
         | NP PPY
PPY      → VP
         | COMPSA
NP       → ARTICLE NPB
         | NPB
NPB      → NUMBER NPB2
         | NOUN NPB2
         | PROPER_NOUN NPB2
         | PRONOUN
NPB2     → NUMBER NPB2
         | NOUN NPB2
         | PROPER_NOUN NPB2
         | ε
```

* Non-terminals: 32
* Productions: 88
* Terminals: 18 (ADJECTIVE, ADVERB, ARTICLE, CODE_MIXED, CONNECTOR, INTERJECTION, NEGATION, NOUN, NUMBER, PIDGIN_MARKER, PIDGIN_VERB, PREPOSITION, PRONOUN, PROPER_NOUN, PUNCTUATION, QUESTION_WORD, SUBJUNCTIVE, VERB)
* Left recursion: none (removed - see report section 3.2)
* Left factoring: applied (VP/VTAIL, PPX/PPY, COMPS/COMPSA, NPB/NPB2)
* LL(1) conflicts: 0
