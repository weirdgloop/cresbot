#

"""
"""

from datetime import datetime, timedelta
from enum import Enum
import string
from typing import Union
from urllib.parse import urljoin

import requests

from ..runedate import Runedate

from .exchange_category import ExchangeCategory
from .exchange_models import (
    ExchangeCatalogueCategory,
    ExchangeCatalogueItemList,
    ExchangeCatalogueDetail,
    ExchangeGraph,
)


_FIRE_RUNE_ID = 554


class ExchangeDatabase:
    """
    """

    def __init__(self, interval: int=1):
        """

        :param int interval: The interval to wait between requests in seconds. Defaults to 1.
        """
        # TODO: set user agent
        self.__session = requests.Session()
        self.__host = 'https://secure.runescape.com'
        self.__last_request = None
        self.interval = interval

    def __get(self, path: str, **params) -> dict:
        """
        """
        url = urljoin(self.__host, path)
        # TODO: handle interval
        res = self.__session.get(url, params=params)

        # TODO: handle being ratelimited, should return a 404
        return res.json()

    def get_last_config_update(self) -> datetime:
        """
        """
        path = '/m=itemdb_rs/api/info.json'
        res = self.__get(path)
        last_update = res['lastConfigUpdateRuneday']

        return Runedate(res['lastConfigUpdateRuneday']).to_datetime()

    def get_last_update(self) -> datetime:
        """
        """
        # use the id of a fire rune as it's unlikely to go missing
        # and the way to check for an update is to inspect the last time in the graph
        graph = self.graph(554)
        return graph.daily[-1].time

    def catalogue_category(self, category: ExchangeCategory) -> dict:
        """
        """
        path = '/m=itemdb_rs/api/catalogue/category.json'
        params = {'category': ExchangeCategory(category).value}

        res = self.__get(path, **params)
        return ExchangeCatalogueCategory(**res)

    def catalogue_items(self, category: ExchangeCategory, alpha: str, page: int=1) -> ExchangeCatalogueItemList:
        """
        """
        if alpha == '#':
            alpha = '%23'
        elif alpha not in string.ascii_lowercase:
            raise ValueError('Invalid value for alpha: {}', alpha)

        if page < 1:
            raise ValueError('Invalid value for page: {}. Must be greater than 0.'.format(page))

        path = '/m=itemdb_rs/api/catalogue/items.json'
        params = {'category': ExchangeCategory(category).value,
                  'alpha': alpha,
                  'page': page}

        res = self.__get(path, **params)
        return ExchangeCatalogueItemList(**res)

    def catalogue_items_iterator(self, category: ExchangeCategory, alpha: str=None, page: int=1):
        """
        """
        if alpha is None:
            data = self.catalogue_category(category)

            for alpha in data['alpha']:
                if not alpha['items']:
                    continue

                yield from self.catalogue_items_iterator(category, alpha['letter'], page=1)
        else:
            while True:
                res = self.catalogue_items(self, category, alpha, page)

                for item in res.items:
                    yield item

                if len(res.items) < 12:
                    break

                # go to the next page
                page += 1

    def catalogue_detail(self, item_id: int) -> ExchangeCatalogueDetail:
        """
        """
        path = '/m=itemdb_rs/api/catalogue/detail.json'
        params = {'item': item_id}

        res = self.__get(path, **params)
        return ExchangeCatalogueDetail(**res)

    def graph(self, item_id: int) -> ExchangeGraph:
        """
        """
        path = '/m=itemdb_rs/api/graph/{}.json'.format(item_id)

        res = self.__get(path)
        return ExchangeGraph(**res)
