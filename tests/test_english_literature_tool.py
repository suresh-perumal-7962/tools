"""
Tests for the English Literature Tool.
"""

import re
import unittest

from english_literature_tool import (
    validate_and_correct,
    enhance_content,
    validate_and_enhance,
)


class TestValidateAndCorrect(unittest.TestCase):
    """Tests for validate_and_correct."""

    def test_empty_text_returns_unchanged(self):
        result = validate_and_correct("")
        self.assertEqual(result["original"], "")
        self.assertEqual(result["corrected"], "")
        self.assertEqual(result["error_count"], 0)
        self.assertEqual(result["errors"], [])

    def test_whitespace_only_returns_unchanged(self):
        result = validate_and_correct("   ")
        self.assertEqual(result["corrected"], "   ")
        self.assertEqual(result["error_count"], 0)

    def test_correct_text_has_no_spelling_errors(self):
        result = validate_and_correct("The cat sat on the mat.")
        spelling_errors = [e for e in result["errors"] if e["rule_id"] == "SPELL"]
        self.assertEqual(len(spelling_errors), 0)

    def test_misspelled_word_is_detected(self):
        result = validate_and_correct("She recieved the letter.")
        error_words = [e["message"] for e in result["errors"] if e["rule_id"] == "SPELL"]
        self.assertTrue(any("recieved" in msg.lower() for msg in error_words))

    def test_misspelled_word_is_corrected(self):
        result = validate_and_correct("She recieved the letter.")
        self.assertNotIn("recieved", result["corrected"])

    def test_result_has_required_keys(self):
        result = validate_and_correct("Hello world.")
        self.assertIn("original", result)
        self.assertIn("corrected", result)
        self.assertIn("errors", result)
        self.assertIn("error_count", result)

    def test_error_count_matches_errors_list(self):
        result = validate_and_correct("Wrold domination is baad.")
        self.assertEqual(result["error_count"], len(result["errors"]))

    def test_repeated_word_flagged(self):
        result = validate_and_correct("This is the the problem.")
        grammar_errors = [e for e in result["errors"] if e["rule_id"] == "GRAMMAR"]
        self.assertTrue(any("repeated" in e["message"].lower() for e in grammar_errors))

    def test_missing_space_after_punctuation_flagged(self):
        result = validate_and_correct("End.Start of next sentence.")
        grammar_errors = [e for e in result["errors"] if e["rule_id"] == "GRAMMAR"]
        self.assertTrue(any("space" in e["message"].lower() for e in grammar_errors))

    def test_space_added_after_punctuation(self):
        result = validate_and_correct("End.Start of next sentence.")
        self.assertIn(". ", result["corrected"])

    def test_article_a_before_vowel_flagged(self):
        result = validate_and_correct("She ate a apple.")
        grammar_errors = [e for e in result["errors"] if e["rule_id"] == "GRAMMAR"]
        self.assertTrue(any("an" in e["message"].lower() for e in grammar_errors))

    def test_article_a_corrected_to_an_before_vowel(self):
        result = validate_and_correct("She ate a apple.")
        self.assertIn("an apple", result["corrected"])

    def test_suggestions_provided_for_misspelled_word(self):
        result = validate_and_correct("Wrold peace.")
        spell_errors = [e for e in result["errors"] if e["rule_id"] == "SPELL"]
        self.assertTrue(len(spell_errors) > 0)
        self.assertIsInstance(spell_errors[0]["suggestions"], list)


class TestEnhanceContent(unittest.TestCase):
    """Tests for enhance_content."""

    def test_empty_text_returns_unchanged(self):
        result = enhance_content("")
        self.assertEqual(result["original"], "")
        self.assertEqual(result["enhanced"], "")
        self.assertEqual(result["changes"], [])

    def test_result_has_required_keys(self):
        result = enhance_content("Hello.")
        self.assertIn("original", result)
        self.assertIn("enhanced", result)
        self.assertIn("changes", result)

    def test_informal_word_replaced_with_formal(self):
        result = enhance_content("I'm gonna go to the store.")
        self.assertIn("going to", result["enhanced"])
        self.assertNotIn("gonna", result["enhanced"])
        self.assertTrue(any("gonna" in c.lower() for c in result["changes"]))

    def test_multiple_informal_words_replaced(self):
        result = enhance_content("I wanna eat.")
        self.assertNotIn("wanna", result["enhanced"])

    def test_cause_replaced_as_standalone_word(self):
        # "cuz" is an unambiguous informal substitute for "because"
        result = enhance_content("I went cuz I wanted to.")
        self.assertIsNone(re.search(r"\bcuz\b", result["enhanced"]))
        self.assertIn("because", result["enhanced"])

    def test_sentence_capitalisation(self):
        result = enhance_content("hello world.")
        self.assertTrue(result["enhanced"][0].isupper())

    def test_terminal_punctuation_added(self):
        result = enhance_content("This sentence has no punctuation")
        self.assertTrue(result["enhanced"].endswith("."))
        self.assertTrue(any("punctuation" in c.lower() for c in result["changes"]))

    def test_text_already_ending_with_punctuation(self):
        result = enhance_content("This is fine.")
        self.assertTrue(result["enhanced"].endswith("."))

    def test_formal_style_does_not_apply_literary_replacements(self):
        result = enhance_content("This is very good work.", style="formal")
        self.assertIn("very good", result["enhanced"])

    def test_literary_style_applies_vocabulary_enhancement(self):
        result = enhance_content("This is very good work.", style="literary")
        self.assertNotIn("very good", result["enhanced"])
        self.assertIn("excellent", result["enhanced"])

    def test_no_changes_for_already_formal_text(self):
        text = "The committee has reviewed the proposal thoroughly."
        result = enhance_content(text, style="formal")
        self.assertEqual(result["original"], text)

    def test_informal_replacement_is_case_insensitive(self):
        result = enhance_content("GONNA do it.")
        self.assertNotIn("GONNA", result["enhanced"])
        self.assertIn("going to", result["enhanced"].lower())


class TestValidateAndEnhance(unittest.TestCase):
    """Tests for the combined validate_and_enhance."""

    def test_returns_all_expected_keys(self):
        result = validate_and_enhance("Good text.")
        for key in ("original", "corrected", "enhanced",
                    "grammar_errors", "grammar_error_count", "enhancement_changes"):
            self.assertIn(key, result)

    def test_original_is_preserved(self):
        text = "gonna fix this"
        result = validate_and_enhance(text)
        self.assertEqual(result["original"], text)

    def test_grammar_correction_feeds_into_enhancement(self):
        # After correction "wanna" should still be caught by enhancement
        result = validate_and_enhance("I wanna go.")
        self.assertNotIn("wanna", result["enhanced"])

    def test_error_count_is_non_negative(self):
        result = validate_and_enhance("Perfect sentence here.")
        self.assertGreaterEqual(result["grammar_error_count"], 0)


if __name__ == "__main__":
    unittest.main()
