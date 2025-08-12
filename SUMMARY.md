Problem statement:
Add docstrings for optional connection parameter in database utilities.

Approach taken:
Implemented optional connection parameter handling in `get_db` and `init_database` and documented behavior.

Files changed:
- src/professional_invoice_manager/db.py

Risks & mitigations:
- Misuse of connection parameter could close caller-supplied connections; safeguarded by only closing when created internally.

Assumptions:
- Tests continue to depend on existing behavior when no connection is supplied.
