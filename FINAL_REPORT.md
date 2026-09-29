# YAOUNDÉ COMPILER CONSTRUCTION PROJECT
## Lexical and Syntactic Analysis of Informal Urban Communication in Yaoundé

**Course:** CS4110 - Compiler Construction | **Instructor:** Engr. Tanwi Nkiamboh  
**Institution:** ICT University - Faculty of Information and Communication Technologies  
**Examination:** Final Examination, Summer 2026 - Tuesday, September 29, 2026 (B.S. Chumbow Hall)  
**Group members:** _(fill in - groups of 3)_

> Structure follows the exam paper: 1 Data Collection, 2 Lexical Analysis, 3 Syntactic Analysis, 4 Implementation, 5 Deliverables (report contents, source code, presentation). Mark allocations are shown in each heading.

## Contents
1. Data Collection (10)
2. Lexical Analysis (10 + 10)
3. Syntactic Analysis (5 + 5 + 5 + 5)
4. Implementation (5 + 2 + 3)
5. Screenshots of the Working Analyzer
6. Source Code and Test Cases
7. Presentation and Demonstration (5)
8. Discussion: Why Yaoundé Communication Is Linguistically Complex
9. Challenges, Limitations and Future Work
10. Conclusion
- Appendices: A. How to run, B. File listing

---

## 1. DATA COLLECTION (10 marks)

### 1.1 Objective
Record 10-15 real statements heard in Yaoundé on the exam topics: taxi/commuting, internet, electricity, market bargaining, rainy season, fuel scarcity, roadside business, bendskin, security checkpoints, life at ICT University.

### 1.2 Method
- **15 statements** transcribed manually, keeping slang, code-mixing and non-standard spelling as spoken.
- Grouped into 6 topic categories.
- Source file: `data/collected_statements.txt`.

### 1.3 Raw Collected Statements

**Taxi & Commuting**
```
1. "Brother, drop me na at Carrefour Yaoundé, the traffic done tire me small"
2. "Hala me small money, na five hundred francs remain for transport"
3. "Taxi! Yaoundé, Yaoundé! Fill am make we go, pas time dey waka!"
```
**Internet & Electricity**
```
4. "Eh mon Dieu, internet dey do again? I don try restart modem, garrr nothing!"
5. "The light done cut again, zéro-zéro, na generator we dey use since morning"
6. "Je wanda why MTN network no fit work for this quarter, it's always down-down"
```
**Market Bargaining & Roadside Business (incl. bendskin)**
```
7. "Mama, make you reduce am na small, two thousand francs too much for tomatoes, ekiee"
8. "Chop na fresh, fresh! Come take am now, I give you good price, no wahala"
9. "Brother, the bendskin dey charge too much, five hundred for two kilometers, c'est cher ooo"
```
**Security & Rainy Season**
```
10. "They say checkpoint ahead, document dey for front, make we be careful pass"
11. "Rain don fall so, the road done become mud, car stuck for quartier Mambanda"
```
**Fuel Scarcity & Everyday Transactions**
```
12. "Petrol dey scarce, pump don empty again, we go wait small before go fill tank"
13. "How much for this phone airtime? OK, load me two thousand balance make I browse"
```
**University & General Slang**
```
14. "Lecture done start, prof say come sit down, but the class dey too crowded, hmmm"
15. "After exam finish, we go for beer na, relax small, this semester done tire me"
```

---

## 2. LEXICAL ANALYSIS

### 2.1 Token Identification (10 marks)
The analyzer recognises **18 token types**; on the 15 statements it produced **245 tokens** (average 16.3 per statement).

| Exam class | Token types | Examples from the data |
|---|---|---|
| Nouns | NOUN, PROPER_NOUN | taxi, light, modem, bendskin, quartier, Yaoundé, MTN |
| Verbs | VERB, PIDGIN_VERB (aspect markers) | drop, cut, restart / dey, done, don, fit |
| Slang | INTERJECTION | garrr, ekiee, hmmm, ooo, Eh, OK, wahala, zéro-zéro |
| Code-mixed (French + English + Pidgin) | CODE_MIXED, PIDGIN_MARKER | mon Dieu, c'est cher, Je wanda / na, am, me, small |
| Pidgin grammar words | NEGATION, SUBJUNCTIVE | no / make ("make we go") |
| Function words | PRONOUN, ARTICLE, PREPOSITION, CONNECTOR, ADJECTIVE, ADVERB, NUMBER, QUESTION_WORD, PUNCTUATION | I, the, for, but, fresh, again, five, How, "," |

