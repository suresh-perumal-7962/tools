"""
English Literature Tool

Validates input content, corrects grammatical errors, and enhances content on request.
"""

import re
import argparse
import sys
from spellchecker import SpellChecker


# ─────────────────────────────────────────────
# Grammar rule definitions
# ─────────────────────────────────────────────

# Common informal-to-formal word replacements for content enhancement
INFORMAL_TO_FORMAL = {
    "gonna": "going to",
    "wanna": "want to",
    "kinda": "kind of",
    "sorta": "sort of",
    "gotta": "got to",
    "yeah": "yes",
    "yep": "yes",
    "nope": "no",
    "cuz": "because",
    "cos": "because",
    "gimme": "give me",
    "lemme": "let me",
    "woulda": "would have",
    "coulda": "could have",
    "shoulda": "should have",
    "lotsa": "lots of",
    "lotta": "a lot of",
    "ya": "you",
    "thru": "through",
    "tho": "though",
    "asap": "as soon as possible",
    "btw": "by the way",
    "imo": "in my opinion",
    "fyi": "for your information",
}

# Weak expressions replaced with stronger alternatives in 'literary' style
WEAK_TO_STRONG = {
    r"\bvery good\b": "excellent",
    r"\bvery bad\b": "terrible",
    r"\bvery big\b": "enormous",
    r"\bvery small\b": "tiny",
    r"\bvery happy\b": "elated",
    r"\bvery sad\b": "despondent",
    r"\bvery tired\b": "exhausted",
    r"\bvery hungry\b": "famished",
    r"\bvery large\b": "immense",
    r"\bvery fast\b": "swift",
    r"\bvery slow\b": "sluggish",
    r"\bvery cold\b": "frigid",
    r"\bvery hot\b": "scorching",
    r"\bvery angry\b": "furious",
    r"\bvery scared\b": "terrified",
    r"\bnice\b": "pleasant",
}

# Common grammar rule patterns: (pattern, suggestion_message, re_flags)
# Note: use 0 (no flags) for rules that must be case-sensitive.
GRAMMAR_RULES = [
    # Doubled words, e.g. "the the"
    (
        r"\b(\w+)\s+\1\b",
        'Possible repeated word: "{word}".',
        re.IGNORECASE,
    ),
    # "a" before vowel sound
    (
        r"\ba ([aeiouAEIOU]\w+)",
        'Use "an" instead of "a" before a vowel sound.',
        re.IGNORECASE,
    ),
    # "an" before consonant sound
    (
        r"\ban ([^aeiouAEIOU\s]\w+)",
        'Use "a" instead of "an" before a consonant sound.',
        re.IGNORECASE,
    ),
    # Missing space after sentence-ending punctuation (case-sensitive: match letter)
    (
        r"[.!?][A-Za-z]",
        "Missing space after punctuation.",
        0,
    ),
    # Lowercase letter immediately after sentence-ending punctuation + whitespace
    (
        r"[.!?]\s+[a-z]",
        "Sentence should begin with a capital letter.",
        0,
    ),
]

# ─────────────────────────────────────────────
# Core functions
# ─────────────────────────────────────────────

_spell_checker = None


def _get_spell_checker() -> SpellChecker:
    """Return a shared SpellChecker instance (lazily initialised)."""
    global _spell_checker
    if _spell_checker is None:
        _spell_checker = SpellChecker()
    return _spell_checker


def _check_spelling(text: str) -> list[dict]:
    """Return a list of spelling errors found in *text*."""
    checker = _get_spell_checker()

    # Words that are informal (will be handled by enhancement) or are
    # contractions – we exclude these from spell-checking to avoid
    # incorrect "corrections".
    _skip_words = set(INFORMAL_TO_FORMAL.keys())

    errors = []
    for match in re.finditer(r"\b[a-zA-Z]+(?:'[a-zA-Z]+)?\b", text):
        word = match.group()
        # Skip single letters
        if len(word) <= 1:
            continue
        # Skip contractions (e.g. "I'm", "don't", "it's")
        if "'" in word:
            continue
        # Skip words handled by the informal→formal replacements
        if word.lower() in _skip_words:
            continue
        misspelled = checker.unknown([word.lower()])
        if misspelled:
            candidates = list(checker.candidates(word.lower()) or [])
            errors.append(
                {
                    "message": f'Possible spelling mistake: "{word}".',
                    "offset": match.start(),
                    "length": len(word),
                    "context": text[max(0, match.start() - 20): match.end() + 20],
                    "suggestions": candidates[:3],
                    "rule_id": "SPELL",
                }
            )
    return errors


