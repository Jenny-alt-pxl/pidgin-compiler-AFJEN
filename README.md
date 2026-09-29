# AFJEN Compiler

**Lexical and syntactic analysis - and translation - of Yaoundé street speech**

Founded by **Tembong Jennette** and **Abang Afumbon** - *AFJEN* = **AF**umbon + **JEN**nette.
CS4110 Compiler Construction · ICT University · Instructor: Engr. Tanwi Nkiamboh · September 2026

---

## What is AFJEN?

Yaoundé is a multilingual city: people mix English, French, Pidgin, Ewondo, Fulfulde and slang
("franc-anglais") in a single sentence. AFJEN is a small compiler toolchain for that speech. Give it any amount of
text and it will:

1. **read the words** (lexical analysis, 19 token types defined by regular expressions),
2. **check the structure** (strict table-driven LL(1) parser, conflict-free grammar),
3. **work out the topic and intent** (semantic analysis),
4. **translate it into standard English or Français** - by *sense*, not word by word,
5. **keep learning**: you can add words, expressions and whole statements from the interface.

Nothing is ever refused in the app: unknown words are kept and collected, and looser sentences are analysed clause
by clause. The strict accept / reject behaviour of the grammar is demonstrated by the exam tests.

## Quick start

Requires Python 3.10+ (tkinter is included with the standard Windows installer). No other packages.

```bash
python run_gui.py                              # the AFJEN Compiler desktop window (Python + tkinter)
python run_web.py                              # the AFJEN web app in your browser (JavaScript + Node.js + Express)
python main.py                                 # interactive text menu
python main.py translate "You dey ok?"         # English and Français in the terminal
python main.py analyze "The light done cut again"
python main.py test                            # full test suite for the 30 statements
python main.py accept-reject                   # accepted / rejected sentences (strict LL(1) grammar)
python main.py trace "The light done cut"      # step-by-step LL(1) parse (stack, lookahead, action)
python main.py grammar                         # grammar, FIRST/FOLLOW sets, conflict check
python main.py words                           # the dictionary (A-Z)
python tests/test_afjen.py                     # 18 unit tests for the translator, dictionary, statements and engine
cd web && node --test test/api.test.js         # 7 API tests for the web app
python analysis/generate_tables.py             # regenerate grammar / FIRST-FOLLOW / parsing-table documents
```

## Two front ends, two languages

AFJEN has one compiler engine and two ways to use it:

| | Language / framework | Run |
|---|---|---|
| **Desktop app** | Python + tkinter | `python run_gui.py` |
| **Web app** | JavaScript (Node.js + **Express** server, HTML/CSS/JS front end) | `python run_web.py` (or `npm install` then `npm start`) |

The web app lives in `web/`. The Express server (`web/server.js`) starts the Python engine once (`web/bridge.py`,
which calls `src/engine.py`) and exchanges one JSON line per request with it, so the browser and the desktop window
always give identical results - lexer, LL(1) parser, translation, dictionary and statements are never duplicated.
API: `POST /api/analyze`, `GET|POST|DELETE /api/dictionary`, `GET|POST|DELETE /api/statements`, `GET /api/insights`,
`GET /api/health`. Requirements: Node.js 18+ (nodejs.org) and Python 3.

**Running the web app** - from the project folder (`pidgin-compiler-AFJEN`):
```
python run_web.py
```
It finds Node.js, installs the web dependencies the first time, picks a free port (3000, or the next free one),
starts the server and opens your browser. Press Ctrl+C to stop. Alternatives: `npm install` then `npm start` (from the
project folder or from `web/`).

| Problem | Fix |
|---|---|
| `Node.js was not found` / `npm is not recognized` | Install the LTS version from nodejs.org, then close and reopen the terminal / VS Code |
| `Could not read package.json` | You are in the wrong folder - `cd` into `pidgin-compiler-AFJEN` first |
| `Cannot find module 'express'` | Run `npm install` (or just `python run_web.py`, which installs it) |
| Page says "Could not start Python" | Run `python run_web.py` (it passes the right Python), or set `AFJEN_PYTHON` to your python.exe |
| Port 3000 busy | Nothing to do - it moves to 3001, 3002 ... and prints the address |

## The interface

| Page | What it does |
|---|---|
| **Translate** | Type or paste text; live translation; English / Français switch; **Save to file**, Copy, Copy both; word table, sentence tree and grammar-fit ring |
| **Dictionary** | 350+ words and expressions in alphabetical order (A-Z letter bar, search); add, remove, import / export CSV |
| **Statements** | The 30 statements with verified English and French; add your own; export CSV |
| **Insights** | Word-frequency chart from your word bank and your translation history |
| **Test Suite** | Run the exam tests inside the app |
| **Grammar** | The LL(1) grammar with FIRST / FOLLOW sets |
| **About** | The founders, the story of the project and how AFJEN works |

