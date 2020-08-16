#! /usr/bin/env python3

"""A task for updating the hiscore counts module on the RuneScape Wiki."""

import argparse
from datetime import datetime
import logging

from lib.config import Config
from lib.util import setup_logging
from lib.hiscores import Hiscores
from lib.proxy_list import ProxyList
from lib.rswiki.hiscore_counts import get_current_counts, update_counts, save_counts


LOGGER = logging.getLogger(__name__)

LOG_FILE_FMT = "hiscorecounts-{}.log"
PAGE_NAME = "Module:Hiscore counts"

PROXY_URL_FMT = "https://us-central1-runescape-wiki.cloudfunctions.net/exchange{}"


def main():
    """Program entry point."""
    args = parse_args()
    config = Config.from_toml(args.config)
    setup_logging(args.verbose, config, LOG_FILE_FMT)

    proxy_list = ProxyList([PROXY_URL_FMT.format(i) for i in range(1, 73)], 12)
    hiscores = Hiscores(proxy_list)
    start = datetime.utcnow()

    try:
        cur_counts = get_current_counts(config, PAGE_NAME)
        new_counts = update_counts(cur_counts, hiscores)

        save_counts(config, PAGE_NAME, new_counts)
    except Exception as exc:
        LOGGER.exception(exc)
    else:
        LOGGER.info("Hiscore counts completed successfully")
    finally:
        end = datetime.utcnow()
        # TODO: write this to separate file
        LOGGER.info(
            "STATS: hiscores requests: %s, hiscore errors: %s, end_delay: %s, total_time: %s",
            hiscores.total_requests,
            hiscores.error_requests,
            hiscores.proxy_list.delay,
            str(end - start),
        )
        # TODO: update stats
        # TODO: keep track of errors found while getting new counts


def parse_args() -> argparse.Namespace:
    """
    Handle command line arguments.

    :return: The found arguments.
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("config", help="the configuration file for the task")
    parser.add_argument("-v", "--verbose", action="count", default=0, help="increase log verbosity")

    return parser.parse_args()


if __name__ == "__main__":
    main()
