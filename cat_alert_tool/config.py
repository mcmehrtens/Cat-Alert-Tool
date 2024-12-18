"""Define the CAT configuration functionality."""

from pathlib import Path

import yaml
from pydantic import BaseModel, Field


class ConfigSchema(BaseModel):
    """Top-level configuration schema."""

    tracking_url: str = Field(description="The URL to query for new cats.")


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
