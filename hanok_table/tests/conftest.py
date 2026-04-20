"""Shared fixtures (sqlite in-memory for seating tests)."""

from __future__ import annotations

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from hanok_table.db import Base

# Register models on metadata before create_all
import hanok_table.models  # noqa: F401


@pytest.fixture
def db_session() -> Session:
    engine = create_engine("sqlite:///:memory:", future=True)
    Base.metadata.create_all(engine)
    SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False, future=True)
    s = SessionLocal()
    try:
        yield s
    finally:
        s.close()
