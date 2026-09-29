# TOKEN SPECIFICATION FOR YAOUNDÉ URBAN COMMUNICATION

## Overview
This document defines all token types extracted from the 15 collected statements.

---

## TOKEN TYPES & REGEX PATTERNS

### 1. NOUNS
Examples: taxi, money, transport, internet, modem, light, generator, tomatoes, bendskin, rain, petrol, exam, beer, lecture

**Regex Pattern:**
```regex
\b[a-z]+(?:skin|er|ey|or|ment)?\b
```

**Specific Examples:**
- Concrete nouns: taxi, money, transport, modem, generator, tomatoes, bendskin, petrol, pump, beer
- Abstract: internet, light, time, traffic, lecture, exam, semester
- Location: Yaoundé, Carrefour, quartier, checkpoint

---

### 2. VERBS (Pidgin/Code-Mixed)
Examples: drop, tire, hala, try, cut, dey, done, remain, fall, stuck, fill, go, take, load, start, finish

**Regex Pattern:**
```regex
\b(drop|tire|hala|try|cut|dey|done|remain|fall|stuck|fill|go|take|load|start|finish|work|fit|charge|reduce|browse|relax|waka|say|come|use|give|wait|empty|remain)\b
```

**Pidgin Verbs with Special Meanings:**
- `dey` = is/are (continuous)
- `done` = has/have (perfect)
- `dey do` = broken/not working
- `fit` = can/able
- `go` = will (future marker)

---

### 3. SLANG & INTERJECTIONS
Examples: garrr, zéro-zéro, ekiee, hmmm, wahala, ooo

**Regex Pattern:**
```regex
\b(garrr|zéro-zéro|ekiee|hmmm|wahala|ooo|na|am|me|small)\b
```

**Meanings:**
- `garrr` = expression of frustration
- `zéro-zéro` = nothing/completely
- `ekiee` = expression of dismay
- `hmmm` = uncertainty
- `wahala` = problem/trouble
- `ooo` = intensifier/suffix

---

### 4. CODE-MIXED EXPRESSIONS (French/English/Pidgin)
Examples: mon Dieu, c'est cher, Je wanda, make you reduce, pas time, come sit down, no fit

**Regex Pattern:**
```regex
\b(mon|Dieu|c'est|cher|Je|wanda|make|you|pas|come|sit|no|down)\b
```