### 2.2 Custom Lexical Specification
Custom lexical analyzer in Python (`src/lexical_analyzer.py`): one regular expression per token type, matched in priority order (multi-word code-mixed patterns first, then interjections, Pidgin auxiliaries, closed word classes, and a catch-all NOUN pattern last), with line:column tracking. Representative patterns (authoritative versions are in the source file):

| Token type | Regular expression |
|---|---|
| CODE_MIXED | `\bmon\s+Dieu\b`, `\bc'est\s+cher\b`, `\bJe\s+wanda\b` |
| INTERJECTION | `(garrr\|zéro-zéro\|ekiee\|hmmm\|OK\|Eh\|ooo\|wahala)` (with word-boundary look-arounds) |
| PIDGIN_VERB | `\b(dey\|done\|don\|fit)\b` |
| NEGATION / SUBJUNCTIVE | `\bno\b` / `\bmake\b` |
| PIDGIN_MARKER | `\b(na\|am\|me\|small)\b` |
| PREPOSITION | `\b(at\|for\|in\|on\|before\|after\|since\|from\|with\|to)\b` |
| NUMBER | `\b\d+\b` and `\b(one\|two\|...\|hundred\|thousand)\b` |
| CONNECTOR | `\b(and\|but\|or)\b` and `,` |
| NOUN (catch-all) | `[a-zà-ÿ]+(?:[-'][a-zà-ÿ]+)*` |
| PUNCTUATION | `[.!?"'\-]` |

### 2.3 Token Frequency and Variation (10 marks)
Counts produced by `python main.py test` on all 15 statements:

| Token type | Count | % |
|---|---|---|
| NOUN | 40 | 16.3% |
| VERB | 38 | 15.5% |
| CONNECTOR | 33 | 13.5% |
| PIDGIN_MARKER | 19 | 7.8% |
| PIDGIN_VERB | 16 | 6.5% |
| ADVERB | 12 | 4.9% |
| PREPOSITION | 12 | 4.9% |
| PRONOUN | 12 | 4.9% |
| ADJECTIVE | 10 | 4.1% |
| PROPER_NOUN | 10 | 4.1% |
| NUMBER | 9 | 3.7% |
| ARTICLE | 8 | 3.3% |
| INTERJECTION | 8 | 3.3% |
| PUNCTUATION | 7 | 2.9% |
| SUBJUNCTIVE | 4 | 1.6% |
| CODE_MIXED | 3 | 1.2% |
| NEGATION | 2 | 0.8% |
| QUESTION_WORD | 2 | 0.8% |
| **Total** | **245** | 100% |

**Variation observations**
- Pidgin markers + aspect verbs + `make`/`no` = 41/245 tokens (**16.7%**), a large share for a variety with no standard grammar.
- Nouns (16.3%) and verbs (15.5%) are nearly balanced; nouns cover objects (modem, tomatoes), places (checkpoint, quartier) and abstractions (internet, light).
- Interjections and code-mixed expressions are few (4.5% combined) but appear in most statements as emotional or social markers.
- The same form plays different roles: `go` = motion verb or future marker (handled as a serial verb); `fit` = English adjective or Pidgin "can"; `me` = pronoun or particle.

---

## 3. SYNTACTIC ANALYSIS (5 + 5 + 5 + 5 marks)

