import logging

from tickethub.core.config import LOG_LEVEL


LOG_FORMAT = (
    "%(asctime)s "
    "%(levelname)s "
    "%(name)s "
    "%(message)s"
)


def configure_logging() -> None:
    logging.basicConfig(
        level=LOG_LEVEL,
        format=LOG_FORMAT,
    )

    logging.getLogger("tickethub").setLevel(
        LOG_LEVEL,
    )
