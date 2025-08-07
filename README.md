# python-rtf

A concise module for converting simple RTF documents to plain text. Supports
common control words (e.g., `\par`, `\line`, `\tab`, `\emdash`, `\endash`,
`\~`), hexadecimal and Unicode escapes, and validates RTF brace structure and
malformed escape sequences.

## Table of Contents
- [Installation](#installation)
- [Usage](#usage)
- [Development](#development)
  - [Running tests](#running-tests)
  - [Linting and type checks](#linting-and-type-checks)
  - [Pre-commit](#pre-commit)
- [License](#license)

## Installation
PythonRTF requires Python 3.10 or newer and uses [uv](https://github.com/astral-sh/uv) for dependency management. Ensure `uv` is installed:

```bash
pip install uv
```

## Usage
Convert an RTF file to plain text:

```python
from rtf import RTF

print(RTF.to_plain_text("filename.rtf"))
```

The `RTF` class caches the plain text interpretation of the file and only reparses when the file changes:

```python
from rtf import RTF

r = RTF("input.rtf")
print(r.plain_text())
r.dump("output.txt")
```

## Development
All development tasks rely on `uv` to provide the required tools.

### Running tests
```bash
uvx --with pytest-cov --with-editable . pytest --cov=rtf --cov-report=term-missing
```

### Linting and type checks
```bash
uvx ruff format .
uvx ruff check .
uvx --with pytest pyright
```

### Pre-commit
Run all formatting, linting, type checking, and tests:

```bash
uvx pre-commit run --all-files
```

## License
This project is licensed under the terms of the [MIT License](LICENSE).
