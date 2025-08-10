# Repository Audit

## 1. Repository Overview
Professional Invoice Manager is a Python and PyQt5 desktop application for managing invoices, products, customers and suppliers. Core UI logic lives in `main_with_management.py` with configuration handled by `src/professional_invoice_manager/config.py`. Tests and documentation accompany the application.

## 2. Folder Structure
```
/                             – project root
├── main_with_management.py   – primary application with management UI
├── launch_app.py             – launcher with error handling
├── forms.py                  – dialog form definitions
├── style_manager.py          – CSS styling helper
├── config.json               – runtime configuration values
├── src/
│   └── professional_invoice_manager/
│       ├── __init__.py
│       └── config.py          – configuration management class
├── tests/                    – test scripts (print‑based)
│   ├── test_implementation.py
│   ├── test_management.py
│   ├── test_vat_features.py
│   └── test_vat_integration.py
├── docs/                     – technical documentation
│   ├── database-fixes.md
│   ├── database-fixes-summary.md
│   ├── implementation-summary.md
│   ├── invoice-edit-fixes.md
│   ├── porting-guide.md
│   ├── technical-specification.md
│   └── vat-summary-implementation.md
├── styles/                   – CSS stylesheets
├── archive/                  – legacy resources
└── .github/workflows/        – CI configuration (read‑only)
```

## 3. Findings
### Code
- `main_with_management.py` is a large monolithic script combining UI, database and business logic.
- `src/` package contains only configuration; application modules are not separated for reuse or testing.
- Minimal error handling and logging; reliance on print statements.

### Tests
- Test files mostly print status instead of using assertions, limiting automated verification.
- Tests depend on real database and PyQt5 UI, complicating CI execution.

### Documentation
- Technical docs exist but no `docs/styleguide.md` despite references, leaving coding standards undefined.
- README provides high-level overview but lacks build/test instructions for contributors.

### Dependencies
- `requirements.txt` pins only PyQt5; development dependencies are commented out, risking drift.
- `requirements-dev.txt` specifies versions from 2020–2021; potential updates needed.

### Security
- No secrets detected; shipped SQLite database (`invoice_qt5.db`) may contain sample data but no credentials.
- Configuration file stores non-sensitive defaults; no encryption or credential handling.

## 4. Recommendations
- Break `main_with_management.py` into modular packages under `src/` (database, UI, models).
- Introduce pytest-style tests with assertions and fixtures; consider mocking database and UI.
- Add `docs/styleguide.md` defining code style, commit conventions and testing requirements.
- Regularly update and pin dependencies; separate production vs. development requirements.
- Exclude sample database from repository or provide tooling to generate it.

## 5. Execution‑Ready Task List
### Milestone 1: Establish Standards
- **Add Style Guide**
  - *Files*: `docs/styleguide.md`
  - *Dependencies*: none
  - *Risk*: Low
- **Document Build/Test Workflow**
  - *Files*: `README.md`, `docs/` as needed
  - *Dependencies*: Style guide
  - *Risk*: Low

### Milestone 2: Improve Test Coverage
- **Refactor Tests to Use Assertions**
  - *Files*: `tests/`
  - *Dependencies*: Milestone 1 (established style & workflow)
  - *Risk*: Medium
- **Introduce Mocked Database Fixtures**
  - *Files*: `tests/`, possibly `src/`
  - *Dependencies*: Test refactor
  - *Risk*: Medium

### Milestone 3: Modularize Application Code
- **Extract Database Layer**
  - *Files*: `src/` new modules
  - *Dependencies*: Milestone 1
  - *Risk*: High
- **Separate UI Components**
  - *Files*: `src/` new modules, `main_with_management.py`
  - *Dependencies*: Database layer extraction
  - *Risk*: High

### Milestone 4: Dependency Management
- **Update Requirements and Introduce Locking**
  - *Files*: `requirements.txt`, `requirements-dev.txt`
  - *Dependencies*: none
  - *Risk*: Medium

### Milestone 5: Database Handling
- **Provide Database Initialization Script**
  - *Files*: `src/`, `docs/`
  - *Dependencies*: Modularization
  - *Risk*: Medium

## 6. Questions / Clarifications Needed
- Should a style guide be created or is an existing internal standard to be referenced?
- Is the committed SQLite database necessary for production use, or can it be generated during setup?