### 3.1 Context-Free Grammar
Target structure in EBNF (the informal design, before transformation):
```
STATEMENT  → UTTERANCE (SEPARATOR UTTERANCE)*            (at least one predicate)
UTTERANCE  → PARTICLE* ( NP | IMPERATIVE | QUESTION | SUBJUNCTIVE_CLAUSE | PP )
NARRATIVE  → NP PARTICLE* PREDICATE
PREDICATE  → VP | ADJP COMP* | PP
VP         → NEGATION* PIDGIN_VERB? VERB+ COMP*         (serial verbs: "say come sit down")
COMP       → NP | PP | PARTICLE | ADVERB | ADJECTIVE | SUBJUNCTIVE_CLAUSE
SUBJUNCTIVE_CLAUSE → "make" NP PARTICLE* VP              ("make we go")
QUESTION   → QUESTION_WORD (ADJECTIVE | ADVERB | PP | NP VP?)*
NP         → DETERMINER? (NUMBER | NOUN | PROPER_NOUN)+ | PRONOUN
PP         → PREPOSITION (NP | VP | NP VP)              ("for beer", "before go fill tank")
PARTICLE   → PIDGIN_MARKER | INTERJECTION | CODE_MIXED  (na, am, me, small, garrr, mon Dieu ...)
```
Two grammar "states" record whether a predicate has been seen, so a statement with no predicate
("Brother", "the the the") is rejected while noun fragments around a predicate
("Taxi! Yaoundé, Yaoundé! Fill am ...") are accepted.

### 3.2 Grammar Transformation Steps

**Step 0 - Remove EBNF operators.** `*`, `+` and `?` are not allowed in LL(1), so each is replaced by a
right-recursive helper non-terminal with an ε alternative (`PARTS`, `NPB2`, `COMPS`, `VTAIL`, ...).

**Step 1 - Remove left recursion.** Attaching phrases naturally gives left-recursive rules such as
```
NP → NP NOUN | NOUN            SEPS → SEPS SEP | SEP            VTAIL → VTAIL VERB | ...
```
A top-down parser would loop forever on these. Using A → Aα | β ⇒ A → βA', A' → αA' | ε:
```
NP → NPB      NPB → NOUN NPB2      NPB2 → NOUN NPB2 | ε
```
The final grammar contains no left recursion.

**Step 2 - Left factoring.** Alternatives with a common prefix would need more than one token of lookahead:
```
VP → VERB | VERB COMPS | VERB VP        ⇒   VP → VERB VTAIL ;  VTAIL → VERB VTAIL | COMPS
PP → PREP NP | PREP NP VP | PREP VP     ⇒   PPX → VP | NP PPY ;  PPY → VP | COMPSA
COMPS → NP | NP COMPS' ...              ⇒   COMPS → NP COMPSA | ... ;  COMPSA never starts with NP
```
`COMPSA` also removes the ambiguity between "NP followed by NP" and a compound noun: adjacent nouns are
always read as one compound noun (`Carrefour Yaoundé`, `phone airtime`).

**Final LL(1) grammar (32 non-terminals, 87 productions)**
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

### 3.3 FIRST and FOLLOW Sets
Computed by fixed-point iteration in `src/grammar.py` (program output, not hand estimates).

