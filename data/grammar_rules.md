# CONTEXT-FREE GRAMMAR (CFG) FOR YAOUNDÉ URBAN COMMUNICATION

## Grammar Overview
This CFG is designed to parse the 15 collected statements and capture the structure of 
informal urban communication in Yaoundé, including code-mixing, slang, and Pidgin patterns.

---

## INITIAL GRAMMAR (Before Transformations)

```
STATEMENT  → GREETING? ACTION CLAUSE*
GREETING   → NOUN_DIRECT ("Brother" | "Mama")
ACTION     → IMPERATIVE | NARRATIVE | QUESTION
IMPERATIVE → VERB OBJECT (MODIFIER)*
NARRATIVE  → SUBJECT PREDICATE (TIME_REF)?
QUESTION   → QUESTION_WORD PREDICATE?
CLAUSE     → CONNECTOR ACTION

SUBJECT    → PRONOUN | NOUN_PHRASE
PREDICATE  → VERB OBJECT? (LOCATION | MANNER | REASON)?
OBJECT     → NOUN_PHRASE | PRONOUN
NOUN_PHRASE → ARTICLE? NOUN (MODIFIER)*
ARTICLE    → "the" | "a" | "an"
MODIFIER   → ADJECTIVE | ADVERB | PREPOSITIONAL_PHRASE
ADJECTIVE  → "small" | "fresh" | "good" | "scarce" | "crowded" | "cher" | "down-down"
ADVERB     → "too much" | "again" | "small" | "so"
PREPOSITIONAL_PHRASE → PREPOSITION NOUN_PHRASE
PREPOSITION → "for" | "at" | "in" | "on" | "before"

LOCATION   → "at" PLACE | "for" PLACE
PLACE      → "Yaoundé" | "Carrefour" | "quartier" | "checkpoint" | "quarter" | "Mambanda"
MANNER     → SLANG | INTERJECTION
TIME_REF   → "since" NOUN | "already" | "again"
CONNECTOR  → "and" | "but" | "or" | ","

PIDGIN_VERB → "dey" | "done" | "go" | "fit" | "waka"
ENGLISH_VERB → "drop" | "try" | "cut" | "remain" | "fill" | "take" | ...
NOUN       → CONCRETE_NOUN | ABSTRACT_NOUN | LOCATION_NOUN
CONCRETE_NOUN → "taxi" | "money" | "transport" | "modem" | "tomatoes" | ...
ABSTRACT_NOUN → "internet" | "light" | "time" | "traffic" | ...
PRONOUN    → "I" | "we" | "you" | "me" | "him" | "it"

SLANG      → "garrr" | "zéro-zéro" | "ekiee" | "hmmm" | "wahala" | "ooo"
INTERJECTION → "OK" | "hmmm" | "Eh" | "garrr"
CODE_MIXED → "mon Dieu" | "c'est cher" | "Je wanda"
NUMBER     → DIGIT+
DIGIT      → "0" | "1" | "2" | ... | "9"
```

---

## DETAILED RULE BREAKDOWN

### Rule 1: STATEMENT
```
STATEMENT  → GREETING? ACTION CLAUSE*
```
**Explanation:** A statement can optionally start with a greeting (e.g., "Brother"), followed by an action, 
and can have multiple additional clauses.

**Example from data:**
- "Brother, drop me na at Carrefour Yaoundé, the traffic done tire me small"
  - GREETING: "Brother"
  - ACTION: "drop me at Carrefour Yaoundé"
  - CLAUSE: "the traffic done tire me small"

---

### Rule 2: ACTION
```
ACTION     → IMPERATIVE | NARRATIVE | QUESTION
```
**Explanation:** An action can be imperative (command), narrative (statement), or question.

**Examples:**
- IMPERATIVE: "drop me na at Carrefour Yaoundé" (Stmt 1)
- NARRATIVE: "The light done cut again" (Stmt 5)
- QUESTION: "How much for this phone airtime?" (Stmt 13)

---

### Rule 3: IMPERATIVE
```
IMPERATIVE → VERB OBJECT (MODIFIER)*
```
**Explanation:** Commands typically have a verb followed by what to act on, plus optional modifiers.

**Examples:**
- "drop me na at Carrefour" (Stmt 1)
- "come take am now" (Stmt 8)
- "make you reduce am na small" (Stmt 7)

---

### Rule 4: NARRATIVE
```
NARRATIVE  → SUBJECT PREDICATE (TIME_REF)?
```
**Explanation:** Statements about facts or events, with optional time references.

**Examples:**
- "The light done cut again" (Stmt 5)
- "Rain don fall so" (Stmt 11)
- "Lecture done start" (Stmt 14)

---

