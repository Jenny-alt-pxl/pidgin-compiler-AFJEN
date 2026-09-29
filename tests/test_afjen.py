"""
Unit tests for the AFJEN additions: translator, user dictionary, never-reject analysis.
Run:  python tests/test_afjen.py
"""

import os
import sys
import tempfile
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))

import corpus
import statements
import translator as T
import userdict
from lexical_analyzer import LexicalAnalyzer, TokenType
from parser import analyze_robust, parse_statement


class TranslatorTests(unittest.TestCase):
    def test_verified_statements_have_both_languages(self):
        self.assertGreaterEqual(len(T.VERIFIED), 30)
        for text, versions in T.VERIFIED.items():
            self.assertTrue(versions["en"] and versions["fr"], text)
            self.assertEqual(T.translate(text, "en"), (versions["en"], "verified"))
            self.assertEqual(T.translate(text, "fr"), (versions["fr"], "verified"))

    def test_aspect_markers(self):
        cases = {
            "The network dey slow": "The network is slow.",
            "I no fit pay five hundred": "I can't pay five hundred.",
            "The taxi don reach Carrefour": "The taxi has reached Carrefour.",
            "We go reach soon": "We will reach soon.",
            "She bin tchop rice": "She ate rice.",
            "Wuna mos pay for bus": "You all must pay for bus.",
            "How you dey?": "How are you?",
        }
        for src, expected in cases.items():
            self.assertEqual(T.translate(src, "en")[0], expected, src)

    def test_sense_based_expressions(self):
        cases = {
            ("You dey ok", "en"): "You are alright.",
            ("You dey ok?", "en"): "Are you alright?",
            ("You dey dey ok so?", "en"): "Are you normal?",
            ("You dey dey ok so?", "fr"): "Tu es normal ?",
            ("Wetin dey happen?", "en"): "What is going on?",
            ("How you dey?", "fr"): "Comment vas-tu ?",
        }
        for (src, lang), expected in cases.items():
            self.assertEqual(T.translate(src, lang)[0], expected, src)

    def test_french_basics(self):
        self.assertEqual(T.translate("How you dey?", "fr")[0], "Comment vas-tu ?")
        self.assertEqual(T.translate("Driver, stop here", "fr")[0], "Chauffeur, arrête ici.")

    def test_any_text_is_translated_never_refused(self):
        for text in ["x", "asdf qwerty 123 !!!", "é à ü 你好 😀", "the the the", "Brother, drop me. " * 30]:
            for lang in ("en", "fr"):
                out, method = T.translate(text, lang)
                self.assertIsInstance(out, str)
                self.assertIn(method, ("verified", "automatic"))


class RobustAnalysisTests(unittest.TestCase):
    def test_full_partial_and_informal(self):
        r = analyze_robust("The light done cut. the the the. Some random words here today")
        kinds = [s["kind"] for s in r["sentences"]]
        self.assertEqual(kinds[0], "full")
        self.assertIn("informal", kinds[1:])
        self.assertEqual(len(r["sentences"]), 3)

    def test_long_input(self):
        r = analyze_robust("Brother, drop me na at Carrefour Yaoundé. " * 200)
        self.assertEqual(len(r["sentences"]), 200)
        self.assertEqual(r["coverage"], 100)

    def test_strict_parser_still_rejects(self):
        self.assertFalse(parse_statement("the the the")[1])
        self.assertTrue(parse_statement("The light done cut")[1])


class StatementTests(unittest.TestCase):
    def setUp(self):
        self._old = statements.USER_PATH
        self._tmp = tempfile.TemporaryDirectory()
        statements.USER_PATH = os.path.join(self._tmp.name, "user_statements.json")
        statements.apply()

    def tearDown(self):
        statements.USER_PATH = self._old
        statements.apply()
        self._tmp.cleanup()

    def test_corpus_has_thirty_statements_all_accepted(self):
        self.assertEqual(len(corpus.CORPUS), 30)
        for c in corpus.CORPUS:
            self.assertTrue(parse_statement(c["text"])[1], c["text"])
            self.assertTrue(c["en"] and c["fr"])
            self.assertIn(c["topic"], corpus.TOPICS)

    def test_add_and_remove_statement(self):
        ok, _ = statements.add_statement("Waka go slow, road dey bad", "Walk slowly, the road is bad.",
                                         "Marche doucement, la route est mauvaise.", "Taxi & Commuting")
        self.assertTrue(ok)
        self.assertEqual(T.translate("Waka go slow, road dey bad", "fr"),
                         ("Marche doucement, la route est mauvaise.", "verified"))
        self.assertEqual(len(statements.all_statements()), 31)
        self.assertTrue(statements.remove_statement("Waka go slow, road dey bad"))
        self.assertEqual(len(statements.all_statements()), 30)

    def test_validation(self):
        self.assertFalse(statements.add_statement("", "a", "b", "x")[0])
        self.assertFalse(statements.add_statement("hello there", "", "b", "x")[0])
        self.assertFalse(statements.add_statement(str(corpus.CORPUS[0]["text"]), "a", "b", "x")[0])


class DictionaryOrderTests(unittest.TestCase):
    def test_alphabetical(self):
        import dictionary
        words = [r[0] for r in dictionary.build_dictionary()]
        keys = [dictionary.sort_key(w) for w in words]
        self.assertEqual(keys, sorted(keys))
        self.assertGreaterEqual(len(words), 100)


class UserDictionaryTests(unittest.TestCase):
    def setUp(self):
        self._old_path = userdict.USER_PATH
        self._tmp = tempfile.TemporaryDirectory()
        userdict.USER_PATH = os.path.join(self._tmp.name, "user_dictionary.json")
        userdict.apply()

    def tearDown(self):
        userdict.USER_PATH = self._old_path
        userdict.apply()
        self._tmp.cleanup()

    def test_add_noun_and_translate(self):
        ok, _ = userdict.add_word("bobo", "noun", "boyfriend", "copain", "m")
        self.assertTrue(ok)
        self.assertEqual(T.translate("Bobo dey here", "en")[0], "Boyfriend is here.")
        self.assertTrue(userdict.remove_word("bobo"))

    def test_add_verb_changes_token_type(self):
        userdict.add_word("mbanga", "verb", "dance", "danser")
        tokens = LexicalAnalyzer().tokenize("We mbanga")
        self.assertEqual(tokens[1].type, TokenType.VERB)
        self.assertEqual(T.translate("The taxi mbanga", "en")[0], "The taxi dances.")
        self.assertEqual(T.translate("The taxi mbanga", "fr")[0], "Le taxi danse.")

    def test_validation(self):
        self.assertFalse(userdict.add_word("", "noun", "a", "b")[0])
        self.assertFalse(userdict.add_word("two words", "noun", "a", "b")[0])
        self.assertFalse(userdict.add_word("dey", "noun", "a", "b")[0])       # built-in
        self.assertFalse(userdict.add_word("okay", "noun", "", "b")[0])
        self.assertFalse(userdict.add_word("okay", "colour", "a", "b")[0])

    def test_csv_round_trip(self):
        userdict.add_word("kwat", "noun", "neighbourhood", "quartier", "m")
        path = os.path.join(self._tmp.name, "words.csv")
        self.assertEqual(userdict.export_csv(path), 1)
        userdict.remove_word("kwat")
        self.assertEqual(userdict.import_csv(path), (1, 0))


if __name__ == "__main__":
    unittest.main(verbosity=2)