| Non-terminal | FIRST | FOLLOW |
|---|---|---|
| S | ARTICLE, CODE_MIXED, CONNECTOR, INTERJECTION, NOUN, NUMBER, PIDGIN_MARKER, PREPOSITION, PRONOUN, PROPER_NOUN, PUNCTUATION, QUESTION_WORD, SUBJUNCTIVE, VERB | $ |
| U0 | ARTICLE, CODE_MIXED, CONNECTOR, INTERJECTION, NOUN, NUMBER, PIDGIN_MARKER, PREPOSITION, PRONOUN, PROPER_NOUN, PUNCTUATION, QUESTION_WORD, SUBJUNCTIVE, VERB | $ |
| U0B | ARTICLE, CONNECTOR, NOUN, NUMBER, PREPOSITION, PRONOUN, PROPER_NOUN, PUNCTUATION, QUESTION_WORD, SUBJUNCTIVE, VERB | $ |
| BODY0 | ARTICLE, NOUN, NUMBER, PREPOSITION, PRONOUN, PROPER_NOUN, QUESTION_WORD, SUBJUNCTIVE, VERB | $ |
| R0 | ADJECTIVE, ADVERB, ARTICLE, CONNECTOR, NEGATION, PIDGIN_VERB, PREPOSITION, PRONOUN, PUNCTUATION, VERB | $ |
| F1 | CONNECTOR, PUNCTUATION, ε | $ |
| G1 | ADJECTIVE, ADVERB, ARTICLE, CODE_MIXED, CONNECTOR, INTERJECTION, NEGATION, NOUN, NUMBER, PIDGIN_MARKER, PREPOSITION, PRONOUN, PROPER_NOUN, PUNCTUATION, QUESTION_WORD, SUBJUNCTIVE, VERB, ε | $ |
| G2 | ADJECTIVE, ADVERB, ARTICLE, CONNECTOR, NEGATION, NOUN, NUMBER, PREPOSITION, PRONOUN, PROPER_NOUN, PUNCTUATION, QUESTION_WORD, SUBJUNCTIVE, VERB, ε | $ |
| BODY1 | ADJECTIVE, ADVERB, ARTICLE, NEGATION, NOUN, NUMBER, PREPOSITION, PRONOUN, PROPER_NOUN, QUESTION_WORD, SUBJUNCTIVE, VERB | $ |
| R1 | ADJECTIVE, ADVERB, ARTICLE, CONNECTOR, NEGATION, PIDGIN_VERB, PREPOSITION, PRONOUN, PUNCTUATION, VERB, ε | $ |
| SEPS | CONNECTOR, PUNCTUATION | $, ADJECTIVE, ADVERB, ARTICLE, CODE_MIXED, CONNECTOR, INTERJECTION, NEGATION, NOUN, NUMBER, PIDGIN_MARKER, PREPOSITION, PRONOUN, PROPER_NOUN, PUNCTUATION, QUESTION_WORD, SUBJUNCTIVE, VERB |
| SEP | CONNECTOR, PUNCTUATION | $, ADJECTIVE, ADVERB, ARTICLE, CODE_MIXED, CONNECTOR, INTERJECTION, NEGATION, NOUN, NUMBER, PIDGIN_MARKER, PREPOSITION, PRONOUN, PROPER_NOUN, PUNCTUATION, QUESTION_WORD, SUBJUNCTIVE, VERB |
| PARTS | CODE_MIXED, INTERJECTION, PIDGIN_MARKER, ε | $, ADJECTIVE, ADVERB, ARTICLE, CONNECTOR, NEGATION, NOUN, NUMBER, PIDGIN_VERB, PREPOSITION, PRONOUN, PROPER_NOUN, PUNCTUATION, QUESTION_WORD, SUBJUNCTIVE, VERB |
| PART | CODE_MIXED, INTERJECTION, PIDGIN_MARKER | $, ADJECTIVE, ADVERB, ARTICLE, CODE_MIXED, CONNECTOR, INTERJECTION, NEGATION, NOUN, NUMBER, PIDGIN_MARKER, PIDGIN_VERB, PREPOSITION, PRONOUN, PROPER_NOUN, PUNCTUATION, QUESTION_WORD, SUBJUNCTIVE, VERB |
| PRED | ADJECTIVE, ADVERB, NEGATION, PIDGIN_VERB, PREPOSITION, VERB | $, CONNECTOR, PUNCTUATION |
| IMP | VERB | $, CONNECTOR, PUNCTUATION |
| VP | NEGATION, PIDGIN_VERB, VERB | $, CONNECTOR, PUNCTUATION |
| VPA | ADJECTIVE, ADVERB, PREPOSITION, VERB | $, CONNECTOR, PUNCTUATION |
| VTAIL | ADJECTIVE, ADVERB, ARTICLE, CODE_MIXED, INTERJECTION, NOUN, NUMBER, PIDGIN_MARKER, PREPOSITION, PRONOUN, PROPER_NOUN, SUBJUNCTIVE, VERB, ε | $, CONNECTOR, PUNCTUATION |
| ADJP | ADJECTIVE, ADVERB | $, ADJECTIVE, ADVERB, ARTICLE, CODE_MIXED, CONNECTOR, INTERJECTION, NOUN, NUMBER, PIDGIN_MARKER, PREPOSITION, PRONOUN, PROPER_NOUN, PUNCTUATION, SUBJUNCTIVE |
| COMPS | ADJECTIVE, ADVERB, ARTICLE, CODE_MIXED, INTERJECTION, NOUN, NUMBER, PIDGIN_MARKER, PREPOSITION, PRONOUN, PROPER_NOUN, SUBJUNCTIVE, ε | $, CONNECTOR, PUNCTUATION |
| COMPSA | ADJECTIVE, ADVERB, CODE_MIXED, INTERJECTION, PIDGIN_MARKER, PREPOSITION, SUBJUNCTIVE, ε | $, CONNECTOR, PUNCTUATION |
| NONNP | ADJECTIVE, ADVERB, CODE_MIXED, INTERJECTION, PIDGIN_MARKER | $, ADJECTIVE, ADVERB, ARTICLE, CODE_MIXED, CONNECTOR, INTERJECTION, NOUN, NUMBER, PIDGIN_MARKER, PREPOSITION, PRONOUN, PROPER_NOUN, PUNCTUATION, SUBJUNCTIVE |
| SUBCL | SUBJUNCTIVE | $, CONNECTOR, PUNCTUATION |
| QCL | QUESTION_WORD | $, CONNECTOR, PUNCTUATION |
| QA | ADJECTIVE, ADVERB, ARTICLE, NOUN, NUMBER, PREPOSITION, PRONOUN, PROPER_NOUN, ε | $, CONNECTOR, PUNCTUATION |
| QB | NEGATION, PIDGIN_VERB, VERB, ε | $, CONNECTOR, PUNCTUATION |
| PPX | ARTICLE, NEGATION, NOUN, NUMBER, PIDGIN_VERB, PRONOUN, PROPER_NOUN, VERB | $, CONNECTOR, PUNCTUATION |
| PPY | ADJECTIVE, ADVERB, CODE_MIXED, INTERJECTION, NEGATION, PIDGIN_MARKER, PIDGIN_VERB, PREPOSITION, SUBJUNCTIVE, VERB, ε | $, CONNECTOR, PUNCTUATION |
| NP | ARTICLE, NOUN, NUMBER, PRONOUN, PROPER_NOUN | $, ADJECTIVE, ADVERB, ARTICLE, CODE_MIXED, CONNECTOR, INTERJECTION, NEGATION, PIDGIN_MARKER, PIDGIN_VERB, PREPOSITION, PRONOUN, PUNCTUATION, SUBJUNCTIVE, VERB |
| NPB | NOUN, NUMBER, PRONOUN, PROPER_NOUN | $, ADJECTIVE, ADVERB, ARTICLE, CODE_MIXED, CONNECTOR, INTERJECTION, NEGATION, PIDGIN_MARKER, PIDGIN_VERB, PREPOSITION, PRONOUN, PUNCTUATION, SUBJUNCTIVE, VERB |
| NPB2 | NOUN, NUMBER, PROPER_NOUN, ε | $, ADJECTIVE, ADVERB, ARTICLE, CODE_MIXED, CONNECTOR, INTERJECTION, NEGATION, PIDGIN_MARKER, PIDGIN_VERB, PREPOSITION, PRONOUN, PUNCTUATION, SUBJUNCTIVE, VERB |

