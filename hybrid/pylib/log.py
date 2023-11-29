import logging
import sys
from os.path import basename
from os.path import splitext


def setup_logger(level=logging.INFO):
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def module_name() -> str:
    return splitext(basename(sys.argv[0]))[0]


def started() -> None:
    setup_logger()
    logging.info("=" * 80)
    logging.info("%s started", module_name())


def finished() -> None:
    logging.info("%s finished", module_name())
