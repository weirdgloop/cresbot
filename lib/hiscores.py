# Copyright (C) 2018 Matthew Dowdell <mdowdell244@gmail.com>

"""
"""

from contextlib import contextmanager
from copy import copy
import enum
import logging
import math
from time import sleep, time

from bs4 import BeautifulSoup, NavigableString as nstr
import requests


URL = 'http://services.runescape.com/m=hiscore/ranking'
URL_IRONMAN = 'http://services.runescape.com/m=hiscore_ironman/ranking'
HEADERS = {'User-Agent': 'RuneScape Wiki Hiscores Counts Updater (Maintained by <cqm.fwd@gmail.com>)'}

LOGGER = logging.getLogger(__name__)


class Count(enum.Enum):
    LEVEL_99 = 1
    LEVEL_120 = 2
    EXP_MAX = 3
    LOWEST_RANK = 4


class Exp(enum.Enum):
    XP_99 = 13034431
    XP_120 = 104273167
    XP_99_ELITE = 36073511
    XP_120_ELITE = 80618654
    XP_MAX = 200000000


class Skill(enum.Enum):
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

    def is_elite(self) -> bool:
        """
        """
        return self in [Skill.INVENTION]

    @property
    def xp_99(self) -> int:
        """
        """
        ret = Exp.XP_99_ELITE if self.is_elite() else Exp.XP_99
        return ret.value

    @property
    def xp_120(self) -> int:
        """
        """
        ret = Exp.XP_120_ELITE if self.is_elite() else Exp.XP_120
        return ret.value

    @property
    def xp_max(self) -> int:
        """
        """
        return Exp.XP_MAX.value


