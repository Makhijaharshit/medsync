"""
Test fixtures.

Tests run against the same live PostgreSQL used by the app.
The schema is expected to exist (created by `alembic upgrade head`);
the session-scoped fixture below guarantees that by running the migration
once at session start. Each test uses a per-test transaction that is
rolled back at teardown so tests do not leak state into each other.
"""
import subprocess
import sys
from pathlib import Path

import pytest
from sqlalchemy.orm import Session

from app.core.database import SessionLocal, engine
import app.models  # noqa: F401  ensures all models are registered

BACKEND_DIR = Path(__file__).resolve().parent.parent
ALEMBIC_CMD = [sys.executable, "-m", "alembic"]


@pytest.fixture(scope="session", autouse=True)
def _schema_ready():
    """Ensure the migrated schema is in place before any test runs."""
    subprocess.run(
        [*ALEMBIC_CMD, "upgrade", "head"],
        cwd=BACKEND_DIR,
        check=True,
        capture_output=True,
    )
    yield


@pytest.fixture
def db() -> Session:
    """A session bound to a transaction that is rolled back per test."""
    connection = engine.connect()
    transaction = connection.begin()
    session = SessionLocal(bind=connection)
    try:
        yield session
    finally:
        session.close()
        transaction.rollback()
        connection.close()