### 3.4 LL(1) Parsing Table
For each production A → α, the table entry (A, a) is set for every a in FIRST(α), and for every a in
FOLLOW(A) when α can derive ε. The construction reports **0 conflicts** (each cell has at most one
production), which proves the grammar is LL(1); the table has 272 filled entries. The full
table is in `analysis/ll1_parsing_table.md` (regenerate with `python analysis/generate_tables.py`).

Trace of "The light done cut" (`python main.py trace "The light done cut"`):

| Step | Lookahead | Action |
|---|---|---|
| 1-5 | ARTICLE | S → U0, U0 → PARTS U0B, PARTS → ε, U0B → BODY0, BODY0 → NP PARTS R0 |
| 6-7 | ARTICLE | NP → ARTICLE NPB; match "The" |
| 8-9 | NOUN | NPB → NOUN NPB2; match "light" |
| 10-12 | PIDGIN_VERB | NPB2 → ε; PARTS → ε; R0 → PRED F1 |
| 13-15 | PIDGIN_VERB | PRED → VP; VP → PIDGIN_VERB VPA; match "done" |
| ... | VERB, $ | VPA → VERB VTAIL; match "cut"; VTAIL → COMPS → ε; F1 → ε; **ACCEPT** |

### 3.5 Testing the Grammar: Accepted and Rejected Sentences
Run with `python main.py accept-reject`. The parser (`src/parser.py`) is the strict table-driven LL(1) parser;
the earlier permissive parser is kept in `src/lenient_parser.py` only for comparison.

