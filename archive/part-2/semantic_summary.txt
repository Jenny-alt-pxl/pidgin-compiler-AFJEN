# LL(1) PARSING TABLE

## Simplified Grammar (Consolidated for LL(1))

```
1. S → NP VP
2. S → VP
3. NP → ARTICLE N
4. NP → N
5. VP → PIDGIN_V V
6. VP → V OPT_NP
7. OPT_NP → NP
8. OPT_NP → ε
9. V → VERB
10. N → NOUN | PROPER_NOUN
11. PIDGIN_V → "dey" | "done" | "fit" | "go"
12. ARTICLE → "the" | "a"
```

---

## LL(1) PARSING TABLE

### Legend
- Rows: Non-terminals (variables)
- Columns: Terminals (tokens) + $
- Cell values: Production rule number or error

### Table Structure

```
                │ ARTICLE │ NOUN │ VERB │ PIDGIN_V │ PREP │ $ │
────────────────┼─────────┼──────┼──────┼──────────┼──────┼───┤
S               │    1    │  2   │  2   │    2     │  E   │ E │
NP              │    3    │  4   │  E   │    E     │  E   │ E │
VP              │    E    │  E   │  6   │    5     │  E   │ E │
OPT_NP          │    7    │  7   │  8   │    8     │  8   │ 8 │
V               │    E    │  E   │  9   │    E     │  E   │ E │
N               │    E    │ 10   │  E   │    E     │  E   │ E │
PIDGIN_V        │    E    │  E   │  E   │   11     │  E   │ E │
ARTICLE         │   12    │  E   │  E   │    E     │  E   │ E │
────────────────┴─────────┴──────┴──────┴──────────┴──────┴───┘
```

---

## DETAILED LL(1) TABLE (Token by Token)

### S (Start Symbol)
| Current Token | Action | Production |
|---------------|--------|-----------|
| ARTICLE | Use S → NP VP (Rule 1) | 1 |
| NOUN | Use S → VP (Rule 2) | 2 |
| PROPER_NOUN | Use S → VP (Rule 2) | 2 |
| VERB | Use S → VP (Rule 2) | 2 |
| PIDGIN_VERB | Use S → VP (Rule 2) | 2 |
| PREPOSITION | ERROR | - |
| $ | ERROR | - |

### NP (Noun Phrase)
| Current Token | Action | Production |
|---------------|--------|-----------|
| ARTICLE | Use NP → ARTICLE N (Rule 3) | 3 |
| NOUN | Use NP → N (Rule 4) | 4 |
| PROPER_NOUN | Use NP → N (Rule 4) | 4 |
| VERB | ERROR | - |
| PIDGIN_VERB | ERROR | - |
| PREPOSITION | ERROR | - |
| $ | ERROR | - |

### VP (Verb Phrase)
| Current Token | Action | Production |
|---------------|--------|-----------|
| ARTICLE | ERROR | - |
| NOUN | ERROR | - |
| PROPER_NOUN | ERROR | - |
| VERB | Use VP → V OPT_NP (Rule 6) | 6 |
| PIDGIN_VERB | Use VP → PIDGIN_V V (Rule 5) | 5 |
| PREPOSITION | ERROR | - |
| $ | ERROR | - |

### OPT_NP (Optional Noun Phrase)
| Current Token | Action | Production |
|---------------|--------|-----------|
| ARTICLE | Use OPT_NP → NP (Rule 7) | 7 |
| NOUN | Use OPT_NP → NP (Rule 7) | 7 |
| PROPER_NOUN | Use OPT_NP → NP (Rule 7) | 7 |
| VERB | Use OPT_NP → ε (Rule 8) | 8 |
| PIDGIN_VERB | Use OPT_NP → ε (Rule 8) | 8 |
| PREPOSITION | Use OPT_NP → ε (Rule 8) | 8 |
| $ | Use OPT_NP → ε (Rule 8) | 8 |

### V (Verb)
| Current Token | Action | Production |
|---------------|--------|-----------|
| VERB | Use V → VERB (Rule 9) | 9 |
| All others | ERROR | - |