class Hiscores:
    """
    """

    def __init__(self, delay: int = 12):
        """
        """
        self._last = None
        self._url = None
        self._total_requests = 0
        self._error_requests = 0
        self._delay = delay
        self._default_params = {'category_type': 0, 'table': 0, 'page': 0}

    @contextmanager
    def set_url(self, url: str):
        self._url = url
        yield
        self._url = None

    @property
    def delay(self) -> int:
        """
        """
        return self._delay

    @property
    def total_requests(self) -> int:
        """
        """
        return self._total_requests

    @property
    def error_requests(self):
        return self._error_requests

    def __get(self, params: dict) -> BeautifulSoup:
        """

        :param **params:
        """
        if self._last is not None:
            while time() < (self._last + self.delay):
                sleep(1)

        res = requests.get(self._url, params=params, headers=HEADERS)

        self._total_requests += 1
        self._last = time()

        soup = BeautifulSoup(res.text, 'html.parser')
        errors = soup.select('#errorContent')

        # handle ratelimit
        if len(errors):
            self._delay += 1
            self._error_requests += 1

            LOGGER.warning('Request error: %s', res.url)
            LOGGER.warning('Assuming ratelimit, sleeping for 30 seconds and incrementing delay between requests to %s',           self._delay)
            sleep(30)

            return self.__get(params)

        LOGGER.debug('Request success: %s', res.url)

        return soup

    def __find_value(
        self,
        params: dict,
        column: int,
        value: int,
        _step: int = 1,
        _checked: list = None,
        _up: bool = None,
        _found: bool = False,
        _reqs: int = 0
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

        soup = self.__get(params)
        rows = (x for x in soup.select('div.tableWrap tbody tr') \
                if not isinstance(x, nstr))
        trs = []

        for tr in rows:
            tds = (x for x in tr.contents if not isinstance(x, nstr))
            trs.append(tuple(tds))

        # check if the last value on the page is `value`
        # if so jump forwards
        last_val = trs[-1][column].a.string.strip().replace(',', '')

        if int(last_val) >= value:
            if not len(_checked):
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
            if (params.get('page') + 1) in _checked:
                rank = trs[-1][0].a.string.strip()
                return int(rank.replace(',', ''))

            # track which pages have already been visited
            _checked.append(params.get('page'))
            params['page'] += int(_step)
            return self.__find_value(params, column, value, _step, _checked, _up, _found)

        # check if the first value if less than `value`
        # if so jump backwards
        first_val = trs[0][column].a.string.strip().replace(',', '')

        if int(first_val) < value:
            # check we're not on the first page (no players have `value`)
            if params.get('page') == 1:
                LOGGER.info('Found after checking %s pages', len(_checked))
                return 0

            if not len(_checked):
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
            if (params['page'] - 1) in _checked:
                rank = trs[0][0].a.string.strip()
                LOGGER.info('Found after checking %s pages', len(_checked))
                return int(rank.replace(',', ''))

            # track which pages have already been visited
            _checked.append(params.get('page'))
            params['page'] -= int(_step)

            # don't let the page drop below 1
            if params['page'] < 1:
                raise Exception('Page number dropped below 1.')

            return self.__find_value(params, column, value, _step, _checked, _up, _found)

        # we should be on the correct page, so check every value
        # until one is found that matches `value`
        data = []

        for tds in trs:
            rank = tds[0].a.string.strip()
            val = tds[column].a.string.strip().replace(',', '')

            if int(val) >= value:
                data.append(rank)
            else:
                break

        LOGGER.info('Found after checking %s pages', len(_checked))
        return int(data[-1].replace(',', ''))

    def get_99s(self, skill: Skill, last: int = 0) -> int:
        """
        """
        # 25 ranks per page
        start_page = max(1, math.ceil(last / 25))
        LOGGER.debug('Start page for %s 99s count: %s (rank: %s)',
                     skill.name.capitalize(), start_page, last)

        params = copy(self._default_params)
        params.update({'table': skill.value, 'page': start_page})

        with self.set_url(URL):
            ret = self.__find_value(params, 3, skill.xp_99)
            LOGGER.info('%s 99s count: %s', skill.name.capitalize(), ret)

        return ret


    def get_99s_ironman(self, skill: Skill, last: int = 0) -> int:
        """
        """
        # 25 ranks per page
        start_page = max(1, math.ceil(last / 25))
        LOGGER.debug('Start page for %s 99s ironman count: %s (rank: %s)',
                     skill.name.capitalize(), start_page, last)

        params = copy(self._default_params)
        params.update({'table': skill.value, 'page': start_page})

        with self.set_url(URL_IRONMAN):
            ret = self.__find_value(params, 3, skill.xp_99)
            LOGGER.info('%s 99s ironman count: %s', skill.name.capitalize(), ret)

        return ret

    def get_120s(self, skill: Skill, last: int = 0) -> int:
        """
        """
        # 25 ranks per page
        start_page = max(1, math.ceil(last / 25))
        LOGGER.debug('Start page for %s 120s count: %s (rank: %s)',
                     skill.name.capitalize(), start_page, last)

        params = copy(self._default_params)
        params.update({'table': skill.value, 'page': start_page})

        with self.set_url(URL):
            ret = self.__find_value(params, 3, skill.xp_120)
            LOGGER.info('%s 120s count: %s', skill.name.capitalize(), ret)

        return ret

    def get_120s_ironman(self, skill: Skill, last: int = 0) -> int:
        """
        """
        # 25 ranks per page
        start_page = max(1, math.ceil(last / 25))
        LOGGER.debug('Start page for %s 120s ironman count: %s (rank: %s)',
                     skill.name.capitalize(), start_page, last)

        params = copy(self._default_params)
        params.update({'table': skill.value, 'page': start_page})

        with self.set_url(URL_IRONMAN):
            ret = self.__find_value(params, 3, skill.xp_120)
            LOGGER.info('%s 120s ironman count: %s', skill.name.capitalize(), ret)

        return ret

    def get_200m_xp(self, skill: Skill, last: int = 0) -> int:
        """
        """
        # 25 ranks per page
        start_page = max(1, math.ceil(last / 25))
        LOGGER.debug('Start page for %s 200m XP count: %s (rank: %s)',
                     skill.name.capitalize(), start_page, last)

        params = copy(self._default_params)
        params.update({'table': skill.value, 'page': start_page})

        with self.set_url(URL):
            ret = self.__find_value(params, 3, skill.xp_max)
            LOGGER.info('%s 200m XP count: %s', skill.name.capitalize(), ret)

        return ret

    def get_200m_xp_ironman(self, skill: Skill, last: int = 0) -> int:
        """
        """
        # 25 ranks per page
        start_page = max(1, math.ceil(last / 25))
        LOGGER.debug('Start page for %s 200m ironman XP count: %s (rank: %s)',
                     skill.name.capitalize(), start_page, last)

        params = copy(self._default_params)
        params.update({'table': skill.value, 'page': start_page})

        with self.set_url(URL_IRONMAN):
            ret = self.__find_value(params, 3, skill.xp_max)
            LOGGER.info('%s 200m XP ironman count: %s', skill.name.capitalize(), ret)

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
            params.update({'table': skill.value, 'page': 1})
            soup = self.__get(params)
            # should be 7 keys here
            page = soup.select('.pageNumbers li a')[-1].string

            # load the page and get the last row of the hiscores table
            params.update({'page': page})
            soup = self.__get(params)
            cells = tuple(x for x in soup.select('div.tableWrap tbody tr') \
                          [-1].contents if not isinstance(x, nstr))

            rank = int(cells[0].a.string.strip().replace(',', ''))
            level = int(cells[2].a.string.strip().replace(',', ''))

        LOGGER.info("%s lowest rank: %s, level: %s", skill.name.capitalize(), rank, level)

        return {
            'rank': rank,
            'level': level,
        }
