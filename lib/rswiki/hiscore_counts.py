#

"""Utilities for working with hiscore counts modules.
"""

from collections import defaultdict
from contextlib import contextmanager
from copy import deepcopy
from datetime import datetime
from enum import Enum
import json
import locale
import logging
import re

from ..config import WikiConfig
from ..exception import HiscoresError
from ..mediawiki import Api
from ..hiscores import Hiscores, Skill


__all__ = []


LOGGER = logging.getLogger(__name__)

SKILL_PATTERN = r'{table}\[[\'"]{name}[\'"]\]\s*=\s*[\'"]([\d\.,]+?)[\'"]'
SKILL_REPLACE = '{table}["{name}"] = "{value}"'

UPDATED_PATTERN = r'{table}\[[\'"]{name}[\'"]\]\s*=\s*[\'"]([\w ]+?)[\'"]'
UPDATED_REPLACE = '{table}["{name}"] = "{value}"'


class Language(Enum):
    """The possible languages for the module."""

    EN = "en"
    PT_BR = "pt-br"

    @property
    def key(self) -> str:
        """Get the language in a format usable for python attribute lookups."""
        return self.value.replace("-", "_")  # pylint: disable=no-member

    @property
    def module(self) -> str:
        """Get the name of the module for the language."""
        return {
            Language.EN: "Module:Hiscore counts",
            Language.PT_BR: "Módulo:Contagem de Recordes",
        }[self]

    @property
    def updated(self) -> str:
        """Get the translation for 'updated'."""
        return {Language.EN: "updated", Language.PT_BR: "data",}[self]

    @property
    def level(self) -> str:
        """Get the translation for 'level'."""
        return {Language.EN: "level", Language.PT_BR: "nível",}[self]

    @property
    def rank(self) -> str:
        """Get the translation for 'rank'."""
        return {Language.EN: "rank", Language.PT_BR: "rank",}[self]

    @property
    def date_fmt(self) -> str:
        """Get the date format for the language."""
        return {Language.EN: "%d %B %Y", Language.PT_BR: "%d de %B de %Y",}[self]

    @property
    def edit_summary(self):
        """Get the edit summary for the language."""
        return {
            Language.EN: "Updating hiscore counts",
            Language.PT_BR: "Atualizando a contagem de recordes",
        }[self]

    @contextmanager
    def locale(self):
        """Set the time locale for the language within a context."""
        locale_string = {Language.EN: "en_US.utf8", Language.PT_BR: "pt_BR.utf8"}[self]
        prev_locale = locale.getlocale()

        locale.setlocale(locale.LC_ALL, locale_string)
        yield
        locale.setlocale(locale.LC_ALL, prev_locale)


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

    @property
    def pt_br(self) -> str:
        """Get the Brazilian name of the table."""
        return {
            Table.COUNT_99: "contagem_99s",
            Table.COUNT_99_IRONMAN: "contagem_99s_independente",
            Table.COUNT_120: "contagem_120s",
            Table.COUNT_120_IRONMAN: "contagem_120s_independente",
            Table.COUNT_200MXP: "contagem_200mxp",
            Table.COUNT_200MXP_IRONMAN: "contagem_200mxp_independente",
            Table.LOWEST_RANKS: "nivel_minimo",
        }[self]


def get_current_counts(config: WikiConfig, lang: Language) -> str:
    """Get the current counts.

    Used to determine the start point for looking for the current value.
    """
    api = Api(config.username, config.password, config.api_path)

    with api:
        text = api.get_page_content(lang.module)

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
    """Get the latest data from the RuneScape hiscores pages.

    :param dict current_counts: The data to update.
    :param Hiscores hiscores: The hiscores object to get the data with.

    :return: The updated data.
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

    count_99s[Language.EN.updated] = now
    count_99s_ironman[Language.EN.updated] = now
    count_120s[Language.EN.updated] = now
    count_120s_ironman[Language.EN.updated] = now
    count_200mxp[Language.EN.updated] = now
    count_200mxp_ironman[Language.EN.updated] = now
    lowest_ranks[Language.EN.updated] = now

    return {
        Table.COUNT_99: count_99s,
        Table.COUNT_99_IRONMAN: count_99s_ironman,
        Table.COUNT_120: count_120s,
        Table.COUNT_120_IRONMAN: count_120s_ironman,
        Table.COUNT_200MXP: count_200mxp,
        Table.COUNT_200MXP_IRONMAN: count_200mxp_ironman,
        Table.LOWEST_RANKS: lowest_ranks,
    }


def store_counts(filepath: str, new_counts: dict):
    """Store the collected counts as a JSON file.

    :param str filepath: The file to store the data in.
    :param dict new_counts: The data to store.
    """
    data = {}

    for table, counts in new_counts.items():
        data[table.en] = {}

        for skill, value in counts.items():
            if isinstance(skill, Skill):
                data[table.en][skill.en] = value
            else:
                if isinstance(value, datetime):
                    value = value.strftime(Language.EN.date_fmt)

                data[table.en][skill] = value

    content = json.dumps(data, indent=2, sort_keys=True)

    with open(filepath, "wt") as fh:
        fh.write(content + "\n")


def save_counts(config: WikiConfig, lang: Language, new_counts: dict):
    """Save the collected data as a module on a wiki.

    :param WikiConfig config: The configuration for the wiki.
    :param Language lang: The language for the wiki.
    :param dict new_counts: The data to save.
    """
    api = Api(config.username, config.password, config.api_path)

    with api:
        text = api.get_page_content(lang.module)

        with lang.locale():
            for table, counts in new_counts.items():
                _counts = deepcopy(counts)
                table_local = getattr(table, lang.key)
                updated = _counts.pop(Language.EN.updated)

                for skill, value in _counts.items():
                    skill_local = getattr(skill, lang.key)

                    if table == Table.LOWEST_RANKS:
                        for key, val in value.items():
                            if key == Language.EN.level:
                                name = skill_local
                            else:
                                name = skill_local + ".{}".format(lang.rank)

                            text = replace_count(text, table_local, name, val)
                    else:
                        text = replace_count(text, table_local, skill_local, value)

                text = replace_count(
                    text, table_local, lang.updated, updated.strftime(lang.date_fmt)
                )

        LOGGER.info("Updating hiscore counts for API: %s", api.api_path)
        api.edit_page(lang.module, text, lang.edit_summary, bot=True)


def replace_count(text: str, table: str, name: str, value: int) -> str:
    """Replace a count within the given table.

    :param str text: The text to update.
    :param str table: The name of the table to update.
    :param str name: The name of the key in the table to update.
    :param int value: The value to update with.

    :return: The updated text.
    """
    if name in [lang.updated for lang in Language]:
        pattern = UPDATED_PATTERN.format(table=table, name=name)
        replace = UPDATED_REPLACE.format(table=table, name=name, value=value)
    else:
        pattern = SKILL_PATTERN.format(table=table, name=name)
        replace = SKILL_REPLACE.format(table=table, name=name, value=f"{value:n}")

    return re.sub(pattern, replace, text)
