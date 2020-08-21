#! /usr/bin/env python3

"""A task for updating the hiscore counts module on the RuneScape Wiki."""

import argparse
from datetime import datetime
import logging
import os
import time

from lib.config import Config
from lib.util import setup_logging
from lib.hiscores import Hiscores
from lib.proxy_list import ProxyList
from lib.rswiki.hiscore_counts import (
    get_current_counts,
    update_counts,
    store_counts,
    save_counts,
    Language,
)


LOGGER = logging.getLogger(__name__)

LOG_FILE_FMT = "hiscorecounts-{}.log"
COUNTS_FILE_FMT = "hiscorecounts-{}.json"


def main():
    """Program entry point."""
    args = parse_args()
    config = Config.from_toml(args.config)
    setup_logging(args.verbose, config.log_dir, LOG_FILE_FMT)

    proxy_list = ProxyList(config.proxies, 12)
    hiscores = Hiscores(proxy_list)
    start = time.perf_counter()
    start_datetime = datetime.utcnow()

    try:
        cur_counts = get_current_counts(config.wiki.en, Language.EN)
        new_counts = update_counts(cur_counts, hiscores)

        counts_path = os.path.join(
            config.log_dir, COUNTS_FILE_FMT.format(start_datetime.strftime("%Y-%m-%d_%H-%M-%S"))
        )
        store_counts(counts_path, new_counts)

        save_counts(config.wiki.en, Language.EN, new_counts)
        save_counts(config.wiki.pt_br, Language.PT_BR, new_counts)
    except Exception as exc:
        LOGGER.exception(exc)
    else:
        LOGGER.info("Hiscore counts completed successfully")
    finally:
        end = time.perf_counter()
        diff = end - start
        # TODO: write this to separate file
        LOGGER.info(
            "STATS: hiscores requests: %s, hiscore errors: %s, end_delay: %s, total_time: %.2f",
            hiscores.total_requests,
            hiscores.error_requests,
            hiscores.proxy_list.delay,
            diff,
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
