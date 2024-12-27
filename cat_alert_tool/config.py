"""Define the CAT configuration functionality."""

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class Requests(BaseModel):
    """Request configuration schema."""

    base_url: str = Field(description="Base URL of the adoption site.")
    tracking_url: str = Field(description="The URL to query for new cats.")
    fetch_timeout: float = Field(
        description="The number of seconds to wait for a response."
    )
    fetch_attempts: int = Field(
        description="The number of times to attempt to fetch new cats."
    )
    fetch_sleep: float = Field(
        description="The number of seconds to wait after a failed fetch "
        "attempt."
    )


class DB(BaseModel):
    """Database configuration schema."""

    db_dir: str = Field(description="Path to the database directory.")
    db_name: str = Field(description="Database name.")


class ConfigSchema(BaseModel):
    """Top-level configuration schema."""

    requests: Requests
    db: DB


class Config:
    """Encapsulate all the configuration options for the CAT.

    Parameters
    ----------
    file_path
        The path to the YAML configuration file.

    Attributes
    ----------
    file_path

    """

    def __init__(self, file_path: str) -> None:
        self.file_path = Path(file_path)

    def parse(self) -> ConfigSchema:
        """Open, parse, and validate the YAML configuration file.

        Returns
        -------
        ConfigSchema
            Parsed and validated configuration object

        """
        with self.file_path.open() as file:
            raw_data = yaml.safe_load(file)
            return ConfigSchema(**raw_data)
