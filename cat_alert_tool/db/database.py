"""Maintain a cat database that persists script executions."""

import logging
from pathlib import Path

from sqlalchemy import URL, create_engine

logger = logging.getLogger(__name__)


class CatDB:
    """Initialize and interface with the cat database.

    Parameters
    ----------
    db_dir
        The root database directory.
    db_name
        The path to the database file relative to the root database
        directory.
    """

    def __init__(self, db_dir: str, db_name: str) -> None:
        self._db_dir = Path(db_dir) / db_name
        self._create_engine()

    def _create_engine(self) -> None:
        """Initialize the SQLAlchemy engine."""
        logger.info("Creating sqlite database engine at %s...", self._db_dir)
        self.engine = create_engine(
            URL.create("sqlite+pysqlite", database=str(self._db_dir))
        )

    def close(self) -> None:
        """Close the DB connection."""
        logger.info("Closing the DB engine...")
        self.engine.dispose()
