# Copyright (C) 2018 Matthew Dowdell <mdowdell244@gmail.com>

"""
"""

from contextlib import contextmanager
from copy import copy
from enum import Enum
import logging
import math
import time
from urllib.parse import urlparse, urlunparse, parse_qsl, urlencode

from bs4 import BeautifulSoup, NavigableString as nstr
import requests

from .proxy_list import ProxyList


URL = "http://services.runescape.com/m=hiscore/ranking"
URL_IRONMAN = "http://services.runescape.com/m=hiscore_ironman/ranking"
HEADERS = {
    "User-Agent": "RuneScape Wiki Hiscores Counts Updater (Maintained by <cqm.fwd@gmail.com>)"
}

LOGGER = logging.getLogger(__name__)


def request_retry(retries: int):
    def retry(func):
        def retry_with_args(*args, **kwargs):
            for i in range(retries):
                try:
                    ret = func(*args, **kwargs)
                    break
                except RuntimeError as exc:
                    LOGGER.warning(exc)
                    LOGGER.warning("Request failed: attempt %s/%s", i + 1, retries)
            else:
                raise RuntimeError("Failed after {} retries".format(retries))

            return ret

        return retry_with_args

    return retry


class Count(Enum):
    """The types of hiscores count that can be retieved."""

    LEVEL_99 = 1
    LEVEL_120 = 2
    EXP_MAX = 3
    LOWEST_RANK = 4


class Exp(Enum):
    """Experience values at given levels."""

    XP_99 = 13034431
    XP_120 = 104273167
    XP_99_ELITE = 36073511
    XP_120_ELITE = 80618654
    XP_MAX = 200000000


class Skill(Enum):
    """The skills in RuneScape 3."""

    OVERALL = 0
    ATTACK = 1
    DEFENCE = 2
    STRENGTH = 3
    CONSTITUTION = 4
    RANGED = 5
    PRAYER = 6
    MAGIC = 7
    COOKING = 8
    WOODCUTTING = 9
    FLETCHING = 10
    FISHING = 11
    FIREMAKING = 12
    CRAFTING = 13
    SMITHING = 14
    MINING = 15
    HERBLORE = 16
    AGILITY = 17
    THIEVING = 18
    SLAYER = 19
    FARMING = 20
    RUNECRAFTING = 21
    HUNTER = 22
    CONSTRUCTION = 23
    SUMMONING = 24
    DUNGEONEERING = 25
    DIVINATION = 26
    INVENTION = 27
    ARCHAEOLOGY = 28

    def __repr__(self) -> str:
        return "{}.{}".format(self.__class__.__name__, self.name)

    @classmethod
    def from_str(cls, value: str):
        """Convert a string to a skill variant."""
        return cls[value.upper()]

    def is_elite(self) -> bool:
        """Get whether the skill is an elite skill or not."""
        return self in [Skill.INVENTION]

    @property
    def xp_99(self) -> int:
        """Get the experience for level 99 in the skill."""
        ret = Exp.XP_99_ELITE if self.is_elite() else Exp.XP_99
        return ret.value

    @property
    def xp_120(self) -> int:
        """Get the experience for level 120 in the skill."""
        ret = Exp.XP_120_ELITE if self.is_elite() else Exp.XP_120
        return ret.value

    @property
    def xp_max(self) -> int:
        """Get the maximum experience of the skill."""
        if self == Skill.OVERALL:
            return sum([x.xp_max for x in Skill if x != Skill.OVERALL])

        return Exp.XP_MAX.value

    @property
    def en(self) -> str:
        """Get the English name of the skill."""
        return self.name.lower()  # pylint: disable=no-member

    @property
    def pt_br(self) -> str:
        """Get the Brazilian Portuguese name of the skill."""
        return {
            Skill.OVERALL: "total",
            Skill.ATTACK: "ataque",
            Skill.DEFENCE: "defesa",
            Skill.STRENGTH: "força",
            Skill.CONSTITUTION: "condição física",
            Skill.RANGED: "combate à distância",
            Skill.PRAYER: "oração",
            Skill.MAGIC: "magia",
            Skill.COOKING: "culinária",
            Skill.WOODCUTTING: "corte de lenha",
            Skill.FLETCHING: "arco e fcleha",
            Skill.FISHING: "pesca",
            Skill.FIREMAKING: "arte do fogo",
            Skill.CRAFTING: "artesanato",
            Skill.SMITHING: "metalurgia",
            Skill.MINING: "mineração",
            Skill.HERBLORE: "herbologia",
            Skill.AGILITY: "agilidade",
            Skill.THIEVING: "roubo",
            Skill.SLAYER: "extermínio",
            Skill.FARMING: "agricultura",
            Skill.RUNECRAFTING: "criação de runas",
            Skill.HUNTER: "caça",
            Skill.CONSTRUCTION: "construção",
            Skill.SUMMONING: "evocação",
            Skill.DUNGEONEERING: "dungeon",
            Skill.DIVINATION: "divinação",
            Skill.INVENTION: "invenção",
            Skill.ARCHAEOLOGY: "arqueologia",
        }[self]


