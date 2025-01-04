"""Constants used throughout the CAT.

Attributes
----------
DAYS_PER_YEAR
    The number of days per year.
DAYS_PER_MONTH
    The numer of days per month.
DAYS_PER_WEEK
    The number of days per week.
"""

from typing import Final

DAYS_PER_YEAR: Final[int] = 365
DAYS_PER_MONTH: Final[int] = 30
DAYS_PER_WEEK: Final[int] = 7
DB_SCHEMA: Final[list[tuple[int, str, str, int, None, int]]] = [
    (0, "id", "INTEGER", 0, None, 1),
    (1, "pet_id", "TEXT", 0, None, 0),
    (2, "name", "TEXT", 0, None, 0),
    (3, "gender", "TEXT", 0, None, 0),
    (4, "color", "TEXT", 0, None, 0),
    (5, "breed", "TEXT", 0, None, 0),
    (6, "age", "INTEGER", 0, None, 0),
    (7, "url", "TEXT", 0, None, 0),
    (8, "image", "TEXT", 0, None, 0),
]
TABLE_NAME: Final[str] = "cats"
