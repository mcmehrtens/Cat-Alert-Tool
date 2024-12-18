"""Entrypoint for the Cat Alert Tool (CAT)."""

import argparse
import logging

import yaml

from cat_alert_tool.config import Config

cat_str = (
    "  /$$$$$$   /$$$$$$  /$$$$$$$$\n"
    " /$$__  $$ /$$__  $$|__  $$__/\n"
    "| $$  \\__/| $$  \\ $$   | $$   \n"
    "| $$      | $$$$$$$$   | $$   \n"
    "| $$      | $$__  $$   | $$   \n"
    "| $$    $$| $$  | $$   | $$   \n"
    "|  $$$$$$/| $$  | $$   | $$   \n"
    " \\______/ |__/  |__/   |__/   "
)


def parse_arguments() -> argparse.Namespace:
    """Parse command line arguments.

    Returns
    -------
    Namespace
        The parsed arguments.

    """
    parser = argparse.ArgumentParser(
        description=(
            "A Python-based web scraper that notifies the user when a new cat "
            "has been added to the Ames, IA animal shelter."
        ),
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument("config", help="relative path to the config file")
    parser.add_argument(
        "-v",
        "--verbose",
        action="store_true",
        help="increase logging verbosity",
    )

    return parser.parse_args()


def configure_logging(*, verbose: bool) -> logging.Logger:
    """Configure the logging module.

    Parameters
    ----------
    verbose
        If true, sets the logging level to DEBUG, otherwise, the logging
        level will be set to INFO.

    Returns
    -------
    Logger
        This modules logger.

    """
    verbosity = logging.DEBUG if verbose else logging.INFO

    console_handler = logging.StreamHandler()
    console_handler.setLevel(verbosity)

    formatter = logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )
    formatter.default_msec_format = "%s.%03d"

    console_handler.setFormatter(formatter)

    root_logger = logging.getLogger()
    root_logger.setLevel(verbosity)
    root_logger.addHandler(console_handler)

    return logging.getLogger(__name__)


def main() -> None:
    """Entrypoint for the Cat Alert Tool (CAT)."""
    args = parse_arguments()
    config = Config(args.config).parse()
    logger = configure_logging(verbose=args.verbose)
    logger.info("\n%s", cat_str)
    logger.info("Starting the Cat Alert Tool...")
    logger.debug(
        "Configuration:\n%s",
        yaml.dump(
            config.model_dump(warnings="error"), default_flow_style=False
        ),
    )


if __name__ == "__main__":
    main()
