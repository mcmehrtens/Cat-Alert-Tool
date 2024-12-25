"""Get and parse the cats from the tracking URL."""

import logging
import re
import time
from enum import Enum

import bs4
import requests
from bs4 import BeautifulSoup, SoupStrainer

from cat_alert_tool.config import ConfigSchema
from cat_alert_tool.constants import (
    DAYS_PER_MONTH,
    DAYS_PER_WEEK,
    DAYS_PER_YEAR,
)

logger = logging.getLogger(__name__)


class Gender(Enum):
    """Possible cat genders."""

    male = "male"
    female = "female"


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
    id_
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
        gender = "N/A" if self.gender is None else self.gender.name
        return (
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


def parse_name_id_string(name_id_string: str) -> tuple[str, str]:
    """Parse the name/ID string from a cat entry.

    Parameters
    ----------
    name_id_string
        The name/ID string parsed from HTML.

    Returns
    -------
    str
        The cat's name string in lowercase.
    str
        The cat's ID string in uppercase.

    """
    name = ""
    id_ = ""
    match = re.match(r"^(.*)\s\((.*)\)$", name_id_string)
    if match:
        name = match.group(1).lower()
        id_ = match.group(2).upper()
    return name, id_


def parse_gender_string(gender_string: str) -> Gender | None:
    """Parse the gender string from a cat entry.

    Parameters
    ----------
    gender_string
        The gender string parsed from HTML.

    Returns
    -------
    Gender | None
        The cat's gender, if parsable otherwise None.

    """
    try:
        return Gender(gender_string.lower())
    except ValueError:
        return None


def parse_cat_age_string(cat_age_string: str) -> int:
    """Parse the cat age string from a cat entry.

    Parameters
    ----------
    cat_age_string
        The age string parsed from HTML.

    Returns
    -------
    int
        The age of the cat in days. If unparsable, returns 0.

    """
    days_per_year = 365
    days_per_month = 30
    days_per_week = 7
    age = 0
    cat_age_string = cat_age_string.replace("old", "").strip().lower()

    year_pattern = r"(\d+)\s*year(?:s)?"
    month_pattern = r"(\d+)\s*month(?:s)?"
    week_pattern = r"(\d+)\s*week(?:s)?"

    match = re.search(year_pattern, cat_age_string)
    if match:
        age += int(match.group(1)) * days_per_year

    match = re.search(month_pattern, cat_age_string)
    if match:
        age += int(match.group(1)) * days_per_month

    match = re.search(week_pattern, cat_age_string)
    if match:
        age += int(match.group(1)) * days_per_week

    return age


def parse_cat_div(base_url: str, cat_div: bs4.element.Tag) -> Cat:
    """Parse a single cat div.

    Parameters
    ----------
    base_url:
        The base URL for the adoption site.
    cat_div
        The HTML div to parse into the Cat object.

    Returns
    -------
    Cat
        The parsed Cat object.

    """
    cat = Cat()

    a_tag = cat_div.find("a", href=True, on_duplicate_attribute="ignore")
    if a_tag:
        cat.url = base_url + a_tag["href"]

    img_tag = cat_div.find("img", src=True)
    if img_tag:
        cat.image = base_url + img_tag["src"]

    text_fields = cat_div.find_all("div", class_="gridText")
    if text_fields:
        cat.name, cat.id = parse_name_id_string(
            text_fields[1].get_text(strip=True)
        )
        cat.gender = parse_gender_string(text_fields[2].get_text(strip=True))
        cat.color = text_fields[3].get_text(strip=True).lower()
        cat.breed = text_fields[4].get_text(strip=True).lower()
        cat.age = parse_cat_age_string(text_fields[5].get_text(strip=True))

    return cat


def get_cats(config: ConfigSchema) -> list[Cat]:
    """Get all the cats from the tracking URL.

    Parameters
    ----------
    config
        The parsed configuration object.

    Returns
    -------
    list[Cat]
        The Cat objects parsed from the tracking URL.

    """
    logger.info("Beginning the cat fetching routine...")
    cats: list[Cat] = []

    response = None
    attempts = 0
    while attempts < config.requests.fetch_attempts:
        try:
            logger.info("Fetching cats...")
            logger.debug("Fetching from: %s", config.requests.tracking_url)
            response = requests.get(
                config.requests.tracking_url,
                timeout=config.requests.fetch_timeout,
            )
            response.raise_for_status()
            break
        except requests.RequestException:
            logger.exception("HTTP error caught while fetching tracking URL.")
        logger.info(
            "Failed to fetch cats. Sleeping for %f seconds...",
            config.requests.fetch_timeout,
        )
        time.sleep(config.requests.fetch_sleep)
        attempts += 1

    if response is None or attempts == config.requests.fetch_attempts:
        logging.critical("Could not fetch cats from tracking URL.")
        return []

    strainer = SoupStrainer("div", class_="gridResult")
    soup = BeautifulSoup(response.text, "html.parser", parse_only=strainer)
    for div in soup.find_all("div", class_="gridResult"):
        cat = parse_cat_div(config.requests.base_url, div)
        logger.debug("Cat parsed:\n%s\n", cat)
        cats.append(cat)

    logger.info("Found %d cats!", len(cats))
    return cats
