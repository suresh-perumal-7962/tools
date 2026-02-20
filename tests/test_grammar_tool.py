"""Tests for grammar_tool.py"""

import unittest
from unittest.mock import MagicMock, patch

from grammar_tool import (
    _capitalise_sentences,
    _normalise_whitespace,
    enhance,
    validate_and_correct,
)


def _make_mock_match(message, context, offset, length, replacements, rule_id):
    """Create a mock LanguageTool match object."""
    m = MagicMock()
    m.message = message
    m.context = context
    m.offset = offset
    m.errorLength = length
    m.replacements = replacements
    m.ruleId = rule_id
    return m


class TestValidateAndCorrect(unittest.TestCase):
    def test_correct_text_has_no_issues(self):
        tool = MagicMock()
        tool.check.return_value = []
        original = "The quick brown fox jumps over the lazy dog."
        with patch("grammar_tool.language_tool_python.utils.correct", return_value=original):
            result = validate_and_correct(original, tool)
        self.assertEqual(result["issues"], [])
        self.assertEqual(result["corrected"], original)

    def test_detects_grammar_error(self):
        match = _make_mock_match(
            message="Possible agreement error.",
            context="He go to the store.",
            offset=3,
            length=2,
            replacements=["goes"],
            rule_id="HE_VERB_AGR",
        )
        tool = MagicMock()
        tool.check.return_value = [match]
        with patch(
            "grammar_tool.language_tool_python.utils.correct",
            return_value="He goes to the store.",
        ):
            result = validate_and_correct("He go to the store.", tool)
        self.assertEqual(len(result["issues"]), 1)

    def test_corrects_spelling_error(self):
        match = _make_mock_match(
            message='Possible spelling mistake found: "recieved".',
            context="She recieved the letter.",
            offset=4,
            length=8,
            replacements=["received"],
            rule_id="MORFOLOGIK_RULE_EN_US",
        )
        tool = MagicMock()
        tool.check.return_value = [match]
        with patch(
            "grammar_tool.language_tool_python.utils.correct",
            return_value="She received the letter.",
        ):
            result = validate_and_correct("She recieved the letter.", tool)
        self.assertIn("received", result["corrected"])

    def test_returns_issue_keys(self):
        match = _make_mock_match(
            message="Agreement error.",
            context="I goes to school.",
            offset=2,
            length=4,
            replacements=["go"],
            rule_id="AGREEMENT",
        )
        tool = MagicMock()
        tool.check.return_value = [match]
        with patch(
            "grammar_tool.language_tool_python.utils.correct",
            return_value="I go to school.",
        ):
            result = validate_and_correct("I goes to school.", tool)
        issue = result["issues"][0]
        for key in ("message", "context", "offset", "length", "replacements", "rule"):
            self.assertIn(key, issue)

    def test_corrected_text_is_string(self):
        tool = MagicMock()
        tool.check.return_value = []
        with patch(
            "grammar_tool.language_tool_python.utils.correct",
            return_value="There are many reasons.",
        ):
            result = validate_and_correct("Their are many reasons.", tool)
        self.assertIsInstance(result["corrected"], str)


class TestEnhance(unittest.TestCase):
    def test_returns_non_empty_string(self):
        tool = MagicMock()
        tool.check.return_value = []
        with patch(
            "grammar_tool.language_tool_python.utils.correct",
            return_value="She wrote a beautiful poem.",
        ):
            result = enhance("she wrote a beautifull poem.", tool)
        self.assertIsInstance(result, str)
        self.assertTrue(len(result) > 0)

    def test_corrects_spelling_during_enhancement(self):
        tool = MagicMock()
        tool.check.return_value = []
        with patch(
            "grammar_tool.language_tool_python.utils.correct",
            return_value="He wrote a wonderful story.",
        ):
            result = enhance("He writed a wonderfull story.", tool)
        self.assertNotIn("wonderfull", result)

    def test_no_leading_trailing_whitespace(self):
        tool = MagicMock()
        tool.check.return_value = []
        with patch(
            "grammar_tool.language_tool_python.utils.correct",
            return_value="   This is a test.   ",
        ):
            result = enhance("   This is a test.   ", tool)
        self.assertEqual(result, result.strip())


class TestNormaliseWhitespace(unittest.TestCase):
    def test_collapses_multiple_spaces(self):
        self.assertEqual(_normalise_whitespace("hello   world"), "hello world")

    def test_strips_leading_trailing(self):
        self.assertEqual(_normalise_whitespace("  hello  "), "hello")

    def test_collapses_excess_newlines(self):
        result = _normalise_whitespace("line1\n\n\n\nline2")
        self.assertEqual(result, "line1\n\nline2")


class TestCapitaliseSentences(unittest.TestCase):
    def test_capitalises_after_period(self):
        result = _capitalise_sentences("hello. world.")
        self.assertEqual(result, "hello. World.")

    def test_capitalises_after_exclamation(self):
        result = _capitalise_sentences("great! now go.")
        self.assertEqual(result, "great! Now go.")

    def test_capitalises_after_question(self):
        result = _capitalise_sentences("done? yes indeed.")
        self.assertEqual(result, "done? Yes indeed.")

    def test_no_change_when_already_capitalised(self):
        text = "Hello. World."
        self.assertEqual(_capitalise_sentences(text), text)


if __name__ == "__main__":
    unittest.main()

