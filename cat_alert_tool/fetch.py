"""Get and parse the cats from the tracking URL."""

import logging
import re
import time
from enum import Enum

import requests
from selectolax.lexbor import LexborHTMLParser, LexborNode

from cat_alert_tool.cat import Cat, Gender
from cat_alert_tool.config import ConfigSchema

logger = logging.getLogger(__name__)


class TextFields(Enum):
    """Ordering of text fields in the animal div."""

    ANIMAL_TYPE = 0
    NAME_ID = 1
    GENDER = 2
    COLOR = 3
    BREED = 4
    AGE = 5
    LOCATION = 6


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


def parse_cat_div(base_url: str, cat_div: LexborNode) -> Cat:
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

    a_node = cat_div.css_first("a")
    if a_node:
        href = a_node.attributes["href"]
        if href:
            cat.url = base_url + href

    img_node = cat_div.css_first("img")
    if img_node:
        src = img_node.attributes["src"]
        if src:
            cat.image = base_url + src

    text_nodes = cat_div.css("div.gridText")
    if text_nodes:
        cat.name, cat.id = parse_name_id_string(
            text_nodes[TextFields.NAME_ID.value].text(strip=True)
        )
        cat.gender = parse_gender_string(
            text_nodes[TextFields.GENDER.value].text(strip=True)
        )
        cat.color = text_nodes[TextFields.COLOR.value].text(strip=True).lower()
        cat.breed = text_nodes[TextFields.BREED.value].text(strip=True).lower()
        cat.age = parse_cat_age_string(
            text_nodes[TextFields.AGE.value].text(strip=True)
        )

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

    selector = "div.gridResult"
    for div in LexborHTMLParser(response.text).css(selector):
        cat = parse_cat_div(config.requests.base_url, div)
        logger.debug("Cat parsed:\n%s\n", cat)
        cats.append(cat)

    logger.info("Found %d cats!", len(cats))
    return cats
