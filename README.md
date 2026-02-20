# tools

## English Literature Grammar Tool

An English literature assistant that validates input content, corrects grammatical errors, and enhances text on request.

### Features

- **Validate** – check text for grammatical errors and receive a corrected version
- **Enhance** – correct grammar *and* improve readability (whitespace normalisation, sentence capitalisation)

### Requirements

- Python 3.8+
- Java 8+ (required by [LanguageTool](https://languagetool.org/))

### Installation

```bash
pip install -r requirements.txt
```

### Usage

```bash
# Validate and correct grammar
python grammar_tool.py validate "She recieved the letter yesterday."

# Enhance content for better readability
python grammar_tool.py enhance "she wrote a wonderfull poem.  it was very beautifull."

# Read from stdin
echo "He go to the store." | python grammar_tool.py validate
```

#### Example output – validate

```
=== Grammar Report ===
Found 1 issue(s):
  1. [MORFOLOGIK_RULE_EN_US] Possible spelling mistake found: "recieved" → "received"
     Context: …She recieved the letter yesterday.…

=== Corrected Text ===
She received the letter yesterday.
```

#### Example output – enhance

```
=== Enhanced Text ===
She wrote a wonderful poem. It was very beautiful.
```

### Running Tests

```bash
python -m unittest discover tests/
```
