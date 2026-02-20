"""
English Literature Grammar Tool
Validates input content, corrects grammatical errors, and enhances text on request.
"""

import argparse
import re
import sys

import language_tool_python


def get_tool() -> language_tool_python.LanguageTool:
    """Initialise and return a LanguageTool instance for English."""
    return language_tool_python.LanguageTool("en-US")


def validate_and_correct(text: str, tool: language_tool_python.LanguageTool) -> dict:
    """
    Validate the given text and return corrected text along with a list of issues found.

    Returns a dict with keys:
        - corrected: the corrected text
        - issues: list of dicts describing each error/suggestion
    """
    matches = tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)
    issues = [
        {
            "message": match.message,
            "context": match.context,
            "offset": match.offset,
            "length": match.errorLength,
            "replacements": match.replacements[:3],
            "rule": match.ruleId,
        }
        for match in matches
    ]
    return {"corrected": corrected, "issues": issues}


def enhance(text: str, tool: language_tool_python.LanguageTool) -> str:
    """
    Enhance the given text by:
    1. Correcting all grammatical errors detected by LanguageTool.
    2. Applying sentence-level capitalisation and spacing normalisation.

    Returns the enhanced text.
    """
    # Step 1 – apply grammar corrections
    matches = tool.check(text)
    enhanced = language_tool_python.utils.correct(text, matches)

    # Step 2 – normalise whitespace and sentence capitalisation
    enhanced = _normalise_whitespace(enhanced)
    enhanced = _capitalise_sentences(enhanced)

    return enhanced


def _normalise_whitespace(text: str) -> str:
    """Collapse multiple spaces/newlines and strip leading/trailing whitespace."""
    text = re.sub(r" {2,}", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


def _capitalise_sentences(text: str) -> str:
    """Ensure the first letter of every sentence is capitalised."""

    def capitalise_match(match):
        return match.group(1) + match.group(2).upper()

    return re.sub(r"([.!?]\s+)([a-z])", capitalise_match, text)


def _print_issues(issues: list) -> None:
    if not issues:
        print("No grammatical issues found.")
        return
    print(f"Found {len(issues)} issue(s):")
    for i, issue in enumerate(issues, 1):
        replacements = ", ".join(f'"{r}"' for r in issue["replacements"])
        replacement_str = f" → {replacements}" if replacements else ""
        print(f"  {i}. [{issue['rule']}] {issue['message']}{replacement_str}")
        print(f"     Context: …{issue['context']}…")


def main() -> None:
    parser = argparse.ArgumentParser(
        description="English Literature Tool – validate, correct, and enhance text."
    )
    parser.add_argument(
        "mode",
        choices=["validate", "enhance"],
        help=(
            '"validate" – check and correct grammar; '
            '"enhance" – correct grammar and improve readability'
        ),
    )
    parser.add_argument(
        "text",
        nargs="?",
        help="Text to process. If omitted, text is read from standard input.",
    )
    args = parser.parse_args()

    if args.text:
        text = args.text
    else:
        print("Enter text (press Ctrl+D when done):", file=sys.stderr)
        text = sys.stdin.read()

    if not text.strip():
        print("Error: no input text provided.", file=sys.stderr)
        sys.exit(1)

    tool = get_tool()

    if args.mode == "validate":
        result = validate_and_correct(text, tool)
        print("=== Grammar Report ===")
        _print_issues(result["issues"])
        print()
        print("=== Corrected Text ===")
        print(result["corrected"])
    else:
        enhanced = enhance(text, tool)
        print("=== Enhanced Text ===")
        print(enhanced)


if __name__ == "__main__":
    main()