**＋ Add word** and **＋ Add statement** are available on every page. Words can be nouns, verbs, adjectives,
adverbs, interjections, proper nouns or whole **expressions**; they work immediately in the lexer, the parser and the
translator. They are stored in `data/user_dictionary.json` and `data/user_statements.json`.

## Translation - by sense

Three layers, in this order:

1. **Verified** - hand-checked English and French for the 30 statements (and any statement you add).
2. **Expressions** - meaning-based translation of common phrases, aware of the question mark:

   | Pidgin | English | Français |
   |---|---|---|
   | you dey ok | You are alright. | Tu vas bien. |
   | you dey ok? | Are you alright? | Tu vas bien ? |
   | you dey dey ok so? | Are you normal? | Tu es normal ? |
   | wetin dey happen? | What is going on? | Qu'est-ce qui se passe ? |
   | how you dey? | How are you? | Comment vas-tu ? |

3. **Rule engine** - rewrites Pidgin tense and aspect: `dey` = is / are doing, `done` / `don` = has / have done,
   `go` = will, `bin` = did, `wan` = want to, `mos` = must, `no fit` = cannot, `make we` = let's, `wahala` = trouble.
   The output is labelled *Automatic*; its French is the weakest part, so review it - and use
   **Save as a statement…** to store a corrected, verified version.

## How it works (pipeline)

```
text ──► lexical analyzer ──► LL(1) parser ──► semantic analysis ──► translator
         (regular expressions)  (stack + table)   (topic, intent)      (verified → expressions → rules)
```

- `src/lexical_analyzer.py` - regex-based tokenizer with line:column tracking; user-taught words extend it.
- `src/grammar.py` - the LL(1) grammar: 32 non-terminals, 88 productions, 275 table entries, **0 conflicts**;
  FIRST / FOLLOW sets and the predictive table are computed from the productions.
  Left recursion is removed and left factoring applied (see `FINAL_REPORT.md`, section 3).
- `src/parser.py` - table-driven predictive parser with exact error messages; `analyze_robust()` powers the
  never-reject analysis used by the GUI. The earlier permissive parser is kept in `src/lenient_parser.py`.
- `src/semantic_analyzer.py` - topic and intent.
- `src/translator.py`, `src/userdict.py`, `src/statements.py`, `src/dictionary.py`, `src/corpus.py` - translation,
  user data and the dictionary / word bank.

## The statements

`src/corpus.py` holds 30 statements across the exam topics (taxi and commuting, poor internet, electricity, market
bargaining, rainy season, fuel scarcity, roadside business, bendskin, security checkpoints, ICT University, everyday
transactions). **Statements 1-15 were collected in Yaoundé; 16-30 are further typical examples** written for the
project - replace them with statements your group heard yourselves (or add your own in the app). All 30 are accepted by
the strict grammar. `data/collected_statements.txt` lists them by topic.

## Project structure

```
run_gui.py, gui_application.py     the AFJEN desktop window (Python + tkinter)
web/                               the AFJEN web app: server.js (Express), bridge.py, public/ (HTML, CSS, JS), test/
main.py                            menu and command line
src/                               lexer, grammar, parsers, translator, dictionary, statements, semantic analysis
tests/test_cases.py                exam tests (30 statements + accepted / rejected sentences)
tests/test_afjen.py                unit tests (translator, expressions, dictionary, statements)
data/                              statements, grammar rules, token specification, your words / statements, word bank
analysis/                          FIRST/FOLLOW, LL(1) table, test and semantic reports, table generator
archive/part-2/                    the earlier "Part-2" branch work, kept for reference (see below)
FINAL_REPORT.md, PRESENTATION_GUIDE.md, PROJECT_COMPLETION_SUMMARY.txt   documentation
```

## Tests

`python main.py test` runs lexical, syntactic, semantic and diagnostic tests on all 30 statements and the
accepted / rejected sentence sets (30 collected + 14 unseen grammatical sentences must be accepted; 14 malformed
sequences must be rejected). `python tests/test_afjen.py` runs 18 unit tests, and `node --test web/test/api.test.js` runs 7 API tests through the
JavaScript server into the Python engine.

## Notes on the repository

- `archive/part-2/` holds the files of the `Part-2` branch (an earlier, flat copy of the project). They are kept only
  so nothing is lost; the live code is in `src/`, `tests/`, `data/` and `analysis/`.
- `FINAL_REPORT.md` follows the exam paper's structure; sections that quote statement and token counts should be
  re-checked against `python main.py test` before submission (the corpus grew from 15 to 30 statements).

## Credits

Built by **Tembong Jennette** and **Abang Afumbon** for CS4110 at ICT University, with the guidance of
Engr. Tanwi Nkiamboh. *Made with pride in Yaoundé.*
