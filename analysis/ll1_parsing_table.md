# LL(1) Predictive Parsing Table

Cell (A, a) = production to apply when the top of the stack is A and the lookahead is a.
Empty cell = syntax error.

**Conflicts: 0** (the grammar is LL(1))

## Productions (numbered)

1. S → U0
2. U0 → PARTS U0B
3. U0B → BODY0
4. U0B → SEPS U0
5. BODY0 → NP PARTS R0
6. BODY0 → IMP F1
7. BODY0 → QCL F1
8. BODY0 → SUBCL F1
9. BODY0 → PREPOSITION PPX SEPS U0
10. R0 → PRED F1
11. R0 → SEPS U0
12. R0 → PRONOUN PARTS R0
13. R0 → ARTICLE NPB PARTS R0
14. F1 → SEPS G1
15. F1 → ε
16. G1 → PARTS G2
17. G2 → BODY1
18. G2 → SEPS G1
19. G2 → ε
20. BODY1 → NP PARTS R1
21. BODY1 → IMP F1
22. BODY1 → QCL F1
23. BODY1 → SUBCL F1
24. BODY1 → PREPOSITION PPX F1
25. BODY1 → ADJP F1
26. BODY1 → NEGATION PARTS F1
27. R1 → PRED F1
28. R1 → PRONOUN PARTS R1
29. R1 → ARTICLE NPB PARTS R1
30. R1 → F1
31. SEPS → SEP
32. SEP → CONNECTOR
33. SEP → PUNCTUATION
34. PARTS → PART PARTS
35. PARTS → ε
36. PART → PIDGIN_MARKER
37. PART → INTERJECTION
38. PART → CODE_MIXED
39. PRED → VP
40. PRED → ADJP COMPS
41. PRED → PREPOSITION PPX
42. IMP → VERB VTAIL
43. VP → NEGATION VP
44. VP → PIDGIN_VERB VPA
45. VP → VERB VTAIL
46. VPA → VERB VTAIL
47. VPA → ADJP COMPS
48. VPA → PREPOSITION PPX
49. VPA → ε
50. VTAIL → VERB VTAIL
51. VTAIL → COMPS
52. ADJP → ADVERB ADJP
53. ADJP → ADJECTIVE
54. COMPS → NP COMPSA
55. COMPS → PREPOSITION PPX
56. COMPS → NONNP COMPS
57. COMPS → SUBCL
58. COMPS → ε
59. COMPSA → PREPOSITION PPX
60. COMPSA → NONNP COMPS
61. COMPSA → SUBCL
62. COMPSA → ε
63. NONNP → PART
64. NONNP → ADVERB
65. NONNP → ADJECTIVE
66. SUBCL → SUBJUNCTIVE NP PARTS VP
67. QCL → QUESTION_WORD QA
68. QA → ADJECTIVE QA
69. QA → ADVERB QA
70. QA → PREPOSITION PPX
71. QA → NP QB
72. QA → ε
73. QB → VP
74. QB → ε
75. PPX → VP
76. PPX → NP PPY
77. PPY → VP
78. PPY → COMPSA
79. NP → ARTICLE NPB
80. NP → NPB
81. NPB → NUMBER NPB2
82. NPB → NOUN NPB2
83. NPB → PROPER_NOUN NPB2
84. NPB → PRONOUN
85. NPB2 → NUMBER NPB2
86. NPB2 → NOUN NPB2
87. NPB2 → PROPER_NOUN NPB2
88. NPB2 → ε

## Parsing table (production numbers)