### Rule 5: PREDICATE
```
PREDICATE  → VERB OBJECT? (LOCATION | MANNER | TIME_REF)?
```
**Explanation:** The predicate contains a verb and optional object, location, manner, or time info.

**Examples:**
- "done cut again" (Stmt 5)
- "dey charge too much" (Stmt 9)
- "dey for front" (Stmt 10)

---

### Rule 6: NOUN_PHRASE
```
NOUN_PHRASE → ARTICLE? NOUN (MODIFIER)*
```
**Explanation:** A noun phrase may have an article (the, a) plus a noun and modifiers.

**Examples:**
- "the traffic" (Stmt 1)
- "five hundred francs" (Stmt 2)
- "two thousand francs" (Stmt 7)

---

### Rule 7: PIDGIN_STRUCTURE
```
PIDGIN_STRUCTURE → SUBJECT PIDGIN_VERB PREDICATE
```
**Explanation:** Captures Pidgin verb patterns like "dey", "done", "fit", "go", "waka".

**Examples:**
- "internet dey do again" (Stmt 4) → SUBJECT=internet, PIDGIN_VERB=dey, PREDICATE=do
- "The light done cut" (Stmt 5) → SUBJECT=light, PIDGIN_VERB=done, PREDICATE=cut
- "car stuck" (Stmt 11) → SUBJECT=car, PIDGIN_VERB=(implicit stuck), PREDICATE=(location)

---

### Rule 8: CODE_MIXING_PATTERN
```
CODE_MIXING_PATTERN → ENGLISH_PHRASE FRENCH_PHRASE | PIDGIN_PHRASE CODE_MIXED
```
**Explanation:** Captures mixed-language patterns common in Yaoundé speech.

**Examples:**
- "Eh mon Dieu" (Stmt 4) → ENGLISH_INTERJECTION + FRENCH_PHRASE
- "c'est cher ooo" (Stmt 9) → FRENCH_PHRASE + PIDGIN_INTERJECTION
- "Je wanda" (Stmt 6) → FRENCH_VERB + ENGLISH_OBJECT (mixed)

---

## SIMPLIFIED GRAMMAR FOR LL(1) PARSING

For easier implementation, we can simplify to:

```
S  → N VP | VP
N  → NOUN | PRONOUN
VP → V | V N | V N PP | V PP | V ADVERB
PP → PREP N | PREP VP
V  → VERB | PIDGIN_VERB VERB
```

**Example Derivations:**

1. "Brother, drop me na at Carrefour Yaoundé, the traffic done tire me small"
   ```
   S → VP (drop ... tire ...)
   VP → V NP PP
   V → drop
   NP → PRONOUN = me
   PP → PREP NP = at Carrefour Yaoundé
   ```

2. "The light done cut again"
   ```
   S → NP VP
   NP → ARTICLE NOUN = the light
   VP → PIDGIN_VERB VERB ADVERB = done cut again
   ```

---

## ISSUES TO ADDRESS

1. **Left Recursion:** None explicitly in initial grammar
2. **Left Factoring:** 
   - ACTION → IMPERATIVE | NARRATIVE | QUESTION
   - These start with different patterns, so no factoring needed
3. **Ambiguity:** 
   - "make you reduce am na small" - multiple interpretations
   - Resolved by treating "na" as a marker/particle

---

## PRODUCTION RULES (FULL LIST)

### Terminal Symbols:
```
NOUN, VERB, PRONOUN, ARTICLE, PREPOSITION, ADJECTIVE, ADVERB, 
SLANG, INTERJECTION, NUMBER, CODE_MIXED, PUNCTUATION
```

### Non-Terminal Symbols:
```
S, STATEMENT, ACTION, IMPERATIVE, NARRATIVE, QUESTION, SUBJECT, 
PREDICATE, OBJECT, NOUN_PHRASE, VERB_PHRASE, PREP_PHRASE, 
MODIFIER, CLAUSE, CONNECTOR
```

### Production Rules (Clean Version):
```
1. S → STATEMENT
2. STATEMENT → ACTION CLAUSE* | GREETING ACTION CLAUSE*
3. ACTION → IMPERATIVE | NARRATIVE | QUESTION
4. IMPERATIVE → VERB NP+ | VERB NP PP+
5. NARRATIVE → NP VP | NP VP PP
6. QUESTION → QWORD VP? | QWORD NP?
7. NP → ARTICLE? N | N
8. VP → PIDGIN_V V NP? PP*
9. VP → V NP? PP*
10. PP → PREP NP
11. N → NOUN | PROPER_NOUN
12. V → VERB
13. PIDGIN_V → "dey" | "done" | "go" | "fit" | "waka"
14. QWORD → "How" | "Why" | "What"
15. CLAUSE → CONNECTOR ACTION
16. ARTICLE → "the" | "a"
17. PREP → "at" | "for" | "in" | "on" | "since"
```

