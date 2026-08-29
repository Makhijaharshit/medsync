"""
Phase 1.1 migration test.

Verifies the initial migration can upgrade to head, downgrade to base,
and upgrade again — all against the live PostgreSQL.
"""
import subprocess
import sys
from pathlib import Path

from sqlalchemy import inspect

from app.core.database import engine

BACKEND_DIR = Path(__file__).resolve().parent.parent
ALEMBIC_CMD = [sys.executable, "-m", "alembic"]
EXPECTED_TABLES = {
    "users",
    "roles",
    "user_roles",
    "patient_profiles",
    "clinician_profiles",
    "responder_profiles",
    "organizations",
}


def _alembic(*args: str) -> None:
    subprocess.run(
        [*ALEMBIC_CMD, *args],
        cwd=BACKEND_DIR,
        check=True,
        capture_output=True,
    )


def _table_names() -> set[str]:
    return set(inspect(engine).get_table_names())


def test_migration_upgrade_downgrade_upgrade_cycle():
    # Start from head (session fixture has already upgraded).
    assert EXPECTED_TABLES.issubset(_table_names())

    # Downgrade to base — all seven tables should disappear.
    _alembic("downgrade", "base")
    remaining = _table_names()
    assert not EXPECTED_TABLES.intersection(remaining), (
        f"tables remained after downgrade: {EXPECTED_TABLES & remaining}"
    )

    # Re-upgrade to head — schema comes back cleanly.
    _alembic("upgrade", "head")
    assert EXPECTED_TABLES.issubset(_table_names())