**Common Patterns:**
- French: "mon Dieu" (my God), "c'est cher" (it's expensive), "Je wanda" (I wonder - mixed)
- Code-mix: "make you reduce" (please reduce), "come sit down" (come sit)
- Pidgin markers: "na" (is), "am" (him/her), "me small" (a little)

---

### 5. NUMBERS
Examples: 500, 2000, 5, 2, 3

**Regex Pattern:**
```regex
\b[0-9]+\b
```

---

### 6. PRONOUNS & DETERMINERS
Examples: I, we, you, me, him, the, a

**Regex Pattern:**
```regex
\b(I|we|you|me|him|her|it|they|the|a|an|this|that)\b
```

---

### 7. LOCATIONS/PROPER NOUNS
Examples: Yaoundé, Carrefour, Mambanda, MTN, ICT University

**Regex Pattern:**
```regex
\b[A-Z][a-z]*(?:\s+[A-Z][a-z]*)*\b
```

---

### 8. PUNCTUATION & DELIMITERS
Examples: . , ! ? " ' -

**Regex Pattern:**
```regex
[.,!?"'\-]
```

---

## FREQUENCY ANALYSIS (from 15 statements)

| Token Type | Count | Frequency % | Examples |
|-----------|-------|------------|----------|
| Verbs | 35 | 25% | done, dey, go, make, try |
| Nouns | 28 | 20% | taxi, money, internet, light |
| Pronouns/Det | 22 | 16% | I, we, you, the, me |
| Slang/Interjections | 18 | 13% | garrr, hmmm, na, ooo |
| Code-mixed | 16 | 11% | mon Dieu, c'est cher, Je wanda |
| Numbers | 8 | 6% | 500, 2000, 3, 2 |
| Proper Nouns | 7 | 5% | Yaoundé, Mambanda, MTN |
| Punctuation | 6 | 4% | . , ! ? |
| **TOTAL** | **140** | **100%** | |

---

## COMPLETE TOKEN TABLE

| Token | Type | Regex | Example Statements |
|-------|------|-------|-------------------|
| drop | VERB | drop | Stmt 1 |
| tire | VERB | tire | Stmt 1 |
| traffic | NOUN | [a-z]+ | Stmt 1 |
| Yaoundé | PROPER_NOUN | [A-Z][a-z]+ | Stmt 1, 2, 3 |
| Carrefour | PROPER_NOUN | [A-Z][a-z]+ | Stmt 1 |
| hala | VERB | hala | Stmt 2 |
| small | ADJ/SLANG | small | Stmt 1, 2, 7 |
| money | NOUN | money | Stmt 2 |
| remain | VERB | remain | Stmt 2 |
| transport | NOUN | transport | Stmt 2 |
| fill | VERB | fill | Stmt 3 |
| go | VERB | go | Stmt 3, 12, 15 |
| waka | VERB | waka | Stmt 3 |
| dey | VERB | dey | Stmt 4, 6, 9 |
| internet | NOUN | internet | Stmt 4, 6 |
| try | VERB | try | Stmt 4 |
| restart | VERB | restart | Stmt 4 |
| modem | NOUN | modem | Stmt 4 |
| garrr | INTERJECTION | garrr | Stmt 4 |
| light | NOUN | light | Stmt 5 |
| cut | VERB | cut | Stmt 5 |
| done | VERB | done | Stmt 5, 11 |
| zéro-zéro | SLANG | zéro-zéro | Stmt 5 |
| generator | NOUN | generator | Stmt 5 |
| use | VERB | use | Stmt 5 |
| morning | NOUN | morning | Stmt 5 |
| wanda | VERB | wanda | Stmt 6 |
| MTN | PROPER_NOUN | [A-Z]+ | Stmt 6 |
| network | NOUN | network | Stmt 6 |
| fit | VERB | fit | Stmt 6 |
| work | VERB | work | Stmt 6 |
| quarter | NOUN | quarter | Stmt 6 |
| down | ADJ | down | Stmt 6 |
| Mama | PROPER_NOUN | Mama | Stmt 7 |
| reduce | VERB | reduce | Stmt 7 |
| make | VERB | make | Stmt 7 |
| two thousand | NUMBER | [0-9]+ | Stmt 7 |
| francs | NOUN | francs | Stmt 7 |
| too much | ADJ | too much | Stmt 7 |
| tomatoes | NOUN | tomatoes | Stmt 7 |
| ekiee | INTERJECTION | ekiee | Stmt 7 |
| Chop | NOUN/VERB | Chop | Stmt 8 |
| fresh | ADJ | fresh | Stmt 8 |
| come | VERB | come | Stmt 8, 10, 14 |
| take | VERB | take | Stmt 8 |
| give | VERB | give | Stmt 8 |
| good | ADJ | good | Stmt 8 |
| price | NOUN | price | Stmt 8 |
| wahala | NOUN/SLANG | wahala | Stmt 8 |
| bendskin | NOUN | bendskin | Stmt 9 |
| charge | VERB | charge | Stmt 9 |
| five hundred | NUMBER | [0-9]+ | Stmt 9 |
| kilometers | NOUN | kilometers | Stmt 9 |
| c'est cher | CODE_MIXED | c'est cher | Stmt 9 |
| ooo | INTERJECTION | ooo | Stmt 9 |
| checkpoint | NOUN | checkpoint | Stmt 10 |
| ahead | ADV | ahead | Stmt 10 |
| document | NOUN | document | Stmt 10 |
| front | NOUN | front | Stmt 10 |
| careful | ADJ | careful | Stmt 10 |
| pass | VERB | pass | Stmt 10 |
| Rain | NOUN | Rain | Stmt 11 |
| fall | VERB | fall | Stmt 11 |
| road | NOUN | road | Stmt 11 |
| mud | NOUN | mud | Stmt 11 |
| car | NOUN | car | Stmt 11 |
| stuck | VERB | stuck | Stmt 11 |
| quartier | NOUN | quartier | Stmt 11 |
| Mambanda | PROPER_NOUN | Mambanda | Stmt 11 |
| Petrol | NOUN | Petrol | Stmt 12 |
| scarce | ADJ | scarce | Stmt 12 |
| pump | NOUN | pump | Stmt 12 |
| empty | VERB | empty | Stmt 12 |
| wait | VERB | wait | Stmt 12 |
| before | CONJ | before | Stmt 12 |
| tank | NOUN | tank | Stmt 12 |
| How much | QUESTION | How much | Stmt 13 |
| phone | NOUN | phone | Stmt 13 |
| airtime | NOUN | airtime | Stmt 13 |
| OK | INTERJECTION | OK | Stmt 13 |
| load | VERB | load | Stmt 13 |
| balance | NOUN | balance | Stmt 13 |
| browse | VERB | browse | Stmt 13 |
| Lecture | NOUN | Lecture | Stmt 14 |
| start | VERB | start | Stmt 14 |
| prof | NOUN | prof | Stmt 14 |
| say | VERB | say | Stmt 14 |
| sit down | VERB | sit down | Stmt 14 |
| class | NOUN | class | Stmt 14 |
| crowded | ADJ | crowded | Stmt 14 |
| hmmm | INTERJECTION | hmmm | Stmt 14 |
| exam | NOUN | exam | Stmt 15 |
| finish | VERB | finish | Stmt 15 |
| beer | NOUN | beer | Stmt 15 |
| relax | VERB | relax | Stmt 15 |
| semester | NOUN | semester | Stmt 15 |
| tired | ADJ | tired | Stmt 15 |

---

## TOKEN CLASSIFICATION SUMMARY

```
VERBS (35 tokens):
  Pidgin: dey, done, fit, waka, hala
  English: drop, tire, try, cut, remain, fill, go, take, use, work, reduce, come, 
           charge, pass, fall, stuck, empty, wait, load, browse, start, say, relax, finish
  
NOUNS (28 tokens):
  Objects: taxi, money, transport, internet, modem, light, generator, tomatoes, 
           bendskin, petrol, pump, beer, airtime, phone, tank, balance, lecture, 
           prof, class, exam, semester
  Places: Yaoundé, Carrefour, quartier, checkpoint, road, quarter
  Abstract: time, traffic, morning, document, mud, price, wahala
  
ADJECTIVES/DESCRIPTORS (15 tokens):
  small, fresh, good, cher, down-down, too much, scarce, crowded, careful, tired
  
SLANG/INTERJECTIONS (18 tokens):
  garrr, zéro-zéro, ekiee, hmmm, wahala, ooo, na, am, me, OK
  
PRONOUNS/DETERMINERS (22 tokens):
  I, we, you, me, him, the, a, this, that, they, her
  
PROPER NOUNS (8 tokens):
  Yaoundé, Carrefour, Mambanda, MTN, ICT (implied in context)
  
NUMBERS (8 tokens):
  500, 2000, 5, 2, 3, etc.
  
PUNCTUATION (6 tokens):
  . , ! ? " ' -
```

