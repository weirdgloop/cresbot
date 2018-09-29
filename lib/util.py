#

"""
"""

import argparse
from datetime import datetime
import logging
import sys
import os

from .config import Config


__all__ = ['setup_logging']


def setup_logging(args: argparse.Namespace, config: Config, log_file_fmt: str):
    """
    """
    if args.quiet:
        log_level = logging.WARNING
    elif args.verbose:
        log_level = logging.DEBUG
    else:
        log_level = logging.INFO

    log_format = '[%(asctime)s][%(levelname)s][%(name)s] %(message)s'
    date_format = '%H:%M:%S'

    base_logger = logging.getLogger()
    base_logger.setLevel(log_level)

    formatter = logging.Formatter(log_format, datefmt=date_format)

    cur_date = datetime.utcnow()
    log_path = os.path.join(config.log_dir,
                            log_file_fmt.format(cur_date.strftime('%Y-%m-%d_%H-%M-%S')))

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
    urllib_logger = logging.getLogger('urllib3')
    urllib_logger.setLevel(logging.WARNING)