| Test set | Sentences | Result |
|---|---|---|
| Collected statements (section 1.3) | 15 | **15 accepted** |
| Extra grammatical sentences not in the data | 12 | **12 accepted** (grammar generalises) |
| Malformed sequences | 15 | **15 rejected** |

Malformed examples and the error reported:

| Input | Result | Error message (abridged) |
|---|---|---|
| "the the the" | rejected | unexpected 'the' (ARTICLE) while parsing NPB |
| "for for at" | rejected | unexpected 'for' (PREPOSITION) while parsing PPX |
| "dey dey dey" | rejected | unexpected 'dey' (PIDGIN_VERB) while parsing S |
| "done light cut" | rejected | unexpected 'done' (PIDGIN_VERB) while parsing S |
| "Brother" | rejected | unexpected end of input while parsing R0 (no predicate) |
| "light dey" | rejected | unexpected end of input while parsing VPA |
| "" (empty) | rejected | unexpected end of input while parsing S |
| "The taxi don reach Carrefour" | accepted | - |
| "Why the bendskin dey charge too much?" | accepted | - |

**Known grammar limits:** adjacent nouns are one compound noun; repeated serial verbs ("drop drop drop")
are accepted; only the vocabulary in the lexer is classified (unknown words default to NOUN).

---

## 4. IMPLEMENTATION (5 + 2 + 3 marks)

| Requirement | Where | Marks |
|---|---|---|
| A simple LL(1) parser | `src/parser.py` (strict table-driven LL(1) parser: explicit stack, 1-token lookahead, parse tree, step trace); grammar and table construction in `src/grammar.py` | 5 |
| Reads the tokenized input | `LexicalAnalyzer.tokenize()` output feeds `parse_statement()` | 2 |
| Decides whether a sentence fits the grammar | `parse_statement()` returns `(tree, success, tokens)` and `parse_statement_detailed()` adds error diagnostics (line, column, found token, expected tokens); the menu and `python main.py analyze "<text>"` print ACCEPTED/REJECTED, the parse tree, and a semantic category and intent | 3 |

Design: Python 3; a token holds type, value, line and column; parse-tree nodes hold rule, children and token. An extra semantic pass (`src/semantic_analyzer.py`) assigns a category (transport, energy, internet, …) and an intent.

---

## 5. SCREENSHOTS OF THE WORKING ANALYZER
_(Insert before submission; capture from a real run.)_
1. `python main.py` main menu
2. `python main.py analyze "The light done cut again"` - token table
3. Same run - parse tree and semantic result
4. Menu option 3 - full test suite with per-category results
5. GUI (`python run_gui.py`)

---

## 6. SOURCE CODE AND TEST CASES

| File | Purpose |
|---|---|
| `src/lexical_analyzer.py` | Regex-based lexical analyzer |
| `src/grammar.py` | LL(1) grammar; computes FIRST/FOLLOW and the parsing table; conflict check |
| `src/parser.py` | Strict table-driven LL(1) parser, parse tree, diagnostics, trace |
| `src/lenient_parser.py` | Earlier permissive parser (kept for comparison only) |
| `src/semantic_analyzer.py` | Category / intent classification |
| `tests/test_cases.py` | Test runner: 15 collected statements + 12 extra grammatical + 15 malformed sentences; report generator |
| `analysis/generate_tables.py` | Regenerates grammar rules, FIRST/FOLLOW and the parsing table from `src/grammar.py` |
| `main.py`, `gui_application.py`, `run_gui.py` | Menu / CLI and GUI front-ends |
| `data/` | Statements, token specification, grammar rules |
| `analysis/` | FIRST/FOLLOW, parsing table, test and semantic reports |

Test results (strict parser): lexical 15/15, syntactic 15/15 accepted; 12/12 extra grammatical sentences accepted; 15/15 malformed sequences rejected. By category: Taxi 3/3, Internet & Electricity 3/3, Market 3/3, Security & Weather 2/2, Fuel 2/2, University 2/2.

---

