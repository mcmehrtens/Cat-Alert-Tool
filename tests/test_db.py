"""Database tests."""

import sqlite3
from pathlib import Path
from typing import Final

from cat_alert_tool.constants import DB_SCHEMA, TABLE_NAME
from cat_alert_tool.db import CatDB

TEST_DB_NAME: Final[str] = "test.db"


def test_initialize_db_creates_database_if_nonexistent(tmp_path: Path):
    cat_db = CatDB(str(tmp_path), TEST_DB_NAME)
    cat_db.initialize_db()
    del cat_db
    assert (tmp_path / TEST_DB_NAME).exists()


def test_initialize_db_creates_valid_db(tmp_path: Path):
    cat_db = CatDB(str(tmp_path), TEST_DB_NAME)
    cat_db.initialize_db()
    del cat_db

    con = sqlite3.connect(tmp_path / TEST_DB_NAME)
    cur = con.cursor()
    cur.execute(f"PRAGMA table_info('{TABLE_NAME}')")
    schema = cur.fetchall()
    con.close()
    assert schema == DB_SCHEMA


def test_initialize_db_does_not_override_valid_db():
    raise NotImplementedError


def test_initialize_db_overrides_invalid_db():
    raise NotImplementedError