| | ADJECTIVE | ADVERB | ARTICLE | CODE_MIXED | CONNECTOR | INTERJECTION | NEGATION | NOUN | NUMBER | PIDGIN_MARKER | PIDGIN_VERB | PREPOSITION | PRONOUN | PROPER_NOUN | PUNCTUATION | QUESTION_WORD | SUBJUNCTIVE | VERB | $ |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| **S** |  |  | 1 | 1 | 1 | 1 |  | 1 | 1 | 1 |  | 1 | 1 | 1 | 1 | 1 | 1 | 1 |  |
| **U0** |  |  | 2 | 2 | 2 | 2 |  | 2 | 2 | 2 |  | 2 | 2 | 2 | 2 | 2 | 2 | 2 |  |
| **U0B** |  |  | 3 |  | 4 |  |  | 3 | 3 |  |  | 3 | 3 | 3 | 4 | 3 | 3 | 3 |  |
| **BODY0** |  |  | 5 |  |  |  |  | 5 | 5 |  |  | 9 | 5 | 5 |  | 7 | 8 | 6 |  |
| **R0** | 10 | 10 | 13 |  | 11 |  | 10 |  |  |  | 10 | 10 | 12 |  | 11 |  |  | 10 |  |
| **F1** |  |  |  |  | 14 |  |  |  |  |  |  |  |  |  | 14 |  |  |  | 15 |
| **G1** | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 |  | 16 | 16 | 16 | 16 | 16 | 16 | 16 | 16 |
| **G2** | 17 | 17 | 17 |  | 18 |  | 17 | 17 | 17 |  |  | 17 | 17 | 17 | 18 | 17 | 17 | 17 | 19 |
| **BODY1** | 25 | 25 | 20 |  |  |  | 26 | 20 | 20 |  |  | 24 | 20 | 20 |  | 22 | 23 | 21 |  |
| **R1** | 27 | 27 | 29 |  | 30 |  | 27 |  |  |  | 27 | 27 | 28 |  | 30 |  |  | 27 | 30 |
| **SEPS** |  |  |  |  | 31 |  |  |  |  |  |  |  |  |  | 31 |  |  |  |  |
| **SEP** |  |  |  |  | 32 |  |  |  |  |  |  |  |  |  | 33 |  |  |  |  |
| **PARTS** | 35 | 35 | 35 | 34 | 35 | 34 | 35 | 35 | 35 | 34 | 35 | 35 | 35 | 35 | 35 | 35 | 35 | 35 | 35 |
| **PART** |  |  |  | 38 |  | 37 |  |  |  | 36 |  |  |  |  |  |  |  |  |  |
| **PRED** | 40 | 40 |  |  |  |  | 39 |  |  |  | 39 | 41 |  |  |  |  |  | 39 |  |
| **IMP** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 42 |  |
| **VP** |  |  |  |  |  |  | 43 |  |  |  | 44 |  |  |  |  |  |  | 45 |  |
| **VPA** | 47 | 47 |  |  | 49 |  |  |  |  |  |  | 48 |  |  | 49 |  |  | 46 | 49 |
| **VTAIL** | 51 | 51 | 51 | 51 | 51 | 51 |  | 51 | 51 | 51 |  | 51 | 51 | 51 | 51 |  | 51 | 50 | 51 |
| **ADJP** | 53 | 52 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| **COMPS** | 56 | 56 | 54 | 56 | 58 | 56 |  | 54 | 54 | 56 |  | 55 | 54 | 54 | 58 |  | 57 |  | 58 |
| **COMPSA** | 60 | 60 |  | 60 | 62 | 60 |  |  |  | 60 |  | 59 |  |  | 62 |  | 61 |  | 62 |
| **NONNP** | 65 | 64 |  | 63 |  | 63 |  |  |  | 63 |  |  |  |  |  |  |  |  |  |
| **SUBCL** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 66 |  |  |
| **QCL** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 67 |  |  |  |
| **QA** | 68 | 69 | 71 |  | 72 |  |  | 71 | 71 |  |  | 70 | 71 | 71 | 72 |  |  |  | 72 |
| **QB** |  |  |  |  | 74 |  | 73 |  |  |  | 73 |  |  |  | 74 |  |  | 73 | 74 |
| **PPX** |  |  | 76 |  |  |  | 75 | 76 | 76 |  | 75 |  | 76 | 76 |  |  |  | 75 |  |
| **PPY** | 78 | 78 |  | 78 | 78 | 78 | 77 |  |  | 78 | 77 | 78 |  |  | 78 |  | 78 | 77 | 78 |
| **NP** |  |  | 79 |  |  |  |  | 80 | 80 |  |  |  | 80 | 80 |  |  |  |  |  |
| **NPB** |  |  |  |  |  |  |  | 82 | 81 |  |  |  | 84 | 83 |  |  |  |  |  |
| **NPB2** | 88 | 88 | 88 | 88 | 88 | 88 | 88 | 86 | 85 | 88 | 88 | 88 | 88 | 87 | 88 |  | 88 | 88 | 88 |
