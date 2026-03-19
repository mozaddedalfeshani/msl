"""MSL — Muradian Skill Languages CLI."""

__version__ = "0.2.1"

LOG_FORMAT = "[%(levelname)s] %(message)s"


def configure_logging(verbosity: int = 0) -> None:
    import logging

    level = logging.WARNING
    if verbosity >= 2:
        level = logging.DEBUG
    elif verbosity == 1:
        level = logging.INFO

    logging.basicConfig(level=level, format=LOG_FORMAT)
