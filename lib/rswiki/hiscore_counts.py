#

"""
"""

from collections import defaultdict
from datetime import datetime
from enum import Enum
import logging
from pprint import pprint
import re

from ..config import Config
from ..exception import HiscoresError
from ..mediawiki import Api
from ..hiscores import Hiscores, Skill


__all__ = []


LOGGER = logging.getLogger(__name__)

EN_DATE_FMT = "%d %B %Y"

SKILL_PATTERN = r'{table}\[[\'"]{name}[\'"]\]\s*=\s*[\'"]([\d,]+?)[\'"]'
SKILL_REPLACE = '{table}["{name}"] = "{value:,}"'

UPDATED_PATTERN = r'{table}\[[\'"]{name}[\'"]\]\s*=\s*[\'"]([\w ]+?)[\'"]'
UPDATED_REPLACE = '{table}["{name}"] = "{value}"'


class Table(Enum):
    """The hiscore counts tables."""

    COUNT_99 = "count_99s"
    COUNT_99_IRONMAN = "count_99s_ironman"
    COUNT_120 = "count_120s"
    COUNT_120_IRONMAN = "count_120s_ironman"
    COUNT_200MXP = "count_200mxp"
    COUNT_200MXP_IRONMAN = "count_200mxp_ironman"
    LOWEST_RANKS = "lowest_ranks"

    def __repr__(self) -> str:
        return "{}.{}".format(self.__class__.__name__, self.name)

    @classmethod
    def values(cls) -> list:
        """Get the values of the enum variants."""
        return [x.value for x in cls]

    @property
    def en(self) -> str:
        """Get the English name of the table."""
        return self.value


def get_current_counts(config: Config, page: str) -> str:
    """Get the current counts.

    Used to determine the start point for looking for the current value.
    """
    api = Api(config.username, config.password, config.api_path)

    with api:
        text = api.get_page_content(page)

    ret = defaultdict(dict)
    rgx = re.compile(r'(\w+?)\[[\'"](.+?)[\'"]\]\s*=\s*[\'"]([\d,]+?)[\'"]')

    for line in text.split("\n"):
        if any([line.startswith(x) for x in Table.values()]):
            res = rgx.match(line)

            if res is None:
                continue

            table = Table(res.group(1))
            skill_str = res.group(2)
            value = int(res.group(3).replace(",", ""))
            suffix = None

            if table == Table.LOWEST_RANKS:
                if "." in skill_str:
                    parts = skill_str.split(".", maxsplit=1)
                    skill_str, suffix = parts
                else:
                    suffix = "level"

            try:
                skill = Skill.from_str(skill_str)
            except KeyError:
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
    count_99s = current_counts.get(Table.COUNT_99, {})
    count_99s_ironman = current_counts.get(Table.COUNT_99_IRONMAN, {})
    count_120s = current_counts.get(Table.COUNT_120, {})
    count_120s_ironman = current_counts.get(Table.COUNT_120_IRONMAN, {})
    count_200mxp = current_counts.get(Table.COUNT_200MXP, {})
    count_200mxp_ironman = current_counts.get(Table.COUNT_200MXP_IRONMAN, {})
    lowest_ranks = current_counts.get(Table.LOWEST_RANKS, {})

    for skill in Skill:
        if skill != Skill.OVERALL:
            try:
                count_99s[skill] = hiscores.get_99s(skill, count_99s.get(skill, 1))
            except HiscoresError as exc:
                LOGGER.error("Unable to get 99s count for %s", skill.en)
                LOGGER.exception(exc)

            try:
                count_99s_ironman[skill] = hiscores.get_99s_ironman(
                    skill, count_99s_ironman.get(skill, 1)
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
                    skill, count_120s_ironman.get(skill, 1)
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
        Table.COUNT_99: count_99s,
        Table.COUNT_99_IRONMAN: count_99s_ironman,
        Table.COUNT_120: count_120s,
        Table.COUNT_120_IRONMAN: count_120s_ironman,
        Table.COUNT_200MXP: count_200mxp,
        Table.COUNT_200MXP_IRONMAN: count_200mxp_ironman,
        Table.LOWEST_RANKS: lowest_ranks,
    }


def save_counts(config: Config, page: str, new_counts: dict):
    """
    """
    api = Api(config.username, config.password, config.api_path)

    with api:
        text = api.get_page_content(page)

        for table, counts in new_counts.items():
            updated = counts.pop("updated")

            for skill, value in counts.items():
                if table == Table.LOWEST_RANKS:
                    for key, val in value.items():
                        name = skill.en if key == "level" else skill.en + ".rank"
                        text = replace_count(text, table, name, val, EN_DATE_FMT)
                else:
                    text = replace_count(text, table, skill.en, value, EN_DATE_FMT)

            text = replace_count(text, table, "updated", updated, EN_DATE_FMT)

        LOGGER.info("Updating hiscore counts")
        api.edit_page(page, text, "Updating hiscore counts")


def replace_count(text: str, table: Table, name: str, value: int, date_fmt: str) -> str:
    """
    """
    if name == "updated":
        pattern = UPDATED_PATTERN.format(table=table.en, name=name)
        replace = UPDATED_REPLACE.format(table=table.en, name=name, value=value.strftime(date_fmt))
    else:
        pattern = SKILL_PATTERN.format(table=table.en, name=name)
        replace = SKILL_REPLACE.format(table=table.en, name=name, value=value)

    return re.sub(pattern, replace, text)