def _check_grammar_rules(text: str) -> list[dict]:
    """Return a list of grammar issues found in *text* using built-in rules."""
    errors = []
    for pattern, message_template, flags in GRAMMAR_RULES:
        for match in re.finditer(pattern, text, flags):
            word = match.group(1) if match.lastindex else match.group()
            errors.append(
                {
                    "message": message_template.format(word=word),
                    "offset": match.start(),
                    "length": len(match.group()),
                    "context": text[max(0, match.start() - 20): match.end() + 20],
                    "suggestions": [],
                    "rule_id": "GRAMMAR",
                }
            )
    return errors


def _apply_spelling_corrections(text: str, spelling_errors: list[dict]) -> str:
    """Apply spelling corrections to *text* in reverse order (to preserve offsets)."""
    checker = _get_spell_checker()
    # Sort by offset descending so earlier corrections don't shift later offsets
    for error in sorted(spelling_errors, key=lambda e: e["offset"], reverse=True):
        if error["suggestions"]:
            start = error["offset"]
            end = start + error["length"]
            # Preserve the original capitalisation of the first letter
            replacement = error["suggestions"][0]
            if text[start].isupper():
                replacement = replacement.capitalize()
            text = text[:start] + replacement + text[end:]
    return text


def _apply_grammar_corrections(text: str) -> str:
    """Apply automatic grammar corrections for the built-in rules."""
    # Fix "a" → "an" before vowels
    text = re.sub(r"\ba ([aeiouAEIOU]\w+)", r"an \1", text)
    # Fix "an" → "a" before consonants
    text = re.sub(r"\ban ([^aeiouAEIOU\s]\w+)", r"a \1", text)
    # Add space after punctuation where missing (before a letter)
    text = re.sub(r"([.!?])([A-Za-z])", r"\1 \2", text)
    # Capitalise after sentence-ending punctuation
    text = re.sub(
        r"([.!?]\s+)([a-z])",
        lambda m: m.group(1) + m.group(2).upper(),
        text,
    )
    return text


def validate_and_correct(text: str) -> dict:
    """
    Validate the input text and correct spelling and grammar errors.

    Args:
        text: The input text to validate and correct.

    Returns:
        A dictionary with keys:
            - ``original``    – the original text
            - ``corrected``   – the corrected text
            - ``errors``      – list of detected errors with details
            - ``error_count`` – total number of errors found
    """
    if not text or not text.strip():
        return {
            "original": text,
            "corrected": text,
            "errors": [],
            "error_count": 0,
        }

    spelling_errors = _check_spelling(text)
    grammar_errors = _check_grammar_rules(text)
    all_errors = spelling_errors + grammar_errors

    corrected = _apply_spelling_corrections(text, spelling_errors)
    corrected = _apply_grammar_corrections(corrected)

    return {
        "original": text,
        "corrected": corrected,
        "errors": all_errors,
        "error_count": len(all_errors),
    }


def enhance_content(text: str, style: str = "formal") -> dict:
    """
    Enhance the input text by improving vocabulary, tone, and style.

    Args:
        text:  The input text to enhance.
        style: Enhancement style – ``'formal'`` (default) or ``'literary'``.

    Returns:
        A dictionary with keys:
            - ``original`` – the original text
            - ``enhanced`` – the enhanced text
            - ``changes``  – list of human-readable descriptions of changes made
    """
    if not text or not text.strip():
        return {
            "original": text,
            "enhanced": text,
            "changes": [],
        }

    enhanced = text
    changes = []

    # Replace informal words with formal equivalents
    for informal, formal in INFORMAL_TO_FORMAL.items():
        pattern = r"\b" + re.escape(informal) + r"\b"
        if re.search(pattern, enhanced, re.IGNORECASE):
            new_text = re.sub(pattern, formal, enhanced, flags=re.IGNORECASE)
            if new_text != enhanced:
                changes.append(f'Replaced "{informal}" with "{formal}"')
                enhanced = new_text

    # Apply stronger vocabulary for 'literary' style
    if style == "literary":
        for pattern, replacement in WEAK_TO_STRONG.items():
            new_text = re.sub(pattern, replacement, enhanced, flags=re.IGNORECASE)
            if new_text != enhanced:
                match = re.search(pattern, text, re.IGNORECASE)
                original_expr = match.group(0) if match else pattern
                changes.append(f'Enhanced "{original_expr}" to "{replacement}"')
                enhanced = new_text

    # Capitalise the beginning of each sentence
    sentences = re.split(r"(?<=[.!?])\s+", enhanced)
    capitalized = [s[0].upper() + s[1:] if s else s for s in sentences]
    new_text = " ".join(capitalized)
    if new_text != enhanced:
        changes.append("Capitalised sentence beginnings")
        enhanced = new_text

    # Ensure the text ends with proper punctuation
    stripped = enhanced.rstrip()
    if stripped and stripped[-1] not in ".!?":
        enhanced = stripped + "."
        changes.append("Added terminal punctuation")

    return {
        "original": text,
        "enhanced": enhanced,
        "changes": changes,
    }