## 7. PRESENTATION AND DEMONSTRATION (5 marks)
Each student presents for **3 minutes** (see `PRESENTATION_GUIDE.md`; the paper also lists a 10-minute PowerPoint deliverable).
- **0:00-1:00** Context: multilingual Yaoundé, 15 real statements, 6 categories.
- **1:00-2:00** Approach: 15 token types / 245 tokens, regexes, LL(1) grammar with left-recursion removal and left factoring.
- **2:00-3:00** Live demo: `python main.py analyze "The light done cut again"` → tokens, parse tree, category; then run `python main.py accept-reject` to show malformed input being rejected.

---

## 8. DISCUSSION: WHY YAOUNDÉ COMMUNICATION IS LINGUISTICALLY COMPLEX

### 8.1 Observed patterns
**Code-mixing.** "Eh mon Dieu, internet dey do again?" combines an English interjection, a French phrase, an English noun, a Pidgin aspect marker and an English verb in one utterance. Purpose: social bonding, emphasis, frustration.

**Pidgin aspect system.** `dey` (progressive/habitual: "internet dey do"), `done`/`don` (perfective: "light done cut"), `fit` (ability: "network no fit work"), `go` (future: "we go wait"). Aspect is marked by particles, not verb endings, unlike standard English.

**Pragmatic particles.** `na` (emphasis/focus: "drop me na"), `am` (object marker: "reduce am"), `small` (softener: "tire me small"), `ooo` (intensifier: "c'est cher ooo").

**Ellipsis and informality.** Dropped subjects and auxiliaries ("pump don empty again"), contracted forms ("make you reduce" = "please reduce"), fragmentary speech.

### 8.2 Complexity factors
1. **Multiple languages per utterance:** English, French, Pidgin (and, in the wider city, Fulfulde and Ewondo) with different morphosyntax and no marked boundaries.
2. **Non-standard syntax:** pragmatic rather than grammatical ordering, frequent ellipsis.
3. **Aspect marking by particles:** essential for meaning, absent from standard English grammars.
4. **Lexical ambiguity:** `fit`, `go`, `me`, `na`, `am` change role with context.
5. **Register variation:** market bargaining, university talk and street speech differ; there is no single "correct" form.
6. **No orthographic standard:** garrr, ekiee, zéro-zéro are spelled as heard, so a lexer must rely on lists and patterns.

---

## 9. CHALLENGES, LIMITATIONS AND FUTURE WORK
- **Grammar coverage:** the grammar covers the 15 collected statements and 12 unseen sentences, but it is still small: adjacent nouns are one compound noun, repeated serial verbs are accepted, and words missing from the lexer default to NOUN. *Future work:* a larger corpus and vocabulary, and adverbial clauses with their own subject.
- **Multi-word tokens:** "mon Dieu", "c'est cher" are handled by prioritised multi-word patterns.
- **Ambiguous markers:** `na`, `am`, `go`, `fit` depend on context; the lexer classifies from word lists, not context.
- **Dataset size:** 15 statements; token statistics are indicative only.
- **Languages:** Fulfulde and Ewondo expressions are not yet represented.

## 10. CONCLUSION
The project applies compiler-construction techniques (regex-based lexing, CFG design, left-recursion removal, left factoring, FIRST/FOLLOW, LL(1) table, predictive parsing) to informal Yaoundé speech. Lexical analysis covers all 245 tokens of the collected data; a verified conflict-free LL(1) grammar is provided; and the strict table-driven parser accepts all 15 collected statements and 12 unseen grammatical sentences while rejecting 15 malformed sequences with precise error messages. The main open item is a larger corpus to test how far the grammar generalises.

---

## APPENDICES
### A. How to run
```bash
python main.py                              # interactive menu (needs a terminal)
python main.py demo                         # demo of 3 statements
python main.py test                         # full test suite (writes analysis/test_report.txt)
python main.py analyze "The light done cut again"
python main.py report                       # semantic report JSON
python main.py grammar                      # grammar, FIRST/FOLLOW sets, conflict check
python main.py accept-reject                # accepted / rejected sentence tests
python main.py trace "The light done cut"    # step-by-step LL(1) trace
python analysis/generate_tables.py          # regenerate grammar/FIRST-FOLLOW/table docs
python run_gui.py                           # GUI
```
### B. File listing
```
data/  src/  tests/  analysis/  main.py  gui_application.py  run_gui.py
README.md  FINAL_REPORT.md  PRESENTATION_GUIDE.md
```
