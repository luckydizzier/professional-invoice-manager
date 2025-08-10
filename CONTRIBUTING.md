# Contributing to Professional Invoice Manager

Thank you for your interest in contributing to the Professional Invoice Manager! This document provides guidelines and instructions for contributing to the project.

## 🎯 How to Contribute

### Reporting Bugs

1. **Check existing issues** first to avoid duplicates
2. **Use the bug report template** when creating new issues
3. **Provide detailed information**:
   - Operating system and version
   - Python version
   - PyQt5 version
   - Steps to reproduce the issue
   - Expected vs actual behavior
   - Screenshots if applicable

### Suggesting Features

1. **Check the roadmap** in issues to see if it's already planned
2. **Open a feature request** with detailed description
3. **Explain the use case** and benefits
4. **Consider implementation complexity**

### Code Contributions

#### Development Setup

1. **Fork the repository**
   ```bash
   git clone https://github.com/yourusername/professional-invoice-manager.git
   cd professional-invoice-manager
   ```

2. **Create a virtual environment**
   ```bash
   python -m venv .venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   ```

3. **Install development dependencies**
   ```bash
   pip install -r requirements-dev.txt
   ```

4. **Run tests to ensure everything works**
   ```bash
   pytest tests/
   ```

#### Development Workflow

1. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes**
   - Follow the coding standards (see below)
   - Add tests for new functionality
   - Update documentation as needed

3. **Run quality checks**
   ```bash
   # Format code
   black .
   isort .
   
   # Lint code
   flake8 .
   
   # Type check
   mypy .
   
   # Run tests
   pytest tests/ --cov=.
   ```

4. **Commit your changes**
   ```bash
   git add .
   git commit -m "feat: add your feature description"
   ```

5. **Push and create pull request**
   ```bash
   git push origin feature/your-feature-name
   ```

## 📋 Coding Standards

### Python Code Style

- **Follow PEP 8** for Python code style
- **Use Black** for automatic code formatting
- **Use isort** for import sorting
- **Use type hints** for better code documentation
- **Write docstrings** for all public functions and classes

### Commit Message Format

Follow the [Conventional Commits](https://www.conventionalcommits.org/) format:

```
<type>[optional scope]: <description>

[optional body]

[optional footer(s)]
```

Types:
- `feat`: A new feature
- `fix`: A bug fix
- `docs`: Documentation only changes
- `style`: Changes that do not affect the meaning of the code
- `refactor`: A code change that neither fixes a bug nor adds a feature
- `test`: Adding missing tests or correcting existing tests
- `chore`: Changes to the build process or auxiliary tools

### Code Organization

```
├── main_with_management.py    # Main application entry point
├── config.py                  # Configuration management
├── style_manager.py           # CSS styling system
├── forms.py                   # Dialog forms
├── styles/                    # CSS stylesheets
│   ├── main.css              # Main application styles
│   └── dialogs.css           # Dialog styles
├── tests/                     # Test files
├── docs/                      # Documentation
└── archive/                   # Development history
```

## 🧪 Testing Guidelines

### Writing Tests

1. **Use pytest** for all tests
2. **Use pytest-qt** for GUI testing
3. **Test both success and failure cases**
4. **Mock external dependencies**
5. **Aim for high test coverage** (>80%)

### Test Categories

```python
# Unit tests - test individual functions/methods
def test_format_date():
    assert format_date(1640995200) == "2022-01-01 00:00"

# Integration tests - test component interactions
def test_invoice_creation_workflow():
    # Test complete invoice creation process
    pass

# GUI tests - test user interface
def test_invoice_form_dialog(qtbot):
    dialog = InvoiceFormDialog()
    qtbot.addWidget(dialog)
    # Test dialog behavior
```

### Running Tests

```bash
# Run all tests
pytest tests/

# Run with coverage
pytest tests/ --cov=.

# Run specific test file
pytest tests/test_management.py

# Run with GUI (if needed)
pytest tests/ --no-xvfb  # Linux
```

## 📚 Documentation

### Code Documentation

- **Use docstrings** for all public functions, classes, and methods
- **Follow Google docstring format**
- **Include examples** for complex functions
- **Document parameters and return values**

Example:
```python
def calculate_vat(amount: int, rate: int) -> int:
    """Calculate VAT amount for given net amount and rate.
    
    Args:
        amount: Net amount in cents
        rate: VAT rate as percentage (e.g., 27 for 27%)
        
    Returns:
        VAT amount in cents
        
    Example:
        >>> calculate_vat(10000, 27)
        2700
    """
    return int(round(amount * rate / 100))
```

### User Documentation

- **Update README.md** for user-facing changes
- **Add to docs/** for detailed documentation
- **Include screenshots** for UI changes
- **Update help text** in the application

## 🔧 Architecture Guidelines

### Design Principles

1. **Separation of Concerns**: Keep UI, business logic, and data access separate
2. **Single Responsibility**: Each class/function should have one clear purpose
3. **Dependency Injection**: Avoid tight coupling between components
4. **Error Handling**: Provide graceful error handling with user feedback

### UI Guidelines

1. **Keyboard Navigation**: All functionality must be accessible via keyboard
2. **Responsive Design**: UI should work on different screen sizes
3. **Accessibility**: Support screen readers and high contrast modes
4. **Professional Appearance**: Maintain consistent styling and layout

### Database Guidelines

1. **Use Transactions**: Wrap related operations in database transactions
2. **Parameterized Queries**: Prevent SQL injection with parameterized queries
3. **Foreign Key Constraints**: Maintain data integrity with constraints
4. **Migration Strategy**: Plan for schema changes and data migration

## 🚀 Release Process

### Version Numbering

Follow [Semantic Versioning](https://semver.org/):
- **MAJOR.MINOR.PATCH** (e.g., 2.1.0)
- **MAJOR**: Breaking changes
- **MINOR**: New features, backward compatible
- **PATCH**: Bug fixes, backward compatible

### Release Checklist

1. **Update version** in setup.py and main application
2. **Update CHANGELOG.md** with release notes
3. **Run full test suite** and ensure all tests pass
4. **Build and test** executables for all platforms
5. **Create release tag** and GitHub release
6. **Update documentation** if needed

## 🤝 Community Guidelines

### Code of Conduct

- **Be respectful** and inclusive in all interactions
- **Help others learn** and grow
- **Provide constructive feedback**
- **Focus on the project's goals**

### Getting Help

- **GitHub Issues**: For bugs and feature requests
- **GitHub Discussions**: For questions and general discussion
- **Documentation**: Check docs/ folder for detailed information

## 📋 Pull Request Checklist

Before submitting a pull request, ensure:

- [ ] Code follows the project's coding standards
- [ ] All tests pass locally
- [ ] New tests are added for new functionality
- [ ] Documentation is updated as needed
- [ ] Commit messages follow the conventional format
- [ ] No merge conflicts with the main branch
- [ ] Screenshots are provided for UI changes

## 🎉 Recognition

Contributors will be recognized in:
- **CONTRIBUTORS.md** file
- **Release notes** for significant contributions
- **GitHub contributors** page

Thank you for contributing to the Professional Invoice Manager! 🚀
