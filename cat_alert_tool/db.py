"""Maintain a cat database that persists script executions."""

import logging
import sqlite3
from pathlib import Path

from cat_alert_tool.config import ConfigSchema

logger = logging.getLogger(__name__)


class CatDB:
    """Abstract implementation of the persistent cat database.

    Parameters
    ----------
    config
        The parsed configuration object.
    """

    def __init__(self, config: ConfigSchema) -> None:
        self._db_path = Path(config.db.db_dir) / Path(config.db.db_name)
        self._initialize_db()

    def __del__(self) -> None:
        """Close the database when the object is deleted."""
        if self._con:
            self._con.close()

    def _initialize_db(self) -> None:
        """Initialize the cat DB.

        Creates the cat database if it doesn't exist. Otherwise connects
        to an existing database.
        """
        logger.debug("Initializing database...")
        self._con = sqlite3.connect(self._db_path)
        self._cur = self._con.cursor()

        self._cur.execute("""
        CREATE TABLE IF NOT EXISTS cats (
            id INTEGER PRIMARY KEY,
            pet_id TEXT UNIQUE,
            name TEXT,
            gender TEXT,
            color TEXT,
            breed TEXT,
            age INTEGER,
            url TEXT,
            image TEXT,
            updated INTEGER
        );
        """)