def validate_and_enhance(text: str, style: str = "formal") -> dict:
    """
    Validate, correct grammatical errors, and enhance the input text.

    Args:
        text:  The input text to process.
        style: Enhancement style – ``'formal'`` (default) or ``'literary'``.

    Returns:
        A dictionary combining validation and enhancement results.
    """
    validation_result = validate_and_correct(text)
    enhancement_result = enhance_content(validation_result["corrected"], style=style)

    return {
        "original": text,
        "corrected": validation_result["corrected"],
        "enhanced": enhancement_result["enhanced"],
        "grammar_errors": validation_result["errors"],
        "grammar_error_count": validation_result["error_count"],
        "enhancement_changes": enhancement_result["changes"],
    }


# ─────────────────────────────────────────────
# CLI helpers
# ─────────────────────────────────────────────

def _format_result(result: dict, mode: str) -> str:
    """Format a result dictionary as human-readable output."""
    lines = ["=" * 60]

    if mode in ("validate", "both"):
        lines.append(f"Original Text:\n  {result.get('original', '')}")
        lines.append(f"\nCorrected Text:\n  {result.get('corrected', result.get('original', ''))}")
        error_count = result.get("grammar_error_count", result.get("error_count", 0))
        lines.append(f"\nIssues Found: {error_count}")
        for i, error in enumerate(
            result.get("grammar_errors", result.get("errors", [])), 1
        ):
            lines.append(f"  {i}. {error['message']}")
            if error["suggestions"]:
                lines.append(f"     Suggestions: {', '.join(error['suggestions'])}")

    if mode in ("enhance", "both"):
        lines.append(f"\nEnhanced Text:\n  {result.get('enhanced', '')}")
        changes = result.get("enhancement_changes", result.get("changes", []))
        if changes:
            lines.append(f"\nEnhancements Applied ({len(changes)}):")
            for change in changes:
                lines.append(f"  - {change}")
        else:
            lines.append("\nNo enhancements were necessary.")

    lines.append("=" * 60)
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="English Literature Tool: validate grammar and enhance content."
    )
    parser.add_argument("text", nargs="?", help="Text to process (or use --file)")
    parser.add_argument("--file", "-f", help="Path to a text file to process")
    parser.add_argument(
        "--mode",
        "-m",
        choices=["validate", "enhance", "both"],
        default="both",
        help=(
            "Processing mode: validate (grammar only), "
            "enhance (style only), or both (default)"
        ),
    )
    parser.add_argument(
        "--style",
        "-s",
        choices=["formal", "literary"],
        default="formal",
        help="Enhancement style: formal (default) or literary",
    )

    args = parser.parse_args()

    if args.file:
        try:
            with open(args.file, "r", encoding="utf-8") as fh:
                text = fh.read()
        except FileNotFoundError:
            print(f"Error: File '{args.file}' not found.", file=sys.stderr)
            sys.exit(1)
    elif args.text:
        text = args.text
    else:
        print("Reading from stdin (press Ctrl+D when done):")
        text = sys.stdin.read()

    if args.mode == "validate":
        result = validate_and_correct(text)
    elif args.mode == "enhance":
        result = enhance_content(text, style=args.style)
    else:
        result = validate_and_enhance(text, style=args.style)

    print(_format_result(result, args.mode))


if __name__ == "__main__":
    main()
