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
49. VTAIL → VERB VTAIL
50. VTAIL → COMPS
51. ADJP → ADVERB ADJP
52. ADJP → ADJECTIVE
53. COMPS → NP COMPSA
54. COMPS → PREPOSITION PPX
55. COMPS → NONNP COMPS
56. COMPS → SUBCL
57. COMPS → ε
58. COMPSA → PREPOSITION PPX
59. COMPSA → NONNP COMPS
60. COMPSA → SUBCL
61. COMPSA → ε
62. NONNP → PART
63. NONNP → ADVERB
64. NONNP → ADJECTIVE
65. SUBCL → SUBJUNCTIVE NP PARTS VP
66. QCL → QUESTION_WORD QA
67. QA → ADJECTIVE QA
68. QA → ADVERB QA
69. QA → PREPOSITION PPX
70. QA → NP QB
71. QA → ε
72. QB → VP
73. QB → ε
74. PPX → VP
75. PPX → NP PPY
76. PPY → VP
77. PPY → COMPSA
78. NP → ARTICLE NPB
79. NP → NPB
80. NPB → NUMBER NPB2
81. NPB → NOUN NPB2
82. NPB → PROPER_NOUN NPB2
83. NPB → PRONOUN
84. NPB2 → NUMBER NPB2
85. NPB2 → NOUN NPB2
86. NPB2 → PROPER_NOUN NPB2
87. NPB2 → ε

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
| **VPA** | 47 | 47 |  |  |  |  |  |  |  |  |  | 48 |  |  |  |  |  | 46 |  |
| **VTAIL** | 50 | 50 | 50 | 50 | 50 | 50 |  | 50 | 50 | 50 |  | 50 | 50 | 50 | 50 |  | 50 | 49 | 50 |
| **ADJP** | 52 | 51 |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |
| **COMPS** | 55 | 55 | 53 | 55 | 57 | 55 |  | 53 | 53 | 55 |  | 54 | 53 | 53 | 57 |  | 56 |  | 57 |
| **COMPSA** | 59 | 59 |  | 59 | 61 | 59 |  |  |  | 59 |  | 58 |  |  | 61 |  | 60 |  | 61 |
| **NONNP** | 64 | 63 |  | 62 |  | 62 |  |  |  | 62 |  |  |  |  |  |  |  |  |  |
| **SUBCL** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 65 |  |  |
| **QCL** |  |  |  |  |  |  |  |  |  |  |  |  |  |  |  | 66 |  |  |  |
| **QA** | 67 | 68 | 70 |  | 71 |  |  | 70 | 70 |  |  | 69 | 70 | 70 | 71 |  |  |  | 71 |
| **QB** |  |  |  |  | 73 |  | 72 |  |  |  | 72 |  |  |  | 73 |  |  | 72 | 73 |
| **PPX** |  |  | 75 |  |  |  | 74 | 75 | 75 |  | 74 |  | 75 | 75 |  |  |  | 74 |  |
| **PPY** | 77 | 77 |  | 77 | 77 | 77 | 76 |  |  | 77 | 76 | 77 |  |  | 77 |  | 77 | 76 | 77 |
| **NP** |  |  | 78 |  |  |  |  | 79 | 79 |  |  |  | 79 | 79 |  |  |  |  |  |
| **NPB** |  |  |  |  |  |  |  | 81 | 80 |  |  |  | 83 | 82 |  |  |  |  |  |
| **NPB2** | 87 | 87 | 87 | 87 | 87 | 87 | 87 | 85 | 84 | 87 | 87 | 87 | 87 | 86 | 87 |  | 87 | 87 | 87 |
