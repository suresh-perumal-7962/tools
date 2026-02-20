# tools

## English Literature Tool

An English literature assistant that validates input content, corrects grammatical errors, and enhances text on request.

### Features

- **Spelling & Grammar Validation** – Detects misspelled words (via [pyspellchecker](https://pypi.org/project/pyspellchecker/)) and flags common grammar issues such as repeated words, incorrect article usage (*a*/*an*), missing spaces after punctuation, and uncapitalised sentence starts.
- **Content Enhancement** – Replaces informal language with formal equivalents, capitalises sentence beginnings, ensures proper terminal punctuation, and (with `--style literary`) substitutes weak vocabulary with stronger alternatives.

### Requirements

- Python 3.8+

### Installation

```bash
pip install -r requirements.txt
```

### Usage

```bash
# Validate and enhance text (default mode)
python3 english_literature_tool.py "I'm gonna do it cuz I wanna."

# Grammar validation only
python3 english_literature_tool.py --mode validate "She recieved a email."

# Enhancement only
python3 english_literature_tool.py --mode enhance "I wanna go."

# Literary style enhancement
python3 english_literature_tool.py --mode enhance --style literary "This is very good work."

# Process a file
python3 english_literature_tool.py --file essay.txt
```

### API

```python
from english_literature_tool import validate_and_correct, enhance_content, validate_and_enhance

# Grammar correction
result = validate_and_correct("She recieved a email.")
print(result["corrected"])        # corrected text
print(result["error_count"])      # number of issues found

# Content enhancement
result = enhance_content("I'm gonna go cuz I wanna.", style="formal")
print(result["enhanced"])         # enhanced text
print(result["changes"])          # list of changes made

# Combined: correct then enhance
result = validate_and_enhance("She gonna go.", style="literary")
print(result["enhanced"])
```

### Running Tests

```bash
python3 -m unittest discover -s tests -v
```
