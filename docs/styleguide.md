# Style Guide

## Python
- Follow [PEP 8](https://peps.python.org/pep-0008/) and enforce with `flake8`.
- Maximum line length: 79 characters.
- Sort imports alphabetically using `isort`.
- Write clear names and docstrings for modules, classes, and functions.
- Avoid unused variables and committed build artifacts.

## Git
- Commit message format: `<scope>: <imperative summary>`.
- Reference issues or tasks on a new line: `Refs: <id>`.
- Keep commits focused and atomic.

## Testing
- Lint code with `flake8` before committing.
- Run `pytest` and ensure all tests pass.
- Add tests for new behavior and update existing ones when needed.
