#! /usr/bin/env python3

"""
"""

# TODO: add support for overall counts

import argparse
from collections import defaultdict
from datetime import datetime
import logging
import re

from lib.config import Config
from lib.exception import MediaWikiError, HiscoresError
from lib.hiscores import Hiscores, Skill
from lib.mediawiki import Api
from lib.util import setup_logging


LOGGER = logging.getLogger(__name__)

LOG_FILE_FMT = "hiscorecounts-{}.log"
PAGE_NAME = "Module:Hiscore counts"

EN_DATE_FMT = "%d %B %Y"

SKILL_PATTERN = r'{table}\[[\'"]{name}[\'"]\]\s*=\s*[\'"]([\d,]+?)[\'"]'
SKILL_REPLACE = '{table}["{name}"] = "{value:,}"'

UPDATED_PATTERN = r'{table}\[[\'"]{name}[\'"]\]\s*=\s*[\'"]([\w ]+?)[\'"]'
UPDATED_REPLACE = '{table}["{name}"] = "{value}"'


def main():
    """
    Program entry point.
    """
    args = parse_args()
    config = Config.from_toml(args.config)
    setup_logging(args.verbose, config, LOG_FILE_FMT)

    hiscores = Hiscores()
    start = datetime.utcnow()

    try:
        cur_counts = get_current_counts(config)
        new_counts = update_counts(cur_counts, hiscores)

        save_counts(config, new_counts)
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
            hiscores.delay,
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


def get_current_counts(config: Config) -> str:
    """Get the current counts.

    Used to determine the start point for looking for the current value.
    """
    api = Api(config.username, config.password, config.api_path)

    with api:
        text = api.get_page_content(PAGE_NAME)

    keys = [
        "count_99s",
        "count_99s_ironman",
        "count_120s",
        "count_120s_ironman",
        "count_200mxp",
        "count_200mxp_ironman",
        "lowest_ranks",
    ]

    ret = defaultdict(dict)
    rgx = re.compile(r'(\w+?)\[[\'"](.+?)[\'"]\]\s*=\s*[\'"]([\d,]+?)[\'"]')

    for line in text.split("\n"):
        if any([line.startswith(x) for x in keys]):
            res = rgx.match(line)

            if res is None:
                continue

            table = res.group(1)
            skill_str = res.group(2)
            value = int(res.group(3).replace(",", ""))
            suffix = None

            if table == 'lowest_ranks':
                if '.' in skill_str:
                    parts = skill_str.split(".", maxsplit=1)
                    skill_str, suffix = parts
                else:
                    suffix = 'level'

            try:
                skill = Skill.from_str(skill_str)
            except KeyError as exc:
                LOGGER.warning("Failed to convert %s to a skill", skill_str)
                continue

            if suffix is None:
                ret[table][skill] = value
            else:
                if skill not in ret[table]:
                    ret[table][skill] = {}

                ret[table][skill][suffix] = value

    return ret


def update_counts(current_counts: dict, hiscores: Hiscores) -> dict:
    """
    """
    count_99s = current_counts.get("count_99s", {})
    count_99s_ironman = current_counts.get("count_99s_ironman", {})
    count_120s = current_counts.get("count_120s", {})
    count_120s_ironman = current_counts.get("count_120s_ironman", {})
    count_200mxp = current_counts.get("count_200mxp", {})
    count_200mxp_ironman = current_counts.get("count_200mxp_ironman", {})
    lowest_ranks = current_counts.get("lowest_ranks", {})

    for skill in Skill:
        if skill != Skill.OVERALL:
            try:
                count_99s[skill] = hiscores.get_99s(skill, count_99s.get(skill, 1))
            except HiscoresError as exc:
                LOGGER.error("Unable to get 99s count for %s", skill.en)
                LOGGER.exception(exc)

            try:
                count_99s_ironman[skill] = hiscores.get_99s_ironman(
                    skill, count_99s_ironman.get(skill.en, 1)
                )
            except HiscoresError as exc:
                LOGGER.error("Unable to get 99s ironman count for %s", skill.en)
                LOGGER.exception(exc)

            try:
                count_120s[skill] = hiscores.get_120s(skill, count_120s.get(skill, 1))
            except HiscoresError as exc:
                LOGGER.error("Unable to get 120s count for %s", skill.en)
                LOGGER.exception(exc)

            try:
                count_120s_ironman[skill] = hiscores.get_120s_ironman(
                    skill, count_120s_ironman.get(skill.en, 1)
                )
            except HiscoresError as exc:
                LOGGER.error("Unable to get 120s ironman count for %s", skill.en)
                LOGGER.exception(exc)

        try:
            count_200mxp[skill] = hiscores.get_200m_xp(skill, count_200mxp.get(skill, 1))
        except HiscoresError as exc:
            LOGGER.error("Unable to get 200m XP count for %s", skill.en)
            LOGGER.exception(exc)

        try:
            count_200mxp_ironman[skill] = hiscores.get_200m_xp_ironman(
                skill, count_200mxp_ironman.get(skill, 1)
            )
        except HiscoresError as exc:
            LOGGER.error("Unable to get 200m XP ironman count for %s", skill.en)
            LOGGER.exception(exc)

        try:
            lowest = hiscores.get_lowest_rank(skill)
            lowest_ranks[skill] = lowest
        except HiscoresError as exc:
            LOGGER.error("Unable to get lowest rank data for %s", skill.en)
            LOGGER.exception(exc)

    now = datetime.utcnow()

    count_99s["updated"] = now
    count_99s_ironman["updated"] = now
    count_120s["updated"] = now
    count_120s_ironman["updated"] = now
    count_200mxp["updated"] = now
    count_200mxp_ironman["updated"] = now
    lowest_ranks["updated"] = now

    return {
        "count_99s": count_99s,
        "count_99s_ironman": count_99s_ironman,
        "count_120s": count_120s,
        "count_120s_ironman": count_120s_ironman,
        "count_200mxp": count_200mxp,
        "count_200mxp_ironman": count_200mxp_ironman,
        "lowest_ranks": lowest_ranks,
    }


def save_counts(config: Config, new_counts: dict):
    """
    """
    api = Api(config.username, config.password, config.api_path)

    with api:
        text = api.get_page_content(PAGE_NAME)

        for table, counts in new_counts.items():
            for skill, value in counts.items():
                if table == "lowest_ranks":
                    updated = value.pop("updated")

                    for key, val in value.items():
                        name = skill.en if key == "level" else skill.en + ".rank"
                        text = replace_count(text, table, name, val, EN_DATE_FMT)

                    text = replace_count(text, table, "updated", updated, EN_DATE_FMT)
                else:
                    text = replace_count(text, table, skill.en, value, EN_DATE_FMT)

        api.edit_page(PAGE_NAME, text, "Updating hiscore counts")


def replace_count(text: str, table: str, name: str, value: int, date_fmt: str) -> str:
    """
    """
    if name == "updated":
        pattern = UPDATED_PATTERN.format(table=table, name=name)
        replace = UPDATED_REPLACE.format(table=table, name=name, value=value.strftime(date_fmt))
    else:
        pattern = SKILL_PATTERN.format(table=table, name=name)
        replace = SKILL_REPLACE.format(table=table, name=name, value=value)

    text = re.sub(pattern, replace, text)
    return text


if __name__ == "__main__":
    main()
