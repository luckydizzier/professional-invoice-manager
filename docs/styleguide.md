# Style Guide

## Python
- Follow [PEP 8](https://peps.python.org/pep-0008/) and enforce with `flake8` using the shared configuration file (e.g., `.flake8` or `setup.cfg`).
- Maximum line length: 79 characters.
- Sort imports alphabetically using `isort`.
- Write clear names and docstrings for modules, classes, and functions.
- Avoid unused variables and committed build artifacts.
- Use the `.flake8` or `setup.cfg` file in the repository to ensure consistent linting rules.

## Git
- Commit message format: `<scope>: <imperative summary>`.
  Examples:
    - `feat: add user authentication`
    - `fix: resolve database connection timeout`
- Reference issues or tasks on a new line: `Refs: <id>`.
- Keep commits focused and atomic.

## Testing
- Lint code with `flake8` before committing.
- Run `pytest` and ensure all tests pass.
- Add tests for new behavior and update existing ones when needed.
