import sys
from pathlib import Path

import pytest

sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from professional_invoice_manager.config import (  # noqa: E402
    config as app_config,
)
from professional_invoice_manager.db import init_database  # noqa: E402


@pytest.fixture(autouse=True)
def temporary_database(tmp_path):
    original_db_path = app_config.db_path
    test_db_path = tmp_path / "test.db"
    app_config.set("database.path", str(test_db_path))
    init_database()
    yield
    if test_db_path.exists():
        test_db_path.unlink()
    app_config.set("database.path", original_db_path)