class Hiscores:
    """
    """

    def __init__(self, proxy_list: ProxyList):
        """
        """
        self.proxy_list = proxy_list
        self.proxy_list_iter = iter(proxy_list) if proxy_list else None

        self._url = None
        self._total_requests = 0
        self._error_requests = 0
        self._default_params = {"category_type": 0, "table": 0, "page": 0}

    @contextmanager
    def set_url(self, url: str):
        """Set the ``url`` attribute within a context.

        :param str url: The URL to use.
        """
        self._url = url
        yield
        self._url = None

    @property
    def total_requests(self) -> int:
        """Get the total number of requests."""
        return self._total_requests

    @property
    def error_requests(self) -> int:
        """Get the number of requests that resulted in an error."""
        return self._error_requests

    @request_retry(retries=10)
    def _get(self, params: dict) -> BeautifulSoup:
        """

        :param **params:
        """
        if self.proxy_list_iter is not None:
            proxy = next(self.proxy_list_iter)
        else:
            proxy = None

        url_parts = list(urlparse(self._url))
        query = dict(parse_qsl(url_parts[4]))
        query.update(params)

        url_parts[4] = urlencode(query)
        url = urlunparse(url_parts)

        start = time.perf_counter()
        if proxy is not None:
            res = requests.get(proxy, params={"url": url}, headers=HEADERS)
        else:
            res = requests.get(url, headers=HEADERS)

        end = time.perf_counter()

        LOGGER.debug("Request: %s %s in %.2f seconds", res.status_code, url, end - start)
        self._total_requests += 1

        if res.status_code != 200:
            raise RuntimeError("Request failed with proxy: {}".format(proxy))

        soup = BeautifulSoup(res.text, "html.parser")
        errors = soup.select("#errorContent")

        # handle ratelimit
        if errors:
            self.proxy_list_iter.delay += 1
            self._error_requests += 1

            LOGGER.warning("Request error: %s (proxy: %s)", url, proxy)
            return self._get(params)

        # handle weird sign in page from proxy
        rows = soup.select("div.tableWrap tbody tr")

        if not rows:
            self.proxy_list_iter.delay += 1
            self._error_requests += 1

            LOGGER.warning("Missing hiscores table in response: %s (proxy: %s)", url, proxy)
            return self._get(params)

        return soup

    def _find_value(
        self,
        params: dict,
        column: int,
        value: int,
        _step: int = 1,
        _checked: list = None,
        _up: bool = None,
        _found: bool = False,
        _reqs: int = 0,
    ) -> int:
        """

        :param dict params:
        :param int column:
        :param int value:
        :param int _step:

        :return:
        """
        if _checked is None:
            _checked = []

        soup = self._get(params)
        rows = (x for x in soup.select("div.tableWrap tbody tr") if not isinstance(x, nstr))
        trs = []

        for row in rows:
            cells = (x for x in row.contents if not isinstance(x, nstr))
            trs.append(tuple(cells))

        # check if the last value on the page is `value`
        # if so jump forwards
        try:
            last_val = trs[-1][column].a.string.strip().replace(",", "")
        except IndexError as exc:
            LOGGER.error(soup)
            raise exc

        if int(last_val) >= value:
            if not _checked:
                _up = True
            # only increase the step after first request
            else:
                if _up is False and not _found:
                    _found = True

                if _up and not _found:
                    _step *= 2
                else:
                    _step /= 2

            # check if the next page has already been visited
            # to stop an infinite loop
            if params.get("page") + 1 in _checked:
                rank = trs[-1][0].a.string.strip()
                return int(rank.replace(",", ""))

            # track which pages have already been visited
            _checked.append(params.get("page"))
            params["page"] += int(_step)
            return self._find_value(params, column, value, _step, _checked, _up, _found)

        # check if the first value if less than `value`
        # if so jump backwards
        first_val = trs[0][column].a.string.strip().replace(",", "")

        if int(first_val) < value:
            # check we're not on the first page (no players have `value`)
            if params.get("page") == 1:
                LOGGER.debug("Found after checking %s page(s)", len(_checked) + 1)
                return 0

            if not _checked:
                _up = False
            # only increase the step after first request
            else:
                if _up is True and not _found:
                    _found = True

                if not _up and not _found:
                    _step *= 2
                else:
                    _step /= 2

            # check if the previous page has already been visited
            # to stop an infinite loop
            if params["page"] - 1 in _checked:
                rank = trs[0][0].a.string.strip()
                LOGGER.debug("Found after checking %s page(s)", len(_checked) + 1)
                return int(rank.replace(",", ""))

            # track which pages have already been visited
            _checked.append(params.get("page"))
            params["page"] -= int(_step)

            # don't let the page drop below 1
            if params["page"] < 1:
                raise RuntimeError("Page number dropped below 1.")

            return self._find_value(params, column, value, _step, _checked, _up, _found)

        # we should be on the correct page, so check every value
        # until one is found that matches `value`
        data = []

        for tds in trs:
            rank = tds[0].a.string.strip()
            val = tds[column].a.string.strip().replace(",", "")

            if int(val) >= value:
                data.append(rank)
            else:
                break

        LOGGER.info("Found after checking %s pages", len(_checked) + 1)
        return int(data[-1].replace(",", ""))

    def get_99s(self, skill: Skill, last: int = 0) -> int:
        """Get the number of players with level 99 in a skill.

        :param Skill skill: The skill to get data for.
        :param int last: The last known number of players with level 99 in the skill.

        :return: The number of players with 99 in the requested skill.
        :rtype: int
        """
        # 25 ranks per page
        start_page = max(1, math.ceil(last / 25))
        LOGGER.debug("Start page for %s 99s count: %s (rank: %s)", skill.en, start_page, last)

        params = copy(self._default_params)
        params.update({"table": skill.value, "page": start_page})

        with self.set_url(URL):
            ret = self._find_value(params, 3, skill.xp_99)
            LOGGER.info("%s 99s count: %s", skill.en.capitalize(), ret)

        return ret

    def get_99s_ironman(self, skill: Skill, last: int = 0) -> int:
        """Get the number of ironman players with level 99 in a skill.

        :param Skill skill: The skill to get data for.
        :param int last: The last known number of players with level 99 in the skill.

        :return: The number of players with 99 in the requested skill.
        :rtype: int
        """
        # 25 ranks per page
        start_page = max(1, math.ceil(last / 25))
        LOGGER.debug(
            "Start page for %s 99s ironman count: %s (rank: %s)", skill.en, start_page, last,
        )

        params = copy(self._default_params)
        params.update({"table": skill.value, "page": start_page})

        with self.set_url(URL_IRONMAN):
            ret = self._find_value(params, 3, skill.xp_99)
            LOGGER.info("%s 99s ironman count: %s", skill.en.capitalize(), ret)

        return ret

    def get_120s(self, skill: Skill, last: int = 0) -> int:
        """
        """
        # 25 ranks per page
        start_page = max(1, math.ceil(last / 25))
        LOGGER.debug("Start page for %s 120s count: %s (rank: %s)", skill.en, start_page, last)

        params = copy(self._default_params)
        params.update({"table": skill.value, "page": start_page})

        with self.set_url(URL):
            ret = self._find_value(params, 3, skill.xp_120)
            LOGGER.info("%s 120s count: %s", skill.en.capitalize().capitalize(), ret)

        return ret

    def get_120s_ironman(self, skill: Skill, last: int = 0) -> int:
        """Get the number of players with level 120 in a skill.

        :param Skill skill: The skill to get data for.
        :param int last: The last known number of players with level 120 in the skill.

        :return: The number of players with 120 in the requested skill.
        :rtype: int
        """
        # 25 ranks per page
        start_page = max(1, math.ceil(last / 25))
        LOGGER.debug(
            "Start page for %s 120s ironman count: %s (rank: %s)", skill.en, start_page, last,
        )

        params = copy(self._default_params)
        params.update({"table": skill.value, "page": start_page})

        with self.set_url(URL_IRONMAN):
            ret = self._find_value(params, 3, skill.xp_120)
            LOGGER.info("%s 120s ironman count: %s", skill.en.capitalize(), ret)

        return ret

    def get_200m_xp(self, skill: Skill, last: int = 0) -> int:
        """
        """
        # 25 ranks per page
        start_page = max(1, math.ceil(last / 25))
        LOGGER.debug(
            "Start page for %s 200m XP count: %s (rank: %s)", skill.en, start_page, last,
        )

        params = copy(self._default_params)
        params.update({"table": skill.value, "page": start_page})

        with self.set_url(URL):
            ret = self._find_value(params, 3, skill.xp_max)
            LOGGER.info("%s 200m XP count: %s", skill.en.capitalize(), ret)

        return ret

    def get_200m_xp_ironman(self, skill: Skill, last: int = 0) -> int:
        """
        """
        # 25 ranks per page
        start_page = max(1, math.ceil(last / 25))
        LOGGER.debug(
            "Start page for %s 200m ironman XP count: %s (rank: %s)", skill.en, start_page, last,
        )

        params = copy(self._default_params)
        params.update({"table": skill.value, "page": start_page})

        with self.set_url(URL_IRONMAN):
            ret = self._find_value(params, 3, skill.xp_max)
            LOGGER.info("%s 200m XP ironman count: %s", skill.en.capitalize(), ret)

        return ret

    def get_lowest_rank(self, skill: Skill) -> dict:
        """

        :param Skill skill:

        :return:
        :rtype: dict
        """
        with self.set_url(URL):
            # load the first page and look for a link to the last page
            params = copy(self._default_params)
            params.update({"table": skill.value, "page": 1})
            soup = self._get(params)
            # should be 7 keys here
            page = soup.select(".pageNumbers li a")[-1].string

            # load the page and get the last row of the hiscores table
            params.update({"page": page})
            soup = self._get(params)

            try:
                cells = tuple(
                    x
                    for x in soup.select("div.tableWrap tbody tr")[-1].contents
                    if not isinstance(x, nstr)
                )
            except IndexError as exc:
                LOGGER.error(soup)
                raise exc

            rank = int(cells[0].a.string.strip().replace(",", ""))
            level = int(cells[2].a.string.strip().replace(",", ""))

        LOGGER.info("%s lowest rank: %s, level: %s", skill.en.capitalize(), rank, level)

        return {
            "rank": rank,
            "level": level,
        }
