"""Maintain a cat database that persists script executions."""

import logging
import sqlite3
from collections.abc import Collection
from pathlib import Path
from typing import TypedDict

from pubsub import pub

from cat_alert_tool.config import ConfigSchema
from cat_alert_tool.fetch import Cat, Gender

logger = logging.getLogger(__name__)


class CatRow(TypedDict):
    """Helps parse the database rows into Python dictionaries."""

    pet_id: str | None
    name: str | None
    gender: str | None
    color: str | None
    breed: str | None
    age: int | None
    url: str | None
    image: str | None


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
        );
        """)

    def _row_to_cat(self, row: CatRow) -> Cat:
        """Convert a database row to a Cat object.

        Parameters
        ----------
        row
            A single row from the database.

        Returns
        -------
        Cat
            A Cat object matching the attributes from the database.
        """
        cat = Cat()
        cat.url = row.get("url") or ""
        cat.image = row.get("image") or ""
        cat.name = row.get("name") or ""
        cat.id = row.get("id") or ""
        gender = row.get("gender")
        cat.gender = Gender[gender.upper()] if gender is not None else None
        cat.color = row.get("color") or ""
        cat.breed = row.get("breed") or ""
        cat.age = row.get("age") or 0
        return cat

    def get_cat_ids(self) -> set[str]:
        """Get all the cat IDs currently stored in the database.

        Returns
        -------
        set[str]
            All the cat IDs currently stored in the database.
        """
        self._cur.execute("SELECT pet_id FROM cats")
        return set(self._cur.fetchall())

    def get_cats(self, cat_ids: Collection[str]) -> tuple[Cat, ...]:
        """Get cats from the database.

        Parameters
        ----------
        cat_ids
            The cats to get from the database.

        Returns
        -------
        tuple[Cat]
            The cat objects corresponding to cat_ids. The tuple is
            unordered.
        """
        cat_ids_ = set(cat_ids)
        if not cat_ids:
            return ()

        query = "SELECT * FROM cats WHERE pet_id = ?"

        self._cur.execute(query, list(cat_ids_))
        rows = self._cur.fetchall()

        column_names = [desc[0] for desc in self._cur.description]
        cat_rows = [
            CatRow(**dict(zip(column_names, row, strict=True))) for row in rows
        ]

        return tuple(self._row_to_cat(row) for row in cat_rows)

    def process_cats(self, cats: list[Cat]) -> None:
        """Process a batch of cat.

        If a cat being added is not in the database, add it to the
        database and send a notification. If a cat being added is in the
        database, do nothing. If a cat is in the database and not being
        added, remove it from the database and send a notification.

        Parameters
        ----------
        cats
            The cats to be processed.
        """
        cat_ids = {cat.id for cat in cats}
        curr_cat_ids = self.get_cat_ids()

        new_cat_ids = cat_ids - curr_cat_ids
        adopted_cat_ids = curr_cat_ids - cat_ids

        if new_cat_ids:
            new_cats = tuple(cat for cat in cats if cat.id in new_cat_ids)
            pub.sendMessage("cats.new", cats=new_cats)

        if adopted_cat_ids:
            adopted_cats = self.get_cats(adopted_cat_ids)
            pub.sendMessage("cats.adopted", cats=adopted_cats)
