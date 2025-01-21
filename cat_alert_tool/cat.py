"""The cat object."""

from enum import Enum

from cat_alert_tool.constants import (
    DAYS_PER_MONTH,
    DAYS_PER_WEEK,
    DAYS_PER_YEAR,
)


class Gender(Enum):
    """Possible cat genders."""

    MALE = "male"
    FEMALE = "female"


class Cat:
    """Represents the data associated with one cat.

    Attributes
    ----------
    url
        A link to the details page of the cat.
    image
        A link to a picture of the cat.
    name
        The name of the cat.
    id
        The ID of the cat.
    gender
        The gender of the cat.
    color
        The color of the cat.
    breed
        The breed of the cat.
    age
        The age of the cat in days.

    """

    def __init__(self) -> None:
        self.url: str = ""
        self.image: str = ""
        self.name: str = ""
        self.id: str = ""
        self.gender: Gender | None = None
        self.color: str = ""
        self.breed: str = ""
        self.age: int = 0

    def __str__(self) -> str:
        """Return a string representation of the cat.

        Returns
        -------
        str
            String representation of the cat.

        """
        gender = "N/A" if self.gender is None else self.gender.name.lower()
        return (
            f"id: {self.id.upper()}\n"
            f"name: {self.name}\n"
            f"gender: {gender}\n"
            f"color: {self.color}\n"
            f"breed: {self.breed}\n"
            f"age: {self.get_human_readable_age()}\n"
            f"url: {self.url}\n"
            f"image: {self.image}"
        )

    def get_human_readable_age(self) -> str:
        """Return the age as a human-readable string.

        Returns
        -------
        str
            A human-readable age string.

        """
        days = self.age

        years = days // DAYS_PER_YEAR
        days %= DAYS_PER_YEAR

        months = days // DAYS_PER_MONTH
        days %= DAYS_PER_MONTH

        weeks = days // DAYS_PER_WEEK
        days %= DAYS_PER_WEEK

        parts: list[str] = []
        if years > 0:
            parts.append(f"{years} year{'s' if years != 1 else ''}")
        if months > 0:
            parts.append(f"{months} month{'s' if months != 1 else ''}")
        if weeks > 0:
            parts.append(f"{weeks} week{'s' if weeks != 1 else ''}")
        if days > 0:
            parts.append(f"{days} day{'s' if days != 1 else ''}")

        return ", ".join(parts) if len(parts) > 0 else ""
