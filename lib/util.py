#

"""Utilities for the CLI."""

from datetime import datetime
import logging
import sys
import os


__all__ = ["setup_logging"]

LOG_LEVELS = [logging.WARNING, logging.INFO, logging.DEBUG]


def setup_logging(verbose: int, log_dir: str, log_file_fmt: str):
    """Configure logging.

    :param int verbose:
    :param Config config:
    :param str, log_file_fmt:
    """
    log_level = LOG_LEVELS[min(verbose, 2)]

    log_format = "[%(asctime)s][%(levelname)s][%(name)s] %(message)s"
    date_format = "%H:%M:%S"

    base_logger = logging.getLogger()
    base_logger.setLevel(log_level)

    formatter = logging.Formatter(log_format, datefmt=date_format)

    cur_date = datetime.utcnow()
    log_file = log_file_fmt.format(cur_date.strftime("%Y-%m-%d_%H-%M-%S"))
    log_path = os.path.join(log_dir, log_file)

    fh = logging.FileHandler(filename=log_path)

    fh.setLevel(log_level)
    fh.setFormatter(formatter)

    base_logger.addHandler(fh)

    # attach a stream handler if this is being run manually
    if sys.stdout.isatty():
        sh = logging.StreamHandler()

        sh.setLevel(log_level)
        sh.setFormatter(formatter)

        base_logger.addHandler(sh)

    # force urllib to be quiet
    urllib_logger = logging.getLogger("urllib3")
    urllib_logger.setLevel(logging.WARNING)