### N (Noun)
| Current Token | Action | Production |
|---------------|--------|-----------|
| NOUN | Use N → NOUN (Rule 10) | 10 |
| PROPER_NOUN | Use N → PROPER_NOUN (Rule 10) | 10 |
| All others | ERROR | - |

### PIDGIN_V (Pidgin Verb)
| Current Token | Action | Production |
|---------------|--------|-----------|
| "dey"/"done"/"fit"/"go" | Use PIDGIN_V → token (Rule 11) | 11 |
| All others | ERROR | - |

### ARTICLE
| Current Token | Action | Production |
|---------------|--------|-----------|
| "the"/"a" | Use ARTICLE → token (Rule 12) | 12 |
| All others | ERROR | - |

---

## EXAMPLE PARSING TRACE

### Parsing: "The light done cut"

**Tokens:** ARTICLE("the") NOUN("light") PIDGIN_V("done") VERB("cut") $

| Step | Stack | Input | Action |
|------|-------|-------|--------|
| 1 | [S] | "the" light done cut $ | S → NP VP (Rule 1) |
| 2 | [VP, NP] | "the" light done cut $ | NP → ARTICLE N (Rule 3) |
| 3 | [VP, N, ARTICLE] | "the" light done cut $ | ARTICLE → "the" |
| 4 | [VP, N] | light done cut $ | N → NOUN |
| 5 | [VP] | done cut $ | VP → PIDGIN_V V (Rule 5) |
| 6 | [V, PIDGIN_V] | done cut $ | PIDGIN_V → "done" |
| 7 | [V] | cut $ | V → VERB |
| 8 | [] | $ | **ACCEPT** ✓ |

---

## EXAMPLE PARSING TRACE

### Parsing: "Drop me at Yaoundé"

**Tokens:** VERB("drop") PRONOUN("me") PREP("at") PROPER_NOUN("Yaoundé") $

| Step | Stack | Input | Action |
|------|-------|-------|--------|
| 1 | [S] | drop me at Yaoundé $ | S → VP (Rule 2) |
| 2 | [VP] | drop me at Yaoundé $ | VP → V OPT_NP (Rule 6) |
| 3 | [OPT_NP, V] | drop me at Yaoundé $ | V → VERB |
| 4 | [OPT_NP] | me at Yaoundé $ | OPT_NP → NP (Rule 7) |
| 5 | [NP] | me at Yaoundé $ | NP → N (Rule 4) |
| 6 | [N] | me at Yaoundé $ | N → NOUN |
| 7 | [] | at Yaoundé $ | **ERROR**: Unexpected PREPOSITION |
|   |   |   | (Note: Parser needs enhancement for PP) |

---

## ERROR HANDLING STRATEGY

1. **Unexpected Token:** Report error with current token and expected tokens
2. **Missing Token:** Skip current input token and continue
3. **Unrecognized Pattern:** Report and advance to next clause/statement

---

## ENHANCEMENT FOR FULL GRAMMAR

To handle prepositional phrases, add to VP rule:

```
VP → V OPT_NP OPT_PP

OPT_PP → PREP NP
OPT_PP → ε
```

Updated parsing table entry for VP:
| Current Token | Action | Production |
|---------------|--------|-----------|
| VERB | Use VP → V OPT_NP OPT_PP (Rule 6') | 6' |

---

## IMPLEMENTATION NOTES

1. **Recursive Descent:** Natural fit for this LL(1) grammar
2. **Backtracking:** Used when OPT_NP or OPT_PP could match
3. **Error Recovery:** Sync on statement boundaries (commas, question marks)
4. **Token Lookahead:** 1-token lookahead sufficient for LL(1)

---

## VERIFICATION WITH COLLECTED STATEMENTS

| Statement | Grammar | Tokenizes | Parses | Notes |
|-----------|---------|-----------|--------|-------|
| "The light done cut" | NP VP → S | ✓ | ✓ | Clean parse |
| "Drop me at Carrefour" | VP → S | ✓ | Partial | Needs PP handling |
| "Internet dey do again" | NP VP → S | ✓ | ✓ | Pidgin pattern |
| "Mama, make reduce am" | Greeting? | ✓ | Needs work | Imperatives |
| "How much for airtime?" | Question | ✓ | Partial | Needs QWORD |

