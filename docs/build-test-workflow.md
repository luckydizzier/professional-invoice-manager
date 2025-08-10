# Build and Test Workflow

Follow these steps to prepare the environment, lint the code, and run tests.

## Environment Setup
- Create a virtual environment.
- Install dependencies:
  ```bash
  pip install -r requirements-dev.txt
  ```

## Lint
Run `flake8` to enforce style:
```bash
python -m flake8 src tests
```

## Test
Execute the test suite:
```bash
pytest
```

See [styleguide.md](docs/styleguide.md) for coding conventions.
